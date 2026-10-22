# V2 Settingsservice und Profilmigration (AP-CV2-070)

Der Core bietet versionierte Profile, die öffentlichen Settings-/Wake-Katalogrouten und bestätigte Sessionpatches. Die Desktop-App verwendet diesen Pfad erst nach der Komposition in AP-CV2-100. Die implementierte AP080-Oberfläche samt Credential-/Applyports ist in [protocol-v2-settings-ui.md](protocol-v2-settings-ui.md) beschrieben. Der Serververtrag ist auf `ada13b011e1d3829f78e7f389e3b927795a2b3be` gepinnt.

AP080 korrigiert die Anschlussgrenze für deaktiviertes Wake: gespeicherte lokale Wake-IDs bleiben im Profil, `prepare()` sendet bei `wake_word=False` jedoch die vertragsgemäß leere Wireauswahl. Wiederaktivierung verwendet die erhaltenen IDs.

## Öffentliche APIs und Anschluss

`voice_stt_client.core.v2_profile.V2Profile` enthält `schema_version=2`, `manual`, `wake_word`, `wake_word_ids`, `desired_settings`, `controls`, `unresolved`, `retired` und `issues`. `require_ready()` sperrt ungültige Trigger, ungelöste Migration und Controlkonflikte. Diese Felder enthalten keine Session-ID, Command-ID, Laufzeitpause oder Zugangsdaten.

`voice_stt_client.core.settings_service.SettingsService(session, profile)` wird einmal vor `session.run()` am asyncio-Core angehängt. Er installiert `session.prepare` und verkettet die bestehenden `on_accepted`, `on_message` und `on_lost`-Callbacks. `V2MirrorConnection` und `V2MediaConnection` bleiben die vorhandenen Lifecycle-/Audiokomponenten.

```python
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_media import V2MediaConnection
from voice_stt_client.core.settings_service import SettingsService

# Im Core-Thread; profile stammt aus der expliziten Migration/Profilpflege.
session = V2STTSession(V2TransportConfig(url="wss://stt.voice.marcosudau.com/ws/v2"))
mirror = V2MirrorConnection(session)
settings = SettingsService(session, profile)
media = V2MediaConnection(session, capture, settings_bootstrap=settings.bootstrap)
settings.on_report = deliver_immutable_report
await session.run()
```

`capture` ist eine bestehende `AudioCapture`-Instanz. `deliver_immutable_report` läuft im Core-Thread; die spätere UI muss Reports über ihre Qt-Bridge zustellen. Für Shutdown Transport stoppen und Media, Mirror und `await settings.close()` schließen. Settings übernimmt keine Qt-Widgets, Hotkeyregistrierung oder automatische Reconnectentscheidung.

Die Reihenfolge pro neuer Verbindung lautet: CONNECTING/Generation erhöhen → `prepare` liest Schema, Serverdefaults und ganzen Katalog → Profil/kanonische IDs/gemeinsames Backend prüfen → Hello mit beiden temporären Suppressionbits → Accepted/Snapshot → Medienverfügbarkeit bestätigen → NA-Patch und neuen Snapshot bestätigen → gewünschte Laufzeitpausen durch den Transport wiederherstellen → READY/Audio. Fehler, fehlender Snapshot oder weiterhin ausstehende NA-Werte lassen keine Audiostartfreigabe zu. Profilflags ändern die konfigurierte Triggerunterstützung; vorhandene Controlpausen bleiben eine andere Domäne.

## Wünsche, Policies und Revisionen

`load_metadata()` lädt die drei öffentlichen GET-Routen. `Setting` ist unveränderlich und stellt Scope/Auth/Typ/Grenzen/Default/ApplyPolicy/Calibration bereit. Es gibt 18 Basisschlüssel, 16 Sessionfelder und 15 Serverdefaultfelder. `server_restart` kann als Policy gelesen werden, ist kein eingebauter Basisschlüssel. Der Service verwendet den bestehenden V2-Codec für Schema, Serverread und Patchantworten.

`set_desired(changes)` prüft ein vollständiges NA-Bundle und aktualisiert atomar nur lokalen Intent. `await apply_session()` liest zuerst einen bestätigten Sessionsnapshot und schreibt ausschließlich die elf `next_activation`-Schlüssel. Bei Revisionskonflikt erfolgt genau eine Neuberechnung nach neuem Snapshot mit neuer Command-ID. Nach erfolgreichem Ack ist ein frischer Snapshot erforderlich. Während einer laufenden Activation bleiben deren Startwerte unverändert. Nach `settings.changed`, `input.closed` und `activation.started` aktualisiert ein zusammengefasster Snapshotread die Projektion; auch automatisch geschlossene Inputs werden berücksichtigt.

`report()` und `on_report` liefern einen unveränderlichen `SettingsReport` mit Generation, Session-ID, separater Session-/Serverrevision, `desired`, `requested`, `effective`, `pending`, `unsupported`, Katalogrevision und Stalestatus. `pending` bedeutet Wunsch weicht vom bestätigten wirksamen Wert ab; es ist kein erfundener Serverstatus. Die beiden NS-Noise/VAD-Schlüssel werden als `not_individually_startable_use_server_default` berichtet. Sie lassen sich nicht durch Sessionpatch oder Reconnect als individuelle Präferenz durchsetzen. RuntimeSuppression schreibt ausschließlich der vorhandene Controlcommand; Settingspatches dafür werden abgelehnt.

`select_wake_words(values)` löst IDs, Anzeigenamen und explizite Aliase eindeutig mit Trim/Casefold auf, dedupliziert und validiert die gesamte Auswahl. Exakte kanonische IDs haben Vorrang. Es wird kein Patch gesendet: Auswahländerungen gelten beim nächsten Hello. Die spätere UI entscheidet über Weiterbetrieb, Inputabschluss/Drain und bewussten Reconnect. Unavailable/unknown/mehrdeutige IDs und fehlendes gemeinsames Backend ergeben Fehler, keinen Teil- oder Ersatzbetrieb. `WakeCatalog.entries` veröffentlicht nur öffentliche Metadaten einschließlich Backendgründen, keine internen Artefaktpfade. Die Revision ist eine Ganzzahl. Availability-Events markieren den Cache sofort stale; ein alter HTTP-Read darf ihn nicht frisch erklären. Ein begrenzter Refresh versucht höchstens zweimal, die angekündigte Revision zu lesen.

`await read_server()` liest den eigenen Serverrevisionsraum. `await patch_server(changes, admin_key=...)` liest davor neu, validiert serverzulässige Felder, sendet genau einen PATCH und bestätigt per Read. 401/403/409/422/500 werden getrennt als `SettingsError.code/status` ausgegeben. Nach Fehler oder unbekanntem Ausgang wird erneut gelesen, niemals blind nochmals geschrieben. Der Fehler bleibt ein Fehler, selbst wenn der Read einen gewünschten Wert findet. Ein weiterer Schreibversuch ist eine neue bewusste Transaktion. Der Schlüssel wird nur dem HTTP-Aufruf übergeben und nicht persistiert.

Alle Antworten werden nach Await durch Generation-/Bindingprüfung geschützt. Ältere Snapshot-State-/Settingsrevisionen und Antworten verlorener Sessions dürfen nicht publiziert werden. Reportcallbacks der Accepted-/Snapshotverarbeitung laufen vor dem verketteten Messagecallback; alte Accepted-/Lostcallbacks werden vor deren abschließender Reportpublikation aufgerufen. Availability markiert stale und plant den Refresh, ohne den Messagecallback zu blockieren. `last_metadata_error` kennzeichnet fehlgeschlagene Hintergrundreads.

## Explizite Migration und Reparatur

`migrate_profile(raw, catalog=None)` ist rein und liest die tatsächliche Nutzermapping vor dem Layern von Defaults. Explizite Triggerflags haben Vorrang vor V1 `mode`; unbekannte Modes, triggerlose Profile und widersprüchliche Controls bleiben sichtbar blockiert. Nur bewiesene initial-/followup-Sekundenwerte werden exakt über Decimal nach Integer-ms konvertiert; widersprüchliche lokale und Sessionwerte bleiben ungelöst. V1 extension/warning und andere nicht eindeutig abbildbare Timingfelder bleiben in `retired`; sie werden keinem V2-Watchdog zugeordnet.

Wake-Freitext wird nur am Komma getrennt und mit einem echten Katalog kanonisiert. Offline bleibt der Rohwunsch in `unresolved`; eine spätere Katalogmigration kann ihn auflösen. Bereits versionierte Profile werden niemals erneut aus V1 `mode`/extension abgeleitet. Unavailable IDs bleiben erhalten und blockieren Admission. Reparatur setzt explizit die betreffenden Profilwerte und entfernt ausschließlich tatsächlich gelöste `unresolved`-Einträge; anschließend erneut validieren. Es gibt keinen stillen Reset auf Defaultprofile.

`migrate_config_file(path, catalog=None)` schreibt ausdrücklich in die lokale Nutzerdatei: byteidentische Sicherung neben der Datei (`<name>.pre-v2.bak`), temporäre Datei im selben Verzeichnis, fsync und atomarer Replace. Wiederholung desselben Ergebnisses schreibt nicht erneut. Scheitert Replace, bleiben Original und Backup erhalten. Alle V1-/Geräte-/TLS-/Hotkey-/Feedback-/Clipboardfelder bleiben erhalten. `AppConfig.load()` führt keine Migration aus, lädt/speichert aber das optionale `v2_profile`. Ungültige erhaltene V1-Felder können weiterhin die V1-Validierung sperren; der Reparaturpfad arbeitet deshalb direkt mit der Rohmapping und dem V2-Profil. Nach dessen Reparatur muss die spätere Profilpflege explizit persistieren; Serviceoperationen selbst schreiben keine Configdatei.

## HTTP und Beweisgrenzen

`SettingsHTTP` verwendet Standardbibliothek/`asyncio.to_thread`, verifiziert TLS, akzeptiert ausschließlich den Origin eines credentialsfreien `/ws/v2`-URLs ohne Query/Fragment und feste V2-Routen. Unverschlüsseltes HTTP ist nur auf Loopback zulässig. Defaulttimeout 5 s, Responsegrenze 1 MiB (konfigurierbar bis 4 MiB), keine Redirects. Nach Timeout oder Cancellation wird ein noch laufender nativer Worker behalten; weitere Requests können keine Workerflut erzeugen. Der Coreloop bleibt frei. Fehlermeldungen enthalten keine Keys, URLs, Rohantworten oder ursprünglichen Exceptions.

Die [AP070-Evidenz](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md) belegt HTTP/WS/Media/PCM auf der Produktions-Serverapp und Regression. PortAudio, Modelle und Recorder sind kontrollierte Grenzen. Die empirische Wake-/Nutzsprachgrenze und Kalibrierung bleiben AP-IV2-020; `calibration=pending` ist keine Empfehlung optimaler Werte. Es gibt keine zusätzliche Dependency, Credentialpersistenz oder Serverproduktänderung.

## AP-IV2-020 – HTTP-Recovery

Fehlerantworten werden anhand des HTTP-Status eingeordnet, ohne ihren Body als
Erfolgs-JSON zu lesen. Abgerissene Erfolgsübertragungen sind GET-Transportfehler
bzw. unklare Mutationsergebnisse. Nur der idempotente Metadaten-Preflight darf
temporäre GET-Fehler in einen neuen Verbindungsversuch überführen; HTTP-PATCH
wird dadurch niemals automatisch wiederholt. Ungültiges JSON bei HTTP200 und
TLS-Zertifikatsfehler bleiben blockierend. Fehlende Bootstrap-Snapshots führen
zu einer neuen Session mit erneuter vollständiger Bestätigung.
