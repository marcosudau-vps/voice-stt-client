# Voice-STT-Client V2 – Checkliste für die manuelle Endabnahme

**Zweck:** Alle noch offenen praktischen Bedien-, Hardware-, Stabilitäts- und Freigabepunkte nachvollziehbar abnehmen. Bereits bestandene automatisierte Tests müssen nicht wiederholt werden. **Ein leeres Kästchen bedeutet „noch nicht nachgewiesen“, nicht automatisch „Fehler“.**

| Prüfdaten | Eintrag |
|---|---|
| Testende Person | Codex mit Computer Use und ergänzenden Windows-Diagnosen. Benutzer führte reguläres Tray-Beenden aus. |
| Prüftag / Uhrzeit (Beginn–Ende) | 2026-11-22, 00:14–01:09 MEZ |
| Windows-PC / Betriebssystem | CSL-DESKTOP-PC · Windows 11 Pro · Build 26300 |
| Client-Branch / Commit | `feat/client-v2` / `9f9fdf2` |
| Server-Commit | `e95858e` |
| V2-Endpunkt | `wss://final.v2.voice-stt-server.marcosudau.com/ws/v2` |
| Testpaket | `Desktop\Voice-STT-Client-V2-Finalabnahme` |
| Protokoll der Auffälligkeiten / Screenshots (Pfad) | C:\Users\marco\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Nachweise\computer-use-2026-11-22 |
| Gesamtergebnis am Ende | **NO-GO / BLOCKIERT** |

**So wird diese Liste verwendet:** Ein Kästchen nur dann mit `[x]` abhaken, wenn der beschriebene Schritt **tatsächlich am PC erfolgreich durchgeführt** wurde. Bei Fehlern das Kästchen frei lassen und unter „Befunde“ eine ID, Uhrzeit und Beobachtung notieren. Falls ein Punkt bewusst nicht anwendbar ist, `N/A` mit Begründung ergänzen. Änderungen zunächst nur im **separaten V2-Testprofil** vornehmen. Keine Kennwörter, Tokens oder privaten Diktatinhalte in die Datei aufnehmen.

## 0. Vorbereitung und Schutz der bestehenden Installation

- [x] **V00-01** Prüfen, dass das neue Paket `Voice-STT-Client-V2-Finalabnahme` auf dem Desktop liegt und `START-V2-Finalabnahme.cmd`, `voice-stt-client.exe`, `Testprofil/config.yaml` und `Nachweise/` enthält.  
  **PASS** · 2026-11-22, 00:14:32 · E01. Alle vier geforderten Paketbestandteile vorhanden. EXE 77.414.876 Byte, SHA-256 stimmt.
- [x] **V00-02** Im Testprofil steht **`/ws/v2`**, nicht `/ws/transcribe`; Health-URL zeigt auf die Final-Testdomain.  
  **PASS** · 2026-11-22, 00:14:48 · E01, E02. Profil exakt /ws/v2 und Health auf derselben Final-Testdomain. HTTP 200, ready=true, sttReady=true. Separater aktueller V2-Handshake liefert erwarteten Server-Commit.
- [ ] **V00-03** Aktuelle Einstellungen und eventuell noch laufende Diktate im bisherigen Client sichern/beenden.  
  **N/A** · 2026-11-22, 00:14:32 · E01. Prozessinventar vor Start ohne Altclient und ohne laufendes Altclient-Diktat. Altclient-Dateien blieben während der Vorbereitung am Ort.
- [ ] **V00-04** Den bisherigen Voice-STT-Client **regulär über das Tray beenden**. Prüfen, dass er nicht mehr aktiv ist; keine laufende Aufnahme gewaltsam abbrechen.  
  **N/A** · 2026-11-22, 00:14:32 · E01. Kein aktiver Altclient zum regulären Beenden. Altclient wurde für diese Prüfung nicht gestartet.
- [x] **V00-05** Einen unkritischen Zieltexteditor öffnen (z. B. Windows-Editor) und für alle Diktat-/Einfügetests ausschließlich **Testtexte** verwenden.  
  **PASS** · 2026-11-22, 00:15–00:17 · E03. Computer Use öffnete mit Strg+T einen leeren Notepad-Tab und fokussierte sein Textfeld. Zweites, eigenständiges Qt-Textfeld anschließend bereitgestellt.
- [x] **V00-06** Startzeit, verwendetes Mikrofon und ursprüngliche Einstellungen des V2-Testprofils für eventuelle Rücksetzung dokumentieren.  
  **PASS** · 2026-11-22, 00:14:32–00:17:05 · E01, E04. Vor Start Profilkopie und SHA-256 gesichert. Windows und PortAudio identifizierten bei Systemstandard den ReSpeaker-Eingang; Laufzeitspur meldet 16 kHz und 40-ms-Frames.

## 1. Normaler Start, GUI, Verbindungsstatus

- [ ] **V01-01** `START-V2-Finalabnahme.cmd` per Doppelklick starten; die Anwendung startet ohne Fehlermeldung oder sofortigen Absturz.  
  **NOT_RUN** · 2026-11-22, 00:14:47 · E04. Verifizierter Launcher lief über die Shell, da der Computer-Use-Skill den indirekten Start von CMD-Skripten in Explorer untersagt. Onefile-Prozess und betriebsbereite Qt-/Core-Initialisierung beobachtet. Der geforderte Doppelklick blieb offen.
- [ ] **V01-02** Nach dem ersten Onefile-Entpacken erscheint das Tray-Symbol; Status, Tooltip und Menü sind zugänglich.  
  **BLOCKIERT** · 2026-11-22, 00:15–00:24 · B03, E04. Reguläres Tray-Beenden durch Anwender bestätigt. Computer Use listet die Shell-Taskleiste nicht als Ziel. Symbol, Status, Tooltip und Menü konnten nicht vollständig direkt abgenommen werden.
- [x] **V01-03** Die Verbindung zur Final-Testdomain wird aufgebaut und erreicht einen eindeutigen betriebsbereiten Zustand (`READY` oder entsprechende GUI-Anzeige).  
  **PASS** · 2026-11-22, 00:14:51 / 00:19:19 · E02, E04. Die Desktop-EXE erreichte in zwei Läufen V2-Transportzustand ready. Domain aus geprüftem Profil, Soll-Server-Commit aus gesonderter zeitnaher V2-Probe.
- [x] **V01-04** In den Logs/Diagnoseinformationen ist das **V2-Protokoll `/ws/v2`** ersichtlich; kein Rückfall auf `/ws/transcribe`.  
  **PASS** · 2026-11-22, 00:19:19–00:19:59 · E01, E02, E04. Desktopspur zeigt V2-Verbindungsaufbau, Bootstrap und Ready. Exakter /ws/v2-Endpunkt aus Launcher-Profil und der aktuellen Wire-Probe. V2-Runtime akzeptiert für die Diktatverbindung ausschließlich /ws/v2.
- [x] **V01-05** Einstellungsfenster öffnen, schließen und erneut öffnen; es bleibt bedienbar und blockiert die Anwendung nicht.  
  **PASS** · 2026-11-22, 00:50–01:01 · E12. Der Benutzer öffnete das V2-Hauptfenster aus dem Tray. Computer Use öffnete den lokalen Einstellungsdialog, schloss ihn und öffnete ihn erneut. Das wiedergeöffnete Fenster hatte einen neuen Handle und der Hauptdialog blieb bedienbar.
- [x] **V01-06** Die drei V2-Hauptregister **„Lokale Trigger & Bedienung“**, **„Session“** und **„Serververwaltung“** lassen sich aufrufen.  
  **PASS** · 2026-11-22, 00:50–00:52 · E12. Die Register Lokale Trigger & Bedienung, Session und Serververwaltung wurden in der laufenden EXE aufgerufen und inhaltlich geprüft.
- [x] **V01-07** Das zusätzliche Fenster für lokale Einstellungen hat **fünf Register**; Audio/Geräte, Verlauf, Clipboard, Darstellung/Feedback und Diagnose/Logging sind zugänglich.  
  **PASS** · 2026-11-22, 00:56–00:59 · E13. Alle fünf lokalen Register geöffnet. Audio/Geräte, Verlauf, Clipboard in Allgemein, Darstellung/Feedback und Logging/Diagnose waren zugänglich.
- [ ] **V01-08** Schaltflächen, Tabellen, Beschriftungen, Warnungen, Tooltips und Scrollbereiche sind bei der verwendeten Windows-Skalierung lesbar; nichts ist abgeschnitten.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E12, E13. Drei V2- und fünf lokale Register sichtbar bedienbar, Listen und Tabellen vertikal gescrollt. Einige lange Tabellenwerte sind im Standardviewport abgeschnitten und horizontal scrollbar. Vollständige Tooltip- und Skalierungsmatrix fehlt.
- [ ] **V01-09** Overlay erscheint und lässt sich positionieren bzw. anzeigen/ausblenden; die GUI bleibt auch beim Wechsel des aktiven Programms bedienbar.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Kein targetierbares Overlay und keine belegte sichtbare Positions-/Sichtbarkeitsänderung.
- [x] **V01-10** Einen zweiten Startversuch durchführen: Er wird kontrolliert als zweite Instanz verhindert bzw. an die bestehende Instanz delegiert; keine doppelt registrierten Hotkeys.  
  **PASS** · 2026-11-22, 00:15:40–00:15:41 · E04. Zweiter Start mit demselben Launcher. Runtime protokolliert „RealtimeSTT is already running; second instance exits“. Bestehendes Onefile-PID-Paar blieb erhalten. Ablehnung erfolgt vor zweitem Qt-/Hotkey-Start.

## 2. ReSpeaker / echtes Mikrofon / Audio

- [x] **V02-01** Der **reSpeaker XVF3800** wird in Windows und in der Audio-Geräteauswahl des Clients angezeigt.  
  **PASS** · 2026-11-22, 00:42 / 00:56:35 · E11, E13. Windows zeigte den XVF3800 als Standardeingang. Die Client-Auswahlliste zeigte den vollständigen Gerätenamen. Windows bestätigte VID 2886 / PID 001A.
- [x] **V02-02** Den gewünschten reSpeaker-Eingang im lokalen Einstellungsfenster auswählen und übernehmen.  
  **PASS** · 2026-11-22, 00:56:35–00:56:50 · E13, E04. Vollständigen ReSpeaker-Eintrag in der lokalen GUI ausgewählt und mit Apply übernommen. Laufzeitgerät PortAudio 9. Nach der Prüfung wieder Systemstandard und ursprüngliches YAML.
- [x] **V02-03** Nach Anwenden der Geräteauswahl zeigt der Client das Mikrofon als verfügbar an; keine dauerhafte Audiofehleranzeige.  
  **PASS** · 2026-11-22, 00:56:50–00:57:25 · E13, E04. Der Stream startete nach Apply mit dem explizit ausgewählten ReSpeaker und 16 kHz neu. Die lokale Drei-Sekunden-Prüfung meldete RMS 77,3 und Peak 1,19 %. Keine Audio-Dauerstörung.
- [ ] **V02-04** Mit normaler Stimme in üblicher Entfernung sprechen: Der Client nimmt reales Mikrofonaudio auf, ohne dass man eine synthetische WAV-Datei einspeisen muss.  
  **BLOCKIERT** · 2026-11-22, 00:21–00:24 · B02, E07. ReSpeaker-Stream und messbarer Eingangspegel bestätigt. Menschlicher Testsatz ist nicht zuordenbar. Unbekannter Sprachinhalt im ersten akustischen Lauf ist kein gültiger Testinput.
- [ ] **V02-05** Ein Diktat mit kurzen Sprechpausen und ein weiteres mit mehreren Sätzen testen; keine unerwarteten Aufnahmeabbrüche.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Kein der Sollsprache zuordenbares Diktatpaar mit kurzen Pausen und mehreren Sätzen.
- [ ] **V02-06** Bei ausgewähltem Gerät die Stummschaltung aktivieren und lösen; Clientzustand und Audioverfügbarkeit aktualisieren sich plausibel.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, B04. Tray-Mute und physischer Mute-Schalter konnten nicht bedient bzw. beobachtet werden.
- [ ] **V02-07** Nur wenn betrieblich unkritisch: ReSpeaker **im Ruhezustand** kurz abziehen und wieder anschließen; Geräteverlust wird angezeigt und Wiederverbindung funktioniert.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Keine Möglichkeit zum physischen USB-Abziehen und Wiedereinstecken.
- [ ] **V02-08** Nach der Geräte-Wiederherstellung erneut erfolgreich diktieren; kein vollständiger Neustart des PCs erforderlich.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Kein vorangegangener physischer Geräteentzug mit dokumentierter Rückkehr.
- [ ] **V02-09** Ein ungeeignetes/nicht verfügbares Gerät auswählen (sofern in der UI möglich): nachvollziehbare Fehlermeldung, kein unkontrollierter Crash; danach auf ReSpeaker zurückstellen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Auswahl eines ungültigen Eingangs und Rückstellung erfordern den lokalen Gerätedialog.

## 3. Manuelles Diktat / V2-Steuerbefehle / Ergebnisse

- [ ] **V03-01** Im Profil **manuellen Trigger aktivieren**; aktivierter Status wird nach Übernehmen und neuem Verbinden bestätigt.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, E04. Manuelle Aktivierung in der Ausgangskonfiguration und in der Laufzeit belegt. GUI-Übernahme mit Reconnect blieb offen.
- [x] **V03-02** Den primären Standardhotkey **`Strg+Umschalt+Leertaste`** mit fokussiertem Windows-Editor auslösen; Diktat beginnt genau einmal.  
  **PASS** · 2026-11-22, 00:17:05 · E03, E04. Strg+Umschalt+Leertaste per Computer Use im leeren Notepad-Tab. Genau ein Hotkey-Ereignis und eine eindeutige manuelle Activation mit Aufnahmebeginn.
- [ ] **V03-03** Einen deutlich gesprochenen Testsatz diktieren; die Aufnahme wird nicht vorzeitig geschlossen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Serveraufnahme lief während der Testwiedergabe. Unkontrolliertes Eingangssignal verhindert die Zuordnung zum gesprochenen Sollsatz.
- [ ] **V03-04** **Zwischentext/Realtime-Vorschau** erscheint bei tatsächlicher Streaming-Erkennung, falls für den erkannten Satz geliefert; **Zwischentext wird nicht automatisch eingefügt**.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, E06. Realtime-Ereignisse und bis zum Final leerer Editor beobachtet. Sichtbare Realtime-Vorschau des Sollsatzes bleibt offen.
- [ ] **V03-05** Diktat per konfigurierter Aktion abschließen; der Client erreicht wieder Idle bzw. einen fachlich abgeschlossenen Zustand.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, E06. Server schloss die Aktivierung per Timeout. Der Abschluss durch eine konfigurierte Bedienaktion wurde nicht wirksam nachgewiesen.
- [ ] **V03-06** **Finaltranskript erscheint** im vorgesehenen Ergebnis-/Verlaufsbereich und ist sprachlich nachvollziehbar korrekt.  
  **FAIL** · 2026-11-22, 00:21:50–00:22:49 · B02, E06. V2-Final mit 450 Zeichen und tatsächliche Qt-Einfügung. Der Text entsprach nicht dem definierten SAPI-Test. Realtime-Erkennung setzte 5,4 s vor SAPI ein. Die Urheberschaft/Quelle des Fremdtons ist offen.
- [x] **V03-07** Das Finaltranskript wird im aktiven Texteditor **genau einmal** eingefügt – keine doppelte Ausgabe.  
  **PASS** · 2026-11-22, 00:22:26–00:22:50 · E06. Genau ein nativer `command_sent`-Job (vier Keyevents) im fokussierten isolierten Qt-Testeditor und ein sichtbarer Textblock. Erkennung des Sollsatzes separat fehlgeschlagen.
- [ ] **V03-08** Drei aufeinanderfolgende kurze Diktate durchführen; alle drei Finals sind getrennt, vollständig und in der richtigen Reihenfolge.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Drei kontrolliert unterscheidbare und korrekt erkannte Finals fehlen.
- [ ] **V03-09** Ein längeres Diktat (mindestens **2 Minuten**) mit mehreren Sätzen und Sprechpausen durchführen; Abschluss ohne hängenbleibendes Final.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Keine kontrollierbare akustische Testumgebung für zwei Minuten Sprachmaterial.
- [ ] **V03-10** Während eines offenen Diktats die **Refresh**-Aktion testen (wenn so konfiguriert): erwartete Wirkung ohne Doppelaktivierung oder Textduplikate.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Refresh muss im passenden Aktivierungszustand beobachtet und von einer neuen Aktivierung unterschieden werden.
- [ ] **V03-11** Ein Diktat ausdrücklich **abbrechen (Cancel)**: kein ungewolltes Final-Paste oder Wiederaufleben derselben Aktivierung.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Im Ausgangsprofil ist Cancel nicht belegt. Belegung oder Bedienung über die GUI blieb offen.
- [ ] **V03-12** Separat **Finish** testen: saubere Finalisierung, keine Verwechslung mit Cancel.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Im Ausgangsprofil hat der Finish-Slot keinen Hotkey. Keine tatsächlich ausgeführte Finish-Aktion.
- [ ] **V03-13** Bei deaktivierter manueller Aktivierung führt der manuelle Startversuch nicht zu einer unerlaubten Aufnahme.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Manuellen Trigger deaktivieren und Sperre beobachten erfordert funktionierende GUI-Übernahme.

## 4. Wake Word und kombinierte Trigger

- [x] **V04-01** Im Register „Session“ den Wake-Word-Katalog laden und die Namen/Verfügbarkeiten prüfen (technischer Katalog umfasste 25 Einträge).  
  **PASS** · 2026-11-22, 00:55 · E12, E10. Sessionliste geladen, gescrollt und mehrere auswählbare Namen einschließlich Hey Jarvis gesehen. Die aktuelle lesende V2-Probe bestätigte 25 Einträge bei Katalogrevision 2.
- [ ] **V04-02** **Manuell + Wake Word** gemeinsam aktivieren, z. B. mit der verfügbaren ID `hey_jarvis` (nicht bloß den Anzeigenamen eintragen); Änderungen bestätigen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Keine bestätigte GUI-Übernahme von manual+wake und hey_jarvis in dieser Sitzung.
- [ ] **V04-03** Im Client wird erkennbar, welche Trigger **angefordert** und welche **tatsächlich wirksam** sind; nach ggf. nötigem Reconnect stimmen beide überein.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. GUI-Anzeige Requested/Effective und Readback nach Änderung fehlen.
- [ ] **V04-04** Wake Word mehrmals **mit echter Stimme** auslösen; eine berechtigte Aktivierung wird pro Aufruf nachvollziehbar gestartet.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B04. Mehrere echte Wake-Testsätze einer bekannten menschlichen Stimme sind nicht verfügbar.
- [ ] **V04-05** Ein per Wake Word gestartetes Diktat vollständig bis zum Finaltranskript und Einfügen abschließen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Ein vollständiger kontrollierter Wake-Pfad mit korrekt zugeordnetem Final fehlt.
- [ ] **V04-06** Trotz aktivem Wake Word funktioniert weiterhin der manuelle Hotkey; die beiden Trigger blockieren sich nicht ungewollt.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Bisheriger Hotkey-Nachweis gilt für Manual-only. Kombinierter Lauf fehlt.
- [ ] **V04-07** **Wake-only** testen (manuell aus, Wake an): Wake startet, manueller Start nicht.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Kein erfolgreicher Wake-only-Lauf mit positivem Wake- und negativem Manual-Test.
- [ ] **V04-08** **Nur manuell** testen (Wake aus): manueller Start funktioniert, gesprochenes Wake Word startet nichts.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Ausgangsprofil ist Manual-only. Kontrollierter gesprochener Wake-Negativversuch blieb unbelegt.
- [ ] **V04-09** Wake-Word-Laufzeitpause aktivieren: trotz weiter gespeicherter Wake-Konfiguration löst das Wort während der Pause nicht aus.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Konfigurierter Wake-Betrieb, Pause und akustischer Negativversuch fehlen.
- [ ] **V04-10** Wake-Pause aufheben: Wake Word wird wieder erkannt, ohne dass die komplette Konfiguration neu gespeichert werden muss.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Aufheben der Laufzeitpause und positive akustische Wiedererkennung fehlen.
- [ ] **V04-11** Eine nicht verfügbare oder unbekannte Wake-ID wird verständlich angezeigt und lässt sich nicht unbemerkt als funktionierende Auswahl übernehmen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Ungültige Wake-ID wurde im Produktdialog noch nicht getestet.
- [ ] **V04-12** In einer ruhigen Umgebung und mit normalen Hintergrundgesprächen prüfen, dass keine offensichtlich unerwünschten Wake-Aktivierungen auftreten; Beobachtungszeit notieren.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B04. Keine qualifizierte Wake-Beobachtung in Stille und definierten Hintergrundgesprächen.

## 5. Globale Hotkeys / Aktionen / Konflikte

- [x] **V05-01** Primärer Hotkey funktioniert auch, wenn **ein anderes Fenster** den Fokus hat.  
  **PASS** · 2026-11-22, 00:17:05 · E03, E04. Globaler Hotkey registrierte im fremden Notepad-Fenster eine native Betätigung, während die Tray-App im Hintergrund lief.
- [ ] **V05-02** Primären Hotkey in der V2-Oberfläche auf eine freie Kombination umstellen, speichern und die neue Belegung testen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E14, B02. Freier F10-Hotkey per GUI gespeichert und Win32-Registrierung nachgewiesen. Aktive Diktatauslösung über die neue Belegung blieb wegen der unkontrollierten Audioquelle offen.
- [x] **V05-03** Der **alte** primäre Hotkey löst nach dem Wechsel keine zusätzliche Aktivierung aus.  
  **PASS** · 2026-11-22, 01:03:05–01:03:42 · E14. Nach Apply der Ersatzbelegung war der Alt-Hotkey Win32-seitig frei. Strg+Umschalt+Leertaste im fokussierten leeren Editor erzeugte weder ein Hotkey-Ereignis noch eine Activation.
- [ ] **V05-04** Optionalen **sekundären Hotkey** hinterlegen und seine konfigurierte Aktion (z. B. Finish) testen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Sekundärslot im Ausgangsprofil leer. GUI-Konfiguration und Aktion blieben offen.
- [ ] **V05-05** Für Primary/Secondary jeweils die Optionen **Refresh, Finish, Cancel, Keine Aktion** nachvollziehen; mindestens Finish und Cancel in der Praxis testen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Optionsmatrix und praktische Wirkung von Finish und Cancel in der GUI offen.
- [ ] **V05-06** Falls aktiviert: eigener Wake-Pause-Hotkey schaltet die Laufzeitpause korrekt.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Wake-Pause-Hotkey im Ausgangsprofil leer. Belegung und Umschaltung blieben offen.
- [ ] **V05-07** Overlay-Umschalt-Hotkey blendet das Overlay sichtbar aus/ein, ohne ein Diktat auszulösen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Overlay-Hotkey im Ausgangsprofil leer. Keine beobachtete Umschaltung.
- [ ] **V05-08** Wiedereinfüge-Hotkey **`Strg+Alt+Umschalt+F9`** funktioniert (siehe auch Abschnitt 6).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Ein bekanntes erfolgreiches Testfinal zur Wiederholung fehlt. Unbekannter Sprachinhalt bleibt unbenutzt.
- [ ] **V05-09** Versuch, **denselben Hotkey für zwei Funktionen** zu hinterlegen, wird mit verständlicher Fehlermeldung abgelehnt.  
  **FAIL** · 2026-11-22, 00:55:30 · E14, B09. Duplikat wurde technisch abgewiesen. Die Meldung verweist auf Reparatur eines migrierten Profils und benennt weder den doppelten Hotkey noch die betroffenen Felder.
- [ ] **V05-10** Nach fehlgeschlagenem Hotkey-Apply funktionieren die bisherigen Belegungen weiterhin (Rollback).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E14, B02. Unveränderter YAML-Hash, nach erneutem Einlesen Primärhotkey und ursprünglicher leerer Sekundärslot, vorherige native Bindungen weiter belegt. Wiederholtes Auslösen eines Diktats bzw. Reinsert des unbekannten Finals bleibt offen.
- [x] **V05-11** „Globale Hotkeys aktivieren“ aus-/einschalten: Wirkung entspricht der Einstellung, nach Reaktivierung sind die konfigurierten Hotkeys wieder nutzbar.  
  **PASS** · 2026-11-22, 01:01–01:04:43 · E14. Nach GUI-Apply aus waren Primary und Reinsert Win32-seitig registrierbar. Nach GUI-Apply an waren F10 und Reinsert besetzt. Nach Rücknahme war der ursprüngliche Primary wieder besetzt und F10 frei.

## 6. Clipboard / Texteingabe / Verlauf

- [ ] **V06-01** Text wird in **Windows-Editor** eingefügt, wenn dieser vor dem Final den Fokus hat.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, E03. Windows-Editor diente als bestätigtes Aktivierungsziel. Kein kontrolliertes Final mit Paste in Notepad nachgewiesen.
- [ ] **V06-02** Text wird in **einem zweiten geeigneten Programm** (z. B. Browser-Textfeld) korrekt eingefügt.  
  **FAIL** · 2026-11-22, 00:22:26–00:22:50 · B02, E06. Einmaliges Einfügen im zweiten lokalen Testeditor bestätigt. Sichtbarer Text entspricht nicht dem definierten Testinput, daher kein End-to-End-PASS für korrekte Ausgabe.
- [x] **V06-03** Zwischenstände/Interims erscheinen **niemals** als automatisch eingefügter Text.  
  **PASS** · 2026-11-22, 00:21:52–00:22:26 · E06. Im akustischen Versuch liefen mehrere Realtime-Ergebnisse. Das Editorfeld blieb bis zum Final leer; ein dokumentierter Paste-Job erst beim Final.
- [ ] **V06-04** Ein Final wird **genau einmal** eingefügt; bei aufeinanderfolgenden Aktivierungen gibt es keine Doppel-Pastes.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E06, B02. Ein Final mit genau einem Paste belegt. Folgeaktivierungen mit kontrollierten Finals fehlen.
- [ ] **V06-05** Bereits in der Zwischenablage vorhandenen unkritischen Testtext verwenden und nach dem Paste prüfen, ob sich das Clipboard wie in den lokalen Einstellungen vorgesehen verhält (z. B. Wiederherstellung).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Der erste akustische Lauf nutzt den Profilstandard restore_previous=false. Ein Test mit vorbereitetem bekanntem Clipboard-Inhalt fehlt.
- [ ] **V06-06** Einfügeverzögerung bzw. Zwischenablageeinstellungen verändern und die Wirkung in einer Testanwendung prüfen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Einfügeverzögerung wurde nicht über die GUI verändert und auf Wirkung geprüft.
- [ ] **V06-07** Die Funktion **„Letzten Text erneut einfügen“** bewusst auslösen; sie fügt das letzte Final erneut ein, aber **nur auf den ausdrücklichen Befehl**.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Kein qualifiziertes, unbedenkliches letztes Final für einen absichtlichen Reinsert.
- [ ] **V06-08** Die Wiedereinfügefunktion erzeugt **keinen zusätzlichen Transkriptdatensatz** in der Historie.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Reinsert und Memory-/DB-Verlauf vor und nach einem kontrollierten Testfinal fehlen.
- [ ] **V06-09** Historienfenster öffnen: neu erzeugte Testtranskripte sind in plausibler zeitlicher Reihenfolge vorhanden.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, E13. Historienregister zeigte den einen kurzen Eintrag im Speicher. Eine zeitliche Mehrfachfolge mit eindeutig kontrolliertem Sprachinput fehlt. Der SQLite-Nullstand erklärt sich aus der Standardpolicy für kurze Finals.
- [ ] **V06-10** Einen ausgewählten Historieneintrag erneut einfügen; der gewählte und nicht irgendein anderer Text wird verwendet.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Kein eindeutig qualifizierter Historieneintrag für gezielte Wiedereinfügung.
- [ ] **V06-11** Einen **Testeintrag** löschen; nur der gewünschte Eintrag verschwindet.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B05. Kein ausschließlich zu diesem Test erzeugter, eindeutig unbedenklicher Eintrag. UI-Datenlöschung braucht zudem eine Bestätigung unmittelbar vor der Aktion.
- [ ] **V06-12** Historie deaktivieren bzw. wieder aktivieren (falls in der GUI angeboten): bestehende Einstellungen werden respektiert, Final-Paste funktioniert weiterhin.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. GUI-Umschaltung der Historie und kontrollierter Final-Paste nach Umschaltung fehlen.
- [ ] **V06-13** Eine eventuell angebotene Funktion **„Verlauf leeren“** ausschließlich mit vorher freigegebenen **Testdaten** prüfen; niemals ungefragt vorhandene private Historie löschen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B05. Keine vorher freigegebenen Testdaten im Verlauf. UI-Datenlöschung braucht Bestätigung unmittelbar vor der Aktion.

## 7. ReSpeaker-LED / Sound / visuelle Rückmeldung

- [x] **V07-01** LED-Controller bzw. ReSpeaker-LED-Ring wird erkannt; keine dauerhaften USB- oder LED-Initialisierungsfehler.  
  **PASS** · 2026-11-22, 00:14:50–00:14:51 · E04. Runtime erkennt ReSpeaker-USB-Controller. LEFX-Dienst startet mit 12 LEDs, 30 FPS und 36 Effekten. `output available (respeaker)` ohne dauerhaften Initialisierungsfehler. Keine visuelle Hardwarewertung.
- [ ] **V07-02** LED-Ring signalisiert **Bereitschaft/Idle** passend zur konfigurierten Rückmeldung.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Bereitschaft wurde technisch gemeldet. Physisches LED-Muster ist nicht einsehbar.
- [ ] **V07-03** LED-Ring signalisiert **Aufnahme/Listening** während eines echten Diktats.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Ein Aufnahmezustand ist technisch belegt. Physisches LED-Muster fehlt.
- [ ] **V07-04** Beim Beenden bzw. Schließen der Eingabe erfolgt die passende LED-Rückmeldung.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Keine visuelle Beobachtung am physischen LED-Ring beim Eingabeschluss.
- [ ] **V07-05** Erfolgreiches Final, Cancel und Fehlerfall erzeugen voneinander unterscheidbare bzw. korrekt zugewiesene LED-Muster, sofern konfiguriert.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Kein physischer Vergleich der LED-Muster für Final, Cancel und Fehler.
- [ ] **V07-06** Wake-/manuelle Laufzeitpause wird visuell plausibel angezeigt, sofern konfiguriert.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, B04. Keine ausgelöste Laufzeitpause mit sichtbarer, zuordenbarer Rückmeldung.
- [ ] **V07-07** LED-Helligkeit/Farb- oder Feedbackeinstellungen verändern: tatsächliche Hardwarewirkung prüfen und anschließend auf Wunsch zurücksetzen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Helligkeit/Farbe können ohne physische Sicht auf den Ring nicht wirksam abgenommen werden.
- [ ] **V07-08** Sounds für Start, Stopp, Abschluss, Abbruch und Fehler sind **hörbar** und nicht doppelt ausgelöst (abhängig von aktiver Soundkonfiguration).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04, E13. Sounds waren in der GUI aktiv und fünf WAV-Zuordnungen sichtbar. Die physische Hörbeobachtung für die geforderten Zustände fehlt.
- [ ] **V07-09** Sound-Lautstärke und Ein-/Ausschalten ändern: erwartete Wirkung; keine ungewollte Änderung der Aufnahme.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04. Weder wahrnehmbare Lautstärkewirkung noch Auswirkung auf das Aufnahmesignal belegt.
- [ ] **V07-10** Bei deaktivierten LEDs bzw. nicht verfügbarem Controller funktionieren Mikrofon und Transkription weiterhin; Fehler erscheint nur als Diagnose, nicht als Totalausfall.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Kein deaktivierter LED-Controller in Kombination mit qualifiziertem Mikrofon-Final.
- [ ] **V07-11** Overlay zeigt Aufnahme-, Warte-, Abschluss-, Fehler- und Pausenzustände nachvollziehbar und ohne veraltete Anzeigen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Aufnahme-, Warte-, Abschluss-, Fehler- und Pausenanzeigen wurden nicht als vollständige visuelle Folge beobachtet.

## 8. Einstellungsdialoge, Speicherung und Berechtigungen

### 8.1 Lokale und Sessioneinstellungen

- [x] **V08-01** Werte in „Lokale Trigger & Bedienung“ ändern und übernehmen; gewünschte und tatsächlich wirksame Trigger werden getrennt dargestellt.  
  **PASS** · 2026-11-22, 01:01–01:04 · E12, E14. Lokale Hotkey-Werte über die GUI geändert und erfolgreich übernommen. Dauerhafte Triggerwahl und aktuelle Wirksamkeit wurden getrennt gezeigt. Manueller Trigger blieb wirksam, Wake blieb aus.
- [x] **V08-02** Sessioneinstellungen von der Testinstanz laden; **Angefordert, Wirksam, Serverstandard, Schema-Startwert und Wirksam-ab-Policy** sind nachvollziehbar.  
  **PASS** · 2026-11-22, 00:51–00:52 · E12. Sessionansicht zeigte Angefordert, Wirksam, Serverstandard, Schema-Startwert und Wirksam ab für die Final-Instanz. Session-, Server- und Katalogrevision waren sichtbar.
- [x] **V08-03** Einen ungefährlichen, individuell erlaubten Sessionparameter ändern und übernehmen; bestätigte Wirkung bzw. nötiger Aktivierungs-/Sessionwechsel ist eindeutig sichtbar.  
  **PASS** · 2026-11-22, 00:54 · E12. Sessionparameter Warten auf Eingabeschluss auf 5200 ms übernommen. Revision 1 und Requested/Effective 5200 bei Serverstandard 5000 und Serverrevision 0. Anschließend Rücknahme auf 5000 mit Sessionrevision 2.
- [x] **V08-04** Unveränderliche oder nur per Serverdefault änderbare Felder lassen sich nicht irreführend als sofort wirksame Sessionänderung speichern.  
  **PASS** · 2026-11-22, 00:51 / 01:05 · E12. Wake-Rauschunterdrückung und Sprachschwelle waren in Session ausgegraut, mit Hinweis auf Admin-Serverdefaults. UI unterschied Policy Nächste Verbindung und Änderungsrecht.
- [ ] **V08-05** Wake-Katalog und Serverwerte über „Neu laden“ aktualisieren, ohne zuvor begonnene, noch ungespeicherte Bearbeitungen unbeabsichtigt zu verlieren.  
  **FAIL** · 2026-11-22, 00:52–00:54 · E12, B08. Explizites Reload verwarf ungespeicherte Sessionentwürfe 5200 und 5300 ms zweimal still. Die Oberfläche zeigte danach wieder 5000 ms und nur Serverwerte geladen.
- [ ] **V08-06** Bei einer Änderung während eines aktiven Diktats werden die erforderlichen Optionen (z. B. fertigstellen, abbrechen, später übernehmen) angezeigt; keine stillschweigende Zerstörung des aktiven Diktats.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Kein GUI-Apply mit aktiver Testaufnahme und sichtbarer Optionsauswahl.
- [ ] **V08-07** Gerätewahl/Audioeinstellungen übernehmen; danach weiterhin erfolgreich aufnehmen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Kein GUI-Gerätewechsel mit anschließendem kontrolliertem Diktat.
- [ ] **V08-08** Overlay-Position/Transparenz/Sichtbarkeit verändern und die sichtbare Wirkung prüfen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03. Sichtbare Positions-, Transparenz- oder Sichtbarkeitsänderung fehlt.
- [ ] **V08-09** Zwischenablage-/Textinjektionseinstellungen verändern; Wirkung prüfen und bei Bedarf zurückstellen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Keine GUI-Änderung und Wirkungsmessung von Clipboard/Textinjektion.
- [ ] **V08-10** Historie-/Speichereinstellungen ändern und ihre Wirkung prüfen, ohne andere Profile zu verändern.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Keine GUI-Änderung der Historieneinstellungen mit messbarer Wirkung.
- [ ] **V08-11** Sound-, LED- und Feedbackzuordnungen ändern; jeweils eine echte Zustandsrückmeldung auslösen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, B04. Keine geänderten Zuordnungen mit überprüfter physischer Rückmeldung.
- [x] **V08-12** Diagnose-/Loggingoberfläche öffnen, filtern und Einträge einsehen; beim Auftreten eines Testfehlers ist dessen Uhrzeit nachvollziehbar.  
  **PASS** · 2026-11-22, 00:58–00:59 · E13. Logs-und-Diagnose-Fenster über lokale GUI geöffnet. Suche nach Audio capture started reduzierte die Anzeige auf drei datierte Einträge, darunter den Geräte-Apply um 00:56:50 MEZ.
- [ ] **V08-13** Client regulär schließen und erneut über das V2-Startskript starten: **gespeicherte** Einstellungen bleiben bestehen, **Laufzeitpausen** werden nicht fälschlich dauerhaft gespeichert.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, E04. Regulärer Ausstieg und Start mit identischem YAML belegt. Persistenzänderung und Rücksetzen von Laufzeitpausen fehlen.
- [ ] **V08-14** Einen absichtlich ungültigen Wert oder Hotkeykonflikt eingeben: verständliche Ablehnung und **keine beschädigte Konfigurationsdatei**.  
  **FAIL** · 2026-11-22, 00:55:30–00:55:45 · E14, B09. Ungültige Doppelbelegung abgelehnt und YAML-Hash gleich. Die sichtbare Migrationsmeldung war für die eingegebene Doppelbelegung nicht konkret genug.
- [ ] **V08-15** Prüfen, dass die normale Altclient-Konfiguration und dessen Historie nach allen V2-Änderungen unberührt geblieben sind.  
  **FAIL** · 2026-11-22, 00:17:36–00:18:41 · B01, E05. Erster Lauf schrieb trotz abgesetztem Profil den gemeinsamen Event-Cursor unter LOCALAPPDATA. Neue Bindung Final-Host /ws/logs, Protokoll 2. Altclient-Konfigurationsdatei zeigt keine Änderung im Prüfzeitraum. Der frühere Cursorinhalt liegt nicht als Backup vor.

### 8.2 Geschützte Serververwaltung (nur falls autorisiert)

> **Achtung:** Diese Tests ändern potenziell das Verhalten anderer Nutzer/Sessions auf der Testinstanz. Nur nach ausdrücklicher Freigabe und mit gültigem Schlüssel durchführen. Falls kein Admin-Key oder keine Änderungsfreigabe vorliegt, als **„N/A – nicht autorisiert“** dokumentieren; für eine Freigabe *mit* Adminverwaltung bleibt dieser Bereich dann gesondert offen.

- [x] **V08-16** Ohne Admin-Verifikation sind Serverdefault-Eingabefelder und „Serverdefaults ändern“ gesperrt.  
  **PASS** · 2026-11-22, 00:51 · E12. Serververwaltung zeigte ohne Admin-Verifikation Gesperrt. Wunschfelder und Schaltfläche für Serverdefaults waren deaktiviert. Key-Feld leer, keine Eingabe und keine Mutation.
- [ ] **V08-17** Gültigen Admin-Key **nur im Clientdialog** prüfen; die Felder werden erst nach erfolgreicher Bestätigung freigeschaltet.  
  **N/A** · 2026-11-22, Bewertet 00:26 · B05. Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen.
- [ ] **V08-18** Falls gewünscht: Speichern/Laden/Löschen eines Test-Admin-Keys über den **Windows Credential Manager** korrekt nachvollziehen; der Schlüssel steht nicht im Klartext in YAML/Logs.  
  **N/A** · 2026-11-22, Bewertet 00:26 · B05. Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen.
- [ ] **V08-19** Nur mit Freigabe: **einen reversiblen Serverdefault** ändern, bestätigte Revision und Auswirkungen prüfen.  
  **N/A** · 2026-11-22, Bewertet 00:26 · B05. Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen.
- [ ] **V08-20** Den zuvor geänderten Serverdefault **exakt auf seinen Ausgangswert** zurücksetzen und den erfolgreichen Readback nachweisen.  
  **N/A** · 2026-11-22, Bewertet 00:26 · B05. Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen.
- [ ] **V08-21** Bei ungültigem/abgelaufenem Key oder falscher Revision wird eine Änderung sicher verweigert und die UI entsprechend wieder gesperrt.  
  **N/A** · 2026-11-22, Bewertet 00:26 · B05. Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen.

## 9. Verbindungsabbrüche, Fehlerfälle, Wiederherstellung

- [ ] **V09-01** Während einer ruhenden Session eine **kurze, kontrollierte** Netzwerkunterbrechung simulieren; Client zeigt Verbindungsverlust und verbindet sich wieder.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B06. Keine verfügbare, auf den aktuellen Client begrenzte und reversible Unterbrechung im freigegebenen Umfang.
- [ ] **V09-02** Nach Reconnect eine **neue V2-Session** und betriebsbereiten Zustand beobachten; kein V1-Fallback.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B06. Andere Session nach Neustart belegt. Neue Session nach kontrolliertem Verbindungsabriss fehlt.
- [ ] **V09-03** Nach Reconnect ein normales Diktat mit genau einem Final-Paste durchführen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B06. Kein isolierter Abriss und kein nachfolgendes, korrekt zugeordnetes Final-Paste.
- [ ] **V09-04** Testweise während **einer unkritischen Testaufnahme** die Verbindung unterbrechen: verständlicher Fehlerstatus; keine stillschweigende doppelte Einfügung eines ungewissen Finals.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B06. Unterbrechung im laufenden Diktat ohne Auswirkung auf Rechnernetz und andere Anwendungen nicht verfügbar.
- [ ] **V09-05** Verbindungswiederherstellung nach aktivem Diktat ist nachvollziehbar; kein heimliches Umschalten auf alte Aktivierungs-IDs.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B06. Bindungswechsel und Abweisung alter Aktivierungen nach isoliertem Abriss nicht in diesem Lauf beobachtet.
- [ ] **V09-06** Ein Mikrofon-Mute bzw. kontrollierter Geräteverlust führt zu sicherem Audioverfügbarkeitsstatus; nach Wiederherstellung weiterarbeiten.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, B04. Kein sicher ausgeführtes Mute-/Geräteereignis mit kontrolliertem Folgediktat.
- [ ] **V09-07** Ungültigen Serverendpunkt **nur im separaten Testprofil** testweise verwenden: klarer Fehler, keine endlose UI-Blockade; anschließend **korrekte `/ws/v2`-URL wiederherstellen**.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, E10. Transportprobe gibt für den ungültigen Pfad blocked bei Generation 0 ohne Verbindungsversuch aus. Positivpfad /ws/v2 gültig. GUI-/Neustartprobe und sichtbare Fehlermeldung bleiben offen.
- [x] **V09-08** Client regulär beenden, während er verbunden ist: Prozess endet, LEDs/Hotkeys werden freigegeben und beim Neustart sind keine doppelten Ressourcen belegt.  
  **PASS** · 2026-11-22, 00:18–00:19 / 01:06:04–01:06:30 · E04, E15. Benutzer führte beide Tray-Ausstiege aus. Prozessausstieg und Stop von Audio-, Text- und LED-Dienst bestätigt. Erstlauf wurde erfolgreich neu gestartet. Nach abschließendem Exit waren die drei geprüften Hotkeys freigegeben.
- [x] **V09-09** Fehlermeldungen und technische Diagnose enthalten keine API-Schlüssel oder unnötigen privaten Diktatinhalte.  
  **PASS** · 2026-11-22, 00:26 / 01:06:54 · E08. Abschluss-Stichprobe aus 53 Clientlogzeilen und 370 Beobachtungsdatensätzen. Null Treffer auf Secret-Muster, Secretfelder und Transkriptfelder. Aussage auf geprüften Lauf und Felder begrenzt.

## 10. Langzeittest und Abschlussbeobachtung

- [ ] **V10-01** Eine **30–60-minütige** repräsentative normale Sitzung durchführen (Mikrofon, Tray, Einstellungsdialog, Overlay; ggf. Wake Word).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E09, B02. Reale Laufzeitmessung 30:24 Minuten. Sie umfasst eine kontaminierte Diktatprobe und überwiegend Bereitschaft. Die repräsentative Nutzungsfolge mit erfolgreichen Diktaten fehlt.
- [ ] **V10-02** In dieser Sitzung mindestens **10 unterschiedliche Kurz-Diktate** mit korrektem Final-Paste durchführen; Anzahl dokumentieren.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Keine zehn kontrolliert zuordenbaren Kurz-Diktate mit korrektem Final-Paste.
- [ ] **V10-03** Zusätzlich ein längeres Diktat (mindestens **2 Minuten**) erfolgreich finalisieren; kein hängender Abschluss.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Kein aktiver Test mit zwei Minuten kontrollierter Sprache und erfolgreichem Final.
- [ ] **V10-04** Zwischen zwei Diktaten das aktive Zielprogramm wechseln; Einfügen erfolgt in das **jeweils ausdrücklich fokussierte** Textfeld.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E03, E06, B02. Beide Ziele wurden explizit fokussiert. In Notepad wurde kein qualifiziertes Final eingebracht; deshalb kein Fokuswechsel-PASS.
- [ ] **V10-05** Prüfen, dass keine spontanen, falsch erkannten Aktivierungen, Doppel-Pastes oder wiederkehrenden unvollständigen Finals auftreten.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. Für die repräsentative Stichprobe fehlen die kontrollierten Finals und akustische Wake-Szenarien.
- [ ] **V10-06** Start-/Endwerte von RAM-Verbrauch sowie auffällige CPU-Auslastung dokumentieren; kein stetiges unerklärliches Wachstum oder dauerhaft blockierte Oberfläche.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E09. Anwendungsprozess: 107,44 auf 568,46 MiB Working Set, 466,04 auf 478,28 MiB Private Bytes. Letzte Messphase praktisch konstant, CPU im Mittel 0,236 % der Rechnerkapazität. Pflicht-Lastmix und durchgehende UX-Beobachtung fehlen.
- [ ] **V10-07** Während des Langzeittests Logs auf wiederkehrende Fehler, Endlosschleifen, Reconnect-Stürme und Geräteausfälle prüfen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E09. Messfenster ohne beobachteten Reconnect oder Geräteausfall, 36 Keepalives und genau eine kontrolliert ausgelöste Activation. Der geforderte repräsentative Lastmix fehlt.
- [ ] **V10-08** Nach Abschluss Client sauber beenden und wieder starten: Gerät, Hotkeys, Profil, Historie und Verbindung funktionieren weiterhin.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E04, B03. Kontrollierter Neustart nach dem Erstlauf belegt. Kein vollständiger Neustart nach repräsentativem Soak mit Verlauf-, Geräte- und Hotkey-Nachweis.
- [ ] **V10-09** Gegenprobe: bisheriger Client bzw. dessen bestehende Konfiguration ist nicht verändert worden; die produktiven Serverinstanzen blieben unberührt.  
  **FAIL** · 2026-11-22, 00:17:36–00:18:41 · B01, E05. Gemeinsamer Cursor veränderte sich im ersten Startweg. Serverzugriffe beschränkten sich auf lesenden Health-/Katalogzugriff und normale V2-Testsessions.

## 11. Freigabeentscheidungen

### Fachliche Pflichtkriterien

- [ ] **F01** Regulärer Windows-Start und GUI geprüft (Abschnitt 1).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · E04, E12, B03. EXE, Ready, Single-Instance und Trennung der Dialoge belegt. Tray-Tooltip und geforderter direkter Start-Doppelklick offen.
- [ ] **F02** Reale ReSpeaker-Mikrofonaufnahme erfolgreich (Abschnitt 2).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02. ReSpeaker-Audiostream und physischer Eingangspegel vorhanden. Eindeutig kontrollierte Sprachquelle fehlt.
- [ ] **F03** Manuelle Diktatsteuerung, Finaltranskript und **genau ein** Paste erfolgreich (Abschnitte 3 und 6).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, E06. Nativer Hotkey und einmaliger Paste belegt. Korrektes Solltranskript sowie alle verpflichtenden Steueraktionen fehlen.
- [ ] **F04** Wake Word, beide Trigger und Laufzeitpause unter realen Bedingungen geprüft (Abschnitt 4).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Akustische Wake-Matrix und Laufzeitpause offen.
- [ ] **F05** Globale Hotkeys, Rücknahme von Konflikten und Reinsert erfolgreich (Abschnitt 5).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, B03. Nativer Hotkey belegt. Konfliktrollback und qualifizierter Reinsert fehlen.
- [ ] **F06** ReSpeaker-LED, Overlay und hörbares Soundfeedback praktisch geprüft (Abschnitt 7).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B03, B04. LEFX technisch verfügbar. Physische LED-/Soundbeobachtung und vollständige Overlayfolge fehlen.
- [ ] **F07** Alle für den vorgesehenen Einsatz benötigten Einstellungen über die GUI geändert, bestätigt, gespeichert, neu geladen und ggf. zurückgenommen (Abschnitt 8).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B08, B09, E12, E13. Session-Apply, Rücknahme, GUI-Admin-Guard, Gerätewechsel und Diagnose bestanden. Stiller Draft-Verlust und missverständliche Hotkey-Ablehnung bleiben offen.
- [ ] **F08** Recovery nach Verbindungs-/Gerätefehlern ohne doppelten Textnachtrag (Abschnitt 9).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B04, B06. Isolierter Netzwerkabriss und physische Gerätere­covery ohne Doppel-Paste offen.
- [ ] **F09** Langzeittest erfolgreich und ohne ungelöste kritische Fehler (Abschnitt 10).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B02, E09. Verpflichtende Aktivität im 30–60-Minuten-Lauf fehlt.
- [ ] **F10** Bei Adminfunktionen: Berechtigung, Änderung und Rücksetzung nachgewiesen **oder** Adminfunktionen ausdrücklich aus dem Freigabeumfang ausgeschlossen.  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B05. Adminprüfung ohne gültigen Schlüssel und getrennte Autorisierung offen. Eine Freigabe mit Adminfunktionen ist nicht Gegenstand dieser Empfehlung.
- [x] **F11** Alle festgestellten Defekte sind dokumentiert und als behoben/akzeptiert/offen eingestuft.  
  **PASS** · 2026-11-22, 01:07 · E05, E06, E12, E14. Befunde und Testblockaden mit Schweregrad, Reproduktion und offenem Status im separaten Befundbericht dokumentiert.
- [ ] **F12** Separate technische/rechtliche Produkt- und Redistributonsfreigabe für veröffentlichte Artefakte geklärt (**nicht** durch funktionierende Laufzeitlizenz allein ersetzt).  
  **BLOCKIERT** · 2026-11-22, Bewertet 01:09 · B07. Separate Produkt- und Redistributionsfreigabe fehlt. Frühere Buildtests erlauben keine Rechts- oder Releaseaussage.

**Endentscheid (eine Option ankreuzen):**

- [ ] **GO für die nächste Testphase** – alle dafür erforderlichen Pflichtpunkte bestanden, Einschränkungen dokumentiert.  
  **NOT_RUN** · 2026-11-22, 01:07 · B01–B09. Option ungewählt, Pflichtkriterien sind offen bzw. fehlgeschlagen.
- [ ] **GO mit Auflagen** – nur klar beschriebene, nicht blockierende Restpunkte offen.  
  **NOT_RUN** · 2026-11-22, 01:07 · B01–B09. Option ungewählt, offene Risiken betreffen Pflichtkriterien.
- [x] **NO-GO / BLOCKIERT** – mindestens ein kritisches Kriterium fehlt oder schlägt fehl.  
  **PASS** · 2026-11-22, 01:07 · B01–B09. Diese Entscheidungsoption ist gewählt. PASS markiert die ausgeführte Entscheidung, nicht die Produktfreigabe.

**Freigabeumfang:** Keine Freigabe. Nachlauf zur praktischen Endabnahme. Adminpflege außerhalb dieses Laufs.  
**Freigabe durch:** Ausstehend.  
**Datum / Uhrzeit:** 2026-11-22, 01:09 MEZ

## Befunde und Abweichungen

Für jede festgestellte Auffälligkeit möglichst die **Test-ID** aus dieser Checkliste nutzen.

| Test-ID | Uhrzeit | Erwartet / tatsächlich beobachtet | Schweregrad (Blocker / Hoch / Mittel / Niedrig) | Log/Screenshot | Status / Maßnahme |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

## Abschlussmesswerte und Notizen

| Messwert / Beobachtung | Ergebnis |
|---|---|
| Dauer Langzeittest | 30:24 min Prozessmessung mit einem kontaminierten Diktat und überwiegender Bereitschaft. Repräsentativer Soak BLOCKIERT. |
| Anzahl erfolgreiche Kurz-Diktate | 0 kontrollierte Solltranskripte. 1 technisch abgeschlossener V2-Final-Paste mit Fremdton. |
| Anzahl fehlgeschlagene Diktate / Final-Pastes | 1 abweichendes SAPI-Solltranskript; kein beobachteter Doppel-Paste. |
| Anzahl unerwünschter Wake-Aktivierungen | Kein Wake-Qualifikationstest. Wake war in der laufenden Session deaktiviert. |
| RAM / CPU zu Beginn und am Ende | Working Set 107,44 → 568,46 MiB; Private Bytes 466,04 → 478,28 MiB; CPU 2,00 → 53,69 s, 0,236 % der Rechnerkapazität im Mittel. |
| ReSpeaker-Eingabegerät (Name / Index) | XVF3800, Systemstandard PortAudio 1, expliziter vollständig benannter Eintrag PortAudio 9. 16 kHz. GUI-Pegel RMS 77,3 und Peak 1,19 %. |
| Nachgestellte Netzwerk-/Gerätefehler | Kein Live-Netzabriss oder physischer USB-Verlust. Ungültige Route in netzloser Transportprobe blockiert. |
| Auffällige Zeitpunkte und Logdateien | Cursor 00:17–00:18, SAPI 00:21–00:22, Reload 00:52–00:54, Hotkeykonflikt 00:55, regulärer Exit 01:06. E04, E05, E06, E12, E14 und E15. |
| Bewusst nicht ausgeführte Tests + Grund | Schreibende Adminfälle ohne Autorisierung N/A, physische USB-/Wahrnehmungstests und weitere kontrollierte Diktate BLOCKIERT. |
| Offene Blocker vor einer Freigabe | B01, B02, B03, B04, B06, B07, B08 und B09. Adminumfang B05 separat. |

**Technische Referenz:** `ABNAHMEBERICHT_V2_FINAL_2026-11-21.pdf` / `.md` sowie die im Desktop-Testpaket enthaltenen Nachweise. Die zuvor erbrachten **1.407 erfolgreichen automatisierten Tests**, das echte V2-Handshake und die synthetische Kroko-Sprachprüfung gelten als **technisch geprüft**, nicht als Ersatz für die hier ausstehenden Hands-on-Tests.
