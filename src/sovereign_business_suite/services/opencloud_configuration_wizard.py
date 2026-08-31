"""OpenCloud configuration wizard validation (R016 – Configuration Wizard).

This module validates administrator-supplied OpenCloud configuration
values (host port, config/data directories) before they would be used
by ``OpenCloudConfig``/``OpenCloudService``. It performs no filesystem
access, no Podman/CommandRunner calls, stores nothing, and never
handles the OpenCloud admin password or any other secret.

Scope boundary: this module only validates input and reports errors.
It does not persist the submitted values, does not trigger an
installation (R017), and has no progress tracking (R018/R019).
"""

from dataclasses import dataclass, field

#: Minimum port an administrator may configure. Ports below this are
#: rejected because rootless Podman cannot bind them without extra
#: capabilities, which this PoC does not grant.
_MIN_PORT = 1024

#: Maximum valid TCP port number.
_MAX_PORT = 65535


@dataclass(frozen=True)
class ConfigurationValidationResult:
    """Outcome of validating a submitted OpenCloud configuration.

    Attributes:
        is_valid: True if every field passed validation.
        errors: Mapping of field name (``"host_port"``, ``"config_dir"``,
            or ``"data_dir"``) to a human-readable German error message.
            Empty when ``is_valid`` is True.
        host_port: The parsed port number, or ``None`` if the submitted
            value could not be parsed as a valid port.
        config_dir: The submitted config directory value, stripped of
            surrounding whitespace.
        data_dir: The submitted data directory value, stripped of
            surrounding whitespace.
    """

    is_valid: bool
    errors: dict[str, str] = field(default_factory=dict)
    host_port: int | None = None
    config_dir: str = ""
    data_dir: str = ""


class OpenCloudConfigurationWizardService:
    """Validates OpenCloud configuration input from an administrator.

    This service contains no Flask, Podman, or persistence concerns —
    it only turns raw string input into a validated
    ``ConfigurationValidationResult``.
    """

    def validate(
        self, host_port: str, config_dir: str, data_dir: str
    ) -> ConfigurationValidationResult:
        """Validate the submitted configuration values.

        Args:
            host_port: The submitted port as a string (form input is
                always text).
            config_dir: The submitted absolute path for OpenCloud's
                configuration directory.
            data_dir: The submitted absolute path for OpenCloud's data
                directory.

        Returns:
            A ``ConfigurationValidationResult`` describing whether the
            submission is valid and, if not, which fields failed and
            why.
        """
        errors: dict[str, str] = {}

        parsed_port = self._validate_port(host_port, errors)
        stripped_config_dir = config_dir.strip()
        stripped_data_dir = data_dir.strip()

        self._validate_directory(stripped_config_dir, "config_dir", errors)
        self._validate_directory(stripped_data_dir, "data_dir", errors)

        if (
            "config_dir" not in errors
            and "data_dir" not in errors
            and stripped_config_dir == stripped_data_dir
        ):
            errors["data_dir"] = (
                "Konfigurations- und Datenverzeichnis müssen unterschiedlich sein."
            )

        return ConfigurationValidationResult(
            is_valid=not errors,
            errors=errors,
            host_port=parsed_port,
            config_dir=stripped_config_dir,
            data_dir=stripped_data_dir,
        )

    def _validate_port(self, host_port: str, errors: dict[str, str]) -> int | None:
        """Validate the port value and record an error if invalid.

        Returns:
            The parsed port as an int, or None if invalid.
        """
        try:
            port = int(host_port.strip())
        except (TypeError, ValueError):
            errors["host_port"] = "Der Port muss eine ganze Zahl sein."
            return None

        if port < _MIN_PORT or port > _MAX_PORT:
            errors["host_port"] = (
                f"Der Port muss zwischen {_MIN_PORT} und {_MAX_PORT} liegen."
            )
            return None

        return port

    def _validate_directory(
        self, value: str, field_name: str, errors: dict[str, str]
    ) -> None:
        """Validate a directory path and record an error if invalid."""
        if not value:
            errors[field_name] = "Bitte einen Verzeichnispfad angeben."
        elif not value.startswith("/"):
            errors[field_name] = "Der Pfad muss absolut sein (mit '/' beginnen)."
