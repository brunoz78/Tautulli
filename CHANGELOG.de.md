# Changelog

## v2.19.1 (2026-11-10)

* Sonstiges:
  * Behoben: Snap-Paket startete nicht.


## v2.19.0 (2026-11-10)

* Hinweise:
  * Python 3.10 wird nicht mehr unterstützt. Neu ist mindestens Python 3.11 nötig.
  * Installationen ohne Passwort erhalten beim Update ein zufälliges temporäres Passwort. Die Anmeldedaten stehen im Tautulli-Protokoll. Ändere das Passwort nach der Anmeldung in den Einstellungen.
* Aktivität:
  * Geändert: «ETA» auf den Aktivitätskarten heisst jetzt «Endet um». (#2574)
* Verlauf:
  * Behoben: Filtern der Verlaufstabellen auf den Medienseiten von Sammlungen und Playlists zeigte falsche Ergebnisse.
  * Neu: Benutzer und Mediatheken lassen sich archivieren, ihr Verlauf bleibt erhalten. (#1435, #2778) (Danke @akonopcz)
    * Hinweis: Archivierte Benutzer und Mediatheken sind standardmässig aus Verlauf und Statistik ausgeblendet. Mit «Archivierte Daten anzeigen» im Menü der Navigationsleiste lassen sie sich einblenden.
  * Neu: Gelöschte Benutzer und Mediatheken lassen sich im Bearbeitungsmodus der Tabellen wiederherstellen.
* Benachrichtigungen:
  * Behoben: Telegram-Benachrichtigungen mit Poster und Bildtext erschienen im Benachrichtigungsprotokoll als fehlgeschlagen. (#2852) (Danke @PilaScat)
  * Behoben: Die Parameter für Dolby-Vision-Profil und -Level bleiben leer, wenn kein Dolby Vision vorhanden ist. (#2381)
  * Behoben: Direktlinks in Benachrichtigungen für die Plex-App unter Android und iOS funktionierten nicht.
  * Neu: Ace-Editor zum Bearbeiten der Benachrichtigungstexte.
  * Neu: Ausschluss-Tag für Live-TV in Benachrichtigungen.
  * Neu: Benachrichtigungs-Parameter mit der Letterboxd-URL. (#1904)
  * Neu: Reply-To-Header für den E-Mail-Benachrichtigungsdienst. (#1702)
  * Entfernt: OneSignal-Benachrichtigungen für die Tautulli-Remote-App.
* Newsletter:
  * Behoben: Ein leerer Betreff, Text oder eine leere Nachricht liess sich nicht speichern.
  * Neu: Zeiträume in Wochen und Jahren für Newsletter. (#2042)
  * Neu: Anzahlen in den Parametern für neu hinzugefügte Elemente. (#1787)
  * Behoben: Eigene Newsletter-Vorlagen dürfen nicht mehr im Ausgabeordner der Newsletter liegen. (Danke @SHAHID-XT)
  * Behoben: Absturz des Newsletter-Zeitplans, wenn die lokale Zeitzone nicht ermittelt werden konnte. (#2889, #2890)
* Export:
  * Behoben: Lange Titel werden in den Dateinamen der Exporte gekürzt. (#2777)
* Oberfläche:
  * Behoben: Das zusammengesetzte Poster von Sammlungen fehlte auf den Medienseiten.
  * Behoben: Defekter Link von Sammlungen zu Plex Web auf den Medienseiten.
  * Behoben: Der Hinweis auf ein abgelaufenes Plex-Token erschien nicht.
  * Behoben: Titel von Playlists werden in den Playlist-Tabellen maskiert. (CVE-2026-TBD) (Danke @Cbdlll)
  * Behoben: Medieninfo-Felder werden in den Medieninfo-Tabellen maskiert. (CVE-2026-TBD) (Danke @Cbdlll)
  * Behoben: Die Untertitelsprache wird auf den Aktivitätskarten maskiert. (CVE-2026-TBD) (Danke @Cbdlll)
  * Neu: Verschiedene Korrekturen und Verbesserungen an der Oberfläche.
  * Neu: «Neu hinzugefügt» auf der Startseite kann mehrere Medientypen gleichzeitig zeigen. (#2733)
  * Neu: Die Anmeldung mit Tautulli lässt sich abschalten, sodass nur noch die Plex-Anmeldung geht. (#2092)
* API:
  * Neu: Parameter include_archived für alle API-Befehle zu Verlauf und Statistik.
  * Neu: user_is_archived und library_is_archived in der Antwort von get_history.
  * Neu: deleted_user und is_archived in der Antwort von get_users_table.
  * Neu: deleted_section und is_archived in der Antwort von get_libraries_table.
  * Neu: is_archived in den Antworten von get_user, get_users, get_user_names, get_library und get_library_names.
  * Neu: Parameter row_ids für die API-Befehle undelete_user und undelete_library.
  * Neu: Parameter include_last_triggered für den API-Befehl get_notifiers.
  * Neu: Der API-Befehl get_recently_added nimmt eine kommagetrennte Liste von Medientypen an.
* Sonstiges:
  * Behoben: Einige Standardeinstellungen wurden nach dem Einrichtungsassistenten wieder ausgeschaltet.
  * Behoben: SSRF in /pms_image_proxy durch uneingeschränkte externe Bild-URLs. (CVE-2026-TBD) (Danke @larlarua)
  * Behoben: CSRF über GET-Endpunkte mit Zustandsänderung erlaubte administrative Aktionen. (CVE-2026-TBD) (Danke @zaara2004)
  * Behoben: Erzeugen selbst signierter SSL-Zertifikate funktionierte nicht.
  * Behoben: Eine Änderung des Admin-Passworts meldete bestehende Sitzungen nicht ab. (#2868) (Danke @spjoes)
  * Behoben: Befehlsinjektion über GIT_PATH. (@SHAHID-XT)
  * Neu: Grosse Optimierungen der Datenbank und bessere Leistung.
  * Neu: Installation über Homebrew Cask für macOS. (#2867) (Danke @manakbisht)
  * Neu: Installation über Flatpak für Linux.
  * Neu: CPU-Architektur in der Nutzungsstatistik.
  * Neu: Docker-Image sowie Pakete für Windows und macOS auf Python 3.14.
  * Neu: Protokollmeldungen enthalten bei Fehlern den vollständigen Traceback. (#2760)
  * Neu: Ohne Passwort werden Zugriffe von ausserhalb des lokalen Netzes abgelehnt. Abschaltbar mit allow_public_no_password = 1 in der Konfigurationsdatei.
  * Neu: Die IP-Adresse fehlgeschlagener Anmeldungen wird protokolliert. (#2092)
  * Neu: Neue Installationen erhalten ein zufälliges temporäres Passwort für den Einrichtungsassistenten. (CVE-2026-TBD) (Danke @SHAHID-XT)
  * Neu: Bestehende Installationen ohne Passwort erhalten ein zufälliges temporäres Passwort.
  * Geändert: Der Header X-Api-Key gilt nur noch für `/api` und `/auth/signin`.
  * Entfernt: Kein Docker-Image mehr für arm/v6.
  * Entfernt: Das Installationspaket für Intel x86_64 unterstützt macOS 10.13 und 10.14 nicht mehr.
  * Entfernt: Endpunkt /delete_duplicate_libraries.
  * Entfernt: Import aus PlexWatch und Plexivity.


## v2.18.2 (2026-09-28)

* Aktivität:
  * Behoben: IPv6-Adressen überlagerten die ETA auf den Aktivitätskarten.
  * Behoben: Lange Live-TV-Sendernamen ragten über die Aktivitätskarte hinaus.
* Verlauf:
  * Behoben: Beim Gruppieren von Verlauf ausserhalb von Live-TV muss die GUID übereinstimmen. (#2768, #2769) (Danke @vefilippo)
  * Behoben: Neugruppieren des Verlaufs teilte Live-TV auf.
  * Behoben: Neugruppieren des Verlaufs anhand früherer Dauern und Marker.
    * Hinweis: Ein Neugruppieren des bestehenden Verlaufs verwendet die neue Logik und teilt den Verlauf anhand der GUID auf.
* Benachrichtigungen:
  * Behoben: Benachrichtigungen «Neu hinzugefügt» stürzten ab, wenn das Element vor dem Senden aus Plex entfernt wurde. (#2751) (Danke @TowyTowy)
  * Behoben: Benachrichtigungen zu Pausen kamen wiederholt, während ein Stream puffert.
  * Neu: «undisclosed-recipients:;» ist im Empfängerfeld von E-Mails und Newslettern erlaubt. (#2763, #2837) (Danke @thePFLy)
  * Neu: Gruppierte Titel auf den Infokarten enthalten Bereiche von Staffeln, Folgen und Titeln. (#2835, #2836) (Danke @herikwebb)
* Newsletter:
  * Behoben: Pfad-Traversal im Dateinamen von Newslettern. (Danke @router0mail)
  * Neu: edition_title in den JSON-Daten der Newsletter. (#2840)
* Export:
  * Neu: Angaben zur Lautheitsnormalisierung in den Exportfeldern für die Tonspuren von Filmen und Folgen.
* Oberfläche:
  * Behoben: Vom Server erzeugte HTML-Seiten werden nicht mehr zwischengespeichert. (#2810, #2811)
  * Behoben: Statistik-Karten auf der Startseite liefen in Firefox 155.0 über oder wurden abgeschnitten. (#2821)
  * Neu: X-Frame-Options-Header für die Einstellungsseite.
  * Neu: Links in Tabellenzellen sind leichter zu treffen. (#2754) (Danke @stephenp)
* API:
  * Behoben: Der API-Befehl logout_user_session meldete auch bei Erfolg einen Fehler.
  * Neu: edition_title in der Antwort des API-Befehls get_recently_added.
* Sonstiges:
  * Behoben: Datenbanksicherungen scheiterten, wenn der Sicherungsordner auf einer Netzwerkfreigabe lag. (#2824)
  * Behoben: Importierte Datenbanken wurden nicht optimiert.
  * Neu: Option, beim Windows-Installer keine Desktop-Verknüpfung anzulegen.
  * Neu: Schalter /NOLAUNCH für den Windows-Installer, damit Tautulli nach der Installation nicht startet. (#2234)
  * Neu: Schalter /NOBROWSER für den Windows-Installer, damit sich nach der Installation kein Browser öffnet.


## v2.18.1 (2026-08-26)

* Aktivität:
  * Behoben: Leere Sitzungszeilen wurden in die Datenbank geschrieben.
* Verlauf:
  * Behoben: Der ausführliche Verlauf liess sich nicht aufklappen, wenn «Aktuelle Aktivität in Verlaufstabellen» aktiv war. (#2805)
* Benachrichtigungen:
  * Behoben: Das E-Mail-Passwort wurde beim Speichern der E-Mail-Einstellungen mit einem leeren Wert überschrieben. (#2804)
  * Behoben: Die Benachrichtigung zu neuen Geräten wurde für den lokalen Benutzer erneut ausgelöst. (#2795)
  * Behoben: Platzhalterwerte erschienen in Benachrichtigungstexten innerhalb von Backticks. (#2794)
* Sonstiges:
  * Neu: X-Frame-Options-Header in der Konfigurationsdatei. (#2807)
* API:
  * Behoben: Gastbenutzer konnten über die API den Verlauf anderer Benutzer abrufen.
  * Geändert: Die doppelt verschachtelten Daten in der Antwort von get_plex_logs sind rückgängig gemacht. (#2806)


## v2.18.0 (2026-08-25)

* Aktivität:
  * Behoben: Anzeige der 4K-Auflösung auf den Aktivitätskarten.
  * Neu: Dolby Atmos auf den Aktivitätskarten.
* Benachrichtigungen:
  * Neu: Benachrichtigungs-Parameter für Dolby Atmos.
  * Neu: Benachrichtigungen für die Tautulli-Remote-App laufen über einen Push-Relay statt OneSignal. OneSignal-Benachrichtigungen werden ab dem 1. Oktober 2026 eingestellt. (#2772)
* Export:
  * Neu: editionTitle in den Exportfeldern für Serien, Staffeln und Folgen.
* Verlauf:
  * Behoben: Die Verlaufstabelle wurde beim Laden der Seite doppelt aktualisiert.
  * Behoben: Die Seitenaufteilung der Tabellen geschieht in SQL statt in Python. (#2728) (Danke @stephenp)
  * Behoben: Verschiedene Datenbank-Optimierungen für schnellere Verlaufsabfragen.
* Oberfläche:
  * Behoben: Benutzer und Mediatheken liessen sich in den Tabellen nicht bearbeiten.
  * Behoben: Statistik-Karten auf der Startseite liefen in Firefox 153.0.3 über oder wurden abgeschnitten. (#2776, #2787) (Danke @maldis018)
  * Neu: Knopf zum Löschen und Wiederherstellen von Benutzern und Mediatheken auf deren Profilseiten.
  * Neu: Schalter für die anonyme Nutzungsstatistik im Einrichtungsassistenten und in den Einstellungen. (#2781)
* Sonstiges:
  * Behoben: Besseres Auslesen der Plex-Protokolldateien.
  * Behoben: Pfad-Traversal beim Entpacken von Update-Archiven. (Danke @tonghuaroot)
  * Behoben: Plex-Token konnte über eine Umgehung mit Gross-/Kleinschreibung in pms_image_proxy abfliessen. (Danke @Xiaoyiyi23)
  * Neu: Getrennte macOS-Pakete für arm64 (Apple Silicon) und x86_64 (Intel).
  * Neu: Sicherheits-Header in den Antworten des Webservers.
* API:
  * Behoben: Die Parameter before und after des API-Befehls get_home_stats funktionierten nicht.
  * Behoben: Der Parameter sub_media_type des API-Befehls get_export_fields funktionierte nicht.
  * Behoben: Der Parameter limit des API-Befehls search wurde nicht angewendet.
  * Behoben: Der API-Befehl delete_hosted_images gibt die richtige Fehlerantwort zurück.
  * Behoben: Der API-Befehl notify überschrieb den angegebenen Parameter notify_action.
  * Behoben: Optionale Parameter subject/body/message des API-Befehls set_newsletter_config.
  * Behoben: Die API-Befehle download_plex_log und get_plex_log geben die richtige Fehlerantwort zurück.
  * Behoben: Der API-Befehl logout_user_session gibt ohne row_id die richtige Fehlerantwort zurück.
  * Behoben: Der API-Befehl get_logs sucht, filtert und sortiert vor dem Zuschneiden.
  * Behoben: Die Antwort des API-Befehls get_recently_added enthielt eine leere section_id.
  * Behoben: Der API-Befehl get_metadata gibt bei ungültigem rating_key einen Fehler zurück.
  * Behoben: Der API-Befehl sql legte bei jeder Abfrage eine Datenbanksicherung an.
  * Behoben: API-Befehle gaben nicht die richtige Fehlerantwort 400 zurück.
  * Neu: Infos zu Dolby Atmos in den API-Befehlen get_activity und get_metadata.
  * Neu: Statt des Parameters für den API-Schlüssel kann der Header X-Api-Key verwendet werden.
  * Neu: API-Antwort auf CORS-Preflight-Anfragen (OPTIONS).
  * Geändert: Die API-Befehle edit_user und edit_library ändern nur noch die angegebenen Parameter.
  * Geändert: Die API-Befehle set_notifier_config und set_newsletter_config ändern nur noch die angegebenen Parameter.
  * Geändert: Doppelt verschachtelte Daten in der Antwort von get_plex_logs.
  * Entfernt: Veralteter API-Befehl delete_synced_item.
