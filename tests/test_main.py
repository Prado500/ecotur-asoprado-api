import pytest
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.main import app, parse_cors_origins

UNKNOWN_ORIGIN = "https://evil.example"

ROOT_BODY = {
    "status": "ok",
    "message": "Ecotur-ASOPRADO API (v0.2.0) está en línea",
}


def _allowed_origins() -> list[str]:
    """Returns the allow-list the app's only CORS middleware was registered with."""
    [cors] = [middleware for middleware in app.user_middleware if middleware.cls is CORSMiddleware]
    origins = cors.kwargs["allow_origins"]
    assert isinstance(origins, list)
    return origins


async def test_read_root(client):
    """
    verifies the root health check endpoint responds with an 200 code and the defined
    response message.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == ROOT_BODY


def test_parse_cors_origins_single_origin():
    assert parse_cors_origins("http://localhost:3000") == ["http://localhost:3000"]


def test_parse_cors_origins_trims_and_drops_empties():
    assert parse_cors_origins(" https://a.example , ,https://b.example, ") == [
        "https://a.example",
        "https://b.example",
    ]


@pytest.mark.parametrize("raw", ["", ",,", "  "])
def test_parse_cors_origins_empty_value_is_empty_list(raw):
    assert parse_cors_origins(raw) == []


@pytest.mark.parametrize(
    "raw",
    ["*", " * ", "https://a.example,*", "https://*.azurestaticapps.net"],
)
def test_parse_cors_origins_rejects_wildcard(raw):
    with pytest.raises(ValueError):
        parse_cors_origins(raw)


def test_default_cors_origins_is_local_frontend():
    assert parse_cors_origins(Settings.model_fields["cors_origins"].default) == [
        "http://localhost:3000"
    ]


def test_configured_cors_origins_have_no_wildcard():
    assert _allowed_origins() == parse_cors_origins(get_settings().cors_origins)
    assert isinstance(_allowed_origins(), list)
    assert _allowed_origins()
    assert all("*" not in origin for origin in _allowed_origins())


async def test_cors_allowed_origin_is_echoed_without_credentials(client):
    allowed = _allowed_origins()[0]

    response = await client.get("/", headers={"Origin": allowed})

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == allowed
    assert "origin" in response.headers.get("vary", "").lower()
    assert response.headers.get("access-control-allow-credentials") is None
    assert response.json() == ROOT_BODY


async def test_cors_unknown_origin_gets_no_cors_headers(client):
    assert UNKNOWN_ORIGIN not in _allowed_origins()

    response = await client.get("/", headers={"Origin": UNKNOWN_ORIGIN})

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") is None


async def test_cors_preflight_allowed_origin(client):
    allowed = _allowed_origins()[0]

    response = await client.options(
        "/",
        headers={
            "Origin": allowed,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == allowed
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower()
    assert response.headers.get("access-control-allow-credentials") is None


async def test_cors_preflight_unknown_origin_is_rejected(client):
    response = await client.options(
        "/",
        headers={
            "Origin": UNKNOWN_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None


async def test_request_without_origin_bypasses_cors(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") is None
