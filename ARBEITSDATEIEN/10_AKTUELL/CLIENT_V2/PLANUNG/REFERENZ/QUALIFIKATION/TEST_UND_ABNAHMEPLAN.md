# Teststrategie und detaillierte Abnahme

**Aktuelle Branchführung (Revision 9):** Neue Clientpakete laufen auf `feat/client-v2`, ausgehend von 8bab1b3 mit demselben Produktbaum wie a80a6b1. Der erste neue Commit enthält nur Unterlagen; AP-CV2-000 bleibt offen. Historische Distributed-/Featurebezeichnungen unten benennen die analysierten Ausgangsquellen. Kumulative Kandidaten liegen künftig auf untergeordneten Paketbranches, Code und Planpflege gehen als ein Paketaggregat gemeinsam ein. [Verbindliche Branchreferenz](../GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

Historische Baselineprüfung vom 2026-10-04/05: Ausgangslinie ist der vorhandene Featurestand a80a6b1, kanonisch 8bab1b3. Featurebaseline: 1.192 Tests OK; Release-/Migrationsreferenz f625904: 1.147 Tests OK. CV2-000 integriert die nötigen Releaseverbesserungen und qualifiziert einen neuen, heute noch nicht erzeugten Client-SHA. Die alten Testzahlen sind keine bestandene integrierte Baseline. Jedes Paket erhält unabhängig einen Review in frischer Session gemäß [Agentenregelwerk](../GOVERNANCE/AGENTEN_REGELWERK.md).

CV2-000 prüft zusätzlich die erhaltenen Featureassertions, vollständige kombinierte Testsuite, Imports/Version/Ressourcen und isolierte frühe Wheel/sdist-Installation. Vor CV2-010 müssen Namespace-/Releaseintegration, unabhängiger ROOT_PASS, menschliche Übernahmefreigabe und tatsächlicher CV2-000-Paketcommit auf feat/client-v2 gesichert sein. Die endgültige V2-Buildqualifikation bleibt CV2-110; reale Modelle/Hardware verbleiben in IV2-020.

## Früh und paketweise messen

[Inkrementelle Servercheckpoints](INKREMENTELLE_CHECKPOINTS.md) legen für jedes vorhandene AP einen messbaren Zwischenstand fest: Clientcodec an gepinnten Serverquellen ab CV2-010, tatsächlicher Clienttransport am lokalen Server ab CV2-020, danach Mirror/Audio/Controls/Results/Settings und vollständige App schrittweise. IV2-010 ist das finale volle Prozessgate, nicht der erste Serverkontakt. Prüfungen innerhalb der bestehenden Umsetzung-/Reviewläufe durchführen.

## 1. Prüfebenen und Beweisgrenzen

| Ebene | Prüft | Beweist noch nicht |
| --- | --- | --- |
| Wirefixtures / reine Parser | Formen, UUIDs, Audioencoding, Enums, nullable Felder | funktionsfähige Aufnahme oder UI |
| Mirror / Fakeclock / Permutationsfolgen | Raceguards, Resync, Terminals, Versionen | tatsächliche Socketordnung und ASRqualität |
| Service- / Qt-offscreen- / SQLitetests | Controls, Settings, Datenmigration, Secret-/Sideeffectregeln | echte Win32-/USB-/Clipboardhardware |
| integrierter Client mit externen Fakes | reale Komponentenverdrahtung und Threadgrenzen | echter Serverprozess und echtes Modell |
| echter Client-/Serverprozess, modellfreier Referenzrecorder | Wire-/HTTP-/Logkontrakt an konkreten SHAs | Wakekalibrierung oder reale Speech-to-Text-Qualität |
| reale Modelle, Windows, Mikrofon, ReSpeaker, fremde Anwendung | tatsächlich sichtbares Produktverhalten | weitere nicht getestete Builds/Hardwarekombinationen |

Fakes bilden gültige und ungünstige Serverreihenfolgen ab; nur ein Happy-Path-`FakeSTTSession` genügt nicht. Defekte werden mit reproduzierbarem Test isoliert, gezielt korrigiert und erneut einschließlich Regression geprüft.

## 2. Vorgesehene Testzuordnung – Dateinamen sind Vorschläge

Die folgenden Namen sind **geplante Zuordnungen**, keine Pflicht zur Neuanlage und keine bereits ausgeführten V2clienttests. Vorhandene geeignete Tests dürfen erweitert, Namen und Aufteilung passend zum Bestand gewählt werden. Pflichtinhalt bleibt die Funktionsabdeckung; tatsächliche Methoden und Befehle werden in Matrix und Runreport nachgeführt.

| Modul | Paket / Pflichtinhalt |
| --- | --- |
| `tests/test_v2_protocol.py` | CV2-010: Hello/Commands/Acks/18Events/Snapshot/Audioform/Unknownfelder |
| `tests/test_v2_transport.py` | CV2-020: alle Close-/Ackcodes, Retry, Timeout, Event-vor-Ack, generationcleanup |
| `tests/test_v2_mirror.py` | CV2-030: IDs/Overlap/TerminalvorClose/Resync/Interim/Unknownseq |
| `tests/test_v2_audio_recovery.py` | CV2-040: Continuous-Audio, Device/Mute/LEDtrennung, V2Logbootstrap/Retention |
| `tests/test_v2_controls.py` | CV2-050: Rollen-/Phasenmatrix, Pause/Restart, Win32-Konflikte/Rollback |
| `tests/test_v2_results.py` | CV2-060: UUIDhistorymigration, Finaldedup, Interimnegative, Crashunklarheit |
| `tests/test_v2_settings_service.py` | CV2-070: Configmigration, Katalog, Patch/Apply/Bootstrap, NS-Grenzen |
| `tests/test_v2_settings_ui.py` | CV2-080: Scope-/Admin-/Credential-/Apply-/Drain-UI |
| `tests/test_v2_feedback.py` | CV2-090: quellenneutrale Präsentation, Backgroundguard, Domain/Logdedup |
| `tests/test_v2_runtime_integration.py` | CV2-100: realer App/Core/Bridgeverbund mit externen Fakes |
| `tests/test_v2_release.py` | CV2-110: V2-only, Migrationreader, Version, Ressourcen und Paketnamespace |
| `tests/test_v2_cross_repository.py` | IV2-010: echte WS/HTTPprozesse und eingefrorenes Commitpaar |

Jedes Matrixrequirement bekommt eine konkrete Testmethode oder einen konkreten manuellen Report, sobald implementiert. Die geplante Dateizuordnung ersetzt keine Ausführungsevidence.

## 3. Vollständige Regression und Build

Aus Clientrepo, Projektvenv (Python 3.12):

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.\venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
.\venv\Scripts\python.exe -m compileall -q voice_stt_client scripts tests
git diff --check
```

Alle bestehenden relevanten `test_*.py` bleiben Teil der Suite. Testersatz beim V1cut wird einzeln über Requirement und neuen Test begründet; keine breite Skipliste. Bestehende Utilities-, OBS-, Clipboard-, History-, Build-, Single-Instance- und Ressourcenprüfungen bleiben erhalten.

CV2-110 zusätzlich:

```powershell
.\venv\Scripts\python.exe scripts/build.py --clean
.\venv\Scripts\python.exe -m build --sdist --wheel
.\venv\Scripts\python.exe -m twine check dist/*.whl dist/*.tar.gz
```

Wheel in separate temporäre Umgebung installieren und außerhalb Sourcecheckout starten. Import `voice_stt_client`, Version, Config-/Soundressourcen prüfen; Top-Level-core/ui dürfen nicht als Produktpakete auftauchen. Frozen GUI zusätzlich auf echtem Windows starten. Der Build ist kein Publishingauftrag.

Aus Serverrepo in dessen qualifizierter Projektvenv beim IV2-010-Gate:

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/unit
git diff --check
```

Der vollständige **schnelle** Server-unit-Lauf verwendet pytest, damit vorhandene reine pytestklassen wie Settings-Control-Plane mitlaufen. Golden-/echte Modelltests sind separat opt-in und werden mit tatsächlich vorhandenen Modellen/Artefakten im IV2-020-Gate ausgeführt. Fehlende Importdependencies dürfen nicht als optionaler Modelskip verbucht werden.

## 4. Unverzichtbare Race-/Fehlervektoren

1. Astart, SegmentA, Ainputclose, Bstart, verspätetes FinalA; B bleibt aufnehmend.
2. Aterminal vor Ainputclose; foreground bis Close/Snapshot passend erhalten.
3. Bstart vor Ainputclose; Aclose setzt B nicht idle.
4. Adiscard vor ArecordingEnded/accepted; erstes Terminal endgültig.
5. Event-vor-Finishack, Ack mit alter closingversion; kein Phasenrollback.
6. Suppr-/AudioavailabilityAck ohne Event; bestätigter Wert oder Snapshotklärung.
7. Mehrere Interims mit gleicher stateVersion; Vorschau aktualisiert und eventSeq steigt.
8. Final ohne Interim; leeres completed; empty_finaldiscard; failed; gleiche Texte verschiedener Segmente.
9. Seqgap mit Snapshot hinter gepuffertem Final; Text erhalten, keine doppelte Einfügung.
10. Seqgap mit tatsächlich verlorenem Final; incomplete, kein automatisches Logreplay-Paste.
11. Settings-NApatch während A, Aalte/Bneue Effectivewerte; nächste Session erneut bootstrap.
12. NS-Noise/VADpatch applied aber effectivealt; kein behauptetes Reconnectapply.
13. Netzverlust während Configbootstrap / Ackpending / Interim / Clipboardqueue; alte Generation ohne neue Wirkung.
14. Geräteverlust bei Aforeground und Bdrain; Acancel, Bfinal, Session unverändert.
15. Domainfinal und Logfinal+Replay; einzige Textinjektion und einziges fachliches Completionfeedback.
16. Terminalrecovery1011 ohne weitere Clientnachricht; Slot frei, neue Sessionaufnahme möglich.

Die [maschinenlesbaren Client-Szenarien](../KONTRAKTE/VEKTOREN/client-scenarios.json) spezifizieren zusätzlich Ausgangslagen und überprüfbare Effekte. IDs darin sind Platzhalter für Testbindungen, keine wiederzuverwendenden Produktions-IDs.

## 5. Reale Pflichtfälle M-01 bis M-12

Für jeden Fall: Clientbuild-SHA/hash, Server-SHA/digest, Betriebssystem, Geräte/Driver, effektive Settings, ASRmodell, Startzeit, genaue Aktionen, sichtbare Ausgabe, Teststatus und Belegpfad dokumentieren. Nutzertext und Secrets redigieren. Reale Sprachaufnahmen nur bewusst gewählte Testsamples, außerhalb Git.

| ID | Durchführung | Erwartung / Nachweis |
| --- | --- | --- |
| M-01 | Manual-only: Hotkey im idle, zwei Sprechsegmente im Follow-up, Finish, neuer Start vor altem Final | ein Lifecycle pro Activation; mehrere Segmente korrekt und genau einmal im Zielprogramm; kontinuierlicher Stream |
| M-02 | Wake-only: mindestens zwei ausgewählte IDs nacheinander sprechen; Controlhotkeys bedienen | kanonisches Gewinnerwake, gemeinsamer Lifecycle, Controls trotz Manualdisabled; keine doppelte Activation |
| M-03 | Beide: Hotkey und Wakephrase eng benachbart, Wakephrase während Aufnahme, wiederholte Wakephrase nach Close | erster Trigger gewinnt; laufendes Wake ohne direkte Wirkung; neuer erlaubter Hit folgt Latch-/Cooldownregeln |
| M-04 | Primary/Secondary mit refresh/finish/cancel/none in waiting/recording/followup; fremder Keykonflikt | Phasenmatrix, kein kumulativer Timer, keine Doppelregistrierung/Doppelcommands; Collision sichtbar |
| M-05 | Wakepause und Manualpause getrennt, beide effektiv aus; Netzreconnect, Mute, Programmneustart | Session/Runpause erhalten; kein Aktivierungsfenster; Neustart Basiskonfig ohne alte Pause |
| M-06 | USBmikrofon/ReSpeaker entfernen, separat LEDausgang stören, Hardwaremute ein/aus, wieder einstecken | offener Input cancel nur bei realem Audioverlust; Session/ältere Finals erhalten; LEDonly isoliert; keine Autoactivation |
| M-07 | Serverrestart/Netztrennung bei Vorschau und ausstehendem Final; Logstore separat ausfallen lassen | neue Session, nicht veröffentlichte alte Ausgaben interrupted; alter Text erhalten; Logausfall kein STTlock |
| M-08 | Settings während offener Aufnahme ändern; cancel/finish/vormerken; idle mit noch drainenden Ergebnissen reconnecten | nur explizite gewählte Wirkung; ausstehender Verlust sichtbar, Warten möglich; alte/neue Effectivewerte richtig |
| M-09 | AdminKey falsch/richtig, Credential Manager speichern/ersetzen/löschen, Neustart/Serverwechsel, Storeausfallfake ergänzen | nur Guard-PATCH entsperrt; kein mutierter Default beim Check; keine Secrets in Config/Logs/Exports |
| M-10 | Frozen Client Tray/Overlay/Sound/LED, Manual/Wake-Paarvergleich, Aaltfinal während Baufnahme | gleiche fachliche Phasen; Hintergrundimpuls zerstört aktuellen State nicht; Vorschau segmentbezogen |
| M-11 | Clipboardinjektion in normale und elevated Anwendung, Clipboardkonflikt, Wiedereinfügen, Prozessabbruch nahe Paste | korrekte Fehler/Status, keine automatische Nachinjektion unklarer Versuche, Clipboardvertrag erhalten |
| M-12 | 30min und mindestens100Activations; Wakepositive/-negative plus unmittelbar folgende Nutzsprache; wiederholte Netz/USBwechsel | keine unerklärten Task/Queue/Dedupleaseaks; reale Latenz-/Memory-/Wakegrenzmessung und explizite Kalibrierungsbewertung |

Watchdog-Fristen automatisiert mit Fakeclock ausführlich prüfen; mindestens einen echten warning→expiry→Audioverarbeitungslauf mit legalen verkürzten Serverwerten durchführen und im M-04/M-12-Report festhalten. Konfiguration danach auf Ausgangswerte zurücksetzen. Testsamples mit Fernseher-/Dauersprache belegen, dass VAD den Watchdog nicht verlängert.

## 6. Messwerte und Abnahmekriterien

Vor Realtest die Messmethode und Umgebung fixieren: Audioqueuezeit, Commandroundtrip, Snapshotdauer, erste Preview/Final-Latenz, Warmup-/Endmemory, aktive Tasks, Pendingcommands und Hintergrundactivations. Lokale Grenzwerte aus K-04/CV2-040 sind prüfbar. ASRqualität/-latenz werden gegen den konkret verwendeten Server/Modellstand bewertet; dieser Plan behauptet keine allgemeine Echtzeit-SLA.

Nach warmem Start und Ende keine stetig wachsende Menge von Tasks, Pendingcommands, gehaltenen Audiobuffern oder abgeschlossenen Tombstones ohne Retentionkonzept. Neue kurzfristige Caches dokumentieren Umfang/Bound. Historyretention wird nicht mit Runtimeledgerretention verwechselt.

**Automatisiertes Gate PASS** verlangt alle verpflichtenden Parser-/Core-/UI-/Migration-/Build-/Crossrepo-Tests und volle Regression. **Reales Gate ACCEPTED** verlangt alle M-Fälle, tatsächliche Hardware-/Credential-/Clipboard-/ASRnachweise und keine unbegründeten offenen Pflichtbefunde. calibration pending bleibt offen, bis echte positive Audio- und Grenzbelege vorliegen.

## 7. Bereits in dieser Planung ausgeführte Prüfungen

- V1clientbasis f625904: 1.147 Tests, OK; dies ist Baselineevidence, keine V2clientabnahme.
- Serverada13b0: acht relevante Testdateien für Contract, echte Route, Races, stateVersion, Settings, Terminalrecovery, V1/V2boundary und reine Settingsdomain: 307 PASS, 299 Subtests PASS, ein erwarteter optionaler Vektorvergleichskip.
- Dokumentprüfung: interne Links, Paket-/Requirementreferenzen, Dependencies, Vokabular-/Settingsmengen und Vektorhashs sowie unveränderte Bestandsplanung; endgültige Resultate im [Prüfbericht](../../EVIDENCE/PRUEFBERICHT.md).

Hardware-/Golden-/frozen-V2-Smoke wurden für diese reine Planungsaufgabe nicht als bestanden ausgegeben.


## Umsetzungsvorschläge und technische Startwerte im Review

Der Reviewer bewertet Ergebnisse und Nachweise gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Ein abweichender Modul-/Testname, ein anderes UI-Layout oder eine sichere bestehende Datenrepräsentation ist kein eigener Mangel. Lokale Queue-/Timeout-/Retrywerte werden an der begründeten tatsächlichen Konfiguration geprüft; Beispielwerte sind keine Server-SLA. Pflicht sind begrenzter Speicher, kontrolliertes Timeout-/Überlaufverhalten, keine doppelten Nebenwirkungen und vollständige Regression. Jeder Nachweis ist mit Runtime und getesteter Konfiguration im [Evidenzindex](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) verknüpft.
