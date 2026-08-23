---
id: OBS-120
status: DRAFT
authority: planning
workstream: OBS
phase: C
---

# OBS-120 – Remote Server History & Global Logs

> **Übergabe aus OBS-000** (`00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md §10.3/§10.4`)
>
> - **`SessionHistoryProvider` zuerst, nicht der Admin-Provider** (`FD-B2`). Er
>   braucht keinen Admin-Key, keine Auth-UI und keine `ServerControlConnection`
>   — nur den vorhandenen Session-Token und `hello.logAccess.historyPath`, das
>   der Client heute liest und **verwirft**. Er liefert sofort den wertvollsten
>   Vergleich: „Serverhistorie hat `transcription.completed`, lokale Historie
>   nicht."
> - **`ProviderCapabilities` wird hier eingeführt** (`FD-S3`), additiv, weil
>   `ProviderStatus` eine frozen dataclass mit Defaults ist. Der
>   Serverendpunkt kann nur `channels`, `events`, `sessionId`,
>   `transcriptionId`, `from`, `to`, `afterCursor` und `limit ≤ 1000` — **kein**
>   `activation_id`, **kein** `command_id`, **keinen** Freitext. Ohne
>   Capabilities böte die UI Filter an, die dort still ignoriert würden.
> - **HTTP-Fähigkeit ist Teil dieses Pakets** (`FD-B3`): Der Client hat heute
>   **keinen** HTTP-Client — `requirements.txt` kennt nur `websockets`,
>   `sounddevice`, `numpy`, `PySide6`, `PyYAML` und
>   `led-controller-version-3`. Abhängigkeits- und Buildentscheidung
>   (stdlib gegen neue Abhängigkeit) sowie eine Prüfung der PyInstaller-Spec
>   gehören hierher. Die dortigen `excludes` betreffen den **Server**-Stack in
>   LEFX und stehen dem nicht entgegen.
> - **Invariante O-14:** Remote-Historie wird **nicht** in die lokale SQLite
>   repliziert. Kein Provider schreibt. Dieselbe `event_id` in lokaler Kopie und
>   Remote-Ergebnis ist **gewollt** und der eigentliche Diagnosewert.
> - `QueryFilter.scopes = ("global",)` **bedeutet** die Adminabfrage;
>   `session_id = None` bleibt „ohne Einschränkung".

## Ziel

Historische und serverweite Logs über dieselbe Query-UI sichtbar machen, ohne
Storage- oder Transportwissen in die View zu bringen.

## Scope

- [ ] `SessionHistoryProvider` zuerst
- [ ] `ServerHistoryProvider` / globale Serverlogs danach
- [ ] `ProviderCapabilities` einführen
- [ ] HTTP-Fähigkeit und Buildauswirkung klären
- [ ] Remote Filter/Pagination/Cursor
- [ ] `AUTH_REQUIRED`/`UNAVAILABLE`-Zustände
- [ ] local-vs-remote identity erhalten

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
