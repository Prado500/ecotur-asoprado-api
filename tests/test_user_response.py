"""Output-side contract of UserResponse (backlog A9).

UserResponse must describe the stored account as it is: a row that predates or bypasses the
registration form rules (pattern, lengths, EmailStr, title-case) is still readable and comes
back verbatim. The input DTOs keep rejecting and normalizing what the form receives.

Users are seeded only through ``persist_user`` (ORM, no schema involved) so the stored values
can deliberately break the form rules.
"""

from datetime import UTC, datetime
from unittest.mock import ANY, patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole

USER_RESPONSE_KEYS = {
    "cedula",
    "email",
    "first_name",
    "last_name",
    "phone",
    "id",
    "role",
    "is_active",
    "created_at",
}

REGISTRATION_PAYLOAD = {
    "cedula": "1005911792",
    "email": "turista@example.com",
    "first_name": "Juan",
    "last_name": "Perez",
    "phone": "3001234567",
    "password": "passwordSegura123",
    "data_consent": True,
}


@pytest.fixture(autouse=True)
def mock_send_email():
    """Replaces the verification email dispatch so no SMTP connection is attempted."""
    with patch("app.api.routers.user.send_verification_email", autospec=True) as mock:
        yield mock


async def _count_users(db_session: AsyncSession) -> int:
    result = await db_session.execute(select(func.count()).select_from(User))
    return result.scalar_one()


# === READ PATHS: STORED VALUES COME BACK VERBATIM ===


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("first_name", "Jean-Luc"),
        ("last_name", "O'Brien"),
        ("last_name", "McDonald"),
        ("first_name", "A" * 66),
        ("phone", "6012345678"),
        ("cedula", "12345678901"),
        ("email", "admin@localhost"),
        ("email", "Ana@EXAMPLE.COM"),
    ],
    ids=[
        "hyphen",
        "apostrophe",
        "mixed_case_surname",
        "66_chars",
        "landline",
        "11_digit_cedula",
        "dotless_domain",
        "mixed_case_domain",
    ],
)
async def test_my_profile_returns_stored_values_verbatim(
    client, persist_user, make_auth_headers, field, value
):
    """A stored value the form would reject or rewrite is returned exactly as stored."""
    user = await persist_user(**{field: value})

    response = await client.get("/usuarios/mi-perfil", headers=make_auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == USER_RESPONSE_KEYS
    assert body[field] == value
    assert body["id"] == user.id
    assert body["role"] == "tourist"


async def test_user_directory_survives_one_off_rule_record(client, persist_user, make_auth_headers):
    """One off-rule row among valid ones does not take the admin directory down."""
    admin = await persist_user(role=UserRole.admin)
    valid_one = await persist_user()
    valid_two = await persist_user()
    off_rule = await persist_user(first_name="Jean-Luc")

    response = await client.get("/usuarios/", headers=make_auth_headers(admin))

    assert response.status_code == 200
    body = response.json()
    assert {item["cedula"] for item in body} == {
        admin.cedula,
        valid_one.cedula,
        valid_two.cedula,
        off_rule.cedula,
    }
    off_rule_item = next(item for item in body if item["cedula"] == off_rule.cedula)
    assert off_rule_item["first_name"] == "Jean-Luc"


async def test_deleted_directory_returns_stored_names_verbatim(
    client, persist_user, make_auth_headers
):
    """The recycle-bin directory returns an off-rule deleted account as stored."""
    admin = await persist_user(role=UserRole.admin)
    deleted = await persist_user(last_name="O'Brien", deleted_at=datetime.now(UTC), is_active=False)

    response = await client.get("/usuarios/admin/eliminados", headers=make_auth_headers(admin))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["cedula"] == deleted.cedula
    assert body[0]["last_name"] == "O'Brien"


async def test_patch_on_off_rule_record_returns_200_with_persisted_change(
    client, db_session, persist_user, make_auth_headers
):
    """PATCH on an off-rule row answers 200 and the change is persisted."""
    user = await persist_user(first_name="Jean-Luc")

    response = await client.patch(
        f"/usuarios/{user.cedula}",
        json={"phone": "3001112233"},
        headers=make_auth_headers(user),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "3001112233"
    assert body["first_name"] == "Jean-Luc"
    await db_session.refresh(user)
    assert user.phone == "3001112233"
    assert user.first_name == "Jean-Luc"


# === WRITE PATHS: THE INPUT RULES STILL APPLY ===


async def test_registration_still_rejects_hyphenated_name(client, db_session, mock_send_email):
    """The registration form keeps rejecting a hyphenated name with 422 and no side effect."""
    payload = {**REGISTRATION_PAYLOAD, "first_name": "Jean-Luc"}

    response = await client.post("/usuarios/registro", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert [error["raw_field"] for error in body["detalle"]] == ["first_name"]
    assert await _count_users(db_session) == 0
    mock_send_email.assert_not_called()


async def test_registration_still_title_cases_names(client, db_session, mock_send_email):
    """The registration form keeps normalizing names to title-case before persisting."""
    payload = {**REGISTRATION_PAYLOAD, "first_name": "jUAN", "last_name": "pérez"}

    response = await client.post("/usuarios/registro", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Juan"
    assert body["last_name"] == "Pérez"
    result = await db_session.execute(select(User).where(User.cedula == payload["cedula"]))
    stored = result.scalar_one()
    assert stored.first_name == "Juan"
    assert stored.last_name == "Pérez"
    mock_send_email.assert_called_once_with(
        email_to=payload["email"], first_name="Juan", token=ANY, base_url=ANY
    )


async def test_patch_still_rejects_hyphenated_name(
    client, db_session, persist_user, make_auth_headers
):
    """PATCH keeps rejecting a hyphenated name with 422 and leaves the stored name intact."""
    user = await persist_user()
    original_first_name = user.first_name

    response = await client.patch(
        f"/usuarios/{user.cedula}",
        json={"first_name": "Jean-Luc"},
        headers=make_auth_headers(user),
    )

    assert response.status_code == 422
    body = response.json()
    assert [error["raw_field"] for error in body["detalle"]] == ["first_name"]
    await db_session.refresh(user)
    assert user.first_name == original_first_name
