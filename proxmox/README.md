# Tautulli auf Proxmox

Installiert Tautulli (dieser Fork, mit deutscher Oberfläche) als Python-Dienst in einem
unprivilegierten Debian-13-Container. Die Skripte folgen dem Aufbau von community-scripts.

## Installation

Auf der Shell des Proxmox-Hosts:

```bash
COMMUNITY_SCRIPTS_URL=https://raw.githubusercontent.com/brunoz78/Tautulli/master/proxmox bash -c "$(curl -fsSL https://raw.githubusercontent.com/brunoz78/Tautulli/master/proxmox/ct/tautulli.sh)"
```

Vorgaben lassen sich voranstellen, zum Beispiel `var_ctid=312 var_hostname=pm-tautulli
var_net=192.168.1.50/24 var_gateway=192.168.1.1`.

Danach ist Tautulli unter `http://<IP>:8181` erreichbar und startet mit dem
Einrichtungsassistenten.

## Aufbau im Container

| Pfad | Inhalt |
|---|---|
| `/opt/Tautulli` | Programm (Python-Bibliotheken liegen in `lib/`) |
| `/config` | Daten: `config.ini`, `tautulli.db`, `logs/`, `backups/`, `cache/`, `exports/`, `newsletters/` |

Dienst: `tautulli.service`. Protokoll: `journalctl -u tautulli -f`.

## Umzug aus dem Docker-Image linuxserver/tautulli

Das Image legt alle Daten in `/config` ab, genau wie dieser Container. Statistik, Benutzer,
Benachrichtigungen und Einstellungen bleiben beim Umzug erhalten.

1. Den Docker-Container stoppen (nicht löschen), damit die Datenbank nicht mehr beschrieben wird.
2. Den Inhalt des Volumes sichern, zum Beispiel auf dem Docker-Host:
   `tar -C /pfad/zum/volume -czf tautulli-config.tar.gz .`
3. Im neuen Container den Dienst stoppen: `systemctl stop tautulli`
4. Das Archiv nach `/config` entpacken: `tar -C /config -xzf tautulli-config.tar.gz`
5. Dienst starten: `systemctl start tautulli`

Die Pfade in `config.ini` zeigen bereits auf `/config/...` und passen ohne Änderung. Hängt am
Docker-Container eine eigene Adresse in Benachrichtigungen oder im Reverse-Proxy, diese auf die
neue IP umstellen. Den Docker-Container erst entfernen, wenn der neue Tautulli läuft.

## Update

- In Tautulli: Einstellungen → «Nach Updates suchen». Tautulli lädt die neue Version aus diesem
  Fork und startet neu.
- In der Container-Konsole: `update`.

Neue Versionen erscheinen, wenn das Original ein Release veröffentlicht; der Fork übernimmt es
mit der deutschen Übersetzung.

## Einstellungen

In `/etc/systemd/system/tautulli.service` (danach `systemctl daemon-reload && systemctl
restart tautulli`):

- `TAUTULLI_UI_LANG=de`: Grundsprache für alle Browser. Ohne den Eintrag gilt die Sprache des
  Browsers. Pro Browser lässt sie sich unter Einstellungen → Allgemein → «Sprache der
  Oberfläche» umstellen.
- `TZ=Europe/Zurich`: Zeitzone.
