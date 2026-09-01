"""R017 policy for safe OpenCloud installation bind-mount paths.

R016 deliberately performs syntax-only validation and does not inspect the
filesystem. This module is the separate R017 installation policy: it resolves
paths without creating directories or writing anything, and only permits a
strict child of the running user's ``~/opencloud`` storage root.
"""

from pathlib import Path

# Kept deliberately generic so policy failures do not disclose host paths.
INSTALLATION_PATH_ERROR = (
    "Das Verzeichnis muss ein eigenes Unterverzeichnis im "
    "zulässigen OpenCloud-Speicherbereich sein."
)


def normalize_installation_path(value: str) -> Path | None:
    """Return a safe normalized installation path, or ``None``.

    The allowed root is evaluated for the current user on every call. The
    candidate must be an absolute strict child of ``Path.home() / "opencloud"``
    after lexical normalization and after resolving existing symlinks. The
    root itself, traversal escapes, and symlinks resolving outside the root are
    rejected. Path resolution is read-only; this function never creates or
    writes filesystem entries.

    Args:
        value: An absolute path previously accepted by the R016 syntax check.

    Returns:
        The normalized resolved child path, or ``None`` when the value is not
        an allowed installation path.
    """
    storage_root = (Path.home() / "opencloud").absolute()

    try:
        resolved_root = storage_root.resolve(strict=False)
        # The fixed storage root itself must not be redirected elsewhere.
        if resolved_root != storage_root:
            return None

        candidate = Path(value)
        if not candidate.is_absolute():
            return None
        lexical_candidate = candidate.absolute()
        if lexical_candidate == storage_root or not lexical_candidate.is_relative_to(
            storage_root
        ):
            return None

        resolved_candidate = lexical_candidate.resolve(strict=False)
        if (
            resolved_candidate == resolved_root
            or not resolved_candidate.is_relative_to(resolved_root)
        ):
            return None
    except (OSError, RuntimeError, ValueError):
        # Resolution can fail for malformed paths or symlink loops. Such a
        # value is not safe to pass to a container runtime.
        return None

    return resolved_candidate
