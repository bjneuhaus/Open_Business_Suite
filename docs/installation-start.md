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
3. Sind die Werte gültig, wird `default_opencloud_config()` mit den
   validierten Werten aufgerufen und daraus ein `OpenCloudService`
   erstellt, der genau einmal `install()` aufruft.
4. Das Ergebnis wird in `templates/install.html` gerendert: bei Erfolg
   ein kurzer Bestätigungstext, bei Fehlschlag ein generischer
   Fehlschlaghinweis **ohne** `stdout`/`stderr`-Details — technische
   Ausgaben sind ausdrücklich Gegenstand von R019 und werden hier
   bewusst nicht angezeigt, da sie potenziell sensible Informationen
   enthalten könnten.

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

- `tests/test_app.py::test_install_route_starts_opencloud_once_for_valid_submission`
  prüft per `monkeypatch`, dass `OpenCloudService.install()` bei
  gültiger Eingabe genau einmal aufgerufen wird und eine
  Erfolgsmeldung erscheint.
- `test_install_post_invalid_submission_shows_errors_without_installing`
  stellt sicher, dass ungültige Eingaben dieselben Fehlermeldungen wie
  `/configure` zeigen und `install()` **nicht** aufgerufen wird.
- `test_install_route_uses_validated_values_for_service_configuration`
  prüft, dass die getrimmten, geparsten Wizard-Werte (nicht die
  Rohtexte aus dem Formular) an `default_opencloud_config()` und den
  `OpenCloudService`-Konstruktor weitergereicht werden.
- `test_install_post_reports_failed_install_result` stellt sicher,
  dass ein fehlgeschlagenes `CommandResult` nur generisch gemeldet
  wird und dessen `stderr`-Inhalt **nicht** in der Antwort erscheint.
- Der Test `test_install_post_handles_install_exception_without_leaking_details`
  deckt unerwartete Service-Fehler ab und prüft ebenfalls die generische
  Antwort ohne Fehlerdetails.
- `test_install_get_returns_405` prüft, dass `GET /install` nicht
  erlaubt ist.
