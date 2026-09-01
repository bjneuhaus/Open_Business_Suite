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

from pathlib import Path

import pytest

from sovereign_business_suite.app import create_app
from sovereign_business_suite.services.application_catalog_service import (
    ApplicationCatalogEntry,
    ApplicationCatalogService,
)
from sovereign_business_suite.services.command_runner import CommandResult
from sovereign_business_suite.services.opencloud_configuration_wizard import (
    ConfigurationValidationResult,
    OpenCloudConfigurationWizardService,
)
from sovereign_business_suite.services.opencloud_service import (
    OpenCloudConfig,
    OpenCloudService,
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


def test_configure_get_returns_200_with_form() -> None:
    """GET /configure must render the configuration form."""
    app = create_app()

    response = app.test_client().get("/configure")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "host_port" in html
    assert "config_dir" in html
    assert "data_dir" in html


def test_configure_post_valid_submission_shows_confirmation(
    monkeypatch, tmp_path
) -> None:
    """POST /configure with valid values must show a confirmation."""
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    config_dir = home / "opencloud" / "opencloud-config"
    data_dir = home / "opencloud" / "opencloud-data"
    app = create_app()

    response = app.test_client().post(
        "/configure",
        data={
            "host_port": "9200",
            "config_dir": str(config_dir),
            "data_dir": str(data_dir),
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "9200" in html
    assert str(config_dir) in html
    assert "erfolgreich" in html.lower() or "gültig" in html.lower()
    assert 'action="/install"' in html
    assert "Installation starten" in html


def test_configure_post_invalid_submission_shows_errors() -> None:
    """POST /configure with invalid values must show validation errors."""
    app = create_app()

    response = app.test_client().post(
        "/configure",
        data={"host_port": "not-a-number", "config_dir": "", "data_dir": ""},
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "ganze Zahl" in html
    assert "Verzeichnispfad" in html


def test_configure_post_does_not_trigger_installation(monkeypatch) -> None:
    """POST /configure must never call OpenCloudService.install()."""
    install_calls = []
    monkeypatch.setattr(
        "sovereign_business_suite.services.opencloud_service.OpenCloudService.install",
        lambda self: install_calls.append(True),
    )
    app = create_app()

    app.test_client().post(
        "/configure",
        data={
            "host_port": "9200",
            "config_dir": "/home/training/opencloud/opencloud-config",
            "data_dir": "/home/training/opencloud/opencloud-data",
        },
    )

    assert install_calls == []


def test_configure_route_renders_wizard_service_output(monkeypatch) -> None:
    """POST /configure must render exactly what the wizard service returns.

    Explicit web-layer-to-service integration check, mirroring the
    existing checks for '/' and '/catalog': replaces
    OpenCloudConfigurationWizardService.validate() with a distinctive
    stand-in result and asserts that value — not any hardcoded text in
    the route or template — ends up in the rendered response.
    """
    stand_in_result = ConfigurationValidationResult(
        is_valid=False,
        errors={"host_port": "Distinctive stand-in host_port error message."},
        host_port=None,
        config_dir="/distinctive/stand-in/config-dir",
        data_dir="/distinctive/stand-in/data-dir",
    )
    monkeypatch.setattr(
        OpenCloudConfigurationWizardService,
        "validate",
        lambda self, host_port, config_dir, data_dir: stand_in_result,
    )

    app = create_app()
    response = app.test_client().post(
        "/configure",
        data={
            "host_port": "irrelevant",
            "config_dir": "irrelevant",
            "data_dir": "irrelevant",
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert stand_in_result.errors["host_port"] in html


def test_catalog_page_links_to_configuration_wizard() -> None:
    """The catalog page must link to the configuration wizard.

    The catalog lists installable applications; from there an
    administrator needs a way to reach the configuration wizard for
    the listed OpenCloud entry.
    """
    app = create_app()

    response = app.test_client().get("/catalog")
    html = response.get_data(as_text=True)

    assert 'href="/configure"' in html


def test_install_route_starts_opencloud_once_for_valid_submission(
    monkeypatch, tmp_path
) -> None:
    """POST /install starts OpenCloud once and reports the immediate state."""
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    config_dir = home / "opencloud" / "config"
    data_dir = home / "opencloud" / "data"
    install_calls = []
    monkeypatch.setattr(
        OpenCloudService,
        "install",
        lambda self: install_calls.append(True)
        or CommandResult(returncode=0, stdout="", stderr=""),
    )
    app = create_app()

    response = app.test_client().post(
        "/install",
        data={
            "host_port": "9321",
            "config_dir": str(config_dir),
            "data_dir": str(data_dir),
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Installationsstart wurde ausgelöst" in html
    assert len(install_calls) == 1


def test_install_post_invalid_submission_shows_errors_without_installing(
    monkeypatch,
) -> None:
    """POST /install with invalid values must show errors, no install.

    R017 re-validates the submission before installing. Invalid input
    must never reach OpenCloudService.install().
    """
    install_calls = []
    monkeypatch.setattr(
        OpenCloudService,
        "install",
        lambda self: install_calls.append(True),
    )
    app = create_app()

    response = app.test_client().post(
        "/install",
        data={"host_port": "not-a-number", "config_dir": "", "data_dir": ""},
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "ganze Zahl" in html
    assert install_calls == []


def test_install_post_rejects_paths_outside_allowlist_without_installing(
    monkeypatch, tmp_path
) -> None:
    """R017 must reject syntactically valid paths outside ~/opencloud."""
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    install_calls = []
    monkeypatch.setattr(
        OpenCloudService,
        "install",
        lambda self: install_calls.append(True),
    )

    app = create_app()
    response = app.test_client().post(
        "/install",
        data={
            "host_port": "9200",
            "config_dir": str(tmp_path / "outside-config"),
            "data_dir": str(tmp_path / "outside-data"),
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "zulässigen OpenCloud-Speicherbereich" in html
    assert install_calls == []


def test_install_post_rejects_dot_dot_escape_without_installing(monkeypatch, tmp_path):
    """R017 must reject a path escaping ~/opencloud through '..'."""
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    install_calls = []
    monkeypatch.setattr(
        OpenCloudService,
        "install",
        lambda self: install_calls.append(True),
    )

    app = create_app()
    response = app.test_client().post(
        "/install",
        data={
            "host_port": "9200",
            "config_dir": str(home / "opencloud" / ".." / "escaped-config"),
            "data_dir": str(home / "opencloud" / "data"),
        },
    )

    assert response.status_code == 200
    assert "zulässigen OpenCloud-Speicherbereich" in response.get_data(as_text=True)
    assert install_calls == []


def test_install_post_rejects_symlink_resolving_outside_without_installing(
    monkeypatch, tmp_path
):
    """R017 must reject an existing symlink whose target is outside the root."""
    home = tmp_path / "home"
    root = home / "opencloud"
    root.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "config-link").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    install_calls = []
    monkeypatch.setattr(
        OpenCloudService,
        "install",
        lambda self: install_calls.append(True),
    )

    app = create_app()
    response = app.test_client().post(
        "/install",
        data={
            "host_port": "9200",
            "config_dir": str(root / "config-link"),
            "data_dir": str(root / "data"),
        },
    )

    assert response.status_code == 200
    assert "zulässigen OpenCloud-Speicherbereich" in response.get_data(as_text=True)
    assert install_calls == []


def test_install_route_uses_normalized_values_for_service_configuration(
    monkeypatch, tmp_path
) -> None:
    """POST /install passes normalized wizard values to the service layer."""
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    root = home / "opencloud"
    expected_config = OpenCloudConfig(
        image="stand-in-image",
        container_name="stand-in-opencloud",
        host_port=9321,
        config_dir=str(root / "config"),
        data_dir=str(root / "data"),
    )
    factory_calls = []
    service_configs = []

    def fake_default_config(config_dir, data_dir, host_port):
        factory_calls.append((config_dir, data_dir, host_port))
        return expected_config

    class StandInOpenCloudService:
        def __init__(self, config, command_runner) -> None:
            service_configs.append(config)

        def install(self):
            return CommandResult(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "sovereign_business_suite.app.default_opencloud_config", fake_default_config
    )
    monkeypatch.setattr(
        "sovereign_business_suite.app.OpenCloudService", StandInOpenCloudService
    )

    app = create_app()
    response = app.test_client().post(
        "/install",
        data={
            "host_port": " 9321 ",
            "config_dir": f" {root / 'nested' / '..' / 'config'} ",
            "data_dir": f" {root / 'data'} ",
        },
    )

    assert response.status_code == 200
    assert factory_calls == [(str(root / "config"), str(root / "data"), 9321)]
    assert service_configs == [expected_config]


def test_install_post_reports_failed_install_result(monkeypatch, tmp_path) -> None:
    """POST /install must show a clear failure message on a bad result."""
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    root = home / "opencloud"
    stand_in_failure = CommandResult(
        returncode=1, stdout="", stderr="distinctive stand-in failure reason"
    )
    monkeypatch.setattr(
        OpenCloudService,
        "install",
        lambda self: stand_in_failure,
    )

    app = create_app()
    response = app.test_client().post(
        "/install",
        data={
            "host_port": "9200",
            "config_dir": str(root / "config"),
            "data_dir": str(root / "data"),
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Installationsstart konnte nicht ausgelöst werden" in html
    assert stand_in_failure.stderr not in html


def test_install_post_handles_install_exception_without_leaking_details(
    monkeypatch, tmp_path
) -> None:
    """Unexpected service errors must propagate instead of being masked."""
    secret_detail = "secret-argument-value"
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))

    def fail_install(self):
        raise RuntimeError(secret_detail)

    monkeypatch.setattr(OpenCloudService, "install", fail_install)
    app = create_app()
    app.config["TESTING"] = True

    with pytest.raises(RuntimeError, match=secret_detail):
        app.test_client().post(
            "/install",
            data={
                "host_port": "9200",
                "config_dir": str(home / "opencloud" / "config"),
                "data_dir": str(home / "opencloud" / "data"),
            },
        )


def test_install_get_returns_405() -> None:
    """GET /install must not be allowed; installation is a POST-only action."""
    app = create_app()

    response = app.test_client().get("/install")

    assert response.status_code == 405
