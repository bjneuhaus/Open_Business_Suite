"""Application catalog service (R015 - Application Catalog).

This module provides a minimal, read-only catalog of applications that
the platform can install and manage. It is the foundation for the
later web installer flow (configuration wizard, installation start,
progress display, etc.), but this module itself contains none of that
logic.

Scope boundary: no configuration wizard (R016), no installation
trigger (R017), no progress tracking (R018/R019) — this is purely a
service-layer building block, following the same pattern as
``PlatformService`` and ``PodmanService``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationCatalogEntry:
    """Describes a single application the platform can manage.

    Attributes:
        id: Stable, unique identifier for the application, e.g.
            ``"opencloud"``.
        name: Human-readable display name, e.g. ``"OpenCloud"``.
        description: Short, human-readable description of the
            application.
    """

    id: str
    name: str
    description: str


class ApplicationCatalogService:
    """Provides the catalog of applications available on the platform.

    The catalog is currently a small, hardcoded list containing only
    OpenCloud, matching the project's approach of implementing
    OpenCloud first and abstracting a general catalog/plugin mechanism
    only once more applications exist (see PROJECT.md, "Modulsystem").
    """

    def get_applications(self) -> tuple[ApplicationCatalogEntry, ...]:
        """Return all applications currently in the catalog.

        Returns:
            An immutable tuple of ``ApplicationCatalogEntry`` instances.
        """
        return (
            ApplicationCatalogEntry(
                id="opencloud",
                name="OpenCloud",
                description=(
                    "Open-Source-Plattform fuer Dateispeicherung und "
                    "Zusammenarbeit; erste Referenzanwendung der "
                    "Sovereign Business Suite."
                ),
            ),
        )
