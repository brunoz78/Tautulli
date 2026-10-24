# Tautulli mit deutscher Oberfläche

Dieser Fork von [Tautulli/Tautulli](https://github.com/Tautulli/Tautulli) ergänzt eine deutsche
Weboberfläche. Sonst entspricht er dem jeweils neuesten offiziellen Release des Originals.

## Was der Fork ändert

- **Deutsche Oberfläche:** `data/interfaces/default/js/i18n/i18n.js` übersetzt die Texte im
  Browser anhand von `js/i18n/de.js`. Die Vorlagen und Skripte des Originals bleiben
  unverändert. Datums- und Monatsnamen (moment) und Grafiken (Highcharts) folgen der Sprache.
- **Sprache wählen:** Einstellungen → Allgemein → «Sprache der Oberfläche» (gilt pro Browser,
  Cookie `tautulli_lang`). Ohne Wahl gilt `TAUTULLI_UI_LANG`, sonst die Sprache des Browsers.
- **Updates aus dem Fork:** Der eingebaute Updater sucht neue Versionen in `brunoz78/Tautulli`,
  solange in `config.ini` noch das Original eingetragen ist.
- **Proxmox:** `proxmox/` enthält ein Community-Script für einen Debian-Container
  (siehe `proxmox/README.md`).

Alles Eigene hängt an `fork_addons.py`; im Original ist nur eine Zeile in `Tautulli.py` dazugekommen.

## Übersetzung pflegen

```bash
python tools/i18n/extract.py               # Texte sammeln -> tools/i18n/strings.json
python tools/i18n/extract.py --missing de  # fehlende Übersetzungen anzeigen
python tools/i18n/translate.py de          # fehlende per Claude-API übersetzen (ANTHROPIC_API_KEY)
```

Texte, die keine Oberfläche sind (Produktnamen, Code), stehen in `tools/i18n/ignore.json`.
Fehlersuche im Browser: `localStorage.tautulli_i18n_debug = "1"`, Seite neu laden, dann
`tautulliI18n.missing()` in der Konsole.

## Abgleich mit dem Original

`.github/workflows/fork-sync.yml` läuft montags: Es übernimmt das neueste offizielle Release des
Originals, übersetzt neue Texte (Secret `ANTHROPIC_API_KEY`, sonst ein Issue), prüft den Start
und veröffentlicht ein Release `v<Version>.post<Datum>`. Bei einem Merge-Konflikt entsteht ein
Issue. Ändert das Original Workflow-Dateien, braucht der Push das Secret `SYNC_TOKEN`
(Rechte *Contents* und *Workflows*). Die Workflows des Originals sind im Fork abgeschaltet.

Der Updater von Tautulli folgt dem Branch `master`. Darum wird `master` nur mit einem neuen
Release des Originals oder einer Änderung am Fork weitergeschoben.

## Tests

```bash
python -m pytest tests/test_fork_additions.py
```
