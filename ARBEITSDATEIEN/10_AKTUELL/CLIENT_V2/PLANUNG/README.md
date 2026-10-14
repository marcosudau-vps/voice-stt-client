# Client V2 – AP-IV2-010 / R01-UMSETZUNG / REVIEW_READY, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](../30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](../WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Client V2 – AP-CV2-110 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-14

[Paket-PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base `feat/client-v2`, Head `work/client-v2/ap-cv2-110`.

Aktiver Arbeitsblock [CLIENT_V2](../README.md);
[Einstieg Planung](README.md), [Workflowstatus](../WORKFLOW_STATUS.json).
AP000 bis AP100 tatsächlich ACCEPTED auf feat/client-v2; letzter kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100-PASS, menschlicher R06-Auftrag und wirklicher PR12-Squash
[verifiziert](../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).

AP110 auf `work/client-v2/ap-cv2-110`: ausführbare V1-Autoritäten entfernt,
Migrationreader und Utilities erhalten, Source/Wheel/sdist/Frozen mit belegter
Helloidentität und nativer Windows-GUI qualifiziert. Windows **1353 PASS**,
gezielte **234 PASS**, Servercheckpoint **17 PASS**, compileall/diffcheck und
alle Build-/Ressourcen-/Installationschecks PASS. Getesteter Produktcommit
`cf42a2a9d96c1ebc88035817a5d529dfe04e4306`; finale PR-Spitze ergänzt ausschließlich administrative Unterlagen.
[Report](../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Kompatibilität](../../../../docs/compatibility.md), [Runtime](../../../../docs/protocol-v2-runtime.md).

Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.
Bekannte Legacy-Profile und History werden mit Backup migriert; kein V1-Fallback.
Builds liegen lokal unter dist, kein veröffentlichter Release. Keine realen
ASR-/Mikrofon-/USB-/Fremdanwendungs-/Wahrnehmungsgates behauptet.

**Aktueller Reviewabschluss (2026-10-14):** [AP110 R02 unabhängiger ROOT_PASS](../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) auf `44cf9a8fd1669242c00997966addc3667d448aa0`; FINAL-03 bis FINAL-09 technisch PASS, keine offenen Pflichtfindings. **ROOT_PASS** mit menschlicher **R03-Freigabe** – finale Git-/CI-Prüfung und Squash stehen aus. Kein AP-IV2-010-Start zuvor.

**Übernahmefreigabe 2026-10-14:** [R03-Originalprompt](../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) und [R03-Abschlussablauf](../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/01_REPORT.md) dokumentiert. Aktuelle Phase **READY_FOR_CANONICALIZATION**; unabhängiger R02-ROOT_PASS unverändert. Nach finaler CI und Head-/Baseprüfung ist der einzelne Squash-Merge von PR #13 erlaubt. Ohne belegten GitHub-Merge noch nicht ACCEPTED; kein Release/Tag/Servermerge/AP-IV2-010.

---

## Historischer AP100-Stand vor dessen tatsächlicher kanonischer Übernahme

# Client V2 – AP-CV2-100 / R05-ABNAHME / ROOT_PASS, 2026-10-13

AP-CV2-000 bis AP-CV2-090 auf `feat/client-v2` ACCEPTED; letzter kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der aktuelle AP-CV2-100-Paketbranch `work/client-v2/ap-cv2-100` ([PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)) wurde unabhängig am Kandidaten `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` geprüft: **technischer ROOT_PASS**, 6/6 Paketrequirements erfüllt, `CV2-100-R03-F01` geschlossen.

[R05-Abnahmebericht](../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md), [unabhängige Evidenz](../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/EVIDENCE/INDEX.md), [R04-Korrekturbelege](../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](../WORKFLOW_STATUS.json).

Extern qualifizierte Windows11-Suite **1581 PASS**, gezielte Tests **210 PASS**, **17** echte gepinnte Client-/Servercheckpoints am Server `ada13b0`, GitHub-Actions-CI **38394758805** erfolgreich auf dem geprüften Kandidaten. Reviewer hat diese Belege unabhängig geprüft, aber keine eigene Windows-/Hardwaretestausführung vorgenommen.

**Nächster Schritt: WAITING_FOR_APPROVAL.** Ausdrückliche menschliche Freigabe des Squash-Merges von PR #12 erforderlich, davor aktueller PR-Head, unveränderte Base, ausschließlich administrative R05-Nachträge sowie finale CI prüfen. Kein Merge und kein Start von AP-CV2-110 durch dieses Review.

---

## Historischer R04-Stand vor unabhängigem R05-Review

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](../30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](../WORKFLOW_STATUS.json), [Runtimeinterfaces](../../../../docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

## Historischer Stand vor AP-CV2-020

# Voice-STT Client V2 – Einstieg

Stand **2026-10-11, Revision10, Rollenregelversion7**. AP-CV2-000 ACCEPTED, tatsächlicher PR-#2-Aggregatcommit `1cf076bd2ed56929b1a3780bc140da51348a8295`; AP-CV2-010 ROOT_PASS (R02; WAITING_FOR_APPROVAL); [Paketakte](../30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md). PASS, menschliche Freigabe und tatsächlicher Merge wurden beim AP010-Start geprüft; [AP010-Akte](../30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md). Revision-9-Start und freigegebene Dokumentkorrektur Revision10 bleiben erhalten.

## Dein Einstieg als Auftraggeber

Lies [Dein Ablauf als Auftraggeber](REFERENZ/GOVERNANCE/AUFTRAGGEBER.md). Dort stehen Kurzauftrag, Zustandserkennung, optionale Zusatzreviews und deine separate Übernahmefreigabe. Einmal lesen; je Paket danach nur dessen Ziel und den unabhängigen Reviewreport.

## Einen Agenten beauftragen

| Auftrag | Einziger Einstieg | Danach automatisch über Verweise |
| --- | --- | --- |
| Nächste Aktion selbst bestimmen | [Gemeinsamer Skill](SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md) | Git-/PR-/Aktenstand, Zustände, passende Rolle |
| Paket umsetzen oder konkret korrigieren | [Umsetzungsskill](SKILLS/voice-stt-client-v2-umsetzen/SKILL.md) | aktive Paketdatei, benötigte Kontrakte, Arbeitsregeln, Abgabecheckliste, Aktenvorlagen |
| Fertigen Kandidaten unabhängig prüfen | [Abnahmeskill](SKILLS/voice-stt-client-v2-abnehmen/SKILL.md) | Paket/Runbelege, Abnahmecheckliste, tatsächliche Traceability, eigene Tests, Reviewreport |

Standardauftrag: **„Mach den nächsten Schritt“**. [Gemeinsamer Einstieg](SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md) ermittelt offene Paketlinie, Zustand und passende Rolle selbst; keine manuelle AP-/SHA-/Reportübergabe. [Verbindliche Zustände und Pflege](SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md), [aktuelle strukturierte Übersicht](../WORKFLOW_STATUS.json). Ein ausdrückliches weiteres unabhängiges Review hat Vorrang. ROOT_PASS ohne deine Übernahmefreigabe bleibt Warten.

Die beiden Rollen-Skills bleiben Unterabläufe des gemeinsamen Einstiegs; gezielte Rollenaufträge sind optional weiterhin möglich. Eine Aktion pro Auftrag, keine Eigenabnahme, kein automatischer Main-/Releaseabschluss. Gesamtplanung nur bei Bedarf. Die vollständigen Unterlagen liegen auf feat/client-v2. Tatsächlich erlaubte Kandidaten-Gitrechte beim [ersten Umsetzungsauftrag](SKILLS/voice-stt-client-v2-naechster-schritt/assets/PROMPT_ERSTER_UMSETZUNGSAUFTRAG.md) einmalig festhalten; Folgeaufträge nutzen die gesicherte Arbeitsfreigabe.

## Ablage

```text
README.md                       Einstieg für Auftraggeber
SKILLS/                         Rollenabläufe, Checklisten, Auftrags-/Aktenvorlagen
ARBEITSPAKETE/                   konkrete Spezifikationen und DoD
REFERENZ/
  PLANUNG/                      Gesamtablauf, Zielbild, Umfang, Analysen, Entscheidungen
  KONTRAKTE/                    Serververträge und Vektoren
  TRACEABILITY/                 Matrix und Requirements-JSON
  QUALIFIKATION/                Test-/Build-/Realabnahmeplan
  GOVERNANCE/                   ausführliche Regelwerks-/Workflowreferenz
EVIDENCE/                       Quellen, Baselines und Prüfung der Planung
```

## Fachliche Referenzen bei Bedarf

- [Paketindex](ARBEITSPAKETE/README.md) und [Gesamtimplementierungsplan](REFERENZ/PLANUNG/IMPLEMENTIERUNGSPLAN.md).
- [Produktzielbild](REFERENZ/PLANUNG/ZIELBILD.md), [Erhalt und Umbau](REFERENZ/PLANUNG/ANALYSEN/BESTAND_UND_UMBAU.md), [Branchbewertung](REFERENZ/PLANUNG/ANALYSEN/CLIENT_BRANCH_BEWERTUNG.md).
- [Kontrakte und Vertragsvektoren](REFERENZ/KONTRAKTE/README.md).
- [Traceability](REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md), [Requirements-JSON](REFERENZ/TRACEABILITY/requirements.json) und [Test-/Abnahmeplan](REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md).
- [Umsetzungsspielraum](SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md), [Paketakten](SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md), [ausführliches Agentenregelwerk](REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md).
- [Baselinequelle](EVIDENCE/planning-baseline.json), [Quellenmanifest](EVIDENCE/source-manifest.json) und [Planungsprüfbericht](EVIDENCE/PRUEFBERICHT.md).

Serverreferenz bleibt `ada13b011e1d3829f78e7f389e3b927795a2b3be`; Client setzt die vorhandene Featurelinie fort, V1-main liefert gezielte Releaseverbesserungen. CV2-000 ist tatsächlich übernommen; kanonischer integrierter Start-SHA ist `1cf076bd2ed56929b1a3780bc140da51348a8295`. Exakte Werte und Rollen stehen in der Baselinequelle.

Ein Paket-PR zielt auf `feat/client-v2`. Umsetzer und Reviewer übergeben das Schreibrecht nacheinander; Reviewberichte werden im erlaubten Scope auf dem Paketbranch versioniert. [PR-/SHA-Übergabe](SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md).

Unabhängiger PASS ist die technische Abnahme. Kanonische Übernahme braucht anschließend deinen ausdrücklichen Prompt; die Skillaufrufe erteilen dafür keine automatische Freigabe. Bestehende alte Planungsunterlagen bleiben erhalten; diese Ablage ist eigenständig vollständig.

## Gemeinsamer Entwicklungsbranch

`feat/client-v2` führt diese vollständige Planung und die kommende Umsetzung gemeinsam: erster Commit nur Unterlagen, danach je angenommenem Paket genau ein Commit mit Code und aktualisierten Unterlagen. Bearbeitung/Korrekturen finden auf untergeordneten Paketbranches statt. Verbindliche Zuordnung, Ausgangs-SHAs, Aggregationsprüfungen und Serverabgrenzung: [Branchführung und Planpflege](REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md). Aktive Ablage im Clientrepository: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/`.

Paketweise Funktionsmessung und früher Serverkontakt: [Inkrementelle Checkpoints](REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md).

## Bedarfsgerechte Ausnahme-Referenzen

[Wiederaufnahme, Kandidatenwahl, Serverfix-Routing und Endabschluss](SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md) sowie [unabhängig geprüfte Windows-/Hardwarebelege](REFERENZ/QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md) nur beim betreffenden Fall laden. [Bewertung des externen Prüfberichts](EVIDENCE/BEWERTUNG_PRUEFBEFUNDE_REV10.md). Aktuelle Dokumentrevision/roleSkillVersion stimmen in Baseline und Paketmanifest überein; schemaVersion, Aktenstruktur und Aufwandsmodellversion sind eigenständige Versionen.

Rollenmetadaten Version 6 ergänzen in R03 die Übergabe-/Aktenprüfung und den unabhängigen Testweg; fachlicher Plan und Revision 10 bleiben erhalten. [R03-Report](../30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md).

## Windows-Testverantwortung ab R05

Windows-Vollsuite verbindlich in Umsetzung/Korrektur mit Kandidatenbezug und vollständigen Logs nachweisen. ChatGPT-Reviewer prüfen Code und gültige Belege; keine obligatorische Wiederholung. [Verbindliche Nachweisregel](REFERENZ/QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md). Historische Empfehlungen oder abgeschlossene Reports steuern diese neue Aufgabenverteilung nicht.
