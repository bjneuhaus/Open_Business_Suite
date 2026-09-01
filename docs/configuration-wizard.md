# Konfigurations-Wizard und Installationsstart (R016/R017)

Kurze Architekturnotiz zum OpenCloud-Konfigurations-Wizard und dem daran
anschließenden Installationsstart.

## Zweck

R016 stellt einen serverseitigen Formular-Wizard bereit, mit dem ein
Administrator Port, Konfigurations- und Datenverzeichnis für eine
künftige OpenCloud-Installation eingibt und validieren lässt. Es ist
zunächst ausdrücklich **nur ein Validierungsschritt**: keine Installation,
keine Persistenz, keine Secrets. Nach einer gültigen Bestätigung bietet die
Ansicht den separaten R017-POST-Schritt `/install` an.

## Service-Vertrag

Der Service liegt in
`src/sovereign_business_suite/services/opencloud_configuration_wizard.py`.

`OpenCloudConfigurationWizardService.validate(host_port, config_dir, data_dir)`
nimmt drei Strings entgegen (Formulareingaben sind immer Text) und
liefert ein wirklich unveränderliches `ConfigurationValidationResult` mit.
Auch das `errors`-Mapping ist schreibgeschützt; weder Attribute noch
Einträge des Mappings können nach der Erstellung geändert werden:

| Feld | Bedeutung |
| --- | --- |
| `is_valid` | `True`, wenn alle drei Felder gültig sind |
| `errors` | schreibgeschütztes `Mapping[str, str]`: Feldname → deutschsprachige Fehlermeldung |
| `host_port` | geparster Port als `int`, oder `None` bei Fehler |
| `config_dir` / `data_dir` | getrimmte Eingabewerte |

### Validierungsregeln

- **Port:** muss eine ganze Zahl zwischen 1024 und 65535 sein. Ports
  unter 1024 werden abgelehnt, weil rootless Podman sie ohne
  zusätzliche Capabilities nicht binden kann (siehe
  `docs/opencloud-service.md`, Rootless-Betrieb).
- **Verzeichnisse:** müssen nicht leer sein und mit `/` beginnen
  (absoluter Pfad). `config_dir` und `data_dir` dürfen nicht identisch
  sein.
- Alle anwendbaren Fehler werden gemeinsam zurückgegeben, nicht nur der
  erste gefundene.

Der Service enthält **keinen** Dateisystemzugriff (es wird nicht
geprüft, ob die Pfade tatsächlich existieren oder beschreibbar sind),
keinen `CommandRunner`-/Podman-Aufruf und keine Felder für Secrets
(insbesondere kein Admin-Passwort).

## Web-Ansicht

`GET/POST /configure` in `app.py` ruft ausschließlich
`OpenCloudConfigurationWizardService.validate()` auf und übergibt das
Ergebnis an `templates/configure.html`:

- `GET` zeigt ein leeres Formular.
- `POST` mit gültigen Werten zeigt eine Bestätigung mit den geprüften
  Werten und eine separate Startmöglichkeit per `POST /install`.
- `POST` mit ungültigen Werten zeigt die Formularfelder erneut,
  ergänzt um die jeweiligen Fehlermeldungen.

Die Route selbst enthält keine Validierungslogik — sie vermittelt nur
zwischen Formular, Service und Template. `POST /configure` ruft **kein**
`OpenCloudService.install()` auf und speichert nichts.

## Installationsstart (R017)

`POST /install` nimmt die drei Formwerte entgegen und ruft
`OpenCloudConfigurationWizardService.validate()` **vor jedem Start erneut**
auf. Bei ungültigen Werten wird wieder das Konfigurationsformular mit
Fehlermeldungen gerendert; `OpenCloudService.install()` wird nicht aufgerufen.

Bei gültigen Werten verwendet die Route die normalisierten Werte aus dem
Validierungsergebnis, erzeugt mit
`default_opencloud_config(config_dir, data_dir, host_port)` eine
`OpenCloudConfig` und übergibt sie zusammen mit einem `CommandRunner` an
`OpenCloudService`. Dessen `install()` wird synchron genau einmal aufgerufen.
Die Antwort zeigt nur, ob der unmittelbare Start ausgelöst werden konnte oder
fehlgeschlagen ist. stdout/stderr, technische Details und ein Fortschritts-
oder Ergebnisbildschirm sind ausdrücklich nicht Bestandteil von R017.

Installationsfehler werden kontrolliert mit einer allgemeinen Meldung
angezeigt. Argumente, Pfade und mögliche Secrets aus technischen Fehlern
werden nicht in der Antwort ausgegeben; der R017-Ablauf enthält weiterhin
keine Secret-Felder oder Passwortbehandlung.

## Umfang von R016 und R017

Bewusst **nicht** Bestandteil dieses Web-Orchestrierungs-Slices:

- Fortschrittsanzeige, Hintergrundjobs, Threads, Queues oder Persistenz
  (R018)
- technische stdout-/stderr- oder Log-Anzeige (R019)
- umfassende separate Ergebnis-Seite (R020)
- `opencloud init`, Authentifizierung, Datenbank oder Passwortbehandlung
- Prüfung, ob die angegebenen Verzeichnisse auf der Ziel-VM tatsächlich
  existieren oder beschreibbar sind

Die automatisierte Suite führt keine echten Podman-/VM-Aufrufe aus. Der
manuelle Bootstrap und die Infrastruktur-Voraussetzungen bleiben in
`docs/opencloud-service.md` dokumentiert.

## Tests

- `tests/test_opencloud_configuration_wizard.py` prüft den Service
  unabhängig von Flask: gültige Eingaben, jede einzelne
  Validierungsregel, mehrere gleichzeitige Fehler und dass keine
  Secret-Felder existieren.
- `tests/test_app.py` prüft `GET`/`POST /configure` (Formular,
  Bestätigung, Startmöglichkeit und Fehleranzeige) sowie explizit, dass
  `POST /configure` niemals `OpenCloudService.install()` aufruft.
  Die R017-Tests prüfen außerdem die erneute Validierung bei `POST /install`,
  den einmaligen Aufruf mit normalisierten Werten, ungültige Eingaben,
  kontrollierte Installationsfehler ohne Detailleck und die POST-only-Regel.
