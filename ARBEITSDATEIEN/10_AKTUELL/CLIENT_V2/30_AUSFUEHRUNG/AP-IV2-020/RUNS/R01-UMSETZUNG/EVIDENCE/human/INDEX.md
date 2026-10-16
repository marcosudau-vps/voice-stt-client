## Aktueller Manual-Sprachpfad bestanden

[Neuer Liveversuch am Produkt d95043e](../ux02/manual-voice-20261016-01/assessment.json), [Auswerter](evaluate_manual_trial.py). Tatsächliche F8/F9-Callbacks und Acks, gleiches Segment/Final, eine native Ausgabe ohne Shift. Mensch bestätigt vollständigen Satz und hat GUI-Übernahme betätigt. Erkannter Bindestrich in „Hotkey-Probe“ bleibt explizite orthografische ASR-Abweichung. Quelle enthält keine neue Produktänderung; vollständige M-Gates weiter offen.

### Vorheriger Zwischenstand

## Aktuell: UX02 real bestanden und geschlossen

[Physische Tastenprobe](../ux02/native-physical-20261016-01/assessment.json) und [menschliche Chatbestätigung](../../ZUSATZPROMPTS/013_UX02_NATIVE_BESTAETIGUNG.md) PASS. Produktworker sah tatsächlich Shift/Ctrl und deren Freigabe nach250ms; exakte native Ausgabe. Aktueller d950-Quellstand vollständig identisch mit1390er Qualifikation. Nächster Einzeltest: bestehender wiederholbarer Manual-Sprachpfad mit eigenem Start,8s Vorbereitung und sichtbaren Schritten. Keine allgemeine Fortsetzungsfreigabe nötig.

### Vorheriger Zwischenstand

## Aktuell: UX02 technisch requalifiziert, physischer Nachweis offen

[Produkt d95043e und Gesamtbelege](../ux02/qualification-summary.json), [Freigabe012](../../ZUSATZPROMPTS/012_UX02_FREIGABE.md). [Native Tastenprobe](native_modifier_trial.py), [passender GUIadapter](native_modifier_editor.py), tatsächliche Qt-/Veredicttests/Compile in [UX02-Index](../ux02/INDEX.md). Nur eigenes Testziel/echte physische Modifier/native Produktqueue; kein Mikrofon/Modell nötig. Neuer eigener Start nach jeder Wiederholung,8s ruhige Vorbereitung, anschließend eigenes Übernehmen. START erst nach laufendem Controller; GUI allein startet keine Testqueue.

Aufruf aus dem Repository mit Projektvenv: zuerst native_modifier_editor.py; dessen ausgegebene eigene state.json an native_modifier_trial.py --state <state.json> --evidence <neues-Verzeichnis> --prepare-seconds 8 übergeben. Bestehende Belege werden nicht überschrieben. --self-check prüft Helfer ohne Eingaben; GUIadapter unterstützt --self-check. Die permanente allgemeine Oberfläche bleibt unter tests/manual/v2.

### Frühere chronologische Zwischenstände

## Aktuell: dauerhafter Testclient fertig, UX02 offen

[Testclient](../../../../../../../../../tests/manual/v2/README.md), [zehn Helferprüfungen/Qt/Windows1378 PASS](../ux01/manual-tool-permanent/summary.json). Feste Schritte, wandernder Fokus, Vorbereitung8s und Timer rechts. [Manualprobe](../ux01/repeatable-manual-20261016-01/assessment.json): F8/F9 PASS, Zieleinfügung FAIL durch gehaltenes Shift. [Nicht angewandter Scopevorschlag](../../08_SCOPE_VORSCHLAG_UX02_MODIFIERTASTEN.md). BLOCKED bezüglich vollständiger Qualifikation; kein geänderter Produktcode.

## Wiederholbare Einzelaufgaben

[Controller](stepped_wake_trial.py) wartet ohne Vorlesetimer auf jeden eigenen Start. [Dauerhafte Controllerregressionen](test_stepped_controls.py), [acht Helfertests und Qt-Selbstprüfung](../ux01/repeat-controls/summary.json). Separates großes grünes Satzfeld; Wiederholen, Abbrechen und explizite Übernahme. Attempt-IDs verhindern alte Requests/Statusmeldungen; keine automatische funktionale Erfolgswertung aus Übernehmen oder Exit0. Produkt unverändert.

## Aktueller bestätigter Liveversuch

[Zwei getrennt gestartete Wake-Aufgaben](../ux01/stepped-20261016-01/assessment.json) PASS für unmittelbare vollständige Nutzsätze, tatsächliche native Ausgabe und Leerzeichentrennung. User: „Beide vollständig, mit Leerzeichen“. F9/kompletter M02 weiter offen. [Wiederverwendbare Auswertung](evaluate_stepped_trial.py) exportiert nur vereinbarte Fälle/Hashes und minimierte Diagnosen, keine vollständige History. [Konkreter nativer Binding-Vorcheck](probe_test_bindings.py), [Ergebnisse](../ux01/hotkey-task-precheck/summary.json). UX01 ist ausdrücklich freigegeben und nach technischer Requalifikation/nativer Ausgabe geschlossen; frühere Vorschlagsstände unten historisch.

# Gemeinsame Realtests und wiederverwendbare Werkzeuge

[Manual3000](manual-followup-3000.json), [menschlich gewählte5000ms](manual-followup-5000.json),
[erster Live-Wakeversuch](wake-first-live.json), [behebbarer Hostspeichermangel](host-memory-constraint.json).

[Sechs ausdrücklich freigegebene Original-WAVs und Reproduktion](samples/README.md),
[Fixturemanifest](samples/manifest.json), [Sampleherkunft](sample-index.json).
[Testhilfenprüfung](tool-validation.md), [reale Scores](wake-scores-summary.json),
[vollständige echte Predictionframes](wake-scores-full.json.gz),
[0/160/320/480ms im echten V2-/ASR-Replay](wake-replay-calibration.json).

320ms ist vorbereiteter Livekandidat, noch keine menschliche Endwahl.
Die fehlende Wakephrase der ersten Aufnahme wurde vom Menschen erklärt; drei
positive/drei negative Samples, kein behauptetes Detector-FAIL für diese Datei.

[UX01](ux-findings.json): wirkungsloses append_space, Produktkorrektur noch
außerhalb der Recoveryfreigabe. Keine komplette M-Abnahme aus diesen Teilbelegen.

[Zweite Live320probe](live-wake-320.json), [echter nativer Einfügeprobe-PASS](native-editor-probe.json),
[geführter Lauf mit tatsächlicher erster Einfügung und späterem Fokusverlust](guided-wake-320.json).
Keine pauschale native Einfügestörung behauptet. [Roter UX01-Beleg](append-space-red.json),
[isolierte unapplizierte Vorschau](append-space-preview.json),
[konkreter noch nicht angewandter Scopevorschlag](../../06_SCOPE_VORSCHLAG_UX01.md).

## Ergänzung: UX01-Freigabe und letzte menschliche Rückmeldung

- [Ausdrückliche Freigabe](../../ZUSATZPROMPTS/006_UX01_FREIGABE.md): gleiche R01, Produktkorrektur und Tests/Requalifikation autorisiert.
- [Menschliche Rückmeldung](guided-wake-320-human-feedback.json): beide Sätze vollständig; technische Fokus-/Zielevidenz im [geführten Lauf](guided-wake-320.json) bleibt abweichend nur partiell. Keine nachträgliche Umwertung zu vollständigem PASS.
- [Dauerhafte rote Regression, korrigierte Fixtureannahme](ux01-permanent-red-corrected.json), [gezielte 100 Tests grün](ux01-targeted-green-final.json). Erster roter Testlauf enthielt zusätzlich eine falsche Erwartung an den Rückgabewert für Deduplizierung; erster Greenversuch zusätzlich eine falsche Erwartung an die rohe Queue-API. Die tatsächliche Deduplizierungsautorität liegt im Finalconsumer und bleibt vollständig geprüft.
- Neuer Produkt-/Buildstand und volle Qualifikation folgen unter [UX01-Evidenz](../ux01/). Vorherige Produkt41-Belege werden nicht als Beleg des neuen Produkts ausgegeben.
