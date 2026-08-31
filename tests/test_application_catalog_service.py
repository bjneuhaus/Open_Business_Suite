"""Tests for the application catalog service (R015 - Application Catalog).

These tests only verify the R015 scope: a small, read-only catalog of
installable applications. No configuration wizard (R016), installation
trigger (R017), or lifecycle logic is part of this service.
"""

from dataclasses import fields

from sovereign_business_suite.services.application_catalog_service import (
    ApplicationCatalogEntry,
    ApplicationCatalogService,
)


def test_application_catalog_entry_is_a_frozen_dataclass() -> None:
    """ApplicationCatalogEntry instances must be immutable value objects."""
    entry = ApplicationCatalogEntry(
        id="opencloud",
        name="OpenCloud",
        description="Test description",
    )

    assert {field.name for field in fields(entry)} == {"id", "name", "description"}
    assert entry.id == "opencloud"
    assert entry.name == "OpenCloud"
    assert entry.description == "Test description"


def test_get_applications_returns_opencloud_as_only_entry() -> None:
    """The catalog must currently list exactly OpenCloud."""
    service = ApplicationCatalogService()

    applications = service.get_applications()

    assert len(applications) == 1
    assert applications[0].id == "opencloud"
    assert applications[0].name == "OpenCloud"
    assert applications[0].description == (
        "Open-Source-Plattform fuer Dateispeicherung und "
        "Zusammenarbeit; erste Referenzanwendung der "
        "Sovereign Business Suite."
    )


def test_get_applications_returns_a_tuple() -> None:
    """get_applications() must return an immutable tuple, not a list."""
    service = ApplicationCatalogService()

    applications = service.get_applications()

    assert isinstance(applications, tuple)
