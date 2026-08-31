"""Smoke tests for the sovereign_business_suite package.

These tests only verify that the minimal Python package structure
introduced in R002 is importable and exposes a version string. They do
not test any application behavior (Flask, Podman, etc.) since that is
out of scope for R002.
"""

import sovereign_business_suite


def test_package_is_importable() -> None:
    """The package must be importable without errors."""
    assert sovereign_business_suite is not None


def test_package_has_version() -> None:
    """The package exposes a non-empty __version__ string."""
    assert isinstance(sovereign_business_suite.__version__, str)
    assert sovereign_business_suite.__version__ != ""
