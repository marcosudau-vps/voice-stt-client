# Aktueller V2-Start und Migration – AP-CV2-100, 2026-10-13

GUI und Headless starten dieselbe V2Runtime. Bekannte `/ws/transcribe`-URLs werden
am gleichen Origin nach `/ws/v2` migriert; Profilwünsche kommen aus tatsächlichen
Benutzerwerten. Nach erfolgreichem Bootstrap Originalbackup `.pre-v2.bak` und
atomarer V2-Profilwrite auf Worker, keine gespeicherten Runpausen/Tokens.
Lokale Präferenzen und Historymigration bleiben erhalten. V1-Klassen bleiben noch
für Migration/Regression; finaler Legacyabbau und Build AP110 offen.
[Architektur, öffentliche Ports, Startbefehle und Grenzen](protocol-v2-runtime.md).

## Historische Ergänzungen vor AP100

# Historymigration AP-CV2-060, 2026-10-12

History migriert V1-Integersegmente transaktional nach Schema2 mit TEXT-/Protokoll-/UUID-Herkunft, vorherigem SQLite-Backup und unveränderten Legacy-IDs/Attempts. Pendinginjektion wird nach Crash unknown; keine automatische Wiederholung. [API, Datenmigration und Grenzen](protocol-v2-results.md). Persistierte Konfigurationsmigration bleibt AP070, Appkomposition AP100.

# Transportergänzung AP-CV2-020, 2026-10-12

V2STTSession verwendet `/ws/v2`; explizite Legacy-URLs bleiben erhalten und werden über typed BLOCKED/legacy_endpoint_requires_migration sichtbar. Keine Profilschreiboperation, kein stiller Hostwechsel. [Transportvertrag](protocol-v2-transport.md). Bestehende Appkomposition wird in CV2-100 umgestellt; allgemeine persistierte Konfigmigration bleibt CV2-070.

## Historischer Stand vor AP-CV2-020

# Client-V2-Startbasis und Migration

Stand 2026-10-11, AP-CV2-000. Paketkandidat auf
`work/client-v2/ap-cv2-000`; technische Selbstqualifikation wird in der
[Runakte](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md)
belegt. Unabhängige Abnahme und kanonische Übernahme sind eigene Folgeschritte.

Die Featurelinie wird mit den kompatiblen V1-Verbesserungen aus `f625904`
fortgesetzt. Produktimporte heißen ausschließlich `voice_stt_client.core` und
`voice_stt_client.ui`. Toplevel `core`, `ui` und `app.py` sind entfernt.
Wheel und sdist enthalten Konfiguration und acht WAVs im Paketnamespace.

```powershell
.\venv\Scripts\python.exe -m voice_stt_client --version
.\venv\Scripts\python.exe -m voice_stt_client
.\venv\Scripts\python.exe -m voice_stt_client --config C:\Pfad\client.yaml --headless
```

Ein installiertes Paket stellt zusätzlich `voice-stt-client` bereit.
`--verify-gui-runtime` prüft Qt-Imports ohne Tray, Mikrofon, Serverkontakt
oder Änderung der Benutzerkonfiguration. `VERSION` bleibt die Versionsquelle
(portierter V1-Wert 1.0.0); installierte Wheels lesen dieselbe Version aus
Distributionsmetadaten. Eine V2-Releasefreigabe ist damit nicht verbunden.
Kandidaten-Commit und Tree müssen zusätzlich aus der Paketakte/Git angegeben
werden; die Versionsnummer allein identifiziert diesen Entwicklungsstand nicht.

## Konfiguration und Daten

Packaged `voice_stt_client/config.yaml` liefert Defaults. Benutzerkonfiguration
liegt standardmäßig unter `~/.voice-stt/client/config.yaml`.
`VOICESTT_CLIENT_HOME` setzt das Datenverzeichnis,
`VOICESTT_CLIENT_CONFIG` wählt eine Konfigurationsdatei; `--config` hat Vorrang.
Explizite Dateien werden mit Paketdefaults geschichtet. Fehlen sie oder sind
sie unlesbar, schlägt das Laden fehl. Eine ausdrücklich gewählte Env-Datei
darf keinen stillen Rückfall auf Legacy auslösen.

Ohne explizite Auswahl und ohne neue Benutzerdatei wird
`%LOCALAPPDATA%/RealtimeSTT Client/config.yaml` gelesen. Ein späteres Speichern
geht dann in das neue Benutzerverzeichnis; Legacy bleibt erhalten.
Explizite Profile werden an ihre ursprüngliche Datei zurückgespeichert.
Unbekannte alte Felder werden mit Warnung ignoriert, bekannte Präferenzen
bleiben wirksam. Der genaue V1-All-null-Soundsatz erbt die gebündelten Pfade;
`sounds_enabled=false` sowie individuelle Custompfade/Nullwerte bleiben
erhalten. Es wird beim Lesen keine Konfigurationsdatei geschrieben.

Die Historie verwendet `~/.voice-stt/client/data/transcript_history.db`.
Existiert nur die alte Datenbank unter
`%LOCALAPPDATA%/RealtimeSTT_Client/transcript_history.db`, wird diese in situ
weiterbenutzt. Explizites `db_path` und `VOICESTT_CLIENT_HOME` haben Vorrang;
keine automatische Kopie oder Löschung der alten Historie. Eine ausdrücklich
gewählte neue Datenbasis importiert Legacy nicht automatisch. Eventcursor
bleiben an ihrem bestehenden LocalAppData-Pfad; dieses Paket migriert weder
Schema noch Lifecycle. Diagnose-/LEDdaten benutzen den portierten Benutzerroot.

Manual-/Wake-Word-Flags und Legacy-`session.mode` bleiben erhalten. Deaktivierte
globale Hotkeys und Wake-only-Sessions starten ohne globale Registrierung;
Traycontrols bleiben nutzbar. Der Einstellungsdialog erfasst Hotkeys nativ als
Qt-KeySequence (Meta wird zu Win normalisiert). Bei Konflikt wird eine
Alternative erst nach tatsächlicher Win32-Registrierung übernommen und
angezeigt; Apply behält den vorhandenen Satz bei Ablehnung/Rollback.

## Protokollgrenze und weitere Arbeit

AP-CV2-000 enthält weiterhin den bisherigen Featuretransport auf
`/ws/transcribe` mit ready/start/TriggerAck. Es besteht **keine V2-Kompatibilität**
mit dem gepinnten Server `ada13b011e1d3829f78e7f389e3b927795a2b3be` auf `/ws/v2`.
Diese Serverbaseline ist der Vertrag für die Folgepakete. Keine produktive
Serververbindung wird in diesem Baselinecheckpoint als bestanden behauptet.

Serverautorität, Continuous-Stream-Assertions, Feedback-/Loggingnachweise und
Generation-/Sessionguards der Featurelinie sind erhalten. Die reproduzierbare
Streamstartcharakterisierung (zweite Activation sendet nach Finish erneut
start) bleibt sichtbar. Der Wire-/Transportnachzug gehört CV2-010/020, die
Audiolaufzeit CV2-040 und Runtimeintegration CV2-100; finaler Frozen-GUI- und
Hardware-/ASR-Gate CV2-110/IV2-020. CV2-010 startet erst nach unabhängiger
Abnahme, menschlichem Übernahmeprompt und tatsächlichem CV2-000-Aggregat.

## Start-Hotkeyersatz nach R03

Ein erfolgreich registrierter Ersatzhotkey wird erst nach erfolgreichem Corestart in das gewählte Benutzerprofil geschrieben. Bei Corestartfehler bleiben dessen Bytes unverändert; Registrierungen und Hotkeykonfiguration werden zurückgenommen. Bei Speicherfehler wird der gestartete Core gestoppt und der Start verworfen. Deaktivierte Hotkeys und Wake-only schreiben keine Ersatzkombination. Der bereits im V1-Release vorhandene Reihenfolgefehler wurde in [R03](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md) gezielt korrigiert.
