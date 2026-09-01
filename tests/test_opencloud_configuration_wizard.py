"""Tests for the OpenCloud configuration wizard validation (R016).

These tests only verify the R016 scope: validating user-supplied
OpenCloud configuration values (host port, config/data directories).
No persistence, no Podman/CommandRunner calls, no installation trigger,
and no secrets are part of this service.
"""

from sovereign_business_suite.services.opencloud_configuration_wizard import (
    ConfigurationValidationResult,
    OpenCloudConfigurationWizardService,
)


def make_service() -> OpenCloudConfigurationWizardService:
    return OpenCloudConfigurationWizardService()


def test_valid_input_produces_no_errors() -> None:
    """A fully valid submission must be reported as valid, no errors."""
    service = make_service()

    result = service.validate(
        host_port="9200",
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert isinstance(result, ConfigurationValidationResult)
    assert result.is_valid is True
    assert result.errors == {}
    assert result.host_port == 9200
    assert result.config_dir == "/home/training/opencloud/opencloud-config"
    assert result.data_dir == "/home/training/opencloud/opencloud-data"


def test_non_numeric_port_is_rejected() -> None:
    """A non-numeric host_port must produce a host_port error."""
    service = make_service()

    result = service.validate(
        host_port="not-a-number",
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert result.is_valid is False
    assert "host_port" in result.errors


def test_port_out_of_range_is_rejected() -> None:
    """A port outside 1-65535 must produce a host_port error."""
    service = make_service()

    result = service.validate(
        host_port="70000",
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert result.is_valid is False
    assert "host_port" in result.errors


def test_privileged_port_is_rejected() -> None:
    """A privileged port (<1024) must produce a host_port error.

    Rootless Podman cannot bind privileged ports without extra
    capabilities, so the wizard rejects them up front.
    """
    service = make_service()

    result = service.validate(
        host_port="80",
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert result.is_valid is False
    assert "host_port" in result.errors


def test_relative_config_dir_is_rejected() -> None:
    """A relative config_dir path must produce a config_dir error."""
    service = make_service()

    result = service.validate(
        host_port="9200",
        config_dir="opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert result.is_valid is False
    assert "config_dir" in result.errors


def test_relative_data_dir_is_rejected() -> None:
    """A relative data_dir path must produce a data_dir error."""
    service = make_service()

    result = service.validate(
        host_port="9200",
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="opencloud/opencloud-data",
    )

    assert result.is_valid is False
    assert "data_dir" in result.errors


def test_empty_directories_are_rejected() -> None:
    """Empty/whitespace-only directory values must produce errors."""
    service = make_service()

    result = service.validate(host_port="9200", config_dir="", data_dir="   ")

    assert result.is_valid is False
    assert "config_dir" in result.errors
    assert "data_dir" in result.errors


def test_identical_config_and_data_dir_is_rejected() -> None:
    """config_dir and data_dir must not be the same path."""
    service = make_service()

    result = service.validate(
        host_port="9200",
        config_dir="/home/training/opencloud/shared",
        data_dir="/home/training/opencloud/shared",
    )

    assert result.is_valid is False
    assert "data_dir" in result.errors


def test_multiple_errors_are_all_reported_together() -> None:
    """All applicable errors must be reported in a single result."""
    service = make_service()

    result = service.validate(host_port="abc", config_dir="", data_dir="")

    assert result.is_valid is False
    assert "host_port" in result.errors
    assert "config_dir" in result.errors
    assert "data_dir" in result.errors


def test_result_never_contains_secrets() -> None:
    """ConfigurationValidationResult carries no password/secret fields."""
    service = make_service()

    result = service.validate(
        host_port="9200",
        config_dir="/home/training/opencloud/opencloud-config",
        data_dir="/home/training/opencloud/opencloud-data",
    )

    assert not hasattr(result, "admin_password")
    assert not hasattr(result, "password")
