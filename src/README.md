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

Die Application Service Layer, Podman-Integration und die
OpenCloud-Verwaltung folgen ab späteren Roadmap-Punkten.
