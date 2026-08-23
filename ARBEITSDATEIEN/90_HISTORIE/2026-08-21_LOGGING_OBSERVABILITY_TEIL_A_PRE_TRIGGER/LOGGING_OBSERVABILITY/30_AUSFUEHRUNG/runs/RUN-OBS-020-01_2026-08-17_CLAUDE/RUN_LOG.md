# RUN_LOG — RUN-OBS-020-01_2026-08-17_CLAUDE

Auftrag: `30_AUSFUEHRUNG/Prompts/OBS-020_IMPLEMENTIERUNGSAUFTRAG.md`
Session-Root: `P:\GithubRepos\marcosudau-vps`
Schreibbarer Bereich: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Agent: Claude (Sonnet 5)
Datum: 2026-08-17

## 0. Voraussetzung geprüft

`CURRENT_STATE.md`: "OBS-010: GATE PASS (2026-08-17, unabhaengiger Review)" —
dokumentiert unter "Aktueller organisatorischer Schritt" mit Prüfumfang
(Feldliste, Prioritätsableitung, Wertemengen, Normalizer-Eingänge, Redaction
R-1..R-12, Query-/Storage-/Sink-Protokolle, 640/640 grün, `git diff --check`
leer). Voraussetzung erfüllt — Implementierung freigegeben.

## 1. Gelesen (vor Beginn)

- `ARBEITSDATEIEN/README.md`, `AGENTS.md`
- `00_STEUERUNG/CURRENT_STATE.md`, `MASTERPLAN.md`, `ARBEITSPROZESS.md`
- `10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md`
  (vollständig)
- `10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md`
  (vollständig)
- `10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`
  (FD-D9, FD-R1, FD-R5, FD-R8, Abschnitt 8 Work-Package-Abbildung)
- `20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-020_INGRESS_HEALTH_REDACTION.md`
  (kanonisches Work Package, `authority: planning`, `status: READY`)
- OBS-010-Evidence (`40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/*`) als
  Formatvorbild
- Bestehender Code: `core/observability/{models,redaction,normalizer,ingress,__init__}.py`,
  `core/logging_setup.py`, `tests/test_obs010_*.py`

## 2. Scope-Abgleich gegen WP-OBS-020

Verbindlicher Scope laut Work Package:

- `core/observability/ingress.py` — `ObservabilityIngress`, `NullIngress`,
  `NULL_INGRESS` (das `Ingress`-Protocol aus OBS-010 blieb unverändert
  erhalten, die konkreten Klassen wurden ergänzt)
- eine bounded `queue.Queue` (Default 8192) mit Wasserstandsregel bei 75 %
- `core/observability/health.py` — `LoggingHealthState`,
  `LoggingHealthSnapshot`, `LoggingInternalHealth`, Emergency-stderr
- `core/observability/adapters/python_logging.py` — `UnifiedLogHandler`
- `core/logging_setup.py` — additiv: optionaler Parameter
  `observability=None`, optionaler dritter Handler

Non-Scope eingehalten: kein Worker, kein Store, kein Sink, keine UI, keine
Settings, keine Änderung an Datei-/Stdout-Handler-Verhalten, keine
strukturierten Client-Hooks (OBS-040), kein `report_local_feedback`, kein
`CanonicalEventType`, keine `FeedbackEngine`-Nutzung (Regel G-5).

## 3. Implementierungsschritte (in Ausführungsreihenfolge)

1. `core/observability/health.py` neu angelegt: `LoggingHealthState` (7
   Zustände, CONTRACTS §11.2), `LoggingHealthSnapshot` (frozen dataclass, alle
   Zähler inkl. `deduplicated`, FD-R5), `LoggingInternalHealth` (ein
   `threading.Lock` für alle Zähler, Implementierungsschritt 4), der eigene
   nicht-propagierende Logger `observability.internal` mit
   `_EmergencyStreamHandler` (liest `sys.stderr` bei jedem `emit()` neu,
   schluckt jede Ausnahme, G-2) und `_RateLimiter`/`emergency()` (harte
   Ratenbegrenzung: höchstens eine Zeile je Code und 60 s mit
   Wiederholungszähler, G-4).
2. `core/observability/ingress.py` additiv erweitert: `ObservabilityIngress`
   mit `submit`/`observe_server_result`/`event`/`drain` exakt nach CONTRACTS
   §6, Reihenfolge in `submit` laut Implementierungsschritt 1 (Health
   `FAILED`? → `enabled`/Level? → Wasserstandsregel → `put_nowait`),
   `NullIngress(ObservabilityIngress)` als verhaltensgleiches No-Op,
   `NULL_INGRESS` als Modulkonstante. Das bestehende `Ingress`-Protocol aus
   OBS-010 ist unverändert erhalten geblieben.
3. `core/observability/adapters/__init__.py` (Paketmarker) und
   `core/observability/adapters/python_logging.py` neu:
   `UnifiedLogHandler(logging.Handler)` mit `threading.local`-Wiedereintritts-
   sperre (G-1), `handleError` überschrieben und meldet an Health statt an
   stderr (G-3), `flush()`/`close()` als No-Ops (G-7), Filter, der Records des
   Loggers `observability.internal` verwirft.
4. `core/observability/__init__.py` additiv erweitert: Re-Exports für
   `ObservabilityIngress`, `NullIngress`, `NULL_INGRESS`,
   `LoggingHealthState`, `LoggingHealthSnapshot`, `LoggingInternalHealth`,
   `UnifiedLogHandler` ergänzt; bestehende Re-Exports unverändert.
5. `core/logging_setup.py`: **einzige** geänderte Zeile in der bestehenden
   Funktion ist die Signatur (`def setup_logging(config: LoggingConfig, *,
   observability=None) -> None:`, exakt wie im Sollzustand des Work
   Packages) — der komplette bisherige Funktionskörper ist byte-identisch
   erhalten. Am Ende der Funktion wurden ausschließlich neue Zeilen für den
   optionalen dritten Handler angehängt (lokale Importe, um keinen
   Modul-Import-Zyklus/-Overhead beim regulären Start ohne Observability zu
   erzeugen).
6. Testsuiten neu angelegt (sechs Dateien, unten unter Abschnitt 5
   aufgeführt), inklusive der in WP-OBS-020 benannten Positiv-, Negativ-,
   Failure-, Nebenläufigkeits-/Zeit-, Integrations- und Contract-Tests sowie
   eines End-to-End-Nachweises, dass die OBS-010-Redaction durch die neue
   OBS-020-Pipeline unverändert wirkt (WP-Tests: "Redaction von Secrets",
   "Erhalt nicht sensibler Struktur", "Audio-Payload-Abwehr",
   "Transcript-Policy").
7. Diagnoseskript
   `40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/OBS-020_RUN-01_client_log_before_after_diagnose.py`:
   lädt `core/logging_setup.py` in der Fassung vor dieser Änderung direkt aus
   `git show HEAD:core/logging_setup.py` (ohne den Arbeitsbaum anzufassen)
   und vergleicht `client.log`-Inhalt (a) alt vs. neu ohne `observability`,
   (b) neu ohne vs. neu mit `observability` — beide Vergleiche PASS.

## 4. Design-Entscheidungen, die das Work Package offen ließ (dokumentiert,
      keine Abweichung vom Freeze)

Diese Punkte sind **keine** `DECISION REQUIRED`-Fälle: Das Work Package
spezifiziert Verhalten und Zählernamen, aber nicht jede interne
Implementierungsentscheidung. Alle Entscheidungen bleiben innerhalb des
durch ARCH/CONTRACTS gesetzten Rahmens.

- **Form des `observability`-Parameters in `logging_setup.py`.** Der
  Sollzustand-Codeblock des Work Packages zeigt ausschließlich
  `observability.ingress` und `observability.level`. Da `manager.py`
  (`ObservabilityManager`, die künftige Kompositionswurzel) laut ARCH §5.1
  erst in OBS-030 entsteht, wurde absichtlich **nichts** über diese zwei
  Attribute hinaus vorausgesetzt — kein `instance_id`, kein
  `store_transcription_content` auf dem `observability`-Objekt selbst. Der
  für `from_log_record` nötige Normalizer wird stattdessen aus
  `observability.ingress.instance_id` /
  `observability.ingress.store_transcription_content` /
  `observability.ingress.user_profile` gebaut — Attribute, die
  `ObservabilityIngress` ohnehin für seine eigenen `event()`/
  `observe_server_result()`-Pfade braucht und deshalb bereits als
  Nur-Lese-Properties trägt. Das erfindet keine neue Schnittstelle, sondern
  nutzt vorhandene.
- **`handleError`-Zielzähler.** ARCH §8.1 (G-3) verlangt nur "meldet an
  Health, nicht an stderr", ohne einen Zählernamen festzulegen; der
  eingefrorene Zählerkatalog (CONTRACTS §11.2 / ARCH §7.3) kennt kein
  eigenes `handler_errors`-Feld. Entscheidung: `handleError` zählt
  `malformed` — semantisch dieselbe Aussage wie eine
  Normalizer-Deklination ("dieser LogRecord konnte nicht verarbeitet
  werden"), ohne stderr, Health bleibt `OK` (konsistent mit der
  ARCH-§8.3-Zeile "Normalizer-Ausnahme → … Health OK + malformed++").
  `worker_errors`/`store_errors`/etc. bleiben für den künftigen Worker/Store
  reserviert (OBS-030) und werden von `LoggingInternalHealth` bereits jetzt
  angeboten, aber von OBS-020 selbst nicht ausgelöst.
- **Rate-Limiter-Reichweite pro Code.** G-4 verlangt "höchstens eine Zeile
  je Code und 60 s". Implementiert als ein `_RateLimiter` mit
  Pro-Code-Fenstern (Dictionary), injizierbar über einen optionalen
  `limiter`-Parameter — ausschließlich für deterministische Tests (fester
  Takt statt echtem `time.sleep(60)`); Produktionscode nutzt den
  Default-Limiter.

Keine dieser Entscheidungen ändert Zählerbedeutung, Health-Zustandsmenge,
Warteschlangenverhalten oder eine im Freeze genannte Signatur.

## 5. Neue Tests

- `tests/test_obs020_health.py` — Health-Zustände/-Snapshot, Zähler
  (inkl. Nebenläufigkeit), Rate-Limiter (Burst, Wiederholungszähler,
  Codetrennung), `sys.stderr is None`/`write()` wirft, `propagate is False`.
- `tests/test_obs020_ingress.py` — `submit`-Reihenfolge, Wasserstandsregel
  inkl. N-04 (replayter, typisierter Record wird dennoch verworfen),
  Queue-voll getrennt von Wasserstand, `enabled=False`, Leveltfilter,
  `submit(None)`/Fremdtyp, `drain`, `NullIngress`-Verhaltensgleichheit,
  8×5000-Nebenläufigkeitstest, 100 000-Submits-Zeitbasislinie.
- `tests/test_obs020_python_logging_handler.py` — ein Log-Record → ein
  Record, `exc_info`/`record.args`, vier `extra`-Felder, `%`-Formatfehler,
  werfendes `__str__`, namenloser Thread, Ingress liefert immer `False`,
  werfender Normalizer → `handleError`, werfender `submit` → `handleError`,
  Rekursionstest (G-1), `flush()`/`close()` No-Ops, interner-Logger-Filter.
- `tests/test_obs020_logging_setup_integration.py` — Rückwärtskompatibilität
  ohne `observability`, identischer `client.log`-Inhalt mit/ohne
  Observability, dritter Handler + Level, doppelter Aufruf → genau ein
  `UnifiedLogHandler`.
- `tests/test_obs020_contracts.py` — Isolation (`health.py` importiert weder
  `core.event_models` noch `core.feedback_reducer`; kein `PySide6`; kein
  `sqlite3` in `ingress.py`; keine Laufzeitreferenzen im Handler),
  azyklische Importe, Signaturabgleich `Ingress.event` ↔
  `ObservabilityIngress.event`, `observability.internal` `propagate`.
- `tests/test_obs020_redaction_end_to_end.py` — End-zu-Ende-Nachweis, dass
  die OBS-010-Redaction durch `UnifiedLogHandler`/`ObservabilityIngress`
  unverändert wirkt: Secrets, nicht-sensible Struktur, Audio-Payload-Abwehr
  (Quellcode-Nachweis, dass die Hot-Path-Audiofunktionen keinen Bezug zum
  Ingress haben, plus ein Abwehrtest für einen fehlgeleiteten Byte-Payload),
  Transkript-Policy (beide Richtungen), keine Mutation der Eingabedaten.

## 6. Testläufe

Siehe `40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/TEST_RESULTS.md` für
vollständige Kommandos/Ergebnisse. Kurzfassung: 715 = 640 (Baseline nach
OBS-010) + 75 neu (66 Kernpaket + 9 Redaction-End-zu-Ende), alle grün, kein
bestehender Test geändert.

## 7. Abschlussprüfung

- `git diff --check` → Exit 0 (nur ein harmloser CRLF-Hinweis zu
  `LOG_VERLAUF.md`, kein Fehler)
- `git status --short` → siehe DIFF_SUMMARY.md
- `git diff --stat` → nur `core/logging_setup.py` unter den Produktdateien
  geändert (plus die beiden Steuerungsdateien)
- Scope-Prüfung: erfüllt, siehe Abschnitt 2

## 8. Beobachtung außerhalb des Scopes (nicht behoben, siehe Regel "keine
      fachfremden Produktänderungen")

Unter Windows mit einer `cp1252`-Konsole erzeugt die vorhandene
`ReadableFormatter`-Trennzeichen-Glyphe (`│`, U+2502) beim Schreiben auf
`sys.stdout` einen intern von `logging` abgefangenen `UnicodeEncodeError`
("--- Logging error ---", kein Absturz). Das ist **vorbestehendes** Verhalten
des bereits existierenden Stdout-Handlers (nicht Teil von OBS-020) und tritt
unabhängig vom `observability`-Parameter auf. Nicht behoben — außerhalb des
Scopes von OBS-020 ("keine fachfremden Produktänderungen"); im
Diagnoseskript umgangen (`stdout=False`), damit die Redaction-/Format-Prüfung
unbeeinflusst bleibt.

## 9. Abschluss

`OBS-020 IMPLEMENTED – READY FOR REVIEW`
