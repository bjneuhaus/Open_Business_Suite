"""Tests for CommandRunner (R007 – Command Execution).

These tests mock ``subprocess.run`` entirely — no real process is ever
started by this test module. CommandRunner's job is only to wrap
``subprocess.run`` into a small, predictable, testable result type; it
performs no shell interpolation and no command-specific logic.
"""

import subprocess

from sovereign_business_suite.services.command_runner import (
    CommandResult,
    CommandRunner,
)


def test_run_returns_captured_output_on_success(monkeypatch) -> None:
    """A successful command returns a CommandResult with rc 0."""

    def fake_run(args, capture_output, text, timeout, check):
        assert args == ["echo", "hi"]
        assert capture_output is True
        assert text is True
        assert check is False
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout="hi\n", stderr=""
        )

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()

    result = runner.run(["echo", "hi"])

    assert isinstance(result, CommandResult)
    assert result.returncode == 0
    assert result.stdout == "hi\n"
    assert result.succeeded is True


def test_run_returns_nonzero_returncode_without_raising(monkeypatch) -> None:
    """A failing command is reported via CommandResult, not an exception."""

    def fake_run(args, capture_output, text, timeout, check):
        return subprocess.CompletedProcess(
            args=args, returncode=1, stdout="", stderr="boom"
        )

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()

    result = runner.run(["false"])

    assert result.returncode == 1
    assert result.stderr == "boom"
    assert result.succeeded is False


def test_run_reports_timeout_as_failed_result(monkeypatch) -> None:
    """A timing-out command is reported as a failed CommandResult."""

    def fake_run(args, capture_output, text, timeout, check):
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()

    result = runner.run(["sleep", "999"], timeout=1)

    assert result.succeeded is False
    assert result.returncode != 0
    assert "timed out" in result.stderr.lower()


def test_run_never_uses_shell_interpolation(monkeypatch) -> None:
    """run() must always pass a list of args, never shell=True."""
    captured = {}

    def fake_run(args, capture_output, text, timeout, check):
        captured["args"] = args
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()

    runner.run(["podman", "ps", "-a"])

    assert captured["args"] == ["podman", "ps", "-a"]


def test_run_reports_missing_executable_as_failed_result(monkeypatch) -> None:
    """A missing executable is reported via CommandResult, not raised."""

    def fake_run(args, capture_output, text, timeout, check):
        raise FileNotFoundError(2, "No such file or directory", args[0])

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()

    result = runner.run(["does-not-exist", "--flag"])

    assert result.succeeded is False
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
    assert "does-not-exist" in result.stderr


def test_timeout_message_does_not_leak_command_arguments(monkeypatch) -> None:
    """The timeout error must not echo full argv (may contain secrets)."""

    def fake_run(args, capture_output, text, timeout, check):
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()
    secret = "super-secret-admin-password"

    result = runner.run(["opencloud", "init", "--admin-password", secret], timeout=1)

    assert secret not in result.stderr
    assert "opencloud" in result.stderr  # naming just the executable is fine


def test_missing_executable_message_does_not_leak_command_arguments(
    monkeypatch,
) -> None:
    """The missing-executable error must not echo full argv either."""

    def fake_run(args, capture_output, text, timeout, check):
        raise FileNotFoundError(2, "No such file or directory", args[0])

    monkeypatch.setattr(
        "sovereign_business_suite.services.command_runner.subprocess.run",
        fake_run,
    )
    runner = CommandRunner()
    secret = "super-secret-admin-password"

    result = runner.run(["opencloud", "init", "--admin-password", secret])

    assert secret not in result.stderr
