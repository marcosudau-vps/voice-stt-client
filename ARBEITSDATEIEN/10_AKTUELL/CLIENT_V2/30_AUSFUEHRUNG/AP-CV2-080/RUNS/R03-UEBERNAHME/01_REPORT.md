# AP-CV2-080 / R03-UEBERNAHME – vorgezogene Abschlussakte

**Stand:** 2026-10-13, vor dem angeordneten GitHub-Squash. **Gate:** unabhängiger [R02-ROOT_PASS](../R02-ABNAHME/01_REPORT.md) und tatsächlich erteilter [menschlicher Freigabeauftrag](00_PROMPT_ORIGINAL.md). Technischer Paketstatus bleibt **ROOT_PASS**, Workflow wird auf **READY_FOR_CANONICALIZATION** gesetzt. Noch keine behauptete Promotion oder vorzeitig gesetztes ACCEPTED.

## Verifizierte Ausgangsidentität

- [PR #10](https://github.com/marcosudau-vps/voice-stt-client/pull/10) ist `open`, `mergeable=true`, Base `feat/client-v2` = `canonical_parent 0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`; freigegebener Head `777c8e23f531e24532e78312365798bc83f2234c`, Baum `986d445f0afd83060c0cfd747067e6bed0c67b37`.
- Unabhängiger R02-PASS für `reviewed_sha=eafd918f456551af694ede4af472ed4515b9fdd6`, `reviewed_tree=960270c3f786433967aee7b16333be70f41427fe`, Server-SHA `ada13b011e1d3829f78e7f389e3b927795a2b3be`, **UI-01…10: 10/10 PASS**, keine Pflichtfindings.
- GitHub-Compare `eafd918f456551af694ede4af472ed4515b9fdd6..777c8e23f531e24532e78312365798bc83f2234c`: genau ein zusätzlicher Reviewdocs-Commit mit 18 ausschließlich administrativen Pfaden (Reviewakten, Status, Traceability-/Reviewbelege/Steuerungsübersichten); keine Produkt-, Test-, Kontrakt- oder fachlichen Spezifikationsänderungen.
- Vor diesem Freigabenachtrag [CI #38321633045](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38321633045) `completed/success` auf Head `777c8e23f531e24532e78312365798bc83f2234c` und Base `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`; Windows-Test-/Build- und Wheel-Smokes bestanden.
- Ausdrücklicher Originalprompt ist wörtlich versioniert und auf diese Identität bezogen. Kein konkurrierender kanonischer Commit auf `feat/client-v2` am Prüfzeitpunkt.

## Noch vor GitHub Squash erforderlich

Dieser R03-Akten-/Statuscommit enthält **ausschließlich** die tatsächliche Freigabe, R03-Report/Evidenz, Workflow `READY_FOR_CANONICALIZATION` sowie administrative Paket-/Steuerungsverweise. Er führt keine Produkt- oder Teständerung aus.

Unmittelbar vor dem Squash: finalen PR-Head, Base/Parent und Mergeability frisch prüfen; Diff `reviewed_sha..neuer Head` ausschließlich administrativ; neue CI `completed/success` für neuen Head und unveränderte Base samt verlangter Schritte; Originalprompt und vollständige R02-Akte im Baum. Bei Fehler kein Merge. Ein einziger **GitHub-Squash-and-merge** mit gebundenem erwarteten Head und AP-ID im Titel.

**Nach dem Merge außerhalb dieser vorgezogenen Akte verifizieren:** PR `merged`; von `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3` zum Aggregate exakt ein Commit; einziger Parent = `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`; Tree des Aggregate = Tree des wirklich letzten PR-Heads; etwaige Nachmerge-Pflichtchecks. Den tatsächlichen Aggregate-SHA erst in der Abschlussantwort und dann beim nächsten Paketstart protokollieren. Kein zweiter Aufräumcommit auf der kanonischen Linie. AP090 startet nicht automatisch.
