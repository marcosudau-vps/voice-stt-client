# RUN_REPORT – RUN-OBS-050-02_2026-08-18

## Run-ID

`RUN-OBS-050-02_2026-08-18` (Korrekturlauf)

## Work Package

**OBS-050 – Local Query, Minimal UI & Settings**

## Ausgangszustand

- `OBS-050 GATE FAIL` vom 2026-08-18
  (`40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`),
  zwei blockierende Befunde B-1 und B-2, beide in `ui/logs/log_page.py`.
- HEAD `91a7b7f`; die OBS-050-Dateien aus RUN-01 sind unversioniert.
- Query-Layer, Settings, Apply-Kette, Manager, Worker, Importrichtung und
  „Logging läuft ohne UI" waren im Gate belastbar geprüft und in Ordnung.

## Durchgeführte Arbeiten

1. Beide Befunde mit der unveränderten Gate-Probe selbst reproduziert
   (`FAILURES: 2`, exit 1) und anschließend am Code verifiziert.
2. **B-1**: Umkehrung je Historieseite entfernt; die Ansicht zeigt jede Seite
   in der gelieferten Richtung, ältere Seiten unten. Automatisches Nachladen
   bleibt am Listenende.
3. **B-2**: vier benannte Anfragearten, ein Abfragetrichter `_issue`, der
   Anfrage-ID und Art zusammen festhält, Verzweigung über die verbrauchte Art,
   `_live_cursor` stets aus der jüngsten Zeile.
4. Neun Regressionstests (drei B-1, sechs B-2) und zwei richtiggestellte
   RUN-01-Erwartungen.
5. Neue Laufzeitprobe `probe_obs050_ordering_fix.py` (acht Prüfungen,
   richtungsbewusst) und erneuter Lauf beider Gate-Proben.
6. Evidence RUN-02, Steuerungsdateien aktualisiert.

## Erzeugte und geänderte Dateien

**Produkt:** `ui/logs/log_page.py` (456 → 526 Zeilen). Keine weitere.

**Tests:** `tests/test_obs050_ui.py` (+9 Tests, eine Erwartung
richtiggestellt), `tests/test_obs050_contracts.py` (ein Test folgt dem
Trichter, ein neuer Strukturtest).

**Unterlagen:** dieser Run-Ordner und
`40_EVIDENCE/OBS-050/RUN-02_2026-08-18/` mit `FIX_SUMMARY.md`,
`TEST_RESULTS.md`, `UI_ACCEPTANCE.md`, `probe_obs050_ordering_fix.py`.

## Entscheidungen

| # | Frage | Entscheidung | Grundlage |
|---|---|---|---|
| K-1 | Welche der beiden vom Gate angebotenen B-1-Korrekturen? | **Variante 1** — Umkehrung entfällt, Historie absteigend, ältere Seite unten | Gate-Review §1 B-1; hält `§9.3` „Nachladen am Listenende" wörtlich, braucht weder eine zweite Produktdatei noch einen Modell-Reset je Seite (der Auswahl und Detail verwerfen würde) |
| K-2 | Wie wird die Antwortart bestimmt? | über die **Anfrage**: benannte Arten, ein Trichter `_issue`, Art wird beim Verarbeiten verbraucht | Gate-Review §1 B-2 („Die Richtung einer Antwort aus der **Anfrage** ableiten") |
| K-3 | Woraus wird `_live_cursor` gesetzt? | aus der **jüngsten** gelieferten Zeile, in beiden Live-Fällen | `CONTRACTS §9.2` (`WHERE id > :last`) |
| K-4 | Wird die wechselnde Leserichtung sichtbar gemacht? | ja, ein Wort in der Statuszeile | keine Vertragsvorgabe; die einzige missverständliche Stelle wird benannt statt kommentiert |

Kein `DECISION REQUIRED`, kein normatives Dokument verändert, kein neuer
Recordtyp, kein neuer Zähler, kein neues Konfigfeld.

## Offene Entscheidungen

Keine.

## Tests / Evidence

179 OBS-050-Tests grün unter beiden Runnern; OBS-010…050 625 grün; volle Suite
1137 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag, dessen Lage
außerhalb des Diffs nachgemessen ist. `probe_obs050_ordering_fix.py` 8/8,
`probe_obs050_end_to_end.py` (RUN-01) 12/12, beide exit 0.
`git diff --check` leer.

## Blocker

Keine. B-1 und B-2 sind reproduzierbar behoben.

## Gate-Empfehlung

`OBS-050 CORRECTED – READY FOR RE-REVIEW`. Der Gate-Review bleibt offen und
gehört in eine frische Session.

Für den erneuten Review besonders lohnend:

1. Die Anzeigereihenfolge in **beiden** Modi über mehrere Seiten bzw. Takte —
   und die Einordnung, dass Fall A der alten Gate-Probe für die gewählte
   Variante 1 erwartungsgemäß `monotone(aufsteigend): False` meldet
   (`FIX_SUMMARY.md` Abschnitt 1.3).
2. Ob wirklich kein Pfad mehr eine Anfrage-ID ohne ihre Art vergibt
   (`test_every_query_records_the_kind_of_request_it_was`).
3. Ob der Live-Cursor in jedem Fall aus der jüngsten Zeile stammt.
4. Ob außer `ui/logs/log_page.py` tatsächlich keine Produktdatei berührt ist.

## Nächster Schritt

Erneuter unabhängiger **OBS-050 Gate Review** in frischer Session
(`Prompts/OBS-050_GATE_REVIEW.md`). **OBS-060 nicht beginnen.**
