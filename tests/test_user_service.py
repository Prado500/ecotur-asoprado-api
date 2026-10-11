"""Unit and integration tests for the transport-agnostic UserService contract."""

from datetime import datetime, timedelta, timezone
from unittest.mock import create_autospec

import jwt
import pytest

from app.core.exceptions import (
    AccountNotActiveError,
    AlreadyExistsError,
    AuthorizationError,
    InvalidCredentialsError,
    InvalidVerificationTokenError,
    NotFoundError,
)
from app.core.security import ALGORITHM, SECRET_KEY, create_verification_token, get_password_hash
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserCreateByAdmin, UserLogin, UserRole as SchemaUserRole, UserUpdate
from app.services.audit_service import AuditService
from app.services.user_access_policy import UserAccessPolicy
from app.services.user_service import RegistrationResult, UserService


def _tourist_payload(**overrides) -> UserCreate:
    defaults = dict(
        cedula="1005911792",
        email="turista@example.com",
        first_name="Juan",
        last_name="Perez",
        phone="3001234567",
        password="passwordSegura123",
        data_consent=True,
    )
    defaults.update(overrides)
    return UserCreate(**defaults)


def _admin_payload(**overrides) -> UserCreateByAdmin:
    defaults = dict(
        cedula="5555555555",
        email="newadmin@test.com",
        first_name="New",
        last_name="Admin",
        phone="3000000000",
        password="Password123",
        role=SchemaUserRole.admin,
        data_consent=True,
        is_active=True,
    )
    defaults.update(overrides)
    return UserCreateByAdmin(**defaults)


@pytest.fixture
def user_repo() -> UserRepository:
    """Provides a strict autospec'd UserRepository so signature drift fails tests."""
    return create_autospec(UserRepository, instance=True)


@pytest.fixture
def audit_service() -> AuditService:
    """Provides a strict autospec'd AuditService so signature drift fails tests."""
    return create_autospec(AuditService, instance=True)


@pytest.fixture
def user_service(user_repo, audit_service) -> UserService:
    """Builds the real service over autospec'd repositories and the real policy."""
    return UserService(
        user_repo=user_repo,
        audit_service=audit_service,
        user_access_policy=UserAccessPolicy(),
    )


# ==========================================
# REGISTRATION PIPELINE
# ==========================================


async def test_register_tourist_returns_registration_result(user_repo, audit_service, user_service):
    """Happy path: persists an inactive tourist and returns its verification token."""
    user_repo.get_user_by_email_or_cedula.return_value = None
    user_repo.create_user.side_effect = lambda user: user

    result = await user_service.register_tourist(_tourist_payload())

    assert isinstance(result, RegistrationResult)
    assert isinstance(result.verification_token, str)
    assert result.user is user_repo.create_user.call_args.args[0]
    assert result.user.role == UserRole.tourist
    assert result.user.is_active is False
    assert result.user.password_hash != "passwordSegura123"

    claims = jwt.decode(result.verification_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["sub"] == result.user.email
    assert claims["scope"] == "email_verification"

    user_repo.get_user_by_email_or_cedula.assert_awaited_once_with(
        email="turista@example.com", cedula="1005911792"
    )
    user_repo.create_user.assert_awaited_once()
    audit_service.log_transaction.assert_awaited_once()


async def test_register_tourist_duplicate_raises_already_exists(user_repo, user_service, make_user):
    """Unhappy path: an existing email/cedula aborts registration before persistence."""
    user_repo.get_user_by_email_or_cedula.return_value = make_user()

    with pytest.raises(AlreadyExistsError):
        await user_service.register_tourist(_tourist_payload())

    user_repo.create_user.assert_not_called()
    user_repo.create_user.assert_not_awaited()


# ==========================================
# ORDER INVARIANT: 404 EXISTENCE BEFORE 403 HIERARCHY
# ==========================================


async def test_delete_missing_target_raises_not_found_before_authorization(user_repo, user_service, make_user):
    """Order invariant: existence (404) dominates hierarchy (403) on deletion."""
    user_repo.get_user_by_cedula.return_value = None
    actor = make_user(role=UserRole.tourist)

    with pytest.raises(NotFoundError):
        await user_service.delete_user_account(target_cedula="0000000000", current_user=actor)

    user_repo.soft_delete_user.assert_not_awaited()


async def test_update_missing_target_raises_not_found_before_authorization(user_repo, user_service, make_user):
    """Order invariant: existence (404) dominates hierarchy (403) on updates."""
    user_repo.get_user_by_cedula.return_value = None
    actor = make_user(role=UserRole.tourist)

    with pytest.raises(NotFoundError):
        await user_service.update_user_account(
            target_cedula="0000000000",
            update_data=UserUpdate(first_name="Hacked"),
            current_user=actor,
        )

    user_repo.save_user.assert_not_awaited()


async def test_recover_missing_target_raises_not_found(user_repo, user_service, make_user):
    """Order invariant: existence (404) dominates hierarchy on recovery."""
    user_repo.get_user_by_cedula.return_value = None

    with pytest.raises(NotFoundError):
        await user_service.recover_user_account(
            target_cedula="0000000000",
            current_user=make_user(role=UserRole.superadmin),
        )


async def test_recover_active_target_raises_not_found(user_repo, user_service, make_user):
    """Edge case: an account outside the recycle bin is indistinguishable from a missing one."""
    user_repo.get_user_by_cedula.return_value = make_user(deleted_at=None)

    with pytest.raises(NotFoundError):
        await user_service.recover_user_account(
            target_cedula="0000000000",
            current_user=make_user(role=UserRole.superadmin),
        )


# ==========================================
# AUTHENTICATION
# ==========================================


async def test_authenticate_active_user_returns_bearer_token(user_repo, user_service, make_user):
    """Happy path: valid credentials issue a signed bearer token with the user claims."""
    user = make_user(password_hash=get_password_hash("correctPassword1"), is_active=True)
    user_repo.get_non_deleted_user_by_email.return_value = user

    result = await user_service.authenticate_user(
        UserLogin(email=user.email, password="correctPassword1")
    )

    assert result.token_type == "bearer"
    claims = jwt.decode(result.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["sub"] == user.email
    assert claims["role"] == user.role.value


async def test_authenticate_unknown_email_raises_invalid_credentials(user_repo, user_service):
    """Unhappy path: an unknown email raises the 401 domain error."""
    user_repo.get_non_deleted_user_by_email.return_value = None

    with pytest.raises(InvalidCredentialsError):
        await user_service.authenticate_user(
            UserLogin(email="ghost@example.com", password="wrongPassword1")
        )


async def test_authenticate_wrong_password_raises_invalid_credentials(user_repo, user_service, make_user):
    """Unhappy path: an existing user with a mismatched password maps to the same error."""
    user = make_user(password_hash=get_password_hash("correctPassword1"), is_active=True)
    user_repo.get_non_deleted_user_by_email.return_value = user

    with pytest.raises(InvalidCredentialsError):
        await user_service.authenticate_user(
            UserLogin(email=user.email, password="wrongPassword1")
        )


async def test_authenticate_inactive_account_raises_account_not_active(user_repo, user_service, make_user):
    """Unhappy path: correct credentials on a pending-verification account yield 403 semantics."""
    user = make_user(password_hash=get_password_hash("correctPassword1"), is_active=False)
    user_repo.get_non_deleted_user_by_email.return_value = user

    with pytest.raises(AccountNotActiveError):
        await user_service.authenticate_user(
            UserLogin(email=user.email, password="correctPassword1")
        )


# ==========================================
# EMAIL VERIFICATION
# ==========================================


async def test_verify_email_activates_account(user_repo, user_service):
    """Happy path: a valid token activates the account and returns success."""
    user_repo.activate_user.return_value = True

    result = await user_service.verify_email_account(create_verification_token("turista@example.com"))

    assert result["success"] is True
    assert "message" in result
    user_repo.activate_user.assert_awaited_once_with("turista@example.com")


async def test_verify_email_corrupt_token_raises_invalid_verification_token(user_repo, user_service):
    """Unhappy path: a corrupt token is rejected before any activation attempt."""
    with pytest.raises(InvalidVerificationTokenError):
        await user_service.verify_email_account("not-a-jwt")

    user_repo.activate_user.assert_not_awaited()


async def test_verify_email_expired_token_raises_invalid_verification_token(user_repo, user_service):
    """Unhappy path: an expired token is rejected before any activation attempt."""
    expired_token = jwt.encode(
        {
            "sub": "turista@example.com",
            "scope": "email_verification",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(InvalidVerificationTokenError):
        await user_service.verify_email_account(expired_token)

    user_repo.activate_user.assert_not_awaited()


async def test_verify_email_wrong_scope_raises_invalid_verification_token(user_repo, user_service):
    """Edge case: an otherwise valid JWT with a non-verification scope is rejected."""
    wrong_scope_token = jwt.encode(
        {
            "sub": "turista@example.com",
            "scope": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(InvalidVerificationTokenError):
        await user_service.verify_email_account(wrong_scope_token)

    user_repo.activate_user.assert_not_awaited()


async def test_verify_email_missing_user_raises_not_found(user_repo, user_service):
    """Unhappy path: a valid token for a missing account maps to the 404 domain error."""
    user_repo.activate_user.return_value = False

    with pytest.raises(NotFoundError):
        await user_service.verify_email_account(create_verification_token("ghost@example.com"))


# ==========================================
# ADMINISTRATIVE PROVISIONING
# ==========================================


async def test_create_administrative_account_provisions_admin(user_repo, audit_service, user_service, make_user):
    """Happy path: a superadmin provisions an admin account in a single persistence call."""
    user_repo.get_user_by_email_or_cedula.return_value = None
    actor = make_user(role=UserRole.superadmin)

    await user_service.create_administrative_account(_admin_payload(), actor)

    created_user = user_repo.create_user.call_args.args[0]
    assert created_user.role == UserRole.admin
    assert created_user.cedula == "5555555555"
    assert created_user.is_active is True
    user_repo.create_user.assert_awaited_once()
    audit_service.log_transaction.assert_awaited_once()


async def test_create_administrative_account_duplicate_raises_already_exists(user_repo, user_service, make_user):
    """Unhappy path: an existing email/cedula aborts provisioning before persistence."""
    user_repo.get_user_by_email_or_cedula.return_value = make_user()

    with pytest.raises(AlreadyExistsError):
        await user_service.create_administrative_account(
            _admin_payload(), make_user(role=UserRole.superadmin)
        )

    user_repo.create_user.assert_not_awaited()


async def test_create_administrative_account_rejects_non_superadmin(user_repo, user_service, make_user):
    """Edge case: provisioning governance is checked before any repository access."""
    with pytest.raises(AuthorizationError):
        await user_service.create_administrative_account(
            _admin_payload(), make_user(role=UserRole.admin)
        )

    user_repo.get_user_by_email_or_cedula.assert_not_awaited()


# ==========================================
# INTEGRATION (real HTTP stack)
# ==========================================


async def test_login_invalid_credentials_returns_401_with_bearer_challenge(client):
    """The 401 domain error surfaces through the HTTP stack with the Bearer challenge."""
    response = await client.post(
        "/usuarios/login",
        json={"email": "ghost@example.com", "password": "wrongPassword1"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert "detail" in response.json()
