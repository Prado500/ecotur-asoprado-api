"""Route guard tests (ADR-0012, decision 4; BE-39).

PROTECTED_ROUTES lists every protected route as app.routes declares it (method and path template),
with the guard that protects it; PUBLIC_ROUTES lists every other route. The inventory test keeps
both tables equal to app.routes, so a route added without an entry, or an entry whose route is
gone, fails the suite.
"""

from typing import Any, Literal, NamedTuple

import pytest
from starlette.routing import Route

from app.main import app
from app.models.user import UserRole


class ProtectedRoute(NamedTuple):
    """A protected route, keyed as app.routes declares it, with the guard that protects it.

    Attributes:
        method: HTTP method, upper case.
        path: Path template as declared in app.routes (e.g. "/servicios/{service_id}").
        guard: "admin" for get_current_admin_user, "user" for get_current_user.
        body: JSON body sent with the request; None sends no body.
    """

    method: str
    path: str
    guard: Literal["admin", "user"]
    body: dict[str, Any] | None = None


# Empty on purpose: if a guard let a tourist through, body validation would answer 422, not 403.
# A valid body to POST /usuarios/admin gets 403 from the provisioning policy and hides the guard.
_EMPTY_BODY: dict[str, Any] = {}

PROTECTED_ROUTES: tuple[ProtectedRoute, ...] = (
    ProtectedRoute("GET", "/usuarios/", "admin"),
    ProtectedRoute("GET", "/usuarios/admin/eliminados", "admin"),
    ProtectedRoute("PATCH", "/usuarios/{cedula}/recuperar", "admin"),
    ProtectedRoute("POST", "/usuarios/admin", "admin", _EMPTY_BODY),
    ProtectedRoute("POST", "/servicios/upload-images/", "admin", _EMPTY_BODY),
    ProtectedRoute("POST", "/servicios/", "admin", _EMPTY_BODY),
    ProtectedRoute("GET", "/servicios/admin/inactivos", "admin"),
    ProtectedRoute("GET", "/servicios/admin/eliminados", "admin"),
    ProtectedRoute("PUT", "/servicios/{service_id}", "admin", _EMPTY_BODY),
    ProtectedRoute("PATCH", "/servicios/{service_id}/activar", "admin"),
    ProtectedRoute("PATCH", "/servicios/{service_id}/desactivar", "admin"),
    ProtectedRoute("DELETE", "/servicios/{service_id}", "admin"),
    ProtectedRoute("PATCH", "/servicios/{service_id}/recuperar", "admin"),
    ProtectedRoute("GET", "/auditoria/", "admin"),
    ProtectedRoute("GET", "/usuarios/mi-perfil", "user"),
    ProtectedRoute("DELETE", "/usuarios/{cedula}", "user"),
    ProtectedRoute("PATCH", "/usuarios/{cedula}", "user", _EMPTY_BODY),
)

ADMIN_ROUTES: tuple[ProtectedRoute, ...] = tuple(r for r in PROTECTED_ROUTES if r.guard == "admin")

PUBLIC_ROUTES: frozenset[tuple[str, str]] = frozenset(
    {
        ("POST", "/usuarios/registro"),
        ("GET", "/usuarios/verificar-email"),
        ("POST", "/usuarios/login"),
        ("GET", "/servicios/"),
        ("GET", "/"),
        ("GET", "/openapi.json"),
        ("GET", "/docs"),
        ("GET", "/docs/oauth2-redirect"),
        ("GET", "/redoc"),
    }
)

# Path parameters that name no stored row: the guard must answer before any lookup could.
_PATH_PARAMS: dict[str, str] = {"cedula": "0000000000", "service_id": "999"}


def _url(route: ProtectedRoute) -> str:
    """Fill the route's path template with _PATH_PARAMS."""
    return route.path.format(**_PATH_PARAMS)


def _route_id(route: ProtectedRoute) -> str:
    """Name a parametrized case after its route, e.g. "PUT /servicios/{service_id}"."""
    return f"{route.method} {route.path}"


def _declared_routes() -> set[tuple[str, str]]:
    """Collect (method, path template) for every route of the app.

    HEAD is left out: Starlette adds it to every GET route, it is not a route of its own.

    Returns:
        The set of (method, path) pairs declared in app.routes.
    """
    declared: set[tuple[str, str]] = set()
    for route in app.routes:
        assert isinstance(route, Route), f"unexpected route type: {route!r}"
        declared |= {(method, route.path) for method in (route.methods or set()) - {"HEAD"}}
    return declared


def test_every_route_is_listed_as_protected_or_public() -> None:
    """A route in neither table, or an entry with no route behind it, fails here."""
    protected = {(route.method, route.path) for route in PROTECTED_ROUTES}

    assert _declared_routes() == protected | PUBLIC_ROUTES


@pytest.mark.parametrize("route", PROTECTED_ROUTES, ids=_route_id)
async def test_protected_route_rejects_request_without_token(client, route: ProtectedRoute) -> None:
    """Without a token, every protected route answers 401 with the Bearer challenge."""
    response = await client.request(route.method, _url(route), json=route.body)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)


@pytest.mark.parametrize("route", ADMIN_ROUTES, ids=_route_id)
async def test_admin_route_rejects_tourist(
    client, persist_user, make_auth_headers, route: ProtectedRoute
) -> None:
    """A tourist's valid token gets 403 from every admin route, without a Bearer challenge."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.request(
        route.method, _url(route), json=route.body, headers=make_auth_headers(tourist)
    )

    assert response.status_code == 403
    assert "www-authenticate" not in response.headers
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)
