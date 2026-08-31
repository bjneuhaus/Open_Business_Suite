"""Command execution service (R007 – Command Execution).

This module provides a small, testable wrapper around
``subprocess.run`` for executing external commands (in practice:
``podman``). It performs no shell interpolation — commands are always
passed as an argument list — and never logs or returns secrets beyond
whatever the wrapped command itself writes to stdout/stderr.

Scope boundary: this module knows nothing about Podman, OpenCloud, or
any other specific tool. It is a generic, minimal command runner used
by ``services.opencloud_service``.
"""

import subprocess
from dataclasses import dataclass

#: Default timeout (in seconds) for commands that do not specify one.
#: Chosen generously for Podman image pulls over a typical PoC-VM link.
DEFAULT_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class CommandResult:
    """Outcome of running an external command.

    Attributes:
        returncode: The process exit code. A synthetic code is used
            when the process never produced a real exit code: ``124``
            on timeout (matching the common shell convention) and
            ``127`` when the executable itself could not be found
            (matching "command not found" shell semantics).
        stdout: Captured standard output.
        stderr: Captured standard error, or a synthetic message on
            timeout/missing executable. Synthetic messages never
            include full command arguments (which may contain
            secrets such as passwords) — only the executable name.
    """

    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        """Whether the command completed with exit code 0."""
        return self.returncode == 0


class CommandRunner:
    """Runs external commands and reports their outcome as CommandResult.

    This class never raises on a non-zero exit code, a timeout, or a
    missing executable — callers must inspect
    ``CommandResult.succeeded`` instead. This keeps calling code (e.g.
    ``OpenCloudService``) simple and avoids exception-based control
    flow for expected failure cases like "the container is not running
    yet" or "podman is not installed".
    """

    def run(
        self, args: list[str], timeout: float = DEFAULT_TIMEOUT_SECONDS
    ) -> CommandResult:
        """Run a command given as an argument list.

        Args:
            args: The command and its arguments, e.g.
                ``["podman", "ps", "-a"]``. Never interpreted by a
                shell.
            timeout: Maximum time in seconds to wait for the command.

        Returns:
            A ``CommandResult`` describing the outcome. On timeout or
            a missing executable, ``returncode`` is set to a
            conventional non-zero value and ``stderr`` contains a
            human-readable message that never includes the full
            argument list — no exception is raised in either case.
        """
        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                returncode=124,
                stdout="",
                stderr=(f"Command timed out after {timeout} seconds: {args[0]!r}"),
            )
        except FileNotFoundError:
            return CommandResult(
                returncode=127,
                stdout="",
                stderr=f"Executable not found: {args[0]!r}",
            )

        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
