# V2-Desktop und Runtime – AP-CV2-100 / AP-CV2-110

Stand 2026-10-13. Regulärer GUI- und Headless-Start verwenden `V2Runtime`.
AP100 ist unabhängig abgenommen und kanonisch übernommen; [Runakte](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md).

## Start und Konfiguration

```powershell
.\venv\Scripts\python.exe -m voice_stt_client
.\venv\Scripts\python.exe -m voice_stt_client --config C:\Pfad\client.yaml --headless
```

Der bekannte V1-Pfad `/ws/transcribe` wird beim Zusammenstellen der Runtime
am gleichen Origin auf `/ws/v2` umgesetzt. Alte Queryparameter werden entfernt;
Trigger und Settings kommen aus dem versionierten Profil. Andere Pfade bleiben
erhalten und werden vom V2-Transport gegebenenfalls mit BLOCKED abgewiesen.
`stt.voice.marcosudau.com` bleibt der Serverhost. Versionsnummer 1.0.0 bezeichnet
noch keinen freigegebenen V2-Build; Kandidatenidentität immer zusätzlich angeben.

`AppConfig.load` bewahrt die tatsächlich gelieferten Benutzerwerte für
`runtime_profile`. Paketdefaults werden dadurch nicht als neue Settingswünsche
migriert. Nach erfolgreichem Metadaten-/Bootstrapabgleich wird die originale
Override-Datei bytegleich als `config.yaml.pre-v2.bak` gesichert. Die einzige
neue Profilkonfiguration wird atomar über `AppConfig.save_user` geschrieben.
Bei einer alten AppData-Quelle wird dort gesichert und zum bestehenden neuen
Benutzerziel geschrieben. Lokale Audio-, Overlay-, Sound-, LED-, Clipboard- und
Historypräferenzen bleiben erhalten; ungeklärte/retired Profilwerte bleiben im
V2-Profil sichtbar. Es gibt keine gespeicherten Runpausen, Tokens oder Session-IDs.

## Tatsächliche Komposition und öffentliche Ports

| Port | Verantwortung |
| --- | --- |
| `V2Runtime(config, ...)` | Ein `V2STTSession`, ein `V2MirrorConnection`, Settings, Media, Controls, Results, Logs und Feedback auf derselben Coreloop |
| `RuntimeView` / `get_snapshot()` | Frozen Ansicht aus Generation, Session, Transport, Ready, Closing, MirrorView und ControlConfig |
| `run()` / `shutdown()` | Clipboardworker und Transport starten, Komponenten schließen und ausstehende Transaktionen zusammenführen |
| `primary_dictation_action`, `press_control`, `stop_dictation`, `cancel_dictation` | Servercommands über die vorhandene V2-Control-/Ackautorität |
| `settings_ui_session()` | Je Dialogöffnung eine Lease derselben Settings-/Controls-/Mirrorinstanzen |
| `apply_runtime_config(candidate, *, correlation_id=None)` | Lokale Präferenzen, Audiobarriere, Probe, Workerpersistenz und Rollback; Trigger-/Serveränderung hier abgewiesen; Korrelations-ID rein beobachtend |
| `reconnect_server()` | Bei Foreground oder Drain explizite Entscheidung im V2-Einstellungsdialog verlangen |
| `reinsert_last`, `reinsert_entry`, Historyports | Bereits vorhandene Reinsertion/History/Clipboardqueue; expliziter neuer Versuch, kein neuer Finaldatensatz |
| `V2CoreBridge` | Bestehender CoreBridge-Thread und Commandsignale; V2-Controlintents und Qt-Profiltransaktionen |
| `V2DesktopApplication` | Bestehender SingleInstance-/Tray-/Overlay-/Sound-/LEDrahmen, V2-Rollenhotkeys und V2-Dialog |

AP110 entfernt die ausführbaren V1-Controller-/Session-/Headlessklassen.
Migrationreader, CommandResult und reine alte Darstellungstypen bleiben erhalten;
[Build-/Identitätsnachweis](protocol-v2-release.md).

## Reihenfolge, Guards und Nebenwirkungen

Settingsmetadaten werden über echtes HTTP geladen. Hello fordert zunächst beide
Trigger unterdrückt an. Media meldet die tatsächliche Audioverfügbarkeit;
Settings stellt NA-Wünsche wieder her und bestätigt sie am Snapshot. Erst danach
werden gewünschte Runpausen bestätigt und Transport/Mirror READY. `is_ready`
verlangt passende Generation/Session, operations-ready Mirror und keinen offenen
Snapshotsync. Kein PCM vor diesem Bootstrap. Ein gültiger Sessionzustand mit null
effektivem Trigger bleibt bereit, die Aktivierungsaktion ist gesperrt.

Transport-/Media-/Settings-/Controlsports behalten ihre bestehenden
Bindingguards. Die Qt-Seite plant physische Primary-/Secondaryimpulse aus der
veröffentlichten unveränderlichen Ansicht und hält Generation, Session und
Activation fest; die Coreloop prüft sie erneut. Wakepause hat keinen lokalen
Diktatstart. Der Mirror allein bestimmt Foreground und Hintergrunddrain.
Logs sind diagnostisch und lösen weder Paste noch fachliche Phasenänderungen aus.

Reductioncallbacks laufen zuerst durch Controls und Results, danach durch die
Runtimeansicht und die vorhandene Feedbackengine. `V2ResultService` reserviert
Finalidentitäten vor History/Paste; die bestehende Queue serialisiert Clipboard
und SendInput. Interims gehen ausschließlich in die Segmentvorschau. Disabled
History ändert keine Dedupidentität. Späte Finals von A lassen Foreground B
unverändert. Queuefehler werden thread-safe als sekundäre Diagnose zurückgeführt.
Sound-/LEDfehler ändern weder Session noch Audioverfügbarkeit.

## Threads, Apply und Shutdown

Qt lebt im Main Thread; sämtliche fachlichen Mutable Services auf der bestehenden
asyncio-Coreloop. AudioCapture und TextInjectionQueue behalten ihre eigenen
Worker, LEFX den vorhandenen Adapterworker. Geräteenumeration/Probe und
Konfigurations-I/O laufen auf Workern. GUIupdates kommen über queued Qt-Signale.
Der lokale Dialog bekommt Gerätedaten nach seiner Erstellung asynchron.

Profilpersistenz hat drei Qt-Schritte: `profile_prepare` registriert die neuen
Win32-Rollenkeys transaktional; ein Worker schreibt atomar; `profile_commit`
übernimmt das Profil. Fehler führen zu `profile_rollback` und, falls schon
geschrieben wurde, Wiederherstellung der alten Konfiguration. Der
SettingsUISession-Port unterstützt nun auch awaitable Transaktionen. Dialogclose
unterbricht den atomaren Persistenz-/Adoptionsschritt nicht. Triggerwechsel
nutzen weiterhin cancel/finish/defer und wait/discard mit frischem ApplyContext.
Das echte Servercheckpoint belegt drain-wait vor Reconnect.

Lokaler Settings-Apply bewahrt die bestehende OBS-Auditkette. Die Qt-UI emittiert
`client.settings.apply_started` mit den Apply-Policies und einer neuen
`settings:<id>`-Korrelation. `V2CoreBridge.apply_runtime_config(...,
settings_correlation_id=...)` reicht diese ID an den Core weiter. Nach jeder
angenommenen lokalen Transaktion emittiert `V2Runtime`
`client.settings.runtime_apply`, auch nach Persistenzfehler und Rollback, mit
`session_changed=false`, dem tatsächlichen Audioänderungsflag,
`mode_changed=false`, `success` und `status` sowie aktueller Session/Generation.
Trigger-/Serverprofiländerungen werden an diesem lokalen Port abgewiesen;
sie laufen weiterhin über SettingsUISession. Overlay- oder reine Loggingänderung
löst weder Session- noch Audiorestart aus.

Die UI konsumiert die ID für genau ein `client.settings.apply_completed` mit
Erfolgs-/Fehlerstatus. Busy-Abweisung überschreibt keine laufende Korrelation;
Core-Abweisung und Shutdown schließen einen begonnenen Versuch ebenfalls ab.
Wird der Core nie betreten, entstehen nur Started/Completed, kein erfundener
Runtime-Apply. Doppelte Completion-Signale erzeugen kein zweites Terminalaudit.
Auditdetails enthalten Policies, Änderungsflags und Ergebnis, keine Configwerte.
Alle Emissionen verwenden den vorhandenen nichtwerfenden ClientEventEmitter;
ein Loggingfehler beeinflusst weder Apply noch Rollback.

Shutdown sperrt neue Commands/Outputs, wartet auf begonnene lokale
Konfigurationstransaktionen, beendet Commands und Autostart und schließt
Controls, Settings, Media und Mirror unabhängig. Komponentenclose ist jeweils
auf 7 Sekunden begrenzt; Clipboardjoin auf 2 Sekunden. Die GUI wartet höchstens
10 Sekunden auf ihren Corethread und verarbeitet dabei Qt-Commit-/Rollbackreplies.
Native Keys werden erst danach abgemeldet. Ein Timeout wird als unvollständiger
Shutdown gemeldet; blockierende Betriebssystemtreiber werden nicht als erfolgreich
beendet behauptet. Solche nicht abbrechbaren nativen Calls behalten die vorhandenen
Media-Cleanupgrenzen; sie sind keine zugesicherte OS-Terminierung.

## Nachweisgrenzen

[Integrationstests](../tests/test_v2_runtime_integration.py) verwenden echte
Clientklassen mit kontrollierten Socket-/HTTP-/PortAudio-/Win32grenzen.
[Servercheckpoint](../scripts/check_v2_server_runtime.py) startet den tatsächlichen
Desktop samt Corethread gegen die bytegeprüfte FastAPI-App am Servercommit
`ada13b011e1d3829f78e7f389e3b927795a2b3be`, einschließlich echtem HTTP, Domain-/Log-WS
und temporärer SQLite. Recorder/ASR/Scheduler und physische Ausgaben sind benannte
Grenzen. Reale ASR-/Hardware-/Wahrnehmungsfälle bleiben AP-IV2-020; kompletter
Crossrepo-Gate AP-IV2-010. AP110-Builds und installed/frozen Checkpoint sind im
[Paketnachweis](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md)
selbstqualifiziert; unabhängige AP110-Abnahme und kanonische Übernahme offen.
