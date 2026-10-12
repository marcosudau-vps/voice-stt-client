# AP-CV2-020 – V2-Transportübergabe

AP-CV2-030 ergänzt die [Mirroranbindung und Resync-API](protocol-v2-mirror.md).
`V2MirrorConnection` installiert die Projektion vor dem Transportstart;
`domain_ready` sperrt Activationcommands während Resync auch unmittelbar vor
dem Senden. `on_protocol_fault(binding)` erlaubt dem angeschlossenen Mirror
Snapshotklärung malformed Events, und `reconnect(binding, reason)` schließt
kontrolliert ausschließlich die aktuelle Session. Bestehende Aufrufer ohne
Adapter behalten ihre bisherige Protokollfehlerbehandlung.

Stand 2026-10-12. `voice_stt_client.core.v2_transport.V2STTSession` ist der
headless V2-Transport; `stt_session.STTSession` bleibt bis CV2-100 der bisherige
App-Pfad. Die separate Klasse verhindert einen halben Protokollwechsel im
fertigen Core. CV2-030/040/050/070 verwenden die hier beschriebenen Interfaces,
CV2-100 komponiert sie mit App/CoreBridge. Kein früheres V1-Testkriterium entfällt.

## Konstruktion, Endpoint und Prozessidentität

`V2TransportConfig` ist immutable. Default:
`wss://stt.voice.marcosudau.com/ws/v2`. Eine explizite URL bleibt unverändert;
Legacypfade erzeugen vor jedem Socketopen `BLOCKED` mit
`legacy_endpoint_requires_migration`, ungültige URLs `invalid_endpoint`.
Kein automatischer Host-/Pfadwechsel, keine Profilschreiboperation.
Die spätere App muss diesen Status anzeigen und die bewusste Profiländerung
anbieten. Allgemeine persistierte V1-Konfigurationsmigration bleibt CV2-070.
Der bisherige Appdefault bleibt bis zur Runtimekomposition an seinem V1-Pfad.

`CLIENT_RUN_ID` entsteht beim Modulimport genau einmal im Prozess; alle
Transportinstanzen und Reconnects teilen diese UUIDv4. Jeder Socketopen erhöht
`generation`; Server-Session-ID kommt allein aus validiertem `hello.accepted`.
`SessionBinding(generation, accepted)` hat redigierten repr und wird für alle
generationgebundenen Audio-/Command-/Mirrorcallbacks benutzt. Nach Verlust ist
die alte Bindingidentität ungültig, auch wenn ein Aufrufer sie noch besitzt.

## Lifecycle und Bootstrap

Alle Methoden und synchronen Callbacks gehören auf denselben asyncio-Coreloop.
`await run()` besitzt Connect-, Receive- und Bootstrap-Tasks. `await stop()` ist
idempotent und unterbricht auch Connect/Bootstrap/Backoff; Close ist begrenzt und
bricht bei Timeout den darunterliegenden Transport ab. Kein Thread-/Qt-Zugriff.

Reihenfolge:

1. CONNECTING → Socketopen → ACCEPTING → sofortiges Hello, beide Suppressionbits
   `true`; konfigurierte Trigger und Wakeauswahl kommen aus dem Configobjekt.
2. Validiertes `hello.accepted` → CONFIGURING → `on_accepted(binding)` mit
   initialem Snapshot und getrenntem LogAccess. Der Empfänger läuft anschließend.
3. Injiziertes `bootstrap(session, binding)` meldet Audioavailability und
   erforderliche Settings über `bootstrap_command`. Zulässig sind nur
   `audio_availability.set`, `session_settings.patch`, `session.snapshot.request`.
   Fehlende Implementierung oder ein fehlgeschlagener Ack blockiert.
4. Transport bestätigt zuletzt die gewünschte Suppressionmaske per Command.
   Erst danach READY. Bis dahin kein Nutzercommand und kein PCM.

Das Bootstrapinterface ist eine explizite Grenze, keine behauptete fertige
Settings-/Audiointegration. CV2-040/070 liefern tatsächliche Services; ein
Settings-Patch darf nicht allein aus einem Timeout als wirksam gelten. Der
Bootstrapservice muss seine benötigten Snapshot-/requested/effective-Prüfungen
abschließen, bevor er zurückkehrt. `bootstrap_command` prüft den Ack, wartet
aber nicht auf einen separaten Snapshot. CV2-030 liefert dessen Korrelation.

Callbacks laufen synchron in Empfangsreihenfolge und dürfen weder blockieren
noch einen Command auf dem Empfängertask awaiten. `on_message(binding, message)`
liefert `Event` (inklusive `UnknownEvent`) und `Snapshot`; fremde Sessions und
alte Bindings werden verworfen. Snapshotreplays werden erneut geliefert.
`on_lost(binding)` kommt genau einmal nach Task-/Socketcleanup; es ist die
Invalidierungsgrenze für den späteren Mirror und Logkoordinator.

## Commands und Mirrorübergabe

`await request(kind, binding=optional, **fields)` gibt `CommandCompletion` zurück:
immutable Originalcommand, typisierter Ack, Generation, `projectable` und
`AckAdvice`. Der Transport erzeugt die ID selbst; externe Envelope-/IDvorgaben
sind verboten. `on_completion(completion)` publiziert vor Auflösung des Pending
Future. Der fachliche Aufrufer behandelt die Advice, ohne automatischen
Ersatzcommand: SERVER_STATE/PHASE/CLOSING, SNAPSHOT, CLIENT_ERROR,
TRIGGER_UNAVAILABLE, AUDIO_UNAVAILABLE, SETTINGS_CONFLICT oder SETTINGS_ERRORS.
Fehlerdetails bleiben im typisierten Ack. `closing_input` sperrt weitere
Refreshs derselben Activation lokal. Clientfehler werden kompakt diagnostiziert.

Der Commandtracker hält Session, Generation, ID, einmal serialisiertes JSON
und Future. Höchstens 16 angenommene Aufrufer einschließlich Domainwaitern;
weitere werden mit `CommandCapacity` abgelehnt. Gleiche Commandtypen serialisieren
ihre Mutationen, verschiedene Domains dürfen gleichzeitig Pending haben.
Pro Ackwartezeit 5 s, maximal ein Retry mit exakt denselben gespeicherten
JSONbytes. Kein Retry nach beantwortetem Ablehnungsack. Timeout/Cancellation/
Sendverlust invalidieren den Socket vor neuer Mutation; ein unbekanntes Ergebnis
kann bereits wirksam sein. Neue Session übernimmt keine Pending-/Commandqueue.

`projectable=false` bei Ackversion unter bereits beobachteter Stateversion oder
Settingsrevision. Ein solcher Ack bestätigt nur Pending; seine Phase/Payload
darf der Mirror nicht anwenden. Unbekannte/duplizierte/späte Acks werden nicht
publiziert. Bei eventlosen erfolgreichen Commands kann der Mirror den
unveränderten Originalpayload ausschließlich versionsgesichert projizieren,
alternativ einen Snapshot anfordern. Events führen nicht zu Ackpending-Verlust.
Die State-/Settings-Watermarks sind Guards, kein ActivationMirror.

## Audio, Fehler und Diagnose

`send_audio(pcm, sample_rate, channels=1, frames=None, binding=optional)` liefert
`False` vor READY/bei alter Binding; sonst validiertes bestehendes
uint32LE/JSON/PCM16LE-Format. Keine Queue in dieser Klasse: der begrenzte
Capture-/Sendadapter ist CV2-040. Fehler/Timeout sperren die Verbindung.
Keine ready/start/stop/Domainping-Nachrichten. WebSocketbibliothek übernimmt
Ping/Pong (20 s Interval/Timeout); lange Finalinferenz hat keinen lokalen Timer.

4400/4406/4409-Konfiguration blockieren. 4408 erlaubt genau einen neuen Versuch;
wiederholte Stille ohne erfolgreiches READY dazwischen blockiert. Der
4408-Episodenzähler wird erst nach vollständigem Bootstrap zurückgesetzt,
nicht bereits bei Admission. `session_limit_reached` bzw. 1013: mindestens 10 s
mit Jitter; 1011/Netzverlust: exponentiell .5–30 s, ±30% Jitter, Deckel 30 s.
Nach erfolgreichem Bootstrap wird der Backoff zurückgesetzt. Connect 15 s,
Admission 30 s, Bootstrap 30 s, Close 3 s sind konfigurierbare lokale Bounds.
Keine automatische Activation, Ergebnisnachladung oder Finalinjektion.

HTTP-Upgradeablehnungen werden vor Sessionbindung eingeordnet: 408 und 5xx
verwenden den normalen begrenzten Backoff; 429 verwendet mindestens 10 s.
Andere Statuscodes (einschließlich 401/403 und Endpoint-/Protokollfehlern)
blockieren als `http_upgrade_<code>`, ohne identische Wiederholungsschleife.
Ein anderweitig ungültiger WebSocket-Handshake blockiert als
`invalid_websocket_handshake`, eine von der Bibliothek abgelehnte URI als
`invalid_endpoint`. Nur die feste Fehlerklasse bzw. der HTTP-Status wird
veröffentlicht; Responseheader, Bodies und Exceptiontexte bleiben außerhalb
der Status-/Diagnosecallbacks. Es wird kein Admin-Key an `/ws/v2` gesendet.

Bestehender `ClientEventEmitter` erhält nur State-/Result-/Guard-/IDdiagnose;
keine Tokens, Texte, PCM oder vollständigen Wireobjekte. Loggingfehler bleiben
isoliert. Logtransport und Credentialpersistenz werden hier nicht angelegt.

## Reproduktion des frühen Serverchecks

`scripts/check_v2_server_transport.py --server-root <bytegleicher Export> --server-repository <Servergit>`
wird mit der Client-Projektvenv ausgeführt. Benötigt im Prüfhost FastAPI,
Uvicorn und Halo, ohne zusätzliche Produktabhängigkeit. Serverquellen stammen
aus `ada13b011e1d3829f78e7f389e3b927795a2b3be`; alle geladenen Pythondateien
werden gegen die Gitblobbytes geprüft. Ein Windows-Archiveexport kann CRLF
enthalten; Exportdateien bei Bedarf über `git show <SHA>:<Pfad>` bytegleich
bereitstellen. Keine vorhandenen Server-Worktrees ändern.

Echte Loopback-TCP-/WebSocketverbindung, unveränderte FastAPI-App, Admission,
Controller/Ledger/Replay/Projektionen. Gepinnte `GateAwareRecorder` und
`AutoScheduler` ersetzen Hardware/Modelle; ein benannter Clientbootstrapadapter
ersetzt noch offene Audio-/Settingsservices. Tempdatenroot, Port 0, begrenzte
Readiness und Cleanup. Die finale Prozess-/Qt-/Hardwarequalifikation bleibt
CV2-100/IV2-010/020.
