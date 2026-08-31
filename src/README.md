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

Die OpenCloud-Verwaltung folgt ab späteren Roadmap-Punkten.
