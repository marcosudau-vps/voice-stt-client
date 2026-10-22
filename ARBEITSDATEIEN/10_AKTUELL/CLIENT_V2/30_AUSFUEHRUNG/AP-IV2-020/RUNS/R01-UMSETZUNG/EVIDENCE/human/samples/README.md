# Wiederverwendbare echte Sprach-Testfixtures

Sechs originale, bewusst per Klick aufgenommene ReSpeaker-WAVs, zusammen rund
1,73MB. Die Aufnahme ist menschlich gesprochen, nicht synthetisch. Windows,
ReSpeaker XVF3800, 16000Hz mono/int16, je neun Sekunden, kein gemeldeter
Inputoverflow. [Manifest und SHA256](manifest.json), je Datei originale Metadaten.

Der Auftraggeber hat das Versionieren und Wiederverwenden dieser sechs
Testaufnahmen ausdrücklich [angefordert](../../../ZUSATZPROMPTS/004_TESTAUFNAHMEN_REPO.md).
Unveränderte Kopien liegen weiterhin lokal. Allgemeine Laufzeit-History,
sonstige private Audiodaten und Credentials gehören nicht zu diesem Datensatz.

| Datei | Tatsächliche Rolle |
| --- | --- |
| jarvis_pause.wav | **Negativkontrolle**: nur Nutzsatz; Mensch bestätigt, dass „Hey Jarvis“ vor Aufnahmebeginn gesprochen wurde. Der ursprüngliche positive Prompt im Metadaten-Snapshot ist keine Ground Truth. |
| alexa_pause.wav | Alexa mit bewusster Pause, danach grüner-Lampe-Satz |
| jarvis_direct.wav | Hey Jarvis direkt vor roter-Ball-Satz |
| alexa_direct.wav | Alexa direkt vor gelber-Tasche-Satz |
| negative_speech.wav | natürliche Nutzsprache ohne ausgewähltes Wakewort |
| unselected_phrase.wav | „Computer“ und Nutzsatz; kein ausgewähltes Wakewort |

Drei gültige positive und drei negative Aufnahmen sind keine breite statistische
Erkennungsqualifikation. Wiederholter Replay erzeugt keine neuen unabhängigen
menschlichen Aufnahmen. Erwartete Sätze sind Prompts; tatsächlich gesprochene
Wörter und phonetische Grenzen müssen gegebenenfalls durch Abhören bestätigt
werden. Fehlender positiver Jarvis-mit-Pause-Fall bleibt offen.

## Messwerkzeuge

- [record_wake_samples.py](../record_wake_samples.py): neue, vom Bediener gestartete
  Aufnahmen; benötigt echten ReSpeaker, eigene Testdesktop-Sitzung vorher beenden.
- [score_real_wake.py](../score_real_wake.py): im isolierten Linux-Servercontainer
  ausführen, unveränderte `/qualified`-ONNX-Inferenz und echte Predictionframes;
  Schwellen-/Minframes-/Pre-Roll-Varianten über den unveränderten Tracker.
- [replay_real_samples.py](../replay_real_samples.py): echte Client-V2-Transport- und
  Mirror-Komponenten gegen den gepinnten lokalen Server, echte ASR/Wake-Modelle.
  `manual` liefert die vollständige Audio-ASR-Referenz, `wake` prüft die Wakegrenze.
  Kein Live-Mikrofon und keine native Texteingabe in dieser Replaymessung.
- [observed_session.py](../observed_session.py): tatsächlicher isolierter Desktop
  für zusätzliche Live-Windows-/Hardwaretests, mit beobachteten IDs/Scores/Timern.

Alle Hilfen liegen außerhalb des Produkts. `--self-check` der ersten beiden
Werkzeuge prüft nur den WAV-Schreiber beziehungsweise Frame-Serializer und ist
kein Modell-/Hardware-PASS. Der Testclient bleibt Produktcommit41ca761; Server
ada13b011e1d3829f78e7f389e3b927795a2b3be, lokales Community-DE64-Modell.

## Reproduzierbarer Windows-Replay

Voraussetzungen: Projektvenv, zuvor isoliert eingerichteter **lokaler** Testserver
auf127.0.0.1:18020 mit exakt dem gepinnten Serverstand und den realen Modellen.
V1/VPS unangetastet lassen. Eingabefixture wird nur gelesen; erkannter Rohtext
wird ausschließlich unter LOCALAPPDATA geschrieben.

```powershell
$proofRoot = Join-Path (Get-Location) 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human'
$replayOut = Join-Path $env:LOCALAPPDATA 'VoiceSTT-Qualification/AP-IV2-020/samples/reuse'
.\venv\Scripts\python.exe "$proofRoot/replay_real_samples.py" --mode manual --audio "$proofRoot/samples/jarvis_direct.wav" --out "$replayOut/manual.json"
.\venv\Scripts\python.exe "$proofRoot/replay_real_samples.py" --mode wake --pre-roll-ms 0 --audio "$proofRoot/samples/jarvis_direct.wav" --out "$replayOut/wake-zero.json"
```

Weitere `--audio`-Argumente bündeln Samples. Pre-Roll ist ein vorhandener
Sessionparameter, im Testharness auf0..1000ms begrenzt; ein Versuchsparameter ist
kein ausgelieferter Default. Den gewählten Wert dem laufenden Kalibrierungsbericht
entnehmen. Vor einer Negativbewertung immer die tatsächliche Manifestrolle lesen.

Der Docker-Scorer erhält die gewünschten WAVs und sein Skript ausschließlich
unter `/tmp/iv2-020-human/`, ausgewählte IDs `hey_jarvis` und `alexa`. Vor dem
Kopieren den Containernamen `voicestt-qualification-iv2-020`, dessen Label
`voice-stt.qualification=AP-IV2-020` und die gepinnte Identität verifizieren.
`/qualified` und Serverproduktcode bleiben unverändert.

Die vorhandenen [realen Scorebelege](../wake-scores-summary.json),
[vollständigen Frames](../wake-scores-full.json.gz) und der
[Sampleindex](../sample-index.json) dokumentieren den ersten Messstand;
laufende Kalibrierung ist [hier](../../../03_KALIBRIERUNG.md) beschrieben.
