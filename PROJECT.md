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

### Zielgruppe
Der erste PoC richtet sich an eine kleine Gruppe oder ein Unternehmen mit
**bis zu 40 Personen** als Zielgröße. Diese Zahl ist eine geplante
Obergrenze, keine bereits bestätigte oder gemessene Lastgarantie.

### Betriebsumgebung
Der Betrieb erfolgt auf **einer einzelnen** per SSH erreichbaren
**Ubuntu-26.04**-Linux-VM mit zunächst:
- 4 CPU-Kernen
- 8 GB RAM
- 200 GB Festplattenspeicher

Diese Werte sind PoC-Ressourcen für Installation, Betrieb und Messung –
keine zugesicherte Kapazität für 40 gleichzeitige Benutzer. Speicherverbrauch,
Datenwachstum und Parallelzugriffe von OpenCloud müssen im PoC beobachtet
werden; konkrete Warnschwellen für RAM- und Festplattenauslastung werden
vor der jeweils betroffenen Implementierung (z. B. Installations- oder
Statusprüfung) gesondert festgelegt.

### Administration
Es gibt **genau einen Administrator**, der die Plattform im Ein-Mann-Betrieb
selbst betreibt. Der Administrator verfügt über Linux- und
Containerkenntnisse und benötigt daher neben einer einfachen Bedienung auch
Zugriff auf technische Details und Diagnoseausgaben. Ein Multi-Admin- oder
Rollenmodell ist für den ersten PoC nicht vorgesehen.

### Technologiebasis
- Podman
- Python
- Flask
- serverseitig erzeugtes HTML
- JavaScript nur soweit erforderlich

Kubernetes und OpenShift gehören ausdrücklich nicht zum ersten PoC. Ebenso
sind Cluster-, Hochverfügbarkeits- oder Multi-VM-Anforderungen kein
Bestandteil des ersten PoC.

### Zugriffsmodell
Es wird zwischen zwei Zugriffswegen unterschieden:

- **Verwaltungsoberfläche (Plattform-Administration):** standardmäßig nur
  auf `127.0.0.1` gebunden und ausschließlich über SSH bzw. einen
  SSH-Tunnel erreichbar. Dadurch entfällt im ersten PoC eine eigene
  Authentifizierungsarchitektur für die Verwaltungsoberfläche.
- **OpenCloud-Benutzeroberfläche:** Ob und wie bis zu 40 Personen intern auf
  OpenCloud zugreifen, ist eine **noch offene Entscheidung** und nicht
  automatisch ebenfalls auf `127.0.0.1` beschränkt. Diese Entscheidung wird
  getroffen, sobald der Benutzerzugriff auf OpenCloud tatsächlich Ziel eines
  Roadmap-Punkts wird.

### Offene Entscheidungen (bewusst noch nicht getroffen)
- Persistenzform (Dateien oder SQLite)
- synchrone Ausführung vs. Hintergrundjobs mit Fortschrittsanzeige
- Teststrategie für Podman-Aufrufe (simuliert oder echte VM-Tests)
- konkrete Warnschwellen für Speicher- und RAM-Auslastung
- Umfang und Zeitpunkt von Backup/Restore und Updates
- Sicherheitsmodell für einen eventuellen internen OpenCloud-Benutzerzugriff

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
