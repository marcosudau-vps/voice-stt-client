# R06 · aktualisierte Matrix aller 139 Einträge

Die 136 Prüfkriterien und drei Entscheidungsoptionen sind vollständig erfasst. Die Basisbelege zum 22.11.2026 und die autonomen Zusatzbelege bleiben verlinkt. Neu bewertete Einträge tragen den Bezug „R06 geführt“.

- [Praktischer Basislauf](04_COMPUTER_USE_ERGEBNIS.md)
- [Autonome Restprüfung mit 267 gezielten Tests](07_AUTONOME_RESTPRUEFUNG_2026-11-23.md)
- [Geführter Desktop-Nachlauf](08_GEFUEHRTER_DESKTOP_NACHLAUF_2026-11-23.md)

| Status | Kriterien |
|---|---:|
| PASS | 65 |
| FAIL | 12 |
| BLOCKIERT | 51 |
| NOT_RUN | 1 |
| N/A | 7 |

| ID | Status | Beleg | Befund |
|---|---|---|---|
| V00-01 | PASS | E01 | Alle vier geforderten Paketbestandteile vorhanden. EXE 77.414.876 Byte, SHA-256 stimmt. |
| V00-02 | PASS | E01, E02 | Profil exakt /ws/v2 und Health auf derselben Final-Testdomain. HTTP 200, ready=true, sttReady=true. Separater aktueller V2-Handshake liefert erwarteten Server-Commit. |
| V00-03 | N/A | E01 | Prozessinventar vor Start ohne Altclient und ohne laufendes Altclient-Diktat. Altclient-Dateien blieben während der Vorbereitung am Ort. |
| V00-04 | N/A | E01 | Kein aktiver Altclient zum regulären Beenden. Altclient wurde für diese Prüfung nicht gestartet. |
| V00-05 | PASS | E03 | Computer Use öffnete mit Strg+T einen leeren Notepad-Tab und fokussierte sein Textfeld. Zweites, eigenständiges Qt-Textfeld anschließend bereitgestellt. |
| V00-06 | PASS | E01, E04 | Vor Start Profilkopie und SHA-256 gesichert. Windows und PortAudio identifizierten bei Systemstandard den ReSpeaker-Eingang; Laufzeitspur meldet 16 kHz und 40-ms-Frames. |
| V01-01 | NOT_RUN | E04 | Verifizierter Launcher lief über die Shell, da der Computer-Use-Skill den indirekten Start von CMD-Skripten in Explorer untersagt. Onefile-Prozess und betriebsbereite Qt-/Core-Initialisierung beobachtet. Der geforderte Doppelklick blieb offen. |
| V01-02 | BLOCKIERT | B03, E04 | Reguläres Tray-Beenden durch Anwender bestätigt. Computer Use listet die Shell-Taskleiste nicht als Ziel. Symbol, Status, Tooltip und Menü konnten nicht vollständig direkt abgenommen werden. |
| V01-03 | PASS | E02, E04 | Die Desktop-EXE erreichte in zwei Läufen V2-Transportzustand ready. Domain aus geprüftem Profil, Soll-Server-Commit aus gesonderter zeitnaher V2-Probe. |
| V01-04 | PASS | E01, E02, E04 | Desktopspur zeigt V2-Verbindungsaufbau, Bootstrap und Ready. Exakter /ws/v2-Endpunkt aus Launcher-Profil und der aktuellen Wire-Probe. V2-Runtime akzeptiert für die Diktatverbindung ausschließlich /ws/v2. |
| V01-05 | PASS | E12 | Der Benutzer öffnete das V2-Hauptfenster aus dem Tray. Computer Use öffnete den lokalen Einstellungsdialog, schloss ihn und öffnete ihn erneut. Das wiedergeöffnete Fenster hatte einen neuen Handle und der Hauptdialog blieb bedienbar. |
| V01-06 | PASS | E12 | Die Register Lokale Trigger & Bedienung, Session und Serververwaltung wurden in der laufenden EXE aufgerufen und inhaltlich geprüft. |
| V01-07 | PASS | E13 | Alle fünf lokalen Register geöffnet. Audio/Geräte, Verlauf, Clipboard in Allgemein, Darstellung/Feedback und Logging/Diagnose waren zugänglich. |
| V01-08 | BLOCKIERT | E12, E13 | Drei V2- und fünf lokale Register sichtbar bedienbar, Listen und Tabellen vertikal gescrollt. Einige lange Tabellenwerte sind im Standardviewport abgeschnitten und horizontal scrollbar. Vollständige Tooltip- und Skalierungsmatrix fehlt. |
| V01-09 | BLOCKIERT | B03 | Kein targetierbares Overlay und keine belegte sichtbare Positions-/Sichtbarkeitsänderung. |
| V01-10 | PASS | E04 | Zweiter Start mit demselben Launcher. Runtime protokolliert „RealtimeSTT is already running; second instance exits“. Bestehendes Onefile-PID-Paar blieb erhalten. Ablehnung erfolgt vor zweitem Qt-/Hotkey-Start. |
| V02-01 | PASS | E11, E13 | Windows zeigte den XVF3800 als Standardeingang. Die Client-Auswahlliste zeigte den vollständigen Gerätenamen. Windows bestätigte VID 2886 / PID 001A. |
| V02-02 | PASS | E13, E04 | Vollständigen ReSpeaker-Eintrag in der lokalen GUI ausgewählt und mit Apply übernommen. Laufzeitgerät PortAudio 9. Nach der Prüfung wieder Systemstandard und ursprüngliches YAML. |
| V02-03 | PASS | E13, E04 | Der Stream startete nach Apply mit dem explizit ausgewählten ReSpeaker und 16 kHz neu. Die lokale Drei-Sekunden-Prüfung meldete RMS 77,3 und Peak 1,19 %. Keine Audio-Dauerstörung. |
| V02-04 | PASS | R06 geführt | Wiederholter menschlicher Weckruf und frei gesprochener Testsatz erzeugten ein zugeordnetes Final. |
| V02-05 | BLOCKIERT | B02 | Kein der Sollsprache zuordenbares Diktatpaar mit kurzen Pausen und mehreren Sätzen. |
| V02-06 | PASS | R06 geführt | Hardware-Mute stoppte Capture und blockierte den Hotkey. Aufheben öffnete den ReSpeaker-Stream wieder. Der erste Folgereiz löste kein Recording aus. |
| V02-07 | PASS | R06 geführt | Windows-Geräteliste, Capture und LED-Transport zeigten Verlust und Rückkehr am gleichen Port. |
| V02-08 | PASS | R06 geführt | Nach Rückkehr kam ein zuordenbarer Testtext genau einmal an. Ein Wort wich ab. |
| V02-09 | BLOCKIERT | B03 | Auswahl eines ungültigen Eingangs und Rückstellung erfordern den lokalen Gerätedialog. |
| V03-01 | BLOCKIERT | B03, E04 | Manuelle Aktivierung in der Ausgangskonfiguration und in der Laufzeit belegt. GUI-Übernahme mit Reconnect blieb offen. |
| V03-02 | PASS | E03, E04 | Strg+Umschalt+Leertaste per Computer Use im leeren Notepad-Tab. Genau ein Hotkey-Ereignis und eine eindeutige manuelle Activation mit Aufnahmebeginn. |
| V03-03 | PASS | R06 geführt | Der synthetisch gesprochene Zugsatz kam vollständig über den ReSpeaker an und wurde genau einmal eingefügt. |
| V03-04 | BLOCKIERT | B02, E06 | Realtime-Ereignisse und bis zum Final leerer Editor beobachtet. Sichtbare Realtime-Vorschau des Sollsatzes bleibt offen. |
| V03-05 | PASS | R06 geführt | Der separat konfigurierte Finish-Hotkey schloss die offene Folgephase mit 'finished' und Idle. |
| V03-06 | PASS | R06 geführt | Der vollständige Sollsatz erschien im Testeditor und als Eintrag im lokalen Verlauf. |
| V03-07 | PASS | E06 | Genau ein nativer `command_sent`-Job (vier Keyevents) im fokussierten isolierten Qt-Testeditor und ein sichtbarer Textblock. Erkennung des Sollsatzes separat fehlgeschlagen. |
| V03-08 | BLOCKIERT | R06 geführt | Zuordenbare Kurzfinals vorhanden. Eine Folge von drei vollständigen, jeweils eindeutig getrennten Kurzaufnahmen fehlt. |
| V03-09 | FAIL | R06 geführt | 145 Sekunden akustische Wiedergabe. Bis zum kontrollierten Sitzungswechsel kein Final für diese Aktivierung. |
| V03-10 | PASS | R06 geführt | Während Recording wurde Refresh bestätigt und dieselbe Aktivierungs-ID beibehalten. |
| V03-11 | PASS | R06 geführt | Hotkey-Cancel beendete offene manuelle und Wake-Aktivierungen vor der Sprache. Kein Final, kein Paste. Aktiver Segmentabriss separat über den Relay geprüft. |
| V03-12 | PASS | R06 geführt | Der getrennte Finish-Hotkey drainte die Aktivierung als 'finished' und beendete sie im Zustand Idle. |
| V03-13 | BLOCKIERT | B03 | Manuellen Trigger deaktivieren und Sperre beobachten erfordert funktionierende GUI-Übernahme. |
| V04-01 | PASS | E12, E10 | Sessionliste geladen, gescrollt und mehrere auswählbare Namen einschließlich Hey Jarvis gesehen. Die aktuelle lesende V2-Probe bestätigte 25 Einträge bei Katalogrevision 2. |
| V04-02 | PASS | R06 geführt | Manuell plus 'hey_jarvis' wurden im Produktdialog gewählt und gespeichert. Die neue Verbindung unterstützte beide Auslöser. |
| V04-03 | PASS | R06 geführt | Gespeichertes Hybridprofil und Verbindungswirkung waren im verbundenen Zustand bestätigt. Der Fehler der Offline-Anzeige ist separat bewertet. |
| V04-04 | BLOCKIERT | R06 geführt | Ein gültiger echter Wake-Aufruf nach positiver Vorprobe. Die erste Probe während der Pause bleibt ungewertet. Mehrere gültige menschliche Aufrufe fehlen. |
| V04-05 | PASS | R06 geführt | Echte Stimme löste Wake, Segment, Final und genau einen Paste aus. Ein Wort wich ab. |
| V04-06 | PASS | R06 geführt | Manuelle Kurzaufnahmen und Refresh funktionierten in einer Session mit aktiviertem Wake. |
| V04-07 | BLOCKIERT | B02, B03 | Kein erfolgreicher Wake-only-Lauf mit positivem Wake- und negativem Manual-Test. |
| V04-08 | BLOCKIERT | B02 | Ausgangsprofil ist Manual-only. Kontrollierter gesprochener Wake-Negativversuch blieb unbelegt. |
| V04-09 | PASS | R06 geführt | Nach dem Wake-Pausenhotkey blieb derselbe positive akustische Stimulus ohne Aktivierung oder Paste. |
| V04-10 | PASS | R06 geführt | Nach Aufheben der Pause erkannte die verbundene Desktop-EXE das Test-Weckwort und lieferte ein Final, danach gelang auch ein echter Aufruf. |
| V04-11 | BLOCKIERT | B03 | Ungültige Wake-ID wurde im Produktdialog noch nicht getestet. |
| V04-12 | BLOCKIERT | B02, B04 | Keine qualifizierte Wake-Beobachtung in Stille und definierten Hintergrundgesprächen. |
| V05-01 | PASS | E03, E04 | Globaler Hotkey registrierte im fremden Notepad-Fenster eine native Betätigung, während die Tray-App im Hintergrund lief. |
| V05-02 | BLOCKIERT | E14, B02 | Freier F10-Hotkey per GUI gespeichert und Win32-Registrierung nachgewiesen. Aktive Diktatauslösung über die neue Belegung blieb wegen der unkontrollierten Audioquelle offen. |
| V05-03 | PASS | E14 | Nach Apply der Ersatzbelegung war der Alt-Hotkey Win32-seitig frei. Strg+Umschalt+Leertaste im fokussierten leeren Editor erzeugte weder ein Hotkey-Ereignis noch eine Activation. |
| V05-04 | PASS | R06 geführt | Die separate F8-Belegung löste zuerst Finish und nach bestätigtem GUI-Apply Cancel aus. |
| V05-05 | BLOCKIERT | B03 | Optionsmatrix und praktische Wirkung von Finish und Cancel in der GUI offen. |
| V05-06 | PASS | R06 geführt | F10 pausierte und reaktivierte Wake. Positiver und negativer akustischer Stimulus erfasst. |
| V05-07 | BLOCKIERT | B03 | Overlay-Hotkey im Ausgangsprofil leer. Keine beobachtete Umschaltung. |
| V05-08 | PASS | R06 geführt | Der konfigurierte Reinsert-Hotkey wiederholte den Fahrrad-/Garagentext genau einmal, auch während der Netzstörung. |
| V05-09 | FAIL | E14, B09 | Duplikat wurde technisch abgewiesen. Die Meldung verweist auf Reparatur eines migrierten Profils und benennt weder den doppelten Hotkey noch die betroffenen Felder. |
| V05-10 | BLOCKIERT | E14, B02 | Unveränderter YAML-Hash, nach erneutem Einlesen Primärhotkey und ursprünglicher leerer Sekundärslot, vorherige native Bindungen weiter belegt. Wiederholtes Auslösen eines Diktats bzw. Reinsert des unbekannten Finals bleibt offen. |
| V05-11 | PASS | E14 | Nach GUI-Apply aus waren Primary und Reinsert Win32-seitig registrierbar. Nach GUI-Apply an waren F10 und Reinsert besetzt. Nach Rücknahme war der ursprüngliche Primary wieder besetzt und F10 frei. |
| V06-01 | BLOCKIERT | B02, E03 | Windows-Editor diente als bestätigtes Aktivierungsziel. Kein kontrolliertes Final mit Paste in Notepad nachgewiesen. |
| V06-02 | PASS | R06 geführt | Die Ereignisspur des separaten Qt-Editors belegt den erwarteten Zugsatz und genau einen nativen Paste. |
| V06-03 | PASS | E06 | Im akustischen Versuch liefen mehrere Realtime-Ergebnisse. Das Editorfeld blieb bis zum Final leer; ein dokumentierter Paste-Job erst beim Final. |
| V06-04 | PASS | R06 geführt | Fünf ausgewählte, getrennte Aktivierungen mit je einem Final, einem Einfügeversuch und genau einem Editorereignis belegt. Der Reinsert erzeugte die einzige absichtliche Wiederholung. |
| V06-05 | PASS | R06 geführt | Der vorbereitete Klartextmarker blieb in der Windows-Zwischenablage. Rich-Clipboard war nur nach Zustimmung ausgetauscht worden. |
| V06-06 | BLOCKIERT | B03 | Einfügeverzögerung wurde nicht über die GUI verändert und auf Wirkung geprüft. |
| V06-07 | PASS | R06 geführt | Reinsert erfolgte erst nach dem Hotkey und mit identischem Fingerabdruck zur letzten bekannten Ausgabe. |
| V06-08 | PASS | R06 geführt | Beim Reinsert blieb die Tabelle mit Transkripten bei 12 Einträgen. Die Einfügeversuche stiegen auf 13. |
| V06-09 | PASS | R06 geführt | Nach Aktualisieren zeigte der echte Verlaufsdialog 12 Zeitwerte in absteigender Reihenfolge. |
| V06-10 | BLOCKIERT | B02, B03 | Kein eindeutig qualifizierter Historieneintrag für gezielte Wiedereinfügung. |
| V06-11 | BLOCKIERT | B02, B05 | Kein ausschließlich zu diesem Test erzeugter, eindeutig unbedenklicher Eintrag. UI-Datenlöschung braucht zudem eine Bestätigung unmittelbar vor der Aktion. |
| V06-12 | BLOCKIERT | B02, B03 | GUI-Umschaltung der Historie und kontrollierter Final-Paste nach Umschaltung fehlen. |
| V06-13 | BLOCKIERT | B02, B05 | Keine vorher freigegebenen Testdaten im Verlauf. UI-Datenlöschung braucht Bestätigung unmittelbar vor der Aktion. |
| V07-01 | PASS | E04 | Runtime erkennt ReSpeaker-USB-Controller. LEFX-Dienst startet mit 12 LEDs, 30 FPS und 36 Effekten. `output available (respeaker)` ohne dauerhaften Initialisierungsfehler. Keine visuelle Hardwarewertung. |
| V07-02 | PASS | R06 geführt | Vor Aufnahme beobachtete der Benutzer grün pulsierenden Idle-Ring. |
| V07-03 | PASS | R06 geführt | Der Benutzer sah das Aktivierungsaufblitzen und einen rotierenden Leuchtpunkt während der Aufnahme. |
| V07-04 | PASS | R06 geführt | Nach Aufnahme beobachtete der Benutzer die Rückkehr zum grün pulsierenden Idle-Muster. |
| V07-05 | BLOCKIERT | B04 | Kein physischer Vergleich der LED-Muster für Final, Cancel und Fehler. |
| V07-06 | BLOCKIERT | B03, B04 | Keine ausgelöste Laufzeitpause mit sichtbarer, zuordenbarer Rückmeldung. |
| V07-07 | BLOCKIERT | B04 | Helligkeit/Farbe können ohne physische Sicht auf den Ring nicht wirksam abgenommen werden. |
| V07-08 | BLOCKIERT | R06 geführt | Töne passten laut physischer Stichprobe. Individuelle Zuordnung und Duplikate je Ereignisklasse sind unbelegt. |
| V07-09 | BLOCKIERT | B04 | Weder wahrnehmbare Lautstärkewirkung noch Auswirkung auf das Aufnahmesignal belegt. |
| V07-10 | BLOCKIERT | B02, B03 | Kein deaktivierter LED-Controller in Kombination mit qualifiziertem Mikrofon-Final. |
| V07-11 | BLOCKIERT | B03 | Aufnahme-, Warte-, Abschluss-, Fehler- und Pausenanzeigen wurden nicht als vollständige visuelle Folge beobachtet. |
| V08-01 | PASS | E12, E14 | Lokale Hotkey-Werte über die GUI geändert und erfolgreich übernommen. Dauerhafte Triggerwahl und aktuelle Wirksamkeit wurden getrennt gezeigt. Manueller Trigger blieb wirksam, Wake blieb aus. |
| V08-02 | PASS | E12 | Sessionansicht zeigte Angefordert, Wirksam, Serverstandard, Schema-Startwert und Wirksam ab für die Final-Instanz. Session-, Server- und Katalogrevision waren sichtbar. |
| V08-03 | PASS | E12 | Sessionparameter Warten auf Eingabeschluss auf 5200 ms übernommen. Revision 1 und Requested/Effective 5200 bei Serverstandard 5000 und Serverrevision 0. Anschließend Rücknahme auf 5000 mit Sessionrevision 2. |
| V08-04 | PASS | E12 | Wake-Rauschunterdrückung und Sprachschwelle waren in Session ausgegraut, mit Hinweis auf Admin-Serverdefaults. UI unterschied Policy Nächste Verbindung und Änderungsrecht. |
| V08-05 | FAIL | E12, B08 | Explizites Reload verwarf ungespeicherte Sessionentwürfe 5200 und 5300 ms zweimal still. Die Oberfläche zeigte danach wieder 5000 ms und nur Serverwerte geladen. |
| V08-06 | BLOCKIERT | B03 | Kein GUI-Apply mit aktiver Testaufnahme und sichtbarer Optionsauswahl. |
| V08-07 | BLOCKIERT | B02, B03 | Kein GUI-Gerätewechsel mit anschließendem kontrolliertem Diktat. |
| V08-08 | BLOCKIERT | B03 | Sichtbare Positions-, Transparenz- oder Sichtbarkeitsänderung fehlt. |
| V08-09 | BLOCKIERT | B02, B03 | Keine GUI-Änderung und Wirkungsmessung von Clipboard/Textinjektion. |
| V08-10 | BLOCKIERT | B02, B03 | Keine GUI-Änderung der Historieneinstellungen mit messbarer Wirkung. |
| V08-11 | BLOCKIERT | B03, B04 | Keine geänderten Zuordnungen mit überprüfter physischer Rückmeldung. |
| V08-12 | PASS | E13 | Logs-und-Diagnose-Fenster über lokale GUI geöffnet. Suche nach Audio capture started reduzierte die Anzeige auf drei datierte Einträge, darunter den Geräte-Apply um 00:56:50 MEZ. |
| V08-13 | BLOCKIERT | B03, E04 | Regulärer Ausstieg und Start mit identischem YAML belegt. Persistenzänderung und Rücksetzen von Laufzeitpausen fehlen. |
| V08-14 | FAIL | E14, B09 | Ungültige Doppelbelegung abgelehnt und YAML-Hash gleich. Die sichtbare Migrationsmeldung war für die eingegebene Doppelbelegung nicht konkret genug. |
| V08-15 | FAIL | B01, E05 | Erster Lauf schrieb trotz abgesetztem Profil den gemeinsamen Event-Cursor unter LOCALAPPDATA. Neue Bindung Final-Host /ws/logs, Protokoll 2. Altclient-Konfigurationsdatei zeigt keine Änderung im Prüfzeitraum. Der frühere Cursorinhalt liegt nicht als Backup vor. |
| V08-16 | PASS | E12 | Serververwaltung zeigte ohne Admin-Verifikation Gesperrt. Wunschfelder und Schaltfläche für Serverdefaults waren deaktiviert. Key-Feld leer, keine Eingabe und keine Mutation. |
| V08-17 | N/A | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-18 | N/A | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-19 | N/A | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-20 | N/A | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V08-21 | N/A | B05 | Außerhalb des ausdrücklich autorisierten Prüfumfangs. Eine Freigabe mit geschützter Adminverwaltung bleibt offen. |
| V09-01 | FAIL | R06 geführt | Der isolierte Idle-Abriss ging in Backoff und erholte sich. Bei erneut beobachtetem Verbindungsabriss behauptete der Bedienungsdialog weiterhin eine wirksame Verbindung. |
| V09-02 | PASS | R06 geführt | Zwei geplante Schnitte führten zu neuen V2-Session-IDs und READY ohne V1-Fallback. |
| V09-03 | PASS | R06 geführt | Nach aktivem Abriss erschien der kontrollierte Zugsatz in der neuen V2-Session einmal vollständig. Das Folgediktat nach dem Idle-Schnitt war verkürzt. |
| V09-04 | FAIL | R06 geführt | Abriss 75 ms nach Recording-Start erzeugte keinen unerwünschten Paste. Der sichtbar geprüfte Triggerdialog zeigte beim zweiten ungeplanten Verbindungsverlust einen irreführenden Zustand. |
| V09-05 | PASS | R06 geführt | Aktivierter Schnitt wechselte Generation und Session. Alte Aktivierung erzeugte keine Einfügung. Die alte Steuerabsicht war im autonomen Kontrolltest abgewiesen worden. |
| V09-06 | PASS | R06 geführt | Mute blockierte zuverlässig den Hotkey. Der USB-Wiederanlauf lieferte ein Folgediktat ohne Neustart. |
| V09-07 | BLOCKIERT | B03, E10 | Transportprobe gibt für den ungültigen Pfad blocked bei Generation 0 ohne Verbindungsversuch aus. Positivpfad /ws/v2 gültig. GUI-/Neustartprobe und sichtbare Fehlermeldung bleiben offen. |
| V09-08 | FAIL | R06 geführt | Der Anwendungsprozess beendete Audio, LED und Texteingabe. Der Onefile-Starter hielt eine Warnung über sein temporäres Verzeichnis offen und endete erst nach Bestätigung. |
| V09-09 | PASS | E08 | Abschluss-Stichprobe aus 53 Clientlogzeilen und 370 Beobachtungsdatensätzen. Null Treffer auf Secret-Muster, Secretfelder und Transkriptfelder. Aussage auf geprüften Lauf und Felder begrenzt. |
| V10-01 | BLOCKIERT | R06 geführt | Über 33 Minuten realer Desktopbetrieb mit Geräteeingriffen und mehreren Eingaben. Overlay-Sichtwirkung und der geforderte vollständige Normalbetrieb blieben offen. |
| V10-02 | BLOCKIERT | R06 geführt | Fünf unterschiedliche kurze WAV-Reize mit zuordenbaren Ergebnissen. Abweichende Texte und nicht getrennte Aktivierungen, Serie durch ungeplanten Verbindungsverlust unterbrochen. |
| V10-03 | FAIL | R06 geführt | 145-Sekunden-WAV führte zu Realtime und Segmenten, bis zum kontrollierten Reconnect fehlte ein finales Ergebnis. |
| V10-04 | BLOCKIERT | E03, E06, B02 | Beide Ziele wurden explizit fokussiert. In Notepad wurde kein qualifiziertes Final eingebracht; deshalb kein Fokuswechsel-PASS. |
| V10-05 | BLOCKIERT | B02 | Für die repräsentative Stichprobe fehlen die kontrollierten Finals und akustische Wake-Szenarien. |
| V10-06 | BLOCKIERT | R06 geführt | 62 Stichproben über rund 15 Minuten, App Private Bytes 501,75 auf 510,28 MiB, Rechner-CPU im Mittel 0,595 %. Keine durchgehende Messung ab Start oder belastbare Bewertung des Wachstums. |
| V10-07 | FAIL | R06 geführt | Zwei ungeplante Abrissphasen mit mehreren Reconnect-Versuchen. Zusätzlich 473 gleichartige Audiomeldungen bei physisch entferntem ReSpeaker. |
| V10-08 | BLOCKIERT | R06 geführt | Der App-Prozess endete. Der Onefile-Starter musste per OK geschlossen werden. Ein anschließender Neustart mit erneuter Prüfung von Profil und Verlauf wurde nicht durchgeführt. |
| V10-09 | FAIL | B01, E05 | Gemeinsamer Cursor veränderte sich im ersten Startweg. Serverzugriffe beschränkten sich auf lesenden Health-/Katalogzugriff und normale V2-Testsessions. |
| F01 | BLOCKIERT | E04, E12, B03 | EXE, Ready, Single-Instance und Trennung der Dialoge belegt. Tray-Tooltip und geforderter direkter Start-Doppelklick offen. |
| F02 | PASS | R06 geführt | Der einmalig kontrolliert wiederholte echte Satz wurde über den ReSpeaker erfasst und eingefügt. |
| F03 | PASS | R06 geführt | Korrektes manuelles Sollfinal genau einmal. Finish, Refresh und Cancel im offenen Aktivierungszustand nachgewiesen. |
| F04 | BLOCKIERT | R06 geführt | Hybrid, Pause und ein echter Wake-Aufruf nachgewiesen. Mehrfach-Live und alle akustischen Triggerkombinationen fehlen. |
| F05 | PASS | R06 geführt | Native Hotkeys und absichtliches Reinsert praktisch belegt. Die vorherige R06-Gegenprobe bestätigte unveränderte Bindungen nach konflikthaftem Apply. |
| F06 | BLOCKIERT | R06 geführt | Drei LED-Phasen und Tonstichprobe vorhanden. Vollständige sichtbare Overlayfolge und trennscharfe Töne fehlen. |
| F07 | BLOCKIERT | B08, B09, E12, E13 | Session-Apply, Rücknahme, GUI-Admin-Guard, Gerätewechsel und Diagnose bestanden. Stiller Draft-Verlust und missverständliche Hotkey-Ablehnung bleiben offen. |
| F08 | PASS | R06 geführt | Der isolierte Netzwerk- und der physische USB-Abriss erholten sich ohne doppelten Textnachtrag. Die irreführende Offline-Anzeige bleibt als eigener Fehler. |
| F09 | FAIL | R06 geführt | Das Langfinal fehlte im geprüften Desktoplauf. Die Kurzserie war unvollständig und zwei ungeplante Verbindungsabbrüche traten auf. |
| F10 | BLOCKIERT | B05 | Adminprüfung ohne gültigen Schlüssel und getrennte Autorisierung offen. Eine Freigabe mit Adminfunktionen ist nicht Gegenstand dieser Empfehlung. |
| F11 | PASS | E05, E06, E12, E14 | Befunde und Testblockaden mit Schweregrad, Reproduktion und offenem Status im separaten Befundbericht dokumentiert. |
| F12 | BLOCKIERT | B07 | Separate Produkt- und Redistributionsfreigabe fehlt. Frühere Buildtests erlauben keine Rechts- oder Releaseaussage. |

## Entscheidung

| Option | Status |
|---|---|
| GO für die nächste Testphase | NOT_RUN |
| GO mit Auflagen | NOT_RUN |
| NO-GO / BLOCKIERT | PASS |
