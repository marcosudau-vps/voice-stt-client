# R06-Nachtrag vom 23.11.2026 · autonome Restprüfung

Kandidat 9f9fdf2b19f99a6d4f255d76b6cfa9ef3de493b2, EXE-SHA-256 28cea377ee59b2342fd9f5fd2d10a93cc6e2a8a1df950a9a1efa3af216ab65f8.
Final-Testinstanz e95858e3c010a7e9324b49bb44fee349abe7128a, Protokoll 2. Die reguläre Tray-Anwendung blieb aus. Die eingebettete Onefile-Diagnose lief offscreen. Synthetische PCM-Dateien wurden am Audio-Testport eingespielt. Das ReSpeaker-Mikrofon und die Lautsprecher blieben außerhalb des Prüflaufs.

Die 99 offenen Einträge aus [dem Prüfprotokoll](04_COMPUTER_USE_ERGEBNIS.md) wurden einzeln zugeordnet. 66 davon haben ergänzende technische Belege. Die Protokollteile von V09-02 und V09-05 sind an der tatsächlichen Final-Testinstanz nachgewiesen. Die visuelle Desktop-Wiederanlaufprüfung kann diese Nachweise als Vorprüfung nutzen. Die formale Desktop-Checkliste behält ihre ursprünglichen Status, weil die zugehörigen praktischen Wirkungen mit der eingefrorenen EXE erst in einem bestätigten Lauf abgenommen werden.

## Ergebnisse

| Beleg | Durchgeführt | Lokale Datei |
|---|---|---|
| A1 | Verifizierte Onefile-EXE im eingebauten Qt-Diagnosemodus. Fünf lokale Tabs, Overlay und Feedback-Ressourcen. Separat Overlay-Komponente mit Sichtbarkeit, Lage und Deckkraft. Qt offscreen. | frozen-offscreen.json, overlay-component.json |
| A2 | Reale Finals und Interims mit 16-kHz-SAPI-Dateien. Drei unterschiedliche erwartete Satzinhalte, jeweils ein Einfügeauftrag. Finish, Refresh und Cancel über die produktive Runtime-Steuerung. | live-fixtures.json, live-fixtures/manual-recovery/observed.json |
| A3 | Wake-only, Hybridmodus und reine manuelle Aktivierung mit synthetischem PCM. Server bestätigte Pause und Aufheben. Zwei Wake-Auslösungen bei wieder aktiver Erkennung. Zusätzlich negative Testaudios. Kombinierter erster ASR-Versuch hatte keinen Recording-Start vor Finish. Im Wiederholungsversuch wurde auf Recording gewartet und ein korrektes Final geliefert. | replay-wake.json, hybrid-retry.json, replay-dictation.json |
| A4 | 16 echte Win32-Hotkey-Checks. WM_HOTKEY für fünf Rollen, je einmal bei gehaltenem Tastendruck, fremde Belegung, 1409 und Rollback. Synthetische Tasten in der nativen Komponente. | native/hotkeys.json, native/hotkeys.log |
| A5 | Produkt-Clipboard-Queue und Win32 SendInput im eigenen Qt-Prozess. Unicode-Paste, Entdoppelung, explizites Reinsert, keine neue Historienzeile und Wiederherstellung des gesetzten synthetischen Testtexts. Beide ersten Versuche endeten vor Einfügung. Die erfolgreiche Einfügesequenz nutzte den vom eigenen Ziel gemeldeten PID statt des Python-Startprozesses. Die abschließende Sicherung der ursprünglichen Windows-Zwischenablage konnte nicht zurückgespielt werden. | native-target-pid/stdout.json, native-target-pid/native-paste.json, provenienz-nachher.json |
| A6 | Reale V2-Settings-Änderung mit offenem Testsegment. Fehlende Auswahl schützt Eingabe und Profil. Verschobene Änderung hält alte Session und Final bis Abschluss, neue Session bestätigt Wake-only. Die Wiederholung wartet ausdrücklich auf den asynchronen Einfügeauftrag. | settings-live-confirm.json, settings-overlay-confirm.log |
| A7 | Eigener V2-Socket im Idle und während einer aktiven Testaufnahme getrennt. Reconnect mit neuer Server-Session, keine Ausgabe der abgebrochenen Aktivierung, veraltete Steuerabsicht verworfen. Lokaler, nur auf die Final-Testinstanz begrenzter CONNECT-Relay separat mit echten TLS-Verbindungen geprüft. | live-fixtures.json, v2-loopback-relay.json |
| A8 | Zehn verschiedene kurze synthetische Diktate in 49,48 Sekunden mit je einem Final und einem Einfügeauftrag. Ein weiterer synthetischer Durchlauf mit 145 Sekunden PCM und vier eindeutigen Final-Segmenten in einer Aktivierung. Kein echter 30–60-Minuten-Desktop-Soak. | replay-dictation.json |
| A9 | 267 gezielte Pakettests für Settings-UI, Hotkeys, History, Clipboard, Medienverlust, Resultat und Feedback. Der Runner protokolliert die simulierten Komponenten und Fehlerpfade. | gezielte-tests.log |

## Aufräumkontrolle und Abweichung

Die Bytevergleiche ergaben keine Änderung an der Test-YAML oder am gemeinsamen Cursor. Es lief danach kein Voice-STT-Testclient und kein eigener Editorprozess. Es wurden ausschließlich normale Sessions und lesende API-Aufrufe an der Final-Testinstanz verwendet. Produktivsysteme und Serverdefaults blieben außerhalb der Änderung.

Der native Hilfstest hat den vorherigen lokalen Clipboard-Inhalt nicht zurückgespielt. Der harmlose R06-Testmarker stand bei der Kontrolle weiterhin in der gemeinsamen Zwischenablage. Der ursprüngliche Inhalt wurde nur im Speicher des inzwischen beendeten Helfers gehalten und ist aus diesem Lauf nicht wiederherstellbar. Die restaurierte Testzeichenfolge belegt die Produktoption im isolierten Versuch. Die fehlende Rückgabe der Benutzer-Zwischenablage ist eine Abweichung des Hilfstests. Weitere Clipboard-Schreibtests wurden daraufhin ausgesetzt.

Die drei bestehenden Produktbefunde bleiben offen. Der gemeinsame Cursorpfad, der Verlust von Entwürfen beim Neuladen und der unpräzise Hotkeykonflikthinweis brauchen für eine Korrektur einen eigenen Auftrag. Das frühere NO-GO bleibt maßgeblich.

## Was vor Ort noch gebraucht wird

- Vor dem Desktop-Test bestätigtes Ja im Chat und eine leise Umgebung. Falls der Tray-Einstieg oder das reguläre Beenden nicht zugänglich sind, erfolgt dafür eine kurze Übergabe.
- LED-Muster und Ton an den angekündigten Zuständen beobachten. Mute und USB-Abziehen/Wiederanschließen einmal durchführen. Die Folgeprüfung der wiedererkannten Eingabe übernimmt Codex.
- Ein gesprochener Satz reicht für eine Live-Stichprobe. Mehrfach ausdrücklich geforderte Live-Wake-Aufrufe bleiben bei diesem Umfang offen. Die weiteren Diktate und Wake-Trigger laufen mit Testaudio.
- Der Netzwerkfehler wird ausschließlich am Testclient erzeugt. Die isolierte technische Unterbrechung ist schon reproduziert. Kein Bediengriff am VPS.
- Separate Admin-/Releasefreigaben und das nötige Bestätigen echter UI-Löschvorgänge mit Testdaten bleiben auf ihren jeweiligen Umfang begrenzt.

## Zuordnung der 99 ursprünglich offenen Fälle

Die letzte Spalte benennt die nächste praktische Prüfmöglichkeit. Ein Prüfgate kann mehrere darunterliegende Fälle zusammenfassen.

| ID | Stand R06 | Zusätzlicher Beleg | Nächster Schritt |
|---|---|---|---|
| V01-01 | NOT_RUN | – | Mithilfe vor Ort oder Live-Stichprobe |
| V01-02 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V01-08 | BLOCKIERT | A1 | Codex im bestätigten Desktop-Testlauf |
| V01-09 | BLOCKIERT | A1 | Codex im bestätigten Desktop-Testlauf |
| V02-04 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V02-05 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V02-06 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V02-07 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V02-08 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V02-09 | BLOCKIERT | A9 | Codex im bestätigten Desktop-Testlauf |
| V03-01 | BLOCKIERT | A6 | Codex im bestätigten Desktop-Testlauf |
| V03-03 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-04 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-05 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-06 | FAIL | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-08 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-09 | BLOCKIERT | A8 | Codex im bestätigten Desktop-Testlauf |
| V03-10 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-11 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-12 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V03-13 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-02 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-03 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-04 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V04-05 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-06 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-07 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-08 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-09 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-10 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-11 | BLOCKIERT | A3 | Codex im bestätigten Desktop-Testlauf |
| V04-12 | BLOCKIERT | A3 | Mithilfe vor Ort oder Live-Stichprobe |
| V05-02 | BLOCKIERT | A4 | Codex im bestätigten Desktop-Testlauf |
| V05-04 | BLOCKIERT | A4 | Codex im bestätigten Desktop-Testlauf |
| V05-05 | BLOCKIERT | A4 | Codex im bestätigten Desktop-Testlauf |
| V05-06 | BLOCKIERT | A3, A4 | Codex im bestätigten Desktop-Testlauf |
| V05-07 | BLOCKIERT | A4 | Codex im bestätigten Desktop-Testlauf |
| V05-08 | BLOCKIERT | A4 | Codex im bestätigten Desktop-Testlauf |
| V05-09 | FAIL | – | Offener Produktbefund |
| V05-10 | BLOCKIERT | A4 | Codex im bestätigten Desktop-Testlauf |
| V06-01 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V06-02 | FAIL | A5 | Codex im bestätigten Desktop-Testlauf |
| V06-04 | BLOCKIERT | A2, A5 | Codex im bestätigten Desktop-Testlauf |
| V06-05 | BLOCKIERT | A5 | Codex im bestätigten Desktop-Testlauf |
| V06-06 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V06-07 | BLOCKIERT | A5 | Codex im bestätigten Desktop-Testlauf |
| V06-08 | BLOCKIERT | A5 | Codex im bestätigten Desktop-Testlauf |
| V06-09 | BLOCKIERT | A2 | Codex im bestätigten Desktop-Testlauf |
| V06-10 | BLOCKIERT | A9 | Codex im bestätigten Desktop-Testlauf |
| V06-11 | BLOCKIERT | A9 | Freigabe oder Bestätigung zum konkreten Schritt |
| V06-12 | BLOCKIERT | A9 | Codex im bestätigten Desktop-Testlauf |
| V06-13 | BLOCKIERT | A9 | Freigabe oder Bestätigung zum konkreten Schritt |
| V07-02 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V07-03 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V07-04 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| V07-05 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V07-06 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V07-07 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V07-08 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V07-09 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V07-10 | BLOCKIERT | A8 | Codex im bestätigten Desktop-Testlauf |
| V07-11 | BLOCKIERT | A9 | Codex im bestätigten Desktop-Testlauf |
| V08-05 | FAIL | – | Offener Produktbefund |
| V08-06 | BLOCKIERT | A6 | Codex im bestätigten Desktop-Testlauf |
| V08-07 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V08-08 | BLOCKIERT | A1 | Codex im bestätigten Desktop-Testlauf |
| V08-09 | BLOCKIERT | A5 | Codex im bestätigten Desktop-Testlauf |
| V08-10 | BLOCKIERT | A9 | Codex im bestätigten Desktop-Testlauf |
| V08-11 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V08-13 | BLOCKIERT | A6 | Codex im bestätigten Desktop-Testlauf |
| V08-14 | FAIL | – | Offener Produktbefund |
| V08-15 | FAIL | – | Offener Produktbefund |
| V09-01 | BLOCKIERT | A7 | Codex im bestätigten Desktop-Testlauf |
| V09-02 | BLOCKIERT | A7 | Protokollnachweis vorhanden, Desktop-Gegenprobe im Wiederanlaufszenario |
| V09-03 | BLOCKIERT | A7 | Codex im bestätigten Desktop-Testlauf |
| V09-04 | BLOCKIERT | A7 | Codex im bestätigten Desktop-Testlauf |
| V09-05 | BLOCKIERT | A7 | Protokollnachweis vorhanden, Desktop-Gegenprobe im Wiederanlaufszenario |
| V09-06 | BLOCKIERT | A9 | Mithilfe vor Ort oder Live-Stichprobe |
| V09-07 | BLOCKIERT | A9 | Codex im bestätigten Desktop-Testlauf |
| V10-01 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V10-02 | BLOCKIERT | A8 | Codex im bestätigten Desktop-Testlauf |
| V10-03 | BLOCKIERT | A8 | Codex im bestätigten Desktop-Testlauf |
| V10-04 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V10-05 | BLOCKIERT | A8 | Codex im bestätigten Desktop-Testlauf |
| V10-06 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V10-07 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V10-08 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| V10-09 | FAIL | – | Offener Produktbefund |
| F01 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| F02 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| F03 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| F04 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| F05 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| F06 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| F07 | BLOCKIERT | – | Offener Produktbefund |
| F08 | BLOCKIERT | – | Mithilfe vor Ort oder Live-Stichprobe |
| F09 | BLOCKIERT | – | Codex im bestätigten Desktop-Testlauf |
| F10 | BLOCKIERT | – | Freigabe oder Bestätigung zum konkreten Schritt |
| F12 | BLOCKIERT | – | Freigabe oder Bestätigung zum konkreten Schritt |

[Lokaler Nachweisindex](EVIDENCE/AUTONOM_2026-11-23/INDEX.md)
