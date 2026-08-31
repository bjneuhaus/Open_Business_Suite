# Sovereign Business Suite

Proof of Concept für eine modular verwaltete Open-Source-Unternehmensplattform.

Der erste PoC richtet sich an eine kleine Gruppe oder ein Unternehmen mit bis zu 40 Personen als Zielgröße und läuft auf einer einzelnen per SSH erreichbaren Ubuntu-26.04-VM (4 CPU-Kerne, 8 GB RAM, 150 GB Speicher) mit Podman und einer Python/Flask-basierten Verwaltungsoberfläche. Der einzige Administrator betreibt die Plattform selbst. Die Verwaltungsoberfläche ist standardmäßig nur über `127.0.0.1`/SSH-Tunnel erreichbar; der Benutzerzugriff auf OpenCloud ist separat zu entscheiden. Erste Referenzanwendung ist OpenCloud. Details siehe `PROJECT.md`.

## Für AI/Coding Agents
Vor Änderungen unbedingt `AGENTS.md` lesen.

## Dokumente
- `PROJECT.md`
- `ROADMAP.md`
- `WORKFLOW.md`
- `CODE_STYLE.md`
- `DEFINITION_OF_DONE.md`
- `CHANGELOG.md`

## Status
Projektinitialisierung / Proof of Concept.
