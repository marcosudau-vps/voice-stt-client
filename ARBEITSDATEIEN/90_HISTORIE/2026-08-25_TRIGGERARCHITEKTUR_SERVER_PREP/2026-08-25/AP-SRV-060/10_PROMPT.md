# SPEKULATIVE VORIMPLEMENTIERUNG – AP-SRV-060

## 1. Rolle

Du implementierst spekulativ einen möglichst großen Teil von
`AP-SRV-060 – Wake-Word-Katalog, Detection und Audiogrenze`.

Die vorhandene Wake-Word-Pipeline funktioniert bereits grundsätzlich.
Dieses Paket ist **kein Rewrite**.

Ziel:
- vorhandenen Code auf den frozen Wake-Word-Vertrag härten,
- echte Produktänderungen + Tests erzeugen,
- offene Kalibrierwerte bewusst offen lassen.


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
P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\prep-srv-060
```

Branch:
```text
prep/AP-SRV-060/wakeword
```

Start:
```text
db3d2b49539afbf4812d90e13f26f099b9314fe9
```

Preflight exakt prüfen.
Kein Push, Rebase, Merge, neues venv.

## 3. Bestehende Komponenten zuerst lesen und wiederverwenden

Mindestens:

```text
VoiceSTT/core/openwakeword_catalog.py
VoiceSTT/core/wakeword.py
VoiceSTT/core/recording.py
VoiceSTT/core/preroll.py
VoiceSTT/core/activation_control.py
VoiceSTT_server/operations.py
api_fastapi_server/server.py
```

Insbesondere vorhandene:
- OpenWakeWord-Katalog-/Pfadauflösung,
- selected-only Modellpfade,
- Session-Resolver,
- Sensitivity,
- Recorder-Wakeword-Callback,
- Pre-Roll-Selector,
- Controlled Gate.

Keine zweite Wake-Word-Engine bauen.

## 4. Frozen Katalogvertrag

Katalogeintrag mindestens:

```text
id
displayName
aliases
artifactVersion
available
unavailableReason? 
catalogRevision
```

Regeln:
- kanonische stabile ID;
- Unicode trim + case-insensitive Lookup;
- nur explizite Aliase;
- keine Heuristik wie beliebiges Entfernen von "hey";
- Alias-Kollision ist Fehler/ambiguous, keine automatische Auswahl;
- global disabled → nicht available;
- im Build vorhanden aber nicht ladbar → nicht available + maschinenlesbarer Grund.

Katalogrevision steigt bei sichtbarer Katalogänderung.

## 5. Global Disable / Providergrenze

Serverweite Disableliste und Katalogdefaults gehören fachlich SRV-050-Settings.

Da dieser Prep-Branch unabhängig startet:
- kleinen Provider/Port schaffen;
- aktuellen Settingswert oder vorhandene Config lesen;
- keine zweite Settings-Control-Plane implementieren.

Markierung im Bericht:
`REQUIRES_FINAL_SRV_050_BINDING`.

## 6. Atomare Sessionadmission

Session wählt eine oder mehrere Wake-Word-IDs.

Wenn irgendein Eintrag:
- unbekannt,
- globally disabled,
- nicht ladbar,
- Alias mehrdeutig,

dann:
- gesamte Auswahl ablehnen,
- keine Teilinitialisierung,
- kein stiller Fallback,
- alle problematischen IDs maschinenlesbar zurückgeben.

Bei erfolgreicher Admission:
- ausschließlich kanonische IDs intern weiterreichen.

## 7. Selected-only Modellinitialisierung

Nur die angenommene Auswahl für diese Session initialisieren.

Regressionen mit Fake Model:
- 1 Modell,
- 3 Modelle,
- erwartete Maximalmenge,
- Auswahl [A,C] lädt niemals B.

Kein Fallback auf alle Buildmodelle, wenn Sessionauswahl existiert.

## 8. Sensitivity

Gemeinsame Sensitivity für alle aktiven Wake Words einer Session.

Frozen:
- Range 0.0–1.0
- Default 0.5
- serverseitig Effective Value veröffentlichbar.

Da finaler Settingsprovider aus SRV-050 später kommt:
- intern sauber konfigurierbar machen,
- keine parallele Registry.

## 9. Detection-Domainmodell

Der heutige Pfad darf nicht bei anonymem Index/Boolean stehenbleiben.

Führe eine kleine immutable interne Detection-Repräsentation ein,
mindestens:

```text
wakeWordId
score
detectedAt / monotone identity soweit sinnvoll
```

Trenne:
- Raw Detection / Scorediagnose
- akzeptierte fachliche Detection.

Nur akzeptierte Detection kann:
- Activation-Admission versuchen,
- `wakeword.detected` vorbereiten.

## 10. Fachlicher Latch

Verbindlich:

Erster **akzeptierter** Wake-Word-Treffer setzt einen fachlichen Latch bis zum
sicheren Eingabeschluss/Unlock der dadurch erzeugten Activation.

Während Latch:
- kein zweites fachliches `wakeword.detected`,
- kein zweiter Activationversuch,
- keine Source-Merge,
- kein Finish/Cancel/Refresh durch gesprochenes Wake Word.

Rohscores dürfen Diagnose bleiben.

Der bestehende `recorder.wakeword_detected`-Boolean ist nicht automatisch der
fachliche Latch, wenn er durch Recorderzustände zurückgesetzt/reused wird.

Latch-Ownership klar im serverautoritativen Lifecycle verankern.

Da finaler SRV-030-Close gerade korrigiert wird:
- Unlock/Close-Bindung hinter kleinen Adapter legen,
- keine C1-Quickfix-Logik kopieren.

`REQUIRES_FINAL_SRV_030_BINDING`.

## 11. Wake Word während laufender Activation

Semantische Wake-Word-Auswertung als Trigger ist nicht nötig.

Wenn Wake Word gesprochen wird:
- Audio bleibt normales Activation-Audio,
- VAD darf es wie Sprache behandeln,
- keine zweite Activation,
- kein Sourcewechsel,
- kein zweites Domain-Wakeevent.

## 12. Cooldown / Rearm

Cooldown ist konfigurierbarer Zusatzschutz, nicht Ersatz für Latch.

Architektur und Setting-Hook vorbereiten.

Keine willkürlichen Werte erfinden, wenn Plan/Contract sie als kalibrierabhängig lässt.

Keine pauschale Mehrfachchunk-Regel wie 2/3, 5 Treffer etc. einführen,
solange Score-/Audio-Evidence sie nicht belegt.

## 13. Detection-Auswahl bei mehreren Kandidaten

Falls mehrere gültige Kandidaten im selben Auswertungsschritt über Schwelle liegen:
- bestehende höchste-Score-Regel kann erhalten werden, sofern Contract nicht widerspricht;
- Ergebnis muss kanonische ID + Score behalten;
- deterministischer Tie-Break dokumentieren, falls erforderlich.

Keine zufällige Dict-/Filesystemreihenfolge als Semantik.

## 14. Audiogrenze / Pre-Roll

Vorhandenen `preroll.py`-Selector und vorhandene Frame-Metadaten wiederverwenden.

Trenne logisch:

```text
Detector-History
vs.
Nutztranskript-Audioanfang
```

Ziele:
- Wake Word selbst nicht im Nutztranskript,
- direkt anschließende Sprache vollständig erhalten,
- `0 ms` Pre-Roll weiterhin zulässig.

Keine zweite VAD-Pipeline / zweiten VAD-Pass einführen.

Kalibrierwerte parametrierbar lassen.

## 15. Accepted Detection → Eventport

Bereite serverintern eine akzeptierte Detection so vor, dass SRV-040 daraus exakt
`wakeword.detected` mit mindestens:

```text
activationId
wakeWordId
score
primarySource = wake_word
```

projizieren kann.

Keinen zweiten v2-Wireencoder in diesem Branch bauen.

`REQUIRES_FINAL_SRV_040_BINDING`.

## 16. Katalog-REST-Port

Bereite Domain-/Servicefunktion für:

```text
GET /api/v2/wake-words
```

vor bzw. implementiere den REST-Read, soweit unabhängig sauber möglich.

Antwort versioniert und nur nicht geheime Build-/Availabilitydaten.

Falls SRV-050-Disableprovider noch fehlt:
- Adapter,
- kein hardcodierter zweiter Configstore.

## 17. Ressourcen-/Startzeitmessung

Der AP verlangt Messung mit:
- 1 Modell,
- 3 Modellen,
- erwarteter Maximalzahl.

Baue ein reproduzierbares Test-/Evidence-Harness, das:
- Initialisierungszeit misst,
- soweit im Projekt üblich RSS/Memory misst,
- geladene Modell-IDs protokolliert.

Wenn reale Modelle/Artefakte im lokalen Environment verfügbar sind:
Messung durchführen.

Wenn nicht:
- Harness trotzdem fertigstellen,
- sauber `ENVIRONMENT_EVIDENCE_PENDING` dokumentieren,
- keine Werte erfinden.

## 18. Pflicht-Tests

### Catalog
- canonical lookup case-insensitive,
- Unicode trim,
- expliziter Alias,
- Alias-Kollision,
- disabled,
- unloadable,
- catalogRevision.

### Admission
- eine ungültige ID lehnt gesamte Auswahl ab,
- mehrere problematische IDs vollständig melden,
- kein Partial Load,
- kein Fallback.

### Selected-only
- 1,
- 3,
- Maximalmenge,
- exakt ausgewählte Modelle.

### Sensitivity
- 0.0,
- 1.0,
- unter/über Range,
- ein gemeinsamer Effective Value.

### Detection/Latch
- ein hoher Treffer → genau eine akzeptierte Detection,
- mehrere Folgechunks mit hohem Score → genau eine,
- Rohdiagnose darf mehrfach sein, Domainwirkung nicht,
- während Activation kein zweiter Trigger,
- nach sicherem Unlock wieder neue Detection möglich,
- ID und Score bleiben erhalten.

### Multi-candidate
- höchster gültiger Score deterministisch,
- Tie-Break explizit getestet, falls nötig.

### Pre-Roll
- Wakeword aus Nutzgrenze,
- direkte Folgesprache erhalten,
- 0ms,
- unsicherer Selector fällt konservativ zurück.

### Integration
- Wake Admission öffnet denselben ActivationController-Pfad wie Manual,
  mit `primarySource=wake_word`,
- kein separater Wake-Lifecycle.

## 19. Nicht in diesem Paket

- allgemeine v2-Protokollimplementierung,
- vollständige Settings-Control-Plane,
- Client-Hotkeys/Wake-Pause,
- ReSpeaker/Mute,
- Legacyabbau,
- neue Wakeword-ML-Modelle trainieren.

## 20. Dokumentation

Serverdokumentation:
- Katalog,
- selected-only,
- Admission,
- Latch,
- Sensitivity,
- Cooldown/Pre-Roll,
- Evidence-Harness.

Keine Client-Planungsdateien ändern.
Keine `ABNAHME.md`.

## 21. Validierung

- fokussierte Wake-/Catalog-/Prerolltests,
- Integrationstests,
- Vollsuite,
- `git diff --check`.

Keine roten Tests.

## 22. Commit

Ein lokaler Prep-Commit:

```text
prep(wakeword): implement speculative AP-SRV-060 contract
```

Kein Push.

## 23. Abschlussbericht

```text
STATUS
Branch
Start-SHA
Prep-SHA
Prep-Tree
Working Tree clean

Catalog
Admission
Selected-only
Sensitivity
Detection/Latch
Audio boundary
Resource harness

REQUIRES_FINAL_SRV_030_BINDING
REQUIRES_FINAL_SRV_040_BINDING
REQUIRES_FINAL_SRV_050_BINDING
ENVIRONMENT_EVIDENCE_PENDING

Tests / counts
Geänderte Dateien
git diff --check
Push: nein
```

Dann stoppen.
