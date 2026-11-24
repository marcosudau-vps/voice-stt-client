# R06 – native Zielanwendungen und EXE-Pilot (24.11.2026)

## Native Windows-Einfügung – erfolgreich
13/13 technische Checks PASS_SCOPED. Korrigierter Quellclient, echter gepinnter V2-Server, echter ReSpeaker über Lautsprecher-Testreize, unveränderte produktive TextInjectionQueue und Win32-Clipboard/SendInput-Backend, zusätzlicher Sicherheitsguard ausschließlich für eigene Testfenster.
- Eigenes leeres Notepad-Dokument per eindeutig zugeordnetem HWND/PID und UI Automation verifiziert. Erstes akustisches Diktat exakt wie autoritatives History-Final eingefügt; beide Sollmarker erkannt; ein Einfügevorgang; vorheriger Klartext-Zwischenablageinhalt wiederhergestellt.
- Zweites akustisches Diktat in eigener separater Qt-Editoroberfläche nach tatsächlichem Fokuswechsel eingefügt; erneut exakt wie Final, beide Sollmarker, ein Einfügevorgang, Clipboard wiederhergestellt. Notepad blieb unverändert; Ziele und Texte verschieden.
- Gemeinsamer Cursor unverändert, Core/Tray beendet. Keine anderen Fenster beschrieben; kein Produktcode geändert. V06-01/V10-04 PASS_SCOPED. Kein gleichzeitiger Vollnachweis für erhöhte Fremdanwendungen, keine erneute physische Tastaturprüfung erforderlich für diese beiden Kriterien.
- Vorheriger separater Clipboard-Helper mit Klartext: erste exakte Unicode-Einfügung und Deduplizierung erfolgreich; explizite Wiedereinfügung command_sent, aber exakter Vergleich timeout (beobachtet 73 Zeichen); ursprüngliche Clipboard-Wiederherstellung nicht nachgewiesen, weil Sequenz sich geändert hatte. Historischer positiver Reinsert-Nachweis bleibt; dieser Versuch wird nicht als PASS umgedeutet.

## Frozen-Pilot
Korrigierte EXE (SHA 07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe): echter Primary-/Finish-Hotkey, echtes akustisches Final und exakt einmal native Einfügung mit Sollmarkern erfolgreich. Erste 60-s-Probe stoppte nach 6,56 s Ready-Messung, weil Clipboard vor abgeschlossener Wiederherstellung bewertet wurde; keine Schlussfolgerung über Ursache ohne Nachtest. Frühere Probe hatte nachgewiesenen Hotkey-Audit, aber Core antwortete core_unavailable; längere Startbereitschaft im neuen Pilot führte zu erfolgreicher Activation.
Dauerprüfung separat; kein bestandener 30–60-Minuten-Nachweis behauptet.

## Rest
V10-01 repräsentativer Dauerbetrieb des korrigierten Frozen-Kandidaten; Bewertung verbleibender Teilnachweise und unabhängige Gesamtfreigabe. Historische Abrisse ACCEPTED_RISK und Redistributionsfreigabe USER_APPROVED wie Bericht 21. Admin im Freigabeumfang technisch erfolgreich.

Belege: EVIDENCE/NATIVE_ZIELANWENDUNGEN_2026-11-24. Kein Commit/Push/Merge/Release.

## Korrigierter Pilot
30,08 s Ready, zwei echte native Hotkey-Diktate mit exakt je einem Final und identischem Text im Testeditor; Clipboard-Restore beide erfolgreich. Beide akustischen Sollmarker-Sätze abweichend, kein Einfügefehler. Keine Reconnects, keine ERROR-Zeilen, Exit 0, keine _MEI-Reste. Der vorangegangene zweite 60-s-Pilot hatte einen Testzeitgeberfehler (alte Idle-Zeit beim Wechsel zur Aktivierung), der die sofortige Beendigung und command_outcome_unknown auslöste. Dieser Fehler ist im Testskript behoben. Belege: frozen-endurance-30s.json und frozen-endurance-60s-retest.json.
