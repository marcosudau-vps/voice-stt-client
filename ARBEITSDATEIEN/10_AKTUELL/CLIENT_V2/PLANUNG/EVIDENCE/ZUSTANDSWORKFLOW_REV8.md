> Historischer Nachweis der damaligen Vorbereitung. Keine aktuelle Branch-/Startanweisung. Maßgeblich sind [aktueller Prüfbericht](PRUEFBERICHT.md) und [Branchführung](../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

# Zustandsermittlung Revision 8 – Auftrag und Nachweise

Stand 2026-10-11. Dokument-/Skilländerung auf work/client-v2/rollenworkflow, Basis b0525e6. Kein Produktcode, kein AP begonnen/abgenommen, kein Commit/Push/PR/Merge. Revision 7 und ihre damaligen Prüfergebnisse bleiben als frühere Dokumentprüfung erhalten; diese Revision ergänzt die gemeinsame Auswahl der nächsten Aktion.

## Tatsächliche Nutzeraufträge

> Kannst du das bitte dann noch so festschreiben? Also dass es eben diese festgelegten Zustände gibt, die erkannt werden und somit auch immer die richtigen Stände eingetragen sind, die dann eben auch erkannt werden, sodass halt ein neuer Agent theoretisch gar nichts von mir braucht, sondern einfach nur wissen muss: mach den nächsten Schritt. Und anhand der dokumentierten Stände ist klar, wo er einsteigen muss.

> Und selbst wenn ein Agent jetzt ein Review macht und mir empfiehlt, das zu übernehmen, kann ich theoretisch nochmal einen beauftragen, der ein zweites unabhängiges Review trotzdem nochmal macht?

## Ergebnis und Validierung

[Gemeinsamer Skill](../SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md) führt zur [Zustandsreferenz](../SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md), zur passenden Rolle und deren Checkliste. [WORKFLOW_STATUS.json](../../WORKFLOW_STATUS.json) ist die initiale strukturierte Übersicht, nur Planungsbereitschaft für AP-CV2-000. Die Rollen müssen Status-/Akten-/Belegverweise vor Abgabe pflegen. Offene Paketlinien haben Vorrang; kanonische Aufnahme wird aus Git/PR erkannt, ohne zusätzlichen Statuscommit. Menschliche Gitfreigaben werden nicht aus der Statusdatei erfunden.

Ein zusätzliches ausdrücklich beauftragtes unabhängiges Review erhält eine neue Akte. Frühere Berichte und offene Pflichtfindings bleiben berücksichtigt; neuer Pflichtbefund blockiert Übernahme trotz älterem PASS. Keine zusätzliche Pflichtsession für jedes AP eingeführt.

[Prüfergebnis](workflow-next-step-validation.json): Alle drei Skills mit skill-creator quick_validate bestanden. Verweise/Erreichbarkeit, JSON/Initialzustand, unveränderte Kontrakte/Vektoren/216 Requirements/Paketumfang und Git-Dokumentenscope bestanden; git diff --check grün. Kein Produkt-PASS oder ausgeführter Agenten-/GitHub-Automat behauptet: dies sind verbindliche Agentenanweisungen, kein implementierter Hintergrunddienst.

## Prüfung der vorgesehenen Situationen

| Situation | Festgelegte Entscheidung |
| --- | --- |
| Nur Startcommit vorhanden | AP-CV2-000 nach einmaliger Bereitstellung der Unterlagen starten |
| Feature unverändert, Paket-PR REVIEW_READY | Review des offenen Pakets statt erneuter Umsetzung |
| Maßgeblicher Review verlangt Änderungen | Korrektur der dokumentierten Findings |
| Fachlich veränderter Korrekturkandidat eingereicht | Frischer unabhängiger Review, älteren PASS nicht übernehmen |
| ROOT_PASS, keine menschliche Übernahmefreigabe | Warten und PASS melden |
| Passende tatsächliche menschliche Freigabe | Genau eine überprüfte kanonische Übernahme |
| Aggregatecommit vorhanden, Status noch vor Merge | Abschluss aus Provenienz ableiten, im nächsten Paket nachführen |
| Zweitreview trotz bereits vorhandenem PASS ausdrücklich gewünscht | Frisches Zusatzreview, eigene Akte, keine Übernahme währenddessen |
| Zusatzreview mit Pflichtbefund | CHANGES_REQUIRED, älteren PASS nicht als ausreichend behandeln |
| Neuer PASS, alter Pflichtbefund noch ungeklärt | Keine Übernahme; Befund konkret prüfen/schließen |
| Noch aktive fremde Session | Keine parallele Übernahme ihrer Arbeit |
| Mehrere konkurrierende Kandidaten/fehlende Belege | Konkreten Konflikt melden, keine zufällige Rollen-/Standwahl |

Diese Tabelle dokumentiert die Prüfung der Regeln anhand von Situationen, keine tatsächlich ausgeführten Agentensessions. Änderungen werden dauerhaft als vollständiger Dateisatz gesichert und vor AP-CV2-000 in dessen Paketbranch aufgenommen; feat/client-v2 bleibt bis zum freigegebenen Paketaggregat unverändert.
