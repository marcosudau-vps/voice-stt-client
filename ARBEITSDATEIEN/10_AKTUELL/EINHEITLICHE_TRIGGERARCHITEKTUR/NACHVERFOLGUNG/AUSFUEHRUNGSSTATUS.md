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
| AP-SRV-030 | `voice-stt-server` | PASS | `8535ee79bb2d898d9897e91b57d6a735c479edf0` | Execution-/Root-PASS-Source `325e55c186713069b25208871da4fef16470f85a`; Canonical Archive-Complete `b220dd03a594d2b9f8cad65fd279046be36864cc` | AP-SRV-040 freigegeben; Parent `8535ee7…` |
| AP-SRV-040 | `voice-stt-server` | PASS | Execution Source `325e55c186713069b25208871da4fef16470f85a`; Root-reviewed C3 `6f73a4e347be51d02005e81a0c6be546f036deef` | Canonical `c0806e5bc5d503580070f2dacc88831d51447938` | AP-SRV-050 freigegeben; Parent `b220dd03a594d2b9f8cad65fd279046be36864cc` |
| AP-CLI-000 | `voice-stt-client` | PASS | `db102fdc6dd70e4de798a363608d1e7412533dd7` | `042fcd203c873d6f84a270413c47bc5da1fbf1ed` | Clientbaseline erfüllt; AP-CLI-010 dependency-seitig entblockt, Ausführung bewusst deferred |

## AP-SRV-030 – Execution-/Root-PASS Source

```text
Execution-/Root-PASS source:
325e55c186713069b25208871da4fef16470f85a
Tree ec5b6e0849bb7a0949ae5da05d168b8c19a4456e

Canonical Archive-Complete PASS:
b220dd03a594d2b9f8cad65fd279046be36864cc
Tree 61c65f59b1778085affada90b66411e27ec1c004
Parent 8535ee79bb2d898d9897e91b57d6a735c479edf0
```

`325e55c…` bleibt als Execution-/Root-PASS-Provenienz erhalten; der
kanonische Commit `b220dd0…` trägt dieselbe Produkt-/Test-/Dokustand plus
vollständigem Archiv.

## AP-SRV-040 – Root-PASS / Canonical

```text
Start execution source: 325e55c186713069b25208871da4fef16470f85a
Root-reviewed C3:       6f73a4e347be51d02005e81a0c6be546f036deef
C3 tree:                6d36c2639a199c5bdd10a2c8dc1899d8261caee6
Canonical PASS:         c0806e5bc5d503580070f2dacc88831d51447938
Canonical tree:         e9a1a93aecf433941db91827393bc51afef4ebff
Parent:                 b220dd03a594d2b9f8cad65fd279046be36864cc
Dependency:             AP-SRV-050 freigegeben
```

## Nächste Gates

| AP | Status | Erfüllte Dependencies | Noch erforderlich |
|---|---|---|---|
| AP-SRV-050 | READY | AP-SRV-010 bis AP-SRV-040 | auf exakt `c0806e5bc5d503580070f2dacc88831d51447938` / Tree `e9a1a93aecf433941db91827393bc51afef4ebff` starten |
| AP-CLI-010 | DEFERRED BY EXECUTION SEQUENCE | AP-CLI-000; technische Dependency AP-SRV-040 erfüllt | bewusst deferred bis Abschluss Serverlinie AP-SRV-050 → AP-SRV-060 → AP-SRV-070 |

## AP-SRV-030 Evidence-Referenz

- Execution-/Root-PASS-Provenienz: siehe oben (Source `325e55c…`, Tree `ec5b6e…`).
- Der Produkt-/Test-/Dokumentationsstand vor Einfügung der Root-Abnahme wurde als Tree `a61584db3397f388e3039f69082d5befce025b68` vollständig in GitHub Actions Run `33028252444` auf Windows/Python 3.12 validiert.
- C3-Zielregressionen: 2 PASS.
- AP-SRV-030-Fokussuite: 197 PASS, 82 Subtests PASS.
- AP-SRV-020-Regression: 53 PASS, 3 Subtests PASS.
- Vollständige Unit-Suite: 615 PASS, 13 skipped, 167 Subtests PASS.
- Race-/Recovery-Suite: 20/20 Läufe PASS; je Lauf 21 Tests + 4 Subtests.
- Kanonische Akte: `docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-030/` (inkl. `ABNAHME.md` und archivierter Originalprompts).

## Gate-Regel

Ein AP gilt erst als freigegeben, wenn die Koordination Diff, Dokumentation,
fokussierte Tests, vollständige Repositorysuite, sauberen Working Tree und
genau einen AP-Commit geprüft, die Root-Abnahme in diesen Commit amendiert und
den exakten SHA auf den zugehörigen GitHub-Feature-Branch gepusht hat.
