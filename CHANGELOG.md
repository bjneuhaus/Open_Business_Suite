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

### Fix – R005-Follow-up: Route-zu-Service-Integrationstest
- `tests/test_app.py::test_index_route_renders_platform_service_output`
  ergänzt: ersetzt `PlatformService.get_platform_info()` per
  `monkeypatch` durch einen eindeutigen Stand-in-Wert und prüft, dass
  genau dieser Wert in der gerenderten `/`-Antwort erscheint
- schließt die Lücke, dass die ursprünglichen R004/R005-Tests nur auf
  Werte prüften, die zufällig mit den hartkodierten Service-Werten
  übereinstimmten, ohne die tatsächliche Kopplung Route → Service zu
  verifizieren
- `tests/README.md` aktualisiert
- kein Produktionscode geändert, kein neuer Roadmap-Punkt begonnen
  (separater Fix-PR gemäß WORKFLOW.md: ein Roadmap-Punkt = ein Branch)

### R006 – Podman Integration
- `src/sovereign_business_suite/services/podman_service.py`:
  `PodmanService.is_available() -> bool`, prüft ausschließlich
  `shutil.which("podman")` — kein `subprocess`, kein Versionsaufruf,
  keine Container-Aktionen (bewusst reduzierter Umfang, mit @chantal
  abgestimmt)
- `tests/test_podman_service.py` (test-first): deckt vorhandenes und
  fehlendes Podman sowie den exakten Executable-Namen per `monkeypatch`
  ab, ohne echten Prozessaufruf
- `docs/podman-availability.md`: Notiz zu Scope-Grenze (R007/R012+
  bleiben außen vor) und Verifikation auf der Ziel-VM
- auf der PoC-Ziel-VM bestätigt: `podman` ist dort noch nicht
  installiert (`which podman` liefert keinen Treffer);
  `is_available()` würde dort korrekt `False` liefern
- README.md, src/README.md, tests/README.md aktualisiert
- keine Installation von Podman auf der VM, keine Prozessaufrufe, keine
  Container-Operationen (folgt in R007 bzw. R012+)

### R007–R014 – OpenCloud-Vertical-Slice (Command Execution, Podman-Voraussetzungen, OpenCloud-Lebenszyklus)
- `src/sovereign_business_suite/services/command_runner.py`:
  `CommandRunner`/`CommandResult` als generischer, testbarer
  `subprocess.run`-Wrapper (keine Shell-Interpolation, kein Raise bei
  Nicht-Null-Returncode oder Timeout)
- `src/sovereign_business_suite/services/opencloud_service.py`:
  `OpenCloudConfig`/`OpenCloudStatus`/`OpenCloudService` mit
  `install()`, `status()`, `start()`, `stop()`, `remove_container()`;
  Container wird ausschließlich an `127.0.0.1` gebunden, rootless
  (`--userns=keep-id`), mit persistenten Config-/Datenverzeichnissen
- `scripts/provision_opencloud.sh`: einmaliges, manuelles, idempotentes
  Infrastruktur-Skript (Podman-Paketinstallation, systemd-Linger,
  Verzeichnisanlage) — bewusst außerhalb der Python-Anwendung (kein
  `sudo`/`apt` aus dem Code heraus)
- `tests/test_command_runner.py`, `tests/test_opencloud_service.py`
  (test-first): vollständig gegen Mocks/Fakes, kein echter
  Podman-/Prozessaufruf in der Test-Suite
- `docs/opencloud-service.md`: Architekturnotiz, feste Konfiguration
  (Image, Port, Pfade), manueller Bootstrap-Ablauf (`opencloud init`),
  Zugriffsweg per SSH-Tunnel, Teardown-Verhalten
- README.md, src/README.md, tests/README.md aktualisiert
- reale Verifikation auf der PoC-VM (separat, außerhalb der
  automatisierten Test-Suite): Podman 5.7.0 installiert, OpenCloud-
  Container `opencloud` läuft rootless und dauerhaft (systemd-Linger),
  ausschließlich an `127.0.0.1:9200` gebunden, über SSH-Tunnel mit
  HTTP 200 erreichbar
- bewusst nicht Bestandteil: `opencloud init` aus der Anwendung heraus,
  Flask-Endpoint für die Lebenszyklus-Aktionen, Image-Tag-Pinning
  (aktuell `latest`/rolling, als offene Verbesserung dokumentiert),
  vollständiger Image-/Daten-Rückbau beim Teardown

### Fix – R007-Follow-up: CommandRunner-Hardening
- `CommandRunner.run()` fängt jetzt zusätzlich `FileNotFoundError` ab
  (fehlendes Executable, z. B. Podman nicht installiert) und liefert
  einen `CommandResult` mit `returncode=127` statt eine Exception
  weiterzureichen
- Timeout- und Missing-Executable-Fehlermeldungen enthalten nur noch
  den Executable-Namen (`args[0]`), nicht mehr die vollständige
  Argumentliste — verhindert, dass Secrets (z. B. ein per
  `--admin-password` übergebenes OpenCloud-Admin-Passwort) in
  Fehlermeldungen/Logs landen
- `tests/test_command_runner.py`: drei neue Tests (test-first) decken
  fehlendes Executable und das Nicht-Leaken von Argumenten in beiden
  Fehlerpfaden ab
- kein Verhaltenswechsel bei Erfolg oder regulärem Fehlschlag
  (Rückwärtskompatibel zu allen bestehenden Aufrufern)

### Fix – OpenCloud-Image-Digest-Pinning
- `config/opencloud-image.env`: neue, einzige Quelle der Wahrheit für
  den OpenCloud-Image-Verweis (`OPENCLOUD_IMAGE_REPOSITORY`,
  `OPENCLOUD_IMAGE_DIGEST`), verifiziert per `podman images --digests`
  auf der PoC-VM am 2026-08-31
  (`sha256:6db1cfb06d430a663f16e9f33dcd4596d82a4875be0b4df233c26ce5f667ea74`)
- `src/sovereign_business_suite/opencloud_image_config.py`: liest
  diese Datei und stellt `OPENCLOUD_IMAGE_REPOSITORY`,
  `OPENCLOUD_IMAGE_DIGEST`, `OPENCLOUD_IMAGE_REF` als Python-Konstanten
  bereit
- `services/opencloud_service.py`: neue Factory-Funktion
  `default_opencloud_config()` befüllt `OpenCloudConfig.image`
  automatisch mit dem gepinnten Digest statt einem floatenden
  `latest`/rolling-Tag; bestehender `OpenCloudConfig`-Konstruktor
  bleibt unverändert und rückwärtskompatibel
- `scripts/provision_opencloud.sh`: liest denselben Digest aus
  `config/opencloud-image.env`, pullt jetzt genau dieses Image (statt
  gar keins zu pullen)
- `tests/test_opencloud_image_config.py` (neu, test-first) und drei
  neue Tests in `tests/test_opencloud_service.py`: verifizieren Parsen
  der Konfigurationsdatei, Format des Digests und dass
  `default_opencloud_config()`/`install()` den gepinnten Digest
  verwenden
- `docs/opencloud-service.md`, README.md, src/README.md,
  tests/README.md aktualisiert
- Zweck: wiederkehrende Auf-/Abbauzyklen der Plattform während der
  Entwicklung verwenden dasselbe, bereits verifizierte Image, statt
  bei jedem Neuaufbau potenziell eine andere Version zu ziehen; Image
  bleibt beim Teardown weiterhin erhalten (kein Verhaltenswechsel)
