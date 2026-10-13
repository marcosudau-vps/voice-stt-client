# Client V2 – AP-CV2-090 / R02-ABNAHME / ROOT_PASS, 2026-10-13

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP080 ACCEPTED; AP080 tatsächlich auf `1bc5be893060e0d6a80e1d890102bfffebb73a17` übernommen, Single-Parent/Baumgleichheit und unabhängiger PASS/menschlicher Prompt [belegt](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP090 unabhängig mit ROOT_PASS auf `work/client-v2/ap-cv2-090` geprüft (R02); Workflow WAITING_FOR_APPROVAL, menschliche Übernahme ausstehend. Spätere Pakete PLANNED, Server-Distributed bleibt offen.

[Runreport](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [R02-ROOT_PASS](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R02-ABNAHME/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json), [Planungseinstieg](PLANUNG/README.md), [Produktinterfaces](../../../docs/protocol-v2-feedback.md).

Bestehende Feedbackengine mit validiertem V2-Mirroringang, quellenneutralen Phasen und getrenntem Backgrounddrain. Segmentvorschau, Domain-Dedup, diagnostischer Log-/Replaypfad, relative Anzeige ohne Lifecyclecommands; isolierte queued Qt-/Sound-/LEDausgabe. Mappingregeln und Präferenzen bleiben erhalten, UUIDkorrelation nutzt die vorhandene OBSfoundation.

Qualifikation: 1552 vollständige Windows-Tests, 377 gezielte Tests, 39 neue Clienttests; tatsächlicher gepinnter Domain-/Log-/Replay-/Qtcheckpoint 18 Checks. compileall/diffcheck und Akten-/Blobbindung im Evidenzindex. Hardware-/ASR-/Wahrnehmung bleibt AP-IV2-020, reguläre Appkomposition AP100. Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`.

Nächste Aktion: ausdrückliche menschliche Übernahmefreigabe für den unabhängig geprüften PR #11 abwarten; kein automatischer Merge/AP100.

## Historischer Stand vor AP-CV2-020

# Client V2 – AP-CV2-010

AP-CV2-000 ACCEPTED auf `1cf076bd2ed56929b1a3780bc140da51348a8295`, PR #2. AP-CV2-010 ROOT_PASS (R02; Übernahmefreigabe ausstehend): [Paketakte](30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md), [Workflowstatus](WORKFLOW_STATUS.json). Reiner Codec; unveränderte Serverbaseline ada13b0. Nachmergeprovenienz ist in der AP010-Akte nachgewiesen, kein zweiter AP000-Abschlusscommit.

Die folgenden datierten Angaben bleiben Historie.

# Status – Client V2

## Aktuelle ergänzende Abnahme R05 (2026-10-11)

**AP-CV2-000 ROOT_PASS / READY_FOR_CANONICALIZATION**. R04 schließt F01 fachlich; R05 schließt den Testblocker: 1233 Windows-PASS plus5 Startup-PASS. [Report/Freigabe](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md). Finale PR-CI/Base vor Einzel-Squash prüfen; tatsächliche kanonische Übernahme noch nicht erfolgt. Neue Testverantwortung: Windows-Vollsuite im Umsetzungslauf, unabhängiger ChatGPT-Review anhand Code und gültigem Nachweis.

## Historische unabhängige Folgesichtung R04 (2026-10-11)

**AP-CV2-000 BLOCKED** ausschließlich wegen des noch fehlenden unabhängig durchgeführten/veranlassten vollständigen Windows-Prüflaufs. [R04-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R04-ABNAHME/01_REPORT.md). Das frühere Produktfinding `CV2-R02-F01` wurde anhand der korrigierten Startlogik fachlich geschlossen; die vorhandene Windows-CI [38163179818](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38163179818) besteht mit 1233 Tests. Unabhängiger eigener Windows-Test **NOT_RUN**, kein ROOT_PASS. Workflow-/Unterlagenänderungen auf ausdrücklichen Wunsch nicht inhaltlich bewertet. Keine kanonische Übernahme/kein Folgepaket.

## Vorheriger R03-Selbstqualifikationsstand

## Historischer Korrekturkandidat – R03 (2026-10-11)

**AP-CV2-000 REVIEW_READY**. [R03-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md): F01 selbst korrigiert, gesamte Clientsuite 1233 PASS; Wheel/sdist und EXE samt Smokes bestanden. Gemeinsamer Aktenprüfer, Statusabgleich und Testweg präzisiert. [Belegsatz einschließlich drei Archivteilen](PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/README.md) im selben Kandidaten. Nächste Aktion: unabhängiger Vollreview; bisheriger F01 braucht unabhängigen Recheck und R02-NOT_RUN eigenständige Windows-Nachweise. Kein ROOT_PASS oder Merge; Schreibrecht zurückgegeben.

## Historische unabhängige Abnahme – R02 (2026-10-11)

**AP-CV2-000 CHANGES_REQUIRED**. Im [R02-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R02-ABNAHME/01_REPORT.md) ist `CV2-R02-F01` dokumentiert: Hotkey-Fallback speichert Benutzerpräferenz vor bestätigtem Corestart. Der unabhängige Windows-Gesamttest ist **NOT_RUN**, CI 38145266161 ist dagegen grün. Prüfkandidat `8b1c4c157b6b431dac6af69e2e264d0c37579bef`, Tree `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e`, Parent unverändert. Umsetzer-Korrektur und frischer unabhängiger Review stehen an; **kein ROOT_PASS, keine Übernahmefreigabe, kein CV2-010**.

## Historischer R01-Stand vor R02

Stand 2026-10-11. Planung Revision 10; **AP-CV2-000 REVIEW_READY** auf `work/client-v2/ap-cv2-000` ab Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [Paketakte](30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md), [Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json).

Feature-/Releasebasis in voice_stt_client integriert; vollständige pytest-/Unittest-Suite je 1221 Tests grün, Wheel und sdist außerhalb Checkout qualifiziert. Bisheriger V1-Transport bleibt; keine V2-Kompatibilität oder reale Hardwareabnahme. Alle Folgepakete PLANNED; bedingtes Server-FIX nicht gestartet.

Kein unabhängiger PASS und keine menschliche Übernahmefreigabe. Gemeinsame Feature-Spitze bleibt `050e776cf316eb332177294db0c0a2719c2b4415`; integrierter kanonischer Client-SHA offen. Nächste Aktion: unabhängige Abnahme in frischer Session. Ab Abgabe Umsetzer-Schreibrecht pausiert. CV2-010 erst nach PASS, ausdrücklichem Übernahmeprompt und nachgewiesenem Einzelaggregat.

Workflowweite Kandidaten-Gitrechte aus [Originalauftrag](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md) gesichert; keine Main-/Serverpromotion, Tags, Releases, Force-Pushes oder Cleanup. Server-Distributed/ada13b0 bleibt offen. Historischer Revision-9-Start bfade9d und Dokumentkorrektur Revision 10 bleiben erhalten.
