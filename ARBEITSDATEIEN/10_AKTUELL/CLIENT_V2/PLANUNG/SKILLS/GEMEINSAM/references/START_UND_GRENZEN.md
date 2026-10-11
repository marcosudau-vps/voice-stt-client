# Start und gemeinsame Grenzen

Projektablageversion 2, Rollenworkflow Revision 9, Stand 2026-10-11. Diese Referenz gilt für beide Agenten. Gültige AGENTS und tatsächlicher menschlicher Auftrag bestimmen Scope und Gitrechte.

## Auftrag und Iststand

Lies konkreten Auftrag, gültige Repository-/Arbeitsblockregeln, aktuelle Steuerungseinträge unter ARBEITSDATEIEN/00_STEUERUNG und die aktive Paketdatei. Die [Baselinequelle](../../../EVIDENCE/planning-baseline.json) pinnt Server und Herkunftsstände. integratedClientCommit bleibt bis zur qualifizierten CV2-000-Übernahme offen.

Repo, Checkout, Branch, HEAD/Tree, Workingtree, kanonischen Parent und zuständige Paketakte festhalten. Fremde WIP nicht resetten oder überdecken; isolierten Pfad verwenden. Kein zusätzliches Agententeam oder neuer Chat ohne Auftrag.

## Verbindlicher Vorgängercheck

Vor abhängiger Implementierung im [Paketmanifest](../../../EVIDENCE/package-manifest.json) und [Paketindex](../../../ARBEITSPAKETE/README.md) Reihenfolge/Voraussetzungen ermitteln:

1. Aktuellen feat/client-v2-Stand aus Git prüfen; für den PR-Ablauf den entfernten Zielstand ebenfalls lesen. Paketbranch vom letzten tatsächlich übernommenen Stand bilden und dessen SHA als canonical_parent sichern. Review/Korrektur übernimmt stattdessen den konkret übergebenen kumulativen Kandidaten.
2. Beim Vorgänger unabhängigen ROOT_PASS-Report, tatsächlichen menschlichen Übernahmeprompt und eindeutigen Aggregatecommit nachweisen. Der Commit muss in der kanonischen Linie enthalten sein, genau einen Parent haben und zusammen mit dem gemergten Paket-PR zum geprüften Paket gehören. Bei ausdrücklich lokaler Übernahme den gleichwertigen Git-/Pushnachweis verwenden.
3. Vorgängerstatus ist eine Übersicht, kein alleiniger Beweis: voreiliges ACCEPTED reicht nicht. Umgekehrt darf nach belegtem erfolgreichen Merge ein noch auf ROOT_PASS stehender Index anhand der Provenienz beim neuen Paket aktualisiert werden. Kein zusätzlicher Vorgänger-Aufräumcommit.
4. Ist der Vorgänger nur REVIEW_READY/ROOT_PASS ohne Übernahme, fehlt eine Pflichtvoraussetzung oder ist die Base verändert: abhängige Umsetzung nicht beginnen, konkrete Lücke mit nächster Aktion melden. Keine automatische Übernahme, kein stummer Rebase.

AP-CV2-000 benötigt den reinen Planungsstart, keine bereits bestandene CV2-000-Abnahme. Der integrierte Produkt-SHA wird erst dort qualifiziert. Der Check ist verbindliche Agentenarbeit; keine Behauptung bereits eingerichteter Git-Hooks/Branchschutzregeln.

## Produktgrenzen und Status

Serververtrag, Produktziele, Daten-/Credentialschutz und Pflichtnachweise einhalten. [Spielraum](PLANUNGSSPIELRAUM.md) lässt lokale Implementierungsentscheidungen offen; vorhandenes Logging/Feedback gezielt anschließen.

| Zustand | Bedeutung |
| --- | --- |
| PLANNED / CONDITIONAL | Planung, keine ausgeführte Abnahme |
| IN_PROGRESS | beauftragter Run aktiv |
| REVIEW_READY | vollständiger Kandidat, Selbstchecks bestanden |
| CHANGES_REQUIRED | unabhängige Findings, Korrektur erforderlich |
| ROOT_PASS | unabhängige technische Paketabnahme bestanden |
| ACCEPTED / CANONICALIZED | menschlich freigegebener Aggregatecommit tatsächlich übernommen |
| BLOCKED | konkrete fehlende Pflichtvoraussetzung mit Owner/Auflösung |

Teil-PASS/REVIEW_READY/ROOT_PASS allein erlaubt kein Folgepaket. Teststatus PASS/FAIL/NOT_RUN/NOT_PROVEN/SKIPPED_EXPECTED getrennt führen. Fehlender Pflichtnachweis blockiert das zugeordnete Paket, nicht fachfremde frühere Pakete.

## Git, Akten und Planpflege

[Branchreferenz](../../../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md): feat/client-v2 führt nur Planungsstart und je angenommenem Paket einen Single-Parent-Aggregatcommit. Alle Bearbeitung auf Paketbranches. [PR und Reviewübergabe](PR_UND_REVIEW_UEBERGABE.md) lesen, bevor PR-, Review-Push- oder Übernahmeschritte ausgeführt werden. Menschlicher Auftrag kann Kandidaten-Commit/Push/PR erlauben; nur ein späterer ausdrücklicher Übernahmeprompt erlaubt den Squash-Merge nach unabhängigem PASS. Keine Vorlage und kein Agentenurteil ersetzt diese Freigabe. Main/Tags/Release/Cleanup getrennt beauftragen.

[Runablage](PAKETABLAGE_UND_VORLAGEN.md): Original-Prompt, Report, Evidenzindex, Paketindex und genau einen Meilenstein pro relevantem Run/Gate sichern. Abgeschlossene Berichte erhalten, Zusatzsteuerung getrennt. Keine Secrets, Nutzeraudio oder unredigierte Transkripte in Git.

Nur betroffene Requirements, Planstellen und Übergaben pflegen; Belege an Kandidat und Runtime binden. Reviewer ändern nur Reviewbelege/administrative Verweise, keine fachlichen Kriterien. Serverdefekte als eigene AP-SV2-FIX-Instanz mit Repro behandeln. Neue Serverbaseline verlangt betroffene Kontrakte/Vektoren/Quellen/Matrix und Paarqualifikation. FIX_ACCEPTED bedeutet freigegebene Sicherung auf Server-Distributed, keine sofortige Serverfeature-Promotion.

Ausführliche Sonderfälle bei Bedarf: [Regelwerk](../../../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md), [Workflow](../../../REFERENZ/GOVERNANCE/AUSFUEHRUNGS_WORKFLOW.md).

## Gemeinsamer Auftrag und Zustandsermittlung

Bei „Mach den nächsten Schritt“ übernimmt der [gemeinsame Einstieg](../../voice-stt-client-v2-naechster-schritt/SKILL.md) die Paket-/Rollenauswahl. [Zustandsregeln](ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) verpflichten zur Prüfung offener Paketlinien vor neuem AP und zur Pflege von WORKFLOW_STATUS.json. Bestehende Freigaben nicht erneut abfragen; keine aus dem Status erfinden. Zusätzliches unabhängiges Review ist jederzeit auf ausdrücklichen Auftrag möglich, neue Akte, keine Eigenabnahme.

## Technische Abnahme und späterer Abschluss

Die unabhängige Prüfung bewertet den eingereichten Kandidaten anhand seiner fachlichen Pflichtkriterien und tatsächlichen Tests. Kriterien, die einen bestandenen Review, menschliche Übernahme oder den kanonischen Abschluss-SHA betreffen, werden erst in der entsprechenden späteren Phase erfüllt. Sie sind keine zirkulären Voraussetzungen für REVIEW_READY oder ROOT_PASS. Der Review fordert keine bereits erfolgte eigene kanonische Übernahme; ACCEPTED bleibt dem nachgewiesenen Abschluss vorbehalten.
