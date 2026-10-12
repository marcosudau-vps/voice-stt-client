# Client V2 – AP-CV2-040 / R04-ABNAHME / CHANGES_REQUIRED, 2026-10-12

AP-CV2-030 ist ACCEPTED auf `3df342c3a7cacaa1226743c4d9bee674e94d33db` (kanonischer Parent). AP-CV2-040 ist **CHANGES_REQUIRED** nach unabhängigem R04-Review des R03-Korrekturkandidaten `7461577b1316ff113bac1c08ea7a836cf4b5023a`: [R04-Bericht](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R04-ABNAHME/01_REPORT.md). R02-F01 wurde geschlossen; der native Timeoutteil von R02-F02 wurde korrigiert, der Cancellation-Fall während des Task-Joins ist weiterhin offen. [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6).

Die R03-Qualifikation bleibt anerkannt: **1373 Windows-Tests, 228 gezielte Tests, 46 Serverfälle / 46 bytegeprüfte Quellen**, sämtliche 188 qualifikationsgebundenen Gitblobs identisch, CI Attempt 2 SUCCESS. Diese grünen Tests umfassen noch keinen Abbruch während des Task-Joins; es gibt daher keinen ROOT_PASS. Keine fachliche Planänderung oder neue Serverbaseline.

Nächste Aktion: **Korrektur von `CV2-040-R02-F02` im bestehenden Paket-PR**, gezielte Regression bei Cancellation während Task-Join, neue gültige Windows-/betroffene Serverqualifikation und erneute unabhängige Abnahme. `feat/client-v2`, Server-Distributed, Main, Tags und Releases bleiben unverändert. Kein Merge oder Start AP-CV2-050.

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
