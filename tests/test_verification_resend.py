"""HTTP tests for POST /usuarios/reenviar-verificacion (BE-64, ADR-0023).

The route answers 200 with the same body whether or not a link leaves, so each case that sends
nothing compares its body with the one a pending tourist gets. The email double is the autouse
mock_send_email of tests/conftest.py: a link left when, and only when, it was called.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import ANY

import jwt
import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import EMAIL_VERIFICATION_SCOPE
from app.main import app
from app.models.audit import AuditLog
from app.models.user import UserRole

URL = "/usuarios/reenviar-verificacion"
FRONTEND_URL = "http://localhost:3000"  # root conftest.py
LONG_AGO = datetime(2026, 11, 1, tzinfo=UTC)

# Accounts that get no link. "sent_seconds_ago" becomes verification_sent_at in the test itself,
# so the clock it measures from is the request's, not the collection's.
NOT_DUE: dict[str, dict[str, Any]] = {
    "admin": {"role": UserRole.admin, "is_active": False},
    "superadmin": {"role": UserRole.superadmin, "is_active": False},
    "soft-deleted-tourist": {"is_active": False, "deleted_at": LONG_AGO},
    "verified-tourist": {"is_active": True, "email_verified_at": LONG_AGO},
    "verified-tourist-deactivated": {"is_active": False, "email_verified_at": LONG_AGO},
    "link-sent-59-seconds-ago": {"is_active": False, "sent_seconds_ago": 59},
}


def _claims(token: str) -> dict[str, Any]:
    """Decodes a token with the app's key, as the verification link does."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])


def _sent_seconds_ago(overrides: dict[str, Any]) -> dict[str, Any]:
    """Turns the "sent_seconds_ago" key of a case into a verification_sent_at from now."""
    overrides = dict(overrides)
    seconds = overrides.pop("sent_seconds_ago", None)
    if seconds is not None:
        overrides["verification_sent_at"] = datetime.now(UTC) - timedelta(seconds=seconds)
    return overrides


async def test_pending_tourist_gets_a_new_link(client, db_session, persist_user, mock_send_email):
    """Happy path: an inactive, unverified tourist gets a link; nothing else changes."""
    tourist = await persist_user(is_active=False)

    response = await client.post(URL, json={"email": tourist.email})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"success", "message"}
    assert body["success"] is True
    mock_send_email.assert_called_once_with(
        email_to=tourist.email, first_name=tourist.first_name, token=ANY, base_url=FRONTEND_URL
    )
    claims = _claims(mock_send_email.call_args.kwargs["token"])
    assert (claims["sub"], claims["scope"]) == (tourist.email, EMAIL_VERIFICATION_SCOPE)
    await db_session.refresh(tourist)
    assert tourist.verification_sent_at is not None
    assert tourist.is_active is False
    assert tourist.email_verified_at is None
    assert (await db_session.execute(select(AuditLog))).scalars().all() == []


async def test_the_new_link_verifies_the_account(client, db_session, persist_user, mock_send_email):
    """Happy path: the emailed token is a working verification link."""
    tourist = await persist_user(is_active=False)
    await client.post(URL, json={"email": tourist.email})
    token = mock_send_email.call_args.kwargs["token"]

    response = await client.get(f"/usuarios/verificar-email?token={token}")

    assert response.status_code == 200
    await db_session.refresh(tourist)
    assert tourist.is_active is True
    assert tourist.email_verified_at is not None


@pytest.mark.parametrize("overrides", NOT_DUE.values(), ids=NOT_DUE.keys())
async def test_account_not_due_a_link_gets_the_same_answer_and_no_email(
    client, db_session, persist_user, mock_send_email, overrides
):
    """Unhappy path: no link and no write, and the body is the one a pending tourist gets."""
    pending = await persist_user(is_active=False)
    account = await persist_user(**_sent_seconds_ago(overrides))
    before = (account.is_active, account.email_verified_at, account.verification_sent_at)

    expected = await client.post(URL, json={"email": pending.email})
    response = await client.post(URL, json={"email": account.email})

    assert expected.status_code == response.status_code == 200
    assert response.json() == expected.json()
    mock_send_email.assert_called_once_with(
        email_to=pending.email, first_name=ANY, token=ANY, base_url=ANY
    )
    await db_session.refresh(account)
    assert (account.is_active, account.email_verified_at, account.verification_sent_at) == before


async def test_unknown_email_gets_the_same_answer_and_no_email(
    client, persist_user, mock_send_email
):
    """Unhappy path: an address with no account answers as a pending tourist's does."""
    pending = await persist_user(is_active=False)

    expected = await client.post(URL, json={"email": pending.email})
    response = await client.post(URL, json={"email": "nadie@example.com"})

    assert expected.status_code == response.status_code == 200
    assert response.json() == expected.json()
    mock_send_email.assert_called_once_with(
        email_to=pending.email, first_name=ANY, token=ANY, base_url=ANY
    )


async def test_tourist_an_admin_activated_without_verifying_gets_a_link(
    client, db_session, persist_user, mock_send_email
):
    """Edge case: an active tourist whose mark is empty gets a link and stays active."""
    tourist = await persist_user(is_active=True)

    response = await client.post(URL, json={"email": tourist.email})

    assert response.status_code == 200
    mock_send_email.assert_called_once_with(
        email_to=tourist.email, first_name=tourist.first_name, token=ANY, base_url=FRONTEND_URL
    )
    await db_session.refresh(tourist)
    assert tourist.is_active is True
    assert tourist.email_verified_at is None


async def test_registration_counts_as_the_first_link(client, mock_send_email):
    """Edge case: right after registering, a resend sends nothing more."""
    payload = {
        "cedula": "1005911792",
        "email": "turista@example.com",
        "first_name": "Juan",
        "last_name": "Perez",
        "phone": "3001234567",
        "password": "passwordSegura123",
        "data_consent": True,
    }
    registered = await client.post("/usuarios/registro", json=payload)

    response = await client.post(URL, json={"email": payload["email"]})

    assert (registered.status_code, response.status_code) == (201, 200)
    mock_send_email.assert_called_once_with(
        email_to="turista@example.com", first_name="Juan", token=ANY, base_url=FRONTEND_URL
    )


async def test_second_request_within_the_interval_sends_nothing(
    client, db_session, persist_user, mock_send_email
):
    """Edge case: two requests in a row send one link and keep the first send time."""
    tourist = await persist_user(is_active=False)

    first = await client.post(URL, json={"email": tourist.email})
    await db_session.refresh(tourist)
    sent_at = tourist.verification_sent_at
    second = await client.post(URL, json={"email": tourist.email})

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    mock_send_email.assert_called_once()
    await db_session.refresh(tourist)
    assert sent_at is not None
    assert tourist.verification_sent_at == sent_at


async def test_link_is_sent_again_once_the_interval_passed(
    client, db_session, persist_user, mock_send_email
):
    """Edge case: 61 seconds after the last link, a new one leaves and the time moves on."""
    tourist = await persist_user(
        is_active=False, verification_sent_at=datetime.now(UTC) - timedelta(seconds=61)
    )
    previous = tourist.verification_sent_at
    assert previous is not None

    response = await client.post(URL, json={"email": tourist.email})

    assert response.status_code == 200
    mock_send_email.assert_called_once()
    await db_session.refresh(tourist)
    assert tourist.verification_sent_at is not None
    assert tourist.verification_sent_at > previous


async def test_email_is_matched_in_lowercase(client, persist_user, mock_send_email):
    """Edge case: the address is lowered before the lookup, as every email input (ADR-0016)."""
    tourist = await persist_user(is_active=False, email="turista@example.com")

    response = await client.post(URL, json={"email": "Turista@EXAMPLE.com"})

    assert response.status_code == 200
    mock_send_email.assert_called_once_with(
        email_to=tourist.email, first_name=tourist.first_name, token=ANY, base_url=FRONTEND_URL
    )


@pytest.mark.parametrize(
    "payload",
    [{"email": "no-es-un-correo"}, {"email": None}, {}],
    ids=["malformed", "null", "missing"],
)
async def test_invalid_body_is_422_and_sends_nothing(
    client, persist_user, mock_send_email, payload
):
    """Unhappy path: a body that is not one address is rejected before any lookup."""
    await persist_user(is_active=False, email="turista@example.com")

    response = await client.post(URL, json=payload)

    assert response.status_code == 422
    assert [error["raw_field"] for error in response.json()["detalle"]] == ["email"]
    mock_send_email.assert_not_called()


async def test_link_is_built_from_frontend_url(client, persist_user, mock_send_email):
    """Edge case: the link base is the injected frontend_url, without its trailing slash."""
    settings = get_settings().model_copy(update={"frontend_url": "https://front.example/"})
    app.dependency_overrides[get_settings] = lambda: settings
    tourist = await persist_user(is_active=False)

    response = await client.post(URL, json={"email": tourist.email})

    assert response.status_code == 200
    mock_send_email.assert_called_once_with(
        email_to=tourist.email,
        first_name=tourist.first_name,
        token=ANY,
        base_url="https://front.example",
    )


async def test_route_declares_its_response_schema(client):
    """Edge case: the 200 answer is MessageResponse in the OpenAPI, two required keys, no more."""
    spec = (await client.get("/openapi.json")).json()

    answer = spec["paths"][URL]["post"]["responses"]["200"]["content"]["application/json"]
    assert answer["schema"] == {"$ref": "#/components/schemas/MessageResponse"}
    schema = spec["components"]["schemas"]["MessageResponse"]
    assert {name: field.get("type") for name, field in schema["properties"].items()} == {
        "success": "boolean",
        "message": "string",
    }
    assert sorted(schema["required"]) == ["message", "success"]
