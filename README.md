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
unter `src/sovereign_business_suite/templates/index.html`).

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

**Erwartetes visuelles Ergebnis:** eine einfache HTML-Seite mit der
Überschrift „Sovereign Business Suite“ und einem Hinweistext, der die
Seite ausdrücklich als Proof of Concept (R004 – Flask-Grundgerüst)
kennzeichnet. Es gibt noch keine Navigation, kein Styling und keine
weitere Funktionalität — Authentifizierung, Datenbank, Podman-
Integration, Jobs und ein `/health`-Endpoint sind bewusst nicht
Bestandteil von R004.

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
| 📌 | Status |

## 📌 Status
Projektinitialisierung / Proof of Concept.
