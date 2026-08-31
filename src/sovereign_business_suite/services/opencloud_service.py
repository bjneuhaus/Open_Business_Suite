"""OpenCloud lifecycle service (R010-R014 – OpenCloud Definition,
Configuration, Installation, Status, Start/Stop).

This module defines the minimal, testable contract for managing a
single OpenCloud Podman container: installing (pulling + running) it,
checking its status, and starting/stopping it. All actual command
execution is delegated to a ``CommandRunner``-compatible object, so
these tests never invoke a real ``podman`` process.

Scope boundary: this service does not run ``opencloud init`` (the
one-time configuration bootstrap remains a documented, manual
provisioning step — see docs/opencloud-service.md) and has no web
endpoint of its own; a Flask route to trigger these actions is not
part of this vertical slice.
"""

from dataclasses import dataclass
from enum import Enum

from sovereign_business_suite.services.command_runner import (
    CommandResult,
    CommandRunner,
)


@dataclass(frozen=True)
class OpenCloudConfig:
    """Configuration for a single OpenCloud container instance.

    Attributes:
        image: Fully qualified container image reference, e.g.
            ``"docker.io/opencloudeu/opencloud-rolling:latest"``.
        container_name: Name given to the Podman container.
        host_port: Port on the host's ``127.0.0.1`` that is forwarded
            to the container's port 9200. The container is always
            bound to ``127.0.0.1`` only, never to a public interface.
        config_dir: Absolute host path for OpenCloud's persistent
            configuration, mounted to ``/etc/opencloud`` in the
            container.
        data_dir: Absolute host path for OpenCloud's persistent data,
            mounted to ``/var/lib/opencloud`` in the container.
    """

    image: str
    container_name: str
    host_port: int
    config_dir: str
    data_dir: str


class OpenCloudStatus(Enum):
    """High-level status of the OpenCloud container."""

    #: No container with the configured name exists yet.
    NOT_INSTALLED = "not_installed"
    #: The container exists and is currently running.
    RUNNING = "running"
    #: The container exists but is not currently running.
    STOPPED = "stopped"


class OpenCloudService:
    """Manages the lifecycle of a single OpenCloud Podman container.

    This service only builds and runs the required ``podman``
    commands via the injected ``CommandRunner``. It performs no shell
    interpolation (arguments are always passed as a list) and does not
    read or log the OpenCloud admin password.
    """

    def __init__(self, config: OpenCloudConfig, command_runner: CommandRunner) -> None:
        """Initialize the service.

        Args:
            config: The OpenCloud container configuration to manage.
            command_runner: The runner used to execute ``podman``
                commands.
        """
        self._config = config
        self._command_runner = command_runner

    def status(self) -> OpenCloudStatus:
        """Report the current status of the OpenCloud container.

        Returns:
            ``OpenCloudStatus.NOT_INSTALLED`` if no container with the
            configured name exists, ``OpenCloudStatus.RUNNING`` if it
            is running, or ``OpenCloudStatus.STOPPED`` otherwise.
        """
        result = self._command_runner.run(
            [
                "podman",
                "inspect",
                self._config.container_name,
                "--format",
                "{{.State.Status}}",
            ]
        )
        if not result.succeeded:
            return OpenCloudStatus.NOT_INSTALLED
        if result.stdout.strip() == "running":
            return OpenCloudStatus.RUNNING
        return OpenCloudStatus.STOPPED

    def install(self) -> CommandResult:
        """Pull the configured image and run a new OpenCloud container.

        The container is started detached, bound exclusively to
        ``127.0.0.1``, running rootless (``--userns=keep-id``), with
        the configured host directories mounted for persistent
        configuration and data.

        Returns:
            The ``CommandResult`` of the ``podman run`` invocation.
        """
        config = self._config
        args = [
            "podman",
            "run",
            "-d",
            "--name",
            config.container_name,
            "--userns=keep-id",
            "-p",
            f"127.0.0.1:{config.host_port}:9200",
            "-v",
            f"{config.config_dir}:/etc/opencloud",
            "-v",
            f"{config.data_dir}:/var/lib/opencloud",
            "-e",
            "PROXY_HTTP_ADDR=0.0.0.0:9200",
            "-e",
            f"OC_URL=https://127.0.0.1:{config.host_port}",
            config.image,
            "server",
        ]
        return self._command_runner.run(args, timeout=300)

    def start(self) -> CommandResult:
        """Start an existing, stopped OpenCloud container.

        Returns:
            The ``CommandResult`` of the ``podman start`` invocation.
        """
        return self._command_runner.run(
            ["podman", "start", self._config.container_name]
        )

    def stop(self) -> CommandResult:
        """Stop a running OpenCloud container.

        Returns:
            The ``CommandResult`` of the ``podman stop`` invocation.
        """
        return self._command_runner.run(["podman", "stop", self._config.container_name])

    def remove_container(self) -> CommandResult:
        """Remove the OpenCloud container without touching its image.

        Used for teardown: only the container is deleted, so no image
        re-download is required for the next installation.

        Returns:
            The ``CommandResult`` of the ``podman rm -f`` invocation.
        """
        return self._command_runner.run(
            ["podman", "rm", "-f", self._config.container_name]
        )
