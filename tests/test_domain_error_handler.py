"""Unit tests for the unified DomainError global handler registered in app.main."""

import json

import pytest
from starlette.requests import Request

from app.core.exceptions import (
    AccountNotActiveError,
    AlreadyExistsError,
    AuthorizationError,
    BusinessRuleViolationError,
    DomainError,
    InvalidCredentialsError,
    InvalidImageUrlError,
    InvalidVerificationTokenError,
    NotFoundError,
    StorageUnavailableError,
    UnsupportedMediaTypeError,
)
from app.main import domain_error_handler

# The handler never reads the request; a bare ASGI scope satisfies its type.
REQUEST = Request({"type": "http"})


class UnknownDomainError(DomainError):
    """Test-only DomainError subtype deliberately absent from the mapping table."""


@pytest.mark.parametrize(
    ("exc", "expected_status"),
    [
        (AuthorizationError("privileges"), 403),
        (NotFoundError("missing"), 404),
        (AlreadyExistsError("duplicate"), 400),
        (InvalidCredentialsError("credentials"), 401),
        (AccountNotActiveError("inactive"), 403),
        (InvalidVerificationTokenError("token"), 400),
        (BusinessRuleViolationError("rule"), 400),
        (StorageUnavailableError("outage"), 503),
        (UnsupportedMediaTypeError("mime"), 415),
        (InvalidImageUrlError("url"), 400),
    ],
)
async def test_known_domain_errors_map_to_documented_status(exc, expected_status):
    """Each mapped subtype resolves to its documented HTTP status echoing detail."""
    response = await domain_error_handler(REQUEST, exc)

    assert response.status_code == expected_status
    assert json.loads(response.body) == {"detail": exc.detail}


async def test_invalid_credentials_response_advertises_bearer_scheme():
    """401 responses must carry the WWW-Authenticate Bearer challenge."""
    response = await domain_error_handler(REQUEST, InvalidCredentialsError("credentials"))

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_non_401_responses_omit_authenticate_header():
    """Edge case: the Bearer challenge is exclusive to authentication failures."""
    response = await domain_error_handler(REQUEST, AccountNotActiveError("inactive"))

    assert response.status_code == 403
    assert "www-authenticate" not in response.headers


async def test_unmapped_subtype_falls_back_to_internal_server_error():
    """Edge case: unknown DomainError subtypes degrade to 500 with the detail intact."""
    response = await domain_error_handler(REQUEST, UnknownDomainError("unexpected"))

    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "unexpected"}
