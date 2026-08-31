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

### R003 – Code Quality
- `ruff.toml` als zentrale, kommentierte Ruff-Linter-Konfiguration ergänzt
  (Zielversion py311, Regel-Auswahl E/W/F/I/UP/B, isort-Einstellung für
  `sovereign_business_suite` als first-party)
- `requirements-dev.txt` mit `black==25.1.0`, `ruff==0.16.5`,
  `pytest==9.1.1` als von den Laufzeitabhängigkeiten getrennte
  Entwicklungswerkzeuge ergänzt; keine flake8-Abhängigkeit aufgenommen
- vorhandener Code (`src/`, `tests/`) mit `black --check`, `ruff check`
  und `pytest` geprüft: alle drei Prüfungen ohne Findings/Fehler, keine
  Codeänderungen notwendig
- Root-`README.md` um Abschnitt „Code-Qualität“ und Inhaltsverzeichnis-
  Eintrag ergänzt; `tests/README.md` aktualisiert
- `DEFINITION_OF_DONE.md` um konkrete Prüfbefehle ergänzt
- Flask-Anwendung, Podman-Integration und CI bleiben außerhalb des Scopes

### R004 – Flask-Grundgerüst
- `src/sovereign_business_suite/app.py`: minimale Flask-App-Factory
  `create_app()`, testbar per Flask-Testclient
- `src/sovereign_business_suite/templates/index.html`: serverseitig
  gerenderte Startseite mit Projekttitel und deutlichem PoC-Hinweis
  (HTML als eigenes Template, keine große Inline-Zeichenkette)
- `tests/test_app.py` (test-first): prüft `create_app()`, `GET /` mit
  Statuscode 200 sowie sichtbaren Startseiteninhalt
- lokaler Start standardmäßig auf `127.0.0.1`:
  `python -m flask --app sovereign_business_suite.app run --host 127.0.0.1 --port 5000`
- Root-`README.md` um Abschnitt „Anwendung starten“ (Startbefehl,
  SSH-Tunnel-Beispiel, erwartetes visuelles Ergebnis) und
  Inhaltsverzeichnis-Eintrag ergänzt; `src/README.md` und
  `tests/README.md` aktualisiert
- keine Authentifizierung, keine Datenbank, keine Podman-Integration,
  keine Jobs, kein `/health`-Endpoint (folgt in späteren Roadmap-Punkten)

### R005 – Application Service Layer
- `src/sovereign_business_suite/services/platform_service.py`:
  `PlatformInfo` (unveränderliches Datenobjekt) und `PlatformService`
  mit `get_platform_info() -> PlatformInfo` als erste Grenze zwischen
  Flask-Webschicht und Plattformlogik
- `app.py`: Route `index()` bezieht Inhalte jetzt über
  `PlatformService.get_platform_info()` statt hartkodierter Werte;
  `templates/index.html` rendert `info.project_name` /
  `info.status_message`
- `tests/test_platform_service.py` (test-first): prüft `PlatformInfo`
  als Value-Objekt und `get_platform_info()` unabhängig von Flask
- `docs/application-service-layer.md`: Architekturnotiz zur Service-
  Grenze und den Regeln für künftige Services in diesem Paket
- `src/README.md`, `tests/README.md`, Root-`README.md` (neuer
  Icon-Eintrag) und `CHANGELOG.md` aktualisiert
- Service enthält bewusst keine Podman-, Prozess- oder
  Dateisystemaufrufe, keine Jobs, keine OpenCloud-Logik und keine
  allgemeine Plugin-Architektur (folgt in R006+)
