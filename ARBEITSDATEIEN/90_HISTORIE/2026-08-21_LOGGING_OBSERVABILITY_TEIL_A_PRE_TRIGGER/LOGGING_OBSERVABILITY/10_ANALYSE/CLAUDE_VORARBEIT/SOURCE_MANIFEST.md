---
id: OBS-000-SOURCE-MANIFEST
status: FINAL
authority: evidence
workstream: OBS
run: RUN-OBS-000-01_2026-08-15_CLAUDE
last_updated: 2026-08-15
---

# SOURCE_MANIFEST – Claude-Vorarbeit Logging

Dieses Manifest belegt, **woher** die in `10_ANALYSE/CLAUDE_VORARBEIT/`
liegenden Analysedateien stammen und dass sie **unverändert** übernommen
wurden.

---

## 1. Ergebnis der rekursiven Suche

Die im Auftrag `PRM-OBS-000-01` §4 genannten acht Dateien wurden rekursiv im
gesamten Workspace gesucht:

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude
```

Befund:

- Alle acht erwarteten Dateien lagen **bereits** unter
  `ARBEITSDATEIEN\AP_THEMA_LOGGING\10_ANALYSE\CLAUDE_VORARBEIT\`.
- Zusätzlich lag dort die neunte Datei `00_README_UND_ABSCHLUSSBEWERTUNG.md`,
  die zur selben Vorarbeit gehört und die Abschlussbewertung trägt.
- Der **ursprüngliche Ablageort** `ARBEITSDATEIEN/AP_THEMA_LOGGING/analyse_code_integration/`
  existiert als Verzeichnis nicht mehr; er ist als Archiv erhalten unter
  `90_ARCHIV/analyse_code_integration.zip`.
- Es wurde **keine Datei kopiert, verschoben, gelöscht oder überschrieben.**
  Die Kopieranweisung aus §4 des Auftrags war gegenstandslos, weil die Ablage
  bereits korrekt war.

## 2. Herkunft und Integrität

Vergleich der Arbeitskopien gegen das Archiv, Byte für Byte über SHA-256:

| Datei in `10_ANALYSE/CLAUDE_VORARBEIT/` | SHA-256 | Ursprungspfad | identisch? |
|---|---|---|---|
| `00_README_UND_ABSCHLUSSBEWERTUNG.md` | `a9c25a07594bcd0b04aadcadaf3ca1fa56b239435eb16651e8aa6bd56ebe0c6f` | `90_ARCHIV/analyse_code_integration.zip → analyse_code_integration/00_README_UND_ABSCHLUSSBEWERTUNG.md` | **ja** |
| `LOGGING_CODE_INTEGRATION_AUDIT.md` | `0c52db2a92a01c88ef472b33384f2ab1376a147dfe3ed77a708c837a6bd011d2` | ebenda | **ja** |
| `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md` | `a0e03198b598eb041c36db175fafc852cc6b47754a83fc67a2b718c606560bd0` | ebenda | **ja** |
| `LOGGING_CONCURRENCY_FAILURE_MODEL.md` | `7278ec0f166d9d2cdcb2dc8155bcf8442c60871c515ff50e0b8c58a0e2d6e437` | ebenda | **ja** |
| `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md` | `c83b3bc59ee21622d2725dfed0ad28b05f4cfdc5c2305629ade094b8ca0f5f7d` | ebenda | **ja** |
| `LOGGING_V1_IMPLEMENTATION_PLAN.md` | `17171a390f748f0b3d081248f1499d6aa05a21281bc7c5f726e98e1dc22addb1` | ebenda | **ja** |
| `LOGGING_OPEN_DECISIONS.md` | `081494685b96e8295d2b0fdcc9a996b5364854e2200c660ad99e884d8106e4cc` | ebenda | **ja** |
| `LOGGING_TEST_MATRIX.md` | `3d955eb60890f4f4fa33f1f90a17e83140521a178e26c5532147e8a93970e450` | ebenda | **ja** |
| `LOGGING_ADVERSARIAL_REVIEW.md` | `e5556e1933ee551c2e1f8aa5f58c45578a0e31ccf31048fc28367608d8339564` | ebenda | **ja** |

**Keine fehlende Pflichtdatei.** `LOGGING_TEST_MATRIX.md`, im Auftrag mit
„falls erzeugt" markiert, ist vorhanden.

## 3. Mehrfach vorhandene Dateien

Für die Grundlagen- und Planungsdateien existieren mehrere Ablagen. Alle
Varianten wurden über SHA-256 verglichen; **es gibt keine inhaltliche
Abweichung**, also auch keine Auswahlentscheidung zu treffen:

| Datei | SHA-256 | vorhanden unter |
|---|---|---|
| `LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md` | `2afba23a800865b3301e135fc3bd17cc75c0aad5f7095069837497848a8b1fdd` | `00_GRUNDLAGEN/`, `20_PLANUNG/`, `verlaufsdokumentation/AP_THEMA_LOGGING/`, `90_ARCHIV/AP_THEMA_LOGGING_OBS000_READY.zip` |
| `LOGGING_V1_ABGRENZUNG_ENTWURF.md` | `60083b2d8be13758e018a61f3161bb7f1d0b35256fe7dc009b3fa3d03bf856bb` | dieselben vier |
| `LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md` | `c168c4b230874fd26b16229cdfdfe7f61ec90dd9ad2f896223959c9d7051e6c2` | `00_GRUNDLAGEN/`, `90_ARCHIV/…OBS000_READY.zip` |
| `ErsterEntwurf_Logging.md` | `429362e0cdc699042f5f59620e7304f418310d117f2ca54a1b2a7e39b225b1a7` | `05_DRAFTS_UNGEPRUEFT/`, `verlaufsdokumentation/AP_THEMA_LOGGING/.unverbindlich_ungeprueft/`, `90_ARCHIV/…OBS000_READY.zip` |
| `LOGGING_GESAMTPLAN/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md` | `b3d6eeca02ada458072acd6d52c44780929fbb51630d17a29686dfd93af16748` | `20_PLANUNG/`, `05_DRAFTS_UNGEPRUEFT/`, beide Archiv-ZIPs |
| `LOGGING_GESAMTPLAN/01_WORKPACKAGE_INDEX.md` | `4c7f905fb4796e12ba13bd431576cc1ebfcd63585eb7092690e8a47be39384fd` | dieselben |
| `LOGGING_GESAMTPLAN/02_OBS000_FREEZE_CHECKLIST.md` | `e532316c55a6f76469f37fc67f02c0ea3807b063448fa49b29ed58c5b388042f` | dieselben |
| `LOGGING_GESAMTPLAN/03_TRACEABILITY_MATRIX.md` | `e399c8106d7240d13100df138393feca677e5f164e15d8e7bef07b9b4bd42b27` | dieselben |

**Hinweis zur Kopie unter `05_DRAFTS_UNGEPRUEFT/LOGGING_GESAMTPLAN/`.** Sie ist
byteidentisch mit der maßgeblichen Fassung unter `20_PLANUNG/`. Der Ordnername
`05_DRAFTS_UNGEPRUEFT` ist hier irreführend, weil `AGENTS.md` diesen Bereich als
„niemals automatisch normativ" führt. Maßgeblich ist ausschließlich
`20_PLANUNG/LOGGING_GESAMTPLAN/`. Die Doppelablage wird in diesem Run **nicht**
gelöscht (kein Auftrag dazu), aber im Run Report als aufzuräumender Punkt
benannt.

## 4. Autoritätseinstufung der Quellen für OBS-000

| Quelle | Rolle in diesem Freeze |
|---|---|
| `10_ANALYSE/CLAUDE_VORARBEIT/LOGGING_CODE_INTEGRATION_AUDIT.md` u. a. | **Ist-Evidence.** Aussagen über den heutigen Code. |
| `10_ANALYSE/CLAUDE_VORARBEIT/LOGGING_ADVERSARIAL_REVIEW.md` | **Red Team.** Korrigiert die übrigen Vorarbeitsdokumente; bei Widerspruch gewinnt das Review, sofern nicht dieser Freeze es ausdrücklich weiter korrigiert. |
| `00_GRUNDLAGEN/LOGGING_ZIELBILD_…_ENTWURF.md` | **Sollrichtung Endzustand**, Entwurf. |
| `00_GRUNDLAGEN/LOGGING_V1_ABGRENZUNG_ENTWURF.md` | **Sollrichtung V1**, Entwurf. |
| `00_GRUNDLAGEN/LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md` | Ist-Evidence zur Triggerarchitektur, insbesondere §1.2 (`activationId` unzuverlässig) und §6 (Beobachtungspunkte). |
| `05_DRAFTS_UNGEPRUEFT/ErsterEntwurf_Logging.md` | **Unverbindlich.** Gelesen, keine Aussage daraus übernommen, die eine neuere Analyse überschreibt. |
| realer Produktcode `voice-stt-client` | **entscheidet** über jede Ist-Aussage. |
