# Client V2 – AP-CV2-070 / R02-ABNAHME / ROOT_PASS, 2026-10-12

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP060 **ACCEPTED**; tatsächliches AP060-Aggregat `473a75d02fb6d00e5664af4328dadaa44da5191a` auf feat/client-v2, Single-Parent und Treegleichheit sowie PASS/menschlicher Prompt [belegt](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP070 ist unabhängig technisch ROOT_PASS gemäß R02-Abnahme, Branch `work/client-v2/ap-cv2-070`; menschliche Übernahme ausstehend. Spätere Pakete bleiben PLANNED; Server-Distributed bleibt bis zum gemeinsamen Abschluss offen.

[Runreport](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json), [Planungseinstieg](PLANUNG/README.md), [Produktinterfaces](../../../docs/protocol-v2-settings.md).

Versionierte V1→V2-Migration mit Backup/Reparatur; dynamischer öffentlicher Wake-Katalog; serverautoritativer Settingsservice mit getrennten Wünschen/requested/effective/pending/unsupported und Revisionsräumen. Reconnectbootstrap bestätigt NA-Werte vor Audiofreigabe. NS-Noise/VAD bleibt nicht individuell startbar; Auswahl wirkt erst beim nächsten Hello. Keine Qt-/Credentialpersistenz, Appkomposition AP100.

Qualifikation: 1460 vollständige Windows-Tests, 243 gezielte Regressionstests, 38 echte HTTP/WS/Media/PCM-Checks und 55 gepinnte Settings-/Wake-Supplementtests ohne Skips; compileall/diffcheck PASS. 34 neue Clienttests. Empirische Wake-/ASR-/Hardwarequalifikation weiterhin AP-IV2-020, kein Nachweis optimaler Kalibrierung.

Nächste Aktion: menschlichen Übernahmeprompt für PR #9 abwarten, vorher aktuellen Head/Base, admin-only-Diff und CI prüfen; kein automatischer Merge/AP080. Runtime Python3.12 in Projektvenv; Testreproduktion über den Runner im Evidenzindex. Die reguläre App bleibt bis AP100 auf dem bisherigen Pfad.

[Unabhängiger R02-ROOT_PASS](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R02-ABNAHME/01_REPORT.md), [Review-Evidenz](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R02-ABNAHME/EVIDENCE/INDEX.md).

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
