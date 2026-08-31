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

Flask, die Application Service Layer, Podman-Integration und die
OpenCloud-Verwaltung folgen ab R004 bzw. späteren Roadmap-Punkten.
