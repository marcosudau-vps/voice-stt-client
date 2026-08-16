# AGENTS.md - ARBEITSDATEIEN

## Vor jedem neuen Run

1. 00_STEUERUNG/CURRENT_STATE.md
2. 00_STEUERUNG/MASTERPLAN.md
3. README bzw. AGENTS des betroffenen Themas
4. aktives Work Package
5. konkreten Prompt

## Sessionregel

Ein Agent-Run = eine Session.

Nur ein noch nicht abgeschlossener Run darf nach einem Usage-Reset in
derselben Session fortgesetzt werden. Review bzw. Gate eines abgeschlossenen
Runs startet in einer frischen Session.

## Ablage

- Soll/Freigabe: 00_NORMATIV
- Grundlagen: 05_GRUNDLAGEN
- Analyse: 10_ANALYSE
- ungepruefte Entwuerfe: 15_DRAFTS_UNGEPRUEFT
- Planung: 20_PLANUNG
- Prompts/Runs: 30_AUSFUEHRUNG
- Evidence: 40_EVIDENCE
- Tools: 50_TOOLS
- abgeloeste Zwischenartefakte: 90_ZWISCHENARCHIV

Nach jedem relevanten Run oder Gate genau einen Meilensteineintrag in
00_STEUERUNG/LOG_VERLAUF.md ergaenzen.

Commit, Push, Merge, Rebase, Tag oder PR nur bei ausdruecklicher Freigabe.