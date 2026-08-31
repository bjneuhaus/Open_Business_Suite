# Definition of Done

Ein Roadmap-Punkt ist erst abgeschlossen, wenn:

- vereinbarte Funktion implementiert
- Scope eingehalten
- Black erfolgreich (`black --check src/ tests/`)
- Ruff erfolgreich (`ruff check src/ tests/`, Konfiguration in `ruff.toml`)
- relevante Tests vorhanden
- bestehende Tests grün (`python -m pytest tests/`)
- sinnvolle Type Hints vorhanden
- erforderliche Docstrings vorhanden
- Benutzer- und technische Dokumentation aktualisiert
- `CHANGELOG.md` aktualisiert
- keine bekannten kritischen Fehler
- Pull Request erstellt bzw. vorbereitet
- menschliches Review erfolgt

Der Coding Agent mergt nicht eigenständig. Nach dem Pull Request endet die Bearbeitung.
