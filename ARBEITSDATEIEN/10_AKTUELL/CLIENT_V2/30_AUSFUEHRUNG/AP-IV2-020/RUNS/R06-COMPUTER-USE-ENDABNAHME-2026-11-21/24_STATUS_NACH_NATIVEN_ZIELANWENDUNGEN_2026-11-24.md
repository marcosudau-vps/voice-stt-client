# R06 – konsolidierte Kriterienmatrix nach nativen Zielanwendungsprüfungen (24.11.2026)

Historische Matrix 09 bleibt unverändert. Aktuelle Befunde aus 10–23; PASS_SCOPED ist ein bestandener Teilnachweis und kein vollständiges PASS. Unveränderte historische PASS bleiben an den ursprünglich geprüften Kandidaten gebunden. Keine Freigabe durch automatische Hochstufung. V06-12 ist bedingt (GUI-Funktion nicht angeboten). Zusätzliche Beobachtungen und verbleibende Grenzen siehe Bericht 15; Matrix 14 bleibt erhalten.

## Kriterien

| ID | Historischer Status | Aktueller Status | Beleg | Befund |
|---|---|---|---|---|
| V00-01 | PASS | PASS | E01 | Alle vier geforderten Paketbestandteile vorhanden. EXE 77.414.876 Byte, SHA-256 stimmt. |
| V00-02 | PASS | PASS | E01, E02 | Profil exakt /ws/v2 und Health auf derselben Final-Testdomain. HTTP 200, ready=true, sttReady=true. Separater aktueller V2-Handshake liefert erwarteten Server-Commit. |
| V00-03 | N/A | N/A | E01 | Prozessinventar vor Start ohne Altclient und ohne laufendes Altclient-Diktat. Altclient-Dateien blieben während der Vorbereitung am Ort. |
| V00-04 | N/A | N/A | E01 | Kein aktiver Altclient zum regulären Beenden. Altclient wurde für diese Prüfung nicht gestartet. |
| V00-05 | PASS | PASS | E03 | Computer Use öffnete mit Strg+T einen leeren Notepad-Tab und fokussierte sein Textfeld. Zweites, eigenständiges Qt-Textfeld anschließend bereitgestellt. |
| V00-06 | PASS | PASS | E01, E04 | Vor Start Profilkopie und SHA-256 gesichert. Windows und PortAudio identifizierten bei Systemstandard den ReSpeaker-Eingang; Laufzeitspur meldet 16 kHz und 40-ms-Frames. |
| V01-01 | NOT_RUN | PASS_SCOPED | 13 Frozen-Normalstart | Normale korrigierte EXE startet und erreicht Ready; Explorer-Doppelklick fehlt. |
| V01-02 | BLOCKIERT | PASS_SCOPED | 11, 13 | Native Qt Tray sichtbar, Tooltip/Menu geprüft, korrigierte EXE mit Trayfenster; physischer Hover/Klick bleibt. |
| V01-03 | PASS | PASS | E02, E04 | Die Desktop-EXE erreichte in zwei Läufen V2-Transportzustand ready. Domain aus geprüftem Profil, Soll-Server-Commit aus gesonderter zeitnaher V2-Probe. |
| V01-04 | PASS | PASS | E01, E02, E04 | Desktopspur zeigt V2-Verbindungsaufbau, Bootstrap und Ready. Exakter /ws/v2-Endpunkt aus Launcher-Profil und der aktuellen Wire-Probe. V2-Runtime akzeptiert für die Diktatverbindung ausschließlich /ws/v2. |
| V01-05 | PASS | PASS | E12 | Der Benutzer öffnete das V2-Hauptfenster aus dem Tray. Computer Use öffnete den lokalen Einstellungsdialog, schloss ihn und öffnete ihn erneut. Das wiedergeöffnete Fenster hatte einen neuen Handle und der Hauptdialog blieb bedienbar. |
| V01-06 | PASS | PASS | E12 | Die Register Lokale Trigger & Bedienung, Session und Serververwaltung wurden in der laufenden EXE aufgerufen und inhaltlich geprüft. |
| V01-07 | PASS | PASS | E13 | Alle fünf lokalen Register geöffnet. Audio/Geräte, Verlauf, Clipboard in Allgemein, Darstellung/Feedback und Logging/Diagnose waren zugänglich. |
| V01-08 | BLOCKIERT | PASS_SCOPED | 13 native-desktop-history-retest-2 | 8 Register bei 2 Größen geometrisch geprüft; vollständige visuelle Lesbarkeit/Skalierung offen. |
| V01-09 | BLOCKIERT | PASS_SCOPED | 11, 13 | Native Overlay-Position, Sichtbarkeit und Opazität geprüft, Wechsel fremder Vordergrundfenster offen. |
| V01-10 | PASS | PASS | E04 | Zweiter Start mit demselben Launcher. Runtime protokolliert „RealtimeSTT is already running; second instance exits“. Bestehendes Onefile-PID-Paar blieb erhalten. Ablehnung erfolgt vor zweitem Qt-/Hotkey-Start. |
| V02-01 | PASS | PASS | E11, E13 | Windows zeigte den XVF3800 als Standardeingang. Die Client-Auswahlliste zeigte den vollständigen Gerätenamen. Windows bestätigte VID 2886 / PID 001A. |
| V02-02 | PASS | PASS | E13, E04 | Vollständigen ReSpeaker-Eintrag in der lokalen GUI ausgewählt und mit Apply übernommen. Laufzeitgerät PortAudio 9. Nach der Prüfung wieder Systemstandard und ursprüngliches YAML. |
| V02-03 | PASS | PASS | E13, E04 | Der Stream startete nach Apply mit dem explizit ausgewählten ReSpeaker und 16 kHz neu. Die lokale Drei-Sekunden-Prüfung meldete RMS 77,3 und Peak 1,19 %. Keine Audio-Dauerstörung. |
| V02-04 | PASS | PASS | R06 geführt | Wiederholter menschlicher Weckruf und frei gesprochener Testsatz erzeugten ein zugeordnetes Final. |
| V02-05 | BLOCKIERT | PASS_SCOPED | 13 acoustic-long-retest | 209 s reales akustisches Langdiktat, 7 getrennte Finals, kein ungeplanter Abbruch; separate Pausenprobe nicht vollständig. |
| V02-06 | PASS | PASS | R06 geführt | Hardware-Mute stoppte Capture und blockierte den Hotkey. Aufheben öffnete den ReSpeaker-Stream wieder. Der erste Folgereiz löste kein Recording aus. |
| V02-07 | PASS | PASS | R06 geführt | Windows-Geräteliste, Capture und LED-Transport zeigten Verlust und Rückkehr am gleichen Port. |
| V02-08 | PASS | PASS | R06 geführt | Nach Rückkehr kam ein zuordenbarer Testtext genau einmal an. Ein Wort wich ab. |
| V02-09 | BLOCKIERT | PASS_SCOPED | 13 native-device-preview-retest-2 | Ungültiges Gerät, kein Crash, GUI auf ReSpeaker zurück und erfolgreiches Diktat. Wiederholte PortAudio-Stacktraces; verständliche UI-Fehleranzeige separat. |
| V03-01 | BLOCKIERT | PASS_SCOPED | 13 native-active-apply-retest-2 | GUI-Profilapply und echte neue Session auf manual-only. |
| V03-02 | PASS | PASS | E03, E04 | Strg+Umschalt+Leertaste per Computer Use im leeren Notepad-Tab. Genau ein Hotkey-Ereignis und eine eindeutige manuelle Activation mit Aufnahmebeginn. |
| V03-03 | PASS | PASS | R06 geführt | Der synthetisch gesprochene Zugsatz kam vollständig über den ReSpeaker an und wurde genau einmal eingefügt. |
| V03-04 | BLOCKIERT | PASS_SCOPED | 13, 15 | Zwei reale akustische Diktate mit Overlay vor Mock-Einfügung; Anwender bestätigt zusätzliche Overlay-Prüfung. |
| V03-05 | PASS | PASS | R06 geführt | Der separat konfigurierte Finish-Hotkey schloss die offene Folgephase mit 'finished' und Idle. |
| V03-06 | PASS | PASS | R06 geführt | Der vollständige Sollsatz erschien im Testeditor und als Eintrag im lokalen Verlauf. |
| V03-07 | PASS | PASS | E06 | Genau ein nativer `command_sent`-Job (vier Keyevents) im fokussierten isolierten Qt-Testeditor und ein sichtbarer Textblock. Erkennung des Sollsatzes separat fehlgeschlagen. |
| V03-08 | BLOCKIERT | PASS_SCOPED | 12 | Zehn getrennte akustische Diktate, Sollmarker und je ein Final/Mock-Auftrag; native Einfügung und Wortgenauigkeit nicht vollständig. |
| V03-09 | FAIL | PASS_SCOPED | 13 acoustic-long-retest | 209 s, 7 eindeutige Finals und 7 Aufträge, 1 Generation; alter Langfinal-Fehler nicht reproduziert. |
| V03-10 | PASS | PASS | R06 geführt | Während Recording wurde Refresh bestätigt und dieselbe Aktivierungs-ID beibehalten. |
| V03-11 | PASS | PASS | R06 geführt | Hotkey-Cancel beendete offene manuelle und Wake-Aktivierungen vor der Sprache. Kein Final, kein Paste. Aktiver Segmentabriss separat über den Relay geprüft. |
| V03-12 | PASS | PASS | R06 geführt | Der getrennte Finish-Hotkey drainte die Aktivierung als 'finished' und beendete sie im Zustand Idle. |
| V03-13 | BLOCKIERT | PASS_SCOPED | 13 acoustic-trigger-wake | Wake-only: manueller Start wirksam gesperrt. |
| V04-01 | PASS | PASS | E12, E10 | Sessionliste geladen, gescrollt und mehrere auswählbare Namen einschließlich Hey Jarvis gesehen. Die aktuelle lesende V2-Probe bestätigte 25 Einträge bei Katalogrevision 2. |
| V04-02 | PASS | PASS | R06 geführt | Manuell plus 'hey_jarvis' wurden im Produktdialog gewählt und gespeichert. Die neue Verbindung unterstützte beide Auslöser. |
| V04-03 | PASS | PASS | R06 geführt | Gespeichertes Hybridprofil und Verbindungswirkung waren im verbundenen Zustand bestätigt. Der Fehler der Offline-Anzeige ist separat bewertet. |
| V04-04 | BLOCKIERT | PASS_SCOPED | 13, 15 | Vier synthetische Wake-Aufrufe; echter Wake-Satz im korrigierten Quellclient bei Wiederholung technisch erfolgreich und vom Anwender bestätigt. Erster Versuch nicht vollständig erfolgreich. |
| V04-05 | PASS | PASS | R06 geführt | Echte Stimme löste Wake, Segment, Final und genau einen Paste aus. Ein Wort wich ab. |
| V04-06 | PASS | PASS | R06 geführt | Manuelle Kurzaufnahmen und Refresh funktionierten in einer Session mit aktiviertem Wake. |
| V04-07 | BLOCKIERT | PASS_SCOPED | 13 acoustic-trigger-wake | Wake-only: zwei Wake-Finals, manueller Start gesperrt. |
| V04-08 | BLOCKIERT | PASS_SCOPED | 13 acoustic-trigger-manual | Manual-only: akustischer Wake-Stimulus negativ, manuelles Final positiv. |
| V04-09 | PASS | PASS | R06 geführt | Nach dem Wake-Pausenhotkey blieb derselbe positive akustische Stimulus ohne Aktivierung oder Paste. |
| V04-10 | PASS | PASS | R06 geführt | Nach Aufheben der Pause erkannte die verbundene Desktop-EXE das Test-Weckwort und lieferte ein Final, danach gelang auch ein echter Aufruf. |
| V04-11 | BLOCKIERT | PASS_SCOPED | 11, 07 | Native Qt Regression für unbekannte/unverfügbare IDs plus servernahe Ablehnung; Frozen-GUI offen. |
| V04-12 | BLOCKIERT | PASS_SCOPED | 13 acoustic-trigger-wake/hybrid | Je 6 s Idle, gewöhnliche synthetische Sprache und pausierter Wake ohne Fehlaktivierung; längere echte Hintergrundstichprobe offen. |
| V05-01 | PASS | PASS | E03, E04 | Globaler Hotkey registrierte im fremden Notepad-Fenster eine native Betätigung, während die Tray-App im Hintergrund lief. |
| V05-02 | BLOCKIERT | PASS_SCOPED | 19 | Native GUI-Neubelegung gespeichert; echte Registrierung, gezieltes WM_HOTKEY, zwei getrennte reale Akustikfinals/Mock-Aufträge; physische Tastatur/Paste offen. |
| V05-03 | PASS | PASS | E14 | Nach Apply der Ersatzbelegung war der Alt-Hotkey Win32-seitig frei. Strg+Umschalt+Leertaste im fokussierten leeren Editor erzeugte weder ein Hotkey-Ereignis noch eine Activation. |
| V05-04 | PASS | PASS | R06 geführt | Die separate F8-Belegung löste zuerst Finish und nach bestätigtem GUI-Apply Cancel aus. |
| V05-05 | BLOCKIERT | PASS_SCOPED | 07, 13, 09 | Optionslogik automatisiert, Finish/Cancel im früheren Desktoplauf belegt, aktuelle GUI aktive Profilentscheidungen geprüft. |
| V05-06 | PASS | PASS | R06 geführt | F10 pausierte und reaktivierte Wake. Positiver und negativer akustischer Stimulus erfasst. |
| V05-07 | BLOCKIERT | PASS_SCOPED | 11 | Native Qt Overlay sichtbar/unsichtbar per Utility-Funktion; physische Hotkey-Auslösung offen. |
| V05-08 | PASS | PASS | R06 geführt | Der konfigurierte Reinsert-Hotkey wiederholte den Fahrrad-/Garagentext genau einmal, auch während der Netzstörung. |
| V05-09 | FAIL | PASS_SCOPED | 11 native Qt | Korrigierte Meldung nennt beide Rollen und Hotkey; Profil unverändert. |
| V05-10 | BLOCKIERT | PASS_SCOPED | 11, 09 E14 | Doppelte Belegung abgewiesen, Profil unverändert, frühere native Bindungsprüfung; vollständiger Frozen-Gegenlauf offen. |
| V05-11 | PASS | PASS | E14 | Nach GUI-Apply aus waren Primary und Reinsert Win32-seitig registrierbar. Nach GUI-Apply an waren F10 und Reinsert besetzt. Nach Rücknahme war der ursprüngliche Primary wieder besetzt und F10 frei. |
| V06-01 | BLOCKIERT | PASS_SCOPED | 23 | Korrigierter Quellclient, echter ReSpeaker, echtes Final, native Win32-Einfügung in eigenes Windows-Notepad-Dokument; exakter UIA-Readback, Sollmarker und Clipboard-Restore bestätigt. |
| V06-02 | PASS | PASS | R06 geführt | Die Ereignisspur des separaten Qt-Editors belegt den erwarteten Zugsatz und genau einen nativen Paste. |
| V06-03 | PASS | PASS | E06 | Im akustischen Versuch liefen mehrere Realtime-Ergebnisse. Das Editorfeld blieb bis zum Final leer; ein dokumentierter Paste-Job erst beim Final. |
| V06-04 | PASS | PASS | R06 geführt | Fünf ausgewählte, getrennte Aktivierungen mit je einem Final, einem Einfügeversuch und genau einem Editorereignis belegt. Der Reinsert erzeugte die einzige absichtliche Wiederholung. |
| V06-05 | PASS | PASS | R06 geführt | Der vorbereitete Klartextmarker blieb in der Windows-Zwischenablage. Rich-Clipboard war nur nach Zustimmung ausgetauscht worden. |
| V06-06 | BLOCKIERT | PASS_SCOPED | 13, 09 V06-05 | Clipboard-Option in GUI übernommen/gespeichert; frühere Klartext-Restore-Probe. Kein Delay-Editor; native aktuelle Wirkungsprüfung offen. |
| V06-07 | PASS | PASS | R06 geführt | Reinsert erfolgte erst nach dem Hotkey und mit identischem Fingerabdruck zur letzten bekannten Ausgabe. |
| V06-08 | PASS | PASS | R06 geführt | Beim Reinsert blieb die Tabelle mit Transkripten bei 12 Einträgen. Die Einfügeversuche stiegen auf 13. |
| V06-09 | PASS | PASS | R06 geführt | Nach Aktualisieren zeigte der echte Verlaufsdialog 12 Zeitwerte in absteigender Reihenfolge. |
| V06-10 | BLOCKIERT | PASS_SCOPED | 13 native-desktop-history-retest-2 | Gezielte Wiedereinfügung per tatsächlichem Dialog; exakt ein Mock-Auftrag für richtige ID. |
| V06-11 | BLOCKIERT | PASS_SCOPED | 13 native-desktop-history-retest-2 | Bestätigung und Löschung nur eines synthetischen Testeintrags, andere bleiben. |
| V06-12 | BLOCKIERT | N/A | 13, 03 Checkliste | Schalter nicht angeboten; Kriterium ausdrücklich bedingt. Keine Aussage zur Wirkung eines optionalen YAML-Schalters. |
| V06-13 | BLOCKIERT | PASS_SCOPED | 13 native-desktop-history-retest-2 | Bestätigung und Leeren nur des isolierten synthetischen Verlaufs. |
| V07-01 | PASS | PASS | E04 | Runtime erkennt ReSpeaker-USB-Controller. LEFX-Dienst startet mit 12 LEDs, 30 FPS und 36 Effekten. `output available (respeaker)` ohne dauerhaften Initialisierungsfehler. Keine visuelle Hardwarewertung. |
| V07-02 | PASS | PASS | R06 geführt | Vor Aufnahme beobachtete der Benutzer grün pulsierenden Idle-Ring. |
| V07-03 | PASS | PASS | R06 geführt | Der Benutzer sah das Aktivierungsaufblitzen und einen rotierenden Leuchtpunkt während der Aufnahme. |
| V07-04 | PASS | PASS | R06 geführt | Nach Aufnahme beobachtete der Benutzer die Rückkehr zum grün pulsierenden Idle-Muster. |
| V07-05 | BLOCKIERT | PASS_SCOPED | 15 | Final und Cancel real durchlaufen; Benutzer bestätigt LED-Beobachtungen. Physischer Fehlerzustand nicht geprüft. |
| V07-06 | BLOCKIERT | PASS_SCOPED | 15 | Wake-Pause real bestätigt, Benutzer bestätigt LED-Beobachtungen aus dem getrennten Hardwarelauf. |
| V07-07 | BLOCKIERT | PASS_SCOPED | 19 | Native GUI-Helligkeit geändert, realer USB-Sink nach Apply verfügbar; Mapping SET_OUTPUT auf Wartephase technisch bestätigt; physische Sichtwirkung offen. |
| V07-08 | BLOCKIERT | PASS_SCOPED | 15, 17 | Anwender bestätigt ausdrücklich passende Töne bei Aufnahmebeginn, Abschluss und Abbruch. Weitere Ereignisklassen und Duplikate nicht separat gemessen. |
| V07-09 | BLOCKIERT | PASS_SCOPED | 19 | QSoundEffect reale Datei/Volume .25/Ready, Sounds-off und Folgediktate erfolgreich; Sound-on-Marker teils abweichend, neue Hörwirkung und kausaler Vergleich offen. |
| V07-10 | BLOCKIERT | PASS_SCOPED | 12, 13 | ReSpeaker/Transkription in realen Akustiktests bei deaktiviertem LED-Controller. |
| V07-11 | BLOCKIERT | PASS_SCOPED | 15 | Overlay-Aufnahme/Abschluss und echte Wake-Eingabe erfolgreich beobachtet. Fehler- und vollständige Pausenanzeige offen. |
| V08-01 | PASS | PASS | E12, E14 | Lokale Hotkey-Werte über die GUI geändert und erfolgreich übernommen. Dauerhafte Triggerwahl und aktuelle Wirksamkeit wurden getrennt gezeigt. Manueller Trigger blieb wirksam, Wake blieb aus. |
| V08-02 | PASS | PASS | E12 | Sessionansicht zeigte Angefordert, Wirksam, Serverstandard, Schema-Startwert und Wirksam ab für die Final-Instanz. Session-, Server- und Katalogrevision waren sichtbar. |
| V08-03 | PASS | PASS | E12 | Sessionparameter Warten auf Eingabeschluss auf 5200 ms übernommen. Revision 1 und Requested/Effective 5200 bei Serverstandard 5000 und Serverrevision 0. Anschließend Rücknahme auf 5000 mit Sessionrevision 2. |
| V08-04 | PASS | PASS | E12 | Wake-Rauschunterdrückung und Sprachschwelle waren in Session ausgegraut, mit Hinweis auf Admin-Serverdefaults. UI unterschied Policy Nächste Verbindung und Änderungsrecht. |
| V08-05 | FAIL | PASS_SCOPED | 11 | Korrigiertes Reload erhält ungespeicherten Sessionentwurf; native Qt echter Server. |
| V08-06 | BLOCKIERT | PASS_SCOPED | 13 native-active-apply-retest-2 | Aktive Eingabe, kein vorausgewähltes destruktives Apply; Cancel/Finish/Defer mit echter Session, kontrollierter Null-PCM. |
| V08-07 | BLOCKIERT | PASS_SCOPED | 13 native-device-preview-retest-2 | GUI-Wechsel auf ReSpeaker und Standardgerät, je erfolgreiches reales akustisches Diktat. |
| V08-08 | BLOCKIERT | PASS_SCOPED | 11 | Native Qt Overlay-Position/Opazität/Sichtbarkeit und Persistenz geprüft. |
| V08-09 | BLOCKIERT | PASS_SCOPED | 11, 13 | Clipboard-Option übernommen/persistiert, native Paste-Wirkung aktueller Kandidat offen. |
| V08-10 | BLOCKIERT | PASS_SCOPED | 13 | Verlaufskapazität wirksam in Runtime übernommen und persistiert, Aufbewahrungsgrenze nicht durch Überschreitung gemessen. |
| V08-11 | BLOCKIERT | PASS_SCOPED | 19 | Sound- und LED-Zuordnungen geändert, echte Zustandsereignisse, realer Soundplayer und USB-Sink; physische Bewertung offen. |
| V08-12 | PASS | PASS | E13 | Logs-und-Diagnose-Fenster über lokale GUI geöffnet. Suche nach Audio capture started reduzierte die Anzeige auf drei datierte Einträge, darunter den Geräte-Apply um 00:56:50 MEZ. |
| V08-13 | BLOCKIERT | PASS_SCOPED | 11, 13 | Persistenz in frischem Prozess gelesen, Frozen-Start/Shutdown; Laufzeitpause-Reset bei Neustart offen. |
| V08-14 | FAIL | PASS_SCOPED | 11 | Präzise Konfliktmeldung, keine Änderung am Profil. |
| V08-15 | FAIL | PASS_SCOPED | 11, 13 | Korrigierte Cursor-Isolation; gemeinsame Cursor-Datei bei neuen Tests unverändert. Historische Änderung nicht rückwirkend wiederhergestellt. |
| V08-16 | PASS | PASS | E12 | Serververwaltung zeigte ohne Admin-Verifikation Gesperrt. Wunschfelder und Schaltfläche für Serverdefaults waren deaktiviert. Key-Feld leer, keine Eingabe und keine Mutation. |
| V08-17 | N/A | PASS_SCOPED | 21 | Autorisierter gültiger Schlüssel im nativen Clientdialog verifiziert; Editoren entsperrt; keine Änderung bei Verifikation. |
| V08-18 | N/A | PASS_SCOPED | 21 | Echter Windows Credential Manager mit isoliertem synthetischem Test-Origin: Save/Read/Delete erfolgreich; reale Credentials unverändert. Kein realer UI-Vault-Roundtrip. |
| V08-19 | N/A | PASS_SCOPED | 21 | Echter Clientdialog 3000 -> 3100 ms, Revision 0 -> 1, neue Session effektiver Wert bestätigt. |
| V08-20 | N/A | PASS_SCOPED | 21 | Echter Clientdialog 3100 -> 3000 ms, Revision 1 -> 2, sämtliche Requested-/Effective-Werte wie zuvor, neue Session bestätigt. |
| V08-21 | N/A | PASS_SCOPED | 21 | Ungültiger Key sperrt UI; falscher Key und Stale Revision serverseitig verweigert; Reconnect invalidiert Adminfreigabe. |
| V09-01 | FAIL | PASS_SCOPED | 11 | Offline-Trigger unbestätigt, Pausenwunsch erhalten, Live-Reconnect; erneute physische Desktopprüfung offen. |
| V09-02 | PASS | PASS | R06 geführt | Zwei geplante Schnitte führten zu neuen V2-Session-IDs und READY ohne V1-Fallback. |
| V09-03 | PASS | PASS | R06 geführt | Nach aktivem Abriss erschien der kontrollierte Zugsatz in der neuen V2-Session einmal vollständig. Das Folgediktat nach dem Idle-Schnitt war verkürzt. |
| V09-04 | FAIL | PASS_SCOPED | 11 | Korrigierte Offline-Anzeige, kein falscher effektiver Trigger in Offline-Probe; alte Abrissprobe bleibt historisch. |
| V09-05 | PASS | PASS | R06 geführt | Aktivierter Schnitt wechselte Generation und Session. Alte Aktivierung erzeugte keine Einfügung. Die alte Steuerabsicht war im autonomen Kontrolltest abgewiesen worden. |
| V09-06 | PASS | PASS | R06 geführt | Mute blockierte zuverlässig den Hotkey. Der USB-Wiederanlauf lieferte ein Folgediktat ohne Neustart. |
| V09-07 | BLOCKIERT | PASS_SCOPED | 13 frozen-invalid-endpoint / frozen-valid-desktop | Ungültiger Pfad: Exit 5, klarer Logfehler, keine UI-Blockade; gültiger Pfad separat Ready. Endanwender-Fehlerdarstellung offen. |
| V09-08 | FAIL | PASS_SCOPED | 11, 13 | Korrigierte EXE Exit 0 via WM_QUIT, Single Instance, keine _MEI-Reste; Langlauf mit realem Gerät/LED/Hotkeys und Tray-Quit offen. |
| V09-09 | PASS | PASS | E08 | Abschluss-Stichprobe aus 53 Clientlogzeilen und 370 Beobachtungsdatensätzen. Null Treffer auf Secret-Muster, Secretfelder und Transkriptfelder. Aussage auf geprüften Lauf und Felder begrenzt. |
| V10-01 | BLOCKIERT | BLOCKIERT | R06 geführt | Über 33 Minuten realer Desktopbetrieb mit Geräteeingriffen und mehreren Eingaben. Overlay-Sichtwirkung und der geforderte vollständige Normalbetrieb blieben offen. |
| V10-02 | BLOCKIERT | PASS_SCOPED | 12 | 10/10 getrennte akustische Kurzfinals/Mock-Aufträge, nicht repräsentativer Frozen-Paste-Langlauf. |
| V10-03 | FAIL | PASS_SCOPED | 13 | 209 s Langdiktat, sieben Finals, kein Hänger; nicht im vollständigen 30–60-min-Frozen-Lauf. |
| V10-04 | BLOCKIERT | PASS_SCOPED | 23 | Echter Fokuswechsel Notepad -> eigene Qt-Editoranwendung, je ein reales Final und native Einfügung, erstes Ziel unverändert; Clipboard in beiden Fällen wiederhergestellt. |
| V10-05 | BLOCKIERT | PASS_SCOPED | 12, 13 | Akustische Serien mit Sollmarkern, gezielte Wake-Negativtests, Langfinal; repräsentativer Dauertest offen. |
| V10-06 | BLOCKIERT | PASS_SCOPED | 19 | Korrigierte Frozen-EXE mit realer Hardware 120s Idle: private MiB 464,527 -> 464,699; mittlere CPU 4,466 Prozent eines Kerns; vollständiger aktiver Langlauf fehlt. |
| V10-07 | FAIL | ACCEPTED_RISK | 19, 21 | Historische Abrisse ausdrücklich durch Auftraggeber als nicht releaseblockierend eingestuft; alter Fallback-Log korrigiert, 120s Frozen-Idle ohne Reconnect. Langzeitprüfung separat offen. |
| V10-08 | BLOCKIERT | PASS_SCOPED | 11, 13 | Frozen normaler Start und sauberer Exit, persistierte Einstellungen readback; kompletter Hardware-/History-/Hotkey-Restart offen. |
| V10-09 | FAIL | PASS_SCOPED | 11, 13 | Korrigierte gemeinsame Cursor-Isolation; historische Cursor-Veränderung bleibt dokumentiert; kein produktiver Server geändert. |
| F01 | BLOCKIERT | PASS_SCOPED | 11, 13 | Frozen-Normalstart/Ready/Single Instance, native Qt Menüs, tatsächlicher Explorer-Doppelklick/Tray-Hover offen. |
| F02 | PASS | PASS | R06 geführt | Der einmalig kontrolliert wiederholte echte Satz wurde über den ReSpeaker erfasst und eingefügt. |
| F03 | PASS | PASS | R06 geführt | Korrektes manuelles Sollfinal genau einmal. Finish, Refresh und Cancel im offenen Aktivierungszustand nachgewiesen. |
| F04 | BLOCKIERT | PASS_SCOPED | 13, 15 | Akustische Triggerkombinationen plus erfolgreicher echter Wake-Aufruf im Quellclient; vollständiges Frozen-E2E weiterhin offen. |
| F05 | PASS | PASS | R06 geführt | Native Hotkeys und absichtliches Reinsert praktisch belegt. Die vorherige R06-Gegenprobe bestätigte unveränderte Bindungen nach konflikthaftem Apply. |
| F06 | BLOCKIERT | PASS_SCOPED | 15, 17 | LED-Ablauf, Töne bei Aufnahmebeginn/Abschluss/Abbruch, Overlay und echter Wake-Satz vom Anwender bestätigt. Fehlerzustand, weitere Tonklassen, geänderte Mappings und Frozen-Gesamtprüfung offen. |
| F07 | BLOCKIERT | PASS_SCOPED | 11, 13 | Draft-Reload, Duplicate, aktive Apply-Optionen, lokale Einstellungen und Gerätediktate korrigiert/geprüft. |
| F08 | PASS | PASS | R06 geführt | Der isolierte Netzwerk- und der physische USB-Abriss erholten sich ohne doppelten Textnachtrag. Die irreführende Offline-Anzeige bleibt als eigener Fehler. |
| F09 | FAIL | PASS_SCOPED | 12, 13 | 10/10 akustische Kurzserie und 209-s-Langfinal auf korrigiertem Quellclient; repräsentativer Frozen-Endurance, ursprüngliche spontane Verluste nicht vollständig geklärt. |
| F10 | BLOCKIERT | PASS_SCOPED | 21 | 25/25 technische Checks am realen Final-Origin: Berechtigung, Änderung, Wirkung, Rücksetzung, Negativproben, isolierter Vault. Admin bleibt Releaseumfang. |
| F11 | PASS | PASS | E05, E06, E12, E14 | Befunde und Testblockaden mit Schweregrad, Reproduktion und offenem Status im separaten Befundbericht dokumentiert. |
| F12 | BLOCKIERT | USER_APPROVED | 21 | Auftraggeber bestätigt Redistributionsfreigabe ausdrücklich als geklärt und nicht releaseblockierend. |

## Bilanz (136 Kriterien; die 3 Entscheidungsoptionen separat)

| Status | Anzahl |
|---|---:|
| PASS | 65 |
| N/A | 3 |
| PASS_SCOPED | 65 |
| BLOCKIERT | 1 |
| ACCEPTED_RISK | 1 |
| USER_APPROVED | 1 |

## Entscheidung

| Option | Status |
|---|---|
| GO für nächste Testphase | NOT_RUN |
| GO mit Auflagen | NOT_RUN |
| NO-GO / BLOCKIERT | PASS – vollständige Releaseabnahme noch nicht abgeschlossen |
