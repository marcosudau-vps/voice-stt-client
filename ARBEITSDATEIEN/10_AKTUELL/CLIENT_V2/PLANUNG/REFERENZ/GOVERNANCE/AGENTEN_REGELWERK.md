# Verbindliche Rollen und Paketabnahme

Stand 2026-10-11, Revision 10. Praktische Rollenabläufe stehen in [Auftraggeberleitfaden](AUFTRAGGEBER.md), [Umsetzungsskill](../../SKILLS/voice-stt-client-v2-umsetzen/SKILL.md) und [Abnahmeskill](../../SKILLS/voice-stt-client-v2-abnehmen/SKILL.md). Dieses Dokument erläutert deren verbindliche Grenzen; kein zusätzlicher vollständiger Lesedurchgang je Run.

## Rollen und Gitrechte

| Rolle | Aufgabe | Gitrechte nach tatsächlichem menschlichem Auftrag |
| --- | --- | --- |
| Auftraggeber | Paket beauftragen, frischen Review veranlassen, nach PASS ausdrücklich Übernahme erlauben | einzige Instanz der kanonischen Übernahmefreigabe |
| Umsetzer | vollständiges Paket, Tests, Traceability, Plan-/Runpflege; Findings korrigieren | Kandidaten-Commits/Push/Paket-PR im beauftragten Scope; Squash-Merge erst nach späterem menschlichem Prompt |
| Reviewer | vollständigen Kandidaten unabhängig prüfen, eigene Tests, Report/Findings/Evidenz | ausschließlich beauftragte Reviewunterlagen und administrative Verweise auf Paketbranch commit/push; keine Produktfixes, keine eigene Übernahmefreigabe |
| ausdrücklich beauftragter Abschlussagent | Freigabe/Identität/CI prüfen, einen Paketcommit übernehmen und Ergebnis nachweisen | genau freigegebener Squash-Merge bzw. ausdrücklich gewählte lokale Einzelaggregation |

Rollen dürfen keine Rechte aus Vorlagen oder technischen Verdicts ableiten. Kandidatenrechte können bereits im Paketauftrag ausdrücklich enthalten sein und müssen nicht für jede Selbstkorrektur erneut erteilt werden. Main, Serverfeature-Promotion, Tags, Releases, Cleanup, Rebase und Force-Push sind keine impliziten Paketaktionen; kein Auto-Merge. Fehlende Gitrechte lassen geprüften lokalen Diff und Report zu, aber keinen behaupteten Remoteabschluss.

## Branchführung und Schreibhoheit

[Branchreferenz](BRANCH_UND_PLANPFLEGE.md): feat/client-v2 beginnt mit einem Unterlagencommit; danach genau ein Single-Parent-Aggregat je angenommenem AP, Code und Planpflege gemeinsam. Alle Bearbeitung auf untergeordneten Paketbranches vom letzten tatsächlich übernommenen Parent. Mehrere unabhängige Versuche von derselben Base erlaubt, nur ein gewählter Kandidat wird übernommen.

Paket-PR-Base ist feat/client-v2. Implementer und Reviewer schreiben nicht gleichzeitig auf denselben Paketbranch. Reviewfreeze am eingereichten SHA; eigener Reviewworktree; danach erlaubter rein administrativer Reviewcommit auf die kumulative Paketlinie. Umsetzer übernimmt die Reviewspitze vor Korrektur. Details: [PR und Reviewübergabe](../../SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md). Ein Reviewer-Docs-Commit wird nicht als automatisch erneut geprüfter Produkt-SHA dargestellt.

## Auftrag und Sessions

Ein Agentenlauf ist eine Session. Noch offener Lauf kann nach Usage-Reset weitergehen; abgeschlossene Akte nicht rückwirkend umschreiben. Review eines fertigen Kandidaten startet in frischer unabhängiger Session. Regelfall ein vollständiger Umsetzungs- plus ein Reviewlauf je AP; weitere Korrekturen nur bei echten Findings. Keine zusätzlichen Agenten/Chats ohne Auftrag.

Paketfolge seriell. [Startcheck](../../SKILLS/GEMEINSAM/references/START_UND_GRENZEN.md) prüft PASS, menschliche Freigabe und tatsächlichen kanonischen Vorgängercommit. PART_PASS/REVIEW_READY/ROOT_PASS ohne Übernahme gibt kein Folgepaket frei. Den kurzen Abschluss kann der noch offene Umsetzerlauf nach menschlichem Prompt erledigen; kein obligatorischer dritter fachlicher Lauf.

## Umsetzung und Prüfung

Fachlicher Paketumfang, Requirements, Produktziele, Serververtrag und Pflichtnachweise verbindlich. [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md) erlaubt begründete interne Umsetzung, andere Modul-/Testnamen und lokale technische Startwerte. Logging/Feedback/Audio/UI erhalten und passend anschließen; keine versteckten Folgefeatures.

Nach Produktänderungen gezielte Tests und gesamte Clienttestsuite, compileall und Diffprüfung; bei Serverfix gesamte schnelle Serversuite und betroffene Clientintegration. Zugeordnete Build-/reale Pflichten gelten nur für die entsprechenden Pakete. Reviewer prüft Regression und kritische Repros eigenständig; nötige Plattformdurchführung auf realem Prüfhost und verifizierte Fremd-Hardwarebelege nach der unten verlinkten Nachweisregel führen. Fehler iterativ reproduzieren/beheben; Pflichtfehler oder Pflicht-NOT_RUN blockieren Paket-PASS. Reine Dokumentänderung braucht Dokument-/Link-/JSON-/Matrixkonsistenz, keine erfundene Produktqualifikation.

Ersetzte V1-Assertions mit fachlichem Nachfolger verknüpfen: Assertion, Requirement, konkrete Testmethode, Begründung. Keine pauschalen Skips oder toleranten Doubles zur Abnahme. Teststatus PASS/FAIL/NOT_RUN/NOT_PROVEN/SKIPPED_EXPECTED getrennt. Tatsächliche frühe [Servercheckpoints](../QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md) bleiben paketweise Pflicht; IV2-010 ist abschließende Paarqualifikation.

## Akten und technisches Verdict

[Runablage](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md): ein Paketindex; pro tatsächlichem Run Original-Prompt, ein Report und Evidenzindex mit Belegen. Zusatzsteuerung getrennt sichern; Entscheidungen bei Bedarf. Ein Steuerungsmeilenstein je relevantem Run/Gate. Secrets, Nutzeraudio, Nutzerdatenbanken und unredigierte Logs nicht in Git.

Reviewer prüft ganzen Paketdiff einschließlich Plan-/Matrixpflege, keine bloße letzte Korrektur. Report identifiziert reviewed_sha/tree, canonical_parent, server_sha, Requirementnachweise, selbst ausgeführte Tests und Findings. ROOT_PASS ausschließlich bei vollständiger DoD. Sonst CHANGES_REQUIRED oder konkrete fehlende Voraussetzung. Finding mit ID, Wirkung/Schwere, Repro, Requirement, Owner und verlangtem Nachweis. Kleine Schwere beseitigt keine Pflicht.

Technischer PASS ist keine menschliche Freigabe. Bei gemeinsamem GitHub-Account ersetzt er keine technisch verlangte GitHub-Approval durch einen anderen Account. Branchschutz/CI sind dadurch nicht automatisch eingerichtet.

## Übernahme und Abschlussprovenienz

Nur nach ausdrücklichem menschlichem Prompt gilt der [Übernahmeablauf](../../SKILLS/voice-stt-client-v2-abnehmen/references/UEBERNAHME.md). Finale Head/Base, ausschließlich erlaubte administrative Änderungen nach Review, vollständige Belege und erforderliche CI vor Squash prüfen. Im GitHub-PR-Verfahren CI für finalen Head bzw. Head/Base-Testmerge belegen; keine unmögliche Vorabprüfung der erst beim Merge erzeugten Squash-SHA. Lokal vorbereitete Einzelaggregation prüft ihren schon existierenden Aggregate-SHA. Nie beide Wege für dasselbe AP.

Nach Merge genau einen neuen Single-Parent-Commit auf exaktem Parent und vollständige Baumgleichheit nachweisen. Fehlgeschlagene Git-/CI-/Promotionsaktion nicht ACCEPTED nennen. Abschluss-SHA aus Git ableiten; Nachmerge-Abschlussnachweis auf nächstem Paketbranch sichern, keinen zweiten Aufräumcommit. Maßgebliche Statusdefinitionen: [Workflow](AUSFUEHRUNGS_WORKFLOW.md).

## Server und Cleanup

Serverfix nur mit konkretem Repro als AP-SV2-FIX-Instanz. Neue Serverbaseline erfordert betroffene Kontrakte/Fixtures/Matrix und gemeinsame Paarqualifikation. Serverfixstatus FIX_ACCEPTED belegt ausschließlich freigegebene Sicherung auf Server-Distributed. Finale Serverrestaggregation später separat freigeben.

Vor ausdrücklich beauftragtem Cleanup Quellcommit/Tree, Review, Aggregatecommit und Belege verknüpfen; benötigte uncommittierte/ignorierte Daten sichern. Keine ungeklärte Arbeit löschen und keine bisherigen Kandidatenhistories umschreiben. Historische Planung/Quellenpins bleiben ihrem geprüften Stand zugeordnet.

## Auswahl der nächsten Rolle

Workflowrevision 10: Ein tatsächlich erteilter Kurzauftrag „Mach den nächsten Schritt“ beauftragt die anhand der [Zustandsregeln](../../SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) bestimmte eine Fachaktion. Der [gemeinsame Einstieg](../../SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md) ermittelt AP/Kandidat/Rolle selbst. Keine manuelle Übergabe nötig; tatsächliche Gitrechte bleiben in gesicherter Arbeitsfreigabe referenziert. Ein kanonischer AP-Commit ist innerhalb des vereinbarten Workflows der Abschlussnachweis; offene Paketlinien und dazugehörige Belege dennoch mitprüfen.

Jeder Run pflegt die Statusübersicht und nächste Aktion vor Abgabe. ROOT_PASS ohne menschlichen Prompt wartet. Eine ausdrücklich beauftragte zusätzliche unabhängige Abnahme hat Vorrang; neue frische Akte, frühere Findings erhalten und klären. Es entsteht keine Pflicht zu einem zweiten Review.

## Wiederaufnahme, Serverrouting und Endnachweis

[Gemeinsame Sonderfallreferenz](../../SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md) regelt tatsächliche Schreibübergabe/Recovery, Auswahl und Ersetzung von Kandidaten, ausdrücklich beauftragte Server-FIX-Linien samt Clientrückkehr, nachträgliche Zusatzkorrekturen und COMPLETED ohne weiteres reguläres Paket. Statusfelder erteilen weiterhin keine Rechte.

Echte Plattform-/Hardwaredurchführung darf bei fehlendem Agentenzugriff ein benannter Bediener übernehmen. Reviewer prüft Identität, Vollständigkeit und Wirkung und veranlasst notwendige Wiederholungen; Eigen-/Fremddurchführung getrennt berichten. [Verbindliche Nachweisregel](../QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md). Keine Aufhebung eines Pflichtgates.
