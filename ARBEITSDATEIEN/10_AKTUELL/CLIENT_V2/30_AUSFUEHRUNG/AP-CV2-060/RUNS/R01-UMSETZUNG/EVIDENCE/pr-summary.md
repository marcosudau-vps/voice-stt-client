AP-CV2-060 verarbeitet veröffentlichte Finals mit ihrer ursprünglichen Session-/Activation-/Segmentherkunft und verhindert doppelte Ausgabe. Die V1-Historie migriert mit Backup und Rollback verlustfrei zu UUID-fähigen Segmenten. Automatische Ausgabe und bewusstes Reinsert reservieren ihren Versuch vor Clipboard/SendInput; ein unklarer Crashversuch wird unknown und nicht automatisch wiederholt.

**Status:** REVIEW_READY. Unabhängige Abnahme offen; kein eigener ROOT_PASS, kein Merge und kein Folgepaketstart. Ab vollständiger Übergabe sind Paketbranchänderungen pausiert.

- Base: `feat/client-v2`; Head: `work/client-v2/ap-cv2-060`.
- Kanonischer Parent: `ce95c66a7a3b4440faaa33289351871a040ebe19` (AP050, PR7; PASS/Freigabe/tatsächliche Übernahme belegt).
- Eingereichter Kandidat: `66b6e39daa86855ae1314025bc06344eb55f7d39`, Tree `fbe3931c3b68efa510bee1e35db4b77ad7a83f27`.
- Server: `ada13b011e1d3829f78e7f389e3b927795a2b3be`; unverändert.
- RESULT-01 bis RESULT-13 einzeln im versionierten Report/Requirementnachweis zugeordnet; fachliche Kriterien und Owner unverändert.

Validierung: **1426 Windowsgesamttests**, **323 gezielte Tests** (-W error), **19 echte gepinnte Server-/WebSocketchecks**, compileall und diffcheck PASS. 29 neue Tests einschließlich fünf tatsächlicher Prozessabbrüche. Alle 195 qualifizierten Produktblobs und Pflichtloghashes stimmen mit dem getesteten Kandidaten überein. Erster Vollsuitelauf TIMEOUT300s dokumentiert; unveränderter finaler Kandidat vollständig PASS in 117.86s.

[Runreport](https://github.com/marcosudau-vps/voice-stt-client/blob/66b6e39daa86855ae1314025bc06344eb55f7d39/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenzindex](https://github.com/marcosudau-vps/voice-stt-client/blob/66b6e39daa86855ae1314025bc06344eb55f7d39/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Result-API und Migration](https://github.com/marcosudau-vps/voice-stt-client/blob/66b6e39daa86855ae1314025bc06344eb55f7d39/docs/protocol-v2-results.md).

Testgrenzen: gepinnter produktiver Server über TCP/WebSocket bis realem Clientmirror/Resultservice/SQLite/Injectionworker; Recorder-/Modellergebnisse und Clipboard/SendInput am benannten Testadapter. Appkomposition bleibt AP100, tatsächliche ASR-/Hardware-/Fokus-/Anwendungsabnahme AP-IV2-020. command_sent beweist einen abgesandten Einfügebefehl, keine Aufnahme durch eine fremde Anwendung.

