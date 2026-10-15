# AP-IV2-020 – IN_PROGRESS, Fortsetzung R01, 2026-10-15

AP-IV2-010 tatsächlich ACCEPTED, kanonischer Parent `b80ed8b` unverändert.
Paketbranch `work/client-v2/ap-iv2-020`, kumulativer Draft-PR #15.
Die ausdrückliche Scope-Freigabe erlaubt enge Client-Reconnect-/Recoverykorrekturen
im selben R01. Systematischer Audit, rote Fehlernachweise und Regressionen laufen;
neue Produkt-/Build-/Paar-/Windowsqualifikation ersetzt keine offenen Realfälle.
Die bisherigen 1360 grünen Windowsprüfungen sind historische Vorfix-Evidenz.
M-/Wakepositive-/Kalibrierungs-/30min100-Gates bleiben offen, kein REVIEW_READY.
[Report](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1 und produktive Server geschützt; Server nur lokal, keine Übernahme/Releases.

## Vorheriger datierter Stand

# RealtimeSTT Client V2 – Projektübersicht

Stand 2026-10-14. Windows-Client mit Python3.12/PySide6, Qt im Main Thread,
asyncio-Core im eigenen Thread, nativen Win32-Hotkeys, Clipboard/SendInput und
SQLite-Historie. Host `stt.voice.marcosudau.com`, Desktopendpoint `/ws/v2`.

AP000 bis AP100 wurden nach unabhängiger Abnahme und menschlicher Freigabe auf
`feat/client-v2` übernommen; AP100-Aggregat ist `62ca35a`. AP110 bereinigt alte
Produktautoritäten und qualifiziert Wheel/sdist/EXE. Aktueller Abgabe-/Reviewstatus:
[Workflowstatus](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

GUI und Headless komponieren Transport, Mirror, Media, Settings, Controls,
Results, Logs und Feedback. Serverevents steuern Lifecycle und Deadlines;
Zwischentext bleibt Overlay-only, Finals werden history-first genau einmal
reserviert. Logausfall ändert keinen Domainzustand. Alte Config-/Historyreader
bleiben für explizite Migration erhalten; V1-Transport/Controller/Fallback und
lokale Diktattimer sind entfernt. Rollen und Phasen bleiben quellenneutral.

[Bedienung und Build](../README.md), [Migration und Kompatibilitätsmatrix](compatibility.md),
[Runtimeinterfaces](protocol-v2-runtime.md), [Paketierung](protocol-v2-release.md).
Aktive verbindliche Planung: [CLIENT_V2](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md).
AP110 ist tatsächlich auf `43759d3` übernommen. AP-IV2-010 liegt als automatisiert
geprüftes festes Paar in [PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14) REVIEW_READY vor;
[Nachweise](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md).
Unabhängige Abnahme/Übernahme, AP-IV2-020 und Server-Distributed bleiben offen. Ein Build-/Selbstcheck
ersetzt weder unabhängigen ROOT_PASS noch menschliche kanonische Übernahme.
