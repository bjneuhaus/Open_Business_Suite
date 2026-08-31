"""Tests for the pinned OpenCloud image configuration.

This module verifies that the single source of truth
(config/opencloud-image.env) is parsed correctly and that the composed
image reference has the expected shape. No registry or Podman calls
are made.
"""

import re

from sovereign_business_suite.opencloud_image_config import (
    OPENCLOUD_IMAGE_DIGEST,
    OPENCLOUD_IMAGE_REF,
    OPENCLOUD_IMAGE_REPOSITORY,
)


def test_repository_is_a_bare_repository_without_tag_or_digest() -> None:
    """The repository value must contain neither a tag nor a digest."""
    assert "@" not in OPENCLOUD_IMAGE_REPOSITORY
    assert OPENCLOUD_IMAGE_REPOSITORY == "docker.io/opencloudeu/opencloud-rolling"


def test_digest_has_expected_sha256_format() -> None:
    """The pinned digest must look like a valid sha256 digest string."""
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", OPENCLOUD_IMAGE_DIGEST)


def test_image_ref_combines_repository_and_digest() -> None:
    """OPENCLOUD_IMAGE_REF must be '<repository>@<digest>'."""
    assert (
        OPENCLOUD_IMAGE_REF == f"{OPENCLOUD_IMAGE_REPOSITORY}@{OPENCLOUD_IMAGE_DIGEST}"
    )
