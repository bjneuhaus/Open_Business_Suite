# Podman-Verfügbarkeit (R006)

Kurze Notiz zur ersten, bewusst minimalen Podman-Integration.

## Umfang von R006

`PodmanService.is_available()` prüft ausschließlich, ob der
`podman`-Befehl über `shutil.which("podman")` auf dem `PATH` des Hosts
gefunden wird.

Bewusst **nicht** Bestandteil von R006:

- Aufruf von `podman version` oder einem anderen Unterbefehl
- jeder `subprocess`-Aufruf (folgt in R007 – Command Execution)
- Starten, Stoppen oder Prüfen von Containern (folgt ab R012+ –
  OpenCloud Installation)
- Installation von Podman auf der Ziel-VM (bleibt manuelle
  Administrator-Aufgabe im PoC)

## Verifikation auf der Ziel-VM

Auf der PoC-Ziel-VM (`training@<vm-adresse>`, Ubuntu 26.04) ist Podman
zum Zeitpunkt von R006 noch nicht installiert (`which podman` liefert
keinen Treffer). `PodmanService.is_available()` liefert dort also
korrekt `False`. Die Installation von Podman selbst ist nicht
Bestandteil dieses Roadmap-Punkts.

## Tests

`tests/test_podman_service.py` verwendet `monkeypatch`, um
`shutil.which` zu ersetzen, und deckt drei Fälle ab:

- Podman ist auf `PATH` vorhanden → `True`
- Podman ist nicht auf `PATH` vorhanden → `False`
- es wird exakt nach dem Namen `"podman"` gesucht

Die Tests führen keinen echten Prozessaufruf aus und sind daher
unabhängig davon lauffähig, ob Podman auf der jeweiligen
Entwicklungsmaschine installiert ist.
