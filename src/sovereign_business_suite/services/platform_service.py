"""Platform application service (R005).

This module defines the Application Service Layer boundary between the
Flask web layer and the platform's own logic, as sketched in
``PROJECT.md`` (Web UI -> Application/Service Layer ->
Installation/Module Layer -> Podman/OS).

R005 only establishes this boundary with a minimal, read-only contract.
It intentionally contains no Podman, process, or filesystem access —
those are introduced in later roadmap items (R006+).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformInfo:
    """Immutable, presentation-agnostic information about the platform.

    Attributes:
        project_name: Human-readable name of the platform.
        status_message: Short status description, e.g. the current
            development phase.
    """

    project_name: str
    status_message: str


class PlatformService:
    """Application service providing platform-level information.

    This service is the single entry point the web layer uses to read
    platform information. It does not know about Flask, HTML, or any
    other presentation concern.
    """

    def get_platform_info(self) -> PlatformInfo:
        """Return the current platform information.

        Returns:
            A ``PlatformInfo`` describing the platform's name and
            current status.
        """
        return PlatformInfo(
            project_name="Sovereign Business Suite",
            status_message=(
                "Proof of Concept für eine modular verwaltete "
                "Open-Source-Unternehmensplattform."
            ),
        )
