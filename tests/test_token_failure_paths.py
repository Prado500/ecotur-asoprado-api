"""
Failure-path tests for JWT handling in get_current_user and verify_email_account.

The HTTP cases pin the answers of branches that had no test. The direct calls check what
`raise ... from err` adds and no HTTP response shows: the JWT error kept as __cause__.
"""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import create_autospec

import jwt
import pytest
from dotenv import dotenv_values
from fastapi import HTTPException
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.exceptions import InvalidVerificationTokenError
from app.core.security import create_access_token, create_verification_token
from app.main import app
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.user_access_policy import UserAccessPolicy
from app.services.user_service import UserService

PROTECTED_ROUTE = "/usuarios/mi-perfil"
VERIFY_ROUTE = "/usuarios/verificar-email"
FOREIGN_KEY = "foreign-signing-key-known-only-to-these-tests"
ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"

PersistUser = Callable[..., Awaitable[User]]
AuthHeaders = Callable[[User], dict[str, str]]
MakeToken = Callable[..., str]
SignClaims = Callable[..., str]


def _expired_token() -> str:
    """Signs an access token for an email with no account that expired a minute ago."""
    return create_access_token(data={"sub": "ghost@test.com"}, expires_delta=timedelta(minutes=-1))


def _corrupt_token() -> str:
    """Returns a value that is not a JWT at all."""
    return "not-a-jwt"


def _bearer(token: str) -> dict[str, str]:
    """Builds the Authorization header for a token the factories cannot produce."""
    return {"Authorization": f"Bearer {token}"}


def _resign(token: str, key: str) -> str:
    """Signs a genuine token's claims again with the given key, keeping its algorithm."""
    claims = jwt.decode(token, options={"verify_signature": False})
    algorithm = jwt.get_unverified_header(token)["alg"]
    return jwt.encode(claims, key, algorithm=algorithm)


def _env_example_jwt_key() -> str:
    """Reads the JWT key that .env.example ships, the one a developer may copy as is."""
    key = dotenv_values(ENV_EXAMPLE)["JWT_SECRET_KEY"]
    assert key
    return key


def _assert_bearer_401(response: Response) -> None:
    """Checks the 401 contract: Bearer challenge and a body with only a text detail."""
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)


def _user_service(user_repo: Any) -> UserService:
    """Builds the real UserService over the given repository double."""
    return UserService(
        user_repo=user_repo,
        audit_service=create_autospec(AuditService, instance=True),
        user_access_policy=UserAccessPolicy(),
    )


@pytest.fixture
def user_repo() -> Any:
    """Provides a strict autospecced UserRepository so signature drift fails the tests."""
    return create_autospec(UserRepository, instance=True)


async def test_valid_token_on_protected_route_returns_the_user(
    client: AsyncClient, persist_user: PersistUser, make_auth_headers: AuthHeaders
) -> None:
    """Happy path: a valid token resolves to the active user it names."""
    await persist_user()
    user = await persist_user()

    response = await client.get(PROTECTED_ROUTE, headers=make_auth_headers(user))

    assert response.status_code == 200
    assert response.json()["cedula"] == user.cedula


async def test_expired_token_on_protected_route_returns_401(
    client: AsyncClient, persist_user: PersistUser, make_token: MakeToken
) -> None:
    """Unhappy path: only the expiry stands between this token and an active user."""
    user = await persist_user()

    response = await client.get(
        PROTECTED_ROUTE, headers=_bearer(make_token(user, expires_delta=timedelta(minutes=-1)))
    )

    _assert_bearer_401(response)


async def test_corrupt_token_on_protected_route_returns_401(client: AsyncClient) -> None:
    """Unhappy path: a value that is not a JWT never reaches the user lookup."""
    response = await client.get(PROTECTED_ROUTE, headers=_bearer(_corrupt_token()))

    _assert_bearer_401(response)


async def test_expired_and_corrupt_tokens_get_distinct_details(client: AsyncClient) -> None:
    """Edge case: each failure keeps its own answer, compared without reading the text."""
    expired = await client.get(PROTECTED_ROUTE, headers=_bearer(_expired_token()))
    corrupt = await client.get(PROTECTED_ROUTE, headers=_bearer(_corrupt_token()))

    assert expired.json()["detail"] != corrupt.json()["detail"]


async def test_corrupt_token_gets_the_same_detail_as_an_unknown_user(client: AsyncClient) -> None:
    """Edge case: a corrupt token is answered like a valid token for nobody, text unread."""
    corrupt = await client.get(PROTECTED_ROUTE, headers=_bearer(_corrupt_token()))
    unknown = await client.get(
        PROTECTED_ROUTE, headers=_bearer(create_access_token(data={"sub": "ghost@test.com"}))
    )

    _assert_bearer_401(corrupt)
    _assert_bearer_401(unknown)
    assert corrupt.json()["detail"] == unknown.json()["detail"]


async def test_token_without_subject_returns_401(client: AsyncClient) -> None:
    """Edge case: a validly signed token with no sub claim identifies nobody."""
    token = create_access_token(data={"role": "tourist"})

    response = await client.get(PROTECTED_ROUTE, headers=_bearer(token))

    _assert_bearer_401(response)


async def test_token_for_unknown_user_returns_401(
    client: AsyncClient, persist_user: PersistUser
) -> None:
    """Unhappy path: a valid token whose subject has no account is rejected."""
    await persist_user()
    token = create_access_token(data={"sub": "ghost@test.com"})

    response = await client.get(PROTECTED_ROUTE, headers=_bearer(token))

    _assert_bearer_401(response)


async def test_access_token_without_scope_returns_401(
    client: AsyncClient, persist_user: PersistUser, sign_claims: SignClaims
) -> None:
    """Unhappy path: a token like those signed before BE-42, with no scope, opens nothing.

    Same subject, role and lifespan as a login token, for an active user: only the missing
    scope stands between it and the route.
    """
    user = await persist_user()
    token = sign_claims(
        {"sub": user.email, "role": user.role.value}, expires_delta=timedelta(minutes=30)
    )

    response = await client.get(PROTECTED_ROUTE, headers=_bearer(token))

    _assert_bearer_401(response)


async def test_verification_token_gets_the_same_detail_as_a_corrupt_token(
    client: AsyncClient, persist_user: PersistUser
) -> None:
    """Edge case: a verification token is answered like a corrupt one, text unread."""
    user = await persist_user()

    verification = await client.get(
        PROTECTED_ROUTE, headers=_bearer(create_verification_token(user.email))
    )
    corrupt = await client.get(PROTECTED_ROUTE, headers=_bearer(_corrupt_token()))

    _assert_bearer_401(verification)
    assert verification.json()["detail"] == corrupt.json()["detail"]


async def test_token_for_inactive_user_returns_401(
    client: AsyncClient, persist_user: PersistUser, make_auth_headers: AuthHeaders
) -> None:
    """Edge case: a valid token stops working once its account is inactive."""
    user = await persist_user(is_active=False)

    response = await client.get(PROTECTED_ROUTE, headers=make_auth_headers(user))

    _assert_bearer_401(response)


async def test_token_for_soft_deleted_active_user_returns_401(
    client: AsyncClient, persist_user: PersistUser, make_auth_headers: AuthHeaders
) -> None:
    """Edge case: a soft-deleted account is rejected even while is_active is still True."""
    user = await persist_user(deleted_at=datetime(2026, 1, 15, 12, 0, tzinfo=UTC))

    response = await client.get(PROTECTED_ROUTE, headers=make_auth_headers(user))

    _assert_bearer_401(response)


async def test_access_token_signed_with_another_key_returns_401(
    client: AsyncClient, persist_user: PersistUser, make_token: MakeToken
) -> None:
    """Unhappy path: a token re-signed with a foreign key is rejected for an active user."""
    user = await persist_user()

    response = await client.get(
        PROTECTED_ROUTE, headers=_bearer(_resign(make_token(user), FOREIGN_KEY))
    )

    _assert_bearer_401(response)


async def test_verification_token_signed_with_another_key_returns_400_and_keeps_account_inactive(
    client: AsyncClient, db_session: AsyncSession, persist_user: PersistUser
) -> None:
    """Unhappy path: a re-signed verification token is rejected and activates nothing."""
    user = await persist_user(is_active=False)

    response = await client.get(
        VERIFY_ROUTE,
        params={"token": _resign(create_verification_token(user.email), FOREIGN_KEY)},
    )

    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)
    await db_session.refresh(user)
    assert user.is_active is False


async def test_access_token_signed_with_the_env_example_key_returns_401(
    client: AsyncClient, persist_user: PersistUser, make_token: MakeToken
) -> None:
    """Edge case: the key that .env.example ships signs nothing this app accepts.

    Protects whoever copies the example as their .env; CI and production use their own keys.
    """
    user = await persist_user()

    response = await client.get(
        PROTECTED_ROUTE, headers=_bearer(_resign(make_token(user), _env_example_jwt_key()))
    )

    _assert_bearer_401(response)


async def test_protected_route_verifies_with_the_injected_settings(
    client: AsyncClient, persist_user: PersistUser, make_auth_headers: AuthHeaders
) -> None:
    """Edge case: get_current_user verifies with the Settings it is given, not a module copy."""
    user = await persist_user()
    rotated = get_settings().model_copy(update={"jwt_secret_key": FOREIGN_KEY})
    app.dependency_overrides[get_settings] = lambda: rotated

    response = await client.get(PROTECTED_ROUTE, headers=make_auth_headers(user))

    _assert_bearer_401(response)


@pytest.mark.parametrize(
    ("build_token", "expected_cause"),
    [(_expired_token, jwt.ExpiredSignatureError), (_corrupt_token, jwt.DecodeError)],
    ids=["expired", "corrupt"],
)
async def test_get_current_user_chains_the_jwt_error_as_cause(
    user_repo: Any, build_token: Callable[[], str], expected_cause: type[Exception]
) -> None:
    """The 401 keeps the JWT error as its cause, and the repository is never consulted."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=build_token(), user_repo=user_repo, settings=get_settings())

    assert exc_info.value.status_code == 401
    assert type(exc_info.value.__cause__) is expected_cause
    assert user_repo.mock_calls == []


@pytest.mark.parametrize(
    ("build_token", "expected_cause"),
    [(_expired_token, jwt.ExpiredSignatureError), (_corrupt_token, jwt.DecodeError)],
    ids=["expired", "corrupt"],
)
async def test_verify_email_chains_the_jwt_error_as_cause(
    user_repo: Any, build_token: Callable[[], str], expected_cause: type[Exception]
) -> None:
    """The domain error keeps the JWT error as its cause."""
    service = _user_service(user_repo)

    with pytest.raises(InvalidVerificationTokenError) as exc_info:
        await service.verify_email_account(build_token())

    assert type(exc_info.value.__cause__) is expected_cause


async def test_verify_email_expired_and_corrupt_tokens_get_distinct_errors(user_repo: Any) -> None:
    """Edge case: each verification failure keeps its own detail, compared without reading it."""
    service = _user_service(user_repo)

    with pytest.raises(InvalidVerificationTokenError) as expired:
        await service.verify_email_account(_expired_token())
    with pytest.raises(InvalidVerificationTokenError) as corrupt:
        await service.verify_email_account(_corrupt_token())

    assert expired.value.detail != corrupt.value.detail
