# AP-CV2-040 / R02 – Unabhängige technische Abnahme

**Verdict: CHANGES_REQUIRED.** Fachlich geprüfter Kandidat, keine kanonische Übernahme. Datum 2026-10-12 (Europe/Berlin). Eigenständige Session ohne Mitwirkung an R01. [Originalauftrag](00_PROMPT_ORIGINAL.md), [Belegindex](EVIDENCE/INDEX.md), [Paketakte](../../00_PAKET.md).

## Git- und Kandidatenidentität

| Feld | Tatsächlicher Wert |
| --- | --- |
| Repository | `marcosudau-vps/voice-stt-client` |
| PR/Base | [#6](https://github.com/marcosudau-vps/voice-stt-client/pull/6) → `feat/client-v2` |
| Kandidatenbranch | `work/client-v2/ap-cv2-040` |
| **reviewed_sha** | `79cffe19b103cfcc325f5c15a7532da763ff3f9c` |
| **reviewed_tree** | `1449c1b71015d978349826891644565b3711e17a` |
| canonical_parent | `3df342c3a7cacaa1226743c4d9bee674e94d33db` |
| qualifizierter Implementierungscommit | `efd8362fc63bc8a98fdbc9edccd4b4074c659393` (`dd63a7822a39ca332a2a62a113ad75b16bf9397b`) |
| gepinnter Server | `ada13b011e1d3829f78e7f389e3b927795a2b3be` |
| Schreibhoheit bei Übergabe | `writeOwner=null`, Paket-PR vor Review unverändert |
| Urteil | `CHANGES_REQUIRED`, offene Findings: `CV2-040-R02-F01`, `CV2-040-R02-F02` |

PR-Metadaten, Git-Commits, Parentkette, veröffentlichte commitgebundene Dateien und die 49 geänderten PR-Dateien selbst abgerufen. Der kanonische Parent ist die tatsächliche PR-#5-Squashspitze, deren Git-Commit einen einzigen Parent besitzt. R01-Produktstand ist gegenüber dem eingereichten Head unverändert; die danach geänderten Dateien sind administrative Unterlagen.

## Fachlicher Prüfgegenstand

Geprüft wurden [AP-CV2-040](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-040.md), die referenzierten Verträge K-01/K-04, der vollständige veröffentlichte PR-Diff und die betroffenen Komponenten `v2_media.py`, `audio_capture.py`, `session_coordinator.py`, `event_stream.py`, `event_protocol.py`, `event_cursor_store.py`, `event_models.py`, der Crossrepo-Audio-Checkpoint-Harness sowie relevante Tests. Positiv nachvollzogen: generationgebundene PCMqueue und Callbackguard, die getrennte LEDverfügbarkeit, kontinuierliches Capture erst nach config-ready, Logcursorbindung an Session/Channels und die beobachtende, nicht domainautoritative Logverarbeitung. Keine neuen serverseitigen Produktänderungen.

Die 23 Paketrequirements AUDIO-01..AUDIO-12 sowie LOG-01..LOG-11 wurden einzeln anhand der [Methodenzuordnung](../R01-UMSETZUNG/EVIDENCE/requirement-coverage.md), vorhandener Tests und Serverfälle zugeordnet. Diese Nachweise reichen für die unten aufgeführten zwei bisher ungeprüften Fehlerpfade nicht aus. Fachliche Kriterien/Owner/Requirementtexte wurden im Review nicht verändert.

## Umsetzungstests – unabhängige Fremdbelegprüfung

| Prüfung | Extern im Umsetzungslauf ausgeführt | Unabhängige Beurteilung |
| --- | --- | --- |
| Windows-Vollsuite | **PASS**, 1367 Tests, keine dokumentierten Skips, Exit 0, 103.513 s Testlauf | **PASS als überprüfter Fremdbeleg**, eigene Wiederholung NOT_RUN |
| Gezielte Regression, warnings=error | **PASS**, 222 Tests, Exit 0 | **PASS als überprüfter Fremdbeleg**, eigene Wiederholung NOT_RUN |
| Realer Client-/Servercheckpoint | **PASS**, 41 Fälle, 46 bytegeprüfte gepinnte Serverquellen | **PASS als überprüfter Fremdbeleg**, eigene Ausführung NOT_RUN |
| compileall / git diff --check | **PASS**, Exit 0 / R01-Diffprüfung | **PASS als überprüfter Fremdbeleg**, eigene Runtimeausführung NOT_RUN |
| Physisches Mikrofon/USB/LED, ASR/Wakequalität | nicht ausgeführt | **SKIPPED_EXPECTED/NOT_PROVEN**, als spätere IV2-020-Gates ausgewiesen |

Geprüfte Quelle: [Windowsmanifest](../R01-UMSETZUNG/EVIDENCE/windows-validation.json), [vollständiges Windowslog](../R01-UMSETZUNG/EVIDENCE/windows-full-unittest.txt), [gezieltes Testlog](../R01-UMSETZUNG/EVIDENCE/targeted-unittest.txt), [Servercheckpoint](../R01-UMSETZUNG/EVIDENCE/server-audio-checkpoint.json). Windows 11, Python 3.12.10, projektgebundene venv, Qt offscreen und Kommandos samt Exitcodes sind enthalten.

**Eigene Identitätsprüfung:** Die GitHub-Blob-IDs sämtlicher elf im PR geänderten Produkt-, Test- und Skriptdateien wurden separat gegen `qualifiedGitBlobs` des versionierten Windowsmanifests verglichen: **11/11 identisch**. Das manifeste Ergebnis verbindet Basis, exakten getesteten Produktdiff und vollständige Logs mit dem veröffentlichten Stand. Es wurden keine Nach-Qualifikations-Produkt-/Teständerungen festgestellt. Nicht von diesem Reviewer behauptet: eigene Windows-/Server-/Hardwaredurchführung oder unabhängige Hash-Neuberechnung aller umfangreichen Logbytes.

## Pflichtfinding CV2-040-R02-F01 – Availability-Command hängt an nativem Stop

**Schwere:** HOCH · **Status:** OPEN · **Requirements:** AUDIO-06, AUDIO-07, K-04 §6 · **Owner:** AP-CV2-040-Umsetzer.

**Fundstelle:** [`voice_stt_client/core/v2_media.py` L293–310](https://github.com/marcosudau-vps/voice-stt-client/blob/79cffe19b103cfcc325f5c15a7532da763ff3f9c/voice_stt_client/core/v2_media.py#L293-L310), insbesondere L306–310 sowie `_stop_capture` L253–256.

**Deterministischer Reproduktionsauftrag:** Laufende READY-Session und aktive Activation einrichten. Mock-Capture so ausstatten, dass `capture.stop()` beim Verlust des Audiogeräts an einem kontrollierten `threading.Event` blockiert. `media.set_device_available(False)` auf dem Coreloop auslösen; vor Freigabe des Events die im STT-Socket empfangenen Commands prüfen.

**Expected:** PCM sofort lokal gesperrt, und `audio_availability.set(audioAvailable=false)` erreicht den Server unabhängig vom blockierten nativen Stop rechtzeitig, damit die offene Activation gecancelt und ältere Backgroundfinals erhalten bleiben.

**Actual (aus geprüftem Kontrollfluss):** Der Lifecycle wartet bei Device-/Muteverlust zuerst auf `await self._stop_capture()`; `_report_availability(..., False)` folgt ausschließlich danach. Bei blockierendem `capture.stop()` bleibt die Servermeldung aus. Der vorhandene Test `test_device_loss_mute_recovery_and_led_are_separate` verwendet eine sofort rückkehrende Test-Capture-Freigabe und deckt diese Reihenfolge nicht ab. Ein gezielter Live-Repro wurde vom Reviewer mangels lokaler Checkout-/Runtimeausführung **NOT_RUN**.

**Verlangt:** Meldung von `false` vom möglicherweise blockierenden Geräte-Stopp entkoppeln, ohne alte PCM-Frames freizugeben. Gezielt blockierenden Stop testen, Ack-/Cancelreihenfolge und unveränderte ältere Finals beweisen; danach betroffene Tests plus gültige vollständige Windows-Requalifikation.

## Pflichtfinding CV2-040-R02-F02 – Timeout verhindert Logcleanup

**Schwere:** HOCH · **Status:** OPEN · **Requirements:** AUDIO-09 (Lifecycle/Recovery), K-04 §6 (Shutdown) · **Owner:** AP-CV2-040-Umsetzer.

**Fundstelle:** [`voice_stt_client/core/v2_media.py` L373–390](https://github.com/marcosudau-vps/voice-stt-client/blob/79cffe19b103cfcc325f5c15a7532da763ff3f9c/voice_stt_client/core/v2_media.py#L373-L390).

**Deterministischer Reproduktionsauftrag:** READY-Session mit aktivem Logtransport und einer laufenden nativen `_capture_operation` anlegen. Native Operation kontrolliert über das konfigurierte `shutdown_timeout` hinaus blockieren; `media.close()` aufrufen, Timeout beobachten, Zustand des Logtransports und zweiten `close()`-Aufruf kontrollieren. Alternativ `capture.stop()` über das Timeout hinaus blockieren.

**Expected:** Unvollständiger Capture-Shutdown wird wahrheitsgemäß als Timeout gemeldet; dennoch räumt die unabhängige Logdomain ihre Tasks/Sockets auf. Ein erneuter Shutdown darf verbliebene Ressourcen nicht unwiederbringlich überspringen.

**Actual (aus geprüftem Kontrollfluss):** `_closed=True` wird vor allen awaits gesetzt. `wait_for(_capture_operation)` oder `wait_for(_stop_capture())` kann `TimeoutError` werfen, bevor `await self.logs.shutdown()` erreicht wird. Jeder Folgeaufruf kehrt wegen `_closed` sofort zurück; Logcleanup ist übersprungen. Bestehende Tests prüfen nur vollständige und vor Ablauf endende native Vorgänge; der Timeoutfehlerpfad ist unbelegt. Gezielte Runtime-Reproduktion hier **NOT_RUN**.

**Verlangt:** Fehlerisolierten, auch bei nativem Timeout kontrolliert budgetierten Cleanup der unabhängigen Logressourcen implementieren; unvollständigen nativen Stop sichtbar lassen; Regression für Timeout/noch aktiven Logtransport/zweiten Close und anschließend Windows-Requalifikation nachweisen.

## Nichtblockierende Aktenkorrektur und Übergabe

Die einleitende Zustandsübersicht von `PLANUNG/ARBEITSPAKETE/README.md` war beim Prüfeingang veraltet (AP-CV2-030 als WAITING_FOR_APPROVAL statt ACCEPTED, AP-CV2-040 als PLANNED statt REVIEW_READY). Als rein administrativer Reviewnachtrag auf den belegten tatsächlichen Stand berichtigt; keine fachliche Kriterienänderung.

Gesamturteil: **CHANGES_REQUIRED**; keine technische Freigabe, kein Merge und kein Folgepaket AP-CV2-050. Der Umsetzer korrigiert **beide** Befunde im bestehenden Paket-PR auf Basis der aktualisierten Reviewspitze, dokumentiert neue gezielte Regressionen und komplette kandidatengebundene Windows-Vollsuite/Serverintegration soweit betroffen und legt denselben kumulativen Kandidaten erneut unabhängig vor. Die Reviewunterlagen werden separat nach `79cffe19b103cfcc325f5c15a7532da763ff3f9c` committiert; dieser administrative Folgecommit ist ausdrücklich **nicht** der fachlich geprüfte Kandidat.

Reviewmethodik: unabhängiges statisches Code-/Tests-/Dokumentationsreview über commitgebundene GitHub-Ressourcen, keine neue Windows-Testausführung. Das Urteil bezieht sich ausschließlich auf die benannte Kandidatenidentität und prüft keine späteren Korrekturen vorab.
