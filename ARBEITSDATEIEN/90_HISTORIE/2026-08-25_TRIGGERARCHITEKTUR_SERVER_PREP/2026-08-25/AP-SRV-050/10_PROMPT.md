# SPEKULATIVE VORIMPLEMENTIERUNG – AP-SRV-050

## 1. Rolle

Du implementierst spekulativ einen möglichst großen Teil von
`AP-SRV-050 – Settings-Control-Plane und Servermetadaten`.

Das ist echter Produktcode + echte Tests, aber noch kein kanonischer AP-Candidate.
Ziel ist ein eigenständiger Settings-Domainbaustein, den der spätere SRV-040-Wirehandler
nur noch aufrufen muss.


## Gemeinsamer Referenzzustand

- Repository: `marcosudau-vps/voice-stt-server`
- Start-SHA: `db3d2b49539afbf4812d90e13f26f099b9314fe9`
- Start-Tree: `579d5f5dfb2e3a2ab4e7891cf1b233c7fa8422e3`
- C1 ist ein veröffentlichter, aber nicht final abgenommener AP-SRV-030-Candidate.
- Die kanonische SRV-030-Korrektur läuft getrennt.
- Dieser Prep-Branch darf C1 nicht amendieren und nicht pushen.

### Normative Quellen im Clientrepo – NUR LESEN

`P:\GithubRepos\marcosudau-vps\voice-stt-client\ARBEITSDATEIEN\10_AKTUELL\EINHEITLICHE_TRIGGERARCHITEKTUR\`

Mindestens vollständig lesen:

- `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`
- `PLANUNG/ZIELBILD.md`
- `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md`
- `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`
- `PLANUNG/VERTRAGSVEKTOREN/protocol-v2-vectors.json`
- `PLANUNG/IMPLEMENTIERUNGSPLAN.md`
- `NACHVERFOLGUNG/TRACEABILITY.md`
- `NACHVERFOLGUNG/FUNDE.md`

Serverseitig mindestens:

- `AGENTS.md`
- `docs/.archiv/README.md`
- `docs/einheitliche-triggerarchitektur.md`
- `docs/module-map.md`

Keine Clientdatei verändern.

Bei Widerspruch:
1. Frozen Contract / bestätigte Entscheidungen
2. Frozen Wire-Schema
3. Implementierungsplan
4. Code
5. Tests
6. alte Analysen

Tests können falsches Altsoll enthalten.


## 2. Arbeitsort / Git

Worktree:
```text
P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\prep-srv-050
```

Branch:
```text
prep/AP-SRV-050/settings-control
```

Start:
```text
db3d2b49539afbf4812d90e13f26f099b9314fe9
```

Preflight:
```powershell
git branch --show-current
git rev-parse HEAD
git rev-parse HEAD^{tree}
git status --short
```

Erwartung Branch/HEAD/Tree exakt wie oben/C1.
Bei Abweichung `BLOCKED`.

Kein Push, kein Rebase, kein Merge, kein neues venv.

## 3. Bestehende Grundlage wiederverwenden

Vor Neuentwurf den tatsächlichen Servercode lesen und vorhandene Strukturen wiederverwenden:

- `ServerSettings`
- `ACTIVE_RUNTIME_SETTINGS`
- `NEW_SESSION_RUNTIME_SETTINGS`
- `STARTUP_ONLY_SETTINGS`
- `coerce_setting_value(...)`
- `VoiceSTTService.update_settings(...)`
- `VoiceSTTService.persist_settings(...)`
- `RuntimeConfigStore`
- bestehende Admin-Key-Authentifizierung
- Session-Settings-/Public-Settings-Helfer

Keine zweite parallele Persistenzschicht.
Keine zweite lose Liste von Settingkeys in `server.py`.

## 4. Zielarchitektur

Eine zentrale Settings-Registry / Settings-Control-Plane besitzt für jede
serververwaltete Einstellung mindestens:

```text
key
scope
auth
type
constraints
defaultValue
requestedValue
effectiveValue
applyPolicy
```

Scopes:
- `session`
- `server`
- `client_local`

Apply:
- `live`
- `next_activation`
- `next_session`
- `server_restart`

`settingsRevision` ist serverautoritativ und monoton.

Unsichere künftige Keynamen nur in dieser zentralen Registry kapseln.
Keine Stringduplikate quer durch den Server.

## 5. Verbindliche Trigger-Timings JETZT vollständig implementieren

Exakt diese öffentlichen Keys, Defaults, Bereiche und Apply-Policy:

| Key | Default | Bereich | Apply |
|---|---:|---:|---|
| `activation.initialSpeechTimeoutMs` | 15000 | 100–3600000 | `next_activation` |
| `activation.followupTimeoutMs` | 3000 | 100–60000 | `next_activation` |
| `activation.segmentWatchdogInitialMs` | 600000 | 60000–3600000 | `next_activation` |
| `activation.segmentWatchdogRefreshMs` | 180000 | 30000–600000 | `next_activation` |
| `activation.segmentWatchdogWarningMs` | 30000 | 5000 bis kleiner als wirksame Frist | `next_activation` |
| `activation.closingRecoveryTimeoutMs` | 5000 | 1000–30000 | `next_activation` |

Falls die interne Serverkonfiguration Sekunden nutzt:
- öffentliche API bleibt Millisekunden;
- Konversion zentral und exakt;
- keine Float-Drift in Schema/Response.

Watchdog-Warning muss kleiner als die jeweils wirksame Frist validiert werden.
Kein C1-Breitbereich von 0.01–3600 als endgültigen Contract übernehmen.

## 6. Verbindliche Settings-Domänen / Policies

### Activation-/VAD-/Watchdog-Timings
- Scope: Session mit Serverdefault
- Auth: Sessionrecht
- Apply: `next_activation`

### Wake-Word-Auswahl
- Scope: Session
- Apply: `next_session`

### Wake-Word-Sensitivity
- Scope: Session mit Serverdefault
- Range: 0.0–1.0
- Default: 0.5
- Apply: `next_activation`

### Wake-Word-Cooldown / Pre-Roll
- Session mit Serverdefault.
- genaue Apply-Policy `next_activation` bzw. `next_session`, falls Modellneuaufbau nötig.
- noch offene Kalibrierdefaults NICHT erfinden.

### Runtime-Suppression Manual/Wake
- Laufzeit-/Sessionabbild
- `live` für neue Admission.
- diese Policy kann SRV-040 transportieren; hier Metadaten/Policy sauber modellieren.

### globale Wake-Word-Disableliste / Katalogdefaults
- Scope `server`
- Admin-Key
- wirkt auf neue Sessions.

### Servermodelle / Serverdefaults
- Scope `server`
- Admin-Key
- nur soweit bereits vorhandene Servermechanik sauber abbildbar.
- keine fachfremde Vollmigration.

### Client-local
Hotkeys, Gerät, Mute, Feedback, Autostart, Textinjektion sind
`client_local` und werden **nicht** als Serverpersistenz implementiert.
Sie dürfen im Schema nur dann erscheinen, wenn der Contract dies für UI-Metadaten sinnvoll
vorsieht; der Server darf keine Autorität darüber behaupten.

## 7. Requested vs Effective

Die Control Plane muss Requested und Effective sauber unterscheiden.

Beispiele:
- neue `next_activation`-Werte sind bestätigt/requested, ändern aber eine laufende Activation nicht;
- nächste Activation erhält den neuen Effective-Snapshot;
- `next_session` wirkt erst auf neu aufgebaute Sessions;
- `server_restart` darf nicht als live angewendet dargestellt werden.

Eine laufende Activation behält ihren beim Start eingefrorenen
`effectiveSettings`-Snapshot.

## 8. Revision und atomare Patches

Implementiere transaktional:

```text
baseSettingsRevision
changes
```

Regeln:
- `baseSettingsRevision` muss aktuelle Revision treffen;
- sonst `settings_revision_conflict`;
- irgendein ungültiges Feld → kompletter Patch abgelehnt;
- keine Teilanwendung;
- keine teilweise Persistenz;
- feldbezogene maschinenlesbare Fehler;
- erfolgreiche bestätigte Settingsänderung erhöht `settingsRevision` genau einmal
  pro logischer Transaktion.

Concurrent-Patch-Test erzwingen.

Die Validierung muss abgeschlossen sein, bevor Memory/Persistenz verändert wird.

## 9. Session-Patch-Port

Implementiere eine klar testbare service-/domainseitige Operation für:

```text
session_settings.patch
```

Sie erhält mindestens:
- Session-ID/Context,
- baseSettingsRevision,
- changes.

Sie liefert ein strukturiertes Ergebnis, das SRV-040 später direkt in
`command.ack` projizieren kann.

Keinen parallelen WebSocketparser erfinden.

## 10. REST-v2-Zieloberfläche

Soweit unabhängig von SRV-040 real implementieren:

```text
GET /api/v2/settings/schema
GET /api/v2/settings/server
PATCH /api/v2/settings/server
```

`GET /api/v2/settings/schema`
- öffentlich,
- keine Secrets.

`GET /api/v2/settings/server`
- öffentlich,
- nur nicht geheime Requested/Effective Values.

`PATCH /api/v2/settings/server`
- bestehender `X-Admin-Key`,
- atomar,
- Revisionprüfung,
- strukturierte Feldfehler.

Zusätzlich spätere SRV-060-Oberfläche nicht hier implementieren:
`GET /api/v2/wake-words` gehört fachlich zum Wake-Word-Katalog; nur Registry/Provider-Port vorbereiten.

## 11. Secret-Regel

Nie ausgeben:
- Admin-Key
- API-Keys
- Tokens
- Credentials
- secret runtime values.

Nicht in:
- Schema,
- Readresponse,
- Patchresponse,
- Error,
- Event,
- Log,
- Debugdump.

Bestehende Sanitizer/Loggingmechanismen verwenden.

## 12. Persistenz

Vorhandenen `RuntimeConfigStore` / bestehende Persistenz wiederverwenden.

Erfolgreicher Serverpatch:
1. alles validieren,
2. atomare neue Settingsinstanz / Updateplan bilden,
3. persistieren,
4. Effective/Requested sauber aktualisieren,
5. Revision bestätigen.

Fehlschlag:
- Memoryzustand unverändert,
- Datei unverändert oder atomar auf vorherigem Stand,
- Revision unverändert.

Keine zweite JSON-Datei oder Datenbank erfinden.

## 13. Schnittstelle zu SRV-030

Die sechs Activation-Timings werden beim Start einer Activation gelatcht.

C1 wird parallel korrigiert. Deshalb:
- keine direkte Kopplung an fragile interne Close-/Lockmethoden;
- einen kleinen `ActivationSettingsProvider`/äquivalenten Port verwenden;
- finaler SRV-030-Adapter wird später gesetzt.

Markiere solche Bindungen im Bericht:
`REQUIRES_FINAL_SRV_030_BINDING`.

## 14. Schnittstelle zu SRV-040

Dieser Branch startet bewusst nicht auf dem noch unfertigen SRV-040-Prep-Branch.

Darum:
- Domain-Control-Plane und REST dürfen vollständig sein;
- WebSocket-Encoding nicht duplizieren;
- strukturiertes Session-Patch-Ergebnis bereitstellen;
- späterer 040-Port soll dünn sein.

Markiere:
`REQUIRES_FINAL_SRV_040_BINDING`.

## 15. Tests

Mindestens:

### Registry / Schema
- alle sechs Activationkeys exakt;
- Typ, Default, Range, Scope, Auth, Apply.
- Wake sensitivity 0.0–1.0 / Default 0.5.
- keine Secrets.

### Validation
- jeder Timing-Min/Max-Grenzwert;
- eins unter min / über max;
- Watchdog warning >= wirksame Frist abgelehnt;
- falsche Typen;
- unknown keys.

### Revision
- erfolgreicher Patch erhöht Revision genau einmal;
- stale revision;
- zwei konkurrierende Patches → genau einer gewinnt auf gleicher Base;
- Retry auf neuer Revision.

### Atomicity
Multi-Key-Patch mit einem invaliden Feld:
- kein Key angewendet;
- Memory unverändert;
- Persistenz unverändert;
- Revision unverändert.

### Apply
- laufende Activation behält Snapshot;
- nächste Activation erhält neue next_activation-Werte;
- next_session nicht als live darstellen;
- server_restart nicht als live darstellen.

### REST/Auth
- öffentliche GETs ohne Admin-Key;
- PATCH ohne/falscher Key abgelehnt;
- PATCH mit korrektem Key;
- Secret-Redaction.

### Persistenz
- round-trip;
- atomarer Write;
- Restart-Leseweg soweit bestehende Mechanik erlaubt.

## 16. Nicht in diesem Paket

- kompletter v2-WebSocketlayer;
- Wake-Word-Detection-Latch/Audioarbeit;
- Client-UI/Credential Manager;
- vollständige Migration sämtlicher fachfremder Altsettings;
- Legacyabbau.

## 17. Dokumentation

Serverdokumentation:
- Registry/Ownership,
- REST-v2-Zieloberfläche,
- Apply-Policies,
- Revision/Atomicity,
- Trigger-Timingkeys.

Keine Client-Planungsdateien verändern.
Keine `ABNAHME.md`.

## 18. Validierung

- neue Settings-Tests,
- relevante Servertests,
- vollständige Serversuite,
- `git diff --check`.

Ein Prep-Paket darf nicht mit roten Tests abschließen.

## 19. Commit

Ein lokaler Prep-Commit:

```text
prep(settings): implement speculative AP-SRV-050 control plane
```

Kein Push.

## 20. Abschlussbericht

```text
STATUS
Branch
Start-SHA
Prep-SHA
Prep-Tree
Working Tree clean

Settings-Architektur
Registry
Revision/Transaction
Persistenz
REST
Session-Patch-Port

Fertig abgedeckte Keys
Noch kalibrier-/abhängigkeitsgebundene Keys

REQUIRES_FINAL_SRV_030_BINDING
REQUIRES_FINAL_SRV_040_BINDING

Tests / Counts / Commands
Geänderte Dateien
git diff --check
Push: nein
```

Dann stoppen.
