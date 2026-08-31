# OpenCloud-Service (R007–R014, Vertical Slice)

Diese Notiz beschreibt den gebündelten Vertical Slice, der Command
Execution, Podman-Voraussetzungen und die OpenCloud-Lebenszyklus-
verwaltung zusammenführt.

## Bausteine

| Modul | Verantwortung |
| --- | --- |
| `services/command_runner.py` | Generischer, testbarer Wrapper um `subprocess.run`. Kennt keine konkreten Befehle. |
| `services/podman_service.py` | Unverändert seit R006: `is_available()` prüft nur `shutil.which("podman")`. |
| `services/opencloud_service.py` | `OpenCloudConfig` (Image/Port/Pfade) + `OpenCloudService` mit `install()`, `status()`, `start()`, `stop()`, `remove_container()`. Baut `podman`-Kommandos und delegiert an `CommandRunner`. |
| `scripts/provision_opencloud.sh` | Einmaliges, manuelles Infrastruktur-Skript (Podman-Paket, systemd-Linger, Verzeichnisse). Bewusst außerhalb der Python-Anwendung, da die Anwendung selbst nie `sudo`/`apt` aufruft. |

## Feste Konfiguration (PoC)

- Image: `docker.io/opencloudeu/opencloud-rolling:latest`
- Container-Name: `opencloud`
- Port-Bindung: **ausschließlich** `127.0.0.1:9200` (nie öffentlich)
- Config-Verzeichnis: `~/opencloud/opencloud-config` → `/etc/opencloud`
- Daten-Verzeichnis: `~/opencloud/opencloud-data` → `/var/lib/opencloud`
- Rootless-Betrieb: `--userns=keep-id`

Bekannte offene Verbesserung: `latest`/"rolling" ist kein reproduzierbarer
Tag. Eine feste Versions-/Digest-Pinning-Entscheidung ist für einen
späteren Roadmap-Punkt vorgesehen und bewusst nicht Teil dieses Slices.

## Was absichtlich draußen bleibt

- `opencloud init` (einmalige Passwort-/Config-Erzeugung) bleibt ein
  **manueller, dokumentierter Schritt** (siehe unten), kein Teil von
  `OpenCloudService`. Grund: `init` verlangt in der aktuellen Rolling-
  Release interaktive Bestätigung für Zertifikatsprüfung und wird über
  `--insecure=true --admin-password <pw>` non-interaktiv ausgeführt;
  das Admin-Passwort wird dabei bewusst nie von der Anwendung selbst
  erzeugt, geloggt oder gespeichert.
- Kein Flask-Endpoint für `install()`/`status()`/`start()`/`stop()` in
  diesem Slice — reine Service-Schicht, Web-Anbindung ist ein späterer
  Schritt.
- Kein `apt`/`sudo`-Aufruf aus dem Python-Paket heraus (Prinzip der
  minimalen Rechte); das erledigt `provision_opencloud.sh` manuell.

## Manueller Bootstrap auf der Ziel-VM

```bash
# 1. Einmalige Infrastruktur-Vorbereitung
bash scripts/provision_opencloud.sh

# 2. Einmalige OpenCloud-Konfiguration (Admin-Passwort wird generiert,
#    NIE ins Repo oder in Logs geschrieben)
ADMIN_PW=$(openssl rand -base64 18)
echo "$ADMIN_PW" > ~/.opencloud_admin_pw
chmod 600 ~/.opencloud_admin_pw
podman run --rm \
  --userns=keep-id \
  -v ~/opencloud/opencloud-config:/etc/opencloud \
  -v ~/opencloud/opencloud-data:/var/lib/opencloud \
  --entrypoint opencloud \
  docker.io/opencloudeu/opencloud-rolling:latest init \
  --admin-password "$ADMIN_PW" \
  --insecure=true \
  --quiet
```

Danach übernimmt `OpenCloudService.install()` das Starten des
eigentlichen Servers.

## Zugriff

Die Web-Oberfläche ist ausschließlich über `127.0.0.1:9200` auf der VM
erreichbar. Zugriff von außen ausschließlich per SSH-Tunnel:

```bash
ssh -L 9200:127.0.0.1:9200 <benutzer>@<vm-adresse>
```

Danach im Browser: `https://127.0.0.1:9200/` (selbstsigniertes
Zertifikat im PoC — Browser-Warnung einmalig akzeptieren).

## Teardown

`OpenCloudService.remove_container()` entfernt ausschließlich den
Container. Das Image bleibt erhalten (kein erneuter Download nötig),
ebenso die Config-/Datenverzeichnisse auf dem Host. Ein vollständiger
Rückbau (Image- und Datenlöschung) ist kein Bestandteil dieses Slices
und würde einen expliziten, separat freizugebenden Schritt erfordern.

## Tests

Alle Tests in `tests/test_command_runner.py` und
`tests/test_opencloud_service.py` verwenden Mocks/Fakes für
`subprocess.run` bzw. `CommandRunner` — es findet kein echter
Prozessaufruf statt. Die reale Verifikation gegen die PoC-VM erfolgt
separat und wird hier nicht automatisiert getestet.
