# R06 · Fortsetzung und gezielte Nachqualifikation durch ChatGPT
Stand 23.11.2026. Auftrag: unterbrochenen Codex-Lauf fortsetzen; keine Promotion/Veröffentlichung. Arbeitsstand 17fce388e747daf37b97e96ed1fcf6421338873d plus unveränderter lokaler Produkt-/Testdiff (SHA-256 f6bff20f30623fdfeee7633d936575ce05c7da274bb61ecee13e3b581e9fc53b). Keine Änderung an Produktcode, Testserverdefaults, Benutzerprofilen oder globaler Zwischenablage durch diese Fortsetzung.

## Wiederhergestellte Nachweise des vorherigen Agenten
- Vollsuite: 1414 Tests, 172.842 s, OK, Logende 23:00:56. Original-Stdout/-Stderr sowie Build- und Frozen-Logs hashgeprüft im lokalen Nachweisordner gesichert. Testresultatliste in EVIDENCE/KORREKTUR_2026-11-23/final-vollsuite-testresults.txt. Der genaue damalige Aufruf und ein damals erzeugter Diff-Fingerprint wurden nicht gefunden; jetzige Datei-/Diffhashes nachgetragen, kein rückwirkend behaupteter sauberer Commit.
- Korrigierte EXE, Version 1.0.0, 77415688 Bytes, SHA-256 07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe; Build 22:59:20. Dirty source, clientCommit=unknown. Historischer Frozen-Offscreen-Smoke PASS. Desktop-Altpaket nicht überschrieben.

## Neu ausgeführte Nachweise
| Bereich | Ergebnis | Umfang |
|---|---|---|
| 6 gezielte QtSurface-Regressionen | 6/6 PASS | Windows-QPA, eigene sichtbare Qt-Widgets, isolierte Testdienste; Reload, Doppelbelegung, Offline/Pause, Entscheidungsdialoge, ungültige/fehlende Wake-Auswahl |
| Reale V2-Transport-/Pausen-Gegenprobe | 8/8 PASS_SCOPED | Produktionsquellclient, Final-Testserver e95858e3c010a7e9324b49bb44fee349abe7128a, Hybrid, Pause, eigener Socketabriss, neue Session, unbestätigte Offline-Anzeige, Pause wieder bestätigt, Resume, exakt ein Final und Einfügeauftrag bei synthetischem PCM; kein nativer Paste |
| Integrierte native Desktop-Oberfläche | 17/17 PASS_SCOPED | Tatsächlicher Quellclient mit nativen Qt-Fenstern/Tray, realer Final-Testserver, absichtlich ungültiges Gerät und deaktivierte Hotkeys/LED/Sound |
| Erweiterte native Desktop-Prüfung | 20/20 PASS_SCOPED | Zusätzlich lokale GUI-Übernahme von Overlay/Clipboard/Verlauf und Datei-Readback; zwei vorgelagerte Fehlbewertungen der Doppelbelegung durch fehlerhafte UTF-8-Decodierung des Hilfsskripts erhalten. Tatsächlicher Hinweis und unveränderter Profilhash waren korrekt. Finaler Wiederholungslauf mit Unicode-Escapes grün. |
| Native Frozen-Smokes | 2/2 PASS_SCOPED | Korrigierte EXE, Windows-QPA, lokales und OneDrive-TEMP, Exit 0, je 0 verbleibende _MEI-Ordner. Kein langer regulärer Traybetrieb. |
| Cursor- und Persistenzprobe | 6/6 PASS_SCOPED | Reales lokales isoliertes Cursor-Schreiben und Readback, unveränderter gemeinsamer Cursor, neu gestarteter Python-Prozess liest gespeicherte Overlayposition/-deckkraft und Verlaufslimit. |

## Zuordnung und Grenzen
- V01-02: natives Tray-Symbolobjekt, Tooltipinhalt und Menüaktionen, Einstellungen und Beenden über QAction belegt; kein physischer Taskleisten-Hover/Explorer-Doppelklick des korrigierten Frozen-Produkts.
- V01-08/-09, V05-07, V07-11, V08-08: reale Overlay-Sichtbarkeit, Umschaltung, Lage, Deckkraft sowie native Dialoge belegt. Vollständige DPI-/Tooltip-/Feedbacksequenz und globaler Overlay-Hotkey offen.
- V02-09: ungültiges Gerät bleibt sichtbar, keine ungewollte Aufnahme; Wiederherstellung eines echten Geräts mit Folgediktat offen.
- V04-11, V05-09/-10, V08-05/-14: konkrete Konfliktmeldung inklusive beider Felder und Tastenkombination, atomarer Profilhash, Reload-Entwurf im echten Dialog, gezielte ungültige Wake-Regression belegt. Realer Trigger-/Hotkey-Einsatz nach Änderung nicht erneut geprüft.
- V08-09/-10/-13: tatsächliche GUI-Speicherung von Clipboard-/Verlauf-/Overlaywerten; Readback in neuem Prozess. Reale Nutzwirkung, regulärer kompletter EXE-Neustart und History-Datenoperationen offen.
- V08-15/V10-09: expliziter Client-Home und isolierter Cursor-Write/Readback gegen unveränderten gemeinsamen Cursor belegt. Native Tests ohne aktivierten Event-Stream; tatsächliche integrierte Event-Stream-Persistenz im korrigierten Frozen-Startweg offen.
- V09-01/-04: reale Transportunterbrechung und neue Session mit korrekter Offline-/Pausenprojektion aus dem korrigierten Quellclient belegt; aktiver Segmentabriss im Frozen-Produkt und sichtbare GUI-Verlustfolge noch offen.
- V09-08: native Frozen-Smokes ohne Entpackrest, regulärer Quellclient-Shutdown bestätigt; langlaufende Tray-EXE nicht nachgeprüft.

## Noch nicht abgeschlossene Pflichtpunkte
1. Korrigierter Frozen-Build mit vollständiger realer Desktop-/Hardwareprüfung. Keine physische Mikrofonaufnahme, native Paste-Ausführung, Änderung fremder Fenster, Hotkey-Auslösung oder LED-/Soundwahrnehmung in dieser Fortsetzung. Dafür kontrollierte Umgebung und ggf. Bediener nötig.
2. 30–60-Minuten-Normalbetrieb, zehn saubere Kurzdiktate, mindestens zwei Minuten Langdiktat, Fokuswechsel Notepad/zweiter Editor, CPU/RAM/Logs und danach regulärer Neustart. Kein Ersatz durch kurze native Smokes/PCM.
3. Ursprüngliches ausstehendes Langfinal und zwei ungeplante Verbindungsabbrüche: Ursache nicht geklärt. Kurzer erfolgreicher Reconnect begründet keine Schließung. Onefile-Warnung nach längerem Traybetrieb nicht reproduziert, nicht geschlossen.
4. Mute- und USB-Logging: Korrektur bereits vollautomatisch belegt. Physischer Retest fehlt. Neue Beobachtung in native Desktop-Runs: absichtlich ungültiger Index 2147483647 erzeugt wiederholt echte PortAudio-Abfragefehler/Stacktraces; nicht die früher falsche 44,1-kHz-Ausweichmeldung. Prüfen, ob Rate-Limit/Deduplizierung für Fehler bei fehlendem Gerät erforderlich; kein neuer Produktpatch ohne reproduzierbare gezielte Bewertung.
5. Admin-Write-Prüfung oder expliziter Ausschluss, Produkt-/Redistributionsentscheidung, sauberer identifizierbarer Kandidat, unabhängiger Review. Kein eigener ROOT_PASS, kein Commit/Push/Merge/Release.

## Urteil
PASS_SCOPED für die oben exakt benannten neuen Nachweise. Gesamtfreigabe NO-GO / BLOCKED_PENDING_DESKTOP_RETEST_AND_REVIEW. Die historische 139-Einträge-Matrix 09 bleibt unverändert als Urteil über den ursprünglichen Kandidaten. Keine pauschale Umwertung auf PASS, keine erneute Durchführung der bereits grünen 1414er Suite. [Nachweisindex](EVIDENCE/FORTSETZUNG_2026-11-23/INDEX.md).
