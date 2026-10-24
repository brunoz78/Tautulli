# Tautulli auf Deutsch

Dieser Fork bringt [Tautulli](https://github.com/Tautulli/Tautulli), das Überwachungs- und
Statistikwerkzeug für den [Plex Media Server](https://plex.tv), mit einer **deutschen
Oberfläche**. Dazu kommen eine Installation als Container auf **Proxmox** und Updates, die direkt
aus diesem Fork kommen.

Ansonsten ist es das Original: Jedes offizielle Release von Tautulli wird automatisch übernommen.

<p align="center">
  <a href="https://github.com/brunoz78/Tautulli/releases/latest">
    <img src="https://img.shields.io/github/v/release/brunoz78/Tautulli?display_name=release&amp;logo=github&amp;label=Aktuelles%20Release&amp;style=for-the-badge" alt="Aktuelles Release">
  </a>
  <a href="https://github.com/brunoz78/Tautulli/actions/workflows/fork-sync.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/brunoz78/Tautulli/fork-sync.yml?label=Wochenabgleich&amp;style=for-the-badge&amp;logo=github" alt="Wochenabgleich">
  </a>
</p>

## Was du hier bekommst

- **Deutsche Oberfläche:** Menüs, Einstellungen, Tabellen, Grafiken, Meldungen und die
  Beschreibungen der Benachrichtigungs-Parameter sind übersetzt, in Schweizer Schreibweise.
  Datums- und Monatsnamen folgen der Sprache.
- **Umschaltbar:** *Einstellungen → Allgemein → Sprache der Oberfläche* (Deutsch oder Englisch,
  gilt pro Browser). Ohne Auswahl gilt die Grundsprache des Servers, sonst die des Browsers.
- **Updates in der App:** *Einstellungen → «Nach Updates suchen»* holt die neueste deutsche
  Ausgabe aus diesem Fork und startet Tautulli neu.
- **Proxmox-Container:** ein Script legt einen Debian-13-Container an und installiert Tautulli
  als Dienst, ohne Docker.
- **Aktuell ohne Aufwand:** Jeden Montag prüft ein Workflow, ob das Original ein neues Release
  hat. Wenn ja, wird es eingespielt und als neues Release `<Version>.post<Datum>` veröffentlicht.
  Bringt es neue englische Texte mit, erscheinen sie als Issue in diesem Fork und werden
  nachübersetzt.

Deine eigenen Texte (Benachrichtigungen, Newsletter) und deine Daten aus Plex (Titel, Namen,
Geräte) bleiben unverändert.

## Installation auf Proxmox

Auf der Shell des Proxmox-Hosts:

```bash
COMMUNITY_SCRIPTS_URL=https://raw.githubusercontent.com/brunoz78/Tautulli/master/proxmox bash -c "$(curl -fsSL https://raw.githubusercontent.com/brunoz78/Tautulli/master/proxmox/ct/tautulli.sh)"
```

Danach ist Tautulli unter `http://<IP>:8181` erreichbar und startet mit dem
Einrichtungsassistenten.

**Umzug aus Docker:** Die Daten liegen in `/config`, im gleichen Aufbau wie beim Image
`linuxserver/tautulli`. Verlauf, Benutzer, Statistik und Benachrichtigungen lassen sich darum
1:1 übernehmen. Die Schritte stehen in [proxmox/README.md](../proxmox/README.md).

## Wie die Übersetzung funktioniert

Die Dateien des Originals bleiben unverändert, bis auf eine einzige Zeile in `Tautulli.py`. Die
Übersetzung geschieht beim Anzeigen im Browser anhand eines Wörterbuchs
(`data/interfaces/default/js/i18n/de.js`). So fliessen neue Versionen des Originals ohne
Konflikte ein. Details für die Pflege stehen in [FORK.md](../FORK.md).

## Hilfe

- **Übersetzung oder Proxmox-Installation:** Fehler oder englische Reste bitte hier als
  [Issue](https://github.com/brunoz78/Tautulli/issues) melden.
- **Bedienung von Tautulli:** Die [Doku des Originals](https://docs.tautulli.com/) und die
  [häufigen Fragen](https://docs.tautulli.com/support/frequently-asked-questions) gelten auch
  hier (auf Englisch).
- **Fehler in Tautulli selbst,** die auch im Original auftreten, gehören zum
  [Original](https://github.com/Tautulli/Tautulli/issues).

## Lizenz

Wie das Original unter der [GNU General Public License v3](../LICENSE).
