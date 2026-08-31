"""Podman availability service (R006).

This module provides a minimal, intentionally reduced check for whether
the ``podman`` command-line tool is installed and reachable on the
host's PATH.

Scope boundary (see WORKFLOW.md / DoD): this service performs no
subprocess calls, no version checks, and no container actions. Running
``podman`` itself belongs to R007 (Command Execution); starting,
stopping, or inspecting containers belongs to R012+ (OpenCloud
Installation and later application roadmap items).
"""

import shutil


class PodmanService:
    """Application service reporting whether Podman is available.

    This service only answers the question "is the ``podman``
    executable present on PATH?". It does not invoke Podman, does not
    read its version, and has no side effects.
    """

    def is_available(self) -> bool:
        """Check whether the ``podman`` executable is on PATH.

        Returns:
            True if ``podman`` is found on PATH, False otherwise.
        """
        return shutil.which("podman") is not None
