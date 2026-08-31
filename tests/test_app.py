"""Tests for the minimal Flask application (R004/R005).

These tests only verify the R004 scope: the app factory works, the
start page responds successfully, and it contains the expected,
recognizable content. No authentication, database, Podman integration,
job system, or additional business logic is tested here since none of
that exists yet.

The R005 follow-up test below additionally verifies, via monkeypatch,
that the ``/`` route actually renders whatever
``PlatformService.get_platform_info()`` returns — closing the gap that
the original R004/R005 tests only checked for values that happened to
be identical to the service's hardcoded output.
"""

from sovereign_business_suite.app import create_app
from sovereign_business_suite.services.application_catalog_service import (
    ApplicationCatalogEntry,
    ApplicationCatalogService,
)
from sovereign_business_suite.services.platform_service import (
    PlatformInfo,
    PlatformService,
)


def test_create_app_returns_flask_app() -> None:
    """create_app() must return a usable Flask application instance."""
    app = create_app()
    assert app is not None
    assert app.name == "sovereign_business_suite.app"


def test_index_route_returns_200() -> None:
    """GET / must succeed."""
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_index_route_shows_project_title_and_poc_hint() -> None:
    """The start page must show the project name and a clear PoC hint."""
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Sovereign Business Suite" in html
    assert "Proof of Concept" in html


def test_index_route_renders_platform_service_output(monkeypatch) -> None:
    """GET / must render exactly what PlatformService returns.

    This is an explicit web-layer-to-service integration check: it
    replaces PlatformService.get_platform_info() with a distinctive
    stand-in value and asserts that value — not any hardcoded text in
    the route or template — ends up in the rendered response.
    """
    stand_in_info = PlatformInfo(
        project_name="Integrationstest-Plattform",
        status_message="Eindeutiger Stand-in-Statustext für den Test.",
    )
    monkeypatch.setattr(
        PlatformService,
        "get_platform_info",
        lambda self: stand_in_info,
    )

    app = create_app()
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert stand_in_info.project_name in html
    assert stand_in_info.status_message in html


def test_catalog_route_renders_application_catalog_service_output(monkeypatch) -> None:
    """GET /catalog must render the exact catalog service output."""
    stand_in_applications = (
        ApplicationCatalogEntry(
            id="distinctive-catalog-id",
            name="Distinctive Catalog Name",
            description="Distinctive catalog description for integration.",
        ),
    )
    monkeypatch.setattr(
        ApplicationCatalogService,
        "get_applications",
        lambda self: stand_in_applications,
    )

    app = create_app()
    response = app.test_client().get("/catalog")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert stand_in_applications[0].id in html
    assert stand_in_applications[0].name in html
    assert stand_in_applications[0].description in html
