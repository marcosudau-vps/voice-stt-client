# AP-CV2-040 – Continuous-Audio und separater Logzugriff

Stand 2026-10-12. `V2MediaConnection` verbindet die vorhandene `AudioCapture`
und `DualSessionCoordinator` mit dem headless `V2STTSession`-Pfad. Der
Domainmirror bleibt allein für geordnete V2-Liveevents zuständig. Qt-Komposition,
Gerätemonitor/LED-Hardware und Sessionsettings werden durch CV2-100/070 bzw.
die Hardwareintegration angebunden. Der bisherige Appstart bleibt unverändert.

```python
session = V2STTSession(config)
mirror = V2MirrorConnection(session)
media = V2MediaConnection(session, capture, settings_bootstrap=bootstrap_settings)
try:
    await session.run()
finally:
    await media.close()
    await mirror.close()
```

Beide Adapter vor `run()` anbringen. Wenn Einstellungen benötigt werden, den
Bootstrap an `settings_bootstrap` übergeben, nicht bereits an den Transport.
Die Media-Konstruktion installiert diesen Bootstrap und verkettet bestehende
Status-/Accepted-/Lost-Callbacks. `AudioCapture.probe()` prüft das Gerät ohne
Aufnahme; negative Verfügbarkeit wird vor der Wiederherstellung der gewünschten
Suppression bestätigt. Bei Geräte-/Muteverlust wird negative Availability noch vor dem möglicherweise blockierenden nativen Stop bestätigt. Capture beginnt erst bei READY. Ein Gerätefehler beim
Öffnen meldet anschließend false; erfolgreiche Wiederanbindung meldet true.

Audio läuft in idle, waiting, recording, followup und draining. Finish, Cancel
und Wakepause ändern diesen Datenpfad nicht. Lokales VAD und Wake-Inferenz
besitzen keine Aufnahmeautorität. Die bestehende Capture-/PortAudio-Logik,
Diagnosezähler und Hintergrundverarbeitung bleiben erhalten.

`set_device_available(bool, binding=...)` und
`set_hardware_muted(bool, binding=...)` gehören auf den asyncio-Coreloop. Ein
überholtes optionales Binding wird abgewiesen. Jede Änderung sperrt sofort
lokale Samples, erhöht den lokalen Queue-Epoch und verwirft den Puffer. Erst
bestätigte Audioverfügbarkeit und aktuelles READY öffnen ihn wieder. Der Server
entscheidet über das Cancel der offenen Activation; ältere Backgroundfinals
bleiben erhalten. Mute-off setzt keine Trigger-Suppression zurück und startet
keine Activation. `set_led_available(bool)` verändert ausschließlich die
LED-Diagnose. Bei gemeinsamem USBverlust beide Geräteports melden; der
Hardwaremonitor und physische Nulladapter bleiben ihrem späteren Owner.

`BoundedAudioQueue` validiert int16-LE-PCM samt Rate, Kanälen und Frames. Default
500 ms, höchstens 128 Pakete/4 MiB; älteste Pakete werden bei Überlauf verworfen.
Einzelpakete über dem Zeitbudget werden abgewiesen, Pop verwirft über 500 ms
alte oder generationfremde Pakete. Der vorhandene Capturepuffer wird ebenfalls
auf 500 ms konfiguriert (bei 40-ms-Chunks zwölf Pakete). Das sind zwei getrennte
begrenzte Stufen; zusammen höchstens rund eine Sekunde gepuffertes Audio,
zusätzlich ein transportseitig begrenzter laufender Send. Die Senderqueue
besitzt höchstens einen ausstehenden Loop-Weckcallback. Drei aufeinanderfolgende
Sends mit erneutem Queueüberlauf führen zu kontrolliertem Reconnect. Der
Berstentest mit 2000 Paketen und der langsame Socket belegen die Grenzen.

`counters()` liefert sent, gated, overflow, stale, invalid, queue_ms,
capture_failures, audio_available, led_available und log_failure. Keine
PCM-Inhalte, Tokens oder Transkripte in diesen Diagnosewerten. Bei Netzverlust
werden Samples sofort gesperrt und Queue/Callbacks invalidiert. Der Transport
räumt Pending-Commands auf; der Mirror markiert offene Ausgaben unterbrochen
und erhält veröffentlichte Texte. Neue Session/Generation erhält neue IDs und
Logcredentials. Gewünschte Suppression bleibt bestehen; gewünschte
Sessionsettings werden über den Settingsbootstrap wiederhergestellt.

Der Logbootstrap verwendet nur `hello.accepted.logAccess`, prüft WebSocket-
und Historypfad gegen denselben Origin und akzeptiert unavailable ohne übrige
Capabilityfelder. Kein Authfallback. Token bleibt im `EventStreamAccess`, wird
nur im ersten Subscribe gesendet und in repr sowie Fehlermeldungen redigiert.
Snapshotresync liefert keine Credentials und ersetzt den bestehenden Logzugriff
nicht. Ablauf/Logfehler stoppt den Logpfad unabhängig vom Audio; neue Session
liefert neues Material. Loghistory/Replay besitzt keine Domain- oder
Injektionswirkung. Integer oder opake String-`segmentId` sind nur Logmetadaten.

Cursorpersistenz bleibt atomar und speichert erst bestätigte Downstreamarbeit.
Zusätzlich zur bisherigen Origin-/Instance-/Protokollbindung werden Session
und sortierte Channels abgeglichen. Schema 1 akzeptiert historische Records
weiter; unscoped Altbestände werden für einen scoped Zugriff nicht wiederverwendet
und beim bloßen Lesen nicht gelöscht. Keine Änderung an config.yaml, History-
SQLite, Registry oder Credentialspeicher. Ein neues Subscribe beginnt bei
abweichender Bindung mit Cursor 0. Gefilterte globale Cursorsprünge sind erlaubt;
Retentiongap überspringt keinen Cursor blind und erhält surviving Events.

`close()` ist nach vollständig erfolgreichem Cleanup idempotent. Lokale Gates
schließen sofort; Transport stoppen, Sender/Lifecycle joinen, laufenden nativen
Geräteaufruf joinen und Capture stoppen. Taskjoins und native Operationen haben
je das Shutdownbudget (Default 3 s). Der unabhängige Logshutdown liegt im
äußersten finally, sodass auch Cancellation während des Task-Joins ihn erreicht.

Logclose läuft in einem eigenen geschützten Task. Owner-Cancellation, auch
wiederholte, wird bis zu dessen Abschluss aufgeschoben und danach weitergegeben;
sie kann nicht die bereits vom Koordinator abgetrennten Ressourcen verlieren.
Das feste Logbudget beträgt Shutdownbudget plus 3 s und wird durch Cancellation
nicht verlängert. Timeout wird sichtbar gemeldet; ausstehende Media-/Native-/
Logtasks bleiben für erneutes `close()` erreichbar. Ein Logretry joint denselben
Shutdowntask und ruft nicht den bereits als shutdown markierten Koordinator
neu auf. Erfolgsstatus entsteht erst bei vollständig erfolgreichem Cleanup.
Parallele Close-Aufrufe sind serialisiert. Nativer Treiberhang bleibt nicht hart
durch asyncio abbrechbar; unvollständiges Cleanup erfordert Retry durch den Owner.

Nachweise: [Runreport](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-040/RUNS/R05-KORREKTUR/01_REPORT.md)
und [Windowsqualifikation](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-040/RUNS/R05-KORREKTUR/EVIDENCE/windows-validation.json).
Der echte Servercheckpoint nutzt ada13b0, reale FastAPI/WebSockets/SQLite/
PCM-Decodierung/Resampling/Controller, synthetische PortAudioeingabe und einen
modellfreien Recorder. Reales Mikrofon, Wake-Engine, ASRqualität und physische
USB-/LED-/Mutefälle bleiben spätere IV2-Nachweise.

## AP-IV2-020 – Native Recovery

Native Probe-/Start-/Stop-/Rekonfigurationsaufrufe werden vollständig serialisiert.
Ownercancellation behält den laufenden nativen Task als Barrier. Ein nachträglicher
Fehler wird beobachtet und der fertige Task danach freigegeben, damit spätere
Gerätewiederkehr möglich bleibt.
