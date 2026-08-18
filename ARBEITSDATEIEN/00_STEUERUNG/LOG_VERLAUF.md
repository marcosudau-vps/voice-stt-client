# Verlaufs-Log

## Hinweise / Beginn

- Vorher gab es eine Implementierungs-Serie mit Antigravity.  (Liegt unter "P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur")
- Das Ergebnis davon hatte schwerwiegende Lücken und vieles was geplant war nicht richtig umgesetzt.
- Da aber schon viel gute Arbeit dadurch vorhanden war, wurde darauf aufbauend eine Implementierungs-Serie mit Claude gestartet.
  in der geschaut werden sollte was übernommen wird und der Rest final fertig gestellt werden sollte.
- An dieser Stelle setzt dieser Ablauf-Log ein.
- Zeiten sind teilweise Schätzungen oder Rekonstruiert und können deshalb ungenau sein.

## Verlauf
  
- 14.08.2026 02:18, 001_VerbindlicherAusführungsauftrag_EinheitlicheServerseitigeTriggerarchitektur_UrsprünglicherAgyPrompt.md, 001_2026-08-14_Prompt.md
  - Beschreibung: Hier hat Claude das Übernommen und ausführliche Anweisungen zu der Vorgeschichte mit Anti-Gravity erhalten. Daraufhin Begann er mit der  Haupt-Implmentierungs-Phase.

- 14.08.2026 09:03, 002_2026-08-14_Prompt_Restarbeiten,_belastbareEndabnahme_und_vollständigeDokumentationsprüfung.md
  - Beschreibung: Die Ergebnisse nach der ersten Implementierungsphase sahen bereits so gut aus und die Tests waren alle grün, dass wir dachten, es wäre nur noch weniger   vervollständigende Restarbeiten und Vorbereitungen auf den Release-Push, z.B: Docs, letzte Nachweise, etc..

- 14.08.2026 15:56, Manueller Test
  - Beschreibung:
    Es wurde ein echter Test mit Hardware und Liveaufnahme gemacht.
    Dabei sind dann die Fehler der Claude-Implementierung aufgefallen.
    Zunächst war noch nicht klar, welchen Umfang sie haben.

- 14.08.2026 15:56, 003_CLAUDE_DIAGNOSEAUFTRAG_TRIGGERARCHITEKTUR.md
  - Beschreibung:
    Um herauszufinden, wie weit die Fehler in die Architektur greifen und wo überhaupt die Fehlerquellen sind oder ein Diagnoseauftrag gegeben.
    Der sollte erstmal analysieren, was los ist.Dabei kam heraus, dass die Änderungen bzw. Fehler tiefgreifender sind als ursprünglich gedacht und auch wirklich weit in die Architektur hineingehen.
    Alte Komponenten wurden entdeckt, die noch nicht komplett entfernt wurden.
    Ab diesem Zeitpunkt war klar, dass eine größere Umbauaktion noch erforderlich sein würde.

- 14.08.2026 16:43, 004_Opus-Sonderauftrag - Code-Only Architekturaufnahme vor Limit-Reset.md
  - Beschreibung:
    Als nächstes wurde jetzt ein Auftrag erteilt, um den Ist-Stand des tatsächlichen Codes zu analysieren.
    Es ging darum, festzustellen wo die Fehler-Schwerpunkte liegen und welche Komponenten wie stark betroffen sind.
    Es wurde explizit darauf geachtet, dass die Analyse nur am Code stattfindet und beispielsweise nicht die Dokumentation mit zur Rate gezogen wird, um ein realistisches Bild zu erhalten.

- 14.08.2026 23:00
  - Beschreibung:
    Nach Auswertung der Informationen zum Istzustand des Codes wurde analysiert, wo die Missverständnisse und falschen Interpretationen des Ziel-Zustandes aufgetreten sein könnten und welche Formulierungen gegebenenfalls nicht deutlich oder scharf genug waren.
    Es wurde daraufhin eine neue Fassung der Gesamtspezifikation und des Endgültigen Zielmodell's formuliert, In der die Aspekte, die mutmaßlich zum Missverständnissen geführt haben, nochmal deutlich hervorgehoben und klargestellt wurden.
    Es wurde begonnen einen grundlegenden Plan zur Migration aufzustellen. Dabei stand zuerst nicht der inhaltliche Teil im Fokus, sondern eher das methodische Vorgehen. Dazu wurden einige Planungsdateien erstellt, z.B. Checklisten.
  
- 14.08.2026 23:26, 005_2026-08-14_Prompt_LetzteGezielteArchitekturklarungVorPlanFreeze.md
  - Beschreibung:  
    Nach Sichtung der letzten Analyseergebnisse und einigen Beratungen wurden die Migrations-Schwerpunkte genauer untersucht.
    Es wurde dann herausgearbeitet, welche Informationen aus dem Code konkret noch fehlen.
    In diesem Auftrag ging es darum die letzten benötigten spezifischen Detailinformationen.Zu den Schwerpunkten zu erhalten.
    Im Laufe der Beratungen und der Planungen wurde beschlossen, dass es sinnvoll sei, vor der eigentlichen Migrationsarbeit noch ein Loggingmodul hinzuzufügen in einem seperaten Arbeitsprozess, da dies die Migration und den Arbeitsprozess dort deutlich erleichtern würde.
    Da ist schon eine konkrete Planung zu dem Loggingmodul gab, An die angeknüpft werden konnte.Musste das Logging-Modul einmal komplett mit der gesamten Architektur geplant werden und es wurde eine Zielspezifikation dafür formuliert.
     Diese soll jedoch nicht komplett vor der Migration umgesetzt werden, sondern es soll gesplittet werden in einen Teil der vorher kommt, der die Basics enthält, die erstmal für die Arbeit der Migration reichen.
    Ein anschließender Teil, in dem die Comfort Features dann noch hinzugefügt werden. Dieser soll aber erst nach der Migration umgesetzt werden.

- 15.08.2026, RUN-OBS-000-01_2026-08-15_CLAUDE, PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md
  - Workstream: OBS (Logging / Observability), Work Package: OBS-000 – Plan Freeze & Baseline
  - Ergebnis / Gate: **OBS-000 PASS**, zusätzlich **OBS-010 READY FOR IMPLEMENTATION** (Readiness-Review: PASS)
  - Beschreibung:
    Damit ist der Logging-Workstream aus der Planungsphase heraus. Die vorher verstreuten Grundlagen — die Zielspezifikation, die V1-Abgrenzung, die sieben Claude-Codeanalysen und das adversariale Review — sind zu einer einzigen, widerspruchsfreien Sollgrundlage zusammengeführt worden.
    Alle Architekturentscheidungen sind geschlossen; die einzige wirklich blockierende (der Paketname) ist zugunsten von `core/observability/` entschieden. Neunzehn Widersprüche zwischen den Quellen wurden benannt und aufgelöst, drei davon in diesem Lauf neu gefunden. Die letzte offene Informationslücke — ob die Client-Roadmap dem Logging-Plan widerspricht — ist geprüft und geschlossen: sie tut es nicht.
    Vier Entscheidungen weichen bewusst von einer ausdrücklich benannten Anforderung der Entwürfe ab und sind deshalb gesondert ausgewiesen. Die sichtbarste: der geplante Memory-Ringbuffer entfällt: die Live-Ansicht bleibt vollständig erhalten, wird aber als tailende Datenbankabfrage gebaut. Das spart eine Komponente und entkoppelt die Oberfläche vom Schreibprozess.
    Es wurde ausschließlich gelesen und geplant. Kein Produktcode, kein Testcode und keine Produktconfig wurden verändert, kein Commit gesetzt.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/30_AUSFUEHRUNG/runs/RUN-OBS-000-01_2026-08-15_CLAUDE/RUN_REPORT.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/40_EVIDENCE/OBS-000/`
  - Nächster Schritt: Arbeitsbaum des Clients festschreiben, danach OBS-010 umsetzen.

- 17.08.2026, Repository-/Workspace-Reorganisation und Baseline
  - Ergebnis / Gate: **Reorganisation abgeschlossen**, **Baseline-Commit erstellt**
  - Beschreibung:
    Der gesamte Workspace-Root wurde aus `marcosudau-vps` + `marcosudau-vps-worktrees`
    (mit parallelen Bereichen main / aktivem Trigger-Workspace / Antigravity-Referenz /
    manuellem Testbestand / Backups) in eine einheitliche Struktur unter
    `P:\GithubRepos\marcosudau-vps\<projekt>\{main,workspaces\einheitliche-triggerarchitektur}`
    überführt. Vorher wurde eine vollständige, validierte Vollsicherung angelegt
    (`P:\GithubRepos\_BACKUP_BEFORE_REORG_20260817\`); die ursprüngliche physische
    Struktur wurde danach unverändert (nicht gelöscht) nach
    `P:\GithubRepos\_LEGACY_BEFORE_REORG_20260817\` verschoben.
    Der aktive Client-Workspace liegt jetzt unter
    `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`.
    Die bereits begonnene ARBEITSDATEIEN-Migration wurde am neuen Pfad abgeschlossen:
    leere Alt-Ordner unter `docs/` entfernt, `docs/archive/..._VERWORFEN.md` nach
    `ARBEITSDATEIEN/90_HISTORIE/VOR_NEUEM_ARBEITSSYSTEM/archive/` verschoben. Der frühere
    Ordner `docs/2026-08-12_led-sound-debugfeedback` war über die Git-Historie dieses
    Repos nicht auffindbar und wurde daher nicht rekonstruiert (nur dokumentiert, kein
    OBS-010-Blocker). Anschließend genau ein lokaler Baseline-Commit
    ("chore: establish OBS-010 project baseline and work archive") auf dem technischen
    Vorgänger `5f2ee4bfceda2cec5bb6ddd0e8c28b2c6c371e1c` erstellt. Kein Push, kein Merge,
    kein Rebase, kein Tag, keine Produktcodeänderung.
  - Nächster Schritt: OBS-010 Implementierung.

- 17.08.2026, RUN-OBS-010-01_2026-08-17_DEEPSEEK, OBS-010_DEEPSEEK_IMPLEMENTIERUNGSAUFTRAG.md
  - Workstream: OBS (Logging / Observability), Work Package: OBS-010 – Canonical Model, Redaction, Normalizer & Contracts
  - Ergebnis / Gate: **OBS-010 IMPLEMENTED – READY FOR CLAUDE GATE REVIEW**
  - Beschreibung:
    Der freigegebene OBS-010-Scope wurde vollständig umgesetzt. Es entstehen
    ausschließlich neue Dateien: das Paket `core/observability/` (models.py,
    redaction.py, normalizer.py, ingress.py-Protokoll, storage/base.py,
    sinks/base.py, query/base.py) sowie 127 Contract-Tests unter
    `tests/test_obs010_*.py`. Kein bestehender Test und keine bestehende
    Produktdatei wurden geändert.
    Die drei Normalizer-Eingänge, die Redaction (R-3/8/9/10/11/12, `unfreeze`,
    hello-Whitelist R-6) und das kanonische Recordmodell entsprechen den
    eingefrorenen Verträgen (CONTRACTS §1–§4, §8; ARCH §5). Die zwei Pflicht-
    Mutationschecks (Redaction entfernen → rot, `unfreeze` entfernen → N-01 rot)
    wurden ausgeführt und belegt.
    Tests: vollständige Client-Suite 640 passed (513 Baseline + 127 neue), beide
    Runner grün; `git diff --check` leer; kein Commit/Push; Server-/LED-Repo
    unberührt. Evidence unter `40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/`,
    Run-Dokumentation unter `30_AUSFUEHRUNG/RUN-OBS-010-01_2026-08-17_DEEPSEEK/`.
  - Wichtigste Artefakte:
    - `core/observability/{models,redaction,normalizer,ingress}.py`
    - `core/observability/{storage,sinks,query}/base.py`
    - `tests/test_obs010_*.py` (7 Dateien)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/RUN-OBS-010-01_2026-08-17_DEEPSEEK/`
  - Nächster Schritt: Claude Review / Gate OBS-010 in frischer Session; danach OBS-020.

- 17.08.2026, OBS-010 Gate Review, `Prompts/OBS-010_GATE_REVIEW.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-010 – Canonical Model, Redaction, Normalizer & Contracts
  - Ergebnis / Gate: **OBS-010 GATE PASS – OBS-020 MAY PROCEED**
  - Beschreibung:
    Unabhängiger Review in frischer Session, gegen den tatsächlichen Repository-
    zustand, `git diff`/`git status`, einen eigenständigen Testlauf und die
    Evidence geprüft — nicht nur gegen `RUN_REPORT.md`. Feldliste/Typen/Defaults
    von `CanonicalLogRecord` stimmen exakt mit `CONTRACTS §1.1/§1.4` überein
    (inkl. Ausschlussliste); Prioritätsableitung (§1.5, inkl. `not replayed`),
    `scope`-Herleitung (§1.3, inkl. `led`/`other` → `instance`), die drei
    Normalizer-Eingänge (§3.1–§3.3, u. a. `LOGGER_CHANNEL_MAP`, `session_id`/
    `generation`/`segment_id` ausschließlich aus `record.__dict__`, `component`
    bei Controlframes fest `"eventstream"`) sowie Redaction R-1..R-12
    (`unfreeze`, hello-Whitelist R-6, Transkript-Zeichenzahl R-10, Tiefen-/
    Knotengrenze R-12) wurden Feld für Feld gegen den Code geprüft, nicht nur
    gegen die Test-Coverage-Tabelle. Eigenständiger pytest-Lauf: 640/640 grün
    (513 Baseline + 127 neu, isoliert `-k obs010`: 127/127); `git diff --check`
    leer; nur `core/observability/**` und `tests/test_obs010_*.py` neu, keine
    bestehende Produktdatei verändert. Diagnoseskript
    (`OBS-010_RUN-01_hello_redaction_diagnose.py`) unabhängig erneut ausgeführt:
    Exit 0, `accessToken` auf keiner Ebene im Ergebnis.
    Gesondert geprüfter Punkt aus dem Implementierungsbericht: „Server-`raw`
    ohne Kopie/Redaction im Normalizer". Befund: **keine Verletzung** der
    Immutability-/Non-Mutation-Anforderung. `models._freeze` gibt eine bereits
    als `MappingProxyType` übergebene `raw`-Payload unverändert per Identität
    zurück (kein rekursives erneutes Einfrieren) — das ist wörtlich durch
    `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.2` gefordert ("Der Ingress nimmt die
    bereits eingefrorene Referenz entgegen und kopiert nichts"). Verifiziert
    wurde zusätzlich am Code, dass `EventProtocolResult.payload`
    (`core/event_protocol.py::_freeze_value`, acht Aufrufstellen) beim Bau
    rekursiv **neue** `MappingProxyType`/`tuple`/`frozenset`-Objekte aus einer
    Dict-Comprehension erzeugt und nirgends die ursprüngliche mutierbare
    Struktur referenziert — es existiert also keine lebende, von außen
    mutierbare Referenz, über die eine spätere Mutation in den Record
    durchschlagen könnte. Für `details` bleibt es unabhängig davon bei einer
    echten Kopie/Neuaufbau (Redaction baut immer eine neue Struktur); für
    `from_client_event` existiert `raw` als Parameter ohnehin nicht. Damit ist
    „ohne Kopie" ein bewusster, vertragskonformer Performance-Entscheid und
    keine Lücke. Kein `FAIL`-Befund in keiner der Pflichtprüfungen (Contract-/
    Anforderungsabdeckung, Scope-Treue, Implementierungsqualität, Fehler-/
    Randfälle, Regressionen, Testqualität — Tests nutzen den echten
    `EventProtocolProcessor` und reale `test_event_protocol.py`-Fixtures statt
    reiner Testdoubles —, Evidence-Konsistenz, `git diff --check`, finaler
    Git-Status, keine unzulässigen Änderungen außerhalb des Work Packages).
    Readiness-Check OBS-020 (verbleibende Zeit genutzt, keine Implementierung
    begonnen): Voraussetzung „OBS-010 Gate PASS" jetzt erfüllt;
    `core/observability/ingress.py` enthält bislang nur das für OBS-020
    vorgesehene `Ingress`-Protokoll (kein `ObservabilityIngress`, kein
    `NullIngress`) und `core/logging_setup.py` ist unverändert — beides wie von
    WP-OBS-020 vorausgesetzt.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/` (erneut geprüft)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-010 Gate Review abgehakt)
  - Nächster Schritt: OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler (Implementierung, frische Session).

- 17.08.2026, RUN-OBS-020-01_2026-08-17_CLAUDE, `Prompts/OBS-020_IMPLEMENTIERUNGSAUFTRAG.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler
  - Ergebnis / Gate: **OBS-020 IMPLEMENTED – READY FOR REVIEW** (kein Gate PASS in diesem Run)
  - Beschreibung:
    Voraussetzung (OBS-010 GATE PASS) laut `CURRENT_STATE.md` erfüllt. Der
    freigegebene Scope wurde vollständig umgesetzt: `core/observability/health.py`
    neu (`LoggingHealthState`, `LoggingHealthSnapshot`, `LoggingInternalHealth`
    mit einem Lock für alle Zähler inkl. `deduplicated`, der eigene
    nicht-propagierende Logger `observability.internal` mit ratenbegrenztem
    Emergency-stderr-Kanal, G-2/G-4); `core/observability/ingress.py` additiv um
    `ObservabilityIngress` (`submit`/`observe_server_result`/`event`/`drain`,
    CONTRACTS §6, eine bounded Queue mit Wasserstandsregel bei 75 %),
    `NullIngress`, `NULL_INGRESS` erweitert — das OBS-010-`Ingress`-Protocol
    blieb unverändert; `core/observability/adapters/python_logging.py` neu
    (`UnifiedLogHandler` mit Wiedereintrittssperre G-1, Health-basiertem
    `handleError` G-3, No-Op `flush()`/`close()` G-7, internem-Logger-Filter);
    `core/logging_setup.py` additiv um den optionalen Parameter
    `observability=None` und einen optionalen dritten Handler erweitert.
    Einzige geänderte Zeile in `core/logging_setup.py` ist die
    Funktionssignatur (exakt der Sollzustand-Codeblock des Work Packages);
    der gesamte bisherige Funktionskörper ist byte-identisch erhalten.
    75 neue Tests über sechs Dateien (Positiv/Negativ/Failure/
    Nebenläufigkeit-und-Zeit/Integration/Contract sowie ein gesonderter
    End-zu-Ende-Nachweis, dass die OBS-010-Redaction durch die neue Pipeline
    unverändert wirkt — Secrets, nicht-sensible Struktur, Audio-Payload-Abwehr,
    Transkript-Policy, keine Mutation der Eingangsdaten). Vollständige
    Client-Suite danach 715/715 grün (640 Baseline + 75 neu), kein
    bestehender Test geändert. `git diff --check` leer; `git diff --stat`
    zeigt nur `core/logging_setup.py` als geänderte Produktdatei; kein
    Cross-Workstream-Diff. Ein eigenständiges Diagnoseskript lädt die
    Vor-Änderungs-Fassung von `core/logging_setup.py` direkt aus
    `git show HEAD:...` (ohne den Arbeitsbaum anzufassen) und bestätigt:
    `client.log` (Datei-Sink) ist mit und ohne den neuen `observability`-
    Parameter byte-identisch (Exit 0). Nebenläufigkeitsnachweis: acht Threads
    × 5000 Submits reconciliieren exakt, keine doppelten `record_id`; die
    100.000-Submits-bei-voller-Queue-Zeitmessung (~15,6–18,5 µs/Aufruf, zwei
    Läufe) ist als Regressionsbasis im Testprotokoll festgehalten, bewusst
    ohne absoluten Grenzwert (ARCH §6.3). Kein Commit, kein Push. Beobachtet,
    nicht behoben: ein vorbestehender, vom `observability`-Parameter
    unabhängiger `UnicodeEncodeError` des Stdout-Handlers unter einer
    `cp1252`-Konsole (außerhalb des WP-OBS-020-Scopes).
  - Wichtigste Artefakte:
    - `core/observability/health.py`, `core/observability/adapters/python_logging.py`
    - `core/observability/ingress.py`, `core/observability/__init__.py` (additiv erweitert)
    - `core/logging_setup.py` (additiv erweitert)
    - `tests/test_obs020_*.py` (6 Dateien, 75 Tests)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/Runs/RUN-OBS-020-01_2026-08-17_CLAUDE/`
  - Nächster Schritt: OBS-020 Gate Review (frische Session), danach OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink.

- 17.08.2026, OBS-020 Gate Review, `Prompts/OBS-020_GATE_REVIEW.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler
  - Ergebnis / Gate: **OBS-020 GATE PASS – OBS-030 MAY PROCEED**
  - Beschreibung:
    Unabhängiger Review in frischer Session, gegen den tatsächlichen
    Repository-Zustand, `git diff`/`git status`, einen eigenständigen
    Testlauf, das Diagnoseskript und die Evidence geprüft — nicht nur gegen
    `RESULT.md`/`RUN_LOG.md`. `git diff --stat` bestätigt: von den
    Produktdateien ist ausschließlich `core/logging_setup.py` geändert
    (+23/-1, einzige geänderte Bestandszeile ist die Funktionssignatur, der
    restliche Funktionskörper byte-identisch), alles Übrige unter
    `core/observability/{health.py, adapters/python_logging.py}` neu bzw.
    `ingress.py`/`__init__.py` additiv erweitert (unverändert seit OBS-010:
    das `Ingress`-Protocol, `models.py`, `redaction.py`, `normalizer.py`).
    Code Feld für Feld gegen `LOGGING_CONTRACTS_FREEZE_V1.md §6/§11.2` und
    `LOGGING_ARCHITEKTUR_FREEZE_V1.md §6.3/§7/§8.1/§8.2/§8.7` geprüft:
    Wasserstandsregel (75 %, `queue_size=8192`), Prioritätsregel inkl.
    `not replayed` (N-04 im Code nachvollzogen), `LoggingHealthState`
    (7 Zustände) und `LoggingHealthSnapshot` (alle Zähler inkl.
    `deduplicated`) exakt wie eingefroren, `UnifiedLogHandler` mit
    Wiedereintrittssperre (G-1), Health-`handleError` (G-3), No-Op
    `flush`/`close` (G-7) und Filter gegen `observability.internal`, Emergency-
    Kanal mit hartem Pro-Code-Ratenlimit (G-4) und `sys.stderr`-Abwehr (G-2).
    Eigenständiger pytest-Lauf: `-k obs020` → 75/75 grün; volle Suite →
    714/715 grün. Der eine Fehlschlag
    (`test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
    `ModuleNotFoundError: No module named 'lefx.interfaces'`) ist **keine
    Regression dieses Pakets**: `git diff --stat` zeigt weder
    `core/led_controller.py` noch `tests/test_ap06_followup.py` als geändert,
    die Datei ist eine vorbestehende, unveränderte Testdatei außerhalb des
    WP-OBS-020-Scopes, und der Fehler stammt aus einer in dieser
    Prüfumgebung unvollständigen `lefx`-Paketinstallation (fehlendes
    `lefx.interfaces`-Submodul), nicht aus dem geprüften Diff. Diagnoseskript
    (`OBS-020_RUN-01_client_log_before_after_diagnose.py`) unabhängig erneut
    ausgeführt: Exit 0, `client.log` vorher/nachher byte-identisch mit und
    ohne `observability`-Parameter. `git diff --check` leer (nur harmloser
    CRLF-Hinweis zu `LOG_VERLAUF.md`).

    Gesondert geprüfter Punkt aus dem Implementierungsbericht: „raw-Referenz
    ohne Kopie". Befund: **keine Verletzung** der Immutability-/
    Non-Mutation-Anforderung, und OBS-020 öffnet dafür **keinen neuen Pfad**.
    Der einzige Ort, an dem OBS-020 `raw` überhaupt berühren könnte, ist
    `ObservabilityIngress.observe_server_result` → `normalizer.from_server_result`
    (unverändert seit OBS-010) — dieser Pfad ist in OBS-020 selbst nicht
    verdrahtet (Non-Scope laut WP-OBS-020: "keine strukturierten
    Client-Hooks, das ist OBS-040") und wird von keinem realen Aufrufer
    erreicht. Der tatsächlich in OBS-020 aktive Pfad
    (`UnifiedLogHandler` → `normalizer.from_log_record`) setzt `raw`
    überhaupt nicht (kein `raw=`-Argument beim Bau des `CanonicalLogRecord`).
    Zusätzlich neu gegenüber OBS-010 geprüft: OBS-020 führt erstmals eine
    echte `queue.Queue` ein, in der ein Record — anders als in OBS-010 — nun
    unbestimmt lange liegen kann, bevor ein künftiger Worker (OBS-030) ihn
    entnimmt. Das ändert am Befund nichts, weil die Unveränderlichkeit von
    `raw` nicht von der Verweildauer in der Queue abhängt, sondern davon, dass
    `result.payload` bereits bei seiner Konstruktion in
    `core/event_protocol.py::_freeze_value` rekursiv aus frischen Objekten
    aufgebaut wird (durch OBS-010 bereits verifiziert, durch OBS-020
    unverändert) — es existiert keine lebende, von außen mutierbare Referenz
    auf die Ausgangsstruktur, unabhängig davon, wie lange das Objekt in der
    Queue wartet. `models._freeze` gibt eine bereits als `MappingProxyType`
    übergebene Referenz wörtlich normativ gedeckt durch
    `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.2` ("Der Ingress nimmt die bereits
    eingefrorene Referenz entgegen und kopiert nichts") unverändert per
    Identität zurück. `details` bleibt davon unberührt: `_redact`/`_freeze`
    bauen dafür immer eine neue Struktur, end-to-end bestätigt durch
    `test_obs020_redaction_end_to_end.py::TestNoMutationOfInputData`
    (eigenständig nachvollzogen). §8.2 hält zusätzlich fest, dass Entfrieren,
    Serialisieren und Redigieren von `raw` bewusst erst im künftigen Worker
    geschehen (inkl. der dort fälligen 64-KiB-Größengrenze) — das ist eine
    für OBS-030 vorgemerkte, keine für OBS-020 fällige Pflicht.

    Weitere Gate-Kriterien: Ingress bleibt rein beobachtend (kein
    Rückkanal in die Runtime-Autorität), Exceptions an der
    Handler-/Normalizer-Grenze sicher isoliert (kein `reject_event`- oder
    sonstiger Laufzeitfehler durch Logging-Fehler auslösbar), Health/Counter
    erzeugen keine Rekursion (G-1..G-4 durch Tests belegt, eigenständig
    nachvollzogen), Redaction entfernt Secrets/Tokens zuverlässig
    (`test_obs020_redaction_end_to_end.py`, eigenständig grün), keine
    Audio-Payloads (Quellcode-Scan der Hot-Path-Funktionen plus
    Abwehrtest), Transcript-Inhalt folgt der Policy in beiden Richtungen,
    strukturierte nicht-sensible Daten bleiben nutzbar, OBS-030 wurde nicht
    vorgezogen (kein Worker/Store/Sink/UI/Settings-Code; `drain()` ist
    vorhanden, aber nur für den künftigen Worker reserviert und in OBS-020
    ungenutzt). Kein `FAIL`-Befund in keiner der Pflichtprüfungen.

    Readiness-Check OBS-030 (verbleibende Zeit genutzt, keine Implementierung
    begonnen): Voraussetzung „OBS-020 Gate PASS" jetzt erfüllt.
    `ObservabilityIngress.drain(max_items, timeout)` sowie alle von einem
    künftigen Worker benötigten `LoggingInternalHealth`-Zähler
    (`written`, `deduplicated`, `store_errors`, `sink_errors`,
    `retention_errors`, `db_bytes`) sind bereits im Zählerschema vorhanden,
    aber unbenutzt — der `LoggingHealthSnapshot` muss beim Bau des Workers
    keine Formänderung mehr erfahren. `ObservabilityManager` (Kompositions-
    wurzel) existiert bewusst noch nicht, wie von WP-OBS-030 vorausgesetzt.
    Kleinere, für OBS-030 vorzumerkende Beobachtung (kein Blocker): Die
    64-KiB-Größengrenze für `raw` sowie das Entfrieren/Redigieren von
    Serverpayloads im Worker (`ARCH §8.2`) sind noch nirgends implementiert —
    laut Freeze normativ dem Worker zugewiesen, also fällig in OBS-030, nicht
    in OBS-020.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/` (erneut geprüft)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-020 Gate Review abgehakt)
  - Nächster Schritt: OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink (Implementierung, frische Session).

- 17.08.2026, OBS-030 Implementierung (`RUN-OBS-030-01_2026-08-17_CLAUDE`)
  - Beschreibung:
    OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink implementiert.
    Neue Module: `core/observability/storage/sqlite.py` (`SQLiteLogStore`:
    DDL/Migration/Indizes nach `CONTRACTS §5.2`, `write_batch` mit
    Replay-Dedupe über den partiellen UNIQUE-Index und `(eingefügt,
    dedupliziert)`-Rückgabe, `run_retention` blockweise/zeitbudgetiert,
    `clear()`, `measure_db_bytes()`), `core/observability/sinks/jsonl_file.py`
    (`JsonlSink`: `schemaVersion` zuerst, Tagesrotation, Größenlimit),
    `core/observability/worker.py` (`LoggingWorker`: dedizierter Daemon-
    Thread, Batching/Flush, raw-Redaction+64-KiB-Truncation **im Worker**
    nach `ARCH §8.2`, Retry-einmal-dann-verwerfen plus Circuit-Breaker bei
    5 aufeinanderfolgenden Fehlschlägen, `disk full` setzt `FAILED_STORE`
    und pausiert Retention, Backpressure-Zustandsübergänge `DROPPING`↔`OK`
    inkl. synthetischer `logging.records_dropped`/`logging.recovered`-
    Records nach `ARCH §7.3`/`G-6`, `request_clear` für „Diagnosehistorie
    löschen"), `core/observability/manager.py` (`ObservabilityManager` als
    Kompositionswurzel inkl. `_NullStore`-Fallback für `store_enabled=False`).
    Additiv erweitert: `core/observability/health.py`
    (`reset_drop_counters`, `record_written`, `record_deduplicated`,
    `record_dropped_shutdown` mit optionalem `count`), `core/observability/__init__.py`
    (vier neue Re-Exports), `app.py::main()` (Manager wird nach
    `AppConfig.load()` gebaut/gestartet, `setup_logging(...,
    observability=...)`, `stop(2.0)` im `finally`, nach `run_gui`s internem
    `bridge.stop(10.0)` — AR-5/AR-6). `core/config.py` erhielt zusätzlich
    `LoggingObservabilityConfig` (Schema nach `CONTRACTS §10.1`) und die
    zugehörige `_from_dict`-Sonderbehandlung analog `history` — als für
    diesen Run zwingend erforderliche minimale Schnittstelle (die
    `app.py`-Verdrahtung braucht eine echte Konfiguration), ausdrücklich als
    solche dokumentiert; die volle Settings-**UI**-Integration (Nachweis
    N-12) bleibt OBS-050.

    Während der Ausführung zwei reale Befunde behoben, nicht nur geplant:
    (1) `ON CONFLICT (producer_id, event_id) DO NOTHING` schlug gegen den
    partiellen Index fehl, bis die `WHERE event_id IS NOT NULL`-Klausel auch
    im `ON CONFLICT`-Ziel wiederholt wurde (SQLite-Pflicht bei partiellen
    Unique-Indizes als Arbiter). (2) Ohne die `_from_dict`-Sonderbehandlung
    für `logging.observability` brach `AppConfig.save()` → `AppConfig.load()`
    für **bestehende** Tests (`test_history.py`, `test_text_injector.py`,
    `test_feedback_mapping.py`, `test_ap06_followup.py::TestSettingsDialog`),
    weil `save()` das neue Feld vollständig serialisiert und der generische
    `_build`-Pfad die verschachtelte Dataclass nicht auflöst — behoben durch
    dieselbe Sonderbehandlung wie bei `history`, siehe `RUN_LOG.md` für die
    vollständige Herleitung.

    82 neue Tests (`tests/test_obs030_*.py`, 7 Dateien): SQLite-Store
    (DDL/Round-Trip/Dedupe/Migration/Retention/N-05-Fremdthread/
    Nebenläufiger-Leser/Neustart, 24), Worker (Ende-zu-Ende
    `logger.info -> SQLite`, Batching, HIGH-Sonderregel/N-04,
    Worker-/Store-/Sink-Fehler, raw-Redaction+Truncation, Retention-Kadenz,
    `request_clear`, Health-Zähler, Shutdown-Flush, Thread-Aufräumung, 20),
    JSONL-Sink (7), Manager (Lifecycle/Ende-zu-Ende/deaktiviert/
    Neustart-über-zwei-Instanzen, 8), Contracts/Isolation (11 + 10 Subtests),
    Config (Defaults/Validierung/Save-Load-Roundtrip, 10),
    App-Wiring (2). Vollständige Suite: 796/797 grün (pytest: 796 passed +
    1 vorbestehender Fehlschlag; `unittest discover`: 797 Tests, derselbe eine
    Fehlschlag) = 715 (Baseline nach OBS-020) + 82 neue. Kein bestehender Test
    geändert. Der eine Fehlschlag (`test_ap06_followup.py`, `lefx.interfaces`
    fehlt lokal) ist identisch zum vorbestehenden, dokumentierten
    Umgebungsbefund und außerhalb des Diffs. Nach `stop()` bleibt in keinem
    Test ein `RealtimeSTT-Observability`-Thread aktiv, geprüft unter `pytest`
    **und** `unittest discover`. `git diff --check` leer;
    `git diff --stat` zeigt ausschließlich `app.py`, `core/config.py`,
    `core/observability/__init__.py`, `core/observability/health.py` als
    geänderte bestehende Dateien — kein Cross-Workstream-Diff
    (`core/controller.py`, `core/session_coordinator.py`,
    `ui/application.py`, `ui/core_bridge.py` unverändert).

    **Kein Gate-PASS in diesem Run** — laut Work Package erfordert das Gate
    einen separaten Review.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-01_2026-08-17_CLAUDE/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-01_2026-08-17_CLAUDE/`
  - Nächster Schritt: OBS-030 Gate Review (frische Session, unabhängig).

- 17.08.2026, OBS-030 Gate Review, `Prompts/OBS-030_GATE_REVIEW.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Ergebnis / Gate: **OBS-030 GATE FAIL**
  - Beschreibung:
    Unabhängiger Review in frischer Session gegen den tatsächlichen
    Repository-Zustand, `git diff`/`git status`, eigenständige Testläufe und
    zusätzlich eigene Laufzeitproben — nicht gegen `RESULT.md`/`RUN_LOG.md`.
    Die Kernmechanik ist belastbar und wurde nachgemessen: Nebenläufigkeit
    (8 Producer-Threads x 1500 Records plus gleichzeitig pollender Leser mit
    `PRAGMA query_only = ON` → `enqueued = written = 12000 Zeilen`,
    `integrity_check ok`, keine Drops, ~22 µs/`submit`, kein Thread-Leck),
    Shutdown-Buchhaltung (1000 eingereiht = 20 geschrieben + 980
    `dropped_shutdown`, genau eine ratenbegrenzte stderr-Zeile, kein Thread
    übrig), Persistenz und Dedupe-Identität über Prozessläufe hinweg
    (identisches `(producer_id, event_id)` im zweiten Manager-Lauf →
    `deduplicated=1`, weiterhin eine Zeile), Retention blockweise/
    zeitbudgetiert ohne `VACUUM`, Migration (`user_version = 99` → Nur-Lesen,
    Fehlschlag → Rollback), Prioritäts-/Wasserstandsregel exakt nach Freeze
    inkl. `not replayed`, kein Memory-Ringbuffer, Überlast sichtbar (genau ein
    Record `logging.records_dropped` mit korrekten Zählern nach der Erholung).
    `git diff --check` leer; geänderte Bestandsdateien ausschließlich `app.py`,
    `core/config.py`, `core/observability/__init__.py`,
    `core/observability/health.py`; kein Cross-Workstream-Diff; kein
    bestehender Test geändert; `-k obs030` 82/82 grün im eigenen Lauf.

    **Drei blockierende Befunde:**
    (B-1) `LoggingWorker.run()` klammert `self._iteration()` nicht in
    `try/except`. Eigene Probe: eine Ausnahme in der Schleife beendet den
    Worker still, `LoggingHealthState.FAILED_WORKER` und
    `record_worker_error` haben null Produktionsaufrufer, Health meldet
    weiterhin `OK`, `Ingress.is_failed()` bleibt `False`, `submit()` liefert
    weiter `True`, Records stranden in der Queue — und Pythons
    `threading`-Excepthook schreibt einen vollständigen, unratenbegrenzten
    Traceback nach stderr, entgegen `ARCH §8.1 G-2/G-4` und `§8.4`. Verstoß
    gegen `ARCH §8.3` („Worker-Ausnahme in der Schleife") und gegen das
    Gate-Kriterium „interne Worker-/DB-Fehler bleiben isoliert". Zusätzlich
    liegt `dataclasses.replace(...)` in `_prepare_record` außerhalb des
    eigenen `try`.
    (B-2) `CONTRACT_COVERAGE.md` behauptet genau dieses Verhalten als
    umgesetzt und setzt die Health-Spalte auf „—" statt `FAILED_WORKER` —
    Verstoß gegen das Gate-Kriterium „Evidence-Konsistenz".
    (B-3) `LoggingObservabilityConfig.validate()` prüft `db_path` und
    `file_sink_dir` nur auf den Typ; der Manager übernimmt jeden absoluten
    Pfad ungeprüft. Nachweis: ein Pfad unter `C:\ProgramData\...` wird
    akzeptiert. `CONTRACTS §4.3 P-8` verlangt ausdrücklich „KEIN Pfad
    ausserhalb des Benutzerprofils akzeptiert"; OBS-030 ist das erste Paket,
    das diese Pfade tatsächlich auflöst und benutzt.

    Weitere, nicht allein gate-entscheidende Befunde: ein defekter Store legt
    den intakten JSONL-Sink mit still (`_write_sink` nur `if ok`, Probe: 0 von
    20 Zeilen); `logging.retention_pressure` entsteht nur als stderr-Zeile,
    nicht als Record (`§5.6`/`§12.4`); Records, die wegen ausgesetztem Store
    verworfen werden, sind nirgends gezählt; kein „leerer Testschreibvorgang"
    nach der 60-s-Pause; `LoggingHealthState.DISABLED` wird nie erzeugt;
    `clear_history()` blockiert den Aufrufer bis zu 5 s (für OBS-050
    vormerken). Vorbestehend und außerhalb des Diffs: neben dem bekannten
    `lefx.interfaces`-Fehlschlag ist
    `test_core_bridge.py::test_async_and_sync_commands_execute_in_worker_loop`
    intermittierend rot (Wartebedingung deckt die `local_feedback`-Zustellung
    nicht ab) — keine Regression dieses Pakets.

    Kein Commit erstellt (Gate FAIL).
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review **nicht** abgehakt)
  - Nächster Schritt: Korrekturlauf `RUN-OBS-030-02` (B-1, B-2, B-3 sowie
    Entscheidung zu W-1/W-2), danach erneutes unabhängiges OBS-030 Gate.
    OBS-040 darf nicht beginnen.

- 17.08.2026, OBS-030 Korrekturlauf, `Prompts/OBS-030_FIX_RUN.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Run: `RUN-OBS-030-02_2026-08-17`
  - Ergebnis / Gate: **OBS-030 CORRECTED – READY FOR RE-REVIEW**
    (kein Gate-PASS; der Gate-Punkt bleibt offen und wurde nicht abgehakt)
  - Beschreibung:
    Gezielter Korrekturlauf zu `OBS-030 GATE FAIL`. Grundlage waren die
    vollständig gelesenen Freeze-Dokumente, WP-OBS-030, der ursprüngliche
    Implementierungsauftrag, der tatsächliche Produktcode und das vollständige
    Gate-Review-Dokument einschließlich W-1 bis W-7 — nicht die
    Zusammenfassungen.

    **B-1 Worker-Fehlerisolation – behoben.** `LoggingWorker.run()` ist
    vollständig geklammert: `_open_store()`, der erste Retentionslauf und
    jeder `_iteration()`-Durchlauf liegen in eigenen `try/except
    Exception`-Blöcken (`BaseException` bewusst nicht, `ARCH §7.3`). Neues
    `_record_loop_failure` erhöht `worker_errors` über
    `LoggingInternalHealth.record_worker_error` und damit über den
    ratenbegrenzten, nicht propagierenden Notausgang (G-2/G-4); die Schleife
    läuft weiter. Erst nach fünf aufeinanderfolgenden Fehlern
    (`WORKER_FAILURE_THRESHOLD`) gibt sie endgültig auf — **kein
    Neustartversuch** (`ARCH §8.3`). Das neue `_finish()` setzt dann
    `FAILED_WORKER` **vor** dem Shutdown-Flush, sodass `Ingress.is_failed()`
    greift und kein Producer mehr ein `True` für einen strandenden Record
    bekommt; `submit()` verwirft **und zählt** (neuer Zähler
    `dropped_failed`, siehe DECISION REQUIRED); Queue-Reste werden als
    `dropped_shutdown` gezählt, notfalls über `qsize()`, wenn selbst `drain`
    defekt ist. `dataclasses.replace(...)` in `_prepare_record` liegt jetzt
    im `try`. Laufzeitprobe (Gegenstück zur Gate-Probe): Worker tot →
    `state = failed_worker`, `worker_errors = 6`, `submit()` → `[False×5]`,
    `dropped_failed = 5`, `dropped_shutdown = 1`, keine Traceback-Zeile auf
    stderr, nur `[observability] …`.

    **B-2 Evidence-Konsistenz – behoben.** Korrigierte
    `CONTRACT_COVERAGE.md` unter `RUN-02_2026-08-17`. Die RUN-01-Evidence und
    die Gate-FAIL-Historie wurden **nicht** gelöscht und **nicht**
    umgeschrieben; stattdessen tragen RUN-01-`CONTRACT_COVERAGE.md`,
    RUN-01-`TEST_RESULTS.md` und RUN-01-`RESULT.md` je einen angehängten,
    ausdrücklich gekennzeichneten Korrekturvermerk.

    **B-3 P-8 – behoben.** `LoggingObservabilityConfig.validate()` prüft
    `db_path` und `file_sink_dir` gegen den **aufgelösten** Pfad
    (`os.path.realpath` + `os.path.normcase`); `..`, absolute Pfade
    außerhalb, relative, laufwerksrelative und UNC-Pfade werden abgelehnt.
    Befund während der Ausführung: `app.py::main()` ruft **kein**
    `AppConfig.validate()`, weshalb `ObservabilityManager._resolve_profile_path()`
    die Prüfung zur Laufzeit wiederholt — ein abgelehnter Pfad wird nicht
    akzeptiert, benutzt wird der eingefrorene Standardort plus eine
    ratenbegrenzte stderr-Zeile. 23 Tests inkl. des im Gate genannten
    `C:\ProgramData\...`-Falls.

    **W-1 bis W-7 entschieden:** W-1 FIXED (Sink läuft unabhängig vom
    Store-Ergebnis; Reihenfolge Store→Sink nach `§11.1` unverändert),
    W-2 FIXED (`logging.retention_pressure` als kanonischer Record,
    `performance`/`WARNING`/`is_internal`, flankengesteuert, `§12.4`/`§5.6`/
    FD-D8), W-3 NOT A DEFECT (Zählersatz `ARCH §7.3` eingefroren, keine
    Normzeile verlangt ein Zählen; Lücke ausdrücklich benannt), W-4 FIXED
    (`SQLiteLogStore.probe_write()` als leerer Testschreibvorgang nach der
    60-s-Pause), W-5 FIXED (`DISABLED` bei `enabled=False`), W-6 DEFERRED
    nach OBS-050 (kein Qt-Aufrufer in OBS-030; Auflage O-03 notiert),
    W-7 FIXED (PRAGMA-Reihenfolge nach `§5.2`, Retentionstakt nach
    *geschriebenen* Records, `stop()` ohne Start zählt Queue-Reste).

    **DECISION REQUIRED `DR-OBS-030-01`:** Der Zähler `dropped_failed`
    erweitert `ARCH §7.3` und `CONTRACTS §11.2` additiv (letztes
    Snapshot-Feld mit Default). Grund: `ARCH §8.3` verlangt „verwerfen **und
    zählen**", der eingefrorene Zählersatz kennt dafür keinen Zähler, und
    eine Abbildung auf `dropped_watermark`/`dropped_queue_full` hätte den
    Record `logging.records_dropped` verfälscht. Offen ausgewiesen und in
    `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (neuer Abschnitt 11)
    nachgetragen — keine stille Planänderung.

    **Tests:** 47 neue Tests in drei Dateien
    (`test_obs030_worker_fault_injection.py` 6,
    `test_obs030_path_boundaries.py` 23, `test_obs030_gate_corrections.py`
    18). `-k obs030`: 129/129 grün unter `pytest` **und** `unittest`.
    `-k "obs010 or obs020 or obs030"`: 331 grün. Volle Client-Suite:
    843 passed / 1 Fehlschlag (`pytest`), `unittest discover` 844 Ran /
    1 error. `git diff --check` leer. Der eine Fehlschlag ist der
    vorbestehende, umgebungsbedingte `lefx.interfaces`-Fehler
    (`core/led_controller.py` außerhalb des Diffs, erneut verifiziert). Der
    vom Gate benannte intermittierende
    `test_core_bridge`-Befund trat nicht auf (fünf isolierte Läufe grün),
    bleibt vorbestehend und wurde bewusst nicht repariert.

    **Scope:** Geändert wurden `core/observability/{worker,storage/sqlite,
    manager,health,ingress}.py` und `core/config.py`.
    `core/observability/ingress.py` ist die einzige Datei außerhalb des
    RUN-01-Diffs; zwingender Grund ist dieselbe Zeile `ARCH §8.3`, die B-1
    einfordert („verwerfen **und zählen**"). Genau ein Test aus RUN-01 wurde
    geändert (`test_obs030_config.py`: das Pfadliteral `C:/tmp/obs-sink`
    widersprach P-8 direkt); kein Test außerhalb von `tests/test_obs030_*.py`
    wurde angefasst. Kein OBS-040, kein OBS-050, kein Refactoring ohne
    Gate-Bezug, kein Cross-Workstream-Diff.

    **Ablage-Auffälligkeit:** `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` war
    im Arbeitsbaum gelöscht, während im nicht versionierten
    `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` eine leere Zweitfassung
    liegt. Der kanonische Pfad wurde mit dem bisherigen Inhalt als Textdatei
    wiederhergestellt und fortgeschrieben (kein `git reset`, kein
    `git clean`); die Zweitfassung blieb unangetastet. Ein bewusster Umzug
    ist offen.

    Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (Abschnitt 11, `DR-OBS-030-01`, offen)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review weiterhin **nicht** abgehakt)
  - Nächster Schritt: erneutes unabhängiges OBS-030 Gate Review in frischer
    Session. OBS-040 darf nicht beginnen.

- 17.08.2026, OBS-030 Cleanup des Korrekturlaufs, `Prompts/OBS-030_FIX_RUN_II.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Run: `RUN-OBS-030-02_2026-08-17` (derselbe Run, nachgelagerter Cleanup)
  - Ergebnis / Gate: **OBS-030 CLEANUP COMPLETED – READY FOR INDEPENDENT
    RE-REVIEW** (kein Gate-PASS; der Gate-Punkt bleibt offen und ist nicht
    abgehakt)
  - Beschreibung:
    Eng begrenzte Rücknahme zweier Änderungen des Korrekturlaufs, die ich in
    der Stellungnahme zu den drei Prüfproblemen selbst als nicht eindeutig
    autorisiert bzw. als echte Contract-Erweiterung eingeordnet hatte. **Kein
    neuer Implementierungslauf, keine neue Architekturarbeit.**

    **Vorab nachgeholte Pflichtlektüre.** Der Korrekturlauf hatte
    `ARBEITSDATEIEN/README.md`, `ARBEITSDATEIEN/AGENTS.md`,
    `00_STEUERUNG/MASTERPLAN.md`, `00_STEUERUNG/ARBEITSPROZESS.md` und
    `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md` ausgelassen; sie sind vor
    diesem Cleanup vollständig gelesen worden (`START_HIER.md` existiert
    nicht; an seiner Stelle das Themen-`README.md`). Zwei Stellen sind
    unmittelbar einschlägig: die Scope-Regel des Themen-`AGENTS.md` („Neue
    Funde nicht automatisch reparieren. Fund → dokumentieren → Blocker?")
    und die Autoritätshierarchie mit `00_NORMATIV/` an der Spitze, zusammen
    mit `LOGGING_DECISIONS_FREEZE_V1.md §10`, dessen `DECISION
    REQUIRED`-Verfahren mit **`anhalten`** beginnt.

    **Korrektur 1 – `dropped_failed` vollständig zurückgenommen.** Entfernt
    aus `LoggingHealthSnapshot` (Feld), `LoggingInternalHealth`
    (Initialisierung, `record_dropped_failed()`, `snapshot()`-Argument) und
    aus `ObservabilityIngress.submit()`. `core/observability/ingress.py` ist
    damit wieder byte-identisch zu `HEAD` und aus dem Diff heraus;
    `core/observability/health.py` steht wieder auf dem vom Gate-Review
    festgehaltenen RUN-01-Stand `+21/-2`. Im Fault-Injection-Test wurde die
    Assertion auf `dropped_failed` durch die Prüfung ersetzt, dass
    abgewiesene Records den Queue-Füllstand nicht verändern; das Probeskript
    und die betroffenen Evidence-Aussagen sind entsprechend angepasst.
    **Kein Ersatzzähler**, und **keine** Abbildung auf `dropped_watermark`,
    `dropped_queue_full` oder `dropped_shutdown`.

    **Korrektur 2 – `DR-OBS-030-01` aus der Freeze-Datei entfernt.** Der vom
    Korrekturlauf angehängte Abschnitt 11 in
    `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` wurde vollständig entfernt;
    die Datei ist byte-identisch zum Stand vor `RUN-OBS-030-02`
    (`git diff`/`git status` für `00_NORMATIV/` leer). Umgesetzt als reine
    Textkürzung — kein `git reset`, kein `git checkout`, kein `git clean`,
    keine History-Aktion. Bestehende Entscheidungen der Abschnitte 1–10
    unverändert. **Damit verändert dieser Run kein normatives Dokument.**

    **Der Entscheidungsbedarf bleibt bestehen und wird nicht entschieden.**
    `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md` ist neu
    gefasst als offene Entscheidung mit Ausgangsproblem, der maßgeblichen
    Formulierung aus `ARCH §8.3` („nur verwerfen und zählen"), dem Konflikt
    mit dem eingefrorenen Zählersatz `ARCH §7.3` / `CONTRACTS §11.2`, beiden
    auslegbaren Lesarten, dem ausdrücklichen Hinweis, dass `dropped_failed`
    **nicht** Bestandteil des finalen Implementierungsstands ist, und dem
    Status „Entscheidung durch unabhängige Prüf-/Entscheidungsinstanz
    ausstehend".

    **B-1 bleibt vollständig bestehen.** Laufzeitprobe nach dem Cleanup:
    Worker tot → `state = failed_worker`, `worker_errors = 6`,
    `is_failed() = True`, `submit()` → `[False×5]`, Queue-Füllstand durch die
    abgewiesenen Submits unverändert, bereits eingereihter Record als
    `dropped_shutdown = 1` gezählt, keine Traceback-Zeile auf stderr (nur
    `[observability] …`), kein Observability-Thread übrig. Ebenso unverändert:
    B-3/P-8, W-1 (Sink-Unabhängigkeit), W-2
    (`logging.retention_pressure`), W-4 (`probe_write`), W-5 (`DISABLED`),
    W-7a/b/c.

    **Tests nach dem Cleanup:** Fault-Injection 6/6, `-k obs030` 129/129
    (`pytest` **und** `unittest`), `obs010+020+030` 331, volle Client-Suite
    843 passed / 1 vorbestehender `lefx.interfaces`-Fehlschlag außerhalb des
    Diffs, `unittest discover` 844 Ran / 1 error, `test_core_bridge` 3×
    grün, `git diff --check` leer. Die Testanzahl ist unverändert — es wurde
    kein Test entfernt, nur eine Assertion ersetzt.

    **Nicht angefasst:** die nachträglichen Korrekturvermerke in der
    RUN-01-Evidence (laut Cleanup-Auftrag ausdrücklich Gegenstand des
    unabhängigen Gate-Reviews), die historische Gate-FAIL-Evidence, die
    fachlichen B-1-/B-3-/W-Korrekturen und der bestehende RUN-02-Eintrag
    dieses Verlaufs (append-only).

    Zusätzlich aus der nachgeholten Pflichtlektüre umgesetzt: `RUN_REPORT.md`
    des Runs folgt jetzt der in `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`
    vorgeschriebenen Gliederung (Run-ID … Gate-Empfehlung, nächster Schritt);
    der fachliche Inhalt ist derselbe.

    Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/RUN_LOG.md` (Abschnitt 8: Cleanup)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md` (offene Entscheidung)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (**unverändert**, Nachtrag entfernt)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review weiterhin **nicht** abgehakt)
  - Nächster Schritt: erneutes unabhängiges OBS-030 Gate Review in frischer
    Session; dort auch über die offene Auslegungsfrage zu `ARCH §8.3`
    entscheiden. OBS-040 darf nicht beginnen.

- 17.08.2026, OBS-030 Gate Review II, `Prompts/OBS-030_GATE_REVIEW_II.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Ergebnis / Gate: **OBS-030 GATE PASS – OBS-040 MAY PROCEED**
  - Beschreibung:
    Zweiter unabhängiger Review in frischer Session über den gesamten
    OBS-030-Endstand seit dem letzten freigegebenen Commit `b363346` — also
    RUN-01, Gate-FAIL, Korrekturlauf `RUN-OBS-030-02` und Cleanup zusammen,
    nicht nur den letzten Diff. Geprüft wurde ausschließlich der tatsächliche
    Repositoryzustand: Code, `git diff`/`git status`, eigene Testläufe mit
    beiden Runnern, eigene Fault-Injection- und Laufzeitproben sowie ein
    Vergleichslauf gegen einen aus `b363346` frisch ausgepackten Baum. Die
    Abschluss-, Korrektur- und Cleanup-Berichte dienten als Hinweis, nicht
    als Nachweis.

    **B-1 geschlossen.** Eigene Fault-Injection: eine injizierte Ausnahme im
    Schleifenrumpf → Worker lebt, `worker_errors = 1`, Schleife verarbeitet
    weiter; vier aufeinanderfolgende Fehler mit anschließendem Erfolg →
    weiterhin `ok`; dauerhaft werfende Schleife → `failed_worker`,
    `worker_errors = 6`, `submit()` liefert `[False×5]`, Queue-Reste als
    `dropped_shutdown = 5` gezählt, `store.close()`/`sink.close()` gelaufen,
    kein Observability-Thread übrig und **kein** `Traceback` auf stderr,
    ausschließlich `[observability] …`-Zeilen. Ebenfalls geprüft:
    `_prepare_record`-Austrittspfad, `qsize`-, `run_retention`- und
    `store.open()`-Ausnahmen, `stop()` auf nie gestartetem Worker (7 von 7
    Records gezählt).

    **Schwelle `WORKER_FAILURE_THRESHOLD = 5` ausdrücklich geprüft und als
    normativ gedeckt begründet** — nicht wegen vorhandener Tests: `ARCH §8.3`
    regelt nur, *was* bei einem Schleifenabbruch geschieht, nicht *wann*;
    dieselbe Zeile liefert die Prämisse („ein Worker, der zweimal stirbt,
    stirbt beim dritten Mal auch"); die beobachtbare Semantik bleibt exakt
    die eingefrorene (`FAILED_WORKER`, kein Neustart, `FAILED`-Zweig aus
    `ARCH §5`); es entsteht kein Zähler, kein Zustand, kein Konfigfeld und
    keine DDL-Änderung.

    **B-2 geschlossen.** Alle prüfbaren Zahlen der RUN-02-Evidence wurden
    eigenständig reproduziert. Die Gate-FAIL-Evidence ist vollständig
    unverändert; kein Befund gelöscht oder verschleiert.

    **B-3 geschlossen.** P-8 gegen den real aufgelösten Profilpfad
    (`C:\Users\marco`) geprüft, für `db_path` **und** `file_sink_dir`, an der
    Config-Grenze **und** im produktiven Managerpfad: gültiger Profilpfad,
    absoluter Fremdpfad, `..`-Escape, Fremdprofil (inkl. Präfixfalle),
    Windows-Laufwerkspfad, UNC, laufwerksrelativ, relativ, leer sowie
    Separator-/Groß-Klein-/Doppelseparator-Normalisierung. Feindliche
    Konfiguration landet im eingefrorenen Standardort; `C:\ProgramData\…`
    wird nicht angelegt. P-9 belegt (`-wal`/`-shm` im selben Verzeichnis).

    **W-1 bis W-7 unabhängig nachgeprüft.** W-1: die Entkopplung von Sink und
    Store ist vertragstreu (`CONTRACTS §11.1` fixiert eine Reihenfolge, keine
    Bedingung; `O-05`); gemessen 20/20 Sinkzeilen bei degradiertem Store,
    Reihenfolge `['store', 'sink']`; die Abweisung bei `FAILED_STORE` ist
    durch das eingefrorene Komponentenbild `ARCH §5` gedeckt. W-2:
    `logging.retention_pressure` Feld für Feld aus der SQLite gelesen
    (Channel `performance`, Level `WARNING`, `observability.worker`,
    `is_internal`, flankengesteuert — bei 2600 Records genau ein Record).
    W-3: Lücke bestätigt und benannt, **kein** neuer Zähler verlangt.
    W-4: `probe_write()` kostet beim Resume 0 `write_batch`-Aufrufe.
    W-5: `disabled` bei `enabled=False`, `ok` bei `store_enabled=False`.
    W-6: zu Recht OBS-050. W-7a/b/c nachgemessen.

    **Entscheidung zu `ARCH §8.3` „nur verwerfen und zählen": Variante 1.**
    Die Frage ist aus dem bestehenden Freeze lösbar; ein neuer Zähler ist
    nicht erforderlich. Tragende Normstellen: `ARCH §5` friert die
    Ingressreihenfolge wörtlich ein und markiert das Zählen ausschließlich am
    Queue-voll-Schritt, während der `FAILED`-Zweig ein reines `return False`
    ist; `§8.3` definiert nirgends Zähler, sondern nennt sie beim Namen, wo
    es sie meint (`worker_errors++` in derselben Zeile, `dropped_shutdown`,
    `malformed++`) und kann daher gegen die als „eingefroren" überschriebene
    Liste in `§7.3` keinen neuen erzeugen; `§8.5 GRENZE 3` benennt den
    Totalverlust nach einem Workerausfall ausdrücklich als
    Architektureigenschaft und „keinen Mangel" und verweist auf den
    RotatingFileHandler als Rückfallebene. Was `§8.3` an Zählung nennt,
    geschieht nachweislich. **Kein Contract-Widerspruch, kein
    DECISION-REQUIRED-Bedarf für die Abnahme; der Reviewer hat keinen Zähler
    implementiert und keine Freeze-Datei angefasst.** Eine spätere
    autorisierte Entscheidung zugunsten der Gegenlesart bliebe möglich und
    gehört sinnvoll mit W-3 zu OBS-060.

    **Freeze-Integrität:** `git diff --stat HEAD -- 00_NORMATIV/` ist leer;
    alle vier Dateien sind byte-identisch zu `b363346`. `DR-OBS-030-01` kommt
    in `00_NORMATIV/` nirgends vor. `LoggingHealthSnapshot` hat wieder exakt
    die 16 Felder aus `CONTRACTS §11.2`, `LoggingObservabilityConfig` exakt
    die 14 Schlüssel aus `§10.1`, die DDL exakt `§5.2`; `ingress.py` ist
    unverändert gegenüber `HEAD`; kein `dropped_failed` im Repository.

    **Historische RUN-01-Evidence:** transparente, datierte und abgesetzte
    Korrekturvermerke; die beanstandeten Originalaussagen stehen wörtlich
    weiterhin da. Kein materielles Evidence-Problem.

    **Teststand:** `-k obs030` 129 passed (`pytest`) und `Ran 129, OK`
    (`unittest`), `obs010+020+030` 331 passed, volle Suite 843 passed /
    1 failed, `unittest discover` 844 Ran / 1 error, `git diff --check` leer.
    Der eine Fehlschlag wurde **gemessen** als vorbestehend nachgewiesen: im
    frisch aus `b363346` ausgepackten Baum 714 passed / derselbe eine
    `lefx.interfaces`-Fehlschlag; die Differenz 843 − 714 = 129 entspricht
    exakt den neuen OBS-030-Tests. Die früher beobachtete Flakiness in
    `test_core_bridge.py` trat in sechs isolierten Läufen und in keinem
    Volllauf auf.

    Nicht-blockierende Beobachtungen N-1 bis N-5 sind im Gate-Review
    dokumentiert (u. a. N-1: `logging.record_rejected` aus `ARCH §8.3` /
    `CONTRACTS §12.4` existiert nirgends im Code — Auslöser liegt im
    OBS-010/020-Normalizerpfad, nicht im OBS-030-Scope; für OBS-040/060).

    Genau ein lokaler Commit für den geprüften OBS-030-Endstand.
    Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/GATE_REVIEW.md`
    - dieselbe Ablage: `probe_gate2_b1_worker.py`, `probe_gate2_w_findings.py`, `probe_gate2_b3_paths.py`, `probe_gate2_e2e.py`, `probe_gate2_sink.py`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review jetzt abgehakt)
  - Nächster Schritt: OBS-040 – Server Live Adapter & Client Observation
    Hooks (Implementierung, frische Session). Readiness geprüft: keine
    Blocker. **OBS-040 MAY PROCEED.**

- 17.08.2026, OBS-040 Implementierung (`RUN-OBS-040-01_2026-08-17`),
  `Prompts/OBS-040_IMPLEMENTIERUNGSAUFTRAG.md`
  - Beschreibung:
    OBS-040 – Server Live Adapter & Client Observation Hooks implementiert.
    Voraussetzung geprüft: OBS-030 steht mit `GATE PASS – OBS-040 MAY
    PROCEED` in `CURRENT_STATE.md` und in der Checkliste.

    **Zwei neue Module**, beide in `ARCH §5.1` eingefroren vorgesehen:
    `core/observability/adapters/server_live.py` (`ServerLiveAdapter` – der
    passive Konsument des Fan-outs; fängt selbst nach `ARCH §7.3` Ebene 1,
    meldet an `LoggingInternalHealth`, fängt nie `BaseException`) und
    `core/observability/adapters/client_events.py` (`ClientEventEmitter` –
    die eine nie werfende Grenze, durch die jede Client-Hook-Aufrufstelle
    geht).

    **Fan-out-Hook** in `core/session_coordinator.py` nach `CONTRACTS §7.1`:
    `on_observation`, `_notify_observer` mit bewusst leerem
    `except Exception`, je **erste Anweisung** in `_handle_event` und
    `_handle_control`. Der Feedbackzweig läuft unverändert über `on_event`
    weiter – ein echtes Fan-out (O-02), kein Durchleiten.

    **Zweiter Beobachtungspunkt** (FD-R3, `CONTRACTS §7.5`): eine Zeile im
    `except`-Zweig von `EventStreamTransport.run()` →
    `client.eventstream.protocol_error`, ohne Rohframe.

    **42 Recordtypen aus `CONTRACTS §12`** über `ui/hotkeys.py`,
    `ui/core_bridge.py`, `ui/application.py`, `ui/led_feedback.py`,
    `ui/settings_dialog.py`, `core/audio_capture.py`, `core/stt_session.py`,
    `core/controller.py`, `core/text_injector.py`,
    `core/session_coordinator.py`, `core/event_stream.py` – umgesetzt in der
    von `§12.6` vorgeschriebenen Reihenfolge nach aufsteigendem Risiko, mit
    einem Testlauf nach jeder Stufe. Korrelationsketten: Trigger send/ack
    über `command_id` + `trigger:<cmd>`, Kommandos über `command:<cmd>`,
    Settings-Apply über `settings:<id>` von `apply_started` über
    `runtime_apply` bis `apply_completed`, Injection über
    `injection:<entryId>`.

    **Gate-Befund N-1 geschlossen:** `logging.record_rejected` existiert
    jetzt (`ingress.emit_record_rejected`), erzeugt an allen vier Stellen,
    die eine Normalizer-Ausnahme sehen können, mit Komponente und
    Ausnahmetyp und **ohne** Originaldaten; Health bleibt `OK`,
    `malformed++` – exakt die Zeile „Normalizer-Ausnahme" aus `ARCH §8.3`.

    **Hot Path und Aggregat nach `ARCH §8.6`:** die neun genannten
    Funktionen erhöhen ausschließlich `int`-Attribute (Quelltextnachweis über
    alle neun); der **Worker** liest sie über eine read-only-Registry am
    Ingress und erzeugt `client.audio.stream_stats`, Channel `performance`,
    Level `DEBUG`, höchstens alle 5 s und nur während aktiven Streamings. Die
    Registry ist der einzige Weg, der `§8.6` („der Worker liest die Zähler")
    und `§5.2` (Importrichtung) gleichzeitig hält.

    **Der wichtigste Nachweis (N-07) erbracht:** ein werfender Beobachter
    verändert weder den Rückgabewert von `_handle_event` noch den Cursorstand
    – gemessen mit dem **echten** `EventProtocolProcessor` und dem **echten**
    `EventCursorStore` auf einer temporären Datei, kein Double. Die vom Work
    Package verlangten Suiten `test_session_coordinator.py`,
    `test_event_stream.py`, `test_feedback_integration.py` und
    `test_trigger_feedback_contract.py` laufen unverändert grün.

    **Fünf reale Befunde während der Ausführung** (Details in `RUN_LOG.md`
    Abschnitt 5): der bestehende OBS-020-Hot-Path-Test hat einen Kommentar
    abgelehnt, der das Wort `ingress` enthielt (Kommentar umformuliert, nicht
    der Test); `run_headless`, `CoreBridge.apply_runtime_config` und die
    Transport-Factory des Coordinators sind durch bestehende Test-Doubles auf
    ihre alten Signaturen fixiert, weshalb der Ingress dort über
    Signaturinspektion bzw. die von `CONTRACTS §6` blessierte Default-Factory
    reist – bewusst **nicht** über `try/except TypeError`, das einen Aufruf
    doppelt ausgeführt hätte; `logging.record_rejected` ist nur defensiv
    erreichbar, weil der Normalizer konstruktiv nie wirft;
    `envelope["meldung"]` liegt auf der Envelope-Oberfläche, nicht in einem
    verschachtelten `extra`.

    **Neun Entscheidungen, alle aus dem bestehenden Freeze auflösbar, kein
    `DECISION REQUIRED`, keine Erweiterung eines eingefrorenen Vertrags.**
    Insbesondere **kein neuer Zähler** in `LoggingHealthSnapshot` – der
    Zählersatz aus `ARCH §7.3` ist unverändert und jetzt durch einen
    Contract-Test fixiert (die Lektion aus dem OBS-030-Cleanup zum
    zurückgenommenen `dropped_failed`). **Kein normatives Dokument ist durch
    diesen Run verändert**; `00_NORMATIV/` erscheint nicht in
    `git status --short`.

    **Teststand:** 115 neue Tests in sechs Dateien; `-k obs040` 115 passed
    (`pytest`) und `Ran 115, OK` (`unittest`); `obs010+020+030+040` 446
    passed; volle Suite 958 passed / 1 vorbestehender, umgebungsbedingter
    Fehlschlag (`test_ap06_followup.py`, `lefx.interfaces` fehlt lokal,
    außerhalb des Diffs), `unittest discover` Ran 959 / 1 error. Differenz
    zur Baseline (843) exakt die 115 neuen Tests. **Kein bestehender Test
    geändert.** `git diff --check` leer, `git diff --stat` 16 Dateien
    +1324/−57, kein Cross-Workstream-Diff. Ende-zu-Ende-Diagnoseskript mit
    echtem Manager, echtem SQLite-Store, echtem Protokollprozessor und
    echtem Cursorstore: P-1 bis P-7 alle PASS, exit 0 – darunter der Nachweis,
    dass 1000 Audiopakete **keine** Zeile erzeugen, das Worker-Aggregat aber
    schon, und dass in **keiner** gespeicherten Zeile das Session-Log-Token
    auftaucht, obwohl der `log.hello`-Payload es nachweislich enthielt.

    **Kein Gate-PASS in diesem Run** – laut Work Package erfordert das Gate
    einen separaten Review in frischer Session. Kein Commit, kein Push, kein
    Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-040-01_2026-08-17/` (`RUN_LOG.md`, `RESULT.md`, `OUTPUT_INDEX.md`)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-040/RUN-01_2026-08-17/` (`TEST_RESULTS.md`, `DIFF_SUMMARY.md`, `CONTRACT_COVERAGE.md`, `OBSERVATION_HOOK_MATRIX.md`, `SERVER_EVENT_MAPPING.md`, `probe_obs040_end_to_end.py`)
    - `core/observability/adapters/server_live.py`, `core/observability/adapters/client_events.py`
    - `tests/test_obs040_server_live_adapter.py`, `tests/test_obs040_fanout_hook.py`, `tests/test_obs040_client_hooks.py`, `tests/test_obs040_hot_path.py`, `tests/test_obs040_failure_isolation.py`, `tests/test_obs040_contracts.py`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-040 Implementierung jetzt abgehakt)
  - Nächster Schritt: OBS-040 Gate Review in frischer Session,
    `Prompts/OBS-040_GATE_REVIEW.md`. Offen für spätere Pakete:
    `apply_config` und die Manager-Übergabe an `DesktopApplication` (OBS-050,
    Befund N-4), N-2/N-3/W-3 und der Lauf gegen den echten Server (OBS-060).

- 17.08.2026, OBS-040 Gate Review (unabhängig, frische Session),
  `Prompts/OBS-040_GATE_REVIEW.md`
  - Ergebnis: **`OBS-040 GATE PASS – OBS-050 MAY PROCEED`**.
  - Beschreibung:
    Geprüft wurde ausschließlich der tatsächliche Repositoryzustand über dem
    Commit `cb0b81f`: Produktcode, `git diff`/`git status`, eigene Testläufe
    mit **beiden** Runnern, ein Vergleichslauf gegen einen frisch aus
    `cb0b81f` ausgepackten Baum (`git archive`) und zwei **eigene**
    Laufzeitproben. Die Abschlussberichte des Implementierungslaufs wurden als
    Hinweis gelesen und an keiner Stelle als Nachweis übernommen. Auflage
    dieses Laufs: keine Produktänderung, kein Commit, kein Push.

    **N-07 eine Ebene tiefer nachgemessen.** Der Implementierungslauf belegt
    ihn an `DualSessionCoordinator._handle_event`; dieser Review fährt den
    echten `EventStreamTransport._dispatch`, also die Stelle, die
    `confirm_event`/`reject_event` besitzt und deren `except BaseException`
    ein Event bei durchschlagender Ausnahme aktiv verwerfen würde. Aufbau ohne
    jedes Double (echter Prozessor, echter `EventCursorStore` auf temporärer
    Datei, echter Transport, echter Coordinator): ein werfender Beobachter
    wird genau einmal gerufen, das Ergebnis wird bestätigt, der Resume-Cursor
    steht identisch zum Lauf ohne Beobachter (5/5), keine Ausnahme verlässt
    den Dispatch, und der Feedbackzweig läuft unverändert. `asyncio.Cancelled
    Error` kommt durch — `Exception` wird gefangen, `BaseException` nirgends.

    **Eigenständig belegt, nicht nachgelesen:** unabhängiges Fan-out (der
    Beobachter sieht auch das vom Runtimepfad wegen Bindings-Mismatch
    verworfene Event, das Duplikat und die Controlframes, der Feedbackzweig in
    diesen drei Fällen nichts); Serverabbildung Feld für Feld nach
    `CONTRACTS §3.2` inkl. `component` aus dem Namensraumpräfix, `message` aus
    `extra["meldung"]`, `segment_id` als `int` und `generation` aus dem
    `SessionContext`; `raw` als Identitätsreferenz statt Kopie (`ARCH §8.2`);
    Replayidentität und Dedupe im echten `SQLiteLogStore` („die erste,
    live empfangene Fassung gewinnt", `deduplicated` steigt); **kein**
    Session-Log-Token in irgendeiner gespeicherten Zeile, obwohl der
    `log.hello`-Payload nachweislich zwei trägt, und `hello` nie `raw` (R-6);
    1000 Hot-Path-Inkremente → 0 Records bei genau einem Worker-Aggregat
    (`performance`/`DEBUG`); ein Ingress, dessen sämtliche Methoden werfen,
    stört den echten Dispatch nicht (O-05). Kein Beobachtungsthread bleibt
    übrig.

    Die sechs benannten Auslegungen A-1 bis A-6 und die drei
    Signaturinspektionen tragen; `inspect.signature` statt
    `try/except TypeError` ist die richtige Wahl, weil ein `TypeError` aus dem
    Inneren des Aufrufs einen Clientlauf bzw. ein Apply doppelt ausgeführt
    hätte. Der `session_coordinator.py`-Diff ändert zwei weitere bestehende
    Zeilen (Default-Transport-Factory) — offen benannt, durch `CONTRACTS §6`
    gedeckt und die kleinstmögliche Abweichung, weil sonst ein bestehender
    Test hätte geändert werden müssen (`ARCH §12`). Alle 57 Löschungen des
    Diffs einzeln durchgesehen: jede erscheint in geänderter Form wieder, kein
    Verhalten entfernt. Kein OBS-050/OBS-100+-Vorgriff, kein neues Konfigfeld,
    `00_NORMATIV/` byte-identisch zu `cb0b81f`, `git diff --check` leer, kein
    Cross-Workstream-Diff, kein bestehender Test geändert.

    **Teststand (eigene Läufe):** volle Suite 958 passed / 1 vorbestehender,
    umgebungsbedingter Fehlschlag (`test_ap06_followup.py`,
    `lefx.interfaces`); Vorbestand gegen den sauberen `cb0b81f`-Baum
    nachgewiesen (dort 843 passed / 1 identischer Fehlschlag), Differenz exakt
    die 115 neuen Tests. `-k obs040` 115/115 grün unter `pytest` (178
    Subtests) **und** `unittest`. Ende-zu-Ende-Probe des Runs unabhängig
    erneut ausgeführt: P-1 bis P-7 PASS, exit 0. Eigene Proben: 21 Prüfungen,
    alle PASS.

    **Befund F-1 (nicht die Implementierung betreffend).**
    `LOGGING_V1_CHECKLISTE.md` enthielt im Arbeitsbaum bereits **vor** diesem
    Review den Haken `- [x] OBS-040 – Gate Review` und einen
    Gate-PASS-Absatz, der mit „Ein lokaler Commit für den geprüften
    OBS-040-Endstand wurde erstellt" endet. `git log` widerlegt das: HEAD ist
    `cb0b81f` (OBS-030), ein OBS-040-Commit existiert nicht. Ebenso fehlten
    Gate-Evidence unter `40_EVIDENCE/OBS-040/`, ein Eintrag hier und ein
    Eintrag in `CURRENT_STATE.md`, das den Gate Review weiterhin als nächsten
    Schritt nannte. Der Eintrag stammt nicht aus `RUN-OBS-040-01`, dessen
    Berichte an fünf Stellen ausdrücklich „Kein Gate-PASS in diesem Run"
    sagen. Der Absatz ist durch das tatsächliche Ergebnis dieses Reviews
    ersetzt worden, ohne die falsche Commit-Behauptung und mit Hinweis auf den
    vorgefundenen Zustand; frühere Häkchen sind unverändert.

    **Sieben nicht-blockierende Beobachtungen N-1 bis N-7** im Gate-Review
    dokumentiert, darunter N-1 (`_enqueue_audio_packet` liest auf dem Hot Path
    zusätzlich `qsize()`, um das von `ARCH §8.6` selbst geforderte
    `max_send_queue_depth` führen zu können — unvermeidbar, aber nicht unter
    A-1…A-6 benannt) und N-2 (`RESULT.md` nennt 175 statt 178 Subtests).

    **Kein Commit erstellt.** Der Gate-Prompt sieht bei PASS genau einen
    lokalen Commit vor; für diesen Lauf war „keine Produktänderungen und kein
    Commit/Push" ausdrücklich angeordnet. Der Commit für den geprüften
    OBS-040-Endstand ist damit offen und bleibt einer ausdrücklichen Freigabe
    vorbehalten. Am Produktcode wurde nichts geändert.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-040/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
    - `.../GATE-REVIEW-01_2026-08-17_CLAUDE/gate_probe_obs040_independent.py` (14 Prüfungen)
    - `.../GATE-REVIEW-01_2026-08-17_CLAUDE/gate_probe_obs040_server_mapping.py` (7 Prüfungen)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (Gate-Absatz korrigiert, Befund F-1)
    - `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`
  - Nächster Schritt: **OBS-050 – Local Query, Log View & Settings**
    (Implementierung, frische Session,
    `Prompts/OBS-050_IMPLEMENTIERUNGSAUFTRAG.md`). Readiness geprüft: keine
    Blocker; offen und OBS-050-Scope sind `query/local.py`,
    `query/service.py`, `ui/logs/**`, die Settings-Einträge nach
    `CONTRACTS §10.3`, `apply_config` nach `§10.4` und die Übergabe des
    Managers an `DesktopApplication` (N-4).

- 17.08.2026, OBS-040 Abschlussvermerk (lokaler Gate-Checkpoint-Commit)
  - Nach ausdruecklicher Freigabe wurde genau ein lokaler Checkpoint-Commit
    fuer den gate-geprueften OBS-040-Endstand auf
    `feat/einheitliche-triggerarchitektur` erstellt: Produktstand, die 115
    OBS-040-Tests, die RUN- und Evidence-Unterlagen sowie das Gate-Review samt
    Probeskripten. Die bewusst unversionierten Prompt- und Pipeline-Dateien
    unter `30_AUSFUEHRUNG/` blieben unversioniert.
  - **OBS-040 ist damit vollstaendig abgeschlossen** — Implementierung,
    unabhaengiger Gate Review (`GATE PASS`) und lokaler Checkpoint.
  - **OBS-050 ist freigegeben** (`OBS-050 MAY PROCEED`); die Implementierung
    beginnt in einer frischen Session.
  - **Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**

- 17.08.2026, OBS-050 Implementierung (Run `RUN-OBS-050-01_2026-08-17`)
  - Ergebnis: **`OBS-050 IMPLEMENTED – READY FOR REVIEW`**. Kein Gate-PASS in
    diesem Run — das Work Package verlangt einen separaten, unabhaengigen
    Review in frischer Session.
  - **Query-Layer.** `core/observability/query/local.py`
    (`LocalLogProvider`) und `core/observability/query/service.py`
    (`LogQueryService`) schliessen die letzte Luecke der in `ARCH §5.1`
    eingefrorenen Modulstruktur. Eigene kurzlebige Leseverbindungen mit
    `PRAGMA query_only = ON` (nie `mode=ro`, W-13), Keyset-Pagination ueber
    `logs.id` nach `CONTRACTS §5.7`, `raw_json` grundsaetzlich nicht in der
    Listenabfrage, jeder Filterwert als Platzhalter. Drei getestete
    Eigenschaften tragen O-14: der Leser **legt die Datenbankdatei nie an**,
    er **wirft nie** (jeder Fehler ist ein Anzeigezustand) und er **laesst
    keine Verbindung offen**.
  - **Logansicht.** `ui/logs/**` mit den sechs eingefrorenen Modulen. Live und
    Historie sind **derselbe** Abfragepfad mit anderen Parametern: Historie
    `newest_first=True` mit `next_cursor`, Live alle 250 ms
    `newest_first=False` ab dem zuletzt gesehenen Cursor, `LIMIT 500`.
    **Kein Ringbuffer, kein Signal je Record** (FD-S1). Eigener
    `ThreadPoolExecutor(max_workers=1)`, ausdruecklich nicht ueber
    `CoreBridge`.
  - **Einstellungen.** Die neun Eintraege aus `CONTRACTS §10.3` im sechsten Tab
    „Logging & Diagnose", dazu „Diagnosehistorie loeschen" (am **Store**, ueber
    den Manager — nicht am Query-Provider, O-14) und „Logs anzeigen". Die
    Ownership-Domaenen sind getrennt: der Ingress wendet die vier Felder an,
    die er besitzt, die Kompositionswurzel den Handler-Level (`ARCH §8.7`: ein
    Konfigwert, zwei Filter), der Worker Retention, Anzahlgrenze und
    Datei-Sink auf **seinem eigenen** Thread. `store_enabled`/`db_path`
    bleiben `APP_RESTART` und werden zur Laufzeit nicht angewandt.
  - **Apply-Kette.** Eine Zeile in `core/controller.py::apply_runtime_config`
    an der von `§10.4` genannten Stelle. Die harte Regel ist **gemessen**: eine
    reine Observability-Aenderung erreicht eine Fake-Session, deren
    `reconfigure` durchfaellt, nicht — kein Reconnect, kein Audio-Neustart.
  - **Drei reale Befunde, alle behoben.** F-1: `.gitignore` verbarg mit der
    Regel `logs/` das gesamte neue Paket `ui/logs/` — der in `ARCH §5.1`
    eingefrorene Pfad der Logansicht; ohne Korrektur waere das Ergebnis dieses
    Work Packages nicht versionierbar gewesen und ein spaeterer Commit haette
    lautlos eine unvollstaendige Fassung enthalten (behoben mit einer
    begruendeten Negation `!ui/logs/`; die Regel fuer Laufzeitdaten bleibt
    wirksam). F-2: eine Abfrage, die schneller antwortet als `request_page`
    zurueckkehrt, veroeffentlicht synchron im aufrufenden Thread — die Seite
    verwarf dadurch ihre eigene frische Antwort als „veraltet" (behoben durch
    Reservierung der Anfrage-ID vor dem Absetzen). F-3: ein sofort
    zurueckkehrendes `shutdown()` liess eine laufende Abfrage in ein bereits
    zerstoertes `QObject` veroeffentlichen — in PySide6 eine
    Zugriffsverletzung (behoben durch `shutdown(wait=True)`).
  - **F-4 / bewusste Ablage.** Die neun Settings-Eintraege liegen in
    `core/logging_settings_metadata.py` statt in `core/settings_metadata.py`,
    weil `CONTRACTS §12.7` letzteres „bewusst rein" haelt und ein bestehender
    OBS-040-Contract-Test das prueft. `ARCH §12` verlangt in genau diesem Fall
    anzuhalten und die Architektur zu pruefen statt den Test zu aendern; das
    Ergebnis der Pruefung ist diese Trennung. `core/settings_metadata.py` ist
    byte-identisch geblieben. Das in `ARCH §5.1` ausgeschlossene Modul
    `ui/settings/logging_settings.py` entsteht **nicht**.
  - **Zehn Entscheidungen, alle aus dem bestehenden Freeze aufloesbar**: kein
    `DECISION REQUIRED`, **kein neuer Zaehler**, **kein neuer Recordtyp**
    (`§12` ist die verbindliche Liste — auch das Loeschen der Historie erzeugt
    bewusst keinen), kein neues Konfigurationsfeld, **kein normatives Dokument
    veraendert**.
  - **Teststand:** 170 neue Tests in fuenf Dateien, gruen unter `pytest`
    **und** `unittest`; volle Suite 1128 passed / 1 vorbestehender,
    umgebungsbedingter Fehlschlag (`lefx.interfaces`), dessen Vorbestand gegen
    einen frisch aus `91a7b7f` ausgepackten Baum nachgewiesen ist (dort 958
    passed / 1 identischer Fehlschlag; Differenz exakt die 170 neuen Tests).
    **Kein bestehender Test geaendert.** `git diff --check` leer, kein
    Cross-Workstream-Diff. Ende-zu-Ende-Diagnoseskript mit echtem Manager,
    echtem Store, echtem Query-Layer und echtem Qt-Fenster: **12/12 PASS,
    exit 0** — darunter 750 Zeilen paginiert waehrend der Worker
    weiterschreibt (keine Luecke, kein Duplikat), `raw` nur ueber `fetch_raw`,
    „Diagnosehistorie loeschen" mit 765 entfernten Zeilen bei nachweislich
    schreibmethodenfreiem Query-Layer, und drei Records, die **ohne geoeffnetes
    Fenster** geschrieben und von einem spaeter geoeffneten Fenster gezeigt
    werden.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-050-01_2026-08-17/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/RUN-01_2026-08-17/`
      (`TEST_RESULTS.md`, `DIFF_SUMMARY.md`, `CONTRACT_COVERAGE.md`,
      `QUERY_CASES.md`, `UI_ACCEPTANCE.md`, `probe_obs050_end_to_end.py`)
  - **Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**
  - Naechster Schritt: **OBS-050 Gate Review** (unabhaengig, frische Session,
    `Prompts/OBS-050_GATE_REVIEW.md`).

- 18.08.2026, `Prompts/OBS-050_GATE_REVIEW.md` — **OBS-050 Gate Review
  (unabhaengig, frische Session)**
  - Ergebnis: **`OBS-050 GATE FAIL`**. Evidence:
    `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/`
    (`GATE_REVIEW.md`, `gate_probe_obs050_ordering.py`,
    `gate_probe_obs050_live_happy_path.py`).
  - Geprueft wurde ausschliesslich der tatsaechliche Repositoryzustand:
    Produktcode, `git diff`/`git status`/`git diff --check`, eigene
    Testlaeufe mit beiden Runnern, ein Vergleichslauf gegen einen frisch aus
    `91a7b7f` ausgepackten Baum, das Diagnoseskript des Runs (unabhaengig
    wiederholt, 12/12 PASS, exit 0) und **zwei eigene Laufzeitproben gegen den
    echten Stack** — echter `SQLiteLogStore`, echter `LocalLogProvider`,
    echter `LogQueryService`, echtes Qt-`LogPage` (offscreen). Nicht die
    Abschlussberichte.
  - **Belastbar und in Ordnung:** der Query-Layer (kurzlebige
    Leseverbindungen mit `PRAGMA query_only = ON` statt `mode=ro`, Keyset ueber
    `logs.id`, `raw_json` nicht in der Listenabfrage, ausschliesslich
    Platzhalterbindung samt LIKE-Escaping, die Datei wird vom Leser nie
    angelegt, keine Verbindung bleibt offen, `query()` wirft nie, `status()`
    gecacht ohne I/O), die `LogQueryService`-Registry inkl. Failure-Isolation,
    die neun Settings-Eintraege nach `CONTRACTS §10.3` mit getrennten
    Ownership-Domaenen, die eine Zeile in `apply_runtime_config` nach `§10.4`,
    „Diagnosehistorie loeschen" am **Store** ueber den Manager (`FD-S4`,
    O-14), die Managerlebensdauer (`ARCH §6.2(b)`), die Importrichtung und
    „Logging laeuft ohne UI". `00_NORMATIV/`, `20_PLANUNG/` und
    `core/settings_metadata.py` byte-identisch zu `91a7b7f`, kein bestehender
    Test geaendert, volle Suite 1128 passed / 1 vorbestehender,
    umgebungsbedingter Fehlschlag; Baseline aus `91a7b7f` unabhaengig
    nachgemessen: 958 passed / 1 identischer Fehlschlag, Differenz exakt die
    170 neuen Tests.
  - **Blockierend ist ausschliesslich das Gate-Kriterium
    „Filter/Cursor/Sortierung verhalten sich deterministisch"** — nicht im
    Provider, sondern in der Ansicht `ui/logs/log_page.py`:
    - **B-1:** „Weitere laden" und das automatische Nachladen am Listenende
      haengen die umgekehrte, **aeltere** Folgeseite unten an; die Zeitspalte
      springt in der Mitte rueckwaerts. Reproduziert: erste Seite `r7…r11`,
      danach `r7…r11, r2…r6`.
    - **B-2:** startet der Live-Modus auf einer **leeren** Ergebnismenge
      (frische Installation, ein Filter auf den noch nichts passt, jeder
      Filterwechsel im Live-Modus), wird die erste aufsteigende Tail-Antwort
      im absteigenden Zweig verarbeitet: verkehrte Reihenfolge, und
      `_live_cursor` wird aus der **aeltesten** statt der juengsten Zeile
      gesetzt, sodass der naechste Tail dieselben Zeilen als Duplikate
      anhaengt. Reproduziert: `r4,r3,r2,r1,r0,r1,r2,r3,r4`. Der Normalfall —
      Live auf nicht leerer Ergebnismenge — ist korrekt und gegengeprueft.
  - Dazu W-1 (keine Tests fuer die Reihenfolge ueber zwei Seiten und fuer
    „Live auf leerem Store"; deshalb sind B-1/B-2 unentdeckt geblieben), W-2
    (`UI_ACCEPTANCE.md` A-11 „chronologisch dargestellt" gilt nur fuer die
    erste Seite) und sieben nicht blockierende Beobachtungen N-1 bis N-7.
  - Korrekturumfang: **eine** Produktdatei (`ui/logs/log_page.py`) plus zwei
    Tests in `tests/test_obs050_ui.py`. An Query-Layer, Settings, Apply-Kette,
    Manager und Worker ist nichts zu aendern.
  - **Kein Commit erstellt** (Commit nur bei `PASS`); HEAD unveraendert
    `91a7b7f`. **Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**
  - Naechster Schritt: **OBS-050 Korrekturlauf** fuer B-1 und B-2
    (einschliesslich W-1 und W-2), danach ein **erneuter unabhaengiger
    Gate-Review in frischer Session**. **OBS-060 darf nicht beginnen.**

- 18.08.2026, OBS-050 Gate Review (unabhaengig, frische Session)
  - Ergebnis: **`OBS-050 GATE FAIL`**. Geprueft wurde der tatsaechliche
    Repositoryzustand — Produktcode, `git diff`/`git status`/`git diff --check`,
    eigenstaendige Testlaeufe mit beiden Runnern, ein Vergleichslauf gegen einen
    frisch aus `91a7b7f` ausgepackten Baum, das Diagnoseskript des Runs und
    **zwei eigene Laufzeitproben gegen den echten Stack** — nicht die
    Abschlussberichte.
  - **In Ordnung**: Query-Layer (kurzlebige Leseverbindungen mit
    `PRAGMA query_only = ON`, Keyset ueber `logs.id`, `raw_json` nicht in der
    Liste, ausschliesslich Platzhalterbindung, LIKE-Escaping, die Datei wird vom
    Leser nie angelegt, keine Verbindung bleibt offen, `query()` wirft nie),
    Settings, Apply-Kette, Ownership-Trennung, Loeschfunktion am Store,
    Managerlebensdauer, Importrichtung, „Logging laeuft ohne UI", kein
    Ringbuffer, keine vorgezogenen Remote-/Admin-Funktionen.
  - **Blockierend**: das Gate-Kriterium „Filter/Cursor/Sortierung verhalten sich
    deterministisch" ist in der **Ansicht** nicht erfuellt. **B-1** —
    `_on_page_ready` drehte jede Historieseite um und hing die aeltere
    Folgeseite unten an; die sichtbare Zeitachse sprang an jeder Seitengrenze
    zurueck (`r7 … r11, r2 … r6`). **B-2** — die Art einer Antwort wurde aus
    `_live_cursor` statt aus der Anfrage bestimmt; nach einem leeren
    Ausgangsergebnis fiel die erste aufsteigende Tail-Antwort in den
    absteigenden Zweig, wurde umgedreht angezeigt und der Cursor aus der
    **aeltesten** Zeile gesetzt, worauf der naechste Tail dieselben Records
    erneut lieferte (`r4,r3,r2,r1,r0,r1,r2,r3,r4`). Dazu W-1 (Testluecke),
    W-2 (Evidenzformulierung) und sieben nicht blockierende Beobachtungen
    N-1 bis N-7.
  - Kein Commit erstellt; HEAD blieb `91a7b7f`.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`
    - `.../GATE-REVIEW-01_2026-08-18_CLAUDE/gate_probe_obs050_ordering.py`
    - `.../GATE-REVIEW-01_2026-08-18_CLAUDE/gate_probe_obs050_live_happy_path.py`
  - Naechster Schritt: OBS-050 Korrekturlauf fuer B-1 und B-2 (einschliesslich
    W-1 und W-2), danach ein erneuter unabhaengiger Gate-Review.

- 18.08.2026, OBS-050 Korrekturlauf (Run `RUN-OBS-050-02_2026-08-18`)
  - Ergebnis: **`OBS-050 CORRECTED – READY FOR RE-REVIEW`**. **Das Gate bleibt
    offen** — ein Korrekturlauf vergibt sein eigenes Gate nicht.
  - **Eigene Reproduktion vor jeder Aenderung.** Die unveraenderte Gate-Probe
    lief gegen den echten Stack und bestaetigte beide Befunde exakt
    (`FAILURES: 2`, exit 1); anschliessend wurden beide Ursachen am Code
    verifiziert.
  - **B-1 behoben** ueber die vom Gate ausdruecklich angebotene **Variante 1**:
    die Umkehrung je Historieseite entfaellt. Die Ansicht zeigt jede Seite so,
    wie der Provider sie geliefert hat (`newest_first=True`, neueste oben), und
    die aeltere Folgeseite gehoert damit folgerichtig nach unten. `_on_scrolled`
    bleibt unveraendert am unteren Rand — das eingefrorene „automatisches
    Nachladen am Listenende" (`CONTRACTS §9.3`) trifft so buchstaeblich die
    Stelle, an der die naechste Seite hingehoert. Die Keyset-/Cursor-Semantik
    des Providers ist unberuehrt. Variante 2 („Folgeseite oben einfuegen")
    haette den Nachladepunkt an den oberen Rand verlegt und entweder eine
    zweite Produktdatei oder einen Modell-Reset je Seite gebraucht, der Auswahl
    und Detailansicht verwirft.
  - **B-2 behoben**, indem die Semantik einer Antwort aus der **Anfrage** folgt:
    vier benannte Anfragearten, ein einziger Abfragetrichter `LogPage._issue`,
    der Anfrage-ID **und** Art in demselben Schritt festhaelt, eine Verzweigung,
    die die Art beim Verarbeiten **verbraucht** (eine wiederholte Zustellung
    bleibt folgenlos), und ein `_live_cursor`, der in beiden Live-Faellen aus
    der **juengsten** gelieferten Zeile stammt. Der fehlerhafte Zweig ist nicht
    repariert, sondern entfernt: die Fallunterscheidung kann gar nicht mehr aus
    dem Cursorstand entstehen. Keine neue Abfragearchitektur — dieselbe
    Provider-Schnittstelle, derselbe 250-ms-`QTimer`, derselbe
    `ThreadPoolExecutor(max_workers=1)`, kein Ringbuffer.
  - **Umfang**: produktseitig **ausschliesslich** `ui/logs/log_page.py`
    (456 → 526 Zeilen). Tests in `tests/test_obs050_ui.py` und — mechanisch
    bedingt, weil er den Quelltext von `_tail` liest —
    `tests/test_obs050_contracts.py`. Query-Layer, Settings, Apply-Kette,
    Manager, Worker, Tabellenmodell, Filterleiste, Detailansicht und Fenster
    sind unveraendert; `git diff --stat` zeigt fuer die versionierten
    Bestandsdateien exakt denselben Stand wie am Ende von RUN-01.
  - **W-1 geschlossen** mit neun Regressionstests, die die tatsaechliche
    UI-Verarbeitung ueber den echten `LogQueryController` samt Executor-Thread
    pruefen: Reihenfolge ueber drei Seiten, automatisches Nachladen am
    Listenende, Live-Start auf leerem Ergebnis, mehrere aufeinanderfolgende
    Tails, Filter ohne Treffer, Filterwechsel im laufenden Live-Modus,
    befuellter Normalfall und die Antwortzuordnung. Zwei RUN-01-Erwartungen,
    die das fehlerhafte Verhalten festgeschrieben hatten, sind richtiggestellt.
    **W-2** ist in `40_EVIDENCE/OBS-050/RUN-02_2026-08-18/UI_ACCEPTANCE.md`
    behandelt (A-11 bis A-13 neu formuliert, A-34 bis A-42 ergaenzt);
    RUN-01- und Gate-FAIL-Evidence bleiben unveraendert erhalten.
  - **Teststand**: 170 → **179 OBS-050-Tests**, gruen unter `pytest` **und**
    `unittest`; OBS-010…050 625 gruen; volle Suite 1137 passed / 1
    vorbestehender, umgebungsbedingter Fehlschlag (`lefx.interfaces`), dessen
    Lage **ausserhalb des Diffs** fuer diesen Lauf erneut nachgemessen ist
    (weder `tests/test_ap06_followup.py` noch `core/led_controller.py` liegen im
    Diff; derselbe Test schlaegt im frisch ausgepackten `91a7b7f`-Baum identisch
    fehl). Laufzeitproben: `probe_obs050_ordering_fix.py` 8/8 und
    `probe_obs050_end_to_end.py` 12/12, beide exit 0. Die unveraenderte
    Gate-Probe meldet fuer B-2 jetzt `ascending: True, duplicates: False`; fuer
    Fall A meldet sie erwartungsgemaess `False`, weil sie hart auf
    *aufsteigende* Monotonie prueft, die Tabelle nach Variante 1 aber
    durchgehend absteigend ist — der richtungsbewusste Ersatznachweis und die
    Einordnung stehen in `FIX_SUMMARY.md` Abschnitt 1.3.
  - `git diff --check` leer, HEAD unveraendert `91a7b7f`.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-050-02_2026-08-18/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/RUN-02_2026-08-18/`
      (`FIX_SUMMARY.md`, `TEST_RESULTS.md`, `UI_ACCEPTANCE.md`,
      `probe_obs050_ordering_fix.py`)
  - **Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.** Die
    acht bewusst unversionierten Prompt- und Pipeline-Eintraege unter
    `30_AUSFUEHRUNG/` sind unangetastet.
  - Naechster Schritt: **erneuter unabhaengiger OBS-050 Gate Review** in
    frischer Session. **OBS-060 nicht beginnen.**

- 18.08.2026, `Prompts/OBS-050_GATE_REVIEW.md` (Re-Review-Auftrag) —
  **OBS-050 Gate Review II (gezielter Re-Review des Korrekturlaufs)**
  - Ergebnis: **`OBS-050 GATE PASS – OBS-060 MAY PROCEED`**. Evidence:
    `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/GATE-REVIEW-02_2026-08-18_CLAUDE/`
    (`GATE_REVIEW.md`, `gate2_probe_obs050_b1_b2.py`).
  - **Kein vollstaendiger neuer Gate-Review.** Die im ersten Gate bestandenen
    Bereiche wurden nicht erneut auditiert, weil sie nachweislich unveraendert
    sind: der versionierte Anteil ist **stat-identisch** zum ersten Gate (zehn
    Dateien, +475/−25), und nach Aenderungszeitpunkt sind allein
    `ui/logs/log_page.py`, `tests/test_obs050_ui.py` und
    `tests/test_obs050_contracts.py` beruehrt. RUN-01-Evidence und die
    Gate-FAIL-Evidence sind unangetastet; W-2 ist in einer eigenen
    RUN-02-Datei richtiggestellt statt durch Ueberschreiben.
  - **B-1 geschlossen.** Die gewaehlte **absteigende** Historiedarstellung ist
    normativ gedeckt (`CONTRACTS §5.7` friert `ORDER BY id DESC` und
    `AND id < :after_id` ein, `§8` `newest_first=True` als Default, `§9.3`
    verlangt das Nachladen am **Listenende** — mit absteigender Anzeige genau
    der aeltere Rand). Eine aufsteigende Historieanzeige wird nirgends
    gefordert; die gegenteilige Erwartung der ersten Gate-Probe ist damit
    aufgehoben, **ohne neue Contract-Entscheidung**. Eigene Laufzeitprobe ueber
    **fuenf** Seiten: streng absteigend, kein Richtungsbruch, keine Duplikate,
    keine Auslassungen, letzte Seite ohne Folgecursor; automatisches Nachladen
    ueber das echte Scrollbar-Ereignis mit demselben Ergebnis. Provider- und
    Keyset-Cursor unveraendert. Richtung jetzt: **Historie absteigend (neueste
    oben), Live aufsteigend (neueste unten)** — jeweils die Richtung der
    eingefrorenen Abfrage, in der Statuszeile benannt.
  - **B-2 geschlossen.** Jede Abfrage laeuft durch den einen Trichter
    `LogPage._issue(kind, …)`, der Anfrage-ID **und** Anfrageart in demselben
    Schritt festhaelt; `_on_page_ready` verzweigt darueber und verbraucht sie.
    Die Ableitung aus `_live_cursor` existiert nicht mehr, der Cursor stammt in
    beiden Live-Faellen aus der **juengsten** Zeile. Nachgemessen: Leerstart
    bleibt leer, erster Tail aufsteigend und duplikatfrei, Cursor auf dem
    neuesten Record, Folgetails setzen dahinter fort, Filter ohne Treffer und
    Filterwechsel im Live-Modus korrekt, befuellter Normalfall unveraendert,
    und ein absichtlich vergifteter `_live_cursor` aendert die Deutung einer
    Antwort nicht mehr (15/15 PASS, exit 0).
  - **Tests:** neun neue, die vollstaendige Anzeigesequenzen ueber den echten
    `LogQueryController` pruefen und **W-1** genau dort schliessen, wo B-1
    durchgerutscht war; das Double `FakeService` ist unveraendert. Die
    Aenderung in `tests/test_obs050_contracts.py` bildet nur den neuen
    `_issue`-Trichter ab und **schwaecht keine Contract-Anforderung ab** —
    dieselbe Zusicherung an beiden Enden geprueft, plus eine strukturelle
    Verschaerfung.
  - **Regression:** `-k obs050` **179/179** unter `pytest` **und** `unittest`;
    volle Suite 1137 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag
    (`lefx.interfaces`, ausserhalb des Diffs). Ein in einem von drei
    Vollaeufen zusaetzlich auftretender Fehlschlag
    (`test_ui_widgets.py::TestTranscriptOverlay::test_realtime_replaces_text_and_final_fades`)
    ist als **lastabhaengig flatterhaft, nicht als Regression** eingeordnet:
    zwei weitere Vollaeufe gruen, die Datei allein zweimal gruen, Testdatei und
    `ui/overlay.py` vom 2026-08-14 und damit ausserhalb von RUN-01 und RUN-02.
    `git diff --check` leer.
  - Die nicht blockierenden Beobachtungen N-1 bis N-7 des ersten Gates bleiben
    fuer OBS-060 vorgemerkt.
  - **Genau ein lokaler Commit** fuer den gate-geprueften OBS-050-Endstand
    erstellt: `feat(observability): complete OBS-050 local log view` auf
    `feat/einheitliche-triggerarchitektur`, mit Produktstand, den 179
    OBS-050-Tests, den RUN-01-/RUN-02-Unterlagen, der OBS-050-Evidence und
    beiden Gate-Reviews samt Probeskripten. Die **acht** bewusst
    unversionierten Prompt- und Pipeline-Eintraege unter `30_AUSFUEHRUNG/`
    sind **nicht** aufgenommen. **Kein Push, kein Merge, kein Rebase, kein
    Tag, kein PR.**
  - Naechster Schritt: **OBS-060 – V1 Hardening, Evidence & Baseline –
    Implementierung** (`Prompts/OBS-060_IMPLEMENTIERUNGSAUFTRAG.md`, frische
    Session). In diesem Lauf nicht begonnen.
