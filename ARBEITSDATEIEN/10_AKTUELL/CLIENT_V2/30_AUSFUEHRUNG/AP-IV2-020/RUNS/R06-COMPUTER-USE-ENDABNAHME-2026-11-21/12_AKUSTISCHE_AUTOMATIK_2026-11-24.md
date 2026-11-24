# R06 – autonome akustische Gegenprobe und Wiederholungen (24.11.2026)

Auftrag: akustische Tests mit Lautsprecher-Wiedergabe generierter Sprachfixtures wiederholen, bis eine vollständige Zehner-Serie bestanden ist. Vorherige negative Ergebnisse bleiben erhalten.

## Kandidat und Grenzen
- Unveränderter korrigierter Produktionsquellclient (HEAD 17fce388e747daf37b97e96ed1fcf6421338873d plus lokaler Produkt-/Testdiff wie Nachweis 11); echte V2Runtime, kein Tray/Frozen-Produkt in diesen Akustikläufen.
- Final-Testserver: wss://final.v2.voice-stt-server.marcosudau.com/ws/v2, bestätigter Servercommit e95858e3c010a7e9324b49bb44fee349abe7128a.
- Echte Realtek-Lautsprecher, tatsächliches ReSpeaker XVF3800 (Windows DirectSound, Index 9); synthetische WAV-Sprachfixtures, kein direkter PCM-Ersatz in diesen Läufen. Isoliertes Testprofil und History, MockInjectionBackend (kein echter Paste in fremde Anwendungen). Keine Änderungen an globaler Lautstärke, Produktcode oder Server.
- PASS pro Kurzdiktat: alle vorab definierten Schlüsselwörter erkannt, genau ein Final-Historyeintrag und ein Einfügeauftrag. Kein Anspruch auf wortwörtliche Übereinstimmung. Keine privaten Rohtranskripte oder Aufnahmen in Repo-Nachweisen.

## Ergebnisse
| Lauf | Kurzdiktate PASS | Abweichungen |
|---|---:|---|
| Ursprung, bis 00:00:35 | 9/10 | kurz-08 Timeout, Activation started/closed ohne Interim oder Final; Folgediktate wieder erfolgreich |
| Wiederholung 1 | 9/10 | kurz-01 Schlüsselwort blau fehlt, Final und Auftrag jeweils 1 |
| Wiederholung 2 | 8/10 | kurz-05 Schlüsselwortabweichung bei 1 Final/1 Auftrag; kurz-08 Timeout |
| Wiederholung 3 | 10/10 | keine Abweichung |

Wiederholungen 1–3 im selben Clientprozess, gleiche Servergeneration 1 und dieselben zehn WAV-Dateien. Gegenüber Ursprung 650 ms Vorlauf nach Aktivierung und 800 ms Nachlauf nach Wiedergabe; Final-Wartefenster 35 statt 20 Sekunden. Keine Änderungen an ASR- oder VAD-Einstellungen. Lauf 00:01:54 bis 00:05:45, Exit 0, keine Cleanupfehler. Keine ungeplante neue Servergeneration während Wiederholungen.

Ursprung zusätzlich: zwei Wake-Word-Aktivierungen, eine mit allen erwarteten Nutzsatz-Schlüsselwörtern; beide je ein Final und ein Auftrag. Wake-Pause negative Probe PASS; kontrollierter Reconnect auf Generation 2 PASS, anschließendes Folgediktat PASS. Native Qt-/Audio-/History-/Feedback-/Recovery-Regressionssuite: 248 Tests in 37.774 s, OK.

## Bewertung
PASS_SCOPED für eine vollständige Zehner-Serie auf realem akustischem Eingangspfad, produktiver korrigierter Runtime und gepinntem Server. Kein reproduzierbarer Client-Verlust eines bereits erkannten Finals in diesen Versuchen; ursprünglicher und erneuter kurz-08-Timeout zeigen keine erkannte Sprachphase. Die genaue Ursache (Wiedergabe/Mikrofon/VAD/ASR/Timing) bleibt unbestimmt. Nicht allein aufgrund erfolgreicher Wiederholung als nachweislicher Testfehler deklarieren. Keine pauschale Freigabe des Langzeittests, der Frozen-EXE oder der nativen Clipboard-/SendInput-Integration. Historische Abweichungen bleiben dokumentiert.

## Nachweise
EVIDENCE/AKUSTIK_AUTOMATIK_2026-11-24/
- acoustic-automation.json SHA256 8c9e51603b843e5b03f4c1cd9397abac4b06343670d97d5c4c89d8c35dba3fe7
- acoustic-automation-repeat.json SHA256 004608a699fad9c44a589b970b05f171c3ee3dcf25c3fc595a290b228a6eee00
- acoustic-automation.py und acoustic-automation-repeat.py: tatsächlich ausgeführte Hilfsskripte; lokale Ausführungsbasis Nachweise/korrektur-2026-11-23, WAV-Fixtures in Nachweise/autonome-restpruefung-2026-11-23/fixtures.
- automation-media-history-qt.log SHA256 0cede322df25b06afac5389e7b764ad40bbd965cc3d003f6586844721bf38e24

Gesamtstatus R06 bleibt BLOCKED_PENDING_DESKTOP_RETEST_AND_REVIEW; akustische Zehner-Serie jetzt PASS_SCOPED. Kein Commit/Push/Merge/Release.
