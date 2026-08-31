"""Loads the pinned OpenCloud image reference from the single,
versioned source of truth: ``config/opencloud-image.env`` at the
repository root.

This module exists so the image repository/digest are defined exactly
once in a plain, human-editable file, and every consumer (the
OpenCloud service default configuration, the provisioning script's
documentation, and any future tooling) reads the same values instead
of duplicating them.

Scope boundary: this module only parses two ``KEY=value`` lines. It
performs no registry calls and does not verify that the digest still
exists remotely — updating the digest after re-verifying it against
the registry is a manual, documented step (see
config/opencloud-image.env and docs/opencloud-service.md).
"""

from pathlib import Path

#: Path to the repository-root config file, resolved relative to this
#: module so it works regardless of the current working directory.
_CONFIG_FILE = Path(__file__).resolve().parents[2] / "config" / "opencloud-image.env"


def _load_config_values(config_file: Path) -> dict[str, str]:
    """Parse a simple ``KEY=value`` file, ignoring comments/blank lines.

    Args:
        config_file: Path to the file to parse.

    Returns:
        A mapping of key to value for every non-comment, non-blank
        line containing an ``=``.
    """
    values: dict[str, str] = {}
    for line in config_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


_values = _load_config_values(_CONFIG_FILE)

#: Bare image repository, without tag or digest, e.g.
#: ``"docker.io/opencloudeu/opencloud-rolling"``.
OPENCLOUD_IMAGE_REPOSITORY = _values["OPENCLOUD_IMAGE_REPOSITORY"]

#: Pinned, verified image digest, e.g.
#: ``"sha256:6db1cfb06d430a663f16e9f33dcd4596d82a4875be0b4df233c26ce5f667ea74"``.
OPENCLOUD_IMAGE_DIGEST = _values["OPENCLOUD_IMAGE_DIGEST"]

#: Fully qualified, digest-pinned image reference ready to pass to
#: Podman, e.g. ``"docker.io/opencloudeu/opencloud-rolling@sha256:..."``.
OPENCLOUD_IMAGE_REF = f"{OPENCLOUD_IMAGE_REPOSITORY}@{OPENCLOUD_IMAGE_DIGEST}"
