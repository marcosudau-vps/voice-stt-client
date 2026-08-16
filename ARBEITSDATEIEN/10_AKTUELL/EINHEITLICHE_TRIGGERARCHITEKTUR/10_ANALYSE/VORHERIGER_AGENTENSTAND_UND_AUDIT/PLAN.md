# PLAN – Einheitliche serverseitige Triggerarchitektur

Dieser Plan folgt der Arbeitspaketstruktur des normativen Ausführungsauftrags
(AP0–AP11).

**Stand:** abgeschlossen bis auf die manuellen Restabnahmen.
**Gesamtstatus:** `PARTIAL` – GATE 5 und GATE 10 sind
`MANUAL VALIDATION REQUIRED`, alle übrigen Gates sind `PASS`.

Der maßgebliche Gate-Stand steht in `VALIDATION.md`; diese Datei nennt ihn nur
zusammenfassend, damit beide Dokumente nicht auseinanderlaufen können.

| AP | Gate | Status |
| --- | --- | --- |
| AP0 | 0 | **PASS** |
| AP1 | 1 | **PASS** |
| AP2 | 2 | **PASS** |
| AP3 | 3 | **PASS** |
| AP4 | 4 | **PASS** |
| AP5 | 5 | **MANUAL VALIDATION REQUIRED** (Browserlauf) |
| AP6 | 6 | **PASS** |
| AP7 | 7 | **PASS** |
| AP8 | 8 | **PASS** |
| AP9 | 9 | **PASS** |
| AP10 | 10 | **MANUAL VALIDATION REQUIRED** (Audio, Hardware) |
| AP11 | 11 | **PASS** |

Die Abschnitte unten beschreiben, was je Arbeitspaket zu tun war; erledigte
Punkte sind abgehakt.

---

## AP0 – Recovery, Baseline, Ist-Verträge

- [x] Eigener Arbeitsbereich als unabhängige Clones auf identischen HEADs
- [x] Arbeitsstand byteidentisch übertragen und verifiziert
- [x] HEADs, Branches, `git status` dokumentiert
- [x] Fremde vs. eigene Änderungen abgegrenzt (keine fremden vorhanden)
- [x] Vorarbeit klassifiziert (`DECISIONS.md`)
- [x] Produktionsverdrahtung der Vorarbeit geprüft (Hauptbefund: Controlled-Pfad tot)
- [x] Baseline-Testläufe aller drei Suiten protokolliert
- [x] `CONTRACTS.md` mit Iststand gefüllt
- [x] GATE 0 bewertet

---

## AP1 – Recorder Activation Gate

**Vorhanden:** Gate-Modul, Recorder-API, VAD-Startbedingung über Gate.

**Zu tun:**

1. Generationsbindung im Gate (`open`/`close` mit `generation`), damit ein
   spätes `close` einer alten Activation eine neue nicht schließt — auch bei
   `close(None)`.
2. `replace`-Semantik so absichern, dass nur eine neuere Generation eine
   bestehende Activation ersetzen kann.
3. Deterministisches Abort-/Shutdown-Verhalten des Gates.
4. Realitätsnahe Tests gegen eine echte `AudioToTextRecorder`-nahe Instanz
   statt reiner `SimpleNamespace`-Attrappen (§14 verlangt das ausdrücklich).
5. Alle 15 Pflichtfälle aus §14 abdecken, Race-Fälle mehrfach wiederholen.
6. Legacy-Pfad beweisbar unverändert.

**GATE 1:** fokussierte Tests grün, bestehende Recorder-Suite grün, kein
Wakeword-Bypass im Controlled-Modus, Racefälle wiederholt stabil,
`git diff --check` grün.

---

## AP2 – ActivationController

**Vorhanden:** Zustandsmaschine mit monotonen Deadlines, `primarySource`,
`sources`, Versionszähler.

**Zu tun:**

1. `generation` (pro Activation stabil) von `version` (Änderungszähler) trennen.
2. Finalisierungsphase explizit modellieren.
3. Aliasattrappen entfernen bzw. zu echten Properties machen.
4. Fehlende Pflichtfälle aus §15 ergänzen (u. a. ungültige Transitionen,
   Reconnect-/Session-Close-Semantik, Systemzeitsprung).
5. Zustandsdiagramm dokumentieren.

**GATE 2:** alle Transitionen und ungültigen Transitionen getestet, Collisions
getestet, Timer monoton, Generation-Races getestet.

---

## AP3 – WebSocket-Triggervertrag

**Zu tun:**

1. Stream-Lifecycle-Prüfung in `handle_trigger_command` (vor Start, nach Stop,
   nach Close).
2. Korrelierbare Ablehnungen inkl. laufender `activationId`.
3. Vollständige Negativtests aus §16.
4. Legacyclient sendet nie `trigger` und funktioniert unverändert.

**GATE 3:** Trigger und Ack implementiert, Idempotenz bewiesen, Negativfälle
getestet, `hello`/`ready` unverändert, `start`/`stop`-Tests grün.

---

## AP4 – Serverintegration (kritischstes Paket)

**Zu tun:**

1. `parse_session_activation_query` im WebSocket-Einstieg aufrufen.
2. `resolve_session_activation_config` anwenden, `false/false` mit korreliertem
   Fehler und Close ablehnen.
3. `activation_config` über `admit_session` bis in die Session durchreichen.
4. Generationsgebundener Activation-Timer pro Session, der `expire()` aufruft,
   das Gate schließt und `activation.closed` publiziert.
5. Legacy-Wakeword-Follow-up im Controlled-Modus deaktivieren (D-008).
6. Activation-Events (`activation.manual_accepted`, `activation.extended`,
   `activation.closed`) publizieren.
7. `activationId`, `primarySource`, `sources` an Recording-/Transkriptionsevents.
8. Stream-Stop, Session-Close und Reconnect schließen die Activation.
9. Capability `activationTriggers` **erst jetzt** veröffentlichen.
10. Echte E2E-Tests über `TestClient` und `/ws/transcribe`, inklusive der
    Kollisionsmatrix mit den Zählnachweisen
    `Activations = 1 / Segments = 1 / Finals = 1 / Scheduler allocations = 1`.

**GATE 4:** Pflicht-E2E-Tests aus §17 grün, gesamte relevante Serversuite grün.

---

## AP5 – Serverdokumentation und kompatibler Rollout

Dokumentation des Trigger-/Ack-Vertrags, Capabilities, Activationzustände, IDs,
Timer, Kollisionssemantik, Legacyverhalten, Migration, Rollback und der
Privacy-Auswirkung kontinuierlichen Streamings.

**GATE 5:** Legacy-Desktopclient und Browserclient funktionieren gegen den
neuen Server, `start`/`stop` unverändert, Regressionssuite grün.

---

## AP6 – Clientkonfiguration und Migration

1. `manual_trigger_enabled` / `wake_word_trigger_enabled` als führende Felder.
2. Migration exakt nach §11.6: `hotkey → true/false`, `wake_word → false/true`,
   **keine** implizite `true/true`-Migration.
3. `false/false` eindeutig abgelehnt, in UI und Backend mit derselben Regel.
4. Fehlerhafte Migrationstests korrigieren.
5. Persistiertes Userfile, Source-Run und Frozen-Pfadauflösung prüfen.

**GATE 6:** keine alte gültige Config wird unbrauchbar, keine stille
Bedeutungsänderung, beide Trigger separat steuerbar.

---

## AP7 – Client-Lifecycle

1. `send_start`/`send_stop` als Streambefehle wiederherstellen (D-009).
2. Kontinuierlicher Audiostream unabhängig vom Trigger.
3. Pending-Command-Verwaltung mit `commandId` und `trigger_ack`-Auswertung.
4. Kein fachliches Accepted-Feedback vor Ack.
5. Clientseitige Activation-/Follow-up-Autorität abbauen; lokale Timer nur noch
   als Darstellung serverseitiger Autorität.
6. Hotkeyregistrierung nur bei aktivem Manualtrigger; Wakeword-only darf nicht
   an einem Hotkeykonflikt scheitern.
7. Reconnect ausschließlich als Transport-/Streamproblem.

**GATE 7:** Pflichttests aus §20 inkl. doppelter Ack, Ack nach Reconnect, alte
Ack aus alter Generation, Server ohne Triggercapability.

---

## AP8 – Events, Feedback, LEFX

Vollständige Kette Server-Event → Normalizer → Canonical Event → Reducer →
Mapping → Sound/LEFX für alle neuen und geänderten Events. Replay erzeugt
keinen Impuls, Dedupe funktioniert, bestehender Feedback-Fix bleibt erhalten.

**GATE 8:** Manual-Accepted genau einmal, doppeltes Ack ohne Doppelimpuls,
Wakeword während Manualactivation ohne zweite Recordingsequenz.

---

## AP9 – Cross-Repository-Regressionsabnahme

Vollständige Suiten Server, Client, LED. Kritische Race-/Reconnecttests
mehrfach. `CONTRACTS.md` zeilenweise mit PASS/FAIL/N-A-mit-Begründung.

---

## AP10 – Build und reale E2E-Abnahme

Echter Clientbuild und die Pflichtmatrix (`an/aus`, `aus/an`, `an/an`) mit den
25 Pflichtszenarien.

**Vorbehalt:** Szenarien, die echte Audioeingabe, echte ReSpeaker-Hardware oder
manuelle Bedienung erfordern, sind in dieser Umgebung nicht durchführbar. Sie
werden ausdrücklich als `MANUAL VALIDATION REQUIRED` mit konkreter
Testanweisung ausgewiesen und **nicht** als PASS behauptet.

---

## AP11 – Dokumentation und Abschluss

Dokumentation gegen den tatsächlichen Code prüfen, `REPORT.md` mit Iststand,
Git-Nachweis `INITIAL_HEAD == FINAL_HEAD` für alle drei Repositories, Nachweis
dass kein Commit/Push erfolgte und dass der Antigravity-Quellstand unverändert
blieb.

**Abweichung vom Originalauftrag:** GATE 11 des Originalauftrags sieht Push,
Remote-Verifikation und CI-Prüfung vor. Der aktuelle Auftrag verbietet Commit
und Push ausdrücklich. Der Push-Teil von GATE 11 wird daher als bewusst nicht
umgesetzt dokumentiert; die Benutzerentscheidung hat laut §4 des
Originalauftrags Vorrang vor dem Auftragstext selbst.
