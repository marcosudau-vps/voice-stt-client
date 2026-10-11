---
name: voice-stt-client-v2-abnehmen
description: Prüfe einen vollständigen Voice-STT-Client-V2-Paketkandidaten unabhängig und sichere Verdict, Findings und eigene Testbelege als Reviewunterlagen auf dem Paketbranch.
---

# Voice-STT Client V2 – unabhängiger Reviewer

Starte in einer frischen Session nach der Abgabe des Umsetzers. Deine Aufgabe ist unabhängige technische Prüfung und nachvollziehbare Rückmeldung. Produktfixes gehen an den ausführenden Agenten; du gibst keine kanonische Übernahme frei.


Bei einem Auftrag „Mach den nächsten Schritt“ zuerst den [gemeinsamen Einstieg](../voice-stt-client-v2-naechster-schritt/SKILL.md) verwenden; Paket/Rolle/Kandidat aus dem dokumentierten Stand ermitteln. Der erteilte Kurzauftrag gilt für die dadurch bestimmte fachliche Aktion. Vor jeder Abgabe [Zustandsübersicht](../GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) samt Belegverweisen und nächster Aktion pflegen. Gitrechte aus tatsächlichem Prompt bzw. gesicherter fortgeltender Arbeitsfreigabe; Übernahme weiterhin separat.

## Was du liest

1. [Start und Grenzen](../GEMEINSAM/references/START_UND_GRENZEN.md) und den tatsächlich erteilten Reviewauftrag.
2. Die beauftragte Datei im [Paketindex](../../ARBEITSPAKETE/README.md), benötigte Kontraktabschnitte, den vollständigen PR-Diff vom kanonischen Parent sowie Umsetzung-/Korrekturberichte.
3. [Abnahmecheckliste](references/ABNAHMECHECKLISTE.md) und [PR und Reviewübergabe](../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md): Kandidatenfreeze, eigener Worktree, zulässiger Reviewcommit und Rückgabe.
4. [Runablage](../GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) beim Anlegen deiner Akte. Die Gesamtplanung nur bei einer konkreten Scopefrage öffnen.

## Was du prüfst

Verifiziere PR-Base feat/client-v2, eingereichten SHA/Tree, kanonischen Parent, Serverbaseline und vollständigen Paketumfang. Arbeite in eigenem isolierten Worktree auf genau dem eingereichten Stand. Der Umsetzer pausiert Paketbranch-Pushes während deiner Prüfung.

Prüfe Paketziele, Requirements und DoD anhand tatsächlichen Codes und Belegen. Umsetzungsvorschläge gemäß [Spielraum](../GEMEINSAM/references/PLANUNGSSPIELRAUM.md) nach Wirkung beurteilen; abweichende interne Namen allein sind kein FAIL. Daten-/Configmigration, Session-/IDguards, Nebenwirkungen, Fehler/Shutdown und erhaltenes Logging/Feedback konkret prüfen.

Führe kritische Repros und vollständige betroffene Produktregression eigenständig aus bzw. veranlasse die nötige Durchführung auf einem realen Prüfhost gemäß den unten verlinkten Plattform-Nachweisregeln: Client gesamte Clientsuite; Serverfix gesamte schnelle Serversuite plus betroffene Clientintegration. Zugeordnete Build-/Hardware-/Crossrepo-Nachweise aus [Testplan](../../REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md) und [Checkpoints](../../REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md) mit tatsächlicher Herkunft prüfen. Umsetzungstexte oder vorhandene Belegdateien allein beweisen keinen Erfolg.

## Was du schreibst und abgibst

Neue Rnn-ABNAHME-Akte: Original-Prompt, 01_REPORT.md und EVIDENCE/INDEX.md mit eigenen Belegen. Report nennt reviewed_sha/tree, canonical_parent, server_sha, Requirementnachweise, eigene Tests und offene Findings. Findings: ID, Wirkung/Schwere, Repro mit expected/actual, Requirement, Owner und verlangter Nachweis.

ROOT_PASS ausschließlich bei erfüllten Pflichtkriterien; sonst CHANGES_REQUIRED oder konkrete fehlende Voraussetzung. PASS/FAIL/NOT_RUN/NOT_PROVEN/SKIPPED_EXPECTED unterscheiden. Matrix/Requirements und Paketindex ausschließlich mit tatsächlichen Abnahmebelegen/Status ergänzen, keine Kriterien ändern.

Im ausdrücklich erlaubten Scope nur diese Reviewunterlagen committieren und fast-forward auf den unveränderten **Paketbranch** pushen. Keine Produkt-, Test-, Kontrakt- oder fachlichen Planänderungen; keinen zweiten Review-PR. Bei fremdem Branchfortschritt stoppen und neuen Kandidaten melden. Ohne Gitfreigabe Report lokal liefern und offene Bereitstellung nennen.

Übergabe: Verdict, reviewed_sha/tree, Reportpfad, Finding-IDs, Reviewunterlagen-Commit und aktuelle PR-Spitze. PR-Zusammenfassung verlinkt den versionierten Report. Prüfkandidat und späterer Docs-Commit werden nicht als dieselbe geprüfte SHA ausgegeben.

## Wo deine Rolle endet

Ein ROOT_PASS ist technische Abnahme. Die Übernahme verlangt danach einen ausdrücklichen menschlichen Prompt, vorzugsweise an den Umsetzer. Kein Merge, kein Auto-Merge und kein Folgepaketstart durch dein Verdict. Falls der Auftraggeber dich später ausdrücklich mit der kurzen Abschlussaktion beauftragt, gilt der [Übernahmeablauf](references/UEBERNAHME.md); keine obligatorische dritte Prüfsession.

[Review-Auftragsvorlage](assets/PROMPT_ABNAHME.md), [Übernahmevorlage für den Abschlussagenten](assets/PROMPT_UEBERNAHME.md). Regelwerksdetails nur bei Bedarf: [Agentenregelwerk](../../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md).

## Beauftragte Ausnahmefälle

Bei Wiederaufnahme, alternativer Kandidatenlinie, Server-FIX oder letztem Abschluss nur den betreffenden Abschnitt der [Sonderfallreferenz](../GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md) lesen. Für Server-FIX erst tatsächliches Serverrepository, dortigen Kandidaten und Ziel Server-Distributed feststellen; die oben genannten Client-PR-/feat/client-v2-Prüfungen durch diese Serverzuordnung ersetzen. Serverrechte separat aus tatsächlichem Auftrag prüfen. Pflicht-Plattformfälle nach [Hardware-Nachweisregeln](../../REFERENZ/QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md); Eigen- und Fremddurchführung getrennt belegen.
