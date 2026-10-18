## Fehler und Auswirkung

**IV2-020-W01:** Nach einer einmal gesprochenen Wakephrase „Alexa“ entstehen zwei getrennte serverseitige Activations. Beide warten ohne Nutzsprache jeweils bis zum 15-Sekunden-Timeout. Die zweite beginnt unmittelbar nach dem Schließen der ersten Eingabe. Der Client zeigt deshalb erneut Aktivierung/Warten und spielt einen weiteren Wake-Ton.

Im separaten echten Modell-Repro erzeugt die bisherige Wiederfreigabe nach pausierter Inferenz einen weiteren Alexa-Treffer bei **ausschließlich digitaler Stille**. Ein Vergleich mit zurückgesetztem Modellpuffer erzeugt keinen zweiten Treffer. Es handelt sich um einen nachgewiesenen Fehler beim Wiederfreigeben der serverseitigen Wake-Erkennung; ein bloßes clientseitiges LED-Replay erklärt den Livebefund nicht.

Betroffen ist die vollständige Wake-/Feedback-/Stabilitätsqualifikation von **AP-IV2-020** im Clientprojekt. Status dort: **BLOCKED / SERVER_FIX_REQUIRED**. Dieses Issue dokumentiert den Defekt; es beauftragt noch keine Umsetzung oder Serverpromotion.

## Identitäten und Umgebung

- Server: [`ada13b011e1d3829f78e7f389e3b927795a2b3be`](https://github.com/marcosudau-vps/voice-stt-server/commit/ada13b011e1d3829f78e7f389e3b927795a2b3be), unverändert, isolierter lokaler Docker-Qualifikationsserver.
- Clientprodukt: [`7bb564690911d52f6dfe884955ddeb6a27eea6ad`](https://github.com/marcosudau-vps/voice-stt-client/commit/7bb564690911d52f6dfe884955ddeb6a27eea6ad), Windows, echter ReSpeaker XVF3800, Qt-Soundausgabe und native LED-Ausgabe.
- Clientpaket: [Draft-PR15, AP-IV2-020/R01](https://github.com/marcosudau-vps/voice-stt-client/pull/15), Branch `work/client-v2/ap-iv2-020`; kanonischer Parent `b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
- Belegstand für alle unten verlinkten Clientdateien: **`bfc428dc023a3d27bce53a1f5847ed90f07ddf36`**, feste Commitlinks.
- Live: Session `b1482c4a-1b6c-43ba-b0d6-d1ef6b8d5f7d`, Generation1, Settingsrevision1; Follow-up5000ms, Pre-Roll320ms. Die zuvor nur erwogene Schwelle0,85 wurde nicht angewandt.
- Separater Repro: echte ausgewählte ONNX-Modelle `hey_jarvis` und `alexa`, echte gepinnte Engine/Evaluator; Policy-Schwelle0,5. Eine vorhandene, ausdrücklich zur Wiederverwendung freigegebene menschliche Aufnahme, danach digitale Stille.
- Keine Änderung an Serverproduktdateien, laufender Serversession, Wire-Protokoll, V1 oder VPS für diese Untersuchung.

## Livebeobachtung vom 18.10.2026

Menschliche Aussage: einmal zu Beginn „Alexa“ gesprochen, danach während beider Wartephasen geschwiegen und beide 15-Sekunden-Timeouts abgewartet.

| MESZ / UTC | Autoritatives Serverereignis | Activation | Alexa-Modellscore |
| --- | --- | --- | ---: |
| 03:04:57,470 / 01:04:57,470Z | `activation.started`, Quelle `wake_word` | `d0ec17a5-8473-4c7a-9184-f9c63423f3eb` | 0,892665445804596 |
| 03:05:12,472 / 01:05:12,472Z | `activation.input_closed`, `timed_out` | dieselbe erste ID | — |
| 03:05:12,775 / 01:05:12,775Z | neue `activation.started`, Quelle `wake_word` | `b8c973cb-a227-4c70-b130-1e6616b59c95` | 0,9919427633285522 |
| 03:05:27,775 / 01:05:27,775Z | `activation.input_closed`, `timed_out` | dieselbe zweite ID | — |

Der neue Start liegt **303ms nach dem ersten Eingabeschluss**. Beide `wakeword.detected`-Ereignisse nennen `wakeWordId=alexa`; unterschiedliche Activation-/Event-IDs und fortlaufende Sequenzen30–37 bei identischer Session/Generation. Keine Sprachsegmente dieser Activations protokolliert. Die Anzeige folgt damit zwei realen Serveraktivierungen.

Zusätzliche Beobachtung: Der erste native Stoppton läuft von03:05:12,507 bis03:05:13,164; der neue Wake-Ton startet03:05:12,786. Beide überlappen. **Das beweist keine akustische Rückkopplung.** Es wurde kein Mikrofon-PCM dieses Liveversuchs gespeichert; seine genaue akustische Ursache bleibt `NOT_PROVEN`.

Scores sind **keine kalibrierten Wahrscheinlichkeiten**. Eine Schwelle0,85 hätte beide Live-Treffer durchgelassen. Eine pauschale Erhöhung wäre deshalb keine nachgewiesene Korrektur.

[Vollständige gefilterte Liveereignisse, IDs, Scores, native Playerereignisse und Metriken](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/wake-retrigger-20261018/live-analysis.json).

## Codebefund am gepinnten Server

1. [`recording.py`, Inferenzguard](https://github.com/marcosudau-vps/voice-stt-server/blob/ada13b011e1d3829f78e7f389e3b927795a2b3be/VoiceSTT/core/recording.py#L273): `not self.wakeword_detected` verhindert weitere Wake-Inferenz während der offenen Activation. Die Modellhistorie wird während der Pause nicht mit den folgenden Audiobuffern fortgeschrieben.
2. [`server.py::_release_wake_latch`](https://github.com/marcosudau-vps/voice-stt-server/blob/ada13b011e1d3829f78e7f389e3b927795a2b3be/api_fastapi_server/server.py#L2695): Freigabe setzt `wakeword_detected=False` und den Zeitmarker zurück.
3. [`WakeDetectionEvaluator.release_latch`](https://github.com/marcosudau-vps/voice-stt-server/blob/ada13b011e1d3829f78e7f389e3b927795a2b3be/VoiceSTT/core/wake_detection.py#L722): Latch/Tracker werden zurückgesetzt und die Policy neu gelesen; kein Reset des vorgelagerten Modells.
4. [`OpenWakeWordEngine.process`](https://github.com/marcosudau-vps/voice-stt-server/blob/ada13b011e1d3829f78e7f389e3b927795a2b3be/VoiceSTT/core/openwakeword_engine.py#L166) verwendet weiterhin dieselbe upstream Modellinstanz mit gepufferter Feature-/Audiohistorie. Eine vorhandene [`reset()`-Schnittstelle](https://github.com/marcosudau-vps/voice-stt-server/blob/ada13b011e1d3829f78e7f389e3b927795a2b3be/VoiceSTT/core/openwakeword_engine.py#L242) ist vorhanden.

[SHA256 der konkret untersuchten Quellen](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/wake-retrigger-20261018/inspected-server-sources.json).

## Reproduzierbarer Vergleich mit echten Modellen

Der [vollständige Reprohelfer](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/probe_wake_rearm.py) verwendet die unveränderte gepinnte Engine und den tatsächlichen `WakeDetectionEvaluator`. Er verändert keinen Serverproduktcode und keine laufende Session.

1. `alexa_pause.wav` bis zum ersten angenommenen echten Wake-Treffer verarbeiten.
2. Diesen Evaluator mit `accept(..., activation_id='replay-first')` latchen. Wie im Recorder während der Activation keine weiteren Audiobuffers an die Engine geben.
3. `release_latch(activation_id='replay-first')` aufrufen; danach ausschließlich fünf Sekunden digitale Stille auswerten.
4. Mit einer neuen identischen Engine wiederholen, jetzt zwischen Freigabe und neuer Auswertung einmal `engine.reset()` als experimentelle Kontrolle aufrufen.

| Variante | Erster Alexa-Treffer | Erneuter Treffer bei digitaler Stille |
| --- | ---: | --- |
| Modellzustand erhalten | 0,9997421503067017 | **Alexa0,8239456415176392 nach240ms** |
| Modellzustand zurückgesetzt | 0,9997421503067017 | **Keiner**, maximaler Alexa-Score0,0000379979610443 |

Nachgewiesen ist die technische Ursachenklasse: Alte Modellhistorie kann beim Wiederfreigeben ohne neue Wakephrase einen neuen Treffer erzeugen. Ein Reset der disposable Vergleichsengine verhindert diesen Fall.

Grenzen: Lifecycle-Gating wird im Repro emuliert, die 15s-Wandzeit wird nicht abgewartet. Digitale Stille ist ein gezielter Teststimulus, kein neuer realer menschlicher Negativtest. Die fehlende Liveaufnahme kann damit nicht rekonstruiert werden. Ein Vergleichsergebnis allein ersetzt noch keine geprüfte Produktkorrektur.

### Eingaben und Ausführung

- [Originale freigegebene WAV](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/samples/alexa_pause.wav): 16kHz, mono, int16, neun Sekunden, echter ReSpeaker. SHA256 `abae5a687cee97d120487c2a601509aba41d056b4428966959a1ef1e467b09b3`.
- [Fixturemanifest mit Herkunft und Nutzungsfreigabe](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/samples/manifest.json).
- [Vollständiges Messergebnis JSON](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/wake-retrigger-20261018/rearm-replay-result.json).
- [Befehl, Exitcode0, Dauer und Clientidentität vor/nach Ausführung](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/wake-retrigger-20261018/rearm-replay.json).
- [Vollständiger gzip-Log](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/wake-retrigger-20261018/rearm-replay.txt.gz).

Der bestehende isolierte Container hat die gepinnten Quellen unter `/qualified`, den Reprohelfer unter `/tmp/iv2-020-human/probe_wake_rearm.py` und die WAV unter `/tmp/iv2-020-human/human-20261015-061411/alexa_pause.wav`. Zum Nachstellen diese verlinkten Eingaben an dieselben temporären Pfade kopieren; keine Produktdateien überschreiben. Der dokumentierte Aufruf lautet:

```text
docker exec -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=1 voicestt-qualification-iv2-020 /opt/venv/bin/python /tmp/iv2-020-human/probe_wake_rearm.py --audio /tmp/iv2-020-human/human-20261015-061411/alexa_pause.wav --out /tmp/iv2-020-human/rearm-replay.json
```

## Erwartetes Verhalten und Korrekturansatz

Nach Eingabeschluss darf die nächste Wake-Auswertung nicht aus alter, vor der Activation gepufferter Modellhistorie einen neuen Trigger erzeugen. Eine tatsächlich neu gesprochene Wakephrase muss weiterhin ohne künstliche Sperrzeit zulässig bleiben.

Die vorhandene Engine-Resetmethode ist ein konkret wirksamer Ansatz. Vor Umsetzung müssen jedoch Locks, In-flight-Inferenz/Callbacks, Absolutsamplecursor, Prediction-Frame-Buchhaltung, Generationen und Wake-Audiogrenze geprüft werden. Das ist ein enger Server-Lifecyclefix; kein Client-Cooldown, kein Verwerfen autoritativer Serverereignisse und keine Protokoll-/Sicherheitsänderung als Workaround.

## Erforderliche Regression und Abnahme

- [ ] Fehlernachweis vor Korrektur dauerhaft als Regression sichern.
- [ ] Wake-Hit → Latch → Eingabeschluss → Stille erzeugt keinen zweiten Treffer.
- [ ] Neue echte Wakephrase direkt nach Wiederfreigabe bleibt zulässig; Alexa und Hey Jarvis testen.
- [ ] Wiederholte Finish-/Cancel-/Timeout-Zyklen, neue Generation, Geräte-/Transportverlust und In-flight-Auswertung bleiben korrekt.
- [ ] Wake-Audiogrenze, Pre-Roll und unmittelbar folgende Nutzsprache bleiben korrekt; keine Vermischung von Activations oder Generationen.
- [ ] Echte Modellreplays, vollständige schnelle Serversuite und betroffene Clientintegration ausführen.
- [ ] Reale positive/negative Mikrofonprobe und kontrolliertes Schweigen nach Timeout wiederholen, Soundrückkopplung zusätzlich getrennt prüfen.
- [ ] Neue Serveridentität dokumentieren und Client-/Serverpaar vor Rückkehr zur vollständigen AP-IV2-020-Qualifikation erneut prüfen.

Der Client bleibt bis zur verifizierten Korrektur blockiert. Kein eigener Review, automatischer Merge, Serverpromotion oder Release ist durch dieses Issue freigegeben.

[Konsolidierte ursprüngliche Client-Findingakte](https://github.com/marcosudau-vps/voice-stt-client/blob/bfc428dc023a3d27bce53a1f5847ed90f07ddf36/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/12_WAKE_REAKTIVIERUNG_W01.md).
