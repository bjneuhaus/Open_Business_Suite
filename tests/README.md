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

Seit R005 (Application Service Layer) prüft `test_platform_service.py`
zusätzlich `PlatformInfo` als unveränderliches Datenobjekt und
`PlatformService.get_platform_info()` als eigenständige Einheit, unabhängig
von Flask. Ergänzend prüft `test_app.py::test_index_route_renders_platform_service_output`
per `monkeypatch`, dass die Route `/` tatsächlich das ersetzt, was der
Service liefert (Web-Schicht-zu-Service-Integrationstest) — nicht nur
zufällig identische, hartkodierte Werte.

Seit R006 (Podman Integration) prüft `test_podman_service.py` per
`monkeypatch` von `shutil.which`, dass `PodmanService.is_available()`
korrekt zwischen vorhandenem und fehlendem `podman`-Befehl unterscheidet
und exakt nach dem Namen `"podman"` sucht. Es findet kein echter
Prozessaufruf statt.

Seit R007–R014 (OpenCloud-Vertical-Slice) prüft
`test_command_runner.py` `CommandRunner` per `monkeypatch` von
`subprocess.run` (Erfolg, Fehlschlag, Timeout, fehlendes Executable,
keine Shell-Interpolation, keine Argument-/Secret-Leaks in
Fehlermeldungen), `test_opencloud_image_config.py` prüft das Parsen
von `config/opencloud-image.env` und das Zusammensetzen von
`OPENCLOUD_IMAGE_REF`, und `test_opencloud_service.py` prüft
`OpenCloudService` gegen einen Fake-`CommandRunner`: welche
`podman`-Kommandos gebaut werden, wie Ergebnisse interpretiert werden
und dass `default_opencloud_config()` den gepinnten Digest verwendet.
Auch hier findet kein echter Podman-/Prozessaufruf statt.

Die Tests testen bewusst keine weitere Anwendungslogik
(Authentifizierung, Datenbank, echte Podman-/Container-Aufrufe, Jobs),
da diese erst ab späteren Roadmap-Punkten entsteht. Getestet wird
lediglich, ob der `podman`-Befehl vorhanden ist (siehe R006 oben) — kein
tatsächlicher Aufruf von Podman selbst.

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
