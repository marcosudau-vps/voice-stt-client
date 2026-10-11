> Historischer Nachweis der damaligen Vorbereitung. Keine aktuelle Branch-/Startanweisung. Maßgeblich sind [aktueller Prüfbericht](PRUEFBERICHT.md) und [Branchführung](../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

# Rollenworkflow Revision 7 – Umfang und Dokumentprüfung

Stand 2026-10-11. Unterlagenkandidat auf `work/client-v2/rollenworkflow`, Basis `b0525e6b730ce3ed8a0f84cad02305103b59ce5c`. Kein Produkt-/Servercode geändert, kein AP umgesetzt oder unabhängig abgenommen. Kein Commit, Push, PR oder Merge aus diesem Auftrag. `feat/client-v2` bleibt auf dem bisherigen Planungsstart.

## Auftrag im Originalwortlaut

> Okay, kannst du dann einmal je nach Rolle konkrete Anweisungen formulieren beziehungsweise aktualisieren? Also was muss ich genau lesen und machen? Was muss genau der ausführende Agent lesen und machen? Und was muss genau der Reviewer lesen und machen? Dass jeder klar weiss, wie der Ablauf ist und  nichts durcheinander gerät

## Ergebnis

- [Auftraggeberleitfaden](../REFERENZ/GOVERNANCE/AUFTRAGGEBER.md): einmaliger Lesepfad, sechs Aktionen, Übergabedaten, ausfüllbare Aufträge, aktuelle Vorbereitung vor AP-CV2-000.
- Aktualisierte Rollen-Skills/Checklisten für Umsetzung und unabhängige Abnahme; große Planung weiterhin nur bei Bedarf.
- [Gemeinsame PR-Übergabe](../SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md): ein kumulativer Paket-PR, Reviewer-Docs-Commit auf pausierter Paketlinie, geprüfte SHA getrennt von späterer PR-Spitze, ausdrückliche menschliche Übernahmefreigabe, genau ein Squash-Commit.
- Vorlagen für Umsetzung, Review, Korrektur und Übernahme mit passendem tatsächlichem Git-Freigabescope; Paket-/Runreport mit PR-/SHA-/Findingsbezug.
- Startcheck verlangt unabhängigen PASS, menschliche Freigabe und nachgewiesenen kanonischen Vorgängercommit. Vor Merge kein ACCEPTED; nach Merge tatsächliche Git-/PR-Provenienz statt zusätzlichem Aufräumcommit.
- Widersprechende Aggregate-CI-Vorabregel für GitHub-Squash korrigiert; erforderliche PR-Head/Base-Checks bleiben Pflicht. AP-CV2-000 enthält weiterhin die kleinste nötige CI-Anpassung.

## Ausgeführte Prüfungen

[Maschinenlesbares Ergebnis](rollenworkflow-validation.json): interne Markdown-Verweise und Erreichbarkeit der drei Rollen-Einstiege, JSON-Syntax, unveränderte 216 Requirements/Ownership, Paketstatus sowie Quellen-/Kontrakt-/Vektor-/Traceability-/Aufwandsbelege gegen den Git-Planungsstart geprüft. Keine neue Serverquellenanalyse oder neue Produktqualifikation behauptet; diese unveränderten Inhalte behalten ihre bisherigen Belege.

Beide Rollen-Skills mit `skill-creator/scripts/quick_validate.py` in der vorhandenen Python-3.12-Projektvenv geprüft: jeweils `Skill is valid!`. `git diff --check` bestanden. Diff auf erlaubte Unterlagenpfade begrenzt, kanonischer Ref unverändert. Neue Markdown-Dateien zusätzlich in Link-/JSON-/Scopeprüfung einbezogen.

## Durchgespielte Übergaben

| Fall | Verbindlicher Ablauf / Entscheidung |
| --- | --- |
| Kurzauftrag für erstes Paket | Skill → Startcheck → Paket → benötigte Kontrakte → Abgabecheckliste → PR/Runbelege |
| Vorgänger noch nicht übernommen | Kein abhängiger Implementierungsstart; fehlende Übernahme melden |
| REVIEW_READY | Exakten Kandidaten melden, Umsetzer pausiert, frischer Reviewer |
| CHANGES_REQUIRED mit Docs-Push | Reviewbericht vom Paketbranch übernehmen, kumulative Korrektur im selben PR, frischer Review |
| ROOT_PASS plus Docs-Commit | reviewed_sha bleibt Prüfkandidat; aktuelle Head-Differenz ausschließlich administrativ abgleichen |
| PASS ohne menschlichen Prompt | Keine kanonische Übernahme; Paket bleibt ROOT_PASS |
| Menschlicher Prompt, Base/Head verändert | Keine erzwungene Übernahme; Abweichung prüfen und passende Freigabe einholen |
| Erfolgreicher Squash | Ein Commit/ein Parent/Baumgleichheit nachweisen; Folgepaket startet von tatsächlichem kanonischem Abschluss |

Die Tabelle dokumentiert eine Prüfung der Anweisungen anhand dieser Situationen; sie ist kein ausgeführter GitHub-/Agenten-Integrationstest. GitHub-Branchschutz, formelle Approvals und CI wurden in diesem Dokumentauftrag nicht konfiguriert oder ausgeführt.

Die vollständige Unterlagenänderung wird vor AP-CV2-000 geprüft in dessen Paketbranch übernommen und mit dessen Paketaggregat kanonisch gesichert. Es entsteht dadurch kein zusätzlicher Planungscommit auf `feat/client-v2`. Ursprüngliche Planung und bisheriger Startcommit bleiben erhalten.
