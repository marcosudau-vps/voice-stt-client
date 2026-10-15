# Verlauf – Client V2

## 2026-10-11 – CLIENT-V2-START-001

Neuen gemeinsamen Planungs-/Umsetzungsbranch von der kanonischen Clientfeaturebasis angelegt und vollständige Planrevision 6 mit Rollen-Skills importiert. Dateibaum der Clientbasis entspricht Distributed a80a6b1. Start enthält nur Unterlagen; CV2-000 und alle weiteren Paketabnahmen bleiben offen. Paketarbeit auf untergeordneten Branches, spätere Annahme als jeweils ein Code-/Unterlagenaggregat nach unabhängigem PASS und Auftraggeberprompt. Serverlinie und fremde WIP erhalten. Konkreter Startcommit ist als erster Commit nach 8bab1b3 im Gitverlauf ermittelbar; kein Selbst-SHA oder zusätzlicher Aufräumcommit erforderlich.

## 2026-10-11 – CLIENT-V2-ROLLEN-001

Rollenworkflow Revision 7 auf work/client-v2/rollenworkflow ab b0525e6 vorbereitet: Auftraggeberleitfaden, aktualisierte Umsetzung-/Abnahmeskills, Checklisten und Prompt-/Aktenvorlagen. Ein Paket-PR nach feat/client-v2, serialisierte Schreibübergabe, beauftragter Docs-Reviewcommit, menschlicher Übernahmeprompt und ein Squash-Commit je AP. Tatsächlicher Vorgängerabschluss wird vor Folgepaketstart geprüft. Kein Produktcode, keine AP-Abnahme, kein Commit/Push/Merge aus diesem Unterlagenauftrag. Die geprüfte Unterlagenänderung geht in den ersten passenden Paketbranch und dessen Aggregatecommit ein.

## 2026-10-11 – CLIENT-V2-ZUSTAENDE-001: nächster Schritt aus dokumentiertem Stand

Gemeinsamen Einstieg und Workflowrevision 8 ergänzt. Neuer Agent ermittelt AP/Rolle/Kandidat aus offenen Paketlinien, Status-/Runakten und kanonischem Gitverlauf. Festgelegte Workflowphasen mit Pflichtpflege in WORKFLOW_STATUS.json; initial nur AP-CV2-000-Planungsbereitschaft, kein Run/PASS/Freigabeprompt erfunden. Ein ausdrückliches Zusatzreview startet frisch, behält alte Berichte und berücksichtigt alle offenen Pflichtfindings. Menschliche Übernahmefreigabe bleibt getrennt. Unterlagen auf work/client-v2/rollenworkflow vorbereitet, feat/client-v2 unverändert; keine Produktimplementierung oder Git-Veröffentlichung.

## PLAN-CLIENT-V2-009 – 2026-10-11 – vollständiger Unterlagenstart zur Veröffentlichung

Auf ausdrücklichen Auftrag aktuellen vollständigen Unterlagensatz als Revision 9 im noch unveröffentlichten Startcommit von feat/client-v2 konsolidiert und dessen erstmaligen Push vorbereitet. Aktive Vorbereitungsbranch-/Importhinweise ersetzt, historische Prüfstände gekennzeichnet, erste Auftragsvorlage innerhalb des Plans ergänzt und initiale Selbst-SHA durch Gitauflösung ersetzt. Keine Produktänderung und keine AP-Abnahme. Alle Client-/Integrationspakete bleiben offen; Serverada13b0 bleibt gepinnte Distributedreferenz. Prüfdetails: PLANUNG/EVIDENCE/PRUEFBERICHT.md im aktiven Client-V2-Arbeitsblock. Tatsächliche Commit-/Remoteidentität wird nach Transport aus Git ermittelt.

## PLAN-CLIENT-V2-010 – 2026-10-11 – externe Prüffunde bewertet und korrigiert

Sechs Funde geprüft: konkrete Recovery-/Serverrouting-/Auswahlregeln ergänzt, reale Plattformbelege mit unabhängiger Validierung geregelt, vorhandene Ausnahme für spätere Korrekturen konkretisiert, COMPLETED samt Nachmerge-Beleg beschrieben. Versionsmetadaten und Basisschätzung präzisiert. Originalprüfbericht erhalten; dessen ungenaue Commitformulierung berichtigt. Reine Dokumentkorrektur auf work/client-v2/planung-rev10 ab bfade9d, keine Produktumsetzung/AP-Abnahme und kein Commit/Push/PR/Merge aus diesem Auftrag. Prüfdetails in PLANUNG/EVIDENCE/PRUEFBERICHT.md des aktiven Blocks.

## PLAN-CLIENT-V2-011 – 2026-10-11 – Revision 10 zur Veröffentlichung freigegeben

Auf Originalprompt „Go: Revision 10 als einen Dokumentkorrekturcommit auf `feat/client-v2` übernehmen und pushen.“ die vollständige Revision 10 und aktuelle Status-/Agenteneinstiege für genau einen zusätzlichen Dokumentcommit finalisiert. Erhaltener Parent bfade9d, Vorbereitung auf work/client-v2/planung-rev10, Übernahme nur fast-forward und normaler Push mit tatsächlicher Git-/Remoteprüfung. Benannte einmalige Dokumentausnahme vor AP-CV2-000; danach unverändert ein Aggregat je angenommenem AP. Kein Produktcode, keine AP-Abnahme und keine zukünftige Umsetzungsfreigabe. Originalauftrag und abschließende Dokumentprüfung liegen unter PLANUNG/EVIDENCE im aktiven Client-V2-Block. Endgültige Commit-/Transportidentität wird nach Ausführung außerhalb des Commitinhalts gesichert.

## AP-CV2-000 / R01 – 2026-10-11

Integrierter Paketkandidat REVIEW_READY. Maßgeblicher Meilenstein AP-CV2-000-R01 im [Steuerungslog](../../00_STEUERUNG/LOG_VERLAUF.md); Belege in der [Runakte](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md). Nächste Aktion unabhängige Abnahme; keine kanonische Übernahme.

## AP-CV2-000 / R02 – 2026-10-11

Unabhängige statische Paketprüfung von `8b1c4c157b6b431dac6af69e2e264d0c37579bef` mit CI-Provenienz: **CHANGES_REQUIRED**, Finding `CV2-R02-F01` (Hotkey-Fallback persistiert schon vor bestätigtem Corestart), eigene vollständige Windows-Regression `NOT_RUN`. [Versionierter Reviewreport](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R02-ABNAHME/01_REPORT.md). Kein Produktfix, kein Merge, kein Folgepaketstart. Meilenstein AP-CV2-000-R02 im Steuerungslog.


## R03-KORREKTUR – 2026-10-11

Einreichung REVIEW_READY; [Korrekturreport](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md). Meilenstein AP-CV2-000-R03 im Steuerungslog. Unabhängiger Vollreview offen, keine Übernahme.

## AP-CV2-000 / R04 – 2026-10-11

Unabhängige fachliche Folgesichtung von `cd872d4bfa8eccd0167337cbab16a572ca70bfd4`: F01 anhand Codekontrollfluss und neuer Regressionstests geschlossen; externe Windows-CI 1233 PASS für kandidatenidentischen Tree überprüft. **BLOCKED** nur wegen eigenem unabhängigem Windows-Gesamttest NOT_RUN (`R04-T01`); kein weiterer Produktfinding. Arbeits-/Workflowkorrekturen ausdrücklich von Bewertung ausgenommen. [R04-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R04-ABNAHME/01_REPORT.md). Keine Produktänderung, kein ROOT_PASS oder Merge.

## 2026-10-11 – R05 Windows-Nachweis und Nutzerfreigabe

R04-T01 durch tatsächliche unabhängige Windows-Ausführung geschlossen (1233 PASS plus5 Startup-PASS); ROOT_PASS aus R04-Produktreview und R05-Ausführung. Auf ausdrücklichen Nutzerauftrag Testverantwortung vereinfacht, Rollenregelversion7. Nutzerfreigabe für Beleg-/Regelpush und anschließenden Einzel-Squash nach grüner finaler CI gesichert. Kein vorweggenommener Merge. [Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md).


## AP-CV2-010-R01 – 2026-10-11 – Codecqualifikation und REVIEW_READY

Aus tatsächlicher kanonischer AP000-Basis1cf076b: immutable V2-Wirecodec, bytegleiche Originalvektoren, vollständige Fixtures und echter gepinnter Servercheckpoint. Windows1263 Tests, Codec30 Tests, Server188 Checks PASS; individuelle WIRE-01..17-Belege, APIs und Akte aktualisiert. [R01-Report](30_AUSFUEHRUNG/AP-CV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), PR #3 gegen feat/client-v2. Unabhängiger Review als nächste Aktion, Paketbranch ab Übergabe pausiert. Keine eigene Abnahme/Promotion und kein Folgepaketstart.

## AP-CV2-010-R02 – 2026-10-11 – unabhängige technische Abnahme ROOT_PASS

Unabhängiger commitgebundener Vollreview des PR #3: `7124e5629e24817dd711b2e2b697b9c07aa11dd7`, Tree `37b61ff4cab90c18abf8e5bfae920f2e265ad3ab`, Parent `1cf076bd2ed56929b1a3780bc140da51348a8295`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Produkt-/Testdiff, WIRE-01..17, 30 Codec-Tests, 1263 Windowsvollsuite, 188 gepinnte Serverchecks, Originalvektoren und finale GitHub-CI unabhängig validiert; keine Pflichtfindings. Windows/HW durch Reviewer selbst NOT_RUN (gültige Fremdevidenz). [R02-Report](30_AUSFUEHRUNG/AP-CV2-010/RUNS/R02-ABNAHME/01_REPORT.md). Paketstatus ROOT_PASS, Workflow WAITING_FOR_APPROVAL; keine Übernahmefreigabe und kein Merge, AP020 nicht gestartet.

## AP-CV2-030-R01 – 2026-10-12 – Mirror und Resync / REVIEW_READY

Von AP020-Aggregat8fa0f82 nach belegtem unabhängigen PASS, menschlicher Freigabe und Baumgleichheit: reiner Mirror, sichere Segment-/Terminal-/Settingsprojektionen und tatsächliche V2-Transport-/Snapshotanbindung. Alle35 Requirements einzeln verknüpft.1339 Windowsgesamttests,106 gezielte Tests,35 echte Serverchecks/46 Quellblobs und compileall PASS; exakte Basis/Produktdiff/Gitblobs und vollständige Logs gesichert. [R01-Report](30_AUSFUEHRUNG/AP-CV2-030/RUNS/R01-UMSETZUNG/01_REPORT.md). Keine eigene Abnahme, Promotion oder Folgepaketimplementierung; Schreiben ab Übergabe pausiert.

## AP-CV2-040-R01 – 2026-10-12 – Continuous-Audio und Logbootstrap / REVIEW_READY

Vom tatsächlichen AP030-Aggregat3df342c nach geprüfter unabhängiger Abnahme,
menschlicher Freigabe und Single-Parent-/Baumgleichheit: sessionlanger Capture/
PCMflow, begrenzte Epochqueue, getrennte Device-/Mute-/LEDports und separater
V2-Logbootstrap am Bestand. Alle23 Requirements einzeln belegt. 1367 Windows-,
222 gezielte Tests und41 echte Serverfälle/46 bytegeprüfte Quellen PASS;
compileall/diffcheck PASS, vollständige Logs samt Basis/Diff/Blobbindung.
[Report](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R01-UMSETZUNG/01_REPORT.md).
Unabhängige Abnahme offen; Paketbranch ab Übergabe pausiert. Kein eigener
ROOT_PASS, Merge oder Folgepaketstart. Serverada13b0/Distributed und spätere
ASR-/Hardwaregates offen.

## AP-CV2-040-R03 – 2026-10-12 – Availability-/Shutdownkorrektur / REVIEW_READY

R02-Unterlagen per Fast-forward übernommen; F01/F02 in fünf Fehlerfällen reproduziert und anerkannt. Negative Availability vor nativem Stop, unabhängiges finally-Logcleanup und wiederholbares natives Shutdowncleanup korrigiert. 1373 Windows-/228 gezielte Tests,46 echte Serverfälle/46 Quellen sowie compileall/diffcheck PASS. [R03-Report](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R03-KORREKTUR/01_REPORT.md). Historische Belege erhalten, alle23 IDs aktualisiert. Neue unabhängige Abnahme offen; Branch ab Übergabe pausiert. Keine Promotion oder Folgepaketimplementierung.

## AP-CV2-040-R05 – 2026-10-12 – Task-Join-/Logclose-Cancellation / REVIEW_READY

R04-Unterlagen per Fast-forward übernommen, einziger offener F02-Rest anerkannt und in drei Fenstern reproduziert. Äußerstes Log-finally, begrenzter geschützter Task-Join und gehaltener Logshutdowntask schützen Cancellation samt Retry. Fünf neue Regressionen; 1378 Windows-/233 gezielte Tests,52 reale Serverfälle/46 bytegeprüfte Quellen, compileall/diffcheck PASS. [R05-Report](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R05-KORREKTUR/01_REPORT.md). Alle23 IDs neu belegt, R01–R04 erhalten. F01 CLOSED_R04, F02 technisch selbstkorrigiert mit unabhängigem Recheck offen; Branch ab Übergabe pausiert, keine Promotion/kein Folgepaket.


## AP-CV2-100-R01 – 2026-10-13 – Desktopkomposition / REVIEW_READY

Vom kanonischen AP090-Parent dad89bb nach belegtem unabhängigen PASS, menschlichem
Prompt und Single-Parent-/Baumgleichheit. Gemeinsamer V2-Desktop-/Core-/Media-/Settings-/
Result-/Feedbackfluss, Workerpersistenz und kontrollierter Rollback/Shutdown.
1573 Windows-/ 190 gezielte Tests, 17 echte komponierte Serverchecks,
compileall/diffcheck PASS. Unabhängige Abnahme offen, Umsetzungsschreiben ab Abgabe
pausiert; keine kanonische Übernahme oder AP110-Implementierung.

[Runreport](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/01_REPORT.md).

## 2026-10-13 – AP-CV2-100 / R02-KORREKTUR: CI-01

CI-Replaytimeout bei 281-ms-Runnerverzögerung reproduziert; Testfristen für
durable Cursor-IO korrigiert, 280-ms-Regressionsfall ergänzt, fachliche Assertions
erhalten und erweitert. Windows1574/gezielte203/Servercheckpoint17/compileall
PASS, kandidatgebundene vollständige Logs. [R02-Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md).
REVIEW_READY im Selbstcheck; tatsächliche Übergabe erst nach grüner finaler PR-CI.
Keine Eigenabnahme, kanonische Übernahme oder AP110.

## 2026-10-13 – AP-CV2-100 / R04-KORREKTUR: F01

R03-Reviewakte fetch/ff-only übernommen. Fehlende korrelierte Settingsaudits
im tatsächlichen V2-Desktop/Bridge/Core reproduziert und minimal ergänzt; sieben
Positiv-/Negativ-/Rollback-/Busy-/Shutdown-/Ingressfälle hinzugefügt.
Windows1581/gezielte210/Servercheckpoint17/compileall/diffcheck PASS; neue
Kandidaten-/Log-/Gitblobbindung. [R04-Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md).
REVIEW_READY im Selbstcheck, tatsächliche Übergabe nach finaler grüner CI.
R03-CHANGES_REQUIRED historisch erhalten; frischer Gesamt-Review offen, kein Merge/AP110.

## 2026-10-13 – AP-CV2-100 / R05-ABNAHME: unabhängiger ROOT_PASS

PR #12 nach R04-Korrektur vollständig gegen Parent dad89bb5d und Kandidat `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` überprüft. F01 (korrelierte V2-Settings-Audits) nach realer Qt/Core/Bridge-Faultinjection und Red/Green-Tests unabhängig geschlossen, keine neuen Pflichtfindings; FINAL-01/02 und RUNTIME-01..04 technisch PASS. Externe Windows-Belege 1581/210 und gepinnte Servercheckpointfälle 17 sowie CI 38394758805 erfolgreich und unabhängig validiert. [R05-Bericht](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md). **WAITING_FOR_APPROVAL**, keine menschliche Mergefreigabe, kein AP110-Start.

## 2026-10-13 – AP-CV2-100 / R06-UEBERNAHME: menschliche Squash-Freigabe dokumentiert

Wörtlicher Auftrag „Hiermit wird die Freigabe zun Merge von PR #12, Arbeitspaket AP-CV2-100 erteilt. Bitte führe den Merge durch.“ als [Originalprompt](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R06-UEBERNAHME/00_PROMPT_ORIGINAL.md) gesichert. R05-PASS auf 0d45f8e9d3b484631da80be28f31c86ea85ab002; freigegebener Head 4c7be6945ae3f2c52748667963d00a1d5cd30d9f, kanonischer Parent dad89bb5d08e6d34abc5cfab57fc76010c5131dc. Finale PR-CI nach rein administrativem R06-Nachtrag nochmals erforderlich; ACCEPTED erst nach echtem Squash, Git-Parent- und Treeabgleich. Kein AP110-Vorgriff.

## 2026-10-13 – AP-CV2-110 / R01-UMSETZUNG: Legacyabbau und Releasequalifikation / REVIEW_READY

AP100-PASS, menschlichen R06-Auftrag und tatsächlichen PR12-Squash mit Single-Parent/
Baumgleichheit geprüft; vom kanonischen Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3` gestartet.
V1-Controller/Transport/Headless-/Mode-/Timer-/Feedbackfallbackautoritäten entfernt,
Migrationreader/Utilities erhalten, 251 methodengenaue Ersatzverantwortungen belegt.
Loggingapply-/Startretryanschlussfehler iterativ korrigiert. Windows1353/gezielte234/
17 echte Runtime-Serverchecks, compileall/diffcheck, EXE/Wheel/sdist und native
Windows-GUI-/Hello-/Ressourcencheckpoint für Source/Installed/Rebuilt/Frozen PASS.
[Report](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md).
Frischer unabhängiger Gesamt-Review offen; tatsächliche Übergabe erst nach finaler
grüner PR-CI, danach Schreiben pausiert. Kein eigener ROOT_PASS, Merge/Publish/Tag,
Serverpromotion oder AP-IV2-010. Hardware-/ASRgates bleiben explizit offen.
CI-01 LF-Checkout und CI-02 Frozen-Diagnose/Prozesscleanup im selben R01
selbstkorrigiert; frühere Belege erhalten, vollständige Neuqualifikation und
Produktkandidaten-CI38439465278 PASS. Finale Dokumentenspitzen-CI vor Abgabe.

## AP-CV2-110-R02 – 2026-10-14 – unabhängiger ROOT_PASS

PR #13: geprüfter Kandidat `44cf9a8fd1669242c00997966addc3667d448aa0`/Tree `46a4e6205b735ac202dcd611494d306936f8edc3`; sieben FINAL-Requirements technisch PASS, keine offenen Pflichtfindings. Fremde Windows-Vollsuite 1353 Tests, gezielte 234, Server 17 und GitHub-CI 38440922508 unabhängig geprüft; eigene Hardwaretests NOT_RUN. [R02-Bericht](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md). WAITING_FOR_APPROVAL, keine Freigabe/Merge, kein IV2-010.

## AP-CV2-110-R03 – 2026-10-14 – ausdrückliche Squash-Freigabe

Originalprompt für PR #13 wortgleich unter [R03](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) gesichert; unabhängiger R02-ROOT_PASS und Head `84b72e11b64d0d6220fe239614301dfd569d8256`, Zielparent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`, [CI38531198371](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38531198371) erfolgreich. Vor Merge **READY_FOR_CANONICALIZATION**; finale administrative R03-Spitze / CI und danach Squash-/Gitbaumprüfung notwendig. Noch kein ACCEPTED oder AP-IV2-010.

## 2026-10-14 – AP-IV2-010 R01 – REVIEW_READY

Paar Client0f0687c/Serverada13b0, Produkt unverändert ab43759d3. Windows1354, Server1964/14, Prozess11, Grenz17, Smokes7/7, compileall/diffcheck PASS. PR14; unabhängiger Review und spätere menschliche Übernahme ausstehend. Report: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md`. Kein Eigenreview/Merge/Folgepaket.

## 2026-10-15 – AP-IV2-020 / R01-UMSETZUNG: BLOCKED

AP010-Squash b80ed8b nach PASS/Freigabe tatsächlich verifiziert. Lokaler Serverada13b0
mit555 exakten Blobs, echten Community-/ONNX-Modellen und isolierten Daten bereit;
V1/VPS geschützt. Windowsbaseline1354, finale1360 und11 Prozessprüfungen PASS.
Echte Restart-Recovery zweimal FAIL: IV2-020-F01, temporärer HTTP-Vorcheck latcht
permanent BLOCKED. Noch nicht angewandter enger Clientpatch und gebündelte Realtest-
und Kalibrierungsabläufe gesichert. Produktänderungsfreigabe nötig. Reale Pflichtgates
offen; kein REVIEW_READY/PASS. R01 bleibt für dieselbe Fortsetzung zuständig.

## 2026-10-15 – AP-IV2-020 / R01 fortgesetzt: Recovery technisch requalifiziert

Ausdrückliche enge Scope-Ausnahme gesichert; derselbe Branch/R01/Draft-PR15.
Zehn nachgewiesene Client-Reconnect-/Recoveryfehler korrigiert, rote Repros und
Regressionen dokumentiert. Produkt41ca761, neue EXE/Wheel/sdist identitätsgebunden.
1373 Windows-Tests,11 Prozessfälle,1964 Server-Unit-Tests/14 optionale Skips,
native und reale lokale Modell-/Recoveryprüfungen grün. Drei Serverneustarts,
kein vorzeitiges PCM/Triggerfenster, Run-Pausen erhalten. V1/VPS unberührt.
Phase C vorbereitet; echte M-Gates/Kalibrierung/30min100 offen, kein REVIEW_READY.
[Audit](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/05_RECONNECT_AUDIT.md).

2026-10-15 AP-IV2-020/R01 Phase C: echte Manualbaseline und Followup3000/5000ms verglichen; Auftraggeber wählt5000ms. Sourceprodukt41ca761 unverändert, isolierte Profile gesichert. M01-Overlap und weitere M-Fälle offen. UX01 append_space ohne Wirkung außerhalb Recoveryfreigabe dokumentiert. Nach realem PowerShell-OOM nur0,95GB Hostcommitreserve; eigener Testclient sauber beendet, menschliches Freigeben unbenötigten Appspeichers angefragt, dann Wakeblock. Kein REVIEW_READY.

2026-10-15 AP-IV2-020/R01 Phase C: Hostspeicher nach menschlicher Aktion wieder frei, erster echter Wakeversuch ausgewertet. Sechs bewusst aufgenommene WAVs auf ausdrücklichen Nutzerwunsch004 bytegleich mit Manifest/Hashes und Messskripten versioniert. Erste Jarvis-Pauseaufnahme laut Mensch ohne Wakeanteil, Negativkontrolle. Echte ONNX-Frames und V2/Kroko-Replays0/160/320/480ms:320ms erhält beide direkten Nutzsätze, Livebestätigung offen. Produkt41ca761 unverändert, kein vollständiger M-PASS/REVIEW_READY.
