# Application Service Layer

Kurze Architekturnotiz zur Service-Grenze, die seit R005 zwischen der
Flask-Webschicht und der eigentlichen Plattformlogik besteht (siehe
`PROJECT.md`, Architekturprinzip: Web UI → Application/Service Layer →
Installation/Module Layer → Podman/Betriebssystem).

## Grenze

- Paket: `src/sovereign_business_suite/services/`
- Erster Service: `PlatformService` (`platform_service.py`)
- Vertrag: `PlatformService.get_platform_info() -> PlatformInfo`

`PlatformInfo` ist ein unveränderliches (`@dataclass(frozen=True)`),
präsentationsunabhängiges Datenobjekt mit `project_name` und
`status_message`.

## Regeln für Services in diesem Paket

- kein Import von `flask` oder anderen Web-/Präsentationsabhängigkeiten
- keine Podman-, Prozess- oder Dateisystemaufrufe (folgen erst ab R006
  bzw. den jeweils betroffenen Roadmap-Punkten)
- Rückgabewerte sind einfache, typisierte Datenobjekte, keine
  HTML-Fragmente oder Flask-spezifischen Typen

## Verwendung in der Web-Schicht

Die Flask-Route `index()` in `app.py` erzeugt eine `PlatformService`-
Instanz, ruft `get_platform_info()` auf und übergibt das Ergebnis an das
Jinja2-Template `templates/index.html`. Die Route selbst enthält keine
Texte oder Geschäftslogik mehr — sie vermittelt nur zwischen Service und
Template.

## Umfang von R005

R005 legt ausschließlich diese eine Service-Grenze fest. Nicht
Bestandteil:

- Podman-Integration (R006)
- Command Execution (R007)
- Job-System und Fortschrittsmodell (R008/R009)
- OpenCloud-Implementierung (R010+)
- eine allgemeine Plugin-/Modul-Architektur
