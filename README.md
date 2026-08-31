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
- Governance-Dokumente ([`PROJECT.md`](PROJECT.md), [`ROADMAP.md`](ROADMAP.md),
  [`WORKFLOW.md`](WORKFLOW.md), [`CODE_STYLE.md`](CODE_STYLE.md),
  [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md),
  [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md)) bleiben im
  Repository-Root

Jedes der drei Verzeichnisse enthält eine eigene `README.md` mit Zweck und
aktuellem Stand.

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
| 📌 | Status |

## 📌 Status
Projektinitialisierung / Proof of Concept.
