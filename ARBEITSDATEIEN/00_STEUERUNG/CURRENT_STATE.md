# CURRENT STATE

## Logging / Observability

- OBS-000: PASS
- OBS-010: GATE PASS (2026-08-17, unabhaengiger Review)
- OBS-020: GATE PASS (2026-08-17, unabhaengiger Review). Geprueft gegen
  Repository-Zustand, `git diff`/`git status`, eigenstaendigen Testlauf
  (`-k obs020` 75/75 gruen; volle Suite 714/715 gruen, der eine Fehlschlag
  `test_ap06_followup.py` nachweislich vorbestehend/umgebungsbedingt
  [`lefx.interfaces` fehlt lokal] und ausserhalb des Diffs), Diagnoseskript
  und Evidence. Gesondert geprueft: „raw-Referenz ohne Kopie" – keine
  Verletzung, kein neuer Pfad durch OBS-020 (`ARCH §8.2`-gedeckt, `raw` wird
  vom in OBS-020 aktiven Pfad gar nicht gesetzt; der einzige Pfad, der es
  koennte, ist unverdrahtetes OBS-040-Vorgriffsgeruest).
- Naechster Schritt: OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink
  (Implementierung, frische Session). Readiness geprueft: keine Blocker.

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
- Nächster Schritt: OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink
  (Implementierung, frische Session).
**Stand:** 2026-08-17
