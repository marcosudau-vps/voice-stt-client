# R06 · lokale Client-Korrektur und Nachprüfung

Basis 17fce38, ursprünglicher R06-Produktstand 9f9fdf2. Der Auftrag vom 23.11.2026 autorisiert die Korrektur der offenen Clientbefunde und die zugehörige lokale Prüfung. Der ausführende Paketbranch bleibt uncommittiert. Produktive Server und bereits vorhandene Benutzerprofile lagen außerhalb der Änderung.

## Lokale Korrekturen

| Befund | Korrektur und Nachweis |
|---|---|
| Gemeinsamer Cursor trotz getrenntem Client-Home | Der Standardcursor folgt einem expliziten Client-Home in dessen Datenverzeichnis. Ein expliziter Cursorpfad hat Vorrang. Ohne Client-Home gilt weiterhin der bisherige Standardpfad. Regressionstest bestätigt, dass eine vorbereitete gemeinsame Cursor-Datei bytegleich bleibt. |
| Verlust beim Neuladen | Der Dialog aktualisiert Schemawerte, lesende Statusspalten und den Katalog. Editierte Eingabefelder und Triggerentwürfe bleiben erhalten. Bestätigtes Übernehmen aktualisiert den jeweiligen Einstellungsbereich. Qt-Tests prüfen erfolgreiche Aktualisierung, Erhalt der Eingaben und getrennte Bereiche. |
| Irreführender Hotkey-Konflikt | Der lokale Dialog nennt die identische Tastenkombination und beide betroffenen Felder. Die Validierung im Client-Core liefert einen konkreten Konfliktcode und lässt die Persistenz aus. |
| Veralteter Triggerstatus und fehlerhafte Laufzeitpause | Der Dialog benötigt eine bereite Transportbindung und eine passende, bestätigte Spiegelgeneration. Bei Unterbrechung zeigt er einen unbestätigten Verbindungszustand. In der Pause-Zeile stammen gewünschter und wirksamer Wert aus der Laufzeitsteuerung. Nach Verlust zeigt sie den noch gespeicherten Laufzeitwunsch und einen unbestätigten wirksamen Wert. |
| Falsche Mute-Diagnose | Das Audit wertet den booleschen Rückgabewert des Medienpfads aus. Beide Ergebnisse sind geprüft. |
| Wiederholte Ausweichratenmeldung bei USB-Verlust | Die Ausweichrate wird nach erfolgreichem Öffnen und Start des Streams protokolliert. Fehlversuche hinterlassen keine erfolgreiche Ausweichmeldung. Der bestehende Recovery-Takt bleibt bestehen. |


## Build und Testumgebung

Der erste neue EXE-Lauf scheiterte vor dem Anwendungsstart. Computer Use erfasste die Meldung 'Invalid packaged build identity'. Aus dem tatsächlich gebauten Archiv ließ sich ein unvollständiger Teststempel mit künstlichem Commit extrahieren. Der gleichzeitig laufende Build-Test und PyInstaller nutzten denselben Stempelpfad. Der Stempel und die Versionsdatei liegen jetzt in einem temporären Verzeichnis pro Aufruf. Der Build-Test prüft den separaten Pfad, die Lebensdauer und die Aufräumung.

Der erste Vollsuitenlauf reproduzierte einen Fehler beim temporären Git-Checkout. Zwei Git-bezogene Tests bestanden getrennt. Eine kleine Testfolge wies als Ursache leere, vom Testhost injizierte Git-Konfigurationswerte nach. Die Python-Tests stellen die Prozessumgebung nach Testfällen wieder her. Windows gibt die leeren Werte an neue Git-Prozesse anschließend nicht mehr weiter. Der Fix für die Testdurchführung ist auf die Umgebung des lokalen Testprozesses begrenzt. Produkt und Git-Konfiguration auf dem Rechner bleiben von dieser Maßnahme unberührt.
## Gegenproben und verbleibende Freigabepunkte

- Die unveränderte Final-Testinstanz e95858e3 lieferte im vollständigen PCM-Replay des korrigierten Quellclients zehn passende Kurzfinals mit jeweils genau einem Einfügeauftrag. Das 145-Sekunden-Audio ergab vier eindeutige Finalsegmente und vier Einfügeaufträge. Dieser Pfad speist PCM nach dem Mikrofon-Treiber ein und simuliert die Windows-Zwischenablage. Der R06-Befund mit Lautsprecher, ReSpeaker und echter Einfügung bleibt für die Desktop-Nachprüfung offen. Im gepinnten Serverstand wird die angenommene Transkription vor der eigentlichen Final-Inferenz beobachtbar. Die frühere Spur belegt eine fehlende Rückgabe dieser Verarbeitung, die genaue Ursache des damaligen Ausfalls bleibt offen. [PCM-Gegenprobe](EVIDENCE/KORREKTUR_2026-11-23/pcm-gegenprobe.json)
- Der ursprüngliche Onefile-Kandidat durchlief den eingebauten GUI-Verpackungstest mit normaler lokaler und mit OneDrive-basierter temporärer Ablage. Beide Prozesse endeten mit Exit 0 ohne verbliebene Entpackordner. Der lange Tray-Ablauf aus R06 wurde dabei nicht wiederholt. Die einmalige Aufräumwarnung bleibt offen. [Onefile-Gegenprobe](EVIDENCE/KORREKTUR_2026-11-23/onefile-gegentest.jsonl)
- Die automatische Prüfung ersetzt weder die betroffenen Windows-Retests mit dem neuen Build noch den unabhängigen Review. Hardware-/Wahrnehmungsbelege, die vollständige praktische Diktatserie und der repräsentative Dauerlauf bleiben Scope der Nachabnahme. Admin-Prüfbetrieb oder dessen ausdrücklicher Ausschluss sowie Produkt- und Redistributionsfreigabe bleiben gesonderte Entscheidungen.

- [Bewertung des ursprünglichen Desktoplaufs](08_GEFUEHRTER_DESKTOP_NACHLAUF_2026-11-23.md)
- [Prüfmatrix des ursprünglichen Kandidaten](09_STATUS_ALLER_PRUEFPUNKTE_2026-11-23.md)
