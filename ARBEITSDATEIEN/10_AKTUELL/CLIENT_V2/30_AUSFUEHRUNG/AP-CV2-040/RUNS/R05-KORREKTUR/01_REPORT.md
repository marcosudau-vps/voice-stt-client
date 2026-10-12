# AP-CV2-040 / R05 – Cancellation beim Task-Join und Logclose

**REVIEW_READY**, technische Selbstqualifikation; unabhängige Abnahme offen.
2026-10-12, [Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md),
[unveränderter R04-Review](../R04-ABNAHME/01_REPORT.md), PR #6.
Paketbranch `work/client-v2/ap-cv2-040`, kanonischer Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`,
Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

## Ausgangsstand und Bewertung

R04-Unterlagen im sauberen Checkout fetch/fast-forward übernommen. Tatsächlicher
Start/testedBase `1289991613d4577e535eb6067ca332240488c790` entspricht dem PR-Head; feat/client-v2 bleibt
AP030-Aggregat `3df342c3a7cacaa1226743c4d9bee674e94d33db`, PR #5 tatsächlich gemergt, unabhängiger PASS,
menschliche Freigabe, Single-Parent-/Baumprovenienz im vorhandenen Vorgängernachweis
erneut geprüft. Workflowrechte aus AP000/R01; neuer menschlicher Korrekturauftrag.
R05-Schreibhoheit vor Änderung im PR bekanntgemacht. Keine fremde WIP.

**Der einzige offene Abnahmeblocker CV2-040-R02-F02 ist berechtigt.**
F01 bleibt unabhängig CLOSED_R04. R03 behob native Timeoutfälle, ließ aber den
Task-Join außerhalb des Log-finally. Zusätzlich konnte Cancellation beim direkten
Await des Koordinator-Shutdowns dessen abgetrennte Ressourcen verwaisen lassen.
Der alte Cancellationtest traf nur den späteren nativen Wait. Keine Finding-
Zurückweisung, keine Kriterienabsenkung und kein eigener ROOT_PASS.

Vor Produktänderung [60 Baseline-Tests PASS](EVIDENCE/baseline-targeted.txt),
[Befehls-/Basisidentität](EVIDENCE/baseline-identity.json). Drei neue Kandidaten-
Repros auf unverändertem R04-Produktstand [FAIL wie erwartet](EVIDENCE/repro-before-fix.txt):
Sender-/Lifecycle-Join lassen Logtransport aktiv, Logclose-Abbruch lässt die
captured Log-/Expiry-Tasks unerledigt. [Reproidentität](EVIDENCE/repro-identity.json)
enthält vollständigen Befehl, Exitcode, Loghash und leeren Produktdiff. Nur die
Testergänzung war vorhanden. Ein erster Fixtureentwurf erreichte bei Lifecycle
den früheren Transportstop; die finale Synchronisation wartet ausdrücklich auf
Transportstop UND gehaltene Task-Cleanup-Phase, bevor Close gecancelt wird.

Umsetzungsskizze vor Produktänderung: Task-Join unter äußerstes Log-finally ziehen;
unabhängigen Logshutdown vor Owner-Cancellation schützen, Budget und Retry erhalten.
Nur Mediaadapter, dessen Tests und vorhandener Serverharness geändert.

## Gezielte Korrektur und Anschlussstellen

`V2MediaConnection.close()` schützt nun Transportstop, Sender-/Lifecycle-Join
und native Operationen durch das äußerste Log-finally. Ein begrenzter geschützter
Task-Join lässt ausstehende Tasks bei Timeout/Cancellation referenziert; Retry
joint sie ohne zweites Cancel in ihrer Cleanup-Phase. Abgeschlossene Referenzen
werden entfernt. Gates/Queue/Callback werden weiterhin sofort gesperrt.

`_shutdown_logs()` erzeugt genau einen gehaltenen Koordinator-Shutdowntask.
Shield schützt dessen echte Ressourcenbereinigung. Cancellation des Owners,
auch wiederholte, wird bis zum abgeschlossenen Cleanup aufgeschoben und dann
weitergegeben. Das feste Deadlinebudget (Shutdowntimeout + 3 s) wird nicht
verlängert. Timeout meldet unvollständiges Cleanup und hält denselben Logtask
joinbar. Retry umgeht dadurch den bereits gesetzten shutdown-Fastpath des
Koordinators. `_cleanup_complete` bleibt bei jedem Fehler/Abbruch false und
wird erst nach erfolgreichem Retry true. Kein vorgetäuschter Shutdownerfolg.

Die bestehende Timeout-/Native-Retrykorrektur und F01-Reihenfolge bleiben
unverändert wirksam. Kein neuer Configkey, keine Änderungen am Koordinator,
Capturedriver, Serververtrag, Domainmirror, Credentials, History, Settings oder
Dependencies. [Öffentliche Close-Semantik](../../../../../../../docs/protocol-v2-media.md)
aktualisiert. Task-Join erhält dasselbe Defaultbudget 3 s wie native Operationen;
Tests setzen 100 ms für absichtlich blockierte Joins, Logtimeouttest prüft 3,1 s.

## Neue Nachweise je Fehlerfenster

Fünf neue Tests, sämtliche bisherigen Tests erhalten:

- `tests.test_v2_audio_recovery.Media.test_cancel_during_sender_join_cleans_logs_and_retries`
- `tests.test_v2_audio_recovery.Media.test_cancel_during_lifecycle_join_cleans_logs_and_retries`
- `tests.test_v2_audio_recovery.Media.test_repeated_cancel_during_logclose_joins_cleanup_before_raising`
- `tests.test_v2_audio_recovery.Media.test_task_join_timeout_cleans_logs_and_retains_task_for_retry`
- `tests.test_v2_audio_recovery.Media.test_logclose_timeout_retains_pending_cleanup_for_retry`

Aktiver Logtransport mit festgehaltenen Log-/Expiry-Taskhandles; Sender/Lifecycle
in echter eigener Cancel-Cleanup-Phase gehalten. Danach Cancel am Task-Join;
CancelledError bleibt sichtbar, Logs sind geschlossen, erneutes Close beendet
restliches Cleanup. Wiederholtes Cancel trifft kontrolliert tatsächlichen
Logtransportstop; Assertions prüfen erledigte Tasks und echten Stop, nicht nur
die bereits abgetrennte Transportzahl. Timeouttests halten Sender bzw. Logshutdown
über Budget, prüfen referenzierte laufende Tasks/false-Erfolgsflag und erfolgreiche
Freigabe/Retry mit demselben Logtask. Kein sleep-basiertes Erraten des Fehlerfensters.

Echter Checkpoint am bytegeprüften Serverada13b0 erweitert um sechs Fälle:

- `shutdown/task_join_cancel_reported`
- `shutdown/task_join_cancel_real_logs_clean`
- `shutdown/task_join_cancel_retry_complete`
- `shutdown/logclose_cancel_reported`
- `shutdown/logclose_cancel_real_logs_clean`
- `shutdown/logclose_cancel_retry_complete`

Reale READY-Sessions mit LIVE-Logsocket, kontrollierter Sender-Cleanup bzw.
Logtransportstop. Cancel wird an Owner gemeldet; realer Logtransport STOPPED,
Log-/Expiry-Tasks erledigt, danach erfolgreicher Retry. Alle bisherigen 46
Serverfälle bleiben vorhanden. Nur Faultsteuerung an Clientgrenzen ergänzt;
serverseitige Produktionsquellen unverändert, keine Netzwerk-/Credentials-
 oder Nutzerdaten von produktiven Diensten verwendet.

## Vollständige neue Qualifikation

| Prüfung | Ergebnis | Vollständiger Beleg |
| --- | --- | --- |
| Vorherbaseline | PASS, 60 | [Log](EVIDENCE/baseline-targeted.txt) |
| Neue Repros auf alter Produktbasis | 3 erwartete FAILs | [Log](EVIDENCE/repro-before-fix.txt) |
| Gezielte Regression mit warnings=error | PASS, 233 | [Log](EVIDENCE/targeted-unittest.txt) |
| Gesamte Windows-Clientsuite | PASS, 1378, kein Skip | [Log](EVIDENCE/windows-full-unittest.txt) |
| Gepinnter tatsächlicher Servercheckpoint | PASS, 52 Fälle/46 Quellen | [JSON](EVIDENCE/server-audio-checkpoint.json), [stderr](EVIDENCE/server-audio-checkpoint.json.stderr.txt) |
| compileall, Gitdiff, Arbeitsakten | PASS | [Manifest](EVIDENCE/windows-validation.json), [Abgabeprüfung](EVIDENCE/submission-validation.json) |

Qualifiziertes Produkt/Test/Harness auf testedBase `1289991613d4577e535eb6067ca332240488c790` plus
[exaktem staged Diff](EVIDENCE/tested-product.patch), SHA256 `d74675ad1ffea71f812fbfd248c95f0212ff5e308f3ffd606d39995130c658f0`.
Runtime-/Befehls-/Exit-/Loghash-/Gitblobbindung und identische Quellbytehashes
vor/nach Tests im Windowsmanifest. Administrative Unterlagen danach; qualifizierte
Blobs/exakter Diff vor Commit und veröffentlichter Baum nach Push erneut geprüft.
Alle 23 Requirements haben konkrete R05-Methoden-/Serverbelege:
[Coverage](EVIDENCE/requirement-coverage.md), Requirements-JSON und Matrix synchron.
Fachliche Definitionen, Owner, Kontrakte, Quellen und CLIENT OPEN unverändert.
Historische R01–R04-Akten unangetastet; früherer PASS nicht fortgeschrieben.

## Volltest-Wiederholung und Diagnose

Der erste Qualifikationsversuch überschritt das unveränderte 240-s-Harnesslimit;
kein PASS und kein bestimmter Produktfehler daraus abgeleitet. Das ursprüngliche
Script schrieb bei Timeout keinen Teiloutput; der konkrete Blockpunkt ist daher
nicht belegt. Die Diagnoseregression mit periodischem faulthandler-Stackdump
bestand sämtliche 1378 Tests in 109,420 s. Danach bestand die reguläre vollständige
Qualifikation mit unverändertem Produkt/Test/Config und unverändertem 240-s-Limit
1378 Tests in 115,268 s. [Wiederholungsidentität](EVIDENCE/qualification-retry.json),
[vollständiger Diagnoselog](EVIDENCE/windows-full-diagnostic.txt). Das R05-Harness
sichert Timeoutoutput künftig ebenfalls; keine Assertions entfernt, Tests geskippt
oder Produktbudgets für den Retry verändert. Ursache des ersten einzelnen
Harness-Timeouts bleibt nicht reproduziert, kein erfundener Entlastungsnachweis.

## Grenzen und erneute Übergabe

**F02 SELF_CHECK_FIXED_R05, unabhängige Bestätigung offen.** F01 CLOSED_R04.
Derselbe kumulative PR #6, neuer Kandidaten-SHA/Tree nach Commit aus Git im PR
und Übergabekommentar. Workingtree sauber, writeOwner=null nach Übergabe;
Branch danach pausiert. Frische unabhängige Session prüft gesamten Kandidaten.
Kein Merge, Folgepaket, Main-/Tag-/Release-/Server-Distributed-Promotion.

Reales Mikrofon, USB/LED/Mutehardware, ASR und Wakequalität weiterhin NOT_PROVEN
und spätere IV2-Gates; Qt-/Settingskomposition CV2-100/070 unverändert. Ein nativer
Treiberhang ist nicht hart asyncio-abbrechbar. Bei Log-/Taskbudgetüberschreitung
bleibt tatsächliches Cleanup unvollständig und referenziert; der Owner muss
erneut Close ausführen. Kein globaler Coordinator-Refactor für diesen Fix.
