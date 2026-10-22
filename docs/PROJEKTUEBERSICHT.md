## AP-IV2-020/R01 – REVIEW_READY,22.10.2026

[Abschlussbericht40](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/40_REVIEW_READY_UND_KONSOLIDIERTE_QUALIFIKATION.md): **REVIEW_READY**: native ReSpeaker-Altfinal/Recovery/Runpausen und finale normale EXE mit A-final während B-Sprache sowie zwei sichtbaren Ausgaben belegt. Vollständige1400Windows/0Skips/79Module,83Helfer/0Skips,compileall PASS. Produkt0f6c85e/Server67f3ce45 unverändert.18letzte eigene Profile archiviert entfernt, externer Namensraum leer. Zusammengesetzte Methoden/Grenzen und historische Fehlläufe explizit dokumentiert; kein eigener ROOT_PASS. Gleicher R01/Paketbranch/PR15; Schreibhoheit für unabhängigen Review zurückgegeben.

Nachfolgende datierte Zwischenstände sind historisch und durch Bericht40 konsolidiert.

## AP-IV2-020/R01 – Laufzuordnung und Hilfstimer,22.10.2026

[Bericht39](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/39_LAUFZUORDNUNG_UND_TESTTIMER.md): Mensch meldet eingefügten Text/Fensterschluss; gespeicherte Vorbereitung dagegen TIMEOUT ohne Clientstart, Satz nicht mehr bekannt. Beobachtung erhalten, Zuordnung NOT_PROVEN. Hilfstimer korrigiert: vor Start unbegrenzt warten, Laufbudget erst ab Clientstart.82Helfer/0Skips und compileall PASS, Produkt0f6c85e unverändert. Alle verbliebenen eigenen Profile/Helfer-TEMP archiviert entfernt, genehmigter Namensraum leer, kein laufender Test. Keine weitere Sprach-/Wahrnehmungsprobe gestartet. Technische Restmatrix bleibt BLOCKED, gleicher R01/PR15.

## AP-IV2-020/R01 – Abschlussproben,22.10.2026

[Bericht38](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/38_ADMIN_UAC_EXE_UND_MINIMALER_ABSCHLUSS.md): Adminguard positiv und generationgebunden, erhöhtes eigenes UAC-Ziel/APIstatus und drei native Stereomix-EXE-Einfügungen belegt. Erste ReSpeaker-ASR korrekt, automatische Einfügung fehlte; bewusster EXE-Reinsert erfolgreich. Minimaler Ein-Satz-Wakeversuch ohne Hotkeys vorbereitet, Wiederholen/Weiter repariert.80Helfer/Qt PASS; Produkt0f6c85e und1400Windowsbeleg unverändert. Wahrnehmungsabfragen menschlich abgeschlossen. Zehn beendete Profile plus Helfer-TEMP hashgesichert entfernt; nur ungestartete Abschlussprobe bleibt. Technische Restgrenzen NOT_PROVEN, BLOCKED/gleicher R01/PR15.

# AP-IV2-020 – IN_PROGRESS, Phase C vorbereitet, 2026-10-15

Kanonischer Parent `b80ed8b` unverändert, Vorgänger AP010 tatsächlich ACCEPTED.
Paketbranch `work/client-v2/ap-iv2-020`, kumulativer Draft-PR #15, derselbe R01.
Ausdrücklich freigegebener Reconnect-/Recovery-Audit abgeschlossen: zehn technische
Findings behoben. Produktcommit `41ca761`, neue EXE/Wheel/sdist sauber gebunden.
1373 Windows-Tests ohne Skips, 11 Prozessfälle, alle sieben Server-Smokes PASS;
1964 Server-Unit-Tests PASS/14 ausgewiesene optionale Skips. Echter ReSpeaker- und
Desktop-Reconnect, HTTP-/Ackausfall, drei Neustarts, Shutdown und Frozen-GUI grün.
M-Fälle, echte Wakepositive/Nutzsprachgrenze, Wahrnehmung/Kalibrierung und30min100
bleiben NOT_RUN/NOT_PROVEN. Nächste Aktion: gemeinsamer erster Sprach-/Windowsblock.
[Report](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/VPS geschützt; Server nur lokal. Kein REVIEW_READY, Eigenreview, Merge oder Release.

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
