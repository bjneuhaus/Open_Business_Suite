"""Minimal Flask application for the Sovereign Business Suite (R004).

This module only provides the application factory and a single start
page. It intentionally contains no authentication, database access,
Podman integration, background jobs, or health-check endpoint — those
belong to later roadmap items.
"""

from flask import Flask, render_template


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A configured Flask application instance, ready to serve the
        minimal start page.
    """
    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        """Render the server-side start page.

        Returns:
            Rendered HTML for the start page.
        """
        return render_template("index.html")

    return app
