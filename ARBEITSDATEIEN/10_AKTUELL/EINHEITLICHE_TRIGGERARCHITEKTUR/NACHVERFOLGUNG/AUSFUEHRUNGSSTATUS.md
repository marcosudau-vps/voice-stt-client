# Ausführungsstatus – Einheitliche Triggerarchitektur

**Stand:** 2026-08-29 09:09:02 +02:00

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
| AP-SRV-050 | `voice-stt-server` | PASS | Canonical Base `c0806e5bc5d503580070f2dacc88831d51447938`; Execution provenance C1 `489ac23a192b2a64abbcdb6779ed132f159e4518` / C2 `536ff67cda872b1449f88c5d99e8d8c3017139f4` / C3 `18b65216433329456946afd3c41d8df6bbd07d44` | Canonical `c901cda3f2c19eeb78c468524161728498b6e27e` | AP-SRV-060 freigegeben; Parent `c0806e5bc5d503580070f2dacc88831d51447938` |
| AP-SRV-060 | `voice-stt-server` | PASS | Canonical Base `c901cda3f2c19eeb78c468524161728498b6e27e`; Execution provenance C1 `548057e…` / C2 `5e429d6…` / C3 `d681afa…` / Asset-Final `abf8e62…` / Root Source `2b08e37…` | Canonical `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8` | AP-SRV-070 freigegeben; Parent `c901cda3f2c19eeb78c468524161728498b6e27e` |
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

## AP-SRV-050 – Root PASS / Canonical

```text
Start (canonical base): c0806e5bc5d503580070f2dacc88831d51447938
Start tree:             e9a1a93aecf433941db91827393bc51afef4ebff

Execution provenance:
C1  489ac23a192b2a64abbcdb6779ed132f159e4518
    Tree 17eeb88254809c535404c84872111241470f1010
C2  536ff67cda872b1449f88c5d99e8d8c3017139f4
    Tree 9ff02381fef0b6c8dd6e01482d4633e21ef56be4
C3  18b65216433329456946afd3c41d8df6bbd07d44   (Root-PASS Source)
    Tree b0dec32ddde90052956165c249b313478c267773

Canonical PASS:         c901cda3f2c19eeb78c468524161728498b6e27e
Canonical tree:         f81144a26f93fb3bc553ab5110d07197a473aa46
Parent:                 c0806e5bc5d503580070f2dacc88831d51447938
Commit count AP040..AP050: 1
Dependency:             AP-SRV-060 freigegeben
```

Root-Findings `F1`–`F6` sind `PASS`. Produkt-, Test- und dauerhafter
Dokustand des kanonischen Commits sind identisch zum Root-geprüften C3
(Tree `b0dec32d…`); die einzigen Unterschiede sind die drei Root-Close-
Dokumente der AP050-Akte (`ABNAHME.md`, `2026-08-27_README.md`,
`2026-08-27_AP-SRV-050_UMSETZUNGSVERGLEICH.md`).

Testevidenz (aus C3 übernommen, Root-geprüft): Settings `120 passed`;
Protocol v2 `205 passed / 1 skipped / 281 subtests`; Activation/Timer
`218 passed / 82 subtests`; Vollsuite `899 passed / 14 skipped / 448
subtests`; C3-Races Snapshot/Patch `20/20` und settings.changed/Domain
ordering `20/20`.

`git diff --check` meldet ausschließlich die bekannten Markdown-Hardbreak-
Trailing-Spaces der byteidentisch archivierten Promptdatei
`AP-SRV-050/runs/03_ROOT_CORRECTION/2026-08-27_PROMPT.md`; ohne diese Datei
ist der Lauf sauber. Die Datei wurde bewusst nicht verändert, damit der
Byte-/SHA-Nachweis erhalten bleibt.

Root-Disposition: `GET /api/v2/wake-words` gehört `AP-SRV-060`; `SET-13` ist
in `SET-13a` (SRV-050) und `SET-13b` (SRV-060) aufgeteilt.

## AP-SRV-060 – Root PASS / Canonical

```text
Start (canonical base): c901cda3f2c19eeb78c468524161728498b6e27e
Start tree:             f81144a26f93fb3bc553ab5110d07197a473aa46

Execution provenance:
C1             548057e96a8a722c84d9a43451577a4415bcd7b1
               Tree 8751ef47ab17a6c5a1359d75f08fcd18358c5003
C2             5e429d6227d6a4660b79c432aa934318e293ecfd
               Tree ac278c4649e64793bdf938a0a41e484209d882ff
C3             d681afa4580bc8d769777b4fe45a36e3cfc6987a
               Tree 7610f208fefdd890556e0f9a557b377095c5ad4c
Asset-Final    abf8e6207d0019018f55ce4dcf57f81328c4cb5a
               Tree 0276f5752ac918b3e28e15e14d7f11c91182f248
Final Repair   2b08e379a36590c99e48e59c81a39418395d9742   (Root-PASS Source)
               Tree de6fe364545b508a47a87ead67a01c5732477e71

Canonical PASS:         c82923fc6ce889b4dfbbde1f9877b8b76481a1e8
Canonical tree:         de6fe364545b508a47a87ead67a01c5732477e71
Parent:                 c901cda3f2c19eeb78c468524161728498b6e27e
Commit count AP050..AP060: 1
Tree equals ROOT source: JA
Dependency:             AP-SRV-070 freigegeben
```

Umfang: versionierter Buildkatalog (`VoiceSTT/assets/wakeword_models/` mit
ONNX- und TFLite-Dual-Backend-Artefakten), `GET /api/v2/wake-words`
(`SET-13b`), `POST /api/v2/wake-words/refresh`, atomare Sessionadmission,
selected-only Modellinitialisierung, `WakeHitTracker` mit Exactly-once
`wakeword.detected`-Eventing, Single-Backend-je-Engine-Policy sowie die
detection-verankerte Audiogrenze (operationaler Nullpunkt an Trailing Edge des
Wake-Hits).

Testevidenz: Vollsuite `1180 passed, 14 skipped, 762 subtests, 0 failed`.
Empirische Wake-Audio-Kalibrierung (`WW-18`, `WW-19`) bleibt separat als
`EVIDENCE_BLOCKED / calibration pending` ausgewiesen (reale positive
Wake-Word-Aufnahmen existieren im lokalen Umfeld nachweislich nicht). Das
blockiert AP-SRV-060 ROOT PASS nicht.

## Nächste Gates

| AP | Status | Erfüllte Dependencies | Noch erforderlich |
|---|---|---|---|
| AP-SRV-070 | READY | AP-SRV-010 bis AP-SRV-060 | auf exakt `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8` / Tree `de6fe364545b508a47a87ead67a01c5732477e71` starten; Legacyabbau und Protokollgrenze |
| AP-CLI-010 | DEFERRED BY EXECUTION SEQUENCE | AP-CLI-000; technische Dependency AP-SRV-040 erfüllt | bewusst deferred bis Abschluss Serverlinie AP-SRV-060 → AP-SRV-070 |

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
