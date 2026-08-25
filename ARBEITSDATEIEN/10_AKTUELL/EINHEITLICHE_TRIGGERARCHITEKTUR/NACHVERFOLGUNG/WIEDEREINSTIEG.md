# Wiedereinstieg – Einheitliche Triggerarchitektur

**Stand:** 25. August 2026, nach Root-PASS von `AP-SRV-010`

Diese Datei ist die kompakte operative Übergabe für einen neuen Agenten ohne
Chatkontext. Bei einem Widerspruch gelten in dieser Reihenfolge der aktuelle
Git-/Teststand, `STATUS.md` und `AUSFUEHRUNGSSTATUS.md`, der technische
Contract und die konsolidierten fachlichen Entscheidungen. `IDEEN/` und der
Namespace-Unterordner sind keine freigegebenen Quellen.

## 1. Repositories und Branches

| Rolle | Workspace | Branch | letzter freigegebener Produkt-AP-SHA |
|---|---|---|---|
| Server | `P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\einheitliche-triggerarchitektur` | `feat/einheitliche-triggerarchitektur` | `3262079c62c58677cfd6506cd09d020b5b27ef44` (`AP-SRV-010`) |
| Desktop-Client und Koordination | `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur` | `feat/einheitliche-triggerarchitektur` | `042fcd203c873d6f84a270413c47bc5da1fbf1ed` (`AP-CLI-000`) |

Beide Branches verfolgen
`github/feat/einheitliche-triggerarchitektur` unter der Organisation
`marcosudau-vps`. Vor jeder Arbeit sind Branch, `git status --short --branch`
und der Remote-HEAD zu prüfen. Koordinationsdokumente können im Clientbranch
nach dem letzten Client-Produkt-AP liegen und sind kein zusätzlicher
Client-Produktumbau.

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
  `3262079c62c58677cfd6506cd09d020b5b27ef44`.

AP-SRV-010 liefert genau einen serverseitigen Vordergrundslot mit
`idle`, `waiting_first_speech`, `segment_active`, `followup_wait` und
`closing_input`, First-Trigger-wins, stabile Activation-ID/-Sequenz,
gelatchte Quelle, unveränderlichen Settings-Snapshot sowie eine
generationengebundene Gate-/Recorder-Barriere. `finalizing` blockiert den
Vordergrund nicht mehr.

Die vollständigen AP-Nachweise liegen serverseitig unter
`docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-000/` und
`AP-SRV-010/`, clientseitig unter
`ARBEITSPAKETE/AP-CLI-000/`.

## 4. Nächstes Paket und harte Grenzen

`AP-SRV-020` ist READY und startet exakt auf dem Server-SHA
`3262079c62c58677cfd6506cd09d020b5b27ef44`.

Sein Umfang ist:

- unveränderlicher Finaljobkontext mit Session-, Activation-, Segment-ID,
  Sequenz und Settings-Snapshot;
- Pending-Activation-Registry statt globaler Current-Activation-Korrelation;
- genau ein terminaler Segmentausgang für `completed`, `discarded`,
  `cancelled` oder `failed`;
- sessionsweite geordnete Finalpublikation trotz Out-of-order-Completion;
- Queue-Trim, Empty-Final und Workerfehler als sichtbare Terminals;
- Activationterminal erst nach vollständigem Segmentledger.

Nicht vorwegnehmen:

- Commands, Refresh, Watchdog und Closing-Recovery-Timer (`AP-SRV-030`);
- Protokoll v2, Handshake, endgültige Events/Snapshots (`AP-SRV-040`);
- Settings-Control-Plane (`AP-SRV-050`);
- Wake-Word-Katalog/Detection/Kalibrierung (`AP-SRV-060`);
- Legacyabbau (`AP-SRV-070`);
- jegliche Clientproduktänderung.

`AP-CLI-010` ist trotz fertiger Clientbaseline blockiert, bis AP-SRV-040
abgenommen wurde. Deshalb läuft aktuell keine parallele Clientimplementierung.

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
Quellen nicht.

## 6. Tests und Gateprozess

Server:

```powershell
python -m pytest
```

Beim bekannten Windows-Rechteproblem des globalen Pytest-Tempordners werden
`TEMP` und `TMP` auf das ignorierte repositorylokale Verzeichnis `.tmp`
gesetzt. AP-SRV-010 bestand unabhängig `101` fokussierte Tests plus `15`
Subtests und die Vollsuite mit `490 passed, 13 skipped`.

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
