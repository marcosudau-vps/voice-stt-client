# Wiedereinstieg – Einheitliche Triggerarchitektur

**Stand:** 29. August 2026, 09:09:02 +02:00, nach Root-PASS und kanonischem
Abschluss von `AP-SRV-060`

Diese Datei ist die kompakte operative Übergabe für einen neuen Agenten ohne
Chatkontext. Bei einem Widerspruch gelten in dieser Reihenfolge der aktuelle
Git-/Teststand, `STATUS.md` und `AUSFUEHRUNGSSTATUS.md`, der technische
Contract und die konsolidierten fachlichen Entscheidungen. `IDEEN/` und der
Namespace-Unterordner sind keine freigegebenen Quellen.

## 1. Repositories und Branches

| Rolle | Workspace | Branch | letzter freigegebener Produkt-AP-SHA |
|---|---|---|---|
| Server | `P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\einheitliche-triggerarchitektur` | `feat/einheitliche-triggerarchitektur` | `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8` (`AP-SRV-060`, canonical) |
| Desktop-Client und Koordination | `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur` | `feat/einheitliche-triggerarchitektur` | `042fcd203c873d6f84a270413c47bc5da1fbf1ed` (`AP-CLI-000`) |

Beide Branches verfolgen
`github/feat/einheitliche-triggerarchitektur` unter der Organisation
`marcosudau-vps`. Vor jeder Arbeit sind Branch, `git status --short --branch`
und der Remote-HEAD zu prüfen. Koordinationsdokumente können im Clientbranch
nach dem letzten Client-Produkt-AP liegen und sind kein zusätzlicher
Client-Produktumbau.

Die Distributed-/Review-Branches
(`feat/einheitliche-triggerarchitektur-distributed`,
`review/AP-SRV-030/run-01`, `review/AP-SRV-040/run-01`,
`review/AP-SRV-050/run-01`, `work/AP-SRV-060/C3`) sind
**Execution-Provenienz** und **keine** neue kanonische Basis. Die zentrale
Paketkette liegt ausschließlich auf `feat/einheitliche-triggerarchitektur`.

## 2. Lesereihenfolge für einen Neustart

1. repositorylokales `AGENTS.md` vollständig;
2. `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md` im Clientworkspace;
3. diese Datei;
4. `../STATUS.md` und `AUSFUEHRUNGSSTATUS.md`;
5. für Planung: `../PLANUNG/README.md`, danach die dort gerouteten Quellen;
6. für Umsetzung: den datierten Originalprompt und Plan der aktiven
   repositorylokalen AP-Akte vollständig;
7. nur die im Prompt genannten Contractabschnitte, Produktmodule und Tests.

Nicht aus alten Chatnachrichten, `IDEEN/`, Namespace-Dateien,
`90_HISTORIE/` oder historischen Vorplanungen implementieren.

## 3. Abgenommener Sachstand

- `AP-SRV-000` PASS:
  `71a35e074eb90d75f8f91f5ed7cb46accd4b6498`;
- `AP-CLI-000` PASS:
  `042fcd203c873d6f84a270413c47bc5da1fbf1ed`;
- `AP-SRV-010` PASS:
  `3262079c62c58677cfd6506cd09d020b5b27ef44`;
- `AP-SRV-020` PASS:
  `8535ee79bb2d898d9897e91b57d6a735c479edf0`;
- `AP-SRV-030` PASS / canonical:
  `b220dd03a594d2b9f8cad65fd279046be36864cc`;
- `AP-SRV-040` PASS / canonical:
  `c0806e5bc5d503580070f2dacc88831d51447938`;
- `AP-SRV-050` PASS / canonical:
  `c901cda3f2c19eeb78c468524161728498b6e27e`;
- `AP-SRV-060` PASS / canonical:
  `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8`.

Abgenommene Kette:

```text
SRV000
SRV010
SRV020
SRV030 canonical
SRV040 canonical
SRV050 canonical
SRV060 canonical
```

`AP-SRV-030` wurde aus dem bereits abgenommenen Execution-Stand
(`325e55c…`) als archivvollständiger kanonischer Commit geschlossen;
`AP-SRV-040` aus dem Root-geprüften C3 (`6f73a4e…`) als genau ein
kanonischer Commit. Beide liegen linear auf
`feat/einheitliche-triggerarchitektur` direkt auf der SRV-000..020-Kette.

`AP-SRV-050` wurde aus dem Root-geprüften C3
(`18b65216433329456946afd3c41d8df6bbd07d44`, Tree `b0dec32d…`) ebenfalls als
genau ein kanonischer Commit auf `c0806e5…` geschlossen.

`AP-SRV-060` wurde aus dem finalen Root-Source-Stand
(`2b08e379a36590c99e48e59c81a39418395d9742`, Tree `de6fe364545b508a47a87ead67a01c5732477e71`)
als genau ein kanonischer Commit auf `c901cda…` geschlossen (`c82923f…`, Tree `de6fe364…`).
Die Execution-Provenienz liegt auf `work/AP-SRV-060/C3` (C1 `548057e…`,
C2 `5e429d6…`, C3 `d681afa…`, Asset-Finalisierung `abf8e62…`, Final Repair `2b08e37…`).
AP-SRV-060 liefert den versionierten Buildkatalog (`VoiceSTT/assets/wakeword_models/`
mit Dual-Backend ONNX und TFLite), `GET /api/v2/wake-words` (`SET-13b`),
`POST /api/v2/wake-words/refresh`, atomare Sessionadmission, selected-only
Modellinitialisierung, `WakeHitTracker` mit Exactly-once `wakeword.detected`-Eventing,
Single-Backend-je-Engine-Policy sowie die detection-verankerte Audiogrenze
(operationaler Nullpunkt an Trailing Edge des Wake-Hits). Vollsuite:
`1180 passed, 14 skipped, 762 subtests, 0 failed`. Empirische Kalibrierung
(`WW-18`, `WW-19`) bleibt ehrlich als `EVIDENCE_BLOCKED / calibration pending`
ausgewiesen.

AP-SRV-010 liefert genau einen serverseitigen Vordergrundslot mit
`idle`, `waiting_first_speech`, `segment_active`, `followup_wait` und
`closing_input`, First-Trigger-wins, stabile Activation-ID/-Sequenz,
gelatchte Quelle, unveränderlichen Settings-Snapshot sowie eine
generationengebundene Gate-/Recorder-Barriere. `finalizing` blockiert den
Vordergrund nicht mehr.

AP-SRV-020 ergänzt unveränderliche Segment-/Finaljobkontexte,
Exactly-once-Segmentterminale, sessionweiten Reorder-Drain, vollständige
Faultterminalisierung und Activationterminale nach Input-Close plus
vollständigem Drain.

Die vollständigen AP-Nachweise liegen serverseitig unter
`docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-000/` bis
`AP-SRV-060/`, clientseitig unter `ARBEITSPAKETE/AP-CLI-000/`.

## 4. Nächstes Paket und harte Grenzen

`AP-SRV-070` ist READY und startet exakt auf dem kanonischen Server-SHA

```text
c82923fc6ce889b4dfbbde1f9877b8b76481a1e8  (AP-SRV-060 canonical)
Tree de6fe364545b508a47a87ead67a01c5732477e71
```

Sein Umfang ist: Legacyabbau und Protokollgrenze.

Nicht vorwegnehmen: jegliche Clientproduktänderung.

`AP-CLI-010` ist dependency-seitig entblockt (technische Dependency
AP-SRV-040 erfüllt), wird aber **bewusst deferred**: erst nach Abschluss der
Serverlinie `AP-SRV-060 → AP-SRV-070` beginnt die Clientlinie.
Deshalb läuft aktuell keine parallele Clientimplementierung.

## 5. Verbindliche Quellen

- Fachliche Entscheidungen:
  `../PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`;
- Zielbild: `../PLANUNG/ZIELBILD.md`;
- technischer Contract: `../PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md`;
- finaler Paketschnitt: `../PLANUNG/IMPLEMENTIERUNGSPLAN.md`;
- Wirevertrag: `../PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`;
- Anforderungen/AP-Zuordnung: `TRACEABILITY.md`;
- bekannte Abweichungen: `FUNDE.md`;
- Ausführungs- und Abnahmeprozess:
  `../PLANUNG/AUSFUEHRUNGS_WORKFLOW.md`.

Historische Archive belegen nur frühere Zustände und überschreiben diese
Quellen nicht. Das gilt ausdrücklich auch für die am 2026-08-27 gesicherte
Server-Prep-Provenienz unter
`ARBEITSDATEIEN/90_HISTORIE/2026-08-25_TRIGGERARCHITEKTUR_SERVER_PREP/`:
byteidentische Voranalyse-/Planungsstände vom 2026-08-25 zu AP-SRV-040 bis
AP-SRV-070, **nicht normativ**, keine AP-Abnahme, kein kanonischer
Produktstand. Nicht daraus implementieren.

## 6. Tests und Gateprozess

Server:

```powershell
python -m pytest
```

Beim bekannten Windows-Rechteproblem des globalen Pytest-Tempordners werden
`TEMP` und `TMP` auf das ignorierte repositorylokale Verzeichnis `.tmp`
gesetzt. AP-SRV-020 bestand unabhängig `108` fokussierte Tests plus `9`
Subtests und die Vollsuite mit `507 passed, 13 skipped`. Die Root-Abnahme
steht unter `docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-020/` im
Serverworkspace.

Client:

```powershell
P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe -m pytest -q
```

Für jedes AP gilt:

1. datierte repositorylokale Akte vor Implementierungsbeginn;
2. unveränderter Originalprompt mit Repository, Branch, Start-SHA, Scope,
   Dependencies, Tests, Dokumentationszielen und Rückgabeformat;
3. Agent aktualisiert Produktdokumentation und erstellt genau einen lokalen
   AP-Commit, aber pusht nicht;
4. Root prüft vollständigen Range, Tests, Dokumentation und Working Tree;
5. Befunde gehen an denselben Agenten und werden in denselben Commit
   amendiert;
6. Root-Abnahme wird in denselben Commit amendiert; Push erst nach PASS;
7. danach zentrale Status-, Verlauf-, Traceability- und Dependencydaten
   aktualisieren.

Der aktive GitHub-Account für Pushes ist `marcosudau-vps`. Zugangsdaten oder
Token dürfen niemals in Akten, Logs oder Testausgaben übernommen werden.
