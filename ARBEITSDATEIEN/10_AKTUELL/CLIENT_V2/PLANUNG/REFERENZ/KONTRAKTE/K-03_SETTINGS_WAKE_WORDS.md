# K-03 – Settings-Control-Plane und Wake-Word-Katalog

Geltung: exakte Serverfelder und Serverlimits sind verbindlich; interne Clientrepräsentationen sind Vorschläge, lokale technische Werte begründbar anpassbare Startwerte gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Produktverhalten und Schutzwirkungen bleiben Pflicht.

## 1. Oberflächen und Antwortformen

| API | Auth | Antwort / Verwendung |
| --- | --- | --- |
| `GET /api/v2/settings/schema` | öffentlich | `protocolVersion`, `serverVersion`, `serverCommit`, `secretsExposed=false`, `settings[]` |
| `GET /api/v2/settings/server` | öffentlich | Identitätsfelder, **Server-**`settingsRevision`, `settings[]` mit requested/effective Defaults |
| `PATCH /api/v2/settings/server` | Admin-Guard | JSON `{baseSettingsRevision, changes}`; vollständige atomare Antwort |
| `GET /api/v2/wake-words` | öffentlich | `protocolVersion`, `catalogRevision`, `wakeWords[]`; keine Serverversion/Commitfelder |
| `POST /api/v2/wake-words/refresh` | Admin-Guard | Katalogrefresh; vollständiger Erfolg oder HTTP 422 bei unverändertem vorherigem Katalog |
| `session_settings.patch` | eigene Session | Command auf `/ws/v2`, Ack und ggf. Policyevents |

Schemaeintrag: `key`, `scope`, `auth`, `type`, `constraints`, `defaultValue`, `applyPolicy`, optional `description`. Es gibt **keine** per-Entry-`settingsRevision` und keine requested/effective Werte im Schemasnapshot. Serverwerte liefern `requestedValue`/`effectiveValue`; Sessionwerte stehen in den Snapshotmaps. Der veröffentlichte Schemaeintrag enthält nicht die internen Flags `writable` und `has_server_default`; die Clientzuordnung dieser Baseline ist unten vollständig festgelegt.

Scopes: `session`, `server`; `client_local` ist im allgemeinen Vokabular vorhanden, aber unter den 18 eingebauten Registryfeldern nicht belegt. Authwerte: `session`, `admin`. Typen: `int`, `float`, `bool`, `string`, `string_list`. Constraints: inklusive `min`/`max`, `allowed`/`allowedValues`, `minItems`, `lessThanKeys`, `unit`, `calibration`, `calibrationTraceabilityIds`.

Das [direkt exportierte Schema](VEKTOREN/settings-schema.json) und [die Baseline-Serverwerte](VEKTOREN/settings-server-defaults.json) liefern konkrete maschinenlesbare Beispiele. Diese Defaults sind Code-Defaults; ein betriebenes System kann abweichende persistierte Serverdefaults liefern.

## 2. Alle Schlüssel dieser Baseline

`NA` = next_activation, `NS` = next_session, `L` = live. `Serverdefault ja` heißt zusätzlich adminverwalteter Default auf der Serveroberfläche; es macht den Sessionkey nicht zu einem beliebigen Admincommand im WebSocket.

| Schlüssel | Typ / Constraint | Code-Default | Scope / Policy | Sessionpatch / Serverdefault |
| --- | --- | --- | --- | --- |
| `activation.initialSpeechTimeoutMs` | int 100–3 600 000 ms | 15 000 | session / NA | ja / ja |
| `activation.followupTimeoutMs` | int 100–60 000 ms | 3 000 | session / NA | ja / ja |
| `activation.segmentWatchdogInitialMs` | int 60 000–3 600 000 ms | 600 000 | session / NA | ja / ja |
| `activation.segmentWatchdogRefreshMs` | int 30 000–600 000 ms | 180 000 | session / NA | ja / ja |
| `activation.segmentWatchdogWarningMs` | int ≥ 5 000 ms, strikt < Initial und Refresh | 30 000 | session / NA | ja / ja |
| `activation.closingRecoveryTimeoutMs` | int 1 000–30 000 ms | 5 000 | session / NA | ja / ja |
| `wakeWord.sensitivity` | float 0–1 | 0.5 | session / NA | ja / ja |
| `wakeWord.minConsecutivePredictionFrames` | int ≥ 1, calibration pending | 1 | session / NA | ja / ja |
| `wakeWord.cooldownMs` | int ≥ 0 ms, calibration pending | 0 | session / NA | ja / ja |
| `wakeWord.preRollMs` | int ≥ 0 ms, calibration pending | 0 | session / NA | ja / ja |
| `wakeWord.detectorGain` | float 0–3, calibration pending | 1.0 | session / NA | ja / ja |
| `wakeWord.noiseSuppressionEnabled` | bool | false | session / NS | akzeptiert, aber in Session nie wirksam / ja |
| `wakeWord.vadThreshold` | float 0–1, calibration pending | 0.0 | session / NS | akzeptiert, aber in Session nie wirksam / ja |
| `wakeWord.selection` | string_list, minItems 0; zusätzliche Admissionprüfung | aus Hello (Registrydefault `[]`) | session / NS | nur requested / kein Serverdefaultfacet |
| `runtimeSuppression.manual` | bool | aus Hello | session / L | read-only im Patch / kein Serverdefaultfacet |
| `runtimeSuppression.wakeWord` | bool | aus Hello | session / L | read-only im Patch / kein Serverdefaultfacet |
| `wakeWord.inferenceBackend` | string: auto, onnx, tflite | auto | server / NS | wrong_scope / ja |
| `wakeWord.globalDisabledIds` | string_list, minItems 0 | [] | server / NS | wrong_scope / ja |

Damit: **18** Registryfelder, **16** Sessionkeys, **15** Serverdefaultfelder (13 Sessiondefaults plus 2 Serverkeys). Keine dieser eingebauten Definitionen nutzt `server_restart`; die Clientarchitektur muss diese publizierte Policy für Erweiterungen darstellen können.

Bool ist keine Zahl, NaN/Infinity sind unzulässig. Zahlen nicht als Strings senden. Der Validator prüft das vollständig zusammengeführte Kandidatenbundle einschließlich Watchdog-Warnung gegen beide Fristen. Insbesondere ist Refresh=30 000 bei Warning=30 000 ungültig, obwohl beide isolierten Mindestwerte eingehalten wären.

## 3. Sessionpatch und Apply

Patch nur nicht leere Änderungen; `baseSettingsRevision` = bestätigte Sessionrevision. Neue Session beginnt bei Revision 0. Atomar: ein Feldfehler verwirft alles. Fehler sortiert nach Feld; Details `field`, `code`, `message`.

- Unveränderte Werte: `no_change`, keine neue Revision/Eventwirkung.
- Änderungen: `applied`, Revision +1; je betroffener Policy ein `settings.changed` in Ordnung `live`, `next_activation`, `next_session`, `server_restart`; nur erstes Event erhöht stateVersion. Alle Events vor Ack.
- Konflikt: `settings_revision_conflict`, `errors[].code=stale_settings_revision`; Snapshot lesen, neuen Patch berechnen, neue commandId.
- Validierungsfehler: `unknown_key`, `invalid_type`, `out_of_range`, `too_few_items`, `value_not_allowed`, `cross_field_conflict`, `wrong_scope`, `read_only_runtime_authority`, `wake_word_selection_required`, `wake_word_unavailable`.

`next_activation`: Die nächste Activation verwendet neue wirksame Defaults; eine bereits gestartete Activation behält genau ihren `activation.started.effectiveSettings`-Snapshot. `requestedSettings` zeigt den neuen Wunsch sofort; der während offener Activation gelieferte Effective-Snapshot zeigt gelatchte Startwerte. Nach Ende Snapshot neu lesen, um noch anstehende Wünsche nicht als bereits aktiv zu zeigen.

`next_session`: Sessionpatch ändert requested, baut aber die Wake-Engine nicht neu auf. Die nächste Session übernimmt **keine** previous-session Settings. Sie startet aus Serverdefaults und Helloauswahl. Daher:

1. Auswahl ändern: lokal kanonische IDs speichern; neue Verbindung mit geändertem `hello.requestedSession.wakeWordIds`.
2. `noiseSuppressionEnabled` und `vadThreshold`: kein individueller Startparameter im Hello. Als Sessionpräferenz nicht verfügbar; UI read-only mit Erklärung oder Adminserverdefaultpfad. Ein Reconnect plus erneuter Sessionpatch aktiviert diese Werte nicht.
3. Andere gewünschte `next_activation`-Werte nach jedem Hello erneut patchen, bevor Audio/Manualfreigabe erfolgt.
4. Suppression über `trigger_suppression.set`, niemals als Sessionpatch; Basismaske bereits in Hello.

Bekannte Servereigenschaft: Patch von `wakeWord.selection` akzeptiert teilweise Aliase und speichert den Rohwert. Client sendet dort und im Hello ausschließlich kanonische IDs; er benutzt den Patch nicht als Ersatz für eine tatsächliche neue Sessionauswahl.

## 4. Serverpatch

Separate Revision aus `GET /api/v2/settings/server`; nicht die Sessionrevision verwenden. JSON:

```json
{"baseSettingsRevision": 0,
 "changes": {"activation.followupTimeoutMs": 4000}}
```

Antwortfelder: `accepted`, `result`, `settingsRevision`, `changedKeys`, `values`, `effectiveValues`, `applyPolicies`; optional `errors`, `requiresRestart`. `values` und `effectiveValues` sind Maps, nicht identisch mit den `settings[]`-Einträgen der Readantwort. Schema und Readantwort einmalig zusammenführen, keine fiktiven Felder verlangen.

| HTTP | Ergebnis |
| ---: | --- |
| 200 | applied / no_change |
| 409 | settings_revision_conflict |
| 422 | settings_rejected |
| 500 | internal_error, ggf. persistence_failed |
| 401 | Admin-Key fehlt/falsch bei konfiguriertem Key |
| 403 | Remoteverwaltung ohne eingerichteten Serverkey deaktiviert |
| 400 / Frameworkvalidierung | ungültiger Requestbody / Envelope |

Vor Persistenzfehler oder Validierungsfehler erfolgt kein Teilcommit. Katalog-Disableliste beeinflusst Admission neuer Sessions und Capabilities; vorhandene Wake-Engines werden nicht als Hot-Reload behandelt. Keine automatische HTTP-Patchwiederholung nach unklarer Antwort: zuerst Serverread, neuen Stand mit Änderung vergleichen und bewusste erneute Transaktion.

Die V2-Serverseite bildet die 15 Defaultfelder ab. STT-Modellverwaltung, Loggingkonfiguration und andere vorhandene Adminrouten besitzen eigene Verträge und werden nicht als vermeintliche V2-Schemafelder angeboten.

## 5. Katalog und Admission

Katalogeintrag: `id`, `displayName`, `aliases`, `artifactVersion`, `available`, `catalogRevision`; bei nicht verfügbar `unavailableReason`; zusätzlich `backends` mit `onnx`/`tflite` und deren `available`/`unavailableReason`. Kein lokaler Dateipfad. Top-Level- und Eintragsrevision beziehen sich auf denselben Katalogsnapshot.

Der ausgelieferte Katalog hat 25 IDs; UI verwendet die aktuelle Antwort und niemals eine hardcodierte vollständige Liste. Anzeigenamen/Aliase dienen Suche und Anzeige; persistierte Auswahl und Wire ausschließlich `id`. Eingabeauflösung Unicode-trim/case-insensitive gegen explizite Alias-/Displaytabellen, eindeutiger Treffer erforderlich, keine erfundene „Hey“-Entfernung. Unverfügbare zuvor gewählte IDs sichtbar erhalten und Benutzerkorrektur verlangen; kein stilles Downgrade der gespeicherten Auswahl.

Ein Backend für die ganze Auswahl. `auto` wählt plattformgerecht und kann für die gesamte Auswahl ausweichen; explizit onnx/tflite wechselt nicht still. Fehlercode `wake_word_unavailable` mit `reason`: `not_canonical`, `unknown`, `globally_disabled`, `artifact_missing`, `artifact_integrity_mismatch`, `artifact_unloadable`, `pipeline_unavailable`, `runtime_unavailable`, `no_common_backend`, `backend_unavailable`, `catalog_unavailable`. Fehler einer ID lehnt die gesamte Session ab; doppelte IDs werden dedupliziert.

Nur ausgewählte Modelle werden initialisiert. Im offenen Lifecycle keine zweite Wakeactivation. Accepted Hit erzeugt nach `activation.started` genau ein `wakeword.detected` mit kanonischer Gewinner-ID. Rohscores sind Diagnose.

## 6. Kalibrierung und Audioübergang

Die tatsächliche Wakequalifizierung zählt echte neue Predictionframes, gruppiert den Trefferbereich und verwendet die trailing edge des qualifizierten Hits als operationalen Nullpunkt. Detectorgain verändert nur eine Wake-Inferenzkopie. `preRollMs` wird gegen tatsächlich vorhandene Audiohistorie geklemmt; aus der Classifier-Receptive-Field-Größe folgt keine künstliche UI-Obergrenze. Expliziter Cooldown wirkt auch nach sicherem Eingabeschluss.

Für Predictionframes, Cooldown, Pre-Roll, Gain und Wake-VAD fehlen vollständig qualifizierte reale positive Kalibrierungsbelege (Serverkennzeichnung `calibration=pending`, WW-18/WW-19). Defaults sind Startwerte. Die Clientplanung garantiert damit nicht pauschal eine perfekte Entfernung der Wakephrase bei gleichzeitig verlustfreiem Nutzsprachbeginn. AP-IV2-020 misst dies an realen Aufnahmen; Abweichungen werden als Audio-/Serverkalibrierungsbefund klassifiziert.

## 7. Quellen

`api_fastapi_server/settings_control.py` (`builtin_definitions`, `SessionSettingsState`, `ServerSettingsState`), V2-Routen und Admission in `server.py`, `protocol_v2/{handshake,connection,ports}.py`, `VoiceSTT/core/{wakeword_catalog,wake_detection,wake_audio_boundary}.py`; Tests Settings-Control-Plane, Runtimepersistenz, V2settings, Katalog, Selected-only und Wake-E2E. [Manifest](../../EVIDENCE/source-manifest.json).
