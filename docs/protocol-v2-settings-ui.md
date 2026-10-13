# V2-Einstellungen, Admin-Key und Applyentscheidungen (AP-CV2-080)

Der neue `V2SettingsDialog` verwendet die tatsächlichen AP070-Settings- und AP050-Controlservices über einen eigenen Port zum bestehenden asyncio-Core-Thread. Qt bleibt im Main Thread. Der reguläre Appstart wird in AP100 komponiert; der isolierte, reale UI-/Servercheckpoint ist bereits ausführbar. Serverbaseline bleibt `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

## Anschluss und öffentliche APIs

`V2SettingsBridge(loop, factory)` erhält den vorhandenen Coreloop. `factory()` wird dort ausgeführt und erzeugt für jede Dialogöffnung eine neue `SettingsUISession(settings, controls, mirror_connection, credential_store=..., persist_profile=..., wait_timeout=30)`. Alle drei Dienste müssen dieselbe Transport-/Mirrorinstanz verwenden. `SettingsUISession` besitzt keine Qt-Objekte und startet keinen eigenen Thread. Die Factory darf eine nach Close invalidierte Session nicht wiederverwenden.

`V2SettingsDialog(bridge, local_dialog=None, metadata=None)` zeigt lokale Trigger und fünf Controlslots, Sessionwerte und die gesperrte Serververwaltung. Manual und Wake sind gleichzeitig wählbar; mindestens eine Quelle bleibt verpflichtend. Primary-/Secondary-Activeaktionen und der optionale Wake-Pauseslot bleiben auch im Wake-only-Profil erhalten. Der aktuelle Hello-Zustand wird dem gespeicherten Profil gegenübergestellt. Vormerken ist dadurch als noch ausstehende Wirkung erkennbar.

Für den vorhandenen lokalen Dialog `SettingsDialog(config, on_local_apply, v2_local=True)` verwenden. Dieser Modus erhält Verlauf, Zwischenablage, Geräte, Darstellung, Feedback und Logging; Legacybetriebsmodus, alte Zeitfelder, Hotkeygruppen und der ungeschützte Serverreconnect sind ausgeblendet. Der lokale Applycallback darf ausschließlich diese lokalen Änderungen verarbeiten. Änderungen des Serverorigins erfordern in AP100 eine neue Transport-/Settingskomposition, Close des alten Dialogs und einen eigenen Credential-/Authkontext.

`persist_profile(candidate)` ist ein expliziter synchroner Transaktionsport im Core-Thread: erst nach erfolgreicher Validierung werden lokale Profil-/Controländerungen übergeben. Der Callback muss auf Erfolg atomar speichern und darf bei Fehler keinen Teilstand übernehmen. Qt-Widgets dürfen darin nicht aufgerufen werden. Die reguläre Komposition muss ihre bestehende atomare Hotkey-/Konfigurationsübernahme hier koordinieren; der AP080-Checkpoint verwendet die echte `AppConfig.save_user()`-Persistenz in einer temporären Datei, ohne die globale Hotkeyregistrierung der laufenden App umzubauen. Ohne Port wird Apply mit `profile_persistence_required` abgelehnt. Nach normaler Rückkehr übernimmt der Service das Profil und die neue `ControlConfig`, publiziert den Settingsreport und beginnt erst dann die angeforderte Sessionwirkung.

`SettingsUIView` enthält immutable Profil-/Schema-/Requested-/Effective-/Serverdefault-/Katalogdaten, getrennte Revisionen, den aktuellen `ApplyContext`, die konfigurierten Trigger/Wake-IDs der Verbindung und ausschließlich nichtgeheime Credentialmetadaten. `UIReply` trägt Dialogepoch, Request-ID, Operation und View oder einen redigierten Fehlercode. Es werden keine Keys, HTTP-Rohantworten oder Exceptions über Qt publiziert. `request()` erlaubt höchstens eine laufende Anfrage; die UI fragt ihre Projektion alle 500 ms ab, ohne Entwürfe zu überschreiben.

`SettingsUISession.load()`, `load_credential()`, `verify(key=None, remember=False)`, `delete_credential()`, `patch_server(changes)` und `apply_profile(profile, context, choice=None, drain_choice=None, repair_fields=())` laufen auf dem Coreloop. `view()` ist die rein lesende Projektion. Die Qt-Bridge übernimmt Open/Close, begrenzte Futures und queued Replies. `hideEvent` invalidiert synchron die Lease, cancelt die Future, schließt einen offenen Entscheidungsdialog und leert das Passwortfeld. Alte Epochen/Request-IDs werden ignoriert. Coreantworten werden nach Await gegen Generation, Origin und aktive Lease geprüft. Bereits versandte HTTP-Schreibvorgänge können bei Close einen unklaren Ausgang haben; nach Wiederöffnung neu lesen, niemals automatisch wiederholen.

## Werte und Administration

Die Oberfläche verwendet das Server-Schema für Typen, Grenzen, Units, Defaults und Policies. Zahlen werden typstrikt gelesen, Bool/Backend mit Auswahlfeldern und ID-Listen durch Komma getrennt. Requested, Effective, Serverstandard und Schema-Startwert sind eigene Spalten. `calibration=pending` ist ausdrücklich ein unkalibrierter Startwert. `server_restart` wird angezeigt, ohne eine Sessionwirkung zu versprechen.

Noise/VAD sind auf der Sessionseite read-only; vorhandene unsupported Wünsche bleiben im Profil erhalten, werden aber niemals als wirksame Sessionpräferenz angewendet. Änderungen sind nur über die freigegebene Serverdefaultseite möglich. Laufzeitpausen bleiben Controlcommands und werden nicht im Profil gespeichert. Wake-IDs stammen aus dem aktuellen Katalog; fehlende/unavailable IDs bleiben sichtbar und korrigierbar. Katalogladefehler überschreiben keinen Auswahlentwurf. Leere Kataloge haben einen expliziten Hinweis.

`SettingsService.verify_admin(key)` liest den aktuellen Serverdefault und dessen Revision innerhalb des bestehenden Servertransaktionslocks. Es sendet `X-VoiceSTT-Admin-Key` mit einem identischen Wert und verlangt `no_change`, gleiche Revision und leere `changedKeys`. Nur bei 409 erfolgt einmal ein erneuter Read mit neuer Prüftransaktion. Öffentliche GETs oder das Laden eines gespeicherten Keys entsperren die Seite nicht. 401, 403, 409, 422, Serverpersistenzfehler und unklarer Schreibausgang haben unterschiedliche Meldungen. Fehler werden nicht mit einer automatischen schreibenden Wiederholung verdeckt.

`CredentialStore` bietet `read(origin)`, `save(origin, key)` und `delete(origin)`. `credential_target(origin)` normalisiert Scheme/IDNA-Host/effektiven Port und bindet den gehashten Targetname an VoiceSTTClient/v2/admin. Der reale Backend verwendet die Generic-Credential-APIs `CredReadW`, `CredWriteW`, `CredDeleteW` und `CredFree` im aktuellen Windows-Benutzerkonto. Create und Replace benötigen eine explizite geprüfte Speicherung; Delete entfernt den Vault-Eintrag und sperrt den Adminzugang. Ohne Remember bleibt der Key im Prozessspeicher. Ein Storeausfall hat keinen Klartextfallback. Ein vorher gespeicherter Vault-Key bleibt bis zum expliziten Löschen erhalten.

Optionales QSettings erhält nur Targetreferenz und `saved`-Flag. Config, Profil, UIReply/repr und Diagnoseexport erhalten keinen Key. Der Credential-Key bleibt getrennt vom Logtoken und wird nicht an den Audio-WebSocket gesendet. Beim Reopen/Serverwechsel muss wieder geprüft werden; der native Checkpoint belegt Create, verschiedene Replacements, Delete und isolierte Origins.

## Eingabe und Hintergrund-Ergebnisse schützen

`ApplyContext(generation, session_id, activation_id, drain_ids)` bindet die Entscheidung an die tatsächlich dargestellte Session, Vordergrundactivation und ausstehenden Hintergrundactivations. Vor Apply muss dieser Kontext unverändert sein. Der Reconnectbedarf wird gegen den aktuellen Hello-/Effective-Zustand verglichen, damit das erneute Anwenden eines bereits vorgemerkten Profils weiterhin eine Entscheidung verlangt.

Bei offener Activation gibt es ausdrücklich Cancel, Finish mit Ergebniswarten oder Vormerken. Bei Backgrounddrain wird zusätzlich Warten oder ausdrücklicher Verlust gewählt. Close/Cancel des Entscheidungsdialogs ist keine Übernahme. Vormerken speichert nur den Wunsch und lässt Input, Commands und Drain unverändert; es löst keinen späteren automatischen Reconnect aus. Ein erneuter bewusster Apply oder die nächste anderweitig angeforderte Verbindung verwendet das Profil.

Für sofortige Übernahme werden neue Trigger vorübergehend suppressiert. Auf die beiden Acks folgt eine bestätigte Snapshotklärung, bevor das identity-bound Finish-/Cancel-Command an den Controlservice geht. Reconnect erfolgt erst bei bestätigtem Eingabeschluss und terminalem Drain oder ausdrücklicher Drainverlustwahl. Eine inzwischen hinzugekommene Activation/Drain-ID verlangt einen neuen Kontext. Nach 30 Sekunden Ergebniswarten bleibt die Verbindung erhalten, der gespeicherte Wunsch bleibt sichtbar und kann später erneut angewendet werden; dieser lokale Timeout ist kein Server-ASRlimit. Die vorherigen Laufzeitpausen werden auch bei Fehler/Close wiederhergestellt. Es gibt keine lokale zweite Activationautorität.

Eine deaktivierte Wakequelle behält ihre lokale Auswahl. `prepare()` sendet gemäß Hellovertrag dann `wakeWordIds=[]`; Wiederaktivieren verwendet die gespeicherten IDs. Der reale Umschalt-/Draincheckpoint reproduzierte und beseitigte den früheren Verstoß an dieser Anschlussstelle.

Bekannte Migrationskonflikte zu Triggerflags/Mode, Wake-Auswahl, Controls und NA-Zeitfeldern können über die ausdrückliche Reparaturbestätigung ersetzt werden. Der Core erhält unbekannte ungelöste Felder und `retired`-Provenienz; sie werden nicht durch eine bereinigte UI-Mapping still gelöscht. Anschließend werden Migrationdiagnosen neu berechnet. Das Paket führt keine weitere automatische Datenmigration durch.

## Reproduktion und Grenzen

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.\venv\Scripts\python.exe -m unittest tests.test_v2_settings_ui -v
.\venv\Scripts\python.exe scripts/check_v2_settings_ui.py --native --server-root <gepinnter-Serverexport> --server-repository <Serverrepository>
```

Der Checkpoint nutzt echte Produktionsrouten/Controller/Settings am gepinnten Server über lokale TCP-Sockets, Qt im Main Thread und die Clientservices im separaten asyncio-Thread. Recorder/ASR/Modelscheduler und Artefaktprobe sind kontrollierte Grenzen. Die nativen Credentials und das sichtbare Fenster sind reale Windowsvorgänge; Widgeteingaben sind automatisiert. Es gibt keinen Produktivserver-, Mikrofon-, Clipboard- oder ASRqualitätsnachweis. Vollständige Appkomposition und physische Controlregistrierung über die neue Settingsoberfläche bleiben AP100; die reale Gesamtmatrix und empirische Wakekalibrierung bleiben AP-IV2-020.

[AP080-Runreport](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/01_REPORT.md) und [Evidenzindex](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md) führen den kandidatengebundenen Nachweis.
