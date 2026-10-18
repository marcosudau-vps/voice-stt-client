# IV2-020-W01 – erneuter Wake-Treffer nach Eingabeschluss

18.10.2026, AP-IV2-020/R01. **OPEN / SERVER_FIX_REQUIRED**.
Clientprodukt `7bb564690911d52f6dfe884955ddeb6a27eea6ad`, gehaltener
kanonischer Parent `b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
Unveränderter lokaler Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Gleicher Paketbranch, gleicher Draft-PR15. Keine Produktänderungen vorgenommen.

## Menschlicher Anlass und tatsächlicher Verlauf

Der Auftraggeber meldet: LED-Effekt an sich in Ordnung. Nach einmaligem Alexa
zwei direkt folgende Wartephasen, beide schweigend bis zum 15s-Timeout.

| Lokale Zeit MESZ | Autoritatives Serverereignis | Alexa-Score |
| --- | --- | --- |
| 03:04:57,470 | erste Activation gestartet | 0,8926654458 |
| 03:05:12,472 | erste Eingabe geschlossen, `timed_out` | — |
| 03:05:12,775 | zweite Activation gestartet | 0,9919427633 |
| 03:05:27,775 | zweite Eingabe geschlossen, `timed_out` | — |

Zwei unterschiedliche Activation-IDs, fortlaufende Event-Sequenzen,
unveränderte Session/Generation, beide `source=wake_word` / `wakeWordId=alexa`.
Keine Sprachsegmente dieser Activations aufgezeichnet. Der Server hat nach
303ms eine neue Aktivierung angenommen. Dies ist kein bloßes LED-Replay oder
doppeltes clientseitiges Anzeigen derselben Activation.

Der erste native Stoppton startet03:05:12,507, die zweite Wake-Tonausgabe
03:05:12,786. Der Stoppton läuft bis03:05:13,164: es gibt also eine Überlappung.
Akustische Rückkopplung ist aus dieser zeitlichen Nähe allein nicht bewiesen.
Es wurde kein Mikrofon-PCM dieses Durchlaufs gespeichert. Modell-Scores sind
keine kalibrierten Wahrscheinlichkeiten. Eine Schwelle0,85 hätte beide Treffer
zugelassen; eine pauschale Erhöhung wäre keine nachgewiesene Fehlerbehebung.

## Nachgewiesene Ursachenklasse im gepinnten Server

Read-only geprüft, Quellenhashes im [Quellnachweis](EVIDENCE/wake-retrigger-20261018/inspected-server-sources.json):

- `VoiceSTT/core/recording.py`: die Bedingung `not self.wakeword_detected`
  verhindert weitere Inferenz während der offenen Wake-Activation.
- `api_fastapi_server/server.py::_release_wake_latch`: Freigabe setzt
  `wakeword_detected=False` und den Zeitmarker zurück.
- `VoiceSTT/core/wake_detection.py::WakeDetectionEvaluator.release_latch`:
  löscht Latch und Trackerzustand, liest die neue Policy; kein Engine-Reset.
- `VoiceSTT/core/openwakeword_engine.py`: die Engine besitzt eigenen
  upstream Modell-/Featurepuffer und eine `reset()`-Schnittstelle. Die alte
  akustische Modellhistorie bleibt über die Inferenzpause hinweg bestehen.

[Reprohelfer](EVIDENCE/human/probe_wake_rearm.py), ausgeführt ausschließlich
als separater Prozess im vorhandenen lokalen Qualifikationscontainer gegen die
echten gepinnten Modelle. Kein Serverdatei-/Sessionpatch, kein neuer Serverstand:

1. Vorhandene ausdrücklich zur Wiederverwendung freigegebene ReSpeaker-WAV
   `alexa_pause.wav` bis zum ersten echten Treffer verarbeiten.
2. Tatsächlichen Evaluator latchen; wie der Recorder während einer Activation
   keine weitere Inferenz ausführen. Danach denselben Latch freigeben.
3. Ausschließlich digitale Stille zuführen, fünf Sekunden Inferenz beobachten.
4. Vergleich mit frischer identischer Engine; diesmal nach Freigabe einmal die
   vorhandene Engine-Resetmethode aufrufen, wiederum nur digitale Stille.

| Vergleich | Erster echter Treffer | Zweiter Treffer bei digitaler Stille |
| --- | --- | --- |
| Modellpuffer erhalten | Alexa0,999742 | Alexa0,823946 nach240ms |
| Modell vor neuer Suche zurückgesetzt | Alexa0,999742 | keiner; maximaler Alexa-Score0,000038 |

Damit ist nachgewiesen: Die bestehende Wiederfreigabe kann ohne neue
Wakephrase aus altem Modellzustand einen weiteren Treffer erzeugen. Die
Zeitspanne passt zum Livebefund, beweist aber ohne dessen PCM nicht die genaue
historische akustische Ursache. Der Test emuliert das Inferenzgating; die
15s-Realzeitpause wird nicht abgewartet. Digitale Stille ist Teststimulus,
kein Ersatz für einen menschlichen negativen Hardware-Abnahmelauf.

## Konkreter Korrekturweg zur gesonderten Entscheidung

Ein enges Server-FIX ist erforderlich. Noch keine FIX-ID, kein neuer Branch
und keine Server-Schreibfreigabe vorhanden. Vorgesehene Rückkehr bleibt dieses
Clientpaket/Produkt/Parent; Ausgangspunkt des Fixes ist der obige Server-SHA.

Die serverseitige Freigabe muss neue Wake-Auswertung von alter Modellhistorie
trennen. Die vorhandene Engine-Resetmethode ist ein reproduzierbar wirksamer
Ansatz; vor Produktänderung müssen Synchronisation, In-flight-Callbacks,
Absolutsamplecursor, Prediction-Frame-Buchhaltung und Generationen untersucht
werden. Kein Client-Cooldown, Unterdrücken autoritativer Events oder künstliches
Warten als Ersatz. Keine Änderung des Wire-Protokolls oder der Triggerautorität.

Erforderliche dauerhafte Regressionen: erster Hit → Eingabeschluss → Stille
ohne zweiten Hit; neue echte Wakephrase sofort nach Wiederfreigabe weiterhin
zulässig; wiederholte Activations, Finish/Cancel/Timeout, Geräte-/Transportverlust,
neue Generation und unmittelbar anschließende Nutzsprache korrekt. Echte
Modellreplays plus schnelle vollständige Serversuite und betroffene
Clientintegration. Nach unabhängigem Fixreview und ausdrücklich erlaubter
Sicherung neue Serveridentität im Client dokumentieren und Paarqualifikation
wiederholen. V1/VPS/produktive Server bleiben geschützt.

Betroffen: AP-IV2-020-Arbeitsinhalte2/3 und Pflichtnachweise für repeated-hit,
Wakepositive/negative, zuverlässiges Trigger-/Feedbackverhalten sowie die
30min-/100-Activations-Qualifikation. Diese Kriterien bleiben offen bzw. der
aktuelle Reaktivierungsfall FAIL; frühere technische Teil-PASS bleiben historisch
erhalten. Kein REVIEW_READY. LED-Muster separat grundsätzlich positiv bewertet;
keine vollständige Feedbackabnahme daraus ableiten.

## Belege

- [Liveereignisse, getrennte IDs, Scores, native Sounds, Metriken](EVIDENCE/wake-retrigger-20261018/live-analysis.json)
- [Echter Modellvergleich](EVIDENCE/wake-retrigger-20261018/rearm-replay-result.json)
- [Aufruf und unveränderte Clientidentität](EVIDENCE/wake-retrigger-20261018/rearm-replay.json)
- [Vollständiger Ausführungslog](EVIDENCE/wake-retrigger-20261018/rearm-replay.txt.gz)

Die explizite aktuelle Nutzergrenze lautet „Serverproduktcodeänderungen oder
Serverpromotion“ unter „Nicht freigegeben“. Der verbindliche
[Serverfixablauf](../../../../PLANUNG/SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md)
§3 verlangt einen tatsächlichen Serverauftrag. Deshalb ist hier nur die
vollständige Diagnose gesichert; eine Fixinstanz muss gesondert beauftragt werden.

## Server-Issue auf ausdrücklichen Wunsch erstellt

[voice-stt-server#7](https://github.com/marcosudau-vps/voice-stt-server/issues/7) enthält Livezeitlinie, Scores/IDs, konkrete Quellverweise, vollständigen echten Modellvergleich, Fixture/Reprohelfer, Grenzen und Abnahmekriterien. [Gesicherter Issueinhalt](EVIDENCE/wake-retrigger-20261018/server-issue-body.md), [Remoteprüfung](EVIDENCE/wake-retrigger-20261018/server-issue.json). Nur Issueanlage autorisiert, kein Server-FIX gestartet.
