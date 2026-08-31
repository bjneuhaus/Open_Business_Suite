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
- Kein Flask-Endpoint für `install()`/`status()`/`start()`/`stop()` in
  diesem Slice — reine Service-Schicht, Web-Anbindung ist ein späterer
  Schritt.
- Kein `apt`/`sudo`-Aufruf aus dem Python-Paket heraus (Prinzip der
  minimalen Rechte); das erledigt `provision_opencloud.sh` manuell.

## Manueller Bootstrap auf der Ziel-VM

```bash
# 1. Einmalige Infrastruktur-Vorbereitung (liest den gepinnten Digest
#    aus config/opencloud-image.env und pullt genau dieses Image)
bash scripts/provision_opencloud.sh

# 2. Einmalige OpenCloud-Konfiguration (Admin-Passwort wird generiert,
#    NIE ins Repo oder in Logs geschrieben)
source config/opencloud-image.env
IMAGE_REF="${OPENCLOUD_IMAGE_REPOSITORY}@${OPENCLOUD_IMAGE_DIGEST}"
ADMIN_PW=$(openssl rand -base64 18)
echo "$ADMIN_PW" > ~/.opencloud_admin_pw
chmod 600 ~/.opencloud_admin_pw
podman run --rm \
  --userns=keep-id \
  -v ~/opencloud/opencloud-config:/etc/opencloud \
  -v ~/opencloud/opencloud-data:/var/lib/opencloud \
  --entrypoint opencloud \
  "$IMAGE_REF" init \
  --admin-password "$ADMIN_PW" \
  --insecure=true \
  --quiet
```

Danach übernimmt `OpenCloudService.install()` (mit einer über
`default_opencloud_config()` erzeugten Konfiguration) das Starten des
eigentlichen Servers — ebenfalls mit dem gepinnten Digest.

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
