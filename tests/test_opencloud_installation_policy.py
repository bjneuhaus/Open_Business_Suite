"""Regression tests for the R017 OpenCloud installation path policy."""

from pathlib import Path

from sovereign_business_suite.services.opencloud_installation_policy import (
    normalize_installation_path,
)


def patch_home(monkeypatch, home: Path) -> None:
    """Make the policy use an isolated home directory."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))


def test_path_outside_allowlist_is_rejected(monkeypatch, tmp_path) -> None:
    """Paths outside Path.home()/opencloud are not installation paths."""
    home = tmp_path / "home"
    patch_home(monkeypatch, home)

    assert normalize_installation_path(str(tmp_path / "outside")) is None


def test_dot_dot_escape_is_rejected(monkeypatch, tmp_path) -> None:
    """A normalized '..' escape beyond the storage root is rejected."""
    home = tmp_path / "home"
    patch_home(monkeypatch, home)
    escaped = home / "opencloud" / "config" / ".." / ".." / "outside"

    assert normalize_installation_path(str(escaped)) is None


def test_existing_symlink_to_outside_is_rejected(monkeypatch, tmp_path) -> None:
    """An existing symlink resolving outside the root is rejected."""
    home = tmp_path / "home"
    root = home / "opencloud"
    root.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = root / "config-link"
    link.symlink_to(outside, target_is_directory=True)
    patch_home(monkeypatch, home)

    assert normalize_installation_path(str(link)) is None


def test_valid_subpath_is_normalized_without_creating_directories(
    monkeypatch, tmp_path
) -> None:
    """A safe child path is returned normalized and validation is read-only."""
    home = tmp_path / "home"
    patch_home(monkeypatch, home)
    root = home / "opencloud"
    candidate = root / "nested" / ".." / "config"

    normalized = normalize_installation_path(str(candidate))

    assert normalized == root / "config"
    assert not root.exists()


def test_storage_root_itself_is_not_a_valid_installation_path(
    monkeypatch, tmp_path
) -> None:
    """The storage root cannot be used as one config/data directory."""
    home = tmp_path / "home"
    patch_home(monkeypatch, home)

    assert normalize_installation_path(str(home / "opencloud")) is None
