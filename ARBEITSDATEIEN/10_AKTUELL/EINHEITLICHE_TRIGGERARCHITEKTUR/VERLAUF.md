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

## 2026-08-24 02:03 +02:00 – Main→Trigger-Integration und Merge-Konfliktauflösung

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
