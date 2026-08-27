# Ausführungsstatus – Einheitliche Triggerarchitektur

**Stand:** 2026-08-27 03:02:19 +02:00

Diese Datei führt ausschließlich Ausführungsgates und immutable Commit-SHAs.
Fachliche Anforderungen und Planungsstatus bleiben in `TRACEABILITY.md`.

## Abgenommene Arbeitspakete

| AP | Repository | Status | Start-SHA | gepushter PASS-SHA | Dependency-Freigabe |
|---|---|---|---|---|---|
| AP-SRV-000 | `voice-stt-server` | PASS | `13c162950b944dc715fdd81983a7465f8eb0fd79` | `71a35e074eb90d75f8f91f5ed7cb46accd4b6498` | AP-SRV-010 freigegeben |
| AP-SRV-010 | `voice-stt-server` | PASS | `71a35e074eb90d75f8f91f5ed7cb46accd4b6498` | `3262079c62c58677cfd6506cd09d020b5b27ef44` | AP-SRV-020 freigegeben |
| AP-SRV-020 | `voice-stt-server` | PASS | `3262079c62c58677cfd6506cd09d020b5b27ef44` | `8535ee79bb2d898d9897e91b57d6a735c479edf0` | AP-SRV-030 freigegeben |
| AP-SRV-030 | `voice-stt-server` | PASS | `8535ee79bb2d898d9897e91b57d6a735c479edf0` | `325e55c186713069b25208871da4fef16470f85a` | AP-SRV-040 freigegeben; PASS-Tree `ec5b6e0849bb7a0949ae5da05d168b8c19a4456e` |
| AP-CLI-000 | `voice-stt-client` | PASS | `db102fdc6dd70e4de798a363608d1e7412533dd7` | `042fcd203c873d6f84a270413c47bc5da1fbf1ed` | Clientbaseline erfüllt; AP-CLI-010 wartet zusätzlich auf AP-SRV-040 |

## Nächste Gates

| AP | Status | Erfüllte Dependencies | Noch erforderlich |
|---|---|---|---|
| AP-SRV-040 | READY | AP-SRV-010 bis AP-SRV-030 | auf exakt `325e55c186713069b25208871da4fef16470f85a` / Tree `ec5b6e0849bb7a0949ae5da05d168b8c19a4456e` starten; Paketakte und kanonischen Worktree anlegen |
| AP-CLI-010 | BLOCKED | AP-CLI-000 | AP-SRV-040 |

## AP-SRV-030 Root-Evidence

- Finaler kanonischer Serverbranch: `feat/einheitliche-triggerarchitektur-distributed`
- PASS-SHA: `325e55c186713069b25208871da4fef16470f85a`
- PASS-Tree: `ec5b6e0849bb7a0949ae5da05d168b8c19a4456e`
- Parent / AP-SRV-020: `8535ee79bb2d898d9897e91b57d6a735c479edf0`
- Der finale Commit ist genau ein Commit nach AP-SRV-020.
- Der Produkt-/Test-/Dokumentationsstand vor Einfügung der Root-Abnahme wurde als Tree `a61584db3397f388e3039f69082d5befce025b68` vollständig in GitHub Actions Run `33028252444` auf Windows/Python 3.12 validiert.
- C3-Zielregressionen: 2 PASS.
- AP-SRV-030-Fokussuite: 197 PASS, 82 Subtests PASS.
- AP-SRV-020-Regression: 53 PASS, 3 Subtests PASS.
- Vollständige Unit-Suite: 615 PASS, 13 skipped, 167 Subtests PASS.
- Race-/Recovery-Suite: 20/20 Läufe PASS; je Lauf 21 Tests + 4 Subtests.
- Root-Abnahme liegt im finalen Servercommit unter `docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-030/ABNAHME.md`.

## Gate-Regel

Ein AP gilt erst als freigegeben, wenn die Koordination Diff, Dokumentation,
fokussierte Tests, vollständige Repositorysuite, sauberen Working Tree und
genau einen AP-Commit geprüft, die Root-Abnahme in diesen Commit amendiert und
den exakten SHA auf den zugehörigen GitHub-Feature-Branch gepusht hat.
