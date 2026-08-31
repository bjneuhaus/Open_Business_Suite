# Code Style

## Grundprinzip
Code wird für Menschen geschrieben. Verständlichkeit und Wartbarkeit haben Vorrang vor Cleverness.

## Python
- PEP 8
- Formatierung mit **Black**
- Linting mit **Ruff**
- Tests mit **pytest**
- Type Hints
- kleine Funktionen mit klarer Verantwortung
- sprechende Namen
- keine unnötigen Dependencies oder Abstraktionen
- strukturierte Fehlerbehandlung
- sinnvolles Logging

## Docstrings
Jede öffentliche Funktion, Klasse und Methode erhält einen Docstring.

```python
def install_application(application_name: str) -> bool:
    """Install an application managed by the platform.

    Args:
        application_name: Name of the application to install.

    Returns:
        True if the installation completed successfully.

    Raises:
        InstallationError: If the application cannot be installed.
    """
```

## Kommentare
Kommentare erklären vor allem **warum** etwas getan wird. Der Code soll zeigen, **was** getan wird.

## Dependencies
Neue Libraries nur mit klarem Nutzen einführen. Zuerst Standardbibliothek und vorhandene Dependencies prüfen.

## Fehler und Logging
Fehler niemals still ignorieren. Keine Passwörter, Tokens oder Secrets unmaskiert protokollieren.
