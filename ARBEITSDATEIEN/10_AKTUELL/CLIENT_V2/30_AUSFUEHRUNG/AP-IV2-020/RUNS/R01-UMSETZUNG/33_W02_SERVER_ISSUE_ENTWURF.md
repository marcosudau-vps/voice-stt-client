> Fortschreibung21.10.2026: W02 wurde anschließend auf menschliche Entscheidung als aktuell nicht mehr reproduzierbar geschlossen. Kein eigener Freigabeblocker; historische Befunde und Testurteile bleiben erhalten. [Aktueller Stand](36_W02_ABSCHLUSS_UND_FREIGABERESTE.md). Die nachfolgenden Aussagen zum damaligen offenen Status sind historisch.

# IV2-020-W02 – lokaler Server-Issueentwurf, noch nicht veröffentlicht

20.10.2026, AP-IV2-020/R01. **CONFIRMED_BEHAVIOR_ROOT_CAUSE_PENDING**.
Keine Servercodeänderung, kein Deployment/Neustart oder externe Issuenachricht.
Clientprodukt `0f6c85e0ecf971e596aae1b7d265dad7132754e2` unverändert.

## Titelvorschlag

Zusätzliche Alexa-Admission nach Cancel einer manuellen Aufnahme in überlagerter Wakepause-/Reconnectfolge

## Exakter vorhandener Server

`wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`, Info unter
`https://pro.v2.voice-stt-server.marcosudau.com/api/v2/info`.
Commit `67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, Tree
`74f37cad84c5be9e74d880a4b10c3d9623de7da3`,2.0.0, clean/pro,
Instance `793c2cf377d2439d98a7aac719cc1d3f`. Vollständige Info vor/nach stabil,
jeder reale Hello passend. Bereits vorhandener Wakefix aus PR8/Issue7 ist enthalten.

## Reproduktion ohne neue menschliche Aufnahme

Vorhandene freigegebene echte PCMfixture `alexa_pause.wav` aus der Paketakte,
16000Hz/mono/16bit; Dateihash wird gegen das versionierte Manifest geprüft.
Keine generierte Sprache als angeblicher realer Modelltest. Produktions-
Controls/Settings/Mirror/Transport, reale Modelle/ASR, Echtzeit-Pacing.

1. BOTH mit Manual und ausgewählten Alexa/Hey-Jarvis-Modellen öffnen;
   Sessionparameter Follow-up5000ms, Pre-Roll320ms.
2. Echte Alexa per Fixture auslösen, Cancel;5s digitale Stille ohne Zusatzwake.
3. Wake pausieren, positives Fixture erneut übertragen: keine Activation.
4. Auch Manual pausieren. Manueller Reconnect, neue Session/Generation;
   bestätigte Pausen bleiben, positives Fixture ohne Activation/Primarywirkung.
5. Nur eigenen TCP-Socket abbrechen; automatische Recovery in dritte Session,
   beide Pausen weiter bestätigt, positives Fixture ohne Activation.
6. Wake unabhängig freigeben, Manual bleibt pausiert. Positive Alexa funktioniert;
   Cancel und5s digitale Stille ohne Zusatzwake.
7. Manual freigeben, bewusst einmal per Produktions-Primary manuell aktivieren.
   Positives9sFixture vollständig innerhalb dieser manuellen Aufnahme übertragen.
8. Unmittelbar nach Fixtureende Cancel dieser Activation senden. Nach bestätigtem
   Eingabeschluss ausschließlich digitale Nullen übertragen; kein weiteres Activate.

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.verify_server_fix --expected-server-commit 67f3ce45f6ea1ff659382e40c194c70bd33d58ff --pause-manual-boundary-only --first-only --output build/w02-own-diagnostic
```

Diagnostischer HTTP-/Connect-/Bootstraptimeout180s; Ack-/Sicherheitsgrenzen
unverändert. Der Lauf beendet nur seine eigene Verbindung.

## Erwartung und zwei tatsächliche Fehlernachweise

Erwartet: genau drei Activations, Quellen Wake/Wake/Manual, drei Cancelabschlüsse,
kein weiterer Wake oder Start aus Audio der abgeschlossenen manuellen Aufnahme.

Erster Lauf: manuelle Activation `ef855ca1-b8b1-49ef-9faf-1ffba8faf9c7`,
Cancel/input_closed62,156s. Zusätzlicher Start
`e8974269-d876-4c62-9d7b-6c4dfa4061a0`62,594s: **438ms danach**,
Alexa-Score **0,8739580512046814**. Vier statt drei Activations.
[Vollständige bereinigte Ereignisse](EVIDENCE/mute-reinsert-20261020/overlap-failed.json).

Eigenständige Wiederholung: manuelle Activation
`8cfa42ba-46a4-411d-bc9b-dcd252e36b86`, Cancel/input_closed61,860s.
Zusätzlicher Start `40baf062-2595-4b38-a835-ab73a73f3ea4`62,250s,
wakeword.detected62,266s: **390ms/406ms danach**, identischer Alexa-Score.
[Wiederholung](EVIDENCE/mute-reinsert-20261020/overlap-repeat.json).

Beide **FAIL**, keine Umdeutung durch einfachere erfolgreiche Kontrollen.
Der Server liefert neue, eigene Activation-IDs und Wakeevents; dies ist kein
doppelt dargestelltes Clientevent oder erneutes clientseitiges Activate.
Keine neue akustische Aufnahme, Soundausgabe oder Umgebungssprache im Stimulus.

## Einordnung und noch offene Ursachenklärung

Die Grundfolge ohne positiven Stimulus in der abschließenden manuellen Aufnahme
besteht für beide Modelle. Einfache frische Sessions mit positivem Stimulus werden
separat mit Finish/Cancel und Stillekontrollen verglichen;15000msTestfenster dort
ist ausschließlich eine Diagnose, keine Änderung des gewählten5000msDefaults.
[Diagnoseübersicht](EVIDENCE/mute-reinsert-20261020/probe-summary.json).

Nur lesende Prüfung exakt dieses Servercommits: `VoiceSTT/core/recording.py`
führt Wakeinferenz im Zweig `not self.is_recording` aus. In
`VoiceSTT/core/wake_detection.py::release_latch` wird ohne vorhandenen Wake-Latch
vor dem Modellreset zurückgekehrt. `api_fastapi_server/wake_admission.py::release`
delegiert an diese Freigabe. Das ist ein **konkreter Untersuchungsansatz**, noch
kein belegter vollständiger Ursachenbeweis. Zusätzlich Recorder-/Ingressqueues,
absoluten Samplebezug und Mutation/Audio-Reihenfolge instrumentieren.

Keine pauschale Schwellenwerterhöhung oder künstliche Cooldown-Sperre als Fix:
Der zusätzliche Treffer stammt hier nachweislich aus einem definierten Stimulus
und Lifecycleablauf. Ein Fix muss sichere Grenzen für manuelle und Wakeactivations
einschließlich Aufnahmeende, verspäteter Audiopakete und Wiederfreigabe prüfen.
Vorhandene Wake-Latch-/Exactly-once-/Session-/Settingsregeln erhalten.

Betroffen sind mindestens die überlagerten BOTH-/Manual-/Pause-/Recoverygrenzen
von M-03/M-05/M-07, nicht automatisch alle bisherigen einzelnen Clientbelege.
Der konkrete bisherige W01-Wake→Timeout-/Finish-/Cancelbefund bleibt mit seinen
eigenen bestandenen Nachweisen geschlossen; neue Kombination W02 bleibt offen.
Vor weitergehender Serverumsetzung gilt weiterhin die ausdrückliche Grenze:
Serverproduktcodeänderungen brauchen einen gesonderten Auftrag.
