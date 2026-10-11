# Ausführungsworkflow, Status und Übergaben

Stand 2026-10-11, Revision 10. Praktische Einstiege: [Auftraggeber](AUFTRAGGEBER.md), [Umsetzer](../../SKILLS/voice-stt-client-v2-umsetzen/SKILL.md), [Reviewer](../../SKILLS/voice-stt-client-v2-abnehmen/SKILL.md). Jeder Einstieg führt zur nötigen Checkliste und Akten-/Promptvorlage; die Gesamtplanung ist keine pauschale Run-Pflichtlektüre.

## Serieller Paketablauf

1. Auftraggeber beauftragt über den gemeinsamen Einstieg den nächsten Schritt; Paket und Rolle ermittelt der Agent selbst. Tatsächliche Gitrechte stammen aus dem Auftrag oder der gesicherten fortgeltenden Arbeitsfreigabe.
2. Umsetzer prüft [Vorgänger, Iststand und Grenzen](../../SKILLS/GEMEINSAM/references/START_UND_GRENZEN.md), arbeitet isoliert vom letzten übernommenen feat/client-v2-Commit und sichert Originalauftrag.
3. Umsetzer erfüllt Paketziele, Tests, Traceability und Plan-/Aktenpflege; im erlaubten Scope Kandidaten-Commit/Push und Paket-PR nach feat/client-v2. Übergabe REVIEW_READY mit genauem SHA, danach Schreibpause.
4. Frischer unabhängiger Reviewer prüft vollständigen Paketdiff und die kandidatengebundenen Umsetzungsnachweise, lokal im isolierten Worktree oder über GitHub in ChatGPT. Die Windows-Vollsuite wird im Umsetzungslauf nachgewiesen und nicht routinemäßig wiederholt. Er sichert Reviewreport/Evidenz und stellt diese bei tatsächlich erteilter Gitfreigabe durch einen Docs-Push auf denselben Paketbranch bereit. Maßgebliche Findings stehen dort, der PR verlinkt sie.
5. Bei CHANGES_REQUIRED beauftragt der Mensch Korrektur. Umsetzer übernimmt erst die Reviewunterlagen, korrigiert kumulativ, liefert einen neuen Kandidaten im selben PR. Neuer unabhängiger Review; frühere Akten erhalten.
6. Bei ROOT_PASS gibt ausschließlich der Mensch später per ausdrücklichem Prompt die Übernahme frei. Abschlussagent prüft aktuelle Head/Base, administrative Nachträge und erforderliche CI und übernimmt per Squash genau einen Paketcommit.
7. Erfolgreichen Merge/Parent/Commitanzahl/Baum prüfen und Abschluss melden. Erst jetzt Folgepaket beauftragen. Der neue Paketbranch sichert den tatsächlichen Vorgängerabschluss und aktualisiert dessen Übersicht ohne zusätzlichen Vorgängercommit.

SHA-Identitäten, Schreibübergabe, Docs-Commit und CI-Regeln stehen einmalig in [PR und Reviewübergabe](../../SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md). Vorgängerprüfung verlangt PASS, menschliche Freigabe und tatsächliche kanonische Übernahme, nicht lediglich einen Statusstring.

## Status

| Status | Voraussetzung |
| --- | --- |
| PLANNED | spezifiziert, noch nicht umgesetzt |
| IN_PROGRESS | Paketarbeit läuft |
| PART_PASS | nur Teilauftrag erfüllt; Paket bleibt offen |
| REVIEW_READY | vollständiger Kandidat mit Selbstchecks |
| CHANGES_REQUIRED | unabhängiger Review fordert Korrektur |
| ROOT_PASS | unabhängige DoD-/Requirementabnahme des benannten Kandidaten |
| CANONICALIZED / ACCEPTED | ausdrücklich freigegebener Aggregatecommit tatsächlich übernommen und erforderlicher Transport erfolgreich |
| BLOCKED | konkrete fehlende Pflichtvoraussetzung mit Owner/Aktion |
| CONDITIONAL | Serverfix-Vorlage ohne Befund |

Teststatus separat: PASS/FAIL/NOT_RUN/NOT_PROVEN/SKIPPED_EXPECTED. Ein Pflichtskip ist kein Erfolg. Vor Merge keinen ACCEPTED-Status vorschreiben; nach Merge Git-/PR-Provenienz heranziehen, auch wenn das vorab versionierte Paketindexfeld noch ROOT_PASS lautet.

## Akten, Aufwand und Tests

[Runablage](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md): Paketindex plus tatsächliche RUNS/Rnn-ROLLE mit Original-Prompt, einem Report und EVIDENCE/INDEX.md. Weitere Unterlagen nur bei Bedarf. Ein Steuerungsmeilenstein je relevantem Run/Gate; keine vorproduzierten Korrekturruns.

Regelfall ein vollständiger Fachlauf plus ein unabhängiger Review pro Paket. Korrekturen nur für tatsächliche Findings; kurzer menschlich freigegebener Abschluss vorzugsweise im noch offenen Umsetzerlauf. Kein obligatorischer dritter fachlicher Lauf. [Umfangsmodell](../PLANUNG/UMFANG_UND_AGENTENLAEUFE.md) unverändert.

Nach Produktänderung gesamte Clientregression bzw. vorgeschriebene schnelle Serversuite, gezielte Fälle und zugeordnete Build-/Crossrepo-/Hardwarepflichten. Fehler iterativ beheben. Unveränderte bestandene Checks nicht ohne Anlass endlos wiederholen. Reine Dokumentpflege verlangt Konsistenzprüfung. Interne technische Vorschläge bleiben gemäß [Spielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md) anpassbar.

## Server und Rebaseline

Serverada13b0 bleibt auf Distributed, finale Serverrestaggregation erst nach gemeinsamer Qualifikation und eigenem menschlichem Auftrag. Nötige Serverfixinstanzen getrennt führen; kein Client-PR auf Serverfeature/main.

Bei neuem Server-SHA Repro, Vertragswirkung, Clientwirkung und Testpaar belegen. Betroffene Kontrakte/Vektoren/Vokabular/Quellenmanifest/Matrix und Übergaben gemeinsam aktualisieren. Historische Pins nicht still umdeuten. CV2-000 qualifiziert die gezielte Feature-/Releaseintegration; bis dahin integratedClientCommit offen. Fachlicher Serververtrag und frühe [Servercheckpoints](../QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md) bleiben bestehen.

## Gemeinsamer Kurzauftrag und zusätzliche Reviews

Workflowrevision 10 ergänzt den [gemeinsamen Einstieg](../../SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md). Er ermittelt die eine nächste Aktion aus offenen Paket-PRs/Branches, Runakten und kanonischen Abschlüssen. Paket/Rolle/SHA/Reportpfade müssen nicht manuell übergeben werden. Die Ablaufbeschreibung oben beschreibt die ermittelten Rollenaktionen; eine ausdrückliche Zusatzreviewanweisung hat Vorrang.

[Zustandsreferenz](../../SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) definiert Phasen, Pflichtfelder, Übergänge und Pflege. WORKFLOW_STATUS.json wird auf Paketbranches geführt, keine Zwischenstatuscommits auf feat/client-v2. ROOT_PASS ohne menschliche Freigabe wartet. CHANGES_REQUIRED plus tatsächlich erteiltem Kurzauftrag beauftragt Korrektur. Bestehende Kandidatenrechte aus dokumentierter menschlicher Arbeitsfreigabe fortführen.

Ein weiteres unabhängiges Review bleibt optional beauftragbar. Neue Akte, kein Überschreiben; alle Pflichtfindings müssen vor Übernahme geklärt sein. Kein automatischer zusätzlicher Pflichtlauf.

## Unterbrechungen und Repositorywechsel

Beim Reviewbeginn REVIEW_IN_PROGRESS und writeOwner pflegen. Unterbrochene Schreibhoheit, Kandidatenwechsel, SERVER_FIX_REQUIRED, servereigene Sicherung und Rückkehr zum Client gemäß [Sonderfallreferenz](../../SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md). Bei letztem Paket den Endstatus COMPLETED aus tatsächlichen kanonischen Abschlüssen ableiten und Nachmerge-Beleg in der Paketakte sichern; kein Folgepaket/Status-Aufräumcommit erforderlich.
