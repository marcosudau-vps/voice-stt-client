# AP-IV2-020 – BLOCKED, 2026-10-15

AP-IV2-010 tatsächlich ACCEPTED: PR14-Squash `b80ed8b`, unabhängiger R02-PASS und
menschliche R03-Freigabe geprüft. Paketbranch `work/client-v2/ap-iv2-020`.
Produktcode unverändert. Windowsbaseline1354, finale Windowsregression1360 und
11 Prozessprüfungen PASS. Lokaler source-qualified Modellserverada13b0 und reale
ReSpeaker-/USB-/Credential-/Hotkey-/Desktop-/Frozenvorchecks belegt.
**IV2-020-F01:** temporärer Settings-HTTP-Ausfall beim Serverrestart blockiert
Recovery dauerhaft. Konkreter enger Clientfix vorbereitet; Produktänderungsfreigabe
erforderlich. M-/Wakepositive-/Kalibrierungs-/30min100-Gates offen, kein REVIEW_READY.
[Report](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/produktive Server geschützt; keine VPS-Einrichtung, Übernahme oder Releases.

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
