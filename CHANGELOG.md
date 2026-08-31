# Changelog

## [Unreleased]

### Added
- Initiale Projekt-Charta
- Roadmap
- Coding Guidelines
- AI-Agent-Workflow
- Definition of Done

### Changed
- R000: PROJECT.md um verbindliche PoC-Startannahmen ergänzt (Zielgruppe bis
  40 Personen, VM-Ressourcen, Ein-Mann-Administration, Zugriffsmodell mit
  Trennung von Verwaltungsoberfläche und OpenCloud-Benutzerzugriff, Liste
  offener Entscheidungen)
- README.md an aktualisierte Projektbeschreibung angepasst
- fix: Speicherangabe in PROJECT.md und README.md auf tatsächliche 150 GB
  korrigiert (verifiziert per SSH auf der Ziel-VM)
- R001: Repository-Struktur angelegt (`src/`, `tests/`, `docs/` mit
  jeweils eigener README.md); Governance-Dokumente bleiben im Root;
  Root-README.md um Strukturübersicht ergänzt
- R001: `requirements.txt` als bewusst leere Grundlage ergänzt; Inhalt
  folgt in R002 (Python-Projekt)
- R001: README.md zur zentralen Einstiegsseite aufgewertet (Icons,
  Inhaltsverzeichnis, lokale Verlinkungen auf alle Governance-Dokumente
  inkl. Kurzerklärung von Roadmap/Workflow/Code Style, Icon-Legende)

### R002 – Python-Projekt
- minimales, installierbares Python-Paket `sovereign_business_suite`
  unter `src/sovereign_business_suite/` angelegt (`__init__.py` mit
  `__version__`)
- `pyproject.toml` mit Paketmetadaten und Build-Backend (setuptools)
  ergänzt; Paket per `pip install -e .` installierbar
- Import-Smoke-Test `tests/test_package_import.py` ergänzt (test-first:
  zunächst rot, nach Paketanlage grün)
- `requirements.txt` mit `Flask==3.1.3` als exakt gepinnter Kern-
  Abhängigkeit für die spätere Verwaltungsoberfläche (R004) befüllt
- `.gitignore` für `.venv/`, `__pycache__/`, Build-Artefakte ergänzt
- `src/README.md`, `tests/README.md` und Root-`README.md` aktualisiert
- keine Black-/Ruff-/pytest-Konfiguration, kein Flask-Grundgerüst, keine
  Podman-Installation (folgt in R003/R004/R006)
