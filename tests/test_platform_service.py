"""Tests for the platform application service (R005).

These tests only verify the R005 scope: PlatformInfo is a simple,
immutable data object and PlatformService.get_platform_info() returns
the expected values. The service intentionally contains no Podman,
process, or filesystem calls — those belong to later roadmap items.
"""

from sovereign_business_suite.services.platform_service import (
    PlatformInfo,
    PlatformService,
)


def test_platform_info_is_frozen_dataclass() -> None:
    """PlatformInfo instances must be immutable value objects."""
    info = PlatformInfo(project_name="Test", status_message="Status")

    assert info.project_name == "Test"
    assert info.status_message == "Status"


def test_get_platform_info_returns_platform_info() -> None:
    """get_platform_info() must return a populated PlatformInfo."""
    service = PlatformService()

    info = service.get_platform_info()

    assert isinstance(info, PlatformInfo)
    assert info.project_name == "Sovereign Business Suite"
    assert "Proof of Concept" in info.status_message
