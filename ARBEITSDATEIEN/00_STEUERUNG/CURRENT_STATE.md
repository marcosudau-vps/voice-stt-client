# CURRENT STATE

Active Workstream:
Einheitliche Triggerarchitektur

Previous Milestone:
Logging / Observability Teil A
CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE / ARCHIVED

Formal G-OBS-V1:
NOT PASSED

Deferred:
Logging / Observability Teil B
Start nach Trigger mit OBS-100 (bis OBS-180)

Next:
Triggerarchitektur: Serverlinie weiter auf `AP-SRV-070` (Legacyabbau und
Protokollgrenze); letzter kanonisch abgeschlossener Server-AP ist `AP-SRV-060`
(Serverbranch `feat/einheitliche-triggerarchitektur` =
`c82923fc6ce889b4dfbbde1f9877b8b76481a1e8`). Die Clientlane ist technisch
entblockt (technische Dependency AP-SRV-040 erfüllt), wird aber bewusst bis
zum Abschluss der Serverlinie AP-SRV-060 → AP-SRV-070 deferred.
Distributed-/Review-Branches sind Execution-Provenienz und keine neue
kanonische Basis; die zentrale Paketkette liegt auf
`feat/einheitliche-triggerarchitektur`.

---

## Logging / Observability Teil A – Zusammenfassung

Der vorgezogene Logging-/Observability-Workstream (OBS-000 bis OBS-060 plus
Diagnose-UI-Nachbesserung) ist mit Run `OBS-CLOSE-001` (2026-08-23)
organisatorisch abgeschlossen und archiviert:

- Status: `CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`.
- Formal: `G-OBS-V1 NOT PASSED` (kein formales finales Gate-PASS; bestimmte
  manuelle/formale Restabnahmen — u. a. `M-1…M-11` — wurden bewusst auf den
  nach der Trigger-Migration maßgeblichen Gesamtzustand verschoben).
- Archivpfad:
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/`
- Kanonische Produktdokumentation: `docs/observability/`
- Die vollständige Gate-für-Gate-Historie (OBS-000 bis OBS-060, alle Runs,
  Gate-Reviews, Korrekturläufe, Befunde) ist verlustfrei erhalten in:
  - `ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md` (append-only, aktiv, nicht
    verschoben),
  - der archivierten Arbeitsakte unter obigem Archivpfad (Runs, Evidence,
    Work Packages),
  - dem historischen Vor-Kompaktierungs-Snapshot dieser Datei:
    `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/90_ZWISCHENARCHIV/CURRENT_STATE_VOR_KOMPAKTIERUNG_2026-08-23.md`.
- Teil B (`OBS-100` bis `OBS-180`) ist im `MASTERPLAN.md` als
  `DEFERRED / BLOCKED BY TRIGGER ARCHITECTURE` verankert und beginnt erst nach
  der Triggerarchitektur-Migration.

## Einheitliche Triggerarchitektur

- Zielbild und Voranalysen vorhanden. Bereits besprochene Wake-Word-, Pause-
  und Hotkeyentscheidungen wurden am 2026-08-24 in die widersprechenden
  Zielbild- und Analysepassagen konsolidiert; weiterhin offene Verträge sind
  klar als offen abgegrenzt.
- Ergänzend festgelegt: mehrere serielle Sprachsegmente je Activation,
  `refresh` nur in `followup_wait`, dritter optional belegbarer
  Wake-Pause-Hotkey, Finish-/Cancel-Außenwirkung samt Lifecycle-Ereignis und
  selected-only Laden der Wake-Word-Modelle beim Sessionstart. Detection wird
  nach dem ersten akzeptierten Treffer bis zum Unlock gelatcht; nur eine
  zusätzliche Fehlalarm-Bestätigung wird nach Score-/Audio-Messung gehärtet.
- Finish-/Cancel-Phasenmatrix und Retry-Semantik sind fachlich eingefroren:
  genau ein Lifecycle-Ereignis pro neu angenommener Transition, kein Duplikat
  bei Command-Replay; Cancel unterdrückt nur unveröffentlichte Resultate und
  nimmt bereits ausgegebenen Text nicht zurück. Ungültige Wake-Word-Auswahl
  wird vollständig ohne Teilerfolg oder Fallback abgelehnt.
- Serververbindungsverlust verwirft die laufende Activation; Geräteverlust
  cancelt sie, lässt die Serversession aber bestehen. Ein triggerloser Zustand
  darf nur clientlaufzeitweit bestehen und wird beim App-Neustart verworfen.
- Settings-Control-Plane wird in den Umbau aufgenommen: Serverautorität,
  Session-/Server-Scope, Apply-Policies, triggerrelevante Einstellungen und
  admin-geschützte Servereinstellungsseite. Fachfremde Vollmigration bleibt
  für den späteren Settings-Arbeitsblock.
- Daueraufnahme-Schutz: zehn Minuten Default, kein VAD-Reset, Hotkey-Refresh
  als Anwesenheitssignal, Vorwarnung 30 Sekunden vorher und Ende der gesamten
  Activation. Das bereits erfasste Audio wird regulär verarbeitet; investierte
  Sprache wird nicht wegen eines Schutzablaufs stillschweigend verworfen.
- Manual und Wake Word sind getrennt clientlaufzeitweit suppressierbar; eine
  zusätzliche Pause-all-Funktion wird nicht eingeführt. Physische Hotkeys,
  Geräte- und Feedbackkonfiguration bleiben im Client. Der Server kennt nur
  semantische Commands und einen generischen Audioverfügbarkeitsstatus.
- Eine laufende Activation behält ihren unveränderlichen Settings-Snapshot.
  Reconnectpflichtige Änderungen währenddessen werden nicht automatisch
  abgebrochen, sondern über die drei bestätigten UI-Wege gesteuert.
- Der Admin-Key wird bei dauerhafter Speicherung im Windows Credential Manager
  gehalten und bleibt über die UI löschbar. Desktop-Client und Server erhalten
  einen klaren Protokoll-Cut samt Versions-/Commit-Kompatibilitätsmatrix;
  Browser und Legacy-Pfade blockieren den Umbau nicht.
- Der Trigger-Lock endet nach sicherem Schließen des Follow-up-/Eingabefensters
  und wartet nicht auf Final-Inferenz. Ältere Activations dürfen im Hintergrund
  drainen; ihre Resultate bleiben über stabile IDs und Segmentreihenfolge
  korrekt zugeordnet. `finalizing` ist keine blockierende Vordergrundphase.
- Segment-Watchdog: 600 Sekunden initial, nach Refresh mindestens 180 Sekunden
  ab Interaktion, ohne Verkürzung längerer Restzeit und ohne Kumulierung;
  Warnung 30 Sekunden vorher.
- Technischer Contract und finaler Implementierungsplan sind eingefroren.
  `AP-SRV-*` ändert ausschließlich Servercode, `AP-CLI-*` ausschließlich
  Clientcode; `AP-INT-*` validiert nur und ändert keinen Produktcode.
- Exaktes v2-Wire-Schema und gemeinsame maschinenlesbare Vertragsvektoren
  ergänzen den Contract-Freeze. Clientseitiges `activate` darf nur
  `source=manual` tragen; Wake-Word-Admission entsteht ausschließlich intern
  auf dem Server.
- Parallelausführung ist vorbereitet: maximal ein GPT-5.6-Sol-Sub-Agent und
  ein Claude-Code-CLI-Lauf mit Sonnet oder gezielt Opus. Wellen, Gates,
  Modellempfehlungen, Dokumentationsownership und Root-Endabnahme stehen in
  `PLANUNG/AUSFUEHRUNGS_WORKFLOW.md`; konkrete Prompts entstehen paketweise
  aus `ARBEITSPAKETE/AUFTRAGSVORLAGE.md`.
- Traceability ist nach Vollständigkeitsaudit auf 129 eindeutige Summary- und
  Einzelanforderungen granularisiert. Wire-Lücken zu Wake-Auswahl,
  serverinterner Activation-Admission, Command-Korrelation und stabiler
  Pending-Sortierung sind geschlossen; Hotkey-Konfliktregel sowie konkrete
  Wake-Cooldown-/Pre-Roll-Kalibrierwerte bleiben sichtbar vor ihren späteren
  APs offen.
- Server-Feature-Branch und Worktree existieren bereits. Die vorhandenen
  uncommitteten Serveränderungen werden als geerbter Baseline-Diff in
  AP-SRV-000 übernommen; die GitHub-Remote ist eingerichtet.
- Jedes AP erhält eine repositorylokale Akte. Agenten committen lokal, die
  Koordination prüft/amended die Endabnahme und pusht genau einen finalen
  Commit erst nach PASS.
- Nach dem kontrollierten Abschluss von Logging/Observability Teil A ist die
  Triggerarchitektur wieder alleiniger aktiver Hauptworkstream unter
  `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/`.
- Zentrale aktuelle Arbeitsdatei:
  `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`.
- Status und Funde: `NACHVERFOLGUNG/` sowie `STATUS.md` und `VERLAUF.md`.
- Kontextunabhängige operative Übergabe für neue Agents:
  `NACHVERFOLGUNG/WIEDEREINSTIEG.md`.
- Ausführungswelle 1 ist abgenommen und gepusht: AP-SRV-000 auf
  `71a35e074eb90d75f8f91f5ed7cb46accd4b6498`, AP-CLI-000 auf
  `042fcd203c873d6f84a270413c47bc5da1fbf1ed`. Die genaue Gate-Historie steht
  in `NACHVERFOLGUNG/AUSFUEHRUNGSSTATUS.md`.
- AP-SRV-020 ist nach zwei Root-Befunden, Korrektur durch denselben Agenten
  und unabhängiger Root-Abnahme als
  `8535ee79bb2d898d9897e91b57d6a735c479edf0` gepusht. AP-SRV-030 und
  AP-SRV-040 sind danach als kanonische Archive-Complete-Commits auf
  `feat/einheitliche-triggerarchitektur` geschlossen: AP-SRV-030
  `b220dd03a594d2b9f8cad65fd279046be36864cc`, AP-SRV-040
  `c0806e5bc5d503580070f2dacc88831d51447938`. Die erste
  fachliche Clientänderung in AP-CLI-010 ist technisch entblockt, wird aber
  bewusst deferred, bis die Serverlinie AP-SRV-050 → AP-SRV-060 → AP-SRV-070
  abgeschlossen ist.
- `AP-SRV-050` (Settings-Control-Plane) ist nach drei lokalen Läufen
  (C1 Implementierung, C2 sechs Root-Findings, C3 Wire-Atomicity) mit
  `ROOT PASS` abgenommen und als genau ein kanonischer Commit auf
  `feat/einheitliche-triggerarchitektur` geschlossen:
  `c901cda3f2c19eeb78c468524161728498b6e27e` (Parent `c0806e5…`,
  Root-PASS-Source C3 `18b65216433329456946afd3c41d8df6bbd07d44`).
- `AP-SRV-060` (Wake-Word-Katalog, Detection und Audiogrenze) ist mit
  `ROOT PASS` abgenommen und als genau ein kanonischer Commit auf
  `feat/einheitliche-triggerarchitektur` geschlossen:
  `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8` (Parent `c901cda3f2c19eeb78c468524161728498b6e27e`,
  Tree `de6fe364545b508a47a87ead67a01c5732477e71`, Root-Source-Stand
  `2b08e379a36590c99e48e59c81a39418395d9742` aus C1/C2/C3/Asset-Finalisierung/Final-Repair).
  Der Server besitzt damit den versionierten Buildkatalog
  (`VoiceSTT/assets/wakeword_models/` mit ONNX- und TFLite-Dual-Backend-Artefakten),
  die öffentliche Catalog-API `GET /api/v2/wake-words` (`SET-13b`) und
  `POST /api/v2/wake-words/refresh`, atomare Sessionadmission,
  selected-only Modellinitialisierung, `WakeHitTracker` mit Exactly-once
  `wakeword.detected`-Eventing, Single-Backend-je-Engine-Policy sowie die
  detection-verankerte Audiogrenze (operationaler Nullpunkt an Trailing Edge des
  Wake-Hits). Vollsuite: 1180 passed, 14 skipped, 762 subtests, 0 failed.
  Empirische Kalibrierung (`WW-18`, `WW-19`) bleibt ehrlich als
  `EVIDENCE_BLOCKED / calibration pending` ausgewiesen.
  `AP-SRV-070` (Legacyabbau und Protokollgrenze) ist das nächste Serverarbeitspaket.
- Die textuelle Server-Prep-Provenienz vom 2026-08-25 ist byteidentisch
  versioniert unter
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-25_TRIGGERARCHITEKTUR_SERVER_PREP/`.
  Sie ist ausdrücklich **nicht normativ**.

## Workspace-Status (WS-NORM-002)

- Aktiver Workspace: `workspaces\einheitliche-triggerarchitektur`
  (Branch `feat/einheitliche-triggerarchitektur`), Standard-Agent-Session-Root.
- Kein aktiver Logging-Worktree mehr; `workspaces\logging-observability-pre-trigger`
  ist git-seitig entfernt und physisch nicht mehr vorhanden.

## Arbeitsstruktur- und Main-Integration (DOC-ARCH-002)

- Repositoryweite deterministische Arbeitsstruktur (`.agents/skills/arbeitsstruktur/`,
  `AGENTS.md`/`CLAUDE.md`-Verweise) in `main` eingeführt und auf `origin/main`
  gepusht.
- Trigger-Arbeitsblock zunächst auf die deterministische Grundstruktur
  umgestellt und anschließend für die laufende Arbeit auf die klaren
  Einstiege `PLANUNG/` und `NACHVERFOLGUNG/` vereinfacht; doppelte Altpfade
  wurden nach Inhaltsabgleich entfernt.
- `main` kontrolliert in `feat/einheitliche-triggerarchitektur` übernommen;
  Konflikte in Governance-Dokumenten und in `core/controller.py`,
  `core/stt_session.py`, `ui/application.py` sowie den OBS-040-Tests fachlich
  zusammengeführt (beide Entwicklungsstände erhalten, keine Seite verworfen).
- Dieser Organisationsrun trifft keine fachlichen Triggerentscheidungen.

**Stand:** 2026-08-29 09:09:02 +02:00 (CANONICAL CLOSE AP-SRV-060; nächster
aktiver Server-AP ist AP-SRV-070)
