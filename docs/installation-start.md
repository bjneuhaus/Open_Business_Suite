# Installationsstart (R017)

Kurze Architekturnotiz zum Installationsstart für OpenCloud.

## Zweck

R017 fügt eine `POST /install`-Route hinzu, die eine bereits im
Konfigurations-Wizard (R016) geprüfte Eingabe erneut validiert und bei
Erfolg **einmalig, synchron** `OpenCloudService.install()` aufruft. Es
gibt bewusst keinen Hintergrundjob, keine Fortschrittsanzeige
(R018/R019) und keine eigene Ergebnisseite mit technischen Details
(R020) — die Antwort ist ein einfacher Erfolgs- oder
Fehlschlaghinweis.

## Ablauf

`app.py`, Route `POST /install`:

1. Die übermittelten Werte (`host_port`, `config_dir`, `data_dir`)
   werden erneut über `OpenCloudConfigurationWizardService.validate()`
   geprüft — die Validierung aus `/configure` wird niemals über
   Requests hinweg blind vertraut.
2. Sind die Werte ungültig, wird dieselbe Fehleranzeige wie bei
   `/configure` gerendert (`templates/configure.html`); es findet
   **keine** Installation statt.
3. Sind die Werte gültig, wird zusätzlich `normalize_installation_path()`
   (`services/opencloud_installation_policy.py`) für `config_dir` und
   `data_dir` aufgerufen. R016 prüft nur Syntax (absoluter Pfad, kein
   Dateisystemzugriff); dieser separate R017-Policy-Schritt löst
   `..`-Segmente und vorhandene Symlinks tatsächlich auf und verlangt,
   dass das Ergebnis ein echtes Unterverzeichnis des festen
   OpenCloud-Speicherbereichs `~/opencloud` des ausführenden Benutzers
   ist — der Bereich selbst ist kein gültiger Wert. Schlägt das fehl,
   wird dieselbe Fehleranzeige wie bei `/configure` gerendert (mit der
   bewusst generischen, hostpfad-freien Meldung aus
   `INSTALLATION_PATH_ERROR`), ebenfalls ohne Installation.
4. Erst danach wird `default_opencloud_config()` mit den normalisierten
   Pfaden aufgerufen und daraus ein `OpenCloudService` erstellt, der
   genau einmal `install()` aufruft.
5. Das Ergebnis wird in `templates/install.html` gerendert: bei Erfolg
   ein kurzer Bestätigungstext, bei Fehlschlag ein generischer
   Fehlschlaghinweis **ohne** `stdout`/`stderr`-Details — technische
   Ausgaben sind ausdrücklich Gegenstand von R019 und werden hier
   bewusst nicht angezeigt, da sie potenziell sensible Informationen
   enthalten könnten. Ein unerwarteter Fehler in `install()` selbst
   (kein regulärer `CommandResult`-Fehlschlag) wird **nicht**
   unterdrückt: er propagiert als Flasks Standard-500-Antwort, die ohne
   aktivierten Debug-/Testmodus keine Exception-Details preisgibt.

## Sicherheit: Pfad-Allowlist gegen Traversal und Symlink-Escapes

`services/opencloud_installation_policy.py` ist bewusst ein eigenes,
schmales Modul getrennt vom Wizard (R016 bleibt reine Syntaxprüfung
ohne Dateisystemzugriff):

- `normalize_installation_path(value)` löst `value` vollständig auf
  (inklusive `..`-Segmenten und vorhandenen Symlinks) und akzeptiert
  das Ergebnis nur, wenn es ein **echtes Unterverzeichnis** von
  `Path.home() / "opencloud"` ist — der Speicherbereich selbst zählt
  nicht.
- Reine Textmanipulation (`..`-Segmente) wird ebenso abgelehnt wie ein
  Pfad, der syntaktisch innerhalb liegt, aber über einen vorhandenen
  Symlink tatsächlich nach außen zeigt.
- Die Funktion ist rein lesend: sie legt keine Verzeichnisse an und
  schreibt nichts.
- Fehlermeldungen (`INSTALLATION_PATH_ERROR`) sind bewusst generisch
  und nennen keine tatsächlichen Host-Pfade.

`GET /install` ist nicht erlaubt (HTTP 405) — der Installationsstart
ist eine reine POST-Aktion.

## Web-Integration

`templates/configure.html` zeigt bei einer gültigen Prüfung zusätzlich
ein zweites Formular mit Button „Installation starten“, das dieselben
geprüften Werte per `POST` an `/install` weiterreicht. Der
Konfigurations-Wizard selbst (`/configure`) bleibt unverändert ein
reiner Validierungsschritt ohne Installationsauslösung (siehe
[`configuration-wizard.md`](configuration-wizard.md)).

## Umfang von R017

Bewusst **nicht** Bestandteil:

- Hintergrundjobs oder asynchrone Ausführung (R008/R009 bleiben davon
  unberührt; `install()` läuft synchron im Request)
- Fortschrittsanzeige während der Installation (R018)
- Anzeige technischer Ausgaben/Logs (R019)
- Eine eigene, dauerhafte Ergebnisseite mit Verlauf (R020)
- Persistenz der Installationsanfrage oder ihres Ergebnisses

## Tests

- `tests/test_opencloud_installation_policy.py` prüft
  `normalize_installation_path()` unabhängig von Flask: Pfad außerhalb
  der Allowlist, `..`-Traversal-Escape, vorhandener Symlink nach
  außen, gültiger Unterordner (inkl. `..`-Normalisierung ohne
  Verzeichnisanlage) und dass der Speicherbereich selbst kein gültiger
  Installationspfad ist.
- `tests/test_app.py::test_install_route_starts_opencloud_once_for_valid_submission`
  prüft per `monkeypatch`, dass `OpenCloudService.install()` bei
  gültiger Eingabe genau einmal aufgerufen wird und eine
  Erfolgsmeldung erscheint.
- `test_install_post_invalid_submission_shows_errors_without_installing`
  stellt sicher, dass ungültige Eingaben dieselben Fehlermeldungen wie
  `/configure` zeigen und `install()` **nicht** aufgerufen wird.
- `test_install_post_rejects_paths_outside_allowlist_without_installing`,
  `test_install_post_rejects_dot_dot_escape_without_installing` und
  `test_install_post_rejects_symlink_resolving_outside_without_installing`
  prüfen auf Route-Ebene, dass ein syntaktisch gültiger, aber
  außerhalb liegender bzw. eskapierender Pfad abgelehnt wird und
  `install()` nicht aufgerufen wird.
- `test_install_route_uses_normalized_values_for_service_configuration`
  prüft, dass die **normalisierten** Pfade (nicht die Rohtexte aus dem
  Formular) an `default_opencloud_config()` und den
  `OpenCloudService`-Konstruktor weitergereicht werden.
- `test_install_post_reports_failed_install_result` stellt sicher,
  dass ein fehlgeschlagenes `CommandResult` nur generisch gemeldet
  wird und dessen `stderr`-Inhalt **nicht** in der Antwort erscheint.
- `test_install_post_handles_install_exception_without_leaking_details`
  stellt sicher, dass ein unerwarteter Fehler propagiert (statt
  verschluckt zu werden) und dabei keine sensiblen Details preisgibt.
- `test_install_get_returns_405` prüft, dass `GET /install` nicht
  erlaubt ist.
