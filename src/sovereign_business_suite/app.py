"""Minimal Flask application for the Sovereign Business Suite.

R004/R005/R015/R016/R017.

This module provides the application factory, the existing start page, an
administrator-facing application catalog, a configuration wizard, and an
installation-start action for OpenCloud. It intentionally contains no
authentication, database access, background jobs, or progress/result
tracking.

Since R005, the start page's content comes from the Application Service
Layer (``services.platform_service``) instead of being hardcoded in the
route or the template. Since R015, the catalog route follows the same
boundary with ``ApplicationCatalogService``. Since R016, the ``/configure``
route follows the same boundary with
``OpenCloudConfigurationWizardService`` — it only validates input and
never triggers an installation or persists anything. Since R017, the
``/install`` route re-validates the same input and, if valid, triggers a
single synchronous ``OpenCloudService.install()`` call — no background
job, no progress display, and no dedicated result page (R018–R020).
"""

from dataclasses import replace

from flask import Flask, render_template, request

from sovereign_business_suite.services.application_catalog_service import (
    ApplicationCatalogService,
)
from sovereign_business_suite.services.command_runner import CommandRunner
from sovereign_business_suite.services.opencloud_configuration_wizard import (
    OpenCloudConfigurationWizardService,
)
from sovereign_business_suite.services.opencloud_installation_policy import (
    INSTALLATION_PATH_ERROR,
    normalize_installation_path,
)
from sovereign_business_suite.services.opencloud_service import (
    OpenCloudService,
    default_opencloud_config,
)
from sovereign_business_suite.services.platform_service import PlatformService


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A configured Flask application instance, ready to serve the
        start page, application catalog, configuration wizard, and
        installation-start action.
    """
    app = Flask(__name__)
    platform_service = PlatformService()
    application_catalog_service = ApplicationCatalogService()
    configuration_wizard_service = OpenCloudConfigurationWizardService()

    @app.route("/")
    def index() -> str:
        """Render the server-side start page.

        Returns:
            Rendered HTML for the start page, populated with platform
            information from the Application Service Layer.
        """
        info = platform_service.get_platform_info()
        return render_template("index.html", info=info)

    @app.route("/catalog")
    def catalog() -> str:
        """Render the administrator-facing application catalog.

        Returns:
            Rendered HTML containing the catalog service's application
            entries.
        """
        applications = application_catalog_service.get_applications()
        return render_template("catalog.html", applications=applications)

    @app.route("/configure", methods=["GET", "POST"])
    def configure() -> str:
        """Render and process the OpenCloud configuration wizard.

        On ``GET``, shows an empty form. On ``POST``, validates the
        submitted values via ``OpenCloudConfigurationWizardService``
        and shows either the validation errors or a confirmation of
        the accepted values. No installation is triggered and nothing
        is persisted — this route only validates input.

        Returns:
            Rendered HTML for the form, validation errors, or a
            confirmation of valid input.
        """
        result = None
        if request.method == "POST":
            result = configuration_wizard_service.validate(
                host_port=request.form.get("host_port", ""),
                config_dir=request.form.get("config_dir", ""),
                data_dir=request.form.get("data_dir", ""),
            )
        return render_template("configure.html", result=result)

    @app.route("/install", methods=["POST"])
    def install() -> str:
        """Re-validate the submission and start OpenCloud once if valid.

        The submitted values are validated again with the same
        ``OpenCloudConfigurationWizardService`` used by ``/configure``
        — the wizard's own validation is never trusted blindly across
        requests. If validation fails, the same error display as
        ``/configure`` is shown and no installation is attempted. If
        validation succeeds, ``OpenCloudService.install()`` is called
        exactly once, synchronously, and its immediate
        ``CommandResult`` is shown. There is no background job, no
        progress tracking, and no dedicated result page — those are
        R018–R020.

        Returns:
            Rendered HTML showing either validation errors or the
            immediate outcome of the installation attempt.
        """
        result = configuration_wizard_service.validate(
            host_port=request.form.get("host_port", ""),
            config_dir=request.form.get("config_dir", ""),
            data_dir=request.form.get("data_dir", ""),
        )
        if not result.is_valid:
            return render_template("configure.html", result=result)

        normalized_config_dir = normalize_installation_path(result.config_dir)
        normalized_data_dir = normalize_installation_path(result.data_dir)
        path_errors = {}
        if normalized_config_dir is None:
            path_errors["config_dir"] = INSTALLATION_PATH_ERROR
        if normalized_data_dir is None:
            path_errors["data_dir"] = INSTALLATION_PATH_ERROR
        if path_errors:
            result = replace(
                result,
                is_valid=False,
                errors={**result.errors, **path_errors},
            )
            return render_template("configure.html", result=result)

        # The wizard contract guarantees this for a valid result. Keep the
        # invariant explicit at runtime so it also applies under ``python -O``.
        if result.host_port is None:
            raise RuntimeError("Gültige Konfiguration ohne Portwert.")

        service = OpenCloudService(
            default_opencloud_config(
                config_dir=str(normalized_config_dir),
                data_dir=str(normalized_data_dir),
                host_port=result.host_port,
            ),
            CommandRunner(),
        )
        # No blanket exception handling here: CommandRunner.run() never
        # raises (it converts timeouts and a missing executable into a
        # CommandResult itself), so install() has no expected failure
        # path that needs suppressing. An unexpected exception is a bug
        # and should surface as Flask's default 500 response rather
        # than being silently swallowed into a generic "success"-shaped
        # page — Flask's default error handling already avoids leaking
        # exception details as long as debug/testing mode is off.
        install_result = service.install()
        return render_template(
            "install.html", result=result, install_result=install_result
        )

    return app
