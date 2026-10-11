# K-04 – Logstream, Authentifizierung und Recovery

Geltung: exakte Serverfelder und Serverlimits sind verbindlich; interne Clientrepräsentationen sind Vorschläge, lokale technische Werte begründbar anpassbare Startwerte gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Produktverhalten und Schutzwirkungen bleiben Pflicht.

## 1. Drei getrennte Pfade

- `/ws/v2`: aktuelle Sessiondomäne, Audio, Commands, geordnete Liveevents. Keine Domain-Eventhistory und kein Replay.
- `/ws/logs` plus `/api/logs/*`: committed SQLite-Logereignisse, replaybare Diagnosehistory, eigene Autorisierung und Cursor.
- REST-V2-Settings: öffentliches Schema/Read, adminpflichtige Änderung.

Der V2-Spiegel erhält niemals seine Runtimeautorität aus dem Logstream. Logausfall beeinflusst Audio/Controls nicht; Audioausfall invalidiert die alte Domainsession, unabhängig von einem noch funktionierenden Logsocket. Ein nachgeliefertes Logfinal darf weder Text automatisch injizieren noch eine neue Sessionphase verändern.

## 2. Bootstrap-Logzugriff

`hello.accepted.logAccess`:

```text
available, websocketPath, historyPath, accessToken,
sessionId, expiresAt, logProtocolVersion=2,
deliveryMode=sqlite_first, replayAvailable=true,
serverInstanceId, oldestCursor, latestCursor
```

Bei unavailable: `available=false`, `code`, `reason`, kein Token; übrige Capabilityfelder nur verwenden, wenn tatsächlich vorhanden. Verfügbarkeit des Logstores ist keine STT-Admissionvoraussetzung. Resync-Snapshots enthalten kein neues `logAccess`.

Token: zufällig, eigene Session, Channels audit/transcription/performance, 24 Stunden innerhalb des aktuellen Serverprozesses. Kein system-/Fremdsessionrecht. Nur im Speicher, redigierter repr und keine URL, Config, Registry oder Logs. Serverneustart invalidiert Token und serverInstanceId; nach Domainreconnect neues Bootstrapmaterial verwenden. Ein noch gültiges altes Token berechtigt ausschließlich alte Sessionhistory.

Pfadvalidierung: WebSocket- und Historypfade auf denselben konfigurierten Origin auflösen. Keine Tokenweitergabe an einen abweichenden Host aus manipuliertem Bootstrap. Credential und Logtoken bleiben fachlich und hinsichtlich Zugriff/Lebensdauer getrennt; eigene Datentypen sind eine mögliche Umsetzung.

## 3. Subscribe und Cursor

Erste `/ws/logs`-Nachricht:

```json
{"type":"subscribe", "accessToken":"<memory-only>",
 "sessionId":"20000000-0000-4000-8000-000000000001",
 "channels":["audit","transcription","performance"], "afterCursor":0}
```

Antwortfolge: `log.hello` → `log.subscribed` → 0..n `log.event` im Replay → `log.replay_completed` → weitere Liveevents. `log.hello` enthält Protokoll/Mode, Instance, oldest/latestCursor und filterbezogenen `retentionCursor`. `log.subscribed` bestätigt authorizationScope, channels, sessionId, allChannels/allSessions. Sessiontoken akzeptiert keine globale Administration.

`log.keepalive` ist Inaktivitätsnachricht; `{"type":"ping"}` ist nur auf diesem Socket zulässig und erhält `log.pong`.

- Cursor ist globale SQLiteappendposition, **nicht** `eventSeq` und nicht lückenlos im gefilterten Stream.
- Cursorpersistenz nach erfolgreicher Downstreamverarbeitung; Cachebindung an Origin, serverInstanceId, Session und Filter. Änderung des Filters darf nicht alte Cursorarbeit als bereits verarbeitet behandeln.
- `log.gap(reason=retention)` bedeutet gelöschte relevante History, kein Netzfehler; fehlende Spanne anzeigen und überlebende Events normal übernehmen. Nicht blind auf oldestCursor oder retentionCursor springen.
- `log.error(code=cursor_ahead)` verlangt Reset-/Instanceklärung. `event_store_unavailable` → Close 1011; Protokoll-/Authfehler → Close 1008. Logreconnect erfolgt unabhängig von STT.

HTTP-History mit `X-VoiceSTT-Log-Token`; Filter channels/events/sessionId/transcriptionId/from/to/afterCursor/limit, maximal limit 1000. Antwort sortierte Events, nextCursor, oldestCursor, latestCursor, retentionCursor, authorizationScope, allSessions, deliveryMode. Authscope serverseitig erzwungen. History ist Diagnose, kein Ersatz für fehlende Domainsegmente.

Logschema führt Session-, Transkriptions- und Recordingkorrelation getrennt. Es darf kompakte Recorder-IDs und Integersegmentfelder besitzen. Diese werden nicht als V2-`segmentId`-UUID interpretiert. Bei fehlender expliziter Zuordnung nur Session-/Recordingdiagnose, keine heuristische Übernahme auf die aktuelle Activation.

## 4. Admin-Auth und Credential-Speicher

HTTP akzeptiert `X-VoiceSTT-Admin-Key`, `Authorization: Bearer ...`, für V2settings auch denselben Guardalias `X-Admin-Key`. Desktopstandard verwendet `X-VoiceSTT-Admin-Key`. Der Key gehört nicht auf den Audio-WebSocket. `/ws/v2` selbst prüft keinen Anwendungs-Authheader; eine Proxyberechtigung ist gegebenenfalls eine gesonderte Deploymentkonfiguration.

Konfigurierter Serverkey: fehlend/falsch → 401. Kein Serverkey: Remoteverwaltung → 403, Loopback-Test-/Lokalanfragen können zugelassen werden. Der Client darf daraus keinen fiktiven `admin.login`- oder `verify-admin-key`-Endpunkt machen. Öffentliche GETs beweisen keinen gültigen Key.

Verbindliche Clientprüfaktion: nach Laden der Serverwerte ein **No-change-PATCH** auf einen tatsächlich vorhandenen Serverdefault mit aktueller Serverrevision und identischem Wert. Der Guard prüft dabei den Key; `no_change` verändert keinen Default. Bei Revisionskonflikt Werte neu lesen und höchstens einmal neu prüfen; kein automatischer schreibender Wertwechsel. Erfolgreiche öffentliche Reads entsperren die Adminseite nicht.

Persistenzoption nur über Windows Credential Manager. Targetname an normalisierten Serverorigin und Anwendung binden; QSettings hält ausschließlich „gespeichert vorhanden“ und Zielreferenz. Anlegen, Ersetzen und Löschen müssen in der UI möglich sein. Fehlender Credentialstore → ausschließlich Prozessspeicher. Kein Klartextfallback, keine Secrets in Fehlermeldungen, Clipboard oder Diagnoseexporten. Serverwechsel sperrt Seite und lädt eigene Credentials.

## 5. Verbindungsaufbau ohne Aktivierungsfenster

Für jede neue Verbindung:

1. Neue connectionGeneration; bestehende clientRunId und gewünschte Laufzeitsuppression behalten. Benutzertrigger lokal sperren.
2. Katalog/Schema für benötigte Quellen prüfen; nur kanonische Auswahl senden.
3. `hello` mit vorübergehend **beiden** Suppressionbits true senden; dies ist eine lokale Bootstrapmaßnahme, keine Änderung des gewünschten Pausenzustands. Mindestens ein configured Trigger bleibt true.
4. Snapshot validieren und Logzugriff separat binden. Noch kein Mikrofonframe senden.
5. Tatsächliche `audioAvailable` melden, falls vom initialen true abweichend; gewünschte NA-Sessionwerte atomar patchen; ggf. Snapshot für bestätigte requested/effective lesen.
6. Gewünschte Run-Suppressionmaske per Command wiederherstellen; alle notwendigen Acks erfolgreich.
7. Transport ready setzen, kontinuierliches Audio freigeben und Bedienung entsprechend trigger.effective/audioAvailable aktivieren.

Bei Konfigurationsfehler bleibt der Client sichtbar configuring/blocked, sendet kein Audio und eröffnet keine manuelle Activation. Nie aus einem Timeout eine erfolgte Settingsänderung ableiten. Suppressiondesired und Bootstrapmaske sind zwei getrennte lokale Felder.

## 6. Sessionverlust, Geräteverlust, Mute

**Server-/Netzwerkverlust:** kein garantiertes letztes Event. Alle offenen Pending-Commands als transport_lost abschließen; Audio-Sendqueue/Resyncpuffer alte Generation verwerfen; offene Activations und nichtterminale Segmente als lokal interrupted/unvollständig kennzeichnen. Keine alten Ergebnisse später automatisch nachladen/injizieren. Veröffentlichte Texte bleiben. Backoff/Jitter gemäß Close-Matrix in K-01, neuer Hello-/Settingsbootstrap.

**Audiogerät verloren oder Hardware-Mute:** PCM sofort lokal sperren; `audio_availability.set(false)` auf vorhandener Session. Das cancelt nur die offene Activation und sperrt neue Aufnahme. Ältere Backgroundactivations bleiben bestehen. Gerätewiederanbindung lokal, dann korrektes Format und availability=true melden; keine neue Activation ohne Trigger. Hardwaremute und Wakepause bleiben unabhängige lokale Zustände. Mute-off setzt keine Benutzerpause zurück.

**LED/ReSpeaker-Ausgang verloren:** LEDadapter degradieren/wiederanbinden. Ist das Mikrofon separat weiterhin erreichbar, keine Audioavailabilityänderung und kein Cancel. Bei gemeinsamem USBgerät tatsächliche Audio- und LEDverfügbarkeit separat prüfen.

**Settings-Reconnect:** Bei offener Eingabe explizite Benutzerwahl sofort cancel / geordnet finish / vormerken. Zusätzlich ausstehende Backgroundresultate nennen; entweder bis zu deren Terminal warten oder ausdrücklich Ergebnisverlust akzeptieren. Schon drainende Activations sind über `cancel` nicht adressierbar. Ohne Wahl wird kein impliziter Sessionverlust ausgelöst.

**Shutdown:** Bedienung sperren, Tasks begrenzt stoppen, Socket schließen, Clipboard-/LEDqueue kontrolliert herunterfahren, Benutzerwünsche getrennt von transienten Pausen persistieren. Kein unendliches Warten auf Finals; verbleibende Ausgaben als interrupted kennzeichnen.

## 7. Lokale Timeouts (technische Startwerte)

Socketconnect 15 s; Hello sofort; Annahmewartezeit 30 s; Commandack 5 s; Snapshot 5 s mit höchstens einem weiteren Versuch; normaler Reconnect 0.5–30 s mit ±30% Jitter; Sessionlimit mindestens 10 s. Diese Werte sind konfigurierbare technische Startwerte, mit begründetem Latenz-/Last-/Fehlertest anpassbar; die gewählten Begrenzungen werden im Runreport und in den tatsächlichen Tests festgehalten. Die serverseitigen Aktivierungsfristen kommen ausschließlich aus K-03. Eine lange Finalinferenz darf keinen lokalen Finish-/Cancel-/Reconnectautomatismus auslösen.

## 8. Quellen

`protocol_v2/connection.py`, `server.py:admin_auth_error`, `/ws/logs` und Loghistoryrouten; `VoiceSTT_server/event_logging.py`, `docs/structured-logging.md`; Clientbaseline `session_coordinator.py`, `event_protocol.py`, `event_stream.py`, `event_cursor_store.py`, `core/observability/`. Pinned Dateien im [Quellenmanifest](../../EVIDENCE/source-manifest.json).
