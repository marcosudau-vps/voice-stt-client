# CURRENT STATE

## Logging / Observability

- OBS-000: PASS
- OBS-010: GATE PASS (2026-08-17, unabhaengiger Review)
- OBS-030: **GATE FAIL** (2026-08-17, unabhaengiger Review). Drei
  blockierende Befunde (B-1 fehlende Fehlerisolation auf Schleifenebene im
  Worker, B-2 widersprechende Evidence, B-3 P-8-Pfadpruefung fehlt); Details
  in `40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`.
  OBS-040 darf nicht beginnen.
- OBS-030: **CLEANUP COMPLETED – READY FOR INDEPENDENT RE-REVIEW**
  (2026-08-17, Korrekturlauf `RUN-OBS-030-02_2026-08-17` inkl. Cleanup).
  B-1, B-2 und B-3 behoben und getestet; W-1/W-2/W-4/W-5/W-7 korrigiert,
  W-3 und W-6 mit Contract-Referenz begruendet nicht. Der Cleanup hat zwei
  nicht autorisierte Aenderungen desselben Runs zurueckgenommen: den Zaehler
  `dropped_failed` und den Nachtrag `DR-OBS-030-01` in
  `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`. **Kein normatives Dokument
  ist durch diesen Run veraendert.** **Das Gate bleibt offen** — ein
  Korrekturlauf vergibt sein eigenes Gate nicht. Offen bleibt die Auslegung
  von `ARCH §8.3` „nur verwerfen und zaehlen"
  (`40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md`). Details in
  `30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/` und
  `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/`.
- OBS-020: GATE PASS (2026-08-17, unabhaengiger Review). Geprueft gegen
  Repository-Zustand, `git diff`/`git status`, eigenstaendigen Testlauf
  (`-k obs020` 75/75 gruen; volle Suite 714/715 gruen, der eine Fehlschlag
  `test_ap06_followup.py` nachweislich vorbestehend/umgebungsbedingt
  [`lefx.interfaces` fehlt lokal] und ausserhalb des Diffs), Diagnoseskript
  und Evidence. Gesondert geprueft: „raw-Referenz ohne Kopie" – keine
  Verletzung, kein neuer Pfad durch OBS-020 (`ARCH §8.2`-gedeckt, `raw` wird
  vom in OBS-020 aktiven Pfad gar nicht gesetzt; der einzige Pfad, der es
  koennte, ist unverdrahtetes OBS-040-Vorgriffsgeruest).
- OBS-030: **GATE PASS – OBS-040 MAY PROCEED** (2026-08-17, zweiter
  unabhaengiger Review in frischer Session,
  `40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/GATE_REVIEW.md`).
  Geprueft wurde der tatsaechliche Repositoryzustand: Code, `git diff`/
  `git status`, eigene Testlaeufe mit beiden Runnern, eigene
  Fault-Injection- und Laufzeitproben sowie ein Vergleichslauf gegen einen
  aus `b363346` frisch ausgepackten Baum — nicht die Abschluss-, Korrektur-
  oder Cleanup-Berichte. B-1 (Worker-Fehlerisolation inkl. eigener
  Fault-Injection), B-2 (Evidence-Konsistenz) und B-3 (P-8 gegen den real
  aufgeloesten Profilpfad) sind geschlossen; W-1, W-2, W-4, W-5 und W-7
  nachgemessen, W-3 als benannte Luecke und W-6 als OBS-050-Scope bestaetigt.
  Die Schwelle `WORKER_FAILURE_THRESHOLD = 5` ist als normativ gedeckt
  begruendet (keine Erweiterung eines eingefrorenen Vertrags).
  **Entscheidung zu `ARCH §8.3` „nur verwerfen und zaehlen": Variante 1** —
  aus dem bestehenden Freeze loesbar (`ARCH §5` friert den `FAILED`-Zweig als
  reines `return False` ein und markiert das Zaehlen nur am
  Queue-voll-Schritt; `§8.3` referenziert Zaehler, definiert sie nie;
  `§8.5 GRENZE 3` benennt den Totalverlust nach Workerausfall ausdruecklich
  als Architektureigenschaft und nicht als Mangel). **Kein neuer Zaehler,
  keine Freeze-Aenderung, kein DECISION-REQUIRED-Bedarf fuer die Abnahme.**
  `00_NORMATIV/` ist byte-identisch zu `b363346`. Teststand: 129
  OBS-030-Tests (`pytest` und `unittest`), 331 OBS-010+020+030, volle Suite
  843 passed / 1 Fehlschlag, dessen Vorbestand gegen einen sauberen
  `b363346`-Baum nachgewiesen ist (714 passed / 1 identischer Fehlschlag;
  Differenz exakt die 129 neuen Tests). Genau ein lokaler Commit fuer den
  geprueften OBS-030-Endstand erstellt; kein Push, kein Merge, kein Tag.
  Nicht-blockierende Beobachtungen N-1 bis N-5 im Gate-Review dokumentiert.
- Naechster Schritt: **OBS-040 – Server Live Adapter & Client Observation
  Hooks** (Implementierung, frische Session,
  `Prompts/OBS-040_IMPLEMENTIERUNGSAUFTRAG.md`). Readiness im Gate-Review
  geprueft: keine Blocker; der Fan-out-Hook in
  `core/session_coordinator.py` ist genau der offene Gegenstand von OBS-040.
  Mitzunehmen: N-1 (`logging.record_rejected` existiert nirgends im Code)
  und N-4 (Uebergabe des Managers an `DesktopApplication`, fuer OBS-050).

## Einheitliche Triggerarchitektur

- Zielbild und Voranalysen vorhanden.
- Umsetzung wartet auf die vorgeschaltete Observability Foundation.

## Aktueller organisatorischer Schritt

- OBS-010 Gate Review abgeschlossen (2026-08-17, frische Session): **PASS**.
  Unabhängig gegen Repo-Zustand, `git diff`, Tests und Evidence geprüft (nicht
  nur gegen den Abschlussbericht). Feldliste, Prioritätsableitung,
  Wertemengen, alle drei Normalizer-Eingänge, Redaction R-1..R-12 und die
  Query-/Storage-/Sink-Protokolle entsprechen `LOGGING_CONTRACTS_FREEZE_V1.md`.
  Eigenständiger Testlauf bestätigt 640/640 grün (513 Baseline + 127 neu) und
  das Diagnoseskript (Exit 0). Gesondert geprüfter Punkt „raw-Referenz ohne
  Kopie" (`models._freeze` Identity-Branch für `MappingProxyType`): **keine
  Verletzung** — normativ durch `ARCH §8.2` gedeckt, und `result.payload`
  ist über `event_protocol._freeze_value` nachweislich rekursiv aus frischen
  Objekten aufgebaut (keine lebende Referenz auf eine mutierbare
  Ausgangsstruktur), also sicher ohne Kopie referenzierbar. `git diff --check`
  leer, kein Cross-Workstream-Diff. OBS-010 Implementierung abgeschlossen
  (2026-08-17, Run `RUN-OBS-010-01_2026-08-17_DEEPSEEK`): kanonisches Paket
  `core/observability/**` + 127 neue Contract-Tests. Keine bestehende Datei
  geändert.
- Repository-/Workspace-Reorganisation abgeschlossen (2026-08-17).
- Neuer kanonischer Workspace-Pfad:
  `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`
  (ersetzt den bisherigen Pfad unter `marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude\voice-stt-client`).
- Technischer Vorgänger-Commit: `5f2ee4bfceda2cec5bb6ddd0e8c28b2c6c371e1c`
  ("umbau trigger-architektur claude 1 (debugging erforderlich)").
- ARBEITSDATEIEN in voice-stt-client integriert, gemeinsamer Git-Baseline-Commit
  ("chore: establish OBS-010 project baseline and work archive") auf diesem Vorgänger
  erstellt.
- Nächster Schritt: OBS-010 Review / Gate.
- OBS-020 Implementierung abgeschlossen (2026-08-17, Run
  `RUN-OBS-020-01_2026-08-17_CLAUDE`): `core/observability/health.py` und
  `core/observability/adapters/python_logging.py` neu; `ingress.py` additiv um
  `ObservabilityIngress`/`NullIngress`/`NULL_INGRESS` erweitert (das
  OBS-010-`Ingress`-Protocol bleibt unverändert); `core/logging_setup.py`
  additiv um den optionalen Parameter `observability=None` und einen
  optionalen dritten Handler erweitert — einzige geänderte Zeile ist die
  Funktionssignatur, der gesamte bisherige Funktionskörper ist unverändert.
  75 neue Tests (Positiv/Negativ/Failure/Nebenläufigkeit/Integration/
  Contract/End-zu-Ende-Redaction), vollständige Suite 715/715 grün (640 +
  75), kein bestehender Test geändert. `git diff --check` leer, kein
  Cross-Workstream-Diff. Diagnoseskript bestätigt `client.log` (Datei-Sink)
  vorher/nachher byte-identisch (Exit 0). Evidence:
  `40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/`. **Kein Gate-PASS in diesem
  Run** — laut Work Package erfordert das Gate einen separaten Review.
- OBS-020 Gate Review abgeschlossen (2026-08-17, frische Session): **PASS**.
  Unabhängig gegen Repo-Zustand, `git diff`/`git status`, einen eigenständigen
  Testlauf, das Diagnoseskript und die Evidence geprüft (nicht nur gegen
  RESULT.md/RUN_LOG.md). `git diff --stat` bestätigt: einzige geänderte
  Produktdatei ist `core/logging_setup.py` (+23/-1, nur die Signaturzeile
  geändert, Funktionskörper byte-identisch), alles Übrige neu bzw. additiv
  in `core/observability/**`. Health-Zustandsmenge/-Snapshot, Wasserstand-
  /Prioritätsregel inkl. `not replayed`, Rekursionssperren G-1..G-7 und die
  Levelzuständigkeit wurden gegen `LOGGING_CONTRACTS_FREEZE_V1.md §6/§11.2`
  und `LOGGING_ARCHITEKTUR_FREEZE_V1.md §6.3/§7/§8.1/§8.2/§8.7` geprüft.
  Eigenständiger Testlauf: `-k obs020` 75/75 grün; volle Suite 714/715 grün —
  der eine Fehlschlag (`test_ap06_followup.py`, `lefx.interfaces` fehlt in
  dieser Prüfumgebung) ist nachweislich vorbestehend und außerhalb des Diffs
  (`git diff --stat` zeigt weder diese Testdatei noch `led_controller.py` als
  geändert), keine Regression von OBS-020. Diagnoseskript unabhängig erneut
  ausgeführt: Exit 0, `client.log` byte-identisch. `git diff --check` leer.
  Gesondert geprüfter Punkt aus dem Implementierungsbericht: „raw-Referenz
  ohne Kopie". Befund: **keine Verletzung**, und OBS-020 öffnet dafür
  **keinen neuen Pfad** — der einzige Ort, an dem OBS-020 `raw` berühren
  könnte (`observe_server_result` → `from_server_result`), ist in diesem
  Work Package nicht verdrahtet (Non-Scope, das ist OBS-040) und wird von
  keinem realen Aufrufer erreicht; der tatsächlich aktive Pfad
  (`UnifiedLogHandler` → `from_log_record`) setzt `raw` gar nicht. Die neu
  hinzugekommene, tatsächliche `queue.Queue` ändert daran nichts, weil die
  Unveränderlichkeit von `raw` nicht von der Verweildauer in der Queue
  abhängt, sondern von der bereits durch OBS-010 verifizierten rekursiven
  Neuaufbau-Garantie in `event_protocol._freeze_value`; `ARCH §8.2` fordert
  die Identitätsreferenz für `raw` ausdrücklich und weist Entfrieren/
  Serialisieren/Redigieren sowie die 64-KiB-Größengrenze explizit dem
  künftigen Worker zu (OBS-030, nicht OBS-020 fällig). Kein `FAIL`-Befund in
  keiner der Pflichtprüfungen. Readiness-Check OBS-030 (verbleibende Zeit
  genutzt, keine Implementierung begonnen): Voraussetzung „OBS-020 Gate
  PASS" jetzt erfüllt; `drain()` und alle vom künftigen Worker benötigten
  Health-Zähler sind bereits vorhanden und ungenutzt, `ObservabilityManager`
  existiert bewusst noch nicht.
- OBS-030 Implementierung abgeschlossen (2026-08-17, Run
  `RUN-OBS-030-01_2026-08-17_CLAUDE`): neu `core/observability/storage/sqlite.py`
  (`SQLiteLogStore`), `core/observability/sinks/jsonl_file.py` (`JsonlSink`),
  `core/observability/worker.py` (`LoggingWorker`),
  `core/observability/manager.py` (`ObservabilityManager`). Additiv erweitert:
  `core/observability/health.py` (`reset_drop_counters`, `record_written`,
  `record_deduplicated`), `core/observability/__init__.py` (vier neue
  Re-Exports), `app.py::main()` (Manager-Lebensdauer nach AR-5/AR-6:
  `AppConfig.load()` → Manager bauen/starten → `setup_logging(...,
  observability=...)`, `stop(2.0)` im `finally`, nach `run_gui`s internem
  `bridge.stop(10.0)`). `core/config.py` erhielt zusätzlich
  `LoggingObservabilityConfig` (`CONTRACTS §10.1`) inkl. der für die
  `app.py`-Verdrahtung selbst zwingend erforderlichen `_from_dict`-
  Sonderbehandlung (analog `history`) — ausdrücklich als minimale, für
  dieses WP notwendige Schnittstelle dokumentiert; die volle Settings-UI
  (Nachweis N-12) bleibt OBS-050. Während der Ausführung zwei reale Befunde
  behoben: das `ON CONFLICT`-Ziel eines partiellen Unique-Index braucht in
  SQLite dieselbe `WHERE`-Klausel wie der Index; ohne die
  `_from_dict`-Sonderbehandlung hätte `AppConfig.save()`→`load()` bestehende
  Roundtrip-Tests gebrochen (Details in `LOG_VERLAUF.md`). 82 neue Tests
  (`tests/test_obs030_*.py`, 7 Dateien), vollständige Suite 796/797 grün
  (715 Baseline + 82 neu; der eine Fehlschlag `test_ap06_followup.py`
  weiterhin vorbestehend/umgebungsbedingt [`lefx.interfaces` fehlt lokal]
  und außerhalb des Diffs), kein bestehender Test geändert. Nach `stop()`
  kein `RealtimeSTT-Observability`-Thread mehr aktiv (geprüft unter `pytest`
  **und** `unittest discover`). `git diff --check` leer, `git diff --stat`
  zeigt nur `app.py`, `core/config.py`, `core/observability/__init__.py`,
  `core/observability/health.py` als geänderte Bestandsdateien — kein
  Cross-Workstream-Diff. Evidence:
  `40_EVIDENCE/OBS-030/RUN-01_2026-08-17_CLAUDE/`. **Kein Gate-PASS in
  diesem Run** — laut Work Package erfordert das Gate einen separaten
  Review.
- OBS-030 Gate Review abgeschlossen (2026-08-17, frische Session,
  unabhängig): **FAIL**. Geprüft gegen Repository-Zustand, `git diff`/
  `git status`, eigenständige Testläufe und eigene Laufzeitproben, nicht
  gegen den Abschlussbericht. Belastbar nachgemessen und in Ordnung:
  Nebenläufigkeit (8 Producer-Threads × 1500 Records plus gleichzeitiger
  Leser mit `PRAGMA query_only = ON` → 12000 eingereiht = 12000 geschrieben
  = 12000 Zeilen, `integrity_check ok`, keine Drops, ~22 µs/`submit`, kein
  Thread-Leck), Shutdown-Buchhaltung (1000 = 20 geschrieben + 980
  `dropped_shutdown`, eine ratenbegrenzte stderr-Zeile, kein Thread übrig),
  Persistenz und Dedupe-Identität über Prozessläufe hinweg, Retention
  blockweise/zeitbudgetiert ohne `VACUUM`, Migration (`user_version = 99` →
  Nur-Lesen; Fehlschlag → Rollback), Prioritäts-/Wasserstandsregel exakt nach
  Freeze inkl. `not replayed`, kein Memory-Ringbuffer, Überlast sichtbar
  (genau ein Record `logging.records_dropped`). `git diff --check` leer,
  kein Cross-Workstream-Diff, kein bestehender Test geändert.
  **Blockierend:** (B-1) `LoggingWorker.run()` klammert `_iteration()` nicht
  in `try/except` — eine Ausnahme in der Schleife beendet den Worker still,
  `FAILED_WORKER`/`record_worker_error` haben null Produktionsaufrufer,
  Health meldet weiter `OK`, `submit()` liefert weiter `True`, und der
  `threading`-Excepthook schreibt einen unratenbegrenzten Traceback nach
  stderr (`ARCH §8.3`, `§8.1 G-2/G-4`, `§8.4`). (B-2) `CONTRACT_COVERAGE.md`
  behauptet genau dieses Verhalten als umgesetzt (Evidence-Konsistenz).
  (B-3) `db_path`/`file_sink_dir` außerhalb des Benutzerprofils werden
  akzeptiert (`CONTRACTS §4.3 P-8`). Weitere Befunde (W-1 defekter Store
  legt den intakten JSONL-Sink mit still, W-2 `logging.retention_pressure`
  nur als stderr statt als Record, W-3 bis W-7) im Gate-Review-Dokument.
  Kein Commit erstellt.
- OBS-030 Korrekturlauf abgeschlossen (2026-08-17, Run
  `RUN-OBS-030-02_2026-08-17`), Endstand nach Cleanup:
  **`OBS-030 CLEANUP COMPLETED – READY FOR INDEPENDENT RE-REVIEW`**.
  B-1 behoben — `LoggingWorker.run()` ist vollständig geklammert, eine
  Ausnahme im Schleifenrumpf wird gefangen, `worker_errors` steigt über den
  ratenbegrenzten, nicht propagierenden Notausgang (G-2/G-4) und die Schleife
  läuft weiter; erst nach fünf aufeinanderfolgenden Fehlern gibt sie
  endgültig auf, setzt `FAILED_WORKER` **vor** dem Flush (kein
  Neustartversuch, `ARCH §8.3`); `submit()` liefert ab da `False`,
  Queue-Reste werden als `dropped_shutdown` gezählt, und
  `dataclasses.replace(...)` liegt jetzt im `try`. Kein `threading`-Traceback
  erreicht stderr mehr an G-2/G-4 vorbei. B-2 behoben — korrigierte
  `CONTRACT_COVERAGE.md` in `RUN-02_2026-08-17`, dazu angehängte
  Korrekturvermerke an der RUN-01-Evidence; die Gate-FAIL-Historie ist
  unverändert. B-3 behoben — `db_path`/`file_sink_dir` werden gegen den
  aufgelösten Pfad geprüft (`validate()` **und**
  `ObservabilityManager._resolve_profile_path()`, weil `app.py::main()` kein
  `AppConfig.validate()` ruft); `..`, absolute Pfade außerhalb, relative,
  laufwerksrelative und UNC-Pfade werden abgelehnt. W-1 FIXED (Sink läuft
  unabhängig vom Store-Ergebnis, Reihenfolge nach `§11.1` unverändert),
  W-2 FIXED (`logging.retention_pressure` als kanonischer Record), W-3 NOT A
  DEFECT (Zählersatz `ARCH §7.3` eingefroren; Lücke ausdrücklich benannt),
  W-4 FIXED (`probe_write()` als leerer Testschreibvorgang), W-5 FIXED
  (`DISABLED`), W-6 DEFERRED nach OBS-050, W-7 FIXED (PRAGMA-Reihenfolge,
  Retentionstakt nach *geschriebenen* Records, `stop()` ohne Start zählt).
  47 neue Tests; `-k obs030` 129/129 grün unter `pytest` **und** `unittest`;
  volle Suite 843 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag
  (`lefx.interfaces`, außerhalb des Diffs, erneut verifiziert);
  `git diff --check` leer. Genau eine RUN-01-Testdatei angepasst
  (`test_obs030_config.py`, Pfadliteral widersprach P-8) — kein Test
  außerhalb von `tests/test_obs030_*.py` geändert. **Kein Commit** — der
  lokale Commit darf erst nach einem Gate-`PASS` entstehen.
- Cleanup desselben Runs (2026-08-17, Prompt `OBS-030_FIX_RUN_II.md`): Zwei
  Änderungen des Korrekturlaufs zurückgenommen, weil sie durch den Freeze
  nicht gedeckt waren. (1) Der Zähler `dropped_failed` ist vollständig
  entfernt — er war eine echte Erweiterung von `ARCH §7.3` („Zähler –
  eingefroren") und `CONTRACTS §11.2`; `LoggingHealthSnapshot` hat wieder
  exakt die eingefrorene Form, `core/observability/ingress.py` ist wieder
  unverändert gegenüber `HEAD`, `core/observability/health.py` wieder auf dem
  RUN-01-Stand `+21/-2`. Es wurde **kein** Ersatzzähler eingeführt und keine
  Abbildung auf vorhandene Zähler vorgenommen. (2) Der Nachtrag
  `DR-OBS-030-01` ist aus `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`
  entfernt; die Datei ist byte-identisch zum Stand vor dem Run — **kein
  normatives Dokument ist durch diesen Run verändert**. Die fachliche
  B-1-Korrektur bleibt vollständig bestehen (Fehlerisolation,
  `worker_errors`, `FAILED_WORKER`, kein Neustart, `submit() == False`,
  Zählen der Queue-Reste, kein `threading`-Traceback) und ist unverändert
  getestet. Vor dem Cleanup wurde die im Korrekturlauf ausgelassene
  Pflichtlektüre nachgeholt (`ARBEITSDATEIEN/README.md`, `AGENTS.md`,
  `MASTERPLAN.md`, `ARBEITSPROZESS.md`, Themen-`AGENTS.md`); daraus stammt
  auch die Einordnung „Fund → dokumentieren, nicht automatisch reparieren".
  Teststand unverändert: `-k obs030` 129/129, volle Suite 843 passed / 1
  vorbestehender Fehlschlag, `git diff --check` leer. Offen: die Auslegung
  von `ARCH §8.3` „nur verwerfen und zählen"
  (`40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md`, vom Gate zu
  entscheiden), die W-3-Lücke, die W-6-Auflage für OBS-050, der Ablageort von
  `LOGGING_V1_CHECKLISTE.md` (im Arbeitsbaum gelöscht vorgefunden,
  kanonischer Pfad wiederhergestellt) sowie die nachträglichen
  Korrekturvermerke in der RUN-01-Evidence, die laut Cleanup-Auftrag
  unverändert bleiben und dem Gate vorliegen.
**Stand:** 2026-08-17
