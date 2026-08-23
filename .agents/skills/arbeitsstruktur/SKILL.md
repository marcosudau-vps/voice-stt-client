# Skill: Arbeitsstruktur

Dieser Skill verwaltet die Arbeitsaktenstruktur deterministisch.

## Begriffe

- **Arbeitsblock**: größerer zusammengehöriger Themen-/Umbaukomplex unter `10_AKTUELL`, `20_ZURUECKGESTELLT` oder `90_HISTORIE`.
- **Arbeitspaket**: agentengerechte Umsetzungseinheit innerhalb eines Arbeitsblocks.
- **Run**: einzelner Agentenlauf innerhalb eines Arbeitspakets.

## Projektweite Anweisungen

Im Repository-Root müssen `AGENTS.md` und `CLAUDE.md` vorhanden sein bzw. von `Initialize-Arbeitsstruktur.ps1` idempotent ergänzt werden.

`CLAUDE.md` verweist auf `AGENTS.md` und erklärt `.agents/` ausdrücklich als projektlokalen Agenten-/Skill-/Instruktionsbereich analog zu `.claude/`.

## Standardzustände

- `10_AKTUELL/` = aktiv
- `20_ZURUECKGESTELLT/` = bewusst pausiert, nicht abgeschlossen
- `90_HISTORIE/` = abgeschlossen / historisch

## Wichtige Regel zu IDEEN

`IDEEN/` ist kein Projektwissen. Inhalte daraus dürfen von Agenten nicht für Analyse, Recherche, Planung, Entscheidung oder Implementierung verwendet werden, sofern der Auftrag nicht ausdrücklich eine konkrete Datei daraus nennt.

## Arbeitspakete

Die Detailregeln stehen in jedem Arbeitsblock unter `PLANUNG/README.md`.

Kernanforderungen:
- klarer Zielzustand,
- prüfbare Akzeptanzkriterien,
- konkrete Validierung,
- sauberer Scope,
- dokumentierte Abhängigkeiten,
- standardmäßig eigener Commit nach vollständigem PASS.

Wenn ein AP vollständig erfolgreich umgesetzt und validiert ist, erstellt der ausführende Agent standardmäßig einen dedizierten Commit, außer:
- der Auftrag verbietet Commits ausdrücklich,
- Änderungen lassen sich nicht sicher von fremden Working-Tree-Änderungen isolieren,
- ein technischer/Git-Blocker verhindert den Commit.

Es wird niemals blind mit `git add -A` gestaged, wenn fremde Änderungen vorhanden sein können.

## Skripte

### Repository-Struktur initialisieren
`Initialize-Arbeitsstruktur.ps1`

- ergänzt/erstellt Root-`AGENTS.md` idempotent,
- ergänzt/erstellt Root-`CLAUDE.md` idempotent,
- legt fehlende Steuerungsdateien/Grundordner an,
- überschreibt bestehende Steuerungsdateien nicht.

### Repository-Struktur validieren
`Test-Arbeitsstruktur.ps1`

Prüft Root-Anweisungen, Steuerungsdateien, Grundordner und Skill-Skripte.

### Arbeitsblock erstellen
`New-Arbeitsblock.ps1`

Erstellt:
- `README.md`
- `STATUS.md`
- `VERLAUF.md`
- `PLANUNG/README.md` mit Planungsleitfaden, AP-Standard, Commit-Regel und Implementierungsplan-Beispiel
- `IDEEN/README.md`
- `ARBEITSPAKETE/README.md`

Kein `QUELLEN/`-Ordner wird standardmäßig erzeugt.

### Arbeitsblock validieren
`Test-Arbeitsblock.ps1`

Prüft Pflichtdateien, Metadaten, Zustands-/Pfadkonsistenz, Ideen-Sperre, Planungs-/AP-Regeln und unerwünschte Altstruktur.

### Zurückstellen
`Defer-Arbeitsblock.ps1`

Verschiebt deterministisch von `10_AKTUELL` nach `20_ZURUECKGESTELLT`, aktualisiert Status und Verlauf.

### Wiederaufnehmen
`Resume-Arbeitsblock.ps1`

Verschiebt deterministisch zurück nach `10_AKTUELL`, aktualisiert Status und Verlauf.

### Verlauf promoten
`Promote-ArbeitsblockVerlauf.ps1`

Übernimmt fehlende standardisierte Einträge aus dem lokalen `VERLAUF.md` chronologisch in `00_STEUERUNG/LOG_VERLAUF.md`.

### Abschließen
`Close-Arbeitsblock.ps1`

Standardmäßig nach Integration auf `main`:
1. validiert,
2. markiert den Arbeitsblock als abgeschlossen,
3. schreibt `ABSCHLUSS.md`,
4. promotet den lokalen Verlauf,
5. erzeugt ein SHA-256-Manifest,
6. verschiebt deterministisch nach `90_HISTORIE/YYYY-MM-DD_<NAME>`.

`CURRENT_STATE.md` und `MASTERPLAN.md` werden bewusst nicht automatisch inhaltlich geraten.

## Sicherheitsprinzip

Die Verwaltungs-Skripte:
- führen keine Branch-Wechsel aus,
- committen selbst nichts,
- pushen nichts,
- führen kein `reset`, `clean`, `stash`, `rebase` oder Force-Operationen aus.

Die AP-Commit-Regel ist eine Arbeitsregel für den ausführenden Implementierungsagenten und nicht Aufgabe der Strukturverwaltungsskripte.
