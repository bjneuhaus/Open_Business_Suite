"""Tests for OpenCloudService (R010-R014 – OpenCloud lifecycle).

These tests use a fake CommandRunner and never invoke a real ``podman``
process. They verify the commands OpenCloudService builds and how it
interprets CommandRunner results — not real container behavior. Real
verification against the PoC VM happens separately (see
docs/opencloud-service.md).
"""

from sovereign_business_suite.opencloud_image_config import OPENCLOUD_IMAGE_REF
from sovereign_business_suite.services.command_runner import CommandResult
from sovereign_business_suite.services.opencloud_service import (
    OpenCloudConfig,
    OpenCloudService,
    OpenCloudStatus,
    default_opencloud_config,
)


class FakeCommandRunner:
    """Records every call and returns a pre-scripted CommandResult."""

    def __init__(self, result: CommandResult) -> None:
        self.result = result
        self.calls: list[list[str]] = []

    def run(self, args: list[str], timeout: float = 120) -> CommandResult:
        self.calls.append(args)
        return self.result


def make_config() -> OpenCloudConfig:
    return OpenCloudConfig(
        image="docker.io/opencloudeu/opencloud-rolling:latest",
        container_name="opencloud",
        host_port=9200,
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )


def test_status_running_when_podman_reports_container_running() -> None:
    """status() reports RUNNING when podman inspect returns 'running'."""
    runner = FakeCommandRunner(
        CommandResult(returncode=0, stdout="running\n", stderr="")
    )
    service = OpenCloudService(config=make_config(), command_runner=runner)

    status = service.status()

    assert status == OpenCloudStatus.RUNNING
    assert runner.calls == [
        [
            "podman",
            "inspect",
            "opencloud",
            "--format",
            "{{.State.Status}}",
        ]
    ]


def test_status_not_installed_when_container_missing() -> None:
    """status() reports NOT_INSTALLED when podman inspect fails."""
    runner = FakeCommandRunner(
        CommandResult(returncode=125, stdout="", stderr="no such container")
    )
    service = OpenCloudService(config=make_config(), command_runner=runner)

    status = service.status()

    assert status == OpenCloudStatus.NOT_INSTALLED


def test_status_stopped_when_container_exited() -> None:
    """status() reports STOPPED for any non-'running' known state."""
    runner = FakeCommandRunner(
        CommandResult(returncode=0, stdout="exited\n", stderr="")
    )
    service = OpenCloudService(config=make_config(), command_runner=runner)

    assert service.status() == OpenCloudStatus.STOPPED


def test_start_runs_podman_start_and_returns_success() -> None:
    """start() runs 'podman start <name>' and reports success."""
    runner = FakeCommandRunner(CommandResult(returncode=0, stdout="", stderr=""))
    service = OpenCloudService(config=make_config(), command_runner=runner)

    result = service.start()

    assert result.succeeded is True
    assert runner.calls == [["podman", "start", "opencloud"]]


def test_stop_runs_podman_stop_and_returns_success() -> None:
    """stop() runs 'podman stop <name>' and reports success."""
    runner = FakeCommandRunner(CommandResult(returncode=0, stdout="", stderr=""))
    service = OpenCloudService(config=make_config(), command_runner=runner)

    result = service.stop()

    assert result.succeeded is True
    assert runner.calls == [["podman", "stop", "opencloud"]]


def test_install_builds_expected_run_command_with_localhost_binding() -> None:
    """install() must bind the container exclusively to 127.0.0.1."""
    runner = FakeCommandRunner(CommandResult(returncode=0, stdout="", stderr=""))
    service = OpenCloudService(config=make_config(), command_runner=runner)

    result = service.install()

    assert result.succeeded is True
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call[0:3] == ["podman", "run", "-d"]
    assert "--name" in call and "opencloud" in call
    assert "-p" in call
    port_index = call.index("-p") + 1
    assert call[port_index] == "127.0.0.1:9200:9200"
    assert "--userns=keep-id" in call
    assert "docker.io/opencloudeu/opencloud-rolling:latest" in call


def test_install_mounts_configured_config_and_data_directories() -> None:
    """install() must mount the configured config/data host directories."""
    runner = FakeCommandRunner(CommandResult(returncode=0, stdout="", stderr=""))
    service = OpenCloudService(config=make_config(), command_runner=runner)

    service.install()

    call = runner.calls[0]
    joined = " ".join(call)
    assert "/home/training/opencloud/opencloud-config:/etc/opencloud" in joined
    assert "/home/training/opencloud/opencloud-data:/var/lib/opencloud" in joined


def test_default_opencloud_config_uses_pinned_image_digest() -> None:
    """default_opencloud_config() must use the pinned digest, not a tag."""
    config = default_opencloud_config(
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert config.image == OPENCLOUD_IMAGE_REF
    assert "@sha256:" in config.image
    assert config.container_name == "opencloud"
    assert config.host_port == 9200


def test_default_opencloud_config_allows_overriding_host_port() -> None:
    """default_opencloud_config() must allow a custom host_port."""
    config = default_opencloud_config(
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
        host_port=9300,
    )

    assert config.host_port == 9300


def test_install_uses_pinned_digest_image_from_default_config() -> None:
    """install() must pass the pinned digest-based image to podman run."""
    runner = FakeCommandRunner(CommandResult(returncode=0, stdout="", stderr=""))
    config = default_opencloud_config(
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )
    service = OpenCloudService(config=config, command_runner=runner)

    service.install()

    assert OPENCLOUD_IMAGE_REF in runner.calls[0]
