# AP04 – AntiGravity-Ausführungs- und Prüfprotokoll

> **Status:** datierte Belegsammlung, nicht kanonisch  
> **Beginn:** 25. Juli 2026  
> **Modell:** `gemini-3.6-flash-high`  
> **Maximaler Agentenzyklus:** ein Initialauftrag und bis zu drei
> Korrekturaufträge

Dieser Ordner dokumentiert die durch AntiGravity ausgeführte Umsetzung von
Arbeitspaket 4 und die anschließende unabhängige Prüfung.

Verbindlich bleiben der tatsächliche Code, die erfolgreich reproduzierbaren
Tests sowie die kanonischen Projektdokumente. Die Dateien in diesem Ordner
dienen ausschließlich der Nachvollziehbarkeit von Aufträgen, Agentenberichten,
erzeugten Arbeitsartefakten und Prüfentscheidungen.

## Ablageschema

- `00_AUSGANGSSTAND.md`: unveränderter Test- und Hashstand vor AP4
- `00_INITIAL_PROMPT.md`: vollständiger erster Ausführungsauftrag
- `00_initial/`: von AntiGravity erzeugte Artefakte und CLI-Protokoll
- `01_KORREKTUR_PROMPT.md` bis `03_KORREKTUR_PROMPT.md`: nur bei tatsächlich
  erforderlichen Korrekturrunden
- `01_korrektur/` bis `03_korrektur/`: Artefakte der jeweiligen Runde
- `PRUEFBERICHT_*.md`: unabhängige Befunde nach einer Runde
- `SELBSTFERTIGSTELLUNG.md`: direkte Fertigstellung nach Ausschöpfen der drei
  AntiGravity-Korrekturrunden
- `GESAMTABNAHME.md`: abschließende Bewertung mit reproduzierbaren Nachweisen

Jeder Prompt und jeder erhaltene Abschlussbericht wird unverändert oder als
klar gekennzeichnete, vollständige Transkription gespeichert. Von AntiGravity
erzeugte Pläne und Walkthroughs erhalten rundenspezifische Dateinamen, damit
spätere Korrekturen frühere Belege nicht überschreiben.
