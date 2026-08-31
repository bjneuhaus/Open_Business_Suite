# tests/

Automatisierte Tests für die Sovereign Business Suite.

Dieses Verzeichnis enthält die pytest-basierten Tests für das Paket
`sovereign_business_suite` unter `src/`.

Seit R002 (Python-Projekt) existiert ein Import-Smoke-Test
(`test_package_import.py`), der nur prüft, dass das Paket installierbar
und importierbar ist und eine `__version__` bereitstellt.

Seit R004 (Flask-Grundgerüst) prüft `test_app.py` zusätzlich mit dem
Flask-Testclient, dass `create_app()` eine funktionsfähige Anwendung
liefert, `GET /` erfolgreich antwortet (Statuscode 200) und die
Startseite den Projektnamen sowie einen erkennbaren PoC-Hinweis enthält.
Die Tests testen bewusst keine weitere Anwendungslogik (Authentifizierung,
Datenbank, Podman-Integration, Jobs), da diese erst ab späteren
Roadmap-Punkten entsteht.

Ausführung (im Projekt-Root, mit aktivierter virtueller Umgebung und
installiertem Paket):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/
```

Seit R003 (Code Quality) sind Black, Ruff und pytest als
Entwicklungswerkzeuge in `requirements-dev.txt` verankert und eine
Ruff-Konfiguration liegt in `ruff.toml` im Repository-Root. Siehe auch die
Sektion „Code-Qualität“ in der Root-`README.md`.
