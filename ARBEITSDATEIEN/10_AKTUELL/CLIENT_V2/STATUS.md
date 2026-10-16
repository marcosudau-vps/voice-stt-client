**Aktualisierung16.10.:** UX01 nativ bestätigt und geschlossen. Zwei einzeln gestartete direkte Wake-Nutzsätze vollständig, ohne Rufwort und mit Leerzeichen bestätigt. F9-Finish mangels Commandack noch unbewiesen; gezielter einzelner Manualtest mit eigener Vorschau/Start folgt. Produkt17261e6 unverändert; vollständige M-Gates/30min100 weiter offen.

# AP-IV2-020 – IN_PROGRESS, Phase C läuft, 2026-10-15

Kanonischer Parent `b80ed8b` unverändert, Vorgänger AP010 tatsächlich ACCEPTED.
Paketbranch `work/client-v2/ap-iv2-020`, kumulativer Draft-PR #15, derselbe R01.
Ausdrücklich freigegebener Reconnect-/Recovery-Audit abgeschlossen: zehn technische
Findings behoben. Recoveryprodukt41ca761 historisch; zusätzlicher freigegebener UX01-Fix am Produkt `17261e6`, neue EXE/Wheel/sdist sauber gebunden.
1378 Windows-Tests ohne Skips, 11 Prozessfälle, alle sieben Server-Smokes PASS;
1964 Server-Unit-Tests PASS/14 ausgewiesene optionale Skips. Echter ReSpeaker- und
Desktop-Reconnect, HTTP-/Ackausfall, drei Neustarts, Shutdown und Frozen-GUI grün.
M-Fälle, echte Wakepositive/Nutzsprachgrenze, Wahrnehmung/Kalibrierung und30min100
bleiben NOT_RUN/NOT_PROVEN. Nächste Aktion: gemeinsamer erster Sprach-/Windowsblock.
[Report](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/VPS geschützt; Server nur lokal. Kein REVIEW_READY, Eigenreview, Merge oder Release.


Neuer Produkt-/Build-/Paarstand17261e6 autonom qualifiziert; native Ausgabebestätigung und vollständige Realgates bleiben offen. Der nächste Ein-Klick-Block steht im Testeditor bereit.

## Vorheriger datierter Stand

# Client V2 – AP-IV2-010 / R02-ABNAHME / ROOT_PASS, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

**R02:** [unabhängiger ROOT_PASS](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R02-ABNAHME/01_REPORT.md), 7/7 GATE PASS, 0 Findings. **R03-Freigabe ausdrücklich erteilt**; READY_FOR_CANONICALIZATION, Merge steht noch aus. Reales AP-IV2-020-Gate weiterhin NOT_RUN.

**R03-Übernahmebereit:** [menschlicher Originalprompt](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md), [Preflightbericht](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R03-UEBERNAHME/01_REPORT.md), CI des letzten Docs-Commit noch zu prüfen; kein ACCEPTED vor nachgewiesenem Squash.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Client V2 – AP-CV2-110 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-14

[Paket-PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base `feat/client-v2`, Head `work/client-v2/ap-cv2-110`.

Aktiver Arbeitsblock [CLIENT_V2](README.md);
[Einstieg Planung](PLANUNG/README.md), [Workflowstatus](WORKFLOW_STATUS.json).
AP000 bis AP100 tatsächlich ACCEPTED auf feat/client-v2; letzter kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100-PASS, menschlicher R06-Auftrag und wirklicher PR12-Squash
[verifiziert](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).

AP110 auf `work/client-v2/ap-cv2-110`: ausführbare V1-Autoritäten entfernt,
Migrationreader und Utilities erhalten, Source/Wheel/sdist/Frozen mit belegter
Helloidentität und nativer Windows-GUI qualifiziert. Windows **1353 PASS**,
gezielte **234 PASS**, Servercheckpoint **17 PASS**, compileall/diffcheck und
alle Build-/Ressourcen-/Installationschecks PASS. Getesteter Produktcommit
`cf42a2a9d96c1ebc88035817a5d529dfe04e4306`; finale PR-Spitze ergänzt ausschließlich administrative Unterlagen.
[Report](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Kompatibilität](../../../docs/compatibility.md), [Runtime](../../../docs/protocol-v2-runtime.md).

Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.
Bekannte Legacy-Profile und History werden mit Backup migriert; kein V1-Fallback.
Builds liegen lokal unter dist, kein veröffentlichter Release. Keine realen
ASR-/Mikrofon-/USB-/Fremdanwendungs-/Wahrnehmungsgates behauptet.

**Aktueller Reviewabschluss (2026-10-14):** [AP110 R02 unabhängiger ROOT_PASS](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) auf `44cf9a8fd1669242c00997966addc3667d448aa0`; FINAL-03 bis FINAL-09 technisch PASS, keine offenen Pflichtfindings. **ROOT_PASS** mit menschlicher **R03-Freigabe** – finale Git-/CI-Prüfung und Squash stehen aus. Kein AP-IV2-010-Start zuvor.

**Übernahmefreigabe 2026-10-14:** [R03-Originalprompt](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) und [R03-Abschlussablauf](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/01_REPORT.md) dokumentiert. Aktuelle Phase **READY_FOR_CANONICALIZATION**; unabhängiger R02-ROOT_PASS unverändert. Nach finaler CI und Head-/Baseprüfung ist der einzelne Squash-Merge von PR #13 erlaubt. Ohne belegten GitHub-Merge noch nicht ACCEPTED; kein Release/Tag/Servermerge/AP-IV2-010.

---

## Historischer AP100-Stand vor dessen tatsächlicher kanonischer Übernahme

# Client V2 – AP-CV2-100 / R05-ABNAHME / ROOT_PASS, 2026-10-13

AP-CV2-000 bis AP-CV2-090 auf `feat/client-v2` ACCEPTED; letzter kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der aktuelle AP-CV2-100-Paketbranch `work/client-v2/ap-cv2-100` ([PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)) wurde unabhängig am Kandidaten `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` geprüft: **technischer ROOT_PASS**, 6/6 Paketrequirements erfüllt, `CV2-100-R03-F01` geschlossen.

[R05-Abnahmebericht](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md), [unabhängige Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/EVIDENCE/INDEX.md), [R04-Korrekturbelege](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json).

Extern qualifizierte Windows11-Suite **1581 PASS**, gezielte Tests **210 PASS**, **17** echte gepinnte Client-/Servercheckpoints am Server `ada13b0`, GitHub-Actions-CI **38394758805** erfolgreich auf dem geprüften Kandidaten. Reviewer hat diese Belege unabhängig geprüft, aber keine eigene Windows-/Hardwaretestausführung vorgenommen.

**Nächster Schritt: WAITING_FOR_APPROVAL.** Ausdrückliche menschliche Freigabe des Squash-Merges von PR #12 erforderlich, davor aktueller PR-Head, unveränderte Base, ausschließlich administrative R05-Nachträge sowie finale CI prüfen. Kein Merge und kein Start von AP-CV2-110 durch dieses Review.

---

## Historischer R04-Stand vor unabhängigem R05-Review

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](WORKFLOW_STATUS.json), [Runtimeinterfaces](../../../docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

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
