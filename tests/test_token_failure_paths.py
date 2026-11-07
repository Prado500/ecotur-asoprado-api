"""
Failure-path tests for JWT handling in get_current_user and verify_email_account.

The HTTP cases pin the answers of branches that had no test. The direct calls check what
`raise ... from err` adds and no HTTP response shows: the JWT error kept as __cause__.
"""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import create_autospec

import jwt
import pytest
from fastapi import HTTPException
from httpx import AsyncClient, Response

from app.api.dependencies import get_current_user
from app.core.exceptions import InvalidVerificationTokenError
from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.user_access_policy import UserAccessPolicy
from app.services.user_service import UserService

PROTECTED_ROUTE = "/usuarios/mi-perfil"

PersistUser = Callable[..., Awaitable[User]]
AuthHeaders = Callable[[User], dict[str, str]]
MakeToken = Callable[..., str]


def _expired_token() -> str:
    """Signs an access token for an email with no account that expired a minute ago."""
    return create_access_token(data={"sub": "ghost@test.com"}, expires_delta=timedelta(minutes=-1))


def _corrupt_token() -> str:
    """Returns a value that is not a JWT at all."""
    return "not-a-jwt"


def _bearer(token: str) -> dict[str, str]:
    """Builds the Authorization header for a token the factories cannot produce."""
    return {"Authorization": f"Bearer {token}"}


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
        await get_current_user(token=build_token(), user_repo=user_repo)

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
