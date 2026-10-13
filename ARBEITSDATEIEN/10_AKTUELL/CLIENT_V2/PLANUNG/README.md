# Client V2 – AP-CV2-080 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-13

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP070 **ACCEPTED**; AP070-Aggregat `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3` tatsächlich auf feat/client-v2, Single-Parent/Treegleichheit und unabhängiger PASS/menschlicher Prompt [belegt](../30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP080 technisch ROOT_PASS; menschliche Squash-Freigabe in R03 gesichert; tatsächliche Übernahme noch offen. Branch `work/client-v2/ap-cv2-080`. Spätere Pakete PLANNED, Server-Distributed bleibt bis zum gemeinsamen Abschluss offen.

[R02-Abnahme](../30_AUSFUEHRUNG/AP-CV2-080/RUNS/R02-ABNAHME/01_REPORT.md), [Runreport](../30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](../30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](../WORKFLOW_STATUS.json), [Planungseinstieg](README.md), [Produktinterfaces](../../../../docs/protocol-v2-settings-ui.md).

V2-Trigger-/Session-/Serverdialog, getrennte requested/effective/pending-Werte, schemaabhängige Typen/Grenzen/Defaults/Applypolicies, öffentliche Wake-Mehrfachauswahl. Adminprüfung mit tatsächlichem No-change-PATCH; Windows Credential Manager originbezogen mit Create/Replace/Delete und Memory-only bei Ausfall. Reconnect verlangt ausdrückliche Activation-/Drainentscheidung; asynchrone Replies sind dialog-/generationgebunden.

Qualifikation: 1513 vollständige Windows-Tests, 296 gezielte Regressionstests, 53 neue Clienttests. Reale Serverchecks: UI27, native Windows-UI/Vault29, bestehende Settings38, Supplement55 ohne Skips. compileall/diffcheck und Akten-/Blobprüfung PASS. Vollständige Log-/Hash-/Kandidatenbindung im Evidenzindex.

Nächste Aktion: CI- und Head-/Parentprüfung der genehmigten PR-Übernahme, anschließend genau ein Squash; kein automatischer AP090-Start. Reguläre Appkomposition samt koordinierter nativer Hotkey-Persistenz bleibt AP100; reale ASR/Mikrofon-/Wakekalibrierung AP-IV2-020. Die neue Oberfläche ist mit echten Produktionsservices lokal qualifiziert.

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
