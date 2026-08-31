"""Minimal Flask application for the Sovereign Business Suite (R004/R005/R015).

This module provides the application factory, the existing start page, and
an administrator-facing application catalog. It intentionally contains no
authentication, database access, Podman integration, background jobs, or
lifecycle actions.

Since R005, the start page's content comes from the Application Service
Layer (``services.platform_service``) instead of being hardcoded in the
route or the template. Since R015, the catalog route follows the same
boundary with ``ApplicationCatalogService``.
"""

from flask import Flask, render_template

from sovereign_business_suite.services.application_catalog_service import (
    ApplicationCatalogService,
)
from sovereign_business_suite.services.platform_service import PlatformService


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A configured Flask application instance, ready to serve the
        start page and application catalog.
    """
    app = Flask(__name__)
    platform_service = PlatformService()
    application_catalog_service = ApplicationCatalogService()

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

    return app
