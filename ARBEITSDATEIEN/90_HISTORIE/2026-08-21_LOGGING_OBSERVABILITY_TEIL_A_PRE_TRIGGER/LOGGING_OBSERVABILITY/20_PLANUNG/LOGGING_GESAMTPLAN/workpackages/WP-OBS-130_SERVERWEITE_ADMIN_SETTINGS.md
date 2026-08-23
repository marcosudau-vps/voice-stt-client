---
id: OBS-130
status: DRAFT
authority: planning
workstream: OBS
phase: C
---

# OBS-130 – Serverweite Admin-Settings

## Ziel

Dieses Work Package ist Bestandteil des Gesamtplans. Es darf erst auf `READY` gesetzt werden, wenn seine Abhängigkeiten und die zugehörigen Architekturentscheidungen geschlossen sind.

## Scope

- [ ] ServerAdminService implementieren
- [ ] server config read/write
- [ ] runtime/model status
- [ ] capability-driven Admin UI
- [ ] lokale/session/serverweite Config strikt trennen

## Non-Scope

- Keine stillen Änderungen außerhalb dieses Work Packages.
- Keine Änderung normativer Contracts ohne `DECISION REQUIRED`.
- Keine fachliche Runtime-Autorität für Logging.
- Keine Git-History-Aktion ohne ausdrückliche Freigabe.

## Pflichtprüfungen

- [ ] Positive Tests
- [ ] Negative Tests
- [ ] Failure-/Edge-Tests passend zum Paket
- [ ] relevante Produktionspfade
- [ ] `git diff --check`
- [ ] kein unbeabsichtigter Cross-Workstream-Diff

## Evidence

Evidence wird unter einem paketbezogenen Evidence-Ordner abgelegt und enthält mindestens Commands, Exitcodes, Ergebnisse und bekannte Einschränkungen.

## Gate

`PASS` nur nach separatem Review. Ein Coding-Agent darf nicht allein aufgrund eigener grüner Tests das Gate vergeben.
