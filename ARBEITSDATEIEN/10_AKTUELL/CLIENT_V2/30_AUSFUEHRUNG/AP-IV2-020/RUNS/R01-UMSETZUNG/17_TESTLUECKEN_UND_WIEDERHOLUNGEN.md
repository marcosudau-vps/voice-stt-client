# Testlücken: erhaltene Nachweise, Aktenarbeit und erforderliche Wiederholungen

Stand: 19.10.2026, AP-IV2-020 / derselbe R01, Paketbranch und Draft-PR15.
Auftrag: die Folgen des [Servercommit-Audits](16_SERVER_COMMIT_AUDIT.md)
fallbezogen einordnen und unnötige menschliche Wiederholungen vermeiden.
Diese Liste ist eine Belegauswertung, keine neue Testausführung oder Abnahme.
Kein Server/Client wurde dafür gestartet oder verändert.

**Vier der fünf ausgeschlossenen Frühakten haben spätere Wiederholungen für
denselben engen Prüfumfang.** Für die verbleibende Artefaktprüfung ist zunächst
eine technische Nachprüfung ohne menschliche Bedienung vorgesehen. Daraus folgt
keine pauschale Wiederholung unserer bisherigen Sprachversuche.

Referenzserver: `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Letztes technisch qualifiziertes Clientprodukt:
`7bb564690911d52f6dfe884955ddeb6a27eea6ad`.
Spätere Änderungen an Belegen machen ältere Clientstände nicht zum Endprodukt.

## A – Bereits erhalten oder durch spätere Wiederholung abgedeckt

Die fünf alten Akten bleiben ausdrücklich **ungültig als Serverqualifikation**.
Hier werden nur getrennte spätere Nachweise zugeordnet; kein alter PASS/FAIL
wird überschrieben. Zeitangaben in der Tabelle: 15.10.2026, MESZ; jeweils
aufgezeichnete Aktenzeit, nicht aus Dateizeitstempeln geschätzt.

| ID | Prüfung / ausgesonderte Akte | Erhaltener Nachweis | Konsequenz und Grenze |
| --- | --- | --- | --- |
| A01 | Englischer Golden-ASR-Test: `real-golden-asr.json`, `real-golden-asr-stable.json` | [real-golden-exact.json](EVIDENCE/real-golden-exact.json), 00:50:47, PASS; identischer Testbefehl, dieselbe Fixture und erwarteter/erkannter Text „in being comparatively modern“ | Keine Wiederholung allein wegen dieser zwei alten Akten. Belegt einen echten englischen Backend-Smoke, keine allgemeine deutsche Erkennungsqualität. Das alte FAIL bleibt erhalten. |
| A02 | Wake-Negativprobe: `real-wake-negative.json` | [wake-negative-exact.json](EVIDENCE/wake-negative-exact.json), 01:03:53, PASS; identischer Befehl, Alexa/Jarvis, identische 51,925s-Referenz, Schwelle0,5 und übrige Detektoreinstellungen, null Treffer | Keine Wiederholung allein wegen des alten Nachweises. TV, Umgebungsgeräusche und reale Fehlalarmquote sind damit nicht qualifiziert. |
| A03 | Wake-Ressourcen: `real-wake-resources.json` | [wake-resources-exact-rss.json](EVIDENCE/wake-resources-exact-rss.json), 01:03:48, PASS; gleiche Modellauswahl1/3/25, ONNX,200 Iterationen und Eingabeblöcke; [Hilfsskript](EVIDENCE/measure_wake_resources.py) ergänzt tatsächliche RSS-Messung | Enger Ressourcenversuch erneut vorhanden, mit besserer Speichermessung. Kein Ersatz für30min/100 reale Aktivierungen und keine Behauptung identischer Latenzwerte. |
| A04 | Vier technische Client-/Serverpaarläufe | `recovery-audit/pair`, `ux01/pair`, `ux02/pair`, `ux03-close-sound/pair`, jeweils `validation.json`; volle555-Dateien-Servermanifeste im Audit passend | Serverpin für diese historischen Paarläufe belegt; keine Wiederholung allein wegen der entfernten Instanz. Jeweiligen Clientstand und Testart erhalten. |
| A05 | Modellfreie Prozess-/Protokolltests | 50 Akten mit passenden relevanten Serverquellhashes; vollständige Liste im [Auditinventar](EVIDENCE/server-identity-audit-20261018/inventory.json) | Als modellfreie Tests erhalten. Wirewert `unknown` wird nicht zu einem echten Modell-/Runtimebeleg umgedeutet. |
| A06 | Native EXE-/Wheel-/Frozen-Laufzeitidentität | Acht Runtimeakten mit tatsächlich aufgezeichnetem passendem Servercommit, im Auditinventar einzeln bezeichnet | Historische Runtime-/Buildaussagen erhalten; kein vollständiger M-Fall daraus. |
| A07 | Ursprüngliche und native Audio-Pipeline sowie Recovery-Audit | `real-audio-pipeline.json`, `recovery-audit/native/real-audio-pipeline.json`, `recovery-audit/real-recovery.json`; exakter historischer Runnerhash mit Admissionguard zusätzlich geprüft | Diese drei bloßen Commitdeklarationen besitzen einen geprüften Begleitbeleg. Kein Neustart allein für die Pinzuordnung. Pipeline, Recovery und jeweilige Grenzen getrennt bewerten. |
| A08 | Serverfreie Windowsregression, Unit-/Qt-Tests, isolierte Clipboard-/Modifiertastenprobe, LED-Frames und bewusste WAV-Aufnahmen | Kandidaten-, Log-, Fixture- bzw. Audiohashes der jeweiligen Akten | Bleiben in ihrem serverfreien Umfang erhalten. Fehlendes Serverfeld entwertet sie nicht. Eine integrierte Sprach-/Feedbackaussage benötigt weiterhin ihre eigene Zuordnung. |

A01–A03 sind zeitlich nach dem quellgeprüften Build/Image5aaa17e und vor den
späteren Realtests aufgezeichnet. Die gemeinsame Buildkette mit damaligem
555-Dateien-Abgleich und die unveränderten Befehle/Fixtures tragen diese
Zuordnung. **Die Akten haben keine jeweils eigene In-Container-Vollattestierung.**
Das ist ausdrücklich eine durch mehrere Belege gestützte Zuordnung, keine
nachträglich erfundene Einzelmessung. [Vergleichsdaten und Dateihashes](EVIDENCE/server-identity-audit-20261018/followup-disposition.json).

## B – Zuerst ohne Wiederholung aus Belegen zu klären

„Offen“ bedeutet hier zunächst Aktenarbeit. Eine hohe Plausibilität wird nicht
als endgültiges PASS bewertet. Falls die Verknüpfung nicht belegbar ist, folgt
eine gezielte automatisierte Wiederholung am zulässigen Ziel; keine pauschale
Anforderung, sämtliche Sprachtests erneut zu sprechen.

| ID | Gegenstand | Plausibilität aus Chronologie / vorhandene Bindung | Konkrete Restarbeit / menschlicher Aufwand |
| --- | --- | --- | --- |
| B01 | `real-wake-artifacts.json`:25 Modellartefakte, ONNX-Inputframes und Rezeptivfeld | Erhaltene ältere Quelle hat nur CRLF/LF-Unterschiede; spätere Modellidentitäten sind vorhanden. Kein späterer identischer `artifacts`-Lauf gefunden | Dateihashes/Größen mit Modellmanifest verbinden; Inputshape und Rezeptivfeld nur bei belegbar identischem Werkzeug/Modell übernehmen, sonst offline neu messen. **Kein Sprechen/Hardwarebedienen nötig.** Ganze Altakte bleibt ausgeschlossen. |
| B02 | Frühe Admission und Watchdog mit Media-Stall | Zeitlich nach geprüftem Build, gemeinsamer Endpoint und passende spätere Inventare; zusätzlicher historischer Admissionguard bisher nicht nachgewiesen | Runner-/Trace-/Sessionbindung prüfen. Fehlt sie, kurze technische Wiederholung. Der ursprüngliche kontinuierliche Watchdogversuch war ohnehin FAIL/NOT_PROVEN; siehe C05. |
| B03 | Deutscher Wake-/ASR-Replay und Scores bewusster Aufnahmen | Versionierte echte WAVs und Hashes, tatsächlich gemessene Scores/Pre-Roll-Varianten, gemeinsame geprüfte Infrastruktur | Modell-/Werkzeughash, Konfiguration und Ausführung verknüpfen. Notfalls dieselben WAVs erneut abspielen; keine neuen menschlichen Aufnahmen nötig. Keine Übertragung auf beliebige Live-Fehlalarmraten. |
| B04 |5000ms-Nachsprechwahl, UX01-Sprach-/Leerzeichenversuche, UX02-Sprachversuch | Produkt-, Profil-, Session-/Activationidentitäten und menschliche Antworten vorhanden; zeitlich vollständig nach geprüftem Build. Richtiger Pin **stark plausibel**, nicht in jeder Einzelakte unabhängig attestiert | Native Session-/Admissiontrace an die jeweilige Akte binden. Ältere Clientprodukte bleiben historische Teilnachweise.5000ms-Präferenz und „Beide vollständig, mit Leerzeichen“ bleiben erhalten; kein vollständiges M01/M02/M11-PASS. |
| B05 | UX03-Hörbestätigung, weißes LED-Muster und freie Erprobung | UX03 am Produkt7bb5646, Hörbestätigung mit Session/Activation; LED-Session und Profilhash vorhanden. Gemeinsame geprüfte Instanz macht den Pin **stark plausibel** | Sessionzuordnung vervollständigen. „Stoppton hörbar“ und passende Lautstärke/Dauer bleiben menschliche Beobachtungen; die offene gesamte Feedbackkalibrierung bleibt C06/D10. Freie Erprobung war nie formale Abnahme. |
| B06 | Logstore-ENOSPC/STT-Unabhängigkeit | Akte enthält exakt qualifizierte Image-ID5aaa17e, reale SQLite-ENOSPCs und unveränderte STT-Session; separater später entfernter Faultcontainer | Container-/Imagebeleg an die Akte binden. Kein Grund für neuen menschlichen Sprachversuch. Die tatsächliche Erholung des Logstreams wurde damals nicht bewiesen und bleibt offen. |
| B07 | Zusammenfassungen, Submission und Fallmatrix | Verweisen auf Detailprüfungen; eigene konstante `serverCommit`-Zeile ist kein zusätzlicher Lauf | Beleglinks und Begrenzungen pflegen, nicht solche Verwaltungsakten als neue Tests zählen. |
| B08 | W01- und TV-/Finish-Ereignisse | Genaue Session-/Activation-/Zeit-/Scorebelege; W01 zusätzlich Quellhashes und echter Modellreplay. Gemeinsame Infrastruktur spricht stark für den Pin | Ereigniszuordnung bewahren; fehlendes historisches Live-PCM ist nicht nachträglich rekonstruierbar. Kein Live-Akustikbeweis behaupten. Fehlernachprüfung gehört C03/C04. |

Die24 Akten mit bloßer Commitdeklaration sind im
[maschinenlesbaren Zuordnungsplan](EVIDENCE/server-identity-audit-20261018/followup-disposition.json)
**vollständig** A07/B02–B08 zugeordnet. Dabei wird keine historische
Auditkategorie überschrieben. Die273 Akten ohne Einzelattest sind nicht273
offene Tests; darunter sind serverfreie Tests, Rohbelege und Verwaltung.

## C – Praktische Nachprüfung erforderlich oder noch gar nicht erfolgt

Diese Punkte lassen sich durch die bloße Wahrscheinlichkeit des richtigen Pins
nicht schließen. Sie sind **nicht alle neu durch den Commit-Audit entstanden**.
Keiner der folgenden Abläufe wird durch diese Liste zum Start freigegeben.

| ID | Erforderlicher Ablauf | Warum tatsächlich offen | Vorbereitung / Mensch |
| --- | --- | --- | --- |
| C01 | Gewünschtes Serverziel eindeutig festlegen; dann kontrollierter Verbindungsverlust mit Logs, Tray, Overlay und Wiederverbindung | Der Mensch stoppte seinen normalen Server, der Testclient hing jedoch an127.0.0.1:18020. Diese konkrete Aktion prüfte nicht den verbundenen Endpoint | Erst Ziel, Pin, Modelle und Konfiguration dokumentieren. Keine zusätzliche Instanz anlegen, keinen normalen Server ungefragt stoppen. Danach kontrollierte technische Fehlerprobe; Sichtprüfung mit Benutzer bündeln. M07 mit Preview/Pending bleibt zusätzlich nötig. |
| C02 | Starter im echten normalen Windows-Kontext sowie native Log-UI prüfen | T02: äußerer Desktop konnte das virtualisierte Profil nicht lesen. Starter ist jetzt absichtlich deaktiviert. T01: echte Log-UI-Bestätigung fehlt | Nur nach festgelegtem zulässigem Ziel/Ablage einen passenden Startweg herstellen. Normaler Doppelklick und sichtbare Log-/Serveranzeige danach einmal menschlich bestätigen. Deaktivierung ist kein erfolgreicher Starttest. |
| C03 | W01 nach gesonderter Serverkorrektur: Wake→Timeout→Stille ohne erneute Aktivierung; danach echtes neues Wake | Tatsächlicher Defekt offen, [Server-Issue7](https://github.com/marcosudau-vps/voice-stt-server/issues/7). Exakte historische akustische Ursache ohne PCM NOT_PROVEN | Erst beauftragter unabhängiger Server-FIX/zulässiger Kandidat; dann Modellreplay automatisch und ein gebündelter Livevergleich. Servercodeänderung hier weiterhin nicht freigegeben. |
| C04 | Kontrolliertes `finish` und tatsächliches `cancel`, jeweils Pending-/Terminalverhalten und Overlay prüfen | O01: beobachtet wurde F9=`finish`, kein Cancel; Final/Terminal blieb aus. Ein reiner Overlay-/Canceldefekt ist bisher nicht bewiesen | Zuerst Verarbeitung/Terminal technisch diagnostizieren, dann beide Aktionen mit eindeutiger Belegung testen. Erst anschließend kurzer menschlicher Kontrollblock; keine Wiederholung der zufälligen TV-Situation verlangen. |
| C05 | Watchdog bei kontinuierlicher Sprache: Warnung, Ablauf, legaler Abschluss/Final | Ursprünglicher Versuch wurde durch30s-Queuegrenze vor60s-Watchdog beendet. Späterer PASS mit PCM-Stall prüft einen anderen Ablauf | Zulässige Versuchskonfiguration vorbereiten, keine Sicherheitsgrenze umgehen. Echte vorhandene WAVs können automatisiert laufen; menschliche Sprache nur falls erforderlich. FAIL/NOT_PROVEN des alten Falls bleibt erhalten. |
| C06 | Endgültige Feedback-/Wake-/Overlaykalibrierung am finalen Zielpaar | Menschliche LED-/Overlaywünsche und Wake-Fehlalarme noch nicht abschließend geklärt; Modellzustandsfehler W01 verfälscht einen reinen Schwellenvergleich | Erst technische Blocker, dann Varianten und aktuelle Schritte im Testfenster vorab lesbar; jeder Versuch mit eigenem Start/Wiederholen. Stopptonwahl erhalten, nur betroffene Varianten erneut beurteilen. |

## D – Bereits vorher offene vollständige Pflichtfälle

Dies sind die bestehenden Restabnahmen aus [real-cases.json](EVIDENCE/real-cases.json)
und dem [Testplan](../../../../PLANUNG/REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md).
Keine dieser zwölf Zeilen ist bislang vollständig qualifiziert. Teilbelege aus
A/B dürfen später gezielt angerechnet werden; der Serveraudit erzeugt diese
offenen Gesamtfälle nicht erst neu.

| Fall | Bestehender Status | Noch vollständig nachzuweisender Umfang |
| --- | --- | --- |
| M-01 | NOT_PROVEN | Manual-only mit mehreren Segmenten/Nachsprechen; neuer Start vor altem Final, genau einmalige Ausgabe. |
| M-02 | NOT_PROVEN | Wake-only mit beiden IDs und funktionierenden Controls bei deaktiviertem Manual, keine Doppelactivation. |
| M-03 | NOT_RUN | Both: zeitnaher Hotkey/Wake, Wake während Aufnahme und erneuter Treffer nach Eingabeschluss, First-wins-Latch. |
| M-04 | NOT_PROVEN | Vollständige Hotkey-/Phasenmatrix mit Refresh/Finish/Cancel/None, Fremdkollision, nicht kumulierendem Timer. |
| M-05 | NOT_RUN | Getrennte Run-Pausen, beide aus, Reconnect/Mute/Neustart und korrektes Erhalten/Zurücksetzen. |
| M-06 | NOT_RUN | Reale Mikrofon-/USB-/ReSpeaker-Trennung, LED-Fehler getrennt, Hardwaremute und Wiederanstecken; richtige Cancel-/Drainwirkung. |
| M-07 | NOT_PROVEN | Netz-/Serververlust mit Preview und ausstehenden Finals, separater Logstorefehler; keine alte Einfügung/kein STT-Lock. C01/C04 einbinden. |
| M-08 | NOT_RUN | Einstellungen während Aufnahme: explizites Cancel/Finish/Aufschieben sowie Idle/Drain/Reconnect. |
| M-09 | NOT_RUN | Admin falsch/richtig, Credential Manager anlegen/ersetzen/löschen, Neustart/Serverwechsel, Speicherfehler ohne Secrets. |
| M-10 | NOT_RUN | Frozen Tray/Overlay/Sound/LED, Manual-/Wakeparität und altes Final während neuer Aufnahme. Stoppton-Teilnachweis bleibt vorhanden. |
| M-11 | NOT_PROVEN | Native Ausgabe normal/erhöht, Clipboardkonflikt, Wiedereinfügen, Prozessabbruch nahe Paste ohne unklaren Retry. |
| M-12 | NOT_RUN | Mindestens30min/100 Aktivierungen, positive/negative Wake- und direkte Nutzsprache, wiederholte Netz-/USBfehler, Latenz-/Speichergrenzen und Endkalibrierung. |

## Reihenfolge mit möglichst wenig menschlicher Wiederholung

1. **Aktenarbeit zuerst:** B01–B08 klären, bestehende menschliche Antworten,
   Audiofixtures und erhaltene technische Nachweise weiterverwenden.
2. **Ziel/Blocker festlegen:** C01-Serverziel und zulässige Ablage, gesonderter
   W01-Korrekturweg, offene Terminal-/Log-/Starterfragen. Keine eigenständige
   Wiederanlage des entfernten Servers.
3. **Autonome technische Nachprüfungen:** nur nicht belegbare oder durch
   Änderungen betroffene Integrations-/Modell-/Buildprüfungen am endgültigen Paar;
   Watchdog und Fehlerpfade vor der menschlichen Testphase klären.
4. **Gebündelte Benutzerblöcke:** Sprache/Hotkeys/Ausgabe; USB/Mute/Recovery;
   Feedback/Overlay/Kalibrierung; Credential-/Fremdanwendungen. Alle Schritte
   vorher sichtbar, eigener Start und Wiederholung, entspannte Vorbereitung.
5. **Stabilitätslauf und Abschluss:**30min/100, betroffene Regressionen und
   endgültige Konfiguration/Buildidentität. Bei geändertem Serverpin braucht der
   neue Kandidat seine eigene Qualifikation; historische Belege nicht umetikettieren.

Aktueller Status bleibt **BLOCKED / SERVER_FIX_REQUIRED**, kein REVIEW_READY,
kein neuer M-PASS. Diese Liste senkt unnötige Wiederholungen, sie ersetzt keine
fehlende Pflichtprüfung und erteilt keine neue Betriebs-/Serverfreigabe.
