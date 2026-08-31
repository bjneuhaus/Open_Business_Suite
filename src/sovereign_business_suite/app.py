"""Minimal Flask application for the Sovereign Business Suite (R004/R005/R015/R016).

This module provides the application factory, the existing start page, an
administrator-facing application catalog, and a configuration wizard for
OpenCloud. It intentionally contains no authentication, database access,
Podman integration, background jobs, or lifecycle actions.

Since R005, the start page's content comes from the Application Service
Layer (``services.platform_service``) instead of being hardcoded in the
route or the template. Since R015, the catalog route follows the same
boundary with ``ApplicationCatalogService``. Since R016, the ``/configure``
route follows the same boundary with
``OpenCloudConfigurationWizardService`` — it only validates input and
never triggers an installation or persists anything.
"""

from flask import Flask, render_template, request

from sovereign_business_suite.services.application_catalog_service import (
    ApplicationCatalogService,
)
from sovereign_business_suite.services.opencloud_configuration_wizard import (
    OpenCloudConfigurationWizardService,
)
from sovereign_business_suite.services.platform_service import PlatformService


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A configured Flask application instance, ready to serve the
        start page, application catalog, and configuration wizard.
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

    return app
