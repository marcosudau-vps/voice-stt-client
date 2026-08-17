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
