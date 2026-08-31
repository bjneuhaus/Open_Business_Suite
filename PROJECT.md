# Sovereign Business Suite – Project Charter

## Vision
Ziel ist eine einfach zu installierende, zu bedienende und zu wartende Plattform für kleine und mittelständische Unternehmen, die Open-Source-Anwendungen als Alternative zu proprietären Cloud- und SaaS-Lösungen bereitstellt.

Die Plattform entwickelt bestehende Anwendungen nicht neu, sondern übernimmt Installation, Konfiguration, Integration, Verwaltung, Aktualisierung, Überwachung, Backup/Wiederherstellung und Dokumentation.

Langfristig soll sich die Plattform wie ein Produkt anfühlen und nicht wie eine lose Sammlung verschiedener Container.

## Projektprinzipien
1. **Simplicity First**
2. **Usability First**
3. **Documentation First**
4. **Maintainability First**
5. **Iterative Development**

## Proof of Concept
- einzelne Linux-VM
- SSH-Zugriff
- Podman
- Python
- Flask
- serverseitig erzeugtes HTML
- JavaScript nur soweit erforderlich

Kubernetes und OpenShift gehören ausdrücklich nicht zum ersten PoC.

## Erste Anwendung
Die erste integrierte Anwendung ist **OpenCloud**. Sie dient als Referenzimplementierung für den späteren modularen Aufbau.

Zuerst wird ein sauberer Installations- und Verwaltungsprozess für OpenCloud entwickelt. Erst danach werden weitere Anwendungen integriert.

## Weboberfläche
Der Administrator soll Anwendungen auswählen, notwendige Werte konfigurieren, Installationen starten, den Fortschritt verfolgen und optional technische Ausgaben anzeigen können.

Technische Details sollen verfügbar sein, aber nicht Voraussetzung für die normale Bedienung.

## Architekturprinzip

    Web UI
       |
       v
    Application / Service Layer
       |
       v
    Installation / Module Layer
       |
       v
    Podman / Operating System

Die Weboberfläche enthält keine komplexe Installationslogik.

## Modulsystem
OpenCloud wird zuerst implementiert, bevor eine allgemeine Plugin-Architektur festgelegt wird. Erst aus realen Anforderungen abstrahieren.

Ein Modul kann später Name, Beschreibung, Version, Voraussetzungen, Konfiguration, Installation, Statusprüfung, Start/Stop, Update und Deinstallation beschreiben.

## Sicherheit
- keine Secrets im Git-Repository
- keine Secrets in Logs
- keine fest codierten Passwörter
- Eingaben validieren
- sichere Flask-Konfiguration
- minimale Container-Berechtigungen
- möglichst kein Root
- sichere Standardwerte

## Oberstes Prinzip
Bei technischen Entscheidungen gilt:

**Usability → Simplicity → Maintainability → Security → Functionality → Technical Elegance**

Overengineering und spekulative Architektur sind zu vermeiden.
