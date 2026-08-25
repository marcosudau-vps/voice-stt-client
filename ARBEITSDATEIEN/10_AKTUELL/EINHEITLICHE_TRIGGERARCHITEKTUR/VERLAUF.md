# Verlauf – Einheitliche Triggerarchitektur

## 2026-08-23 23:50:00 +02:00 – DOC-ARCH-002 COPY-ONLY-Vorbereitung

- Auftrag: `DOC-ARCH-002_SAFE_COPY_ONLY_ARBEITSSTRUKTUR_EINFUEHRUNG_UND_TRIGGER_VORBEREITUNG.md`
  (der frühere `DOC-ARCH-002_ARBEITSSTRUKTUR_EINFUEHRUNG_UND_TRIGGER_MIGRATION.md`
  ist SUPERSEDED und wurde nicht ausgeführt).
- Toolkit `arbeitsstruktur_toolkit_v2.zip` per SHA-256 verifiziert
  (`0c9621239a3347eaf724416a22dfac9721155efb9c8f3a3f01fd6083a7799f5e`).
- Preflight-Sicherung erstellt: `git status`, Binary-Diff, untracked-Dateien
  und vollständiges SHA-256-Manifest der Altstruktur (677 Dateien) unter
  `SESSION_PROMPTS/DOC-ARCH-002_BACKUP/`.
- Neue Zielstruktur (`PLANUNG/`, `IDEEN/`, `ARBEITSPAKETE/`, `QUELLEN/`)
  zusätzlich angelegt; bestehende Inhalte per COPY (kein MOVE) übernommen.
  82 Dateien kopiert, Source→Target-SHA-256 für alle Dateien identisch
  (0 Abweichungen).
- Alte Struktur vollständig unangetastet stehen gelassen.
- Kein Commit, kein Push in diesem Run.

## 2026-08-24 01:08:47 +02:00 – DOC-ARCH-002 Abschlusslauf

- Auftrag: `DOC-ARCH-002_Abschlusslauf.md`.
- Struktur- und COPY_MAPPING-Prüfung: keine unbeabsichtigten Duplikate,
  keine fehlenden Inhalte in der neuen Struktur festgestellt.
- Cleanup der Altstruktur gemäß `DELETE_CANDIDATES_FOR_MANUAL_REVIEW.md`:
  10 gemappte Altpfade entfernt (siehe unten), nachdem alle 82
  COPY-Paare unmittelbar vorher erneut live re-verifiziert wurden
  (82/82 Source-SHA-256 = Target-SHA-256, 0 Abweichungen).
- Zusätzlich 4 leere, nie gemappte Altordner entfernt
  (`05_GRUNDLAGEN/`, `15_DRAFTS_UNGEPRUEFT/`, `50_TOOLS/`,
  `30_AUSFUEHRUNG/` inkl. leerem `runs/`) – nachweislich inhaltsleer, daher
  ohne Informationsverlust.
- Bewusst erhalten: `20_PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`
  (lokal modifizierte, uncommittete Produktarbeit; siehe `STATUS.md`).
- Tote Referenzen auf entfernte Altpfade in `README.md` und
  `ARBEITSPAKETE/AP-TRG-000_GATE_0/README.md` auf die neuen kanonischen
  Pfade aktualisiert. Historische Nachweisdokumente (COPY_MAPPING.md,
  Evidence-Dateien) unverändert gelassen, da dort der alte Pfad Teil des
  historischen Sachverhalts ist.
- Toolkit-Bugfix: `Test-Arbeitsblock.ps1` (installierte Version unter
  `main/.agents/skills/arbeitsstruktur/scripts/`) korrigiert – ein
  Array-Unwrapping-Fehler bei genau einem Kandidaten-Treffer führte unter
  `Set-StrictMode -Version Latest` zu einem Laufzeitfehler. Fix: das
  Filter-Ergebnis wird jetzt mit `@(...)` in Array-Kontext gezwungen. Nach
  dem Fix läuft das Skript ohne internen Fehler und liefert reale
  Struktur-Befunde. Das ursprüngliche ZIP/Backup wurde nicht verändert.
- `AP-TRG-000_GATE_0/runs/00_QUELLPROMPTS/` nach
  `AP-TRG-000_GATE_0/QUELLPROMPTS/` verschoben (Validator interpretiert
  jeden Ordner direkt unter `runs/` als Ausführungs-Run mit erwarteten
  `PROMPT.md`/`REPORT.md`; die kopierten GATE-0-Quellprompts sind aber kein
  Run). `COPY_MAPPING.md` (historischer COPY-PREP-Nachweis) verweist
  weiterhin auf den damaligen Zielpfad `runs/00_QUELLPROMPTS/` und wurde
  bewusst nicht nachträglich umgeschrieben.
- `Test-Arbeitsblock.ps1` gegen die neue Struktur: 1 verbleibender,
  bewusst dokumentierter Fehler (`20_PLANUNG` – siehe oben), 2
  verbleibende Warnungen (nicht sicherheitsrelevant, Fehlklassifikation
  der GATE-0-Quellprompts als „Run ohne PROMPT.md/REPORT.md" durch den
  generischen AP-Runs-Scan; inhaltlich korrekt, da kein echter Run).
- `Test-Arbeitsstruktur.ps1` auf main: PASS (0 Fehler, 0 Warnungen).
- Main (`1b432c9`) committet und auf `origin/main` gepusht.
- DOC-ARCH-002-Organisationsänderungen im Trigger-Branch committet
  (`6b073de`), ohne die zu diesem Zeitpunkt uncommittete Trigger-
  Produktarbeit (`README.md`, `01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`)
  mitzustagen.

## 2026-08-24 02:03:12 +02:00 – Main→Trigger-Integration und Merge-Konfliktauflösung

- `origin/main` (`1b432c9`) kontrolliert in `feat/einheitliche-triggerarchitektur`
  (auf `6b073de`) integriert.
- Konflikte in 9 Dateien fachlich aufgelöst (keine Seite pauschal
  bevorzugt, echte semantische Integration je Fall):
  - `core/stt_session.py`: main + Trigger-Feld `supports_activation_triggers`
    im `client.session.admitted`-Payload übernommen (Trigger-Seite war
    strikter Superset).
  - `core/controller.py` (3 Stellen): main + `server_owns_activation`-Feld,
    `_manual_accept_correlation()` (fällt für Nicht-Trigger-Fälle exakt auf
    mains `hotkey:{generation}:{token}` zurück) und die neuen
    `presentation_mode`/`effective_wake_word_trigger_enabled`/
    `effective_manual_trigger_enabled`-Properties aus `core/config.py`
    (dort bereits konfliktfrei automerged; `wake_word_enabled` bleibt als
    abwärtskompatible Property erhalten) übernommen.
  - `ui/application.py`: dieselbe `presentation_mode`-Property übernommen.
  - `tests/test_obs040_client_hooks.py`,
    `tests/test_obs040_failure_isolation.py`: mains Stand als Basis, die
    3 zusätzlichen Trigger-Tests (`test_trigger_send_and_ack_share_one_command_id`,
    `test_a_repeated_ack_is_recorded_as_dropped_not_as_received`,
    `test_an_ack_without_a_command_id_is_dropped_and_correlation_stays_empty`,
    `test_a_broken_ingress_does_not_stop_a_trigger`) unverändert wieder
    eingefügt, keine Assertion abgeschwächt.
  - `tests/test_obs040_contracts.py`: mains aktualisierter Archivpfad
    (`90_HISTORIE/2026-08-21_...`) übernommen, die 3
    `client.trigger.*`-Contract-Einträge der Trigger-Seite ergänzt.
  - `ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md`, `LOG_VERLAUF.md`: main war
    in beiden Fällen ein reiner Superset (identisch + zusätzliche, aktuelle
    Fakten); vollständig von main übernommen, keine Trigger-Information
    verloren.
  - `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`: main-Superset
    übernommen, zusätzlich veraltete Pfadverweise
    (`20_PLANUNG/`, `30_AUSFUEHRUNG/prompts/GATE_0/`) auf die neuen
    kanonischen Pfade (`PLANUNG/`, `ARBEITSPAKETE/AP-TRG-000_GATE_0/`)
    korrigiert und ein Abschnitt zur DOC-ARCH-002-Integration ergänzt.
- **Unerwarteter Nebeneffekt entdeckt und bereinigt:** `main` besaß
  unabhängig von diesem Run eine eigene, teilweise Kopie der alten
  Trigger-Arbeitsblock-Struktur unter demselben Pfad
  (`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/00_NORMATIV/`,
  `10_ANALYSE/`, Teile von `20_PLANUNG/planung_migration/`,
  `30_AUSFUEHRUNG/prompts/LEGACY_NUMMERIERT/`, `40_EVIDENCE/`). Da diese
  Dateien am gemeinsamen Merge-Vorfahren nicht existierten, hat git sie
  beim Merge als „add/add"/Rename-Kollateral wieder eingeführt, obwohl sie
  im COPY-PREP- bzw. vorherigen Abschlusslauf-Schritt bereits bereinigt
  worden waren. Für alle 73 betroffenen Dateien wurde vor dem Entfernen
  verifiziert, dass ihr Inhalt (nach Normalisierung von CRLF/LF) exakt mit
  der bereits vorhandenen kanonischen Kopie unter `PLANUNG/`/`QUELLEN/`
  übereinstimmt (27 Dateien unterschieden sich nur in der
  Zeilenendung, 0 echte inhaltliche Abweichungen). Danach erneut entfernt;
  keine Information ging verloren.
- Validierung nach Konfliktauflösung:
  - Keine Merge-Konfliktmarker mehr vorhanden (repositoryweit geprüft).
  - `git diff --check`: keine echten Fehler (nur bestehende
    Trailing-Whitespace-/CRLF-/EOF-Hinweise in unveränderten oder
    Toolkit-Dateien).
  - Gezielte Tests (`tests/test_obs040_client_hooks.py`,
    `tests/test_obs040_contracts.py`, `tests/test_obs040_failure_isolation.py`):
    61/61 PASS.
  - Vollständige Client-Test-Suite (`python -m unittest discover -s tests
    -p "test_*.py"`, identisch zu `.github/workflows/ci.yml`): **1191/1191
    PASS**, keine abgeschwächten Assertions.
  - `python -m compileall app.py core ui scripts tests`: PASS.
- **Kein Merge des unfertigen Trigger-Branches zurück nach `main`.**

## 2026-08-24 10:26:57 +02:00 – PLAN-ORG-001 Planungsbereich vereinfacht

- Verschachtelte Planungsdateien in eine flache Struktur unter `PLANUNG/`
  überführt und `NACHVERFOLGUNG/` als separaten Status-/Fundbereich
  eingerichtet.
- Doppelte, zuvor hash-identisch geprüfte Altpfade entfernt; die konkrete
  Namespace-Idee blieb ausschließlich unter `IDEEN/` erhalten und wurde
  fachlich nicht ausgewertet.
- `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md` als zentrale Arbeitsdatei
  etabliert und die besprochenen Wake-Word-, Pause-, Mute-, Pre-Roll- und
  Hotkey-Entscheidungen aufgenommen.
- Frühere feste Aussage `Hotkey Active = Finish` sowie kumulative
  Extend-Semantik als überholt markiert. Gewünschtes `refresh`: Deadline auf
  den konfigurierten Timeout ab letzter gültiger Interaktion zurücksetzen,
  niemals Zeit ansparen.
- Zwei Ist-Abweichungen nachverfolgt: kumulative `_pending_extension` im
  neuen Server-ActivationController (`FIND-010`) und gemeldete mehrfache
  Wake-Word-Detection-Signale (`FIND-011`).
- Keine Produktcodeänderung, keine AP-Zuordnung und kein Commit in diesem
  Dokumentationslauf.

## 2026-08-24 11:14:03 +02:00 – PLAN-CONS-001 Bekannte Soll-Widersprüche konsolidiert

- Bereits besprochene Entscheidungen aus der zentralen Arbeitsdatei an den
  widersprechenden Stellen im `ZIELBILD.md` übernommen: konfigurierbare
  Active-Hotkey-Aktionen, Default-Richtung `primary=refresh` und
  `secondary=finish`, nicht kumulatives Refresh sowie source-neutrale
  Activation-Steuerung.
- Wake-Word-Pause als separaten Laufzeitzustand präzisiert: automatische
  Reconnects werden überstanden, App-Neustart beginnt ungepausiert, null
  effektive Trigger sind bei Wake-Word-only bewusst erlaubt und ReSpeaker-
  Hardware-Mute bleibt unabhängig.
- Wake-Word-Buildkatalog, globales Disable, Sessionauswahl, kanonische
  IDs/Aliase, gemeinsame Empfindlichkeit und erkennbare Wake-Word-ID in das
  Zielbild übernommen.
- Alte Sollfolgerungen in `TARGET_MIGRATION_MAP.md` und
  `LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md` als überholt markiert
  bzw. auf den besprochenen Stand gebracht; Ist-Codebefunde blieben erhalten.
- Traceability um fehlende CORE-IDs ergänzt und Status-/Fundtexte korrigiert.
- Keine neue fachliche Entscheidung erfunden, kein Namespace-Inhalt gelesen,
  kein Produktcode geändert und kein Commit erstellt.

## 2026-08-24 11:32:38 +02:00 – PLAN-CONS-002 Weitere Bedien- und Lifecycle-Entscheidungen konsolidiert

- Heutiges Mehrsegment-Verhalten als Soll bestätigt: Eine Activation kann
  mehrere aufeinanderfolgende Sprachsegmente über `followup_wait` enthalten;
  der Trigger-Lock bleibt bis zum Abschluss der gesamten Activation gesetzt.
- `refresh` auf `followup_wait` begrenzt und für `waiting_first_speech` sowie
  `segment_active` ausgeschlossen; kein Ansparen oder Kumulieren.
- Drei getrennte Hotkeyplätze festgelegt: zwei konfigurierbare
  Activation-Hotkeys und ein dritter optional belegbarer Hotkey für
  Wake-Word-Pause/-Fortsetzen.
- Finish-/Cancel-Außenwirkung präzisiert: Finish verarbeitet angenommene
  Segmente regulär, Cancel verwirft Nutzresultate; jeder akzeptierte Command
  erzeugt ein korreliertes Lifecycle-Ereignis und jedes angenommene Segment
  einen terminalen Ausgang.
- Wake-Word-Ressourcenstrategie auf selected-only festgelegt: Der Katalog
  bleibt vollständig auswählbar, initialisiert werden beim Sessionstart nur
  die ausgewählten Modelle. RAM und Startzeit werden gemessen statt aus der
  Artefaktgröße abgeleitet.
- Aktuellen OpenWakeWord-Adapter geprüft: ungefähr 32-ms-Chunks, ein neuester
  Score oberhalb der Sensitivity genügt, keine explizite Mehrfach-Chunk-Regel.
  Der fehlende Detection-Guard nach dem ersten Treffer bestätigt den
  Mehrfachsignalpfad. Fachlicher Latch bis zum Unlock ist festgelegt; nur eine
  zusätzliche Fehlalarm-Bestätigung bleibt bis zu Score-/Audio-Traces offen.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert, kein Commit
  erstellt.

## 2026-08-24 12:19:15 +02:00 – PLAN-CONS-003 Finish-/Cancel- und Admission-Verträge fachlich eingefroren

- Finish-/Cancel-Phasenmatrix für `inactive`, `waiting_first_speech`,
  `segment_active`, `followup_wait` und `finalizing` bestätigt.
- Exactly-once-Regel festgelegt: genau ein fachliches Lifecycle-Ereignis je
  neu angenommener Transition; Replays derselben `commandId` liefern dasselbe
  Ack ohne Ereignisduplikat, spätere Commands nur eine idempotente
  Zustandsantwort.
- Cancel-Grenze bestätigt: unveröffentlichte Resultate werden unterdrückt
  oder verworfen; bereits veröffentlichter bzw. eingefügter Text bleibt
  unverändert. Nicht sicher abbrechbare Inferenz darf intern fertiglaufen,
  aber nichts mehr veröffentlichen.
- Wake-Word-Admission atomar festgelegt: unbekannte, deaktivierte oder nicht
  ladbare ID lehnt die vollständige Sessionauswahl mit maschinenlesbarer
  Fehlerliste ab; kein Teilerfolg und kein stiller Fallback.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert und kein Commit
  erstellt.

## 2026-08-24 23:17:21 +02:00 – PLAN-CONS-004 Reconnect-, Settings- und Dauerschutzentscheidungen konsolidiert

- Serververbindungsverlust während einer Activation als Abbruch mit neuer
  Idle-Session festgelegt; Geräteverlust cancelt die Activation, beendet die
  Serversession aber nicht und löst lokale Wiederverbindungsversuche aus.
- Persistierte triggerlose Basiskonfiguration ausgeschlossen. Null effektive
  Trigger bleiben als bewusster Zustand derselben Client-Laufzeit über
  Reconnects, neue Sessions und Geräteverlust erhalten, werden beim
  Programmneustart aber verworfen.
- Server als letzte Settings-Autorität bestätigt: Sessionwerte mit Defaults
  und Effective-Value-Rückmeldung, admin-geschützte Serverwerte sowie
  Änderungen während der Session gemäß Apply-Policy.
- Settings-Control-Plane, triggerrelevante Einstellungen und eine gesperrte
  Servereinstellungsseite in den Trigger-Umbau aufgenommen; vollständige
  fachfremde Settings-Migration bleibt nachgelagert.
- Wake Word aus dem Nutztranskript ausgeschlossen, unmittelbar folgende
  Sprache jedoch als lückenlos zu erhaltender Audiofluss festgelegt.
- Großzügigen Daueraufnahme-Watchdog mit Hotkey-Reset, ohne VAD-Reset,
  Vorwarnung und Abschluss der gesamten Activation festgelegt; offen bleibt
  Finish- oder Cancel-Wirkung auf das bis dahin erfasste Segment.
- Browserclient als späterer, nicht blockierender Nachzug klassifiziert;
  versionierte Desktop-Client-/Server-/Protokoll-Kompatibilitätsmatrix
  gefordert.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert und kein Commit
  erstellt.

## 2026-08-25 00:17:14 +02:00 – PLAN-CONS-005 Zweite fachliche Härtungsrunde abgeschlossen

- Daueraufnahme-Watchdog auf zehn Minuten Default und 30 Sekunden Vorwarnung
  konkretisiert. Bei Ablauf endet die gesamte Activation, das bis dahin
  erfasste Audio wird jedoch regulär verarbeitet; Anwenderarbeit wird ohne
  aktive Entscheidung nur bei technisch unvermeidbarem Verlust verworfen.
- Manual und Wake Word als getrennt laufzeitweit suppressierbar festgelegt;
  keine zusätzliche Sammelaktion zum Pausieren aller Trigger.
- Verantwortungsgrenze geschärft: Physische Hotkeys, ReSpeaker-/Gerätelogik,
  Mute und sämtliche Feedbackkonfiguration bleiben im Client. Der Server
  verarbeitet semantische Activation-Commands, einen generischen
  Audioverfügbarkeitsstatus und liefert zuverlässige Domain-Events.
- Unveränderlichen Settings-Snapshot je Activation und den dreistufigen
  Clientdialog für reconnectpflichtige Änderungen während einer Activation
  bestätigt.
- Dauerhafte Admin-Key-Speicherung im Windows Credential Manager mit
  UI-gesteuertem Anlegen, Ersetzen und Löschen festgelegt; `QSettings` hält
  nur nicht geheime Metadaten, ein Klartext-Fallback ist ausgeschlossen.
- Klaren Desktop-Protokoll-Cut ohne Legacy-Mitschleppen sowie eine
  Versions-/Commit-Kompatibilitätsmatrix und verständliche
  Inkompatibilitätsmeldung bestätigt; Browserclient bleibt nachgelagert.
- Zielbild, Entscheidungen, Reihenfolge, Traceability, Status und technische
  Analysen konsolidiert. Kein Namespace-Inhalt gelesen, kein Produktcode
  geändert und kein Commit erstellt.

## 2026-08-25 01:20:27 +02:00 – PLAN-FREEZE-001 Technischer Contract und Implementierungsplan eingefroren

- Trigger-Lock-Freigabe nach sicherem Ende des Follow-up-/Eingabefensters
  bestätigt. Hintergrund-Finalisierung blockiert neue Activations nicht;
  stabile Activation-/Segment-IDs, Terminalledger und geordnete Veröffentlichung
  verhindern Fehlzuordnung verspäteter Resultate.
- Kanonische Vordergrundphasen `idle`, `waiting_first_speech`,
  `segment_active`, `followup_wait` und `closing_input` festgelegt;
  `finalizing` ist nur noch Hintergrundverarbeitung (`draining`).
- Watchdogvertrag auf 600 Sekunden initial, 180 Sekunden Mindestrestzeit nach
  Refresh und 30 Sekunden Vorwarnung eingefroren. Refresh verkürzt keine
  längere Restzeit und kumuliert nicht.
- Protokollversion 2 mit Handshake, IDs, Commands/Acks, Domain-Events,
  Snapshot, Resync, Settings-Control-Plane, Wake-Word- und Recoveryvertrag in
  `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md` festgeschrieben.
- Finalen Implementierungsplan erstellt und auf ausdrücklichen Wunsch strikt
  repositoryweise geschnitten: `AP-SRV-*` besitzt nur Servercode,
  `AP-CLI-*` nur Clientcode; `AP-INT-*` ändert keinen Produktcode und gibt
  Befunde an ein eindeutig zugeordnetes Korrektur-AP zurück.
- Überholten Reihenfolgeentwurf nach Übernahme in den finalen Plan entfernt;
  README, Status, Current State und Traceability auf Plan-Freeze gebracht.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert und kein Commit
  erstellt.

## 2026-08-25 02:03:42 +02:00 – PLAN-EXEC-001 Parallelausführung und Agentenaufträge vorbereitet

- Exaktes Protokoll-v2-Wire-Schema mit Pflichtfeldern, Acks, Result-Codes,
  Eventfeldern, Snapshot-Semantik und Close-Codes als normative Ergänzung zum
  Contract-Freeze erstellt.
- Maschinenlesbare Positiv-/Negativvektoren für SRV-040, CLI-010 und INT-010
  angelegt. Die frühere Mehrdeutigkeit wurde beseitigt: Der Desktop-Client
  sendet nur manuelle Activation-Commands; Wake-Word-Admission ist
  serverintern.
- Ausführungsworkflow mit maximal einer GPT-5.6-Sol-Lane und einem separaten
  Claude-Code-CLI-Lauf, Abnahme-Gates, konkreten Parallelisierungswellen und
  kapazitätsbewusster Sonnet-/Opus-Zuordnung erstellt.
- Dokumentationspflicht als Bestandteil jedes APs festgeschrieben und eine
  Auftragsschablone mit Repositoryownership, Contract, Tests, Dokumentzielen,
  Commit- und Rückgabeformat angelegt.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert, kein Agentenlauf
  gestartet und kein Commit erstellt.

## 2026-08-25 02:51:08 +02:00 – PLAN-EXEC-002 Traceability und Commit-/Push-Gates vollständig vorbereitet

- Traceability gegen Entscheidungen, Zielbild, technischen Contract,
  Wire-Schema und Implementierungsplan vollständig auditiert und von einer
  stark gebündelten Matrix auf 129 eindeutige Summary- und
  Einzelanforderungen erweitert.
- Live-/Early-Final-/Follow-up-Parallelität normativ ergänzt und vier
  Wire-Unklarheiten geschlossen: leere Wake-Auswahl nur bei deaktivierter
  Wake-Quelle, IDs je manueller oder serverinterner Activation-Admission,
  sessionsweite `activationSequence` für Snapshot-Sortierung sowie
  `causedByCommandId` für Finish-/Cancel-Korrelation.
- Hotkey-Kollisionsregel und konkrete Wake-Cooldown-/Pre-Roll-Kalibrierwerte
  ausdrücklich als offene, vor CLI-020 beziehungsweise SRV-050/060 zu
  schließende Punkte nachverfolgt; kein Baselineblocker.
- Bestehenden Server-Worktree und Feature-Branch bestätigt. Alle lokalen
  Serveränderungen liegen dort weiterhin unverändert; GitHub-Remote für das
  Serverrepository ergänzt.
- Repositorylokale AP-Akten sowie ein lokaler Agentencommit mit
  Korrektur-Amend, Root-Endabnahme im selben Commit und Push erst nach PASS als
  verbindlichen Workflow festgeschrieben.
- Kein Namespace-Inhalt gelesen, kein Produktcode verändert und noch kein
  Implementierungsagent gestartet.

## 2026-08-25 03:28:14 +02:00 – EXEC-W1-001 Baselinewelle abgenommen und gepusht

- `AP-SRV-000` auf dem Serverrepository durch einen GPT-Agenten umgesetzt,
  nach Root-Befund im selben Agentenlauf korrigiert, unabhängig mit 3
  fokussierten Tests sowie der Vollsuite (`492 passed, 13 skipped`) validiert
  und als genau ein Commit gepusht:
  `71a35e074eb90d75f8f91f5ed7cb46accd4b6498`.
- `AP-CLI-000` über Claude Code mit Sonnet umgesetzt, nach drei dokumentierten
  Prüf-/Korrekturrunden im selben Commit gehärtet und durch die Koordination
  mit 24 fokussierten Tests sowie der Vollsuite (`1192 passed`) validiert.
  Gepushter Commit:
  `042fcd203c873d6f84a270413c47bc5da1fbf1ed`.
- Für beide Pakete liegen Originalprompt, Agentenbericht, Root-Abnahme und
  Evidence repositorylokal vor. Es wurde jeweils erst nach PASS gepusht.
- Der GitHub-Account für weitere Operationen ist `marcosudau-vps`.
- `AP-SRV-010` ist freigegeben. Die Client-Lane bleibt bis zum PASS von
  `AP-SRV-040` dependency-bedingt ohne ausführbares Produktpaket.
