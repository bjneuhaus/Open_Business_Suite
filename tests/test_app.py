"""Tests for the minimal Flask application (R004).

These tests only verify the R004 scope: the app factory works, the
start page responds successfully, and it contains the expected,
recognizable content. No authentication, database, Podman integration,
job system, or additional business logic is tested here since none of
that exists yet.
"""

from sovereign_business_suite.app import create_app


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
