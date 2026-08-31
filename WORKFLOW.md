# Entwicklungsworkflow für Hermes und Coding Agents

## Grundregel
**Niemals direkt auf `main` entwickeln.**

`main` enthält ausschließlich vom Projektverantwortlichen freigegebenen Code.

## Ein Roadmap-Punkt = ein Branch
Beispiele:
- `feature/r001-repository-structure`
- `feature/r004-flask-base`
- `feature/r012-opencloud-installation`

## Ablauf
1. Aktuellen Stand von `main` prüfen.
2. Ausdrücklich freigegebenen Roadmap-Punkt lesen.
3. Scope bestimmen.
4. Eigenen Branch erstellen.
5. Ausschließlich diesen Punkt implementieren.
6. Tests aktualisieren.
7. Dokumentation aktualisieren.
8. `CHANGELOG.md` aktualisieren.
9. Pull Request erstellen bzw. vorbereiten.
10. **STOPP.**

Danach auf menschliches Review und ausdrückliche Freigabe warten.

## Verboten
Der Agent darf nicht:
- direkt auf `main` committen,
- eigenständig Pull Requests mergen,
- ungefragt Roadmap-Punkte zusammenfassen,
- nach einem PR automatisch weiterarbeiten,
- größere Architekturänderungen ohne Rücksprache durchführen.

## Scope-Schutz
Zusätzliche Ideen nicht nebenbei implementieren, sondern als zukünftige Roadmap-Punkte dokumentieren.

## Architekturentscheidungen
Bei Frameworks, größeren Dependencies, Datenbank, Modularchitektur, Container-/Deployment-Modell, Authentifizierung oder API-Design gilt:

**Vorschlagen → begründen → Entscheidung abwarten → implementieren.**
