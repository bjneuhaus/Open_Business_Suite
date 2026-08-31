"""Minimal Flask application for the Sovereign Business Suite (R004/R005).

This module only provides the application factory and a single start
page. It intentionally contains no authentication, database access,
Podman integration, background jobs, or health-check endpoint — those
belong to later roadmap items.

Since R005, the start page's content comes from the Application Service
Layer (``services.platform_service``) instead of being hardcoded in the
route or the template, establishing the boundary between the web layer
and the platform's own logic.
"""

from flask import Flask, render_template

from sovereign_business_suite.services.platform_service import PlatformService


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A configured Flask application instance, ready to serve the
        minimal start page.
    """
    app = Flask(__name__)
    platform_service = PlatformService()

    @app.route("/")
    def index() -> str:
        """Render the server-side start page.

        Returns:
            Rendered HTML for the start page, populated with platform
            information from the Application Service Layer.
        """
        info = platform_service.get_platform_info()
        return render_template("index.html", info=info)

    return app
