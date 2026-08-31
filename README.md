# 🏛️ Sovereign Business Suite

Proof of Concept für eine modular verwaltete Open-Source-Unternehmensplattform.

Der erste PoC richtet sich an eine kleine Gruppe oder ein Unternehmen mit bis
zu 40 Personen als Zielgröße und läuft auf einer einzelnen per SSH
erreichbaren Ubuntu-26.04-VM (4 CPU-Kerne, 8 GB RAM, 150 GB Speicher) mit
Podman und einer Python/Flask-basierten Verwaltungsoberfläche. Der einzige
Administrator betreibt die Plattform selbst. Die Verwaltungsoberfläche ist
standardmäßig nur über `127.0.0.1`/SSH-Tunnel erreichbar; der Benutzerzugriff
auf OpenCloud ist separat zu entscheiden. Erste Referenzanwendung ist
OpenCloud. Details siehe [`PROJECT.md`](PROJECT.md).

<details>
<summary>🧭 Inhaltsverzeichnis anzeigen</summary>

- [🤖 Für AI/Coding Agents](#-für-aicoding-agents)
- [📁 Repository-Struktur](#-repository-struktur)
- [🚀 Anwendung starten](#-anwendung-starten)
- [🧹 Code-Qualität](#-code-qualität)
- [📚 Dokumente](#-dokumente)
- [🔤 Icon-Legende](#-icon-legende)
- [📌 Status](#-status)

</details>

## 🤖 Für AI/Coding Agents
Vor Änderungen unbedingt [`AGENTS.md`](AGENTS.md) lesen.

## 📁 Repository-Struktur
- 💻 [`src/`](src/README.md) – Anwendungscode; enthält seit R002 das
  installierbare Python-Paket `sovereign_business_suite`
- 🧪 [`tests/`](tests/README.md) – automatisierte Tests (seit R002 ein
  Import-Smoke-Test; feste pytest-Konfiguration folgt in R003)
- 📄 [`docs/`](docs/README.md) – weiterführende technische Dokumentation zu
  einzelnen Implementierungen
- 📦 [`requirements.txt`](requirements.txt) – Python-Abhängigkeiten (seit
  R002: Flask, exakt gepinnt für die spätere Verwaltungsoberfläche)
- ⚙️ [`pyproject.toml`](pyproject.toml) – Paketmetadaten und Build-Backend
  für `sovereign_business_suite` (seit R002)
- 🧹 [`ruff.toml`](ruff.toml) – zentrale Ruff-Linter-Konfiguration (seit R003)
- 📦 [`requirements-dev.txt`](requirements-dev.txt) – Entwicklungswerkzeuge
  (Black, Ruff, pytest), getrennt von den Laufzeitabhängigkeiten (seit R003)
- 🚀 `src/sovereign_business_suite/app.py` – minimale Flask-App-Factory
  mit serverseitig gerenderter Startseite (Template unter
  `src/sovereign_business_suite/templates/`, seit R004)
- 🧩 `src/sovereign_business_suite/services/platform_service.py` –
  Application Service Layer (`PlatformService`), erste Grenze zwischen
  Web-Schicht und Plattformlogik (seit R005, Details in
  [`docs/application-service-layer.md`](docs/application-service-layer.md))
- 🐳 `src/sovereign_business_suite/services/podman_service.py` –
  `PodmanService.is_available()`, prüft nur `shutil.which("podman")`
  (seit R006, Details in [`docs/podman-availability.md`](docs/podman-availability.md))
- ⚙️ `src/sovereign_business_suite/services/command_runner.py` –
  `CommandRunner`, generischer, testbarer `subprocess.run`-Wrapper
  ohne Shell-Interpolation (seit R007)
- 🔒 [`config/opencloud-image.env`](config/opencloud-image.env) –
  einzige Quelle der Wahrheit für den gepinnten OpenCloud-Image-Digest
- 🔒 `src/sovereign_business_suite/opencloud_image_config.py` – lädt
  `config/opencloud-image.env` und stellt `OPENCLOUD_IMAGE_REF` bereit
- ☁️ `src/sovereign_business_suite/services/opencloud_service.py` –
  `OpenCloudService` mit `install()`/`status()`/`start()`/`stop()`
  für den OpenCloud-Container (seit R010–R014, Details in
  [`docs/opencloud-service.md`](docs/opencloud-service.md))
- 🗂️ `src/sovereign_business_suite/services/application_catalog_service.py` –
  read-only `ApplicationCatalogService.get_applications()` mit
  `ApplicationCatalogEntry` für den administratorseitigen
  Anwendungskatalog (aktuell nur OpenCloud; seit R015, Details in
  [`docs/application-catalog.md`](docs/application-catalog.md))
- 🖥️ `src/sovereign_business_suite/templates/catalog.html` – serverseitiges
  Template für den Katalog unter `/catalog` (seit R015)
- 📜 `scripts/provision_opencloud.sh` – einmaliges, manuelles
  Infrastruktur-Skript (Podman-Paket, systemd-Linger, Verzeichnisse,
  Pull des gepinnten Images)
- Governance-Dokumente ([`PROJECT.md`](PROJECT.md), [`ROADMAP.md`](ROADMAP.md),
  [`WORKFLOW.md`](WORKFLOW.md), [`CODE_STYLE.md`](CODE_STYLE.md),
  [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md),
  [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md)) bleiben im
  Repository-Root

Jedes der drei Verzeichnisse enthält eine eigene `README.md` mit Zweck und
aktuellem Stand.

## 🚀 Anwendung starten
Seit R004 existiert eine minimale Flask-Anwendung mit serverseitig
gerenderter Startseite (`src/sovereign_business_suite/app.py`, Template
unter `src/sovereign_business_suite/templates/index.html`). Seit R015 gibt
es zusätzlich `/catalog`: eine schreibgeschützte Übersicht der
unterstützten Anwendungen (aktuell nur OpenCloud), erreichbar unter
`http://127.0.0.1:5000/catalog`. Die bestehende Startseite unter `/` bleibt
dabei unverändert.

Lokaler Start (nach Einrichtung wie in [🧹 Code-Qualität](#-code-qualität)
beschrieben):

```bash
python -m flask --app sovereign_business_suite.app run \
  --host 127.0.0.1 --port 5000
```

Die Anwendung ist damit standardmäßig **nur lokal auf `127.0.0.1`**
erreichbar (siehe `PROJECT.md`, Zugriffsmodell für die
Verwaltungsoberfläche). Auf der Ziel-VM erfolgt der Zugriff über einen
SSH-Tunnel:

```bash
ssh -L 5000:127.0.0.1:5000 <benutzer>@<vm-adresse>
```

Danach im Browser auf dem eigenen Rechner `http://127.0.0.1:5000/`
öffnen.

**Erwartetes visuelles Ergebnis:** Auf `/` erscheint weiterhin eine einfache
HTML-Seite mit der Überschrift „Sovereign Business Suite“ und einem
Hinweistext, der die Seite ausdrücklich als Proof of Concept (R004 –
Flask-Grundgerüst) kennzeichnet. Der direkte Aufruf von `/catalog` zeigt
zusätzlich die Überschrift „Anwendungskatalog“ und einen Eintrag für
„OpenCloud“ mit Beschreibung. Beide Ansichten sind bewusst schlicht und
ohne Styling. Authentifizierung, Datenbank, Lebenszyklus-Aktionen,
Installation, Jobs und ein `/health`-Endpoint sind weiterhin nicht Teil
von R015.

## 🧹 Code-Qualität
Seit R003 sind Black (Formatierung), Ruff (Linting) und pytest (Tests) als
reproduzierbare Entwicklungswerkzeuge eingerichtet. Sie sind bewusst von den
Laufzeitabhängigkeiten getrennt und liegen in
[`requirements-dev.txt`](requirements-dev.txt).

Einrichtung und Prüfung (im Projekt-Root):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt -r requirements-dev.txt

black --check src/ tests/
ruff check src/ tests/
python -m pytest tests/
```

Die Ruff-Regeln sind in [`ruff.toml`](ruff.toml) kommentiert dokumentiert.
Eine automatisierte CI-Ausführung dieser Prüfungen ist nicht Bestandteil von
R003 und folgt in einem späteren Roadmap-Punkt.

## 📚 Dokumente
- 🎯 [`PROJECT.md`](PROJECT.md) – Projekt-Charta: Vision, Prinzipien, PoC-
  Rahmenbedingungen (Zielgruppe, VM-Ressourcen, Zugriffsmodell) und bewusst
  offene Entscheidungen.
- 🗺️ [`ROADMAP.md`](ROADMAP.md) – die geplanten Roadmap-Punkte (R000, R001, …)
  je Phase. Pro Roadmap-Punkt wird genau ein eigener Branch verwendet; nur
  ausdrücklich freigegebene Punkte werden umgesetzt.
- 🔁 [`WORKFLOW.md`](WORKFLOW.md) – der verbindliche Entwicklungsworkflow für
  Coding Agents: ein Branch pro Roadmap-Punkt, kein direkter Commit auf
  `main`, Ablaufschritte bis zum PR und danach Stopp für menschliches Review.
- 🎨 [`CODE_STYLE.md`](CODE_STYLE.md) – verbindliche Coding-Konventionen
  (Black, Ruff, pytest, Type Hints, Docstrings, Umgang mit Dependencies,
  Fehlerbehandlung und Logging).
- ✅ [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md) – Kriterien, wann ein
  Roadmap-Punkt tatsächlich abgeschlossen ist (Tests, Linting, Dokumentation,
  Changelog, Review).
- 🙋 [`CONTRIBUTING.md`](CONTRIBUTING.md) – wie Beiträge eingebracht werden
  (Branches, Review, welche Dokumente vorher zu lesen sind).
- 📝 [`CHANGELOG.md`](CHANGELOG.md) – chronologische Liste aller
  projektrelevanten Änderungen.
- 🗂️ [`docs/application-catalog.md`](docs/application-catalog.md) –
  technischer Vertrag und Scope des R015-Anwendungskatalogs.

## 🔤 Icon-Legende
| Icon | Bedeutung |
| --- | --- |
| 🏛️ | Projekt / Plattform |
| 🤖 | Hinweise für AI/Coding Agents |
| 📁 | Verzeichnis / Repository-Struktur |
| 💻 | Anwendungscode |
| 🧪 | Tests |
| 📄 | Dokumentation |
| 📦 | Abhängigkeiten |
| 📚 | Dokumentenübersicht |
| 🎯 | Projekt-Charta / Ziele |
| 🗺️ | Roadmap |
| 🔁 | Workflow / Ablauf |
| 🎨 | Code-Stil |
| ✅ | Definition of Done |
| 🙋 | Contributing |
| 📝 | Changelog |
| 🧹 | Code-Qualität (Black, Ruff, pytest) |
| 🚀 | Anwendung starten |
| 🧩 | Application Service Layer |
| 🐳 | Podman-Integration |
| ⚙️ | Command Execution |
| ☁️ | OpenCloud-Service |
| 🔒 | Gepinnter Image-Digest |
| 📋 | Application Catalog |
| 📌 | Status |

## 📌 Status
Projektinitialisierung / Proof of Concept.
