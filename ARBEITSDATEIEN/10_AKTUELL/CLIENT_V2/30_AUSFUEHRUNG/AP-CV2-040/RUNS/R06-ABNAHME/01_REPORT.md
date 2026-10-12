# AP-CV2-040 / R06 – unabhängige Wiederholungsabnahme nach R05

**Technisches Urteil: ROOT_PASS.** 2026-10-12 (Europe/Berlin). Alle Pflichtfindings unabhängig geschlossen; Workflowphase nach diesem Review **WAITING_FOR_APPROVAL**. [Originalauftrag](00_PROMPT_ORIGINAL.md) · [Evidenzindex](EVIDENCE/INDEX.md). Die technische Abnahme berechtigt ausdrücklich **nicht** zu Merge, kanonischer Übernahme, Folgepaketstart oder Release.

## Identität und Prüfmethode

| Merkmal | Unabhängig verifizierter Wert |
| --- | --- |
| Repo / PR | [marcosudau-vps/voice-stt-client #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6), bei Abnahme offen |
| PR-Base | `feat/client-v2`, SHA `3df342c3a7cacaa1226743c4d9bee674e94d33db` |
| Kandidatenbranch | `work/client-v2/ap-cv2-040` |
| **reviewed_sha** (vor eigenem Docs-Commit) | `4ef7a13672bf7c50665e08f5eff837fb5d687419` |
| **reviewed_tree** | `f670a6fce6557ff657644037964025e9f7f1ee1e` |
| canonical_parent | `3df342c3a7cacaa1226743c4d9bee674e94d33db` |
| geprüfte Korrekturbasis (R04-Reviewspitze) | `1289991613d4577e535eb6067ca332240488c790` |
| unveränderte Serverbaseline | `ada13b011e1d3829f78e7f389e3b927795a2b3be` |
| maßgeblicher Umsetzungslauf | [R05-KORREKTUR](../R05-KORREKTUR/01_REPORT.md) |

Die commitgebundene GitHub-Dateiansicht, PR-Metadaten, vollständigen paginierten PR-Patches (92 Dateieinträge), vollständiger GitHub-Compare R04→R05 (ein Single-Parent-Commit) und rekursiver Git-Baum wurden unabhängig eingesehen. Die neun großen PR-Text-/Log-/Traceability-Dateien ohne GitHub-Hunkvorschau wurden über die commitgebundenen vollständigen Inhalte/Manifestdaten statt als unlesbare Patchvorschau beurteilt. Produktänderung im R05-Korrekturdiff beschränkt sich auf `voice_stt_client/core/v2_media.py`, `tests/test_v2_audio_recovery.py` und `scripts/check_v2_server_audio.py`; ergänzte Dokumente/Belege ändern keine anderen Produktmodule. Historische R01–R04-Akten wurden nicht überschrieben.

## Pflichtfindings aus R02/R04

### `CV2-040-R02-F01` – CLOSED (Bestätigung aus R04 erhalten)

Die negative Audioavailability wird in `_lifecycle()` vor einem möglicherweise blockierenden nativen Capturestop bestätigt; lokale PCM-/Epoch-Gates schließen sofort, Session und ältere Backgroundfinals bleiben erhalten. Die drei Geräte-/Mute-/Deaddevice-Regressionen aus R03 sowie echte Serverfälle bleiben in den R05-Vollnachweisen enthalten. Keine Änderung des geschlossenen Pfads in R05.

### `CV2-040-R02-F02` – **CLOSED in R06 / PASS**

Der R04-Pflichtbefund war die Cancellation-Lücke bei `await asyncio.gather()` vor dem `finally` für Logcleanup. Commitgebundener Code `v2_media.py` Zeilen 384–454 behebt diese Ursache:

1. `close()` sichert sowohl `session.stop()` als auch Sender-/Lifecycle-Join und native Captureoperation durch ein **äußeres** `finally` ab; Logcleanup wird auch nach Cancellation am Task-Join erreicht.
2. Sender-/Lifecycle-Join ist mit `wait_for(shield(gather(...)), shutdown_timeout)` begrenzt; noch laufende Taskreferenzen bleiben nach Timeout/Cancellation erhalten und werden bei erneutem Close gejoint, statt den Cleanupabschluss vorzutäuschen.
3. `_shutdown_logs()` startet einen gehaltenen Logkoordinationstask und wartet shielded mit festem Deadlinebudget (`shutdown_timeout + 3`). Wiederholte externe Cancellation wird bis zum Ende des Logtasks aufgeschoben und danach erneut signalisiert; auch ein Logclose-Timeout lässt dieselbe Task für einen Retry erhalten.
4. `_cleanup_complete` wird ausschließlich nach erfolgreichem Durchlaufen von Transport-, Medien- und Logcleanup gesetzt; `_closed` sperrt parallel sofort neue PCM-Arbeit. Der getrennte Loglebenszyklus wird nicht als V2-Domainautorität verwendet.

**Expected/Actual:** Unter kontrolliert gehaltener Sender-/Lifecycle-Cancel-Cleanup-Phase wird `close()` cancelt. Expected: CancelledError beim Owner, Logsocket/-tasks vollständig beendet, unvollständiger Native-/Taskzustand erkennbar, erneutes Close möglich. Actual nach R05: die fünf neuen Tests belegen Sender-/Lifecycle-Cancellation, wiederholte Owner-Cancellation während Logclose sowie Taskjoin-/Logclose-Timeout und Retry mit abgeschirmten Cleanuphandles. Drei Repros waren vor Produktänderung auf dem R04-Stand erwartungsgemäß FAIL; nach Korrektur PASS. Der reale Servercheckpoint enthält neu `shutdown/task_join_cancel_{reported,real_logs_clean,retry_complete}` und `shutdown/logclose_cancel_{reported,real_logs_clean,retry_complete}` mit tatsächlichen Log-/Expiry-Task- und Logsocket-Effekten. Beleg: [R05-Report](../R05-KORREKTUR/01_REPORT.md), [vollständige Tests](../R05-KORREKTUR/EVIDENCE/INDEX.md). K-04 §6, AUDIO-09 und LOG-09 erfüllt.

Keine neuen Pflichtfindings aus dem kumulativ geprüften Paket.

## Unabhängige Prüfung der Qualifikation

| Pflichtnachweis | R05-Fremddurchführung | Unabhängig verifizierter Befund |
| --- | --- | --- |
| Vorherbaseline | 60 PASS vor Produktfix | PASS als Fremdbeleg |
| Fehlerrepros auf R04 | 3 erwartete FAILs, produktunverändert | PASS als kausaler Repro-Nachweis |
| Gezielter Windowslauf, warnings=error | **233 PASS**, Exit 0 | PASS |
| Vollständiger Windowslauf | **1.378 PASS**, Exit 0, 115,268 s | PASS |
| Client-/Serverintegrationscheckpoint | **52 PASS**, 46 bytegeprüfte ada13b0-Serverquellen | PASS |
| compileall, Git-Diffcheck und Arbeitsaktencheck | jeweils Exit 0 / PASS | PASS |
| Qualifizierte Quell-/Test-/Harness-/Konfigblobs | **188/188** im R05-Manifest stimmen mit `reviewed_tree` überein | PASS, **selbstständig anhand Git-Baum geprüft** |
| CI auf exakt `reviewed_sha` | GitHub Actions Run `38207648493`, **Attempt 2 SUCCESS** samt Vollsuite/Build-/Installationssmokes | PASS |
| Paketrequirments | 12 AUDIO + 11 LOG, insgesamt **23/23** in R05-Requirementcoverage sowie Matrix/JSON konkret belegt | PASS |

Die Vollsuite und Windows-/Serverfälle sind **extern ausgeführte, unabhängig überprüfte Nachweise**; **eigene Windows-/PortAudio-/Server-Testausführung: NOT_RUN** (bei gültigem Fremdnachweis nach Abnahmeskill nicht gefordert). Die Windows-Laufzeit war Windows 11 Build 26300, Python 3.12.10 in Projektvenv, PySide6 6.11.1 und Qt offscreen.

Transparente Fehlversuche: Ein früherer R05-Lokalversuch traf das 240-s-Harnesslimit, ohne die konkrete Ursache zu protokollieren. Danach wurden Diagnosevollsuite (1.378 PASS in 109,420 s) und reguläre Vollqualifikation (1.378 PASS in 115,268 s) auf unverändertem Produkt/Test/Config und unverändertem Limit abgeschlossen. CI Attempt 1 hatte drei zeit-/Logbeobachtungsbezogene Testfehler; Attempt 2 bestand auf derselben SHA vollständig ohne Test- oder Timeoutänderungen. Der Ursprung dieser Einzelfälle ist **NOT_PROVEN**; die Fehler werden nicht als PASS ausgegeben und sind kein reproduzierter Defekt des letztlich bestandenen finalen Kandidaten.

Anforderungen/Scope: Durchgängiger PCMflow, generationgebundene Bounds, Device/LED-/Mute-/Recovery-Trennung, korrekte Audioavailability, sessiongebundene Logcredentials, sichere Origin-/Token-/Cursor-/Retention-/Replaygrenzen, observer-only Logging und unabhängiger Shutdown wurden gegen kumulativen PR-Code, K-04 und konkrete R05-Belege geprüft. Keine Config-/Daten-/Historymigration, keine Domainwirkung aus Replay. **Reales PortAudio-/USB-/LED-Gerät und ASR-/Wakequalität: NOT_PROVEN** und vertragsgemäß spätere IV2-Gates; Qt-/Settingskomposition sind CV2-100/070. Kein jetziger AP040-Blocker.

## Dokumentations-/Abschlusszustand

R05-Report, ursprüngliche R01–R04-Akten, Windowsmanifest, gitgebundene Belegpfade, Requirements-JSON/Matrix und Produkt-API-Dokumentation sind vorhanden. Aktive Akten/Index/Manifest/Workflow werden durch diesen rein administrativen Reviewcommit auf **ROOT_PASS / WAITING_FOR_APPROVAL**, **keine offenen Finding-IDs** und diesen R06-Report gestellt. Review-SHA/Tree bezeichnen ausdrücklich den **vor** diesem Dokumentcommit geprüften Stand. Der Docs-Commit ist keine zusätzliche Produktänderung und keine neue Kandidatenqualifikation.

**Nächste Aktion:** menschliche ausdrückliche Freigabe zur kanonischen Übernahme von PR #6 auf `feat/client-v2` unter Angabe von PR, finalem Docs-Head, canonical_parent und R06-PASS-Report. Erst danach darf der gesondert beauftragte Abschlussagent die Übernahme prüfen/durchführen. Vorher keine Übernahme, kein Start AP-CV2-050, keine Serverpromotion, kein Tag/Release.
