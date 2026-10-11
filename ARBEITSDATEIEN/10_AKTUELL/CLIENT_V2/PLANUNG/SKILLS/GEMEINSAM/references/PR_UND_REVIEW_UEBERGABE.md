# Paket-PR, Reviewunterlagen und eindeutige Übergabe

Stand 2026-10-11, Rollenworkflow Revision 9. Pflichtreferenz beim ersten PR-/Review-/Übernahmeschritt; bei Wiederaufnahme nur geänderte Stellen lesen. Client- und Integrationspakete nutzen den Client-Paketbranch. Serverfixes behalten ihre getrennte Server-Distributed-Zielrolle gemäß [Branchreferenz](../../../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

## Ein Paket, ein kumulativer PR

Ziel ist `marcosudau-vps/voice-stt-client`, Base `feat/client-v2`, Head der beauftragte `work/client-v2/<paket>`-Branch. Dessen festgehaltener `canonical_parent` ist der zuletzt übernommene Abschlusscommit. Umsetzung, Planpflege, Korrekturen und Reviewunterlagen sind kumulative Kandidatencommits auf diesem Branch. Kein Force-Push, kein normaler Historymerge auf die Abschlusslinie, kein Auto-Merge.

Ein Draft-PR ist bei erteilter PR-Freigabe schon während der Umsetzung möglich; zur unabhängigen Abnahme erst den vollständigen Kandidaten als REVIEW_READY melden. Korrekturen aktualisieren denselben PR. Titel enthält AP-ID und Ergebnis; Beschreibung nennt Scope, Parent, Server-SHA, aktuellen Kandidaten und Links auf Paket-/Runakten. Findings und Testdetails stehen maßgeblich im versionierten Report; im PR nur Urteil/Kurzfassung und Links pflegen. PR-Anlage/Updates oder Kommentare sind nur im tatsächlich erlaubten Scope zulässig. In Codex den erstellten oder zur Bearbeitung beauftragten PR an die Aufgabe anhängen.

## Schreibübergabe an den Reviewer

1. Umsetzer meldet PR-URL und **exakten eingereichten SHA**; Workingtree sauber, alle erforderlichen Unterlagen und Belege bereits im Kandidaten. Ab diesem Punkt pausiert er Änderungen und Pushes auf diesem Paketbranch.
2. Reviewer verifiziert PR-Base, aktuellen Head und `canonical_parent`, liest den vollständigen Diff vom Parent und prüft genau diesen SHA in eigenem isolierten Worktree. Ein eigener lokaler `review/...`-Branch oder Detached-Checkout vermeidet, denselben lokalen Branch in zwei Worktrees auszuchecken. Tests verändern keine Produktdateien.
3. Reviewer legt einen neuen `Rnn-ABNAHME` unter `30_AUSFUEHRUNG/<AP-ID>/RUNS/` an: tatsächlicher Original-Prompt, `01_REPORT.md`, `EVIDENCE/INDEX.md` und Belege. `reviewed_sha`, `reviewed_tree`, `canonical_parent` und `server_sha` benennen den geprüften Kandidaten **vor** dem Reviewunterlagen-Commit.
4. Bei ausdrücklicher Review-Gitfreigabe committet er ausschließlich seine neue Reviewakte, notwendige Beleg-/Statusverweise in Paketindex, Matrix/Requirements, WORKFLOW_STATUS.json und Steuerungslog. Keine Produkt-, Test-, Kontrakt-, Vektor- oder fachliche Spezifikationsänderung. Auch ein Metadatenpfad ist keine Erlaubnis zur Änderung der fachlichen Kriterien. Fehlt ein Nachweis, als Finding melden, nicht erfinden.
5. Vor dem Push prüfen, dass der entfernte Paketbranch noch den eingereichten SHA hat. Den Reviewcommit nur als normalen Fast-forward auf **diesen Paketbranch** pushen. Ein eigener lokaler Reviewbranch darf damit seine Docs-Spitze auf den entfernten Paketbranch übertragen; keinen zweiten Review-PR eröffnen. Bei fremdem Fortschritt stoppen und den neuen Kandidaten melden. Nicht automatisch rebasen oder überschreiben.
6. Übergabe nennt Verdict, Reportpfad, tatsächlich geprüften SHA sowie den danach erzeugten Reviewunterlagen-Commit/aktuellen PR-Head. Die eigene Commit-ID aus Git ermitteln und in der Übergabe nennen; nicht als Selbst-SHA in den noch zu erzeugenden Report schreiben. Danach geht das Schreibrecht an den Umsetzer zurück, sofern ein Folgeauftrag vorliegt.

Ohne Commit-/Pushfreigabe erstellt der Reviewer trotzdem den lokalen Report und Evidenzsatz und meldet die noch offene Bereitstellung. Ein anderer Agent darf den Report erst nach nachvollziehbarer Übernahme sichern. `ROOT_PASS` ist keine automatische Erlaubnis dazu.

## Korrektur

Umsetzer holt die neue Paketbranch-Spitze und übernimmt sie bei sauberem Checkout fast-forward. Erst dann Findings lesen und im beauftragten Korrekturrun beheben. Report je Finding: Repro, Änderung, neuer Nachweis. Alte Reviewreports bleiben unverändert. Neue Produkt-/Test-/Kontraktänderungen brauchen erneut einen unabhängigen Review des gesamten Paketkandidaten; der letzte PASS darf nicht ungeprüft weitergelten.

## PASS-SHA und PR-Head sind unterschiedliche Identitäten

Der technische PASS gilt für `reviewed_sha/tree`. Der PR enthält danach zusätzlich die Reviewunterlagen. Vor Übernahme den Diff **vom reviewed_sha zum aktuellen PR-Head** prüfen: ausschließlich die oben erlaubten administrativen Akten-/Statusänderungen, mit vollständig enthaltenem PASS-Report. Kein ungeprüfter Produkt-, Test- oder Vertragsunterschied. Zulässige Unterlagennachträge erfordern diesen Abgleich, keine künstliche weitere fachliche Reviewrunde.

Eine menschliche Übernahmefreigabe nennt PR-URL, den aktuellen Head bei Freigabe, kanonischen Parent und den PASS-Report. Das Sichern des tatsächlich erteilten Freigabeprompts kann einen weiteren rein administrativen Paketbranch-Commit erzeugen, wenn der Prompt dies ausdrücklich erlaubt. Dessen Änderungen und neue Spitze ebenfalls abgleichen; nur diese benannte Ausnahme ist von der Freigabe des Ausgangs-Heads gedeckt. Bei anderem Fortschritt neu bewerten und eine neue passende Freigabe einholen. Keine Freigaben aus Vorlagen oder anderen Agenten ableiten.

## Squash-Übernahme nach menschlichem Prompt

Kanonische Übernahmen werden seriell ausgeführt: während eines freigegebenen Paketabschlusses kein zweiter Merge/Push auf `feat/client-v2`. Den Merge, soweit die verwendete Schnittstelle es unterstützt, an die erwartete finale Head-SHA binden; Head und Base unmittelbar vor Ausführung erneut lesen. Diese Arbeitsregel richtet keinen automatischen Branchschutz ein. Andere vorbereitete Paketversuche bleiben auf ihren Arbeitsbranches.

Der beauftragte Abschlussagent (vorzugsweise Umsetzer) liest den [Übernahmeablauf](../../voice-stt-client-v2-abnehmen/references/UEBERNAHME.md). Er sichert die Freigabe, prüft unveränderte Base, finale Head-Identität, administrative Differenzen, Scope, Mergekonflikte und die erforderlichen Prüfungen. Für GitHub-Squash gelten die Checks des finalen PR-Heads bzw. des von der CI geprüften Head/Base-Testmerges. SHA und Base des geprüften Stands dokumentieren. Eine verpflichtende CI darf nicht fehlen/rot/veraltet sein. Die spätere GitHub-Squash-SHA existiert vor dem Merge noch nicht; deshalb keinen unmöglichen Vorabcheck genau dieser SHA verlangen. Falls bisherige CI diese Feature-Base nicht abdeckt, wird der kleinste geeignete PR-Prüfpfad in AP-CV2-000 hergestellt und geprüft, ohne weitere Arbeitspakete zu erfinden.

Nach ausdrücklichem Auftrag **Squash and merge** durchführen ([GitHub-Mergemethoden](https://docs.github.com/en/pull-requests/reference/pull-request-merges)). Der Commit enthält Code, Planpflege, alle Run-/Reviewbelege und gesicherte Freigabe. Direkt danach nachweisen: genau ein neuer Commit von `canonical_parent` zum Aggregate-SHA, genau ein Parent gleich `canonical_parent`, Ergebnisbaum gleich finalem PR-Head (bei unveränderter Base). Erforderliche Nachmerge-Checks ebenfalls prüfen. Bei Abweichung keinen erfolgreichen Abschluss behaupten und keinen zweiten Reparaturcommit auf die Abschlusslinie setzen.

Eine lokal vorbereitete Einzelaggregation bleibt möglich, wenn sie ausdrücklich statt des PR-Merges beauftragt wird: ein Single-Parent-Aggregat auf dem exakten Parent, gleiche Baum-/Belegprüfung, erforderliche CI auf diesem tatsächlich vorbereiteten SHA, Ziel nur fast-forward und Push nur mit Freigabe. Nicht beide Wege für dasselbe Paket ausführen. Main/Serverfeature/Tags/Releases/Cleanup sind separate Aufträge.

## Status ohne zusätzlichen Aufräumcommit

Vor tatsächlichem Merge bleiben Akte und Matrix beim technischen `ROOT_PASS`; eine gesicherte Übernahmefreigabe bedeutet noch nicht ACCEPTED. Nach erfolgreicher Übernahme ergeben **gemergter PR und überprüfter eindeutiger AP-Aggregatecommit** den Status CANONICALIZED/ACCEPTED. Der Abschlussagent meldet SHA/Parent/Tree und Prüfergebnis an den Auftraggeber. Der nächste Paketbranch sichert diesen Abschlussnachweis und aktualisiert die Vorgängerübersicht zusammen mit seiner eigenen Planpflege. Dafür entsteht kein zweiter Commit des vorherigen Pakets. Der nächste Agent muss Git-/PR-Provenienz, PASS und Freigabe prüfen; weder ein veralteter ROOT_PASS-Text allein noch eine voreilig gesetzte ACCEPTED-Zeile reicht aus.
