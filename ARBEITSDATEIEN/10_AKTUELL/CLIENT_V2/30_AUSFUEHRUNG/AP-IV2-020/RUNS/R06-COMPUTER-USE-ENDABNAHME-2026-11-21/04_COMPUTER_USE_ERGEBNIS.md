# R06-Nachlauf · praktische Windows-Endabnahme

**NO-GO / BLOCKIERT** · 2026-11-22, 00:14–01:09 MEZ · CSL-DESKTOP-PC, Windows 11 Pro Build 26300

- Produktcommit `9f9fdf2b19f99a6d4f255d76b6cfa9ef3de493b2` ist direkter Parent des R06-Dokumentationscommits `17fce388e747daf37b97e96ed1fcf6421338873d`. Die Desktop-EXE hat 77.414.876 Byte und SHA-256 `28cea377ee59b2342fd9f5fd2d10a93cc6e2a8a1df950a9a1efa3af216ab65f8`. PR #18 war per `gh pr view` offen, Draft, Base `feat/client-v2`, Head `17fce38`.
- Der Launcher setzt `VOICESTT_CLIENT_HOME` und `VOICESTT_CLIENT_CONFIG` und startet die EXE mit `--config`. Vor dem ersten Lauf gab es keinen aktiven Altclient. Die Ausgangskopie der V2-Konfiguration hat SHA-256 `c38d55659a4cedcbf635e208e82c1088de87e5d1f75cbee02de0f0c6fce1fe04`.
- Testziel ist `wss://final.v2.voice-stt-server.marcosudau.com/ws/v2`. Der Health-Check meldete HTTP 200, Ready und STT Ready. Ein gesonderter V2-Produktquellen-Handshake am 22.11.2026 bestätigte Protokoll 2 und Servercommit `e95858e3c010a7e9324b49bb44fee349abe7128a`. Der Handshake enthielt kein Mikrofon-PCM.
- Windows 11 Pro Build 26300, normaler Desktop in Session 1. ReSpeaker XVF3800 über Windows AudioEndpoint und nativen 16-kHz-Stream verfügbar. PortAudio-Systemstandard Index 1, Wiedergabeziel Realtek-Lautsprecher Index 3. Ein physischer USB-Wechsel oder sichtbarer LED-Ring ist über diese Oberfläche nicht beobachtbar.
- Computer Use betätigte native Hotkeys in Notepad und einem lokalen Qt-Testeditor. Den verifizierten CMD-Launcher startete die Shell. Den ersten V2-Prozess stoppte der Benutzer über den Tray, was die Prozess- und Eventspur bestätigt.
- Nach der Cursorabweichung startete derselbe Launcher erneut. `LOCALAPPDATA` wurde ausschließlich in dessen Prozessbaum auf einen neuen Nachweis-Unterordner umgelenkt. Mit dieser Maßnahme wurde der Ereignis-Cursor dort neu erzeugt. Die V2-YAML wurde für den Neustart nicht geändert.
- Nach der Übergabe des Tray-Dialogs wurden alle acht Register am laufenden Desktopkandidaten geprüft. Session-Apply und Audio-/Hotkey-Änderungen betrafen nur diese Testsession und das isolierte Profil. Serverrevision 0 blieb in den betroffenen Ansichten gleich.
- Nach regulärem Tray-Ausstieg um 01:06:04 MEZ wurde die ursprüngliche Test-YAML aus dem Backup bytegenau wiederhergestellt. Die korrekte /ws/v2-URL und null V2-Prozesse wurden geprüft. Der gemeinsame Cursor war nach der Prozessisolierung unverändert. Der Zustand vor dem Erstlauf ist für diese einzelne Datei mangels Backup nicht wiederherstellbar.

## Testablauf

| Zeit MEZ | Bedienung und Befund | Nachweis |
|---|---|---|
| 00:14:32–00:14:48 | Bestandsaufnahme, Hash, Altclientabgleich, Profilkopie, Checkliste aus Anhang A, Health und erster Launcherstart. | E01, E02 |
| 00:14:50–00:15:41 | Core, Audio und LEFX starten. Desktop erreicht Ready. Zweiter Onefile-Start endet kontrolliert laut `already running`. | E04 |
| 00:15–00:17 | Leeren Notepad-Tab erstellt, Eingabefokus gesetzt. Primären Hotkey gedrückt. Aktivierung einmal registriert. | E03, E04 |
| 00:17:36–00:18:41 | Schreibzugriff auf gemeinsamen Event-Cursor erkannt. Benutzer beendete den Testclient um 00:18:20 regulär. Umgebungsursache eingegrenzt. | B01, E05 |
| 00:19:15–00:19:59 | Derselbe Launcher mit separatem Prozess-LOCALAPPDATA. Session nach Neustart ready. Eigene V2-Wire-Probe bestätigt Server-SHA. | E02, E04, E05, E09 |
| 00:21:50–00:22:50 | Native Aktivierung im isolierten Qt-Feld. Realtime vor SAPI, während der Interims leeres Feld. Server-Final und ein nativer Paste, Text entspricht nicht dem Testsatz. Keine Übernahme des unbekannten Texts in Nachweise. | B02, E06 |
| 00:23:53–00:25:18 | Wiederholte Prüfung des Eingangswegs per Pegelvergleich mit und ohne SAPI ohne aktive Diktat-Activation. Erheblicher Eingangspegel schon ohne Testwiedergabe, akustische Zuordnung ungelöst. | E07 |
| 00:26:11–00:28:21 | Strukturprüfung lokaler Diagnose und zweite Ressourcenmessung. Keine Secret-/Transkriptfeldtreffer in der Stichprobe. | E08, E09 |
| 00:30–00:33 | Read-only-Dateihashvergleich nach Prozessisolation. Separate V2-Settings-Probe ermittelt 19 Schemafelder, 25 Wake-IDs und nicht verifizierten Adminzustand. Ungültiger Pfad in netzloser Transportprobe blockiert. | E05, E10 |
| 00:34–00:36 | Taskleisten-Ausschnitt zeigt den Overflow-Zugang. Im Computer-Use-Fensterinventar bleibt der Tray ohne Ziel. Separate Offline-Reproduktion des Cursorfehlers und 18 gezielte Cursor-/Coordinator-Tests bestanden. | E05, E11 |
| 00:41–00:43 | Windows-Einstellungen → System → Sound zeigt ReSpeaker als Standardaufnahmegerät. Realtek-Lautsprecher als Standardwiedergabe. Lautstärkemixer rein lesend geprüft. | E11 |
| 00:19:36–00:50:00 | 1823,93 Sekunden Laufzeitmessung. Ein Hotkey-Diktat mit Fremdton, kein korrekter Sollsatz. Keine beobachteten Reconnects, 36 Keepalives. Working Set 107,44 → 568,46 MiB, Private Bytes 466,04 → 478,28 MiB. CPU-Mittel 0,236 % der Rechnerkapazität. | E09 |
| 00:50–00:55 | Benutzer öffnet den V2-Hauptdialog aus dem Tray. Alle drei Register sichtbar. Admin-Guard aktiv. Zwei Reloads verwerfen Entwürfe. Sessionwert 5200 ms wirksam bestätigt, auf 5000 zurückgesetzt. Katalog gescrollt bis Hey Jarvis. | E12, B08 |
| 00:55–01:01 | Doppelbelegung technisch abgelehnt und unveränderter YAML-Hash, irreführender Migrationshinweis. Fünf lokale Register, expliziter ReSpeaker-Apply, lokaler Pegel, Logfilter und erneutes Öffnen. Audiowahl wieder Systemstandard. | E13, E14, B09 |
| 01:01–01:04 | Globale Hotkeys aus/an, Win32-Freiraum gemessen. Neue Primärbelegung F10 übernommen. Altbelegung im leeren Editor negativ getestet. Anschließend ursprüngliche native Belegung wiederhergestellt. | E14 |
| 01:05–01:06:54 | Schreibgeschützte Sessionfelder gesichtet. Benutzer beendet Client über Tray. Audio-, Text- und LED-Dienst gestoppt, null V2-Prozesse, Hotkeys frei. Profilkopie bytegenau zurückgespielt, externe Dateien und Diagnose erneut geprüft. | E12, E15 |

## Ergebnis über alle Prüfpunkte

136 Testfälle. Die drei Entscheidungsoptionen werden zusätzlich ausgewiesen und verändern die Testzählung nicht. Zeitangaben mit „Bewertet“ bezeichnen die Bewertung der Blockade, keinen ausgeführten Test. PASS-Angaben gelten für den beschriebenen Lauf und die tatsächlich beobachtete Wirkung.

| Status | Prüfpunkte |
|---|---:|
| PASS | 30 |
| FAIL | 7 |
| BLOCKIERT | 91 |
| NOT_RUN | 1 |
| N/A | 7 |

| ID | Status | Uhrzeit MEZ | Nachweis | Ergebnis / Testgrenze |
|---|---|---|---|---|
| V00-01 | PASS | 00:14:32 | E01 | Alle vier geforderten Paketbestandteile vorhanden. EXE 77.414.876 Byte, SHA-256 stimmt. |
| V00-02 | PASS | 00:14:48 | E01, E02 | Profil exakt /ws/v2 und Health auf derselben Final-Testdomain. HTTP 200, ready=true, sttReady=true. Separater aktueller V2-Handshake liefert erwarteten Server-Commit. |
| V00-03 | N/A | 00:14:32 | E01 | Prozessinventar vor Start ohne Altclient und ohne laufendes Altclient-Diktat. Altclient-Dateien blieben während der Vorbereitung am Ort. |
| V00-04 | N/A | 00:14:32 | E01 | Kein aktiver Altclient zum regulären Beenden. Altclient wurde für diese Prüfung nicht gestartet. |
| V00-05 | PASS | 00:15–00:17 | E03 | Computer Use öffnete mit Strg+T einen leeren Notepad-Tab und fokussierte sein Textfeld. Zweites, eigenständiges Qt-Textfeld anschließend bereitgestellt. |
| V00-06 | PASS | 00:14:32–00:17:05 | E01, E04 | Vor Start Profilkopie und SHA-256 gesichert. Windows und PortAudio identifizierten bei Systemstandard den ReSpeaker-Eingang; Laufzeitspur meldet 16 kHz und 40-ms-Frames. |
| V01-01 | NOT_RUN | 00:14:47 | E04 | Verifizierter Launcher lief über die Shell, da der Computer-Use-Skill den indirekten Start von CMD-Skripten in Explorer untersagt. Onefile-Prozess und betriebsbereite Qt-/Core-Initialisierung beobachtet. Der geforderte Doppelklick blieb offen. |
| V01-02 | BLOCKIERT | 00:15–00:24 | B03, E04 | Reguläres Tray-Beenden durch Anwender bestätigt. Computer Use listet die Shell-Taskleiste nicht als Ziel. Symbol, Status, Tooltip und Menü konnten nicht vollständig direkt abgenommen werden. |
| V01-03 | PASS | 00:14:51 / 00:19:19 | E02, E04 | Die Desktop-EXE erreichte in zwei Läufen V2-Transportzustand ready. Domain aus geprüftem Profil, Soll-Server-Commit aus gesonderter zeitnaher V2-Probe. |
| V01-04 | PASS | 00:19:19–00:19:59 | E01, E02, E04 | Desktopspur zeigt V2-Verbindungsaufbau, Bootstrap und Ready. Exakter /ws/v2-Endpunkt aus Launcher-Profil und der aktuellen Wire-Probe. V2-Runtime akzeptiert für die Diktatverbindung ausschließlich /ws/v2. |
| V01-05 | PASS | 00:50–01:01 | E12 | Der Benutzer öffnete das V2-Hauptfenster aus dem Tray. Computer Use öffnete den lokalen Einstellungsdialog, schloss ihn und öffnete ihn erneut. Das wiedergeöffnete Fenster hatte einen neuen Handle und der Hauptdialog blieb bedienbar. |
| V01-06 | PASS | 00:50–00:52 | E12 | Die Register Lokale Trigger & Bedienung, Session und Serververwaltung wurden in der laufenden EXE aufgerufen und inhaltlich geprüft. |
| V01-07 | PASS | 00:56–00:59 | E13 | Alle fünf lokalen Register geöffnet. Audio/Geräte, Verlauf, Clipboard in Allgemein, Darstellung/Feedback und Logging/Diagnose waren zugänglich. |
| V01-08 | BLOCKIERT | Bewertet 01:09 | E12, E13 | Drei V2- und fünf lokale Register sichtbar bedienbar, Listen und Tabellen vertikal gescrollt. Einige lange Tabellenwerte sind im Standardviewport abgeschnitten und horizontal scrollbar. Vollständige Tooltip- und Skalierungsmatrix fehlt. |
| V01-09 | BLOCKIERT | Bewertet 01:09 | B03 | Kein targetierbares Overlay und keine belegte sichtbare Positions-/Sichtbarkeitsänderung. |
| V01-10 | PASS | 00:15:40–00:15:41 | E04 | Zweiter Start mit demselben Launcher. Runtime protokolliert „RealtimeSTT is already running; second instance exits“. Bestehendes Onefile-PID-Paar blieb erhalten. Ablehnung erfolgt vor zweitem Qt-/Hotkey-Start. |
| V02-01 | PASS | 00:42 / 00:56:35 | E11, E13 | Windows zeigte den XVF3800 als Standardeingang. Die Client-Auswahlliste zeigte den vollständigen Gerätenamen. Windows bestätigte VID 2886 / PID 001A. |
| V02-02 | PASS | 00:56:35–00:56:50 | E13, E04 | Vollständigen ReSpeaker-Eintrag in der lokalen GUI ausgewählt und mit Apply übernommen. Laufzeitgerät PortAudio 9. Nach der Prüfung wieder Systemstandard und ursprüngliches YAML. |
| V02-03 | PASS | 00:56:50–00:57:25 | E13, E04 | Der Stream startete nach Apply mit dem explizit ausgewählten ReSpeaker und 16 kHz neu. Die lokale Drei-Sekunden-Prüfung meldete RMS 77,3 und Peak 1,19 %. Keine Audio-Dauerstörung. |
| V02-04 | BLOCKIERT | 00:21–00:24 | B02, E07 | ReSpeaker-Stream und messbarer Eingangspegel bestätigt. Menschlicher Testsatz ist nicht zuordenbar. Unbekannter Sprachinhalt im ersten akustischen Lauf ist kein gültiger Testinput. |
| V02-05 | BLOCKIERT | Bewertet 01:09 | B02 | Kein der Sollsprache zuordenbares Diktatpaar mit kurzen Pausen und mehreren Sätzen. |
| V02-06 | BLOCKIERT | Bewertet 01:09 | B03, B04 | Tray-Mute und physischer Mute-Schalter konnten nicht bedient bzw. beobachtet werden. |
| V02-07 | BLOCKIERT | Bewertet 01:09 | B04 | Keine Möglichkeit zum physischen USB-Abziehen und Wiedereinstecken. |
| V02-08 | BLOCKIERT | Bewertet 01:09 | B04 | Kein vorangegangener physischer Geräteentzug mit dokumentierter Rückkehr. |
| V02-09 | BLOCKIERT | Bewertet 01:09 | B03 | Auswahl eines ungültigen Eingangs und Rückstellung erfordern den lokalen Gerätedialog. |
| V03-01 | BLOCKIERT | Bewertet 01:09 | B03, E04 | Manuelle Aktivierung in der Ausgangskonfiguration und in der Laufzeit belegt. GUI-Übernahme mit Reconnect blieb offen. |
| V03-02 | PASS | 00:17:05 | E03, E04 | Strg+Umschalt+Leertaste per Computer Use im leeren Notepad-Tab. Genau ein Hotkey-Ereignis und eine eindeutige manuelle Activation mit Aufnahmebeginn. |
| V03-03 | BLOCKIERT | Bewertet 01:09 | B02 | Serveraufnahme lief während der Testwiedergabe. Unkontrolliertes Eingangssignal verhindert die Zuordnung zum gesprochenen Sollsatz. |
| V03-04 | BLOCKIERT | Bewertet 01:09 | B02, E06 | Realtime-Ereignisse und bis zum Final leerer Editor beobachtet. Sichtbare Realtime-Vorschau des Sollsatzes bleibt offen. |
| V03-05 | BLOCKIERT | Bewertet 01:09 | B03, E06 | Server schloss die Aktivierung per Timeout. Der Abschluss durch eine konfigurierte Bedienaktion wurde nicht wirksam nachgewiesen. |
| V03-06 | FAIL | 00:21:50–00:22:49 | B02, E06 | V2-Final mit 450 Zeichen und tatsächliche Qt-Einfügung. Der Text entsprach nicht dem definierten SAPI-Test. Realtime-Erkennung setzte 5,4 s vor SAPI ein. Die Urheberschaft/Quelle des Fremdtons ist offen. |
| V03-07 | PASS | 00:22:26–00:22:50 | E06 | Genau ein nativer `command_sent`-Job (vier Keyevents) im fokussierten isolierten Qt-Testeditor und ein sichtbarer Textblock. Erkennung des Sollsatzes separat fehlgeschlagen. |
| V03-08 | BLOCKIERT | Bewertet 01:09 | B02 | Drei kontrolliert unterscheidbare und korrekt erkannte Finals fehlen. |
| V03-09 | BLOCKIERT | Bewertet 01:09 | B02 | Keine kontrollierbare akustische Testumgebung für zwei Minuten Sprachmaterial. |
| V03-10 | BLOCKIERT | Bewertet 01:09 | B03 | Refresh muss im passenden Aktivierungszustand beobachtet und von einer neuen Aktivierung unterschieden werden. |
| V03-11 | BLOCKIERT | Bewertet 01:09 | B03 | Im Ausgangsprofil ist Cancel nicht belegt. Belegung oder Bedienung über die GUI blieb offen. |
| V03-12 | BLOCKIERT | Bewertet 01:09 | B03 | Im Ausgangsprofil hat der Finish-Slot keinen Hotkey. Keine tatsächlich ausgeführte Finish-Aktion. |
| V03-13 | BLOCKIERT | Bewertet 01:09 | B03 | Manuellen Trigger deaktivieren und Sperre beobachten erfordert funktionierende GUI-Übernahme. |
| V04-01 | PASS | 00:55 | E12, E10 | Sessionliste geladen, gescrollt und mehrere auswählbare Namen einschließlich Hey Jarvis gesehen. Die aktuelle lesende V2-Probe bestätigte 25 Einträge bei Katalogrevision 2. |
| V04-02 | BLOCKIERT | Bewertet 01:09 | B03 | Keine bestätigte GUI-Übernahme von manual+wake und hey_jarvis in dieser Sitzung. |
| V04-03 | BLOCKIERT | Bewertet 01:09 | B03 | GUI-Anzeige Requested/Effective und Readback nach Änderung fehlen. |
| V04-04 | BLOCKIERT | Bewertet 01:09 | B02, B04 | Mehrere echte Wake-Testsätze einer bekannten menschlichen Stimme sind nicht verfügbar. |
| V04-05 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Ein vollständiger kontrollierter Wake-Pfad mit korrekt zugeordnetem Final fehlt. |
| V04-06 | BLOCKIERT | Bewertet 01:09 | B03 | Bisheriger Hotkey-Nachweis gilt für Manual-only. Kombinierter Lauf fehlt. |
| V04-07 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Kein erfolgreicher Wake-only-Lauf mit positivem Wake- und negativem Manual-Test. |
| V04-08 | BLOCKIERT | Bewertet 01:09 | B02 | Ausgangsprofil ist Manual-only. Kontrollierter gesprochener Wake-Negativversuch blieb unbelegt. |
| V04-09 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Konfigurierter Wake-Betrieb, Pause und akustischer Negativversuch fehlen. |
| V04-10 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Aufheben der Laufzeitpause und positive akustische Wiedererkennung fehlen. |
| V04-11 | BLOCKIERT | Bewertet 01:09 | B03 | Ungültige Wake-ID wurde im Produktdialog noch nicht getestet. |
| V04-12 | BLOCKIERT | Bewertet 01:09 | B02, B04 | Keine qualifizierte Wake-Beobachtung in Stille und definierten Hintergrundgesprächen. |
| V05-01 | PASS | 00:17:05 | E03, E04 | Globaler Hotkey registrierte im fremden Notepad-Fenster eine native Betätigung, während die Tray-App im Hintergrund lief. |
| V05-02 | BLOCKIERT | Bewertet 01:09 | E14, B02 | Freier F10-Hotkey per GUI gespeichert und Win32-Registrierung nachgewiesen. Aktive Diktatauslösung über die neue Belegung blieb wegen der unkontrollierten Audioquelle offen. |
| V05-03 | PASS | 01:03:05–01:03:42 | E14 | Nach Apply der Ersatzbelegung war der Alt-Hotkey Win32-seitig frei. Strg+Umschalt+Leertaste im fokussierten leeren Editor erzeugte weder ein Hotkey-Ereignis noch eine Activation. |
| V05-04 | BLOCKIERT | Bewertet 01:09 | B03 | Sekundärslot im Ausgangsprofil leer. GUI-Konfiguration und Aktion blieben offen. |
| V05-05 | BLOCKIERT | Bewertet 01:09 | B03 | Optionsmatrix und praktische Wirkung von Finish und Cancel in der GUI offen. |
| V05-06 | BLOCKIERT | Bewertet 01:09 | B03 | Wake-Pause-Hotkey im Ausgangsprofil leer. Belegung und Umschaltung blieben offen. |
| V05-07 | BLOCKIERT | Bewertet 01:09 | B03 | Overlay-Hotkey im Ausgangsprofil leer. Keine beobachtete Umschaltung. |
| V05-08 | BLOCKIERT | Bewertet 01:09 | B02 | Ein bekanntes erfolgreiches Testfinal zur Wiederholung fehlt. Unbekannter Sprachinhalt bleibt unbenutzt. |
| V05-09 | FAIL | 00:55:30 | E14, B09 | Duplikat wurde technisch abgewiesen. Die Meldung verweist auf Reparatur eines migrierten Profils und benennt weder den doppelten Hotkey noch die betroffenen Felder. |
| V05-10 | BLOCKIERT | Bewertet 01:09 | E14, B02 | Unveränderter YAML-Hash, nach erneutem Einlesen Primärhotkey und ursprünglicher leerer Sekundärslot, vorherige native Bindungen weiter belegt. Wiederholtes Auslösen eines Diktats bzw. Reinsert des unbekannten Finals bleibt offen. |
| V05-11 | PASS | 01:01–01:04:43 | E14 | Nach GUI-Apply aus waren Primary und Reinsert Win32-seitig registrierbar. Nach GUI-Apply an waren F10 und Reinsert besetzt. Nach Rücknahme war der ursprüngliche Primary wieder besetzt und F10 frei. |
| V06-01 | BLOCKIERT | Bewertet 01:09 | B02, E03 | Windows-Editor diente als bestätigtes Aktivierungsziel. Kein kontrolliertes Final mit Paste in Notepad nachgewiesen. |
| V06-02 | FAIL | 00:22:26–00:22:50 | B02, E06 | Einmaliges Einfügen im zweiten lokalen Testeditor bestätigt. Sichtbarer Text entspricht nicht dem definierten Testinput, daher kein End-to-End-PASS für korrekte Ausgabe. |
| V06-03 | PASS | 00:21:52–00:22:26 | E06 | Im akustischen Versuch liefen mehrere Realtime-Ergebnisse. Das Editorfeld blieb bis zum Final leer; ein dokumentierter Paste-Job erst beim Final. |
| V06-04 | BLOCKIERT | Bewertet 01:09 | E06, B02 | Ein Final mit genau einem Paste belegt. Folgeaktivierungen mit kontrollierten Finals fehlen. |
| V06-05 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Der erste akustische Lauf nutzt den Profilstandard restore_previous=false. Ein Test mit vorbereitetem bekanntem Clipboard-Inhalt fehlt. |
| V06-06 | BLOCKIERT | Bewertet 01:09 | B03 | Einfügeverzögerung wurde nicht über die GUI verändert und auf Wirkung geprüft. |
| V06-07 | BLOCKIERT | Bewertet 01:09 | B02 | Kein qualifiziertes, unbedenkliches letztes Final für einen absichtlichen Reinsert. |
| V06-08 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Reinsert und Memory-/DB-Verlauf vor und nach einem kontrollierten Testfinal fehlen. |
| V06-09 | BLOCKIERT | Bewertet 01:09 | B02, E13 | Historienregister zeigte den einen kurzen Eintrag im Speicher. Eine zeitliche Mehrfachfolge mit eindeutig kontrolliertem Sprachinput fehlt. Der SQLite-Nullstand erklärt sich aus der Standardpolicy für kurze Finals. |
| V06-10 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Kein eindeutig qualifizierter Historieneintrag für gezielte Wiedereinfügung. |
| V06-11 | BLOCKIERT | Bewertet 01:09 | B02, B05 | Kein ausschließlich zu diesem Test erzeugter, eindeutig unbedenklicher Eintrag. UI-Datenlöschung braucht zudem eine Bestätigung unmittelbar vor der Aktion. |
| V06-12 | BLOCKIERT | Bewertet 01:09 | B02, B03 | GUI-Umschaltung der Historie und kontrollierter Final-Paste nach Umschaltung fehlen. |
| V06-13 | BLOCKIERT | Bewertet 01:09 | B02, B05 | Keine vorher freigegebenen Testdaten im Verlauf. UI-Datenlöschung braucht Bestätigung unmittelbar vor der Aktion. |
| V07-01 | PASS | 00:14:50–00:14:51 | E04 | Runtime erkennt ReSpeaker-USB-Controller. LEFX-Dienst startet mit 12 LEDs, 30 FPS und 36 Effekten. `output available (respeaker)` ohne dauerhaften Initialisierungsfehler. Keine visuelle Hardwarewertung. |
| V07-02 | BLOCKIERT | Bewertet 01:09 | B04 | Bereitschaft wurde technisch gemeldet. Physisches LED-Muster ist nicht einsehbar. |
| V07-03 | BLOCKIERT | Bewertet 01:09 | B04 | Ein Aufnahmezustand ist technisch belegt. Physisches LED-Muster fehlt. |
| V07-04 | BLOCKIERT | Bewertet 01:09 | B04 | Keine visuelle Beobachtung am physischen LED-Ring beim Eingabeschluss. |
| V07-05 | BLOCKIERT | Bewertet 01:09 | B04 | Kein physischer Vergleich der LED-Muster für Final, Cancel und Fehler. |
| V07-06 | BLOCKIERT | Bewertet 01:09 | B03, B04 | Keine ausgelöste Laufzeitpause mit sichtbarer, zuordenbarer Rückmeldung. |
| V07-07 | BLOCKIERT | Bewertet 01:09 | B04 | Helligkeit/Farbe können ohne physische Sicht auf den Ring nicht wirksam abgenommen werden. |
| V07-08 | BLOCKIERT | Bewertet 01:09 | B04, E13 | Sounds waren in der GUI aktiv und fünf WAV-Zuordnungen sichtbar. Die physische Hörbeobachtung für die geforderten Zustände fehlt. |
| V07-09 | BLOCKIERT | Bewertet 01:09 | B04 | Weder wahrnehmbare Lautstärkewirkung noch Auswirkung auf das Aufnahmesignal belegt. |
| V07-10 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Kein deaktivierter LED-Controller in Kombination mit qualifiziertem Mikrofon-Final. |
| V07-11 | BLOCKIERT | Bewertet 01:09 | B03 | Aufnahme-, Warte-, Abschluss-, Fehler- und Pausenanzeigen wurden nicht als vollständige visuelle Folge beobachtet. |
| V08-01 | PASS | 01:01–01:04 | E12, E14 | Lokale Hotkey-Werte über die GUI geändert und erfolgreich übernommen. Dauerhafte Triggerwahl und aktuelle Wirksamkeit wurden getrennt gezeigt. Manueller Trigger blieb wirksam, Wake blieb aus. |
| V08-02 | PASS | 00:51–00:52 | E12 | Sessionansicht zeigte Angefordert, Wirksam, Serverstandard, Schema-Startwert und Wirksam ab für die Final-Instanz. Session-, Server- und Katalogrevision waren sichtbar. |
| V08-03 | PASS | 00:54 | E12 | Sessionparameter Warten auf Eingabeschluss auf 5200 ms übernommen. Revision 1 und Requested/Effective 5200 bei Serverstandard 5000 und Serverrevision 0. Anschließend Rücknahme auf 5000 mit Sessionrevision 2. |
| V08-04 | PASS | 00:51 / 01:05 | E12 | Wake-Rauschunterdrückung und Sprachschwelle waren in Session ausgegraut, mit Hinweis auf Admin-Serverdefaults. UI unterschied Policy Nächste Verbindung und Änderungsrecht. |
| V08-05 | FAIL | 00:52–00:54 | E12, B08 | Explizites Reload verwarf ungespeicherte Sessionentwürfe 5200 und 5300 ms zweimal still. Die Oberfläche zeigte danach wieder 5000 ms und nur Serverwerte geladen. |
| V08-06 | BLOCKIERT | Bewertet 01:09 | B03 | Kein GUI-Apply mit aktiver Testaufnahme und sichtbarer Optionsauswahl. |
| V08-07 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Kein GUI-Gerätewechsel mit anschließendem kontrolliertem Diktat. |
| V08-08 | BLOCKIERT | Bewertet 01:09 | B03 | Sichtbare Positions-, Transparenz- oder Sichtbarkeitsänderung fehlt. |
| V08-09 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Keine GUI-Änderung und Wirkungsmessung von Clipboard/Textinjektion. |
| V08-10 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Keine GUI-Änderung der Historieneinstellungen mit messbarer Wirkung. |
| V08-11 | BLOCKIERT | Bewertet 01:09 | B03, B04 | Keine geänderten Zuordnungen mit überprüfter physischer Rückmeldung. |
| V08-12 | PASS | 00:58–00:59 | E13 | Logs-und-Diagnose-Fenster über lokale GUI geöffnet. Suche nach Audio capture started reduzierte die Anzeige auf drei datierte Einträge, darunter den Geräte-Apply um 00:56:50 MEZ. |
| V08-13 | BLOCKIERT | Bewertet 01:09 | B03, E04 | Regulärer Ausstieg und Start mit identischem YAML belegt. Persistenzänderung und Rücksetzen von Laufzeitpausen fehlen. |
| V08-14 | FAIL | 00:55:30–00:55:45 | E14, B09 | Ungültige Doppelbelegung abgelehnt und YAML-Hash gleich. Die sichtbare Migrationsmeldung war für die eingegebene Doppelbelegung nicht konkret genug. |
| V08-15 | FAIL | 00:17:36–00:18:41 | B01, E05 | Erster Lauf schrieb trotz abgesetztem Profil den gemeinsamen Event-Cursor unter LOCALAPPDATA. Neue Bindung Final-Host /ws/logs, Protokoll 2. Altclient-Konfigurationsdatei zeigt keine Änderung im Prüfzeitraum. Der frühere Cursorinhalt liegt nicht als Backup vor. |
| V08-16 | PASS | 00:51 | E12 | Serververwaltung zeigte ohne Admin-Verifikation Gesperrt. Wunschfelder und Schaltfläche für Serverdefaults waren deaktiviert. Key-Feld leer, keine Eingabe und keine Mutation. |
| V08-17 | N/A | Bewertet 00:26 | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-18 | N/A | Bewertet 00:26 | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-19 | N/A | Bewertet 00:26 | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-20 | N/A | Bewertet 00:26 | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-21 | N/A | Bewertet 00:26 | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V09-01 | BLOCKIERT | Bewertet 01:09 | B06 | Keine verfügbare, auf den aktuellen Client begrenzte und reversible Unterbrechung im freigegebenen Umfang. |
| V09-02 | BLOCKIERT | Bewertet 01:09 | B06 | Andere Session nach Neustart belegt. Neue Session nach kontrolliertem Verbindungsabriss fehlt. |
| V09-03 | BLOCKIERT | Bewertet 01:09 | B02, B06 | Kein isolierter Abriss und kein nachfolgendes, korrekt zugeordnetes Final-Paste. |
| V09-04 | BLOCKIERT | Bewertet 01:09 | B02, B06 | Unterbrechung im laufenden Diktat ohne Auswirkung auf Rechnernetz und andere Anwendungen nicht verfügbar. |
| V09-05 | BLOCKIERT | Bewertet 01:09 | B06 | Bindungswechsel und Abweisung alter Aktivierungen nach isoliertem Abriss nicht in diesem Lauf beobachtet. |
| V09-06 | BLOCKIERT | Bewertet 01:09 | B03, B04 | Kein sicher ausgeführtes Mute-/Geräteereignis mit kontrolliertem Folgediktat. |
| V09-07 | BLOCKIERT | Bewertet 01:09 | B03, E10 | Transportprobe gibt für den ungültigen Pfad blocked bei Generation 0 ohne Verbindungsversuch aus. Positivpfad /ws/v2 gültig. GUI-/Neustartprobe und sichtbare Fehlermeldung bleiben offen. |
| V09-08 | PASS | 00:18–00:19 / 01:06:04–01:06:30 | E04, E15 | Benutzer führte beide Tray-Ausstiege aus. Prozessausstieg und Stop von Audio-, Text- und LED-Dienst bestätigt. Erstlauf wurde erfolgreich neu gestartet. Nach abschließendem Exit waren die drei geprüften Hotkeys freigegeben. |
| V09-09 | PASS | 00:26 / 01:06:54 | E08 | Abschluss-Stichprobe aus 53 Clientlogzeilen und 370 Beobachtungsdatensätzen. Null Treffer auf Secret-Muster, Secretfelder und Transkriptfelder. Aussage auf geprüften Lauf und Felder begrenzt. |
| V10-01 | BLOCKIERT | Bewertet 01:09 | E09, B02 | Reale Laufzeitmessung 30:24 Minuten. Sie umfasst eine kontaminierte Diktatprobe und überwiegend Bereitschaft. Die repräsentative Nutzungsfolge mit erfolgreichen Diktaten fehlt. |
| V10-02 | BLOCKIERT | Bewertet 01:09 | B02 | Keine zehn kontrolliert zuordenbaren Kurz-Diktate mit korrektem Final-Paste. |
| V10-03 | BLOCKIERT | Bewertet 01:09 | B02 | Kein aktiver Test mit zwei Minuten kontrollierter Sprache und erfolgreichem Final. |
| V10-04 | BLOCKIERT | Bewertet 01:09 | E03, E06, B02 | Beide Ziele wurden explizit fokussiert. In Notepad wurde kein qualifiziertes Final eingebracht; deshalb kein Fokuswechsel-PASS. |
| V10-05 | BLOCKIERT | Bewertet 01:09 | B02 | Für die repräsentative Stichprobe fehlen die kontrollierten Finals und akustische Wake-Szenarien. |
| V10-06 | BLOCKIERT | Bewertet 01:09 | E09 | Anwendungsprozess: 107,44 auf 568,46 MiB Working Set, 466,04 auf 478,28 MiB Private Bytes. Letzte Messphase praktisch konstant, CPU im Mittel 0,236 % der Rechnerkapazität. Pflicht-Lastmix und durchgehende UX-Beobachtung fehlen. |
| V10-07 | BLOCKIERT | Bewertet 01:09 | E09 | Messfenster ohne beobachteten Reconnect oder Geräteausfall, 36 Keepalives und genau eine kontrolliert ausgelöste Activation. Der geforderte repräsentative Lastmix fehlt. |
| V10-08 | BLOCKIERT | Bewertet 01:09 | E04, B03 | Kontrollierter Neustart nach dem Erstlauf belegt. Kein vollständiger Neustart nach repräsentativem Soak mit Verlauf-, Geräte- und Hotkey-Nachweis. |
| V10-09 | FAIL | 00:17:36–00:18:41 | B01, E05 | Gemeinsamer Cursor veränderte sich im ersten Startweg. Serverzugriffe beschränkten sich auf lesenden Health-/Katalogzugriff und normale V2-Testsessions. |
| F01 | BLOCKIERT | Bewertet 01:09 | E04, E12, B03 | EXE, Ready, Single-Instance und Trennung der Dialoge belegt. Tray-Tooltip und geforderter direkter Start-Doppelklick offen. |
| F02 | BLOCKIERT | Bewertet 01:09 | B02 | ReSpeaker-Audiostream und physischer Eingangspegel vorhanden. Eindeutig kontrollierte Sprachquelle fehlt. |
| F03 | BLOCKIERT | Bewertet 01:09 | B02, E06 | Nativer Hotkey und einmaliger Paste belegt. Korrektes Solltranskript sowie alle verpflichtenden Steueraktionen fehlen. |
| F04 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Akustische Wake-Matrix und Laufzeitpause offen. |
| F05 | BLOCKIERT | Bewertet 01:09 | B02, B03 | Nativer Hotkey belegt. Konfliktrollback und qualifizierter Reinsert fehlen. |
| F06 | BLOCKIERT | Bewertet 01:09 | B03, B04 | LEFX technisch verfügbar. Physische LED-/Soundbeobachtung und vollständige Overlayfolge fehlen. |
| F07 | BLOCKIERT | Bewertet 01:09 | B08, B09, E12, E13 | Session-Apply, Rücknahme, GUI-Admin-Guard, Gerätewechsel und Diagnose bestanden. Stiller Draft-Verlust und missverständliche Hotkey-Ablehnung bleiben offen. |
| F08 | BLOCKIERT | Bewertet 01:09 | B04, B06 | Isolierter Netzwerkabriss und physische Gerätere­covery ohne Doppel-Paste offen. |
| F09 | BLOCKIERT | Bewertet 01:09 | B02, E09 | Verpflichtende Aktivität im 30–60-Minuten-Lauf fehlt. |
| F10 | BLOCKIERT | Bewertet 01:09 | B05 | Adminprüfung ohne gültigen Schlüssel und getrennte Autorisierung offen. Eine Freigabe mit Adminfunktionen ist nicht Gegenstand dieser Empfehlung. |
| F11 | PASS | 01:07 | E05, E06, E12, E14 | Befunde und Testblockaden mit Schweregrad, Reproduktion und offenem Status im separaten Befundbericht dokumentiert. |
| F12 | BLOCKIERT | Bewertet 01:09 | B07 | Separate Produkt- und Redistributionsfreigabe fehlt. Frühere Buildtests erlauben keine Rechts- oder Releaseaussage. |
| GO für die nächste Testphase | NOT_RUN | 01:07 | B01–B09 | Option ungewählt, Pflichtkriterien sind offen bzw. fehlgeschlagen. |
| GO mit Auflagen | NOT_RUN | 01:07 | B01–B09 | Option ungewählt, offene Risiken betreffen Pflichtkriterien. |
| NO-GO / BLOCKIERT | PASS | 01:07 | B01–B09 | Diese Entscheidungsoption ist gewählt. PASS markiert die ausgeführte Entscheidung, nicht die Produktfreigabe. |

## Nachweisorte

- Desktop-Testpaket: `C:\Users\marco\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme`
- Lokale Nachweise: `C:\Users\marco\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Nachweise\computer-use-2026-11-22`
- [Bereinigter Belegindex in der R06-Akte](EVIDENCE/COMPUTER_USE/INDEX.md)
