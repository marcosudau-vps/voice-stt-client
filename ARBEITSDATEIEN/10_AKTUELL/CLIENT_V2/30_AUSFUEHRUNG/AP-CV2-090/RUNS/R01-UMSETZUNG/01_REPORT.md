# AP-CV2-090 / R01-UMSETZUNG – REVIEW_READY

Stand 2026-10-13. Eigenprüfung SELF_CHECK_PASS / REVIEW_READY, unabhängige Abnahme offen. **Status:** REVIEW_READY. Nach PR-Abgabe Umsetzungsschreiben pausiert; kein ROOT_PASS, Merge oder AP100-Start.

## Auftrag, Eingang und Skizze

[Originalauftrag](00_PROMPT_ORIGINAL.md), [Next-step-Skill](../../../../PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md), [Umsetzungsskill](../../../../PLANUNG/SKILLS/voice-stt-client-v2-umsetzen/SKILL.md), [Paketvertrag](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-090.md). Pflichtlektüre und relevante Tests vor der ersten Codeänderung durchgeführt. [Eingangsquellen am Parent](EVIDENCE/input-provenance.json).

Parent `1bc5be893060e0d6a80e1d890102bfffebb73a17`, Branch `work/client-v2/ap-cv2-090`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Ausgangsarbeitsbaum sauber. Gefetchtes origin/feat/client-v2 geprüft; AP080 PR10 MERGED, unabhängiger R02-PASS und menschlicher R03-Squashprompt tatsächlich gelesen. Genau ein Single-Parent-Aggregat auf `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`, Baumgleichheit mit Pakethead `17174f093acb66ccdf06b124e640b4a4d5e9c503` [belegt](EVIDENCE/predecessor-canonicalization.json).

Workflowweite Kandidatencommit-/Paketbranch-Push-/PR-Rechte aus [tatsächlichem AP000-Originalauftrag](../../../AP-CV2-000/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md) gelten weiter. Keine Freigabe für kanonische Übernahme. Skizze vor Implementierung: bestehende Engine/Normalisierung/Mapping um validierten Mirroringang erweitern, unveränderliche quellenneutrale Projektion, getrennte Segmentvorschau und deduplizierte Ausgänge, vorhandene OBSkorrelation, Negativ-/Qt-/Migrationstests, tatsächlicher Domain-/Logcheckpoint, ganze Windowsregression und PR-Abgabe.

## Fachliches Ergebnis und Interfaces

Der bestehende FeedbackEngine erhält `handle_reduction(Reduction)` als V2-Eingang. Die erste permanente Entscheidung projiziert Mirror+Availability+Outputstatus; nachfolgende Ereignisentscheidungen enthalten ausschließlich Liveimpulse. Source ist Diagnosespur. Identische Manual-/Wakephasen benutzen dieselben Regeln, Trayfarbe/-texte und Overlaydarstellung. Legacyeingänge bleiben für die bisherige App erhalten; nach V2adoption sind EventStream und STTfallback dauerhaft diagnostisch, ohne Runtimeautorität.

Foregroundphase und Backgroundpending bleiben getrennt. Idle mit mehreren Drains ist triggerbereit. A-Finals können einen Completecue geben, aber weder B-Aufnahme/-Followupzustand noch dauerhafte LEDregel oder B-Vorschau verdrängen. Snapshotcounts erzeugen keinen Ersatzfinal. Terminalschutz und Vorschauersatz kommen aus dem tatsächlichen Mirror. Overlaytext ist PlainText, segmentgebunden, getrennt vom Statuslabel; keine Zwischentexteinfügung. Anzeige ist auf 128 Vorschauen und 16384 Zeichen je Vorschau begrenzt, Originalresultate bleiben ungekürzt.

Event-/Segment-/Activation-/Deadlineidentitäten deduplizieren One-shots mit vorhandenen begrenzten Tabellen. Loglive und SQLite-Replay können keinen zweiten Sound-/LEDimpuls erzeugen, unabhängig vom opaque Logsegmentlabel. Relative monotone Remaininganzeige läuft nur im Overlaytimer; keine Anzeige erzeugt Cancel/Finish oder verändert den Mirror. Watchdogwarnung gehört zum aktiven Foreground; Folgephase verwendet wieder ihre Inputdeadline. Resync, incomplete, device_off, key_rejected, Log-/History-/Injection-/Adapterfehler und Suppression bleiben unterscheidbare sekundäre Hinweise.

`V2FeedbackConnection` erhält die bisherige Callbackreihenfolge (Controls/Results zuerst, dann Feedback) und isoliert Ausgabeexceptions. `FeedbackSnapshot`/`SegmentPreview` sind unveränderlich. Engineguard sperrt alte Generationen, fremde Sessions, rückläufige Sequenz/Stateversion und die Wiederbelebung einer disconnected Generation. `V2FeedbackOutput` liefert über queued Signal im Qt-Mainthread an tatsächliche Tray-/Overlay- und bestehende Sound-/LEDports. Eigene Generation-/Session-/Revisionguards, begrenzte Impulsidentitäten und Closeinvalidierung sperren stale Queues. Ausgabeexceptions sind unabhängig; stabile Kategorien werden einmal gemeldet. LEFX-/Null-/Simulation bleiben erhalten und mit den bestehenden Suites geprüft.

Der reine Reducer importiert keine Loggingmodule. Sein optionaler `on_observation`-Callback wird am V2-Port mit dem vorhandenen ClientEventEmitter/Ingress verbunden. `client.domain.observed` und `client.feedback.decision` tragen Generation/Session/Activation/Domainsegment-UUID und input_closed-causedByCommandId. Allowlist umfasst nur sichere IDs/Sequenz/Phase/Zähler; keine Transkripte, Secrets, Settings oder unbekannte Wirefelder. Bestehende einfache Zähler und bounded Tabellen bleiben erhalten; keine I/O-Arbeit im Audiohotpath.

Gemeinsame notwendige OBSanschlussänderung: Model/Ingress/Query akzeptieren Domainsegment-UUIDstrings neben Legacyinteger. SQLite INTEGER-Affinity speichert UUIDs bereits als TEXT; keine Schema-/DBmigration. Filter und gemischte Keysetpagination halten beide Typen verlustfrei. Tatsächliche Normalizer-/Speicher-/Filtertests belegen den Anschluss; Änderung nur am korrelationsbetroffenen Feld.

Feedbackmapping bleibt Schema2 und bestehende Foundation. Fehlende V2phasenkeys werden aus vorhandenen Regeln ergänzt; explizite Keys gewinnen. Lokale benutzerdefinierte Regeln, Soundwerte, Profilmigration und Originalbackup bleiben erhalten. `migration_report` nennt übernommene Regeln sowie diagnostisch zurückgestellte Wake-detected-Regeln. Kein heimlicher Configwrite; schema1 bleibt sichtbar reparaturpflichtig. Tatsächliche APIs, Callback-/Closeorder, Sideeffects und Migrationsregeln in [protocol-v2-feedback.md](../../../../../../../docs/protocol-v2-feedback.md).

## Fehlerrepros und fachliche Grenzen

Voränderungsbaseline 185 PASS. Ein zuerst falsch benanntes Baseline-Testmodul erzeugte ausschließlich einen Importfehler; der korrigierte vollständige relevante Lauf war vor Produktänderung grün. Frühe Qtprobe fand einen auf B-Aufnahme hängenbleibenden Aktivierungsstatus; Foreground-/Phasenwechsel räumt jetzt den transienten Status auf. Der OBSspeichertest fand zunächst eine falsche Fixtureklasse; der tatsächliche SQLiteLogStore und gemischte Querypfad werden jetzt geprüft.

Die erste vollständige Windowsregression reproduzierte den geschützten OBS-040-Architekturtest: direkter Loggingimport im reinen Reducer. Minimal korrigiert durch generischen non-throwing Hook mit Sinkanbindung am V2-Port. Der ursprüngliche Architekturtest bleibt unverändert. [Vollständiges FAIL-Diagnoselog](EVIDENCE/before-pure-boundary-fix-windows-full-unittest.txt) bleibt erhalten; danach erneute gezielte und ganze Regression plus realer Checkpoint, kein ungeklärter Fehler.

Serverprüfung hatte zunächst einen falschen Gitrepositorypfad und anschließend die unzulässige Annahme, opaque Loglabels müssten byteverschieden zu Domain-UUIDs sein. Richtiger Sourcevergleich gegen Serverrepository main am fest gepinnten ada13b0; Assertion prüft jetzt tatsächlichen fehlenden Einfluss auf Domainidentität/Output statt eine unbelegte IDwertannahme. Kein Serverprodukt geändert und keine Sourceprüfung gelockert.

Checkpoint verwendet reale Produktions-FastAPI, SQLiteeventstore, zwei TCP-WebSocketkanäle, V2Session/Mirror/Controls/DualSessionCoordinator/EventStreamTransport und queued Qt-Ausgabe bis zu echten Tray-/Overlaywidgets. PCM/Recorder/VAD/ASRscheduler und physische Sound-/LEDsinks sind kontrollierte Grenzen. Synthetic Preview/Finaltexte bleiben Testdaten. Kein Kontakt zum produktiven Server, keine Nutzeraudio-/DB-/Secretablage. Die zwei künstlich fehlschlagenden physischen Sinks prüfen Audio-/Control-/Finalereignisfortgang. Reconnect erhält neuen Generation-/Sessionkontext ohne Finalimpulsreplay.

Reguläre Appverdrahtung samt bestehendem Resultat-/History-/Injectionport bleibt AP100. Physischer Mikrofon-/Wake-/ASR-/Sound-/LED-Wahrnehmungsnachweis bleibt AP-IV2-020, Server-Distributed offen. Zwischencheckpoint qualifiziert tatsächliche Client-/Serverpfade, keine reale Gesamtabnahme.

## Validierung und Abgabe

[Windowsmanifest](EVIDENCE/windows-validation.json) bindet Runtime/Projektvenv, Befehle, Exitcodes, Dauer, vollständige Loghashes, lokale Sourcebytes, qualifizierte Gitblobs und den genauen staged binären Produktdiff am Parent. Gitblobs identifizieren normalisierte veröffentlichte Bytes; finaler Head/Tree steht extern in der PR-Beschreibung. Nach einer abschließenden Zeichencodierungs-/Whitespacekorrektur nochmals der gesamte Qualifikationslauf einschließlich aller Testsubprozesse und beider Diffchecks am endgültigen Produkt-/Teststand ausgeführt. Nach erfolgreicher Qualification keine Produkt-/Teständerungen. [FB-01 bis FB-09 einzeln](EVIDENCE/requirement-coverage.md) bleiben CLIENT OPEN bis unabhängiger Abnahme.

| Prüfung | Ergebnis |
| --- | --- |
| Relevante Baseline vor erster Änderung | 185 PASS |
| Neue V2-Feedbacktests einschließlich Qt-Thread-/Faultfälle | 38 PASS, sämtliche Fälle in Gesamtsuite |
| Gezielte Regression mit `-W error` einschließlich OBS-040-Importgrenze | 289 PASS |
| Tatsächlicher gepinnter Domain-/Log-/Replay-/Qtcheckpoint | 18 Checks PASS |
| Gesamte Windows-Clientsuite | 1551 PASS |
| compileall, diff/cached --check | PASS |
| Kandidaten-/Log-/FB-/Aktenbindung | separate Abgabeprüfung PASS |

[Evidenzindex](EVIDENCE/INDEX.md) enthält vollständige Befehle/Artefakthashes. Dokumentation, Matrix/Requirements, Manifest, WORKFLOW_STATUS und operative Einstiege auf REVIEW_READY aktualisiert. AP080-Übernahme ausschließlich in aktueller Paket-/Planpflege nachgeführt; historische Reports unverändert. Genau ein Runmeilenstein. Finaler Paket-PR gegen feat/client-v2 wird angehängt, mit Head/Tree/CI-Kurzfassung identifiziert; Arbeitsbaum bei Abgabe sauber. Nächste Aktion: frisches unabhängiges Review, danach ausdrücklicher menschlicher Übernahmeprompt. Kein Auto-Merge und kein Folgepaketstart.
