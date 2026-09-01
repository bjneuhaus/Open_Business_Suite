# OpenCloud-Service (R007–R014, Vertical Slice)

Diese Notiz beschreibt den gebündelten Vertical Slice, der Command
Execution, Podman-Voraussetzungen und die OpenCloud-Lebenszyklus-
verwaltung zusammenführt.

## Bausteine

| Modul | Verantwortung |
| --- | --- |
| `config/opencloud-image.env` | **Einzige Quelle der Wahrheit** für den gepinnten OpenCloud-Image-Digest (`OPENCLOUD_IMAGE_REPOSITORY`, `OPENCLOUD_IMAGE_DIGEST`). |
| `services/opencloud_image_config.py` | Lädt `config/opencloud-image.env` und stellt `OPENCLOUD_IMAGE_REF` (Repository@Digest) als Python-Konstanten bereit. |
| `services/command_runner.py` | Generischer, testbarer Wrapper um `subprocess.run`. Kennt keine konkreten Befehle. |
| `services/podman_service.py` | Unverändert seit R006: `is_available()` prüft nur `shutil.which("podman")`. |
| `services/opencloud_service.py` | `OpenCloudConfig` (Image/Port/Pfade) + `OpenCloudService` mit `install()`, `status()`, `start()`, `stop()`, `remove_container()`. `default_opencloud_config()` befüllt `image` automatisch mit dem gepinnten Digest. Baut `podman`-Kommandos und delegiert an `CommandRunner`. |
| `scripts/provision_opencloud.sh` | Einmaliges, manuelles Infrastruktur-Skript (Podman-Paket, systemd-Linger, Verzeichnisse, Pull des gepinnten Images). Bewusst außerhalb der Python-Anwendung, da die Anwendung selbst nie `sudo`/`apt` aufruft. Liest den Digest ebenfalls aus `config/opencloud-image.env`. |

## Feste Konfiguration (PoC)

- Image: gepinnt per Digest in [`config/opencloud-image.env`](../config/opencloud-image.env)
  (aktuell `docker.io/opencloudeu/opencloud-rolling@sha256:6db1cfb06d430a663f16e9f33dcd4596d82a4875be0b4df233c26ce5f667ea74`,
  verifiziert am 2026-08-31 auf der PoC-VM). Dieser Digest wird von
  Provisioning-Skript, `OpenCloudService` (via
  `default_opencloud_config()`) und dieser Dokumentation gemeinsam
  genutzt — es gibt keine verstreuten Duplikate. Ein Digest-Update
  erfolgt ausschließlich durch Bearbeiten dieser einen Datei, nachdem
  der neue Digest gegen die Registry verifiziert wurde.
- Container-Name: `opencloud`
- Port-Bindung: **ausschließlich** `127.0.0.1:9200` (nie öffentlich)
- Config-Verzeichnis: `~/opencloud/opencloud-config` → `/etc/opencloud`
- Daten-Verzeichnis: `~/opencloud/opencloud-data` → `/var/lib/opencloud`
- Rootless-Betrieb: `--userns=keep-id`

Digest-Pinning stellt sicher, dass wiederholte Auf-/Abbauzyklen während
der Entwicklung dasselbe, bereits verifizierte Image verwenden statt
bei jedem Neuaufbau möglicherweise eine andere Version über den
`latest`/rolling-Tag zu ziehen.

## Was absichtlich draußen bleibt

- `opencloud init` (einmalige Passwort-/Config-Erzeugung) bleibt ein
  **manueller, dokumentierter Schritt** (siehe unten), kein Teil von
  `OpenCloudService`. Grund: `init` verlangt in der aktuellen Rolling-
  Release interaktive Bestätigung für Zertifikatsprüfung und wird über
  `--insecure=true --admin-password <pw>` non-interaktiv ausgeführt;
  das Admin-Passwort wird dabei bewusst nie von der Anwendung selbst
  erzeugt, geloggt oder gespeichert.
- `OpenCloudService` bleibt HTTP-agnostisch; der minimale Web-Anschluss
  erfolgt seit R017 ausschließlich über `POST /install` in `app.py`.
  Dieser Schritt übernimmt keine Status-, Start-/Stop-, Fortschritts- oder
  technische Ausgabe-Funktionalität (R018–R020).
- Kein `apt`/`sudo`-Aufruf aus dem Python-Paket heraus (Prinzip der
  minimalen Rechte); das erledigt `provision_opencloud.sh` manuell.

## Manueller Aufbau und Start auf der Ziel-VM

Dieser Abschnitt beschreibt den vollständigen manuellen Ablauf für einen
frischen oder wiederholt neu aufgebauten Entwicklungsstand. Die
Verwaltungsoberfläche und OpenCloud werden nicht öffentlich gebunden; der
Browserzugriff erfolgt anschließend über einen SSH-Tunnel.

### Voraussetzungen

- Ubuntu-26.04-VM mit SSH-Zugriff und einem Benutzer mit `sudo`-Rechten
- Repository-Stand aus dem freigegebenen `main`-Branch
- Netzwerkzugriff der VM auf die Paketquelle und die Container-Registry
- Das OpenCloud-Admin-Passwort wird ausschließlich auf der VM erzeugt und
  in `~/.opencloud_admin_pw` mit Modus `0600` gespeichert; es wird niemals in
  Git, Chat oder Logs übernommen.

### Repository auf die VM übertragen

Die folgenden Befehle laufen zunächst auf dem lokalen Rechner. `git archive`
überträgt genau den geprüften Commit, ohne lokale `.git`-Metadaten oder andere
Arbeitsdateien auf die VM zu kopieren:

```bash
git checkout main
git pull --ff-only origin main

ssh username@server 'mkdir -p ~/open-business-suite'
git archive --format=tar HEAD | \
  ssh username@server \
  'tar -xf - -C ~/open-business-suite'
```

Bei einer anderen VM sind Benutzer und Adresse entsprechend zu ersetzen.

### Infrastruktur vorbereiten

Die folgenden Befehle laufen auf der Ziel-VM:

```bash
cd ~/open-business-suite
bash scripts/provision_opencloud.sh
```

Das idempotente Skript installiert bei Bedarf Podman, aktiviert systemd-
Linger für den Rootless-Betrieb, legt die persistenten Verzeichnisse an und
lädt das Image aus `config/opencloud-image.env`. Es startet noch keinen
Container.

### OpenCloud einmalig initialisieren

Diesen Schritt nur ausführen, wenn
`~/opencloud/opencloud-config/opencloud.yaml` noch nicht existiert:

```bash
cd ~/open-business-suite
umask 077

if [ ! -s "$HOME/.opencloud_admin_pw" ]; then
    openssl rand -base64 18 > "$HOME/.opencloud_admin_pw"
fi
chmod 600 "$HOME/.opencloud_admin_pw"

if [ ! -f "$HOME/opencloud/opencloud-config/opencloud.yaml" ]; then
    source config/opencloud-image.env
    IMAGE_REF="${OPENCLOUD_IMAGE_REPOSITORY}@${OPENCLOUD_IMAGE_DIGEST}"
    ADMIN_PW=$(<"$HOME/.opencloud_admin_pw")

    podman run --rm \
      --userns=keep-id \
      -v "$HOME/opencloud/opencloud-config:/etc/opencloud" \
      -v "$HOME/opencloud/opencloud-data:/var/lib/opencloud" \
      --entrypoint opencloud "$IMAGE_REF" init \
      --admin-password "$ADMIN_PW" \
      --insecure=true \
      --quiet
fi
```

Der Passwortwert wird bei diesem Ablauf nicht ausgegeben. Ein vorhandenes
`opencloud.yaml` wird nicht überschrieben.

### OpenCloud starten

Der Start erfolgt über den versionierten `OpenCloudService`; der Service
verwendet die zentrale Digest-Konfiguration und bindet ausschließlich an
`127.0.0.1`:

```bash
cd ~/open-business-suite
export PYTHONPATH="$PWD/src"

python3 -c '
import os

from sovereign_business_suite.services.command_runner import CommandRunner
from sovereign_business_suite.services.opencloud_service import (
    OpenCloudService,
    default_opencloud_config,
)

service = OpenCloudService(
    default_opencloud_config(
        os.path.expanduser("~/opencloud/opencloud-config"),
        os.path.expanduser("~/opencloud/opencloud-data"),
    ),
    CommandRunner(),
)
result = service.install()
print(result.returncode, result.succeeded)
'
```

Wenn der Container bereits angelegt, aber gestoppt ist, genügt bei einem
späteren Neustart:

```bash
podman start opencloud
```

### Verwaltungsoberfläche starten

Die Flask-Anwendung benötigt eine isolierte Python-Umgebung. Auf einer
frischen Ubuntu-VM ist dafür einmalig das Paket `python3-venv` erforderlich:

```bash
cd ~/open-business-suite
sudo apt-get install -y python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip install -r requirements.txt
```

Die Anwendung wird anschließend im Hintergrund und nur auf localhost
gestartet:

```bash
nohup .venv/bin/python -m flask \
  --app sovereign_business_suite.app run \
  --host 127.0.0.1 \
  --port 5000 \
  --no-debugger \
  --no-reload \
  > ~/.open-business-suite-admin.log 2>&1 < /dev/null &
printf "%s\n" "$!" > ~/.open-business-suite-admin.pid
```

### Zugriff und Test-URLs

Auf dem lokalen Rechner wird der SSH-Tunnel für beide Dienste geöffnet:

```bash
ssh \
  -L 5000:127.0.0.1:5000 \
  -L 9200:127.0.0.1:9200 \
  username@server
```

Danach sind diese URLs im lokalen Browser erreichbar:

| Zweck | URL |
| --- | --- |
| Admin-Startseite | `http://127.0.0.1:5000/` |
| Anwendungskatalog | `http://127.0.0.1:5000/catalog` |
| Konfigurations-Wizard | `http://127.0.0.1:5000/configure` |
| OpenCloud | `https://127.0.0.1:9200/` |

Die drei Admin-URLs sollten HTTP `200` liefern. OpenCloud sollte HTTPS `200`
liefern. Beim ersten Aufruf von OpenCloud muss im PoC die Warnung für das
selbstsignierte Zertifikat einmalig bestätigt werden.

### Manuelle Statusprüfung

Die folgenden `curl`-Befehle können auf der Ziel-VM oder auf dem lokalen
Rechner bei aktivem SSH-Tunnel ausgeführt werden. `podman`-Befehle werden auf
der Ziel-VM ausgeführt:

```bash
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/catalog
curl http://127.0.0.1:5000/configure
curl --insecure https://127.0.0.1:9200/

podman ps
podman port opencloud
```

Erwartet wird ein laufender Container mit der Bindung
`127.0.0.1:9200->9200/tcp`; der Flask-Prozess lauscht auf
`127.0.0.1:5000`.

## Teardown

Für einen wiederholbaren Entwicklungszyklus kann die laufende Anwendung
beendet und der OpenCloud-Container entfernt werden:

```bash
# auf der Ziel-VM: Flask-Prozess beenden, falls er über die PID-Datei gestartet wurde
if [ -s "$HOME/.open-business-suite-admin.pid" ]; then
    kill "$(<"$HOME/.open-business-suite-admin.pid")" 2>/dev/null || true
    rm -f "$HOME/.open-business-suite-admin.pid"
fi

cd ~/open-business-suite
export PYTHONPATH="$PWD/src"
python3 -c '
import os

from sovereign_business_suite.services.command_runner import CommandRunner
from sovereign_business_suite.services.opencloud_service import (
    OpenCloudService,
    default_opencloud_config,
)

result = OpenCloudService(
    default_opencloud_config(
        os.path.expanduser("~/opencloud/opencloud-config"),
        os.path.expanduser("~/opencloud/opencloud-data"),
    ),
    CommandRunner(),
).remove_container()
print(result.returncode, result.succeeded)
raise SystemExit(0 if result.succeeded else 1)
'
```

`remove_container()` entfernt ausschließlich den Container. Das Image bleibt
erhalten (kein erneuter Download nötig), ebenso die Config-/Datenverzeichnisse
auf dem Host. Bei Bedarf kann zusätzlich die lokale `.venv` entfernt werden;
`podman system prune` oder eine Image-Löschung gehört ausdrücklich nicht zu
diesem Teardown.

## Tests

Alle Tests in `tests/test_command_runner.py` und
`tests/test_opencloud_service.py` verwenden Mocks/Fakes für
`subprocess.run` bzw. `CommandRunner` — es findet kein echter
Prozessaufruf statt. Die reale Verifikation gegen die PoC-VM erfolgt
separat und wird hier nicht automatisiert getestet.
