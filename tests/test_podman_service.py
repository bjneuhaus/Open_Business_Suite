"""Tests for the Podman availability service (R006).

These tests only verify the reduced R006 scope: whether the ``podman``
executable is present on PATH. No subprocess calls, version checks, or
container actions are involved — those belong to later roadmap items
(R007 Command Execution, R012+ OpenCloud Installation).
"""

from sovereign_business_suite.services.podman_service import PodmanService


def test_is_available_true_when_podman_on_path(monkeypatch) -> None:
    """is_available() must return True when 'podman' is found on PATH."""
    monkeypatch.setattr(
        "sovereign_business_suite.services.podman_service.shutil.which",
        lambda executable: "/usr/bin/podman",
    )
    service = PodmanService()

    assert service.is_available() is True


def test_is_available_false_when_podman_missing(monkeypatch) -> None:
    """is_available() must return False when 'podman' is not on PATH."""
    monkeypatch.setattr(
        "sovereign_business_suite.services.podman_service.shutil.which",
        lambda executable: None,
    )
    service = PodmanService()

    assert service.is_available() is False


def test_is_available_checks_for_podman_executable_name(monkeypatch) -> None:
    """is_available() must look up exactly the 'podman' executable name."""
    checked_names = []

    def fake_which(executable: str) -> str | None:
        checked_names.append(executable)
        return None

    monkeypatch.setattr(
        "sovereign_business_suite.services.podman_service.shutil.which",
        fake_which,
    )
    service = PodmanService()

    service.is_available()

    assert checked_names == ["podman"]
