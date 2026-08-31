# src/

Anwendungscode der Sovereign Business Suite.

Dieses Verzeichnis enthält das Python-Paket `sovereign_business_suite`
(siehe `src/sovereign_business_suite/`), das den eigentlichen
Anwendungscode der Plattform trägt (Service-Layer, Podman-Integration,
Web-UI, Module usw.).

Seit R002 (Python-Projekt) existiert ein minimales, installierbares
Paketskelett (`__init__.py` mit `__version__`), das per `pip install -e .`
installiert werden kann; die Projektmetadaten stehen in
`pyproject.toml` im Repository-Root.

Seit R004 (Flask-Grundgerüst) enthält das Paket zusätzlich eine minimale
Flask-Anwendung: `app.py` mit der App-Factory `create_app()` sowie
`templates/index.html` als serverseitig gerendertes HTML-Template für
die Startseite. Startbefehl, SSH-Tunnel-Beispiel und erwartetes
visuelles Ergebnis stehen in der Root-`README.md`
(Abschnitt „🚀 Anwendung starten“).

Seit R005 (Application Service Layer) enthält das Paket zusätzlich
`services/platform_service.py`: die `PlatformService`-Klasse mit
`get_platform_info() -> PlatformInfo` als erste Grenze zwischen der
Flask-Webschicht und der eigentlichen Plattformlogik. Die Flask-Route in
`app.py` ruft diesen Service auf, statt Texte selbst zu enthalten. Details
siehe [`docs/application-service-layer.md`](../docs/application-service-layer.md).

Seit R006 (Podman Integration) enthält das Paket zusätzlich
`services/podman_service.py`: die `PodmanService`-Klasse mit
`is_available() -> bool`, die ausschließlich prüft, ob der
`podman`-Befehl auf dem `PATH` des Hosts gefunden wird. Details siehe
[`docs/podman-availability.md`](../docs/podman-availability.md).

Seit R007–R014 (OpenCloud-Vertical-Slice) enthält das Paket zusätzlich
`services/command_runner.py` (`CommandRunner`, generischer
`subprocess`-Wrapper) und `services/opencloud_service.py`
(`OpenCloudService` mit `install()`/`status()`/`start()`/`stop()`).
Der OpenCloud-Image-Verweis ist per Digest gepinnt: die einzige Quelle
der Wahrheit ist `config/opencloud-image.env` im Repository-Root,
gelesen von `opencloud_image_config.py`; `default_opencloud_config()`
nutzt diesen Digest automatisch. Details, feste Konfiguration und der
manuelle Bootstrap-Ablauf stehen in
[`docs/opencloud-service.md`](../docs/opencloud-service.md).

Seit R015 enthält das Paket außerdem
`services/application_catalog_service.py`: `ApplicationCatalogService`
mit `get_applications() -> tuple[ApplicationCatalogEntry, ...]` liefert
für den serverseitigen Katalog die erste unterstützte Anwendung OpenCloud
mit stabiler ID, Namen und administrativer Beschreibung. Der read-only
Katalog wird über `GET /catalog` und
`templates/catalog.html` angezeigt; Konfigurations- und Image-Details
werden dabei nicht dupliziert.

Seit R016 enthält das Paket außerdem
`services/opencloud_configuration_wizard.py`:
`OpenCloudConfigurationWizardService.validate()` prüft Port,
Konfigurations- und Datenverzeichnis rein serverseitig, ohne
Installation auszulösen oder etwas zu speichern. `GET/POST /configure`
und `templates/configure.html` zeigen Formular, Bestätigung oder
Fehlermeldungen. Details siehe
[`docs/configuration-wizard.md`](../docs/configuration-wizard.md).

Ein Flask-Endpoint zur Steuerung dieser Services ist kein Bestandteil
dieses Slices und folgt in einem späteren Roadmap-Punkt.
