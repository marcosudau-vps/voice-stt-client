---
id: EV-OBS-000-04
status: FINAL
authority: evidence
workstream: OBS
run: RUN-OBS-000-01_2026-08-15_CLAUDE
---

# EV-04 – Konsistenzcheck der Planungs- und Freeze-Dateien

**Zweck.** Nachweis, dass nach dem Freeze **keine** Planungsdatei mehr eine
Aussage trägt, die von einer eingefrorenen Entscheidung widerlegt ist. Ein
Coding-Agent, der die Planung liest, darf nirgends auf einen gestrichenen
Mechanismus stoßen, ohne dass die Streichung dort ausdrücklich steht.

---

## 1. Suche nach gestrichenen Mechanismen

Gesucht wurde nach allen Begriffen, die durch den Freeze entfallen oder ersetzt
sind.

```bash
cd ARBEITSDATEIEN/AP_THEMA_LOGGING
grep -rn -i "ringbuffer|live_buffer_size|queue_high_size|queue_low_size|\
mode=ro|file_sink_format|auto_vacuum|incremental_vacuum|\
ProviderCapabilities|monotonic_ns" 20_PLANUNG/ 00_NORMATIV/
```

### Ergebnis

| Datei | Treffer | Bewertung |
|---|---:|---|
| `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md` | 5 | alle **Negationen bzw. Streichungsbegründungen** |
| `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md` | 9 | alle Negationen bzw. Vertragskorrekturen (`KEIN mode=ro`, `KEIN auto_vacuum`) |
| `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` | 18 | alle im Entscheidungs- und Widerspruchsregister, mit Begründung |
| `20_PLANUNG/…/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md` | 6 | alle Negationen oder korrekte Vorwärtsverweise auf Teil B |
| `20_PLANUNG/…/01_WORKPACKAGE_INDEX.md` | 1 | Negation |
| `20_PLANUNG/…/02_OBS000_FREEZE_CHECKLIST.md` | 2 | Negationen |
| `workpackages/WP-OBS-030…` | 2 | Negationen (`D-2`, `D-4`) |
| `workpackages/WP-OBS-050…` | 4 | Negationen |
| `workpackages/WP-OBS-120…` | 2 | korrekter Vorwärtsverweis: `ProviderCapabilities` wird **dort** eingeführt |

Stichprobe der Formulierungen:

```text
00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md:468
    - Leser oeffnen **kein** `mode=ro` -- auf einer WAL-Datenbank ist das nicht
00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md:470
    - **Kein** `auto_vacuum`, **kein** `incremental_vacuum`, **kein** `VACUUM`.
00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md:617
    ... -- **kein Ringbuffer**, kein Signal je Record
01_WORKPACKAGE_INDEX.md:29
    (Entscheidung `FD-S1`: kein Ringbuffer, der Live-Modus benutzt die ...)
```

**Kein einziger Treffer fordert einen gestrichenen Mechanismus.**

---

## 2. Prüfung der Nummernkreise

Vor dem Freeze existierten zwei Nummernkreise für dieselbe Arbeit:
`OBS-00 … OBS-13` im V1-Implementierungsplan gegen `OBS-010 … OBS-060` im
Gesamtplan.

| Prüfpunkt | Ergebnis |
|---|---|
| Ist ein maßgeblicher Kreis benannt? | ja — der des Gesamtplans |
| Existiert eine vollständige Abbildung 14 → 6? | ja, `DECISIONS §8.1`, gespiegelt in `01_WORKPACKAGE_INDEX.md` |
| Sind die Titel angepasst? | ja, zwei Korrekturen mit Begründung (OBS-020, OBS-030) |
| Sind die Dateinamen geändert? | **nein, bewusst** — Pfadstabilität; die Korrektur steht im Dokument |
| Ist die Reihenfolgeabweichung Handler↔Store aufgelöst? | ja, `DECISIONS §8.3` |
| Ist die Abhängigkeit OBS-050 korrigiert? | ja, unabhängig von OBS-040 |

---

## 3. Prüfung der Statusfelder

```bash
grep -rn "^status:" 20_PLANUNG/LOGGING_GESAMTPLAN/ 00_NORMATIV/
```

| Datei | Status | erwartet |
|---|---|---|
| `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md` | `FROZEN` | ✔ |
| `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md` | `FROZEN` | ✔ |
| `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` | `FROZEN` | ✔ |
| `00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md` | `FROZEN_BASELINE` | ✔ |
| `WP-OBS-010` | `READY` | ✔ |
| `WP-OBS-020` | `READY` | ✔ |
| `WP-OBS-030…060`, alle Teil-B-Pakete | `DRAFT` | ✔ |

Alle drei normativen Dateien tragen zusätzlich `authority: normative`,
`workstream: OBS`, `freeze_gate: OBS-000`.

---

## 4. Verbleibende Altlasten – benannt, nicht repariert

Zwei Punkte betreffen die Ablage, nicht den Inhalt. Beide sind bewusst nicht in
diesem Run geändert worden, weil dafür kein Auftrag vorlag.

```text
A-1  05_DRAFTS_UNGEPRUEFT/LOGGING_GESAMTPLAN/
     Byteidentische Kopie des Ausgangszustands des Gesamtplans. Der Ordnername
     ist irrefuehrend, weil AGENTS.md diesen Bereich als "niemals automatisch
     normativ" fuehrt -- hier liegt aber eine Kopie des maszgeblichen Plans.
     Sie ist ab jetzt VERALTET, weil der Plan unter 20_PLANUNG fortgefuehrt
     wurde.
     Empfehlung: nach 90_ARCHIV/ verschieben.
     Vermerkt in 20_PLANUNG/LOGGING_GESAMTPLAN/README.md.

A-2  20_PLANUNG/LOGGING_ZIELBILD_..._ENTWURF.md
     20_PLANUNG/LOGGING_V1_ABGRENZUNG_ENTWURF.md
     Byteidentische Kopien der Entwuerfe aus 00_GRUNDLAGEN/. Zwei Ablagen
     desselben Entwurfs, einer davon im Planungsordner -- das koennte den
     Eindruck erwecken, sie seien Planungsstand.
     Sie sind es NICHT: die Autoritaetsreihenfolge in
     00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md §1.1 stellt sie ausdruecklich
     unter die normativen Dateien.
     Empfehlung: eine der beiden Ablagen aufloesen.
```

---

## 5. Gesamturteil

```text
Widerspruch zwischen Planung und Freeze:            KEINER
Gestrichener Mechanismus ohne Streichungsvermerk:   KEINER
Uneindeutiger Nummernkreis:                         AUFGELOEST
Statusfelder:                                       KONSISTENT
Offene Ablage-Altlasten:                            ZWEI, benannt, unkritisch
```
