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

Seit R015 prüft `test_application_catalog_service.py` den unveränderlichen,
minimalen Katalogeintrag und den OpenCloud-Standardkatalog unabhängig von
Flask. `test_app.py::test_catalog_route_renders_application_catalog_service_output`
prüft mit einem unverwechselbaren, per `monkeypatch` eingesetzten Eintrag
explizit die Integration Route → `ApplicationCatalogService` → Template.

Seit R016 prüft `test_opencloud_configuration_wizard.py` jede
Validierungsregel (gültiger Port, ungültiger/außerhalb des Bereichs
liegender/privilegierter Port, relative/leere/identische Verzeichnisse,
mehrere gleichzeitige Fehler) und dass das Ergebnis keine Secret-Felder
enthält — unabhängig von Flask. Ergänzend prüfen
`test_app.py::test_configure_get_returns_200_with_form`,
`test_configure_post_valid_submission_shows_confirmation` und
`test_configure_post_invalid_submission_shows_errors` das
Formularverhalten; `test_configure_post_does_not_trigger_installation`
stellt per `monkeypatch` explizit sicher, dass `POST /configure`
niemals `OpenCloudService.install()` aufruft.

Seit R017 prüft `test_app.py::test_install_route_starts_opencloud_once_for_valid_submission`
per `monkeypatch`, dass `POST /install` bei gültiger Eingabe
`OpenCloudService.install()` genau einmal aufruft und eine
Erfolgsmeldung zeigt.
`test_install_post_invalid_submission_shows_errors_without_installing`
prüft, dass ungültige Eingaben dieselbe Fehleranzeige wie `/configure`
zeigen und `install()` dabei nicht aufgerufen wird.
`test_install_route_uses_normalized_values_for_service_configuration`
prüft, dass die durch `normalize_installation_path()` normalisierten
Pfade — nicht die Rohtexte des Formulars — an
`default_opencloud_config()` und den `OpenCloudService`-Konstruktor
weitergereicht werden.
`test_install_post_reports_failed_install_result` stellt sicher, dass ein
fehlgeschlagenes `CommandResult` nur generisch gemeldet wird und sein
`stderr`-Inhalt nicht in der Antwort erscheint.
`test_install_post_handles_install_exception_without_leaking_details`
stellt sicher, dass ein unerwarteter Fehler propagiert (statt
verschluckt zu werden) und dabei keine sensiblen Details preisgibt.
`test_install_get_returns_405` prüft, dass `GET /install` nicht
erlaubt ist.

`test_opencloud_installation_policy.py` prüft
`normalize_installation_path()` unabhängig von Flask: Pfad außerhalb
der Allowlist, `..`-Traversal-Escape, vorhandener Symlink nach außen,
gültiger Unterordner (inkl. `..`-Normalisierung ohne
Verzeichnisanlage) und dass der Speicherbereich selbst kein gültiger
Installationspfad ist. Ergänzend prüfen
`test_install_post_rejects_paths_outside_allowlist_without_installing`,
`test_install_post_rejects_dot_dot_escape_without_installing` und
`test_install_post_rejects_symlink_resolving_outside_without_installing`
auf Route-Ebene, dass solche Pfade ohne Installationsaufruf abgelehnt
werden. Zwei weitere Route-Regressionstests prüfen, dass syntaktisch
verschiedene Pfade nach `..`- bzw. interner Symlink-Auflösung als identisch
erkannt und mit der bestehenden Meldung abgelehnt werden, ohne
`OpenCloudService.install()` aufzurufen.

R016 bleibt eine read-only Syntaxprüfung ohne Dateisystemzugriff; R017
erzwingt zusätzlich `~/opencloud` sowie Traversal-/Symlink-Policy und
vergleicht die normalisierten Werte. Diese Prüfung ist im PoC mit genau einem
Administrator akzeptiert, aber nicht atomar gegen einen gleichprivilegierten
lokalen Prozess zwischen Prüfung und Podman-Bind-Mount und damit keine
Produktionsgarantie. Eine race-resistente descriptor-/atomare Mount-Übergabe
ist für eine spätere Produktionsumsetzung als Roadmap-Kandidat vorzumerken.

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
