# AP-CV2-040 / R03 – Korrektur von R02-F01 und R02-F02

Status **REVIEW_READY**, technische Selbstqualifikation; erneute unabhängige
Abnahme offen. 2026-10-12, PR #6, `work/client-v2/ap-cv2-040`, kanonischer
Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`, Server
`ada13b011e1d3829f78e7f389e3b927795a2b3be`.

[Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md),
[unveränderter unabhängiger R02-Bericht](../R02-ABNAHME/01_REPORT.md).
Reviewunterlagen vor Korrektur per Fetch/Fast-forward übernommen: Start
`146839809bc234a2dfe4f02cea37d7ce2e4ff480`; sauberer Workingtree, derselbe
PR-Head und unveränderter Featureparent geprüft. Keine fremde WIP oder
Serverproduktänderungen. Vor Produktänderung **54 relevante Tests PASS**;
[Basislog](EVIDENCE/baseline-targeted.txt).

## Befundbewertung und Umsetzungsskizze

**Beide Findings sind berechtigt und werden anerkannt.** Es gibt keinen
zurückgewiesenen Befund und keine Absenkung von Kriterien. Die statische
R02-Analyse wird durch fünf eigene deterministische Laufzeitreproduktionen
bestätigt: Gerätverlust, Hardwaremute und ausgefallene Capture meldeten
negative Availability erst nach Rückkehr des blockierten Stops; Timeout einer
nativen Operation und Timeout des Stops ließen jeweils den Logtransport aktiv.
[Reprolog mit fünf erwarteten FAILs](EVIDENCE/repro-before-fix.txt),
[Identität und Grenzen](EVIDENCE/repro-identity.json).
Nur die neuen Reprotests waren dabei ergänzt; Produktcode entsprach dem
R02-Kandidaten. Die Repro-FAILs sind Fehlernachweise und kein aktuelles
Qualifikationsergebnis.

Skizze vor Änderung: negative Availability vor den möglicherweise blockierenden
Treiberstop ziehen, das vorhandene lokale PCM-Gate beibehalten; unabhängige
Logressourcen in finally aufräumen und Closing/erfolgreiches Cleanup trennen,
damit ein erneuter close-Aufruf einen unvollständigen nativen Vorgang joinen
kann. Keine Änderungen an Serverkontrakt, Domainmirror, Capturedriver,
Logtransport, Nutzerkonfiguration, Schema oder Dependencies.

## CV2-040-R02-F01 – Servermeldung vor nativem Stop

Ursache: `_lifecycle()` wartete in Device-/Mute- und Deaddevicepfad auf
`_stop_capture()`, ehe `_report_availability(False)` erreicht wurde. Die lokale
PCM-Barriere allein informiert den Server nicht über sein offenes Input.

Korrektur in `v2_media.py`: zuerst lokales Gate schließen und Captureavailability
false setzen, dann negative Availability auf dem aktuellen Binding anfordern
und bestätigen; erst danach den nativen Stop awaiten. Die ACK-/Bindingguards
bleiben erhalten. Dadurch cancelt der Server rechtzeitig die offene Activation;
ein langsamer Treiber blockiert nicht länger diese Meldung. Recovery öffnet
weiterhin erst nach tatsächlichem Gerätestart und positiver Bestätigung,
kein automatischer Trigger und keine Änderung gewünschter Suppression.

Neue Testmethoden in `tests.test_v2_audio_recovery.Media`:

- `test_device_loss_reports_false_before_blocked_native_stop`
- `test_hardware_mute_reports_false_before_blocked_native_stop`
- `test_dead_device_reports_false_before_blocked_native_stop`

Kontrollierte Thread-Events halten den Stop offen. Noch vor Freigabe wird die
bestätigte false-Meldung geprüft, daneben gesperrte alte Callbackframes,
leere Queue und erhaltenes Binding. Echter Servernachweis:
`devices/false_acked_before_blocked_native_stop`,
`devices/open_activation_cancelled`, `devices/session_and_older_drain_preserved`
und `background/older_final_while_native_stop_blocked`. Der modellfreie ältere
Finaljob wird ausdrücklich abgeschlossen, während der Treiberstop noch
blockiert ist; der reale Controller/Ledger publiziert ihn genau einmal.

Bewertung: **SELF_CHECK_FIXED, unabhängiger Recheck erforderlich**.

## CV2-040-R02-F02 – Fehlerisoliertes, wiederholbares Cleanup

Ursache: `_closed=True` bedeutete zugleich Abschluss. Ein natives wait_for
konnte vor `logs.shutdown()` aussteigen; der zweite close-Aufruf kehrte danach
sofort zurück. Das bestätigte Reprolog zeigt in beiden Varianten weiterhin
einen aktiven Logtransport.

Korrektur: `_closed` sperrt neue Arbeit, `_cleanup_complete` wird erst nach
vollständig erfolgreichem Shutdown gesetzt. `close()` serialisiert Aufrufe,
stoppt Transport, cancelt/joint Sender/Lifecycle und versucht natives Cleanup
mit dem bisherigen Budget. Der separate Logshutdown wird unabhängig davon
in finally ausgeführt, auch bei Transportfehler oder externer Cancellation.
Timeout wird weiterhin an den Owner weitergegeben. Die laufende native Task
bleibt bei Timeout gehalten; erneutes close joint sie vor einem weiteren Stop.
Kein zweiter paralleler Treiberaufruf, kein vorgetäuschter Erfolg.

Neue Methoden in `tests.test_v2_audio_recovery.Media`:

- `test_native_operation_timeout_closes_logs_and_retries_cleanup`
- `test_native_stop_timeout_closes_logs_and_retries_cleanup`
- `test_cancelled_close_still_cleans_logs_and_can_retry`

Nach Timeout werden aktive Logtransportzahl, gestoppter Transport und erledigte
Log-/Expiry-Tasks geprüft. Ein weiterer close bei weiterhin blockiertem Treiber
meldet erneut Timeout. Nach Freigabe beendet close Capture, joint die native
Operation und wird anschließend idempotent. Cancellation ist zusätzlich
nachgewiesen. Die Tests verwenden 100 ms für den absichtlich überschrittenen
Timeout, nach Eventfreigabe 1 s; ein erster 20-ms-Testwert erfasste gelegentlich
Windows-Executorbereitstellung statt des kontrollierten Treiberhangs. Das
Produktbudget bleibt unverändert 3 s.

Echte Logsocketprüfung im Servercheckpoint:
`shutdown/native_stop_timeout_reported`,
`shutdown/native_timeout_real_logs_clean`,
`shutdown/retry_joins_native_stop`. Reale Logtransport-/Expiry-Tasks sind beendet
und der Logtransport STOPPED, obwohl der native Stop noch nicht freigegeben ist.

Bewertung: **SELF_CHECK_FIXED, unabhängiger Recheck erforderlich**.

## Neue vollständige Qualifikation

| Prüfung | Ergebnis | Vollständige Belege |
| --- | --- | --- |
| Vorherbaseline | PASS,54 Tests | [Log](EVIDENCE/baseline-targeted.txt) |
| Repro auf altem Produktstand | Erwartet FAIL,5/5 | [Log](EVIDENCE/repro-before-fix.txt) |
| Neue Audioregression | PASS,34 Tests | [Log](EVIDENCE/focused-after-fix.txt) |
| Gezielte Gesamtabdeckung, warnings=error | PASS,228 Tests | [Log](EVIDENCE/targeted-unittest.txt) |
| Vollständige Windows-Clientsuite | PASS,1373 Tests, kein Skip | [Log](EVIDENCE/windows-full-unittest.txt) |
| Gepinnter tatsächlicher Client-/Servercheckpoint | PASS,46 Fälle/46 bytegeprüfte Quellen | [JSON](EVIDENCE/server-audio-checkpoint.json), [stderr](EVIDENCE/server-audio-checkpoint.json.stderr.txt) |
| compileall / Gitdiff / Aktenprüfung | PASS | [Runtime und Befehle](EVIDENCE/windows-validation.json), [Abgabeprüfung](EVIDENCE/submission-validation.json) |

Getestete Basis ist die übernommene Reviewspitze `146839809bc234a2dfe4f02cea37d7ce2e4ff480`,
nicht ein neuer kanonischer Featurecommit. Genauer gestagter
[Produkt-/Test-/Harnessdiff](EVIDENCE/tested-product.patch), vollständige
Gitblobliste, lokale Quellbytehashes vor/nach Tests und sämtliche Loghashes
binden die Qualifikation an den korrigierten Kandidaten. Erst danach folgen
administrative Unterlagen; Produkt-/Test-/Konfigurationsblobs werden bei
Veröffentlichung nochmals verglichen. Alle23 Requirements besitzen neue
Korrekturbelege, ursprüngliche Implementation-/Reviewbelege bleiben erhalten.
[Coverage](EVIDENCE/requirement-coverage.md).

## Schnittstellen, Grenzen und Übergabe

[Öffentliche API](../../../../../../../docs/protocol-v2-media.md) aktualisiert.
Keine neuen öffentlichen Datentypen, Configkeys, Settings-/History- oder
Credentialmigration. Callback- und Generationguards bleiben erhalten;
Availability-Reihenfolge und Retrysemantik von close sind oben ausdrücklich
festgelegt. R01-/R02-Originalprompts und abgeschlossene Berichte unverändert.

Der Server bleibt ada13b0, tatsächliche FastAPI/WS/SQLite-/PCM-/Controllerpfade
und alle bisherigen Checkpointfälle bleiben erhalten. Ergänzte Faultinputs
sind kontrollierte Thread-Events um Capturestop; reale PortAudiohardware und
ASR/Wakequalität weiterhin NOT_PROVEN und spätere IV2-Gates. Nativer Treiberhang
kann nicht durch asyncio hart abgebrochen werden; Logs werden trotzdem
aufgeräumt, Timeout bleibt sichtbar und der native Vorgang bleibt joinbar.
Qt-/Settingskomposition weiterhin CV2-100/070, kein Folgepaket begonnen.

Derselbe PR #6 wird kumulativ aktualisiert. Neue Abgabe **REVIEW_READY**;
beide R02-Finding-IDs bleiben als unabhängig nachzuprüfende Befunde verlinkt,
keine selbst erteilte Schließung/ROOT_PASS. Schreibhoheit nach finaler Übergabe
pausiert. Nächste Aktion: neuer unabhängiger Review des gesamten Kandidaten
mit Fokus F01/F02; kanonische Übernahme erst nach PASS und menschlichem Prompt.
