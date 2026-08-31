# Application Catalog (R015)

## Zweck

R015 stellt dem Administrator eine kleine, serverseitig gerenderte Übersicht
der aktuell unterstützten Anwendungen bereit. Die Übersicht ist read-only
und bildet die Grundlage für spätere Web-Installer-Schritte, ohne diese
vorwegzunehmen.

## Service-Vertrag

Der Service liegt in
`src/sovereign_business_suite/services/application_catalog_service.py`.
`ApplicationCatalogService.get_applications()` liefert eine unveränderliche
Sequenz von `ApplicationCatalogEntry`-Objekten. Jeder Eintrag enthält genau
diese drei Werte:

| Feld | Bedeutung | R015-Wert |
| --- | --- | --- |
| `id` | stabile maschinenlesbare Identität | `opencloud` |
| `name` | Name für die Administration | `OpenCloud` |
| `description` | kurze Beschreibung für die Administration | selbst gehostete Dateiablage und Zusammenarbeit |

Die Einträge sind unveränderliche Value Objects. Der Service besitzt keine
Datenbank, keine Dateipersistenz und keine Discovery- oder Plugin-Logik. Der
Katalog enthält zunächst ausschließlich OpenCloud, weil sie die erste
integrierte Referenzanwendung des Projekts ist.

Bewusst nicht im Katalog enthalten sind Image-Referenzen, Digests, Ports,
Hostpfade oder andere Bereitstellungsdetails. Diese Informationen bleiben in
den bestehenden OpenCloud-Konfigurations- und Service-Quellen, insbesondere
`config/opencloud-image.env`, und werden nicht dupliziert.

## Web-Ansicht

`GET /catalog` ruft ausschließlich `ApplicationCatalogService` auf und
übergibt dessen Ergebnis an
`src/sovereign_business_suite/templates/catalog.html`. Die Darstellung
(Name, Beschreibung und HTML-Struktur) liegt damit im Template, nicht in der
Flask-Route. Die Einträge stellen keine Aktionen bereit: Es gibt in R015
keine Installation, Konfiguration, Start/Stop-Funktion oder Statusabfrage
über den Katalog.

Die bestehende Startseite `GET /` und ihr Verhalten bleiben unverändert.
Der Katalog ist als direkter lokaler Verwaltungsweg unter
`http://127.0.0.1:5000/catalog` erreichbar, wenn die Flask-Anwendung lokal
gestartet wurde.

## Tests

- `tests/test_application_catalog_service.py` prüft das unveränderliche,
  minimale Datenmodell und den OpenCloud-Standardkatalog.
- `tests/test_app.py::test_catalog_route_renders_application_catalog_service_output`
  ersetzt den Service per `monkeypatch` durch unverwechselbare Testdaten und
  prüft ausdrücklich den Pfad Route → Service → Template.
