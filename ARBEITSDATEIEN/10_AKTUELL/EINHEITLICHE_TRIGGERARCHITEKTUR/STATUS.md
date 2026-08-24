# Status – Einheitliche Triggerarchitektur

<!-- ARBEITSBLOCK-META
schema: 1
name: EINHEITLICHE_TRIGGERARCHITEKTUR
title: Einheitliche Triggerarchitektur
state: AKTIV
phase: PLANUNG
created_at: 2026-08-24 01:08:47 +02:00
updated_at: 2026-08-24 02:03:12 +02:00
branch: feat/einheitliche-triggerarchitektur
baseline_head: dd0af5ed22e7401895f08c8c13e4e37c7e78ddb7
-->

**Status:** AKTIV
**Phase:** PLANUNG
**Branch:** `feat/einheitliche-triggerarchitektur`

## Aktueller Stand

DOC-ARCH-002 (Arbeitsstruktur-Einführung) ist organisatorisch
abgeschlossen: die neue deterministische Struktur (`PLANUNG/`, `IDEEN/`,
`ARBEITSPAKETE/`, `QUELLEN/`) ist aufgebaut, die Inhalte der alten Struktur
wurden hash-verifiziert übernommen, und die eindeutig ersetzten Altpfade
wurden entfernt. Details siehe `VERLAUF.md` und
`ARBEITSPAKETE/AP-ORG-001_ARBEITSSTRUKTUR_COPY_PREP/`.

Die eigentliche Implementierung der einheitlichen Triggerarchitektur ist
davon unberührt und beginnt erst in den dafür vorgesehenen
Fach-Arbeitspaketen.

## Bewusst erhaltener Altpfad

`20_PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`
bleibt am alten Pfad bestehen, weil sie lokal modifiziert und noch nicht
committet ist (aktive Produktarbeit, kein Organisationsartefakt). Eine
hash-identische Kopie des damaligen Stands liegt zusätzlich unter
`PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`. Wer
diese Datei fertig bearbeitet, committet sie an ihrem kanonischen Pfad
(`PLANUNG/planung_migration/...`) und entfernt danach den alten Pfad.

## Aktive Arbeitspakete

- `AP-TRG-000_GATE_0`: enthält die kopierten GATE-0-Prompts
  (Quelle war `30_AUSFUEHRUNG/prompts/GATE_0/`, inzwischen entfernt; die
  Kopie unter `QUELLPROMPTS/` ist die kanonische Fundstelle).
  Noch nicht ausgeführt, nicht geplant in diesem Run.
- `AP-ORG-001_ARBEITSSTRUKTUR_COPY_PREP`: Organisations-Arbeitspaket für
  COPY-PREP- und Abschlusslauf von DOC-ARCH-002.

## Abgeschlossene Arbeitspakete

Keine Implementierungs-Arbeitspakete abgeschlossen (dieser Run war
ausschließlich organisatorisch).

## Offene Punkte / Blocker

Keine Blocker. Bewusst offen: der alte Pfad von
`01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md` (siehe oben) wird erst mit dem
Abschluss der zugehörigen Produktarbeit bereinigt.

## Nächster Schritt

1. Fachliche Planung/Implementierung der Triggerarchitektur gemäß
   `PLANUNG/README.md` fortsetzen.
2. Bei Abschluss der Arbeit an `01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`:
   Datei an ihrem kanonischen Pfad committen und den alten Pfad entfernen.

**Main→Trigger-Integration:** in diesem Abschlusslauf durchgeführt. `main`
(`1b432c9`) wurde in diesen Branch integriert; Konflikte in 9 Dateien
(Governance-Dokumente, `core/controller.py`, `core/stt_session.py`,
`ui/application.py`, 3 OBS-040-Tests) wurden fachlich zusammengeführt —
keine Seite wurde pauschal bevorzugt, alle Trigger-spezifischen Tests und
Verhaltensweisen sowie alle main-seitigen Fixes blieben erhalten. Die
vollständige Client-Test-Suite (1191 Tests) läuft grün. Details siehe
`VERLAUF.md`.
