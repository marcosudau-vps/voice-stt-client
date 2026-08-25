# Ausführungsstatus – Einheitliche Triggerarchitektur

**Stand:** 2026-08-25 03:28:14 +02:00

Diese Datei führt ausschließlich Ausführungsgates und immutable Commit-SHAs.
Fachliche Anforderungen und Planungsstatus bleiben in `TRACEABILITY.md`.

## Abgenommene Arbeitspakete

| AP | Repository | Status | Start-SHA | gepushter PASS-SHA | Dependency-Freigabe |
|---|---|---|---|---|---|
| AP-SRV-000 | `voice-stt-server` | PASS | `13c162950b944dc715fdd81983a7465f8eb0fd79` | `71a35e074eb90d75f8f91f5ed7cb46accd4b6498` | AP-SRV-010 freigegeben |
| AP-CLI-000 | `voice-stt-client` | PASS | `db102fdc6dd70e4de798a363608d1e7412533dd7` | `042fcd203c873d6f84a270413c47bc5da1fbf1ed` | Clientbaseline erfüllt; AP-CLI-010 wartet zusätzlich auf AP-SRV-040 |

## Nächste Gates

| AP | Status | Erfüllte Dependencies | Noch erforderlich |
|---|---|---|---|
| AP-SRV-010 | READY | AP-SRV-000 | – |
| AP-SRV-020 | BLOCKED | – | AP-SRV-010 |
| AP-SRV-030 | BLOCKED | – | AP-SRV-010 und AP-SRV-020 |
| AP-SRV-040 | BLOCKED | – | AP-SRV-010 bis AP-SRV-030 |
| AP-CLI-010 | BLOCKED | AP-CLI-000 | AP-SRV-040 |

## Gate-Regel

Ein AP gilt erst als freigegeben, wenn die Koordination Diff, Dokumentation,
fokussierte Tests, vollständige Repositorysuite, sauberen Working Tree und
genau einen AP-Commit geprüft, die Root-Abnahme in diesen Commit amendiert und
den exakten SHA auf den zugehörigen GitHub-Feature-Branch gepusht hat.
