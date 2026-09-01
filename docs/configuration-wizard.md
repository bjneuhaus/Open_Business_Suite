# Konfigurations-Wizard (R016)

Kurze Architekturnotiz zum OpenCloud-Konfigurations-Wizard.

## Zweck

R016 stellt einen serverseitigen Formular-Wizard bereit, mit dem ein
Administrator Port, Konfigurations- und Datenverzeichnis für eine
künftige OpenCloud-Installation eingibt und validieren lässt. Es ist
ausdrücklich **nur ein Validierungsschritt**: keine Installation, keine
Persistenz, keine Secrets.

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
  Werten.
- `POST` mit ungültigen Werten zeigt die Formularfelder erneut,
  ergänzt um die jeweiligen Fehlermeldungen.

Die Route selbst enthält keine Validierungslogik — sie vermittelt nur
zwischen Formular, Service und Template. Es wird **kein**
`OpenCloudService.install()` oder eine andere Lebenszyklus-Methode
aufgerufen; ein expliziter Test stellt das sicher.

## Umfang von R016

Bewusst **nicht** Bestandteil:

- Installationsstart (R017)
- Fortschrittsanzeige (R018/R019)
- Persistenz der eingegebenen Werte (z. B. in `OpenCloudConfig`)
- Prüfung, ob die angegebenen Verzeichnisse auf der Ziel-VM tatsächlich
  existieren oder beschreibbar sind
- Erfassung oder Anzeige von Secrets (Admin-Passwort bleibt weiterhin
  ein manueller, dokumentierter Schritt außerhalb der Anwendung, siehe
  `docs/opencloud-service.md`)

## Tests

- `tests/test_opencloud_configuration_wizard.py` prüft den Service
  unabhängig von Flask: gültige Eingaben, jede einzelne
  Validierungsregel, mehrere gleichzeitige Fehler und dass keine
  Secret-Felder existieren.
- `tests/test_app.py` prüft `GET`/`POST /configure` (Formular,
  Bestätigung, Fehleranzeige) sowie explizit, dass `POST /configure`
  niemals `OpenCloudService.install()` aufruft.
