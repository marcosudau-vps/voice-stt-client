## Weißer Idle-Puls bestätigt,19.10.2026

[Direkter realer Vergleich](25_IDLE_BESTAETIGT_UND_LED_ISOLATION.md):20sbei tatsächlich verfügbarer LED-Ausgabe; Mensch „Passt – weiß und angenehme Mindesthelligkeit“. Gewählt: ready_state #FFFFFF, min_brightness0,30, brightness1,0, speed0,45; globale Helligkeit192/255 unverändert. Werte in tests/manual/v2/calibration.yaml und vorhandenen generierten Feedbackprofilen reproduzierbar. CALIBRATION_CONFIRMED nur für direkten Idle-Puls; keine neue Produkt-/Serverdefaultänderung. Andere Phasen/Wake/Frozen bleiben offen, Farbprofile ausdrücklich später.

## Zuordnung des letzten Idle-Vergleichs

[Bericht24](24_IDLE_ZIELZUSTAND_UND_DIREKTVORSCHAU.md): „Es ist in Ordnung so.“ bleibt als Bewertung der sichtbaren LEDs erhalten. Keine Activation/kein Eingabeschluss im Lauf; Ausführung des neuen server.input.idle-Mappings nicht belegt.30/100% deshalb weiter NOT_PROVEN. Direkte LED-only-Vorschau ersetzt die für den Vergleich unnötige Hotkey-/Serverfolge; neue Wahrnehmung ausstehend.

## Feedback und Idle-Puls,19.10.2026

[Physischer Folgeversuch und Vergleich](23_USB_BESTAETIGT_UND_IDLE_KALIBRIERUNG.md): Marco bestätigt Start/Warten/Timeout-/Overlaytimings im manuellen No-Speech-Pfad. Farbschemata ausdrücklich separates späteres Feature. Weißes ready_state bisher per Effektdefault Minimum0,16/Maximum0,55; neuer gewünschter Vergleich Minimum0,30/Maximum1,0, Geschwindigkeit0,45 unverändert. Gesamthelligkeit192/255 bleibt bestehen; Effektprozent sind keine absolute Lichtleistung. Reproduzierbar in tests/manual/v2/calibration.yaml, vom Starter in vorhandenes Feedbackmapping übernommen. Neuer Mindestwert noch CALIBRATION_PENDING bis menschlicher Sichtprüfung; violetter physischer Eindruck am alten Minimum festgehalten, Ursache NOT_PROVEN. Renderer121Zeitpunkte×12LEDs weiß und mindestens76/255 PASS;29Helfer-/1400Windows-Tests PASS. Keine Produkt-/Serverdefaults geändert.

## UX02 reale technische Wartezeit bestätigt

Physisch gehaltenes Shift/Ctrl wurde250ms lang vom Produktworker beobachtet; danach erfolgte eine korrekte native Einfügung ohne Modifier. Mensch bestätigt sichtbaren Text. Technische Grenze1,5s/Poll10ms unverändert, keine neue Default-/Timinganpassung daraus. Nur UX02 geschlossen; übrige subjektive Kalibrierung/Realqualifikation offen.


## UX02: zusätzliche technische Einfügegrenze, 16.10.2026

Am Produkt d95043e: MODIFIER_RELEASE_TIMEOUT_S=1,5s, MODIFIER_POLL_INTERVAL_S=0,01s, Shift/Ctrl/Alt/beide Windows-Tasten. Clientinterne technische Wartegrenze, keine neue frei editierbare Einstellung; keine Änderung von Protokoll-/Serverfristen. Ein gemeinsames Zeitbudget für beide Barrieren, bei Shutdown oder Fokus-/Clipboardwechsel überspringen. Gehaltene Modifier verzögern Einfügung, nicht Final/History. Gezielte Timeout-/Shutdown-/Ownershiptests und volle1390er Regression PASS; physische Wahrnehmung/Bestätigung offen. Acht Sekunden Vorbereitungszeit der Testoberfläche separat, keine Produktkalibrierung. [Aktuelle Qualifikation/Profile](EVIDENCE/ux02/qualification-summary.json).


## Entspannte Teststeuerung

Acht Sekunden Bereitmachen vor Sprechaufforderung, mit `tests.manual.v2 --prepare-seconds 0..30` einstellbar. Nur Testorchestrierung: Follow-up5000ms/Pre-Roll320ms/Sicherheitsgrenzen unverändert. Sichtbare Restzeit zählt tatsächliche Mirrorfrist ab; bei Laden unbekannter Dauer wird verstrichene Wartezeit angezeigt. Lesen/Ergebnisentscheidung ohne kurzen Folgetimer. UX02 verhindert derzeit die vollständige native Ausgabequalifikation.

## Livebestätigung am Produkt17261e6, 16.10.2026

[Zwei getrennt gestartete direkte Wake-Nutzsätze](EVIDENCE/ux01/stepped-20261016-01/assessment.json) mit effektiv5000ms Follow-up/320ms Pre-Roll: Jarvis und Alexa jeweils vollständig, ohne Rufwort, sichtbar mit Leerzeichentrennung. Mensch bestätigt „Beide vollständig, mit Leerzeichen“. Dies stützt den320ms-Livekandidaten und ist keine ausdrückliche Endwahl aller Wake-/Feedbackparameter. Keine neue Rohaufnahme/Grenzannotation. F9-Steuerung bleibt separat nachzuweisen; natürlicher Timeoutjeweils5003ms ab recording_ended gemessen. Keine Produkt-/Serverdefaults geändert.

# Tatsächliche Parameter und Kalibrierung

Stand 2026-10-15. **Gemeinsame Kalibrierung läuft; noch keine final gewählten Defaults.**
Vollständige maschinenlesbare Quellen: [Client/LEFX](EVIDENCE/parameter-inventory.json),
[Serverregistry/effektive Defaults](EVIDENCE/real-server-inventory.json),
[reale Serverkonfiguration](EVIDENCE/local-server-build.json).

## Bedienparameter mit vorhandener Einstellung

| Parameter | Ausgang / zulässige Grenze | Autorität / Wirkung | Geplante Vergleichswerte, noch ungetestet |
| --- | --- | --- | --- |
| InitialSpeechTimeout | 15000; 100..3600000 ms | Server, session next_activation | 8000 / 15000 / 20000 ms |
| FollowupTimeout | 3000; 100..60000 ms | Server, session next_activation | 3000 / 5000 ms (5000 vom Auftraggeber gewünscht) |
| Watchdog Initial/Refresh/Warning | 600000/180000/30000 ms; Initial≥60000, Refresh≥30000, Warning≥5000 und strikt kleiner als beide | Server, session next_activation, keine VAD-Verlängerung | Pflichtvorcheck 60000/30000/5000; danach Ausgang wiederherstellen |
| ClosingRecoveryTimeout | 5000; 1000..30000 ms | technische Servergrenze | zunächst unverändert; Fehler-/Lastbeleg erforderlich |
| Wake sensitivity | 0,5; 0..1 | Server, session next_activation | 0,35 / 0,5 / 0,65 |
| Consecutive prediction frames | 1; Integer≥1 | Server, next_activation; calibration pending | 1 / 2 echte neue Predictionframes |
| Cooldown | 0; ≥0 ms | Server, next_activation; calibration pending | 0 / 500 / 1000 ms |
| Pre-Roll | 0; ≥0 ms, gegen echte Historie geklemmt | Server, next_activation; operational trailing edge, keine garantierte phonetische Grenze | 0 / 80 / 160 ms nach echter Grenzannotation |
| Detector gain | 1,0; 0..3 | Server, next_activation; nur Detektorkopie | 1,0 / 1,5 / 2,0 |
| Noise suppression / Wake-VAD | false / 0,0; bool / 0..1 | Server, next_session; Sessionpatch wird nicht effective | erst bei belegtem Bedarf, ausschließlich lokale Serverdefaults |
| Wake selection/backend | aktuelle kanonische IDs / auto | Auswahl Hello, Backend Server next_session | hey_jarvis + alexa; negative ungewählte Phrase |
| VAD/Sprachende | Silero 0,05, WebRTC 3, Silence 0,55 s, Prebuffer 0,75 s | Serverconfig, außerhalb der 18 V2-Registryfelder | zunächst unverändert, nur über vorhandenen lokalen Configpfad |
| Audio | 16000 Hz, mono, 40 ms | lokaler Client, Formatvertrag | zunächst unverändert |
| Max audio queue / Aufnahmehardcut | 30 s | bestehende Serverconfig; erzwingt auch Finalisierung laufender Segmente nach30s | technischer Bound; verhindert in dieser Ausgangskonfiguration60s-Watchdog. Nicht still zum UX-Tuning ändern |
| Kroko endpoint rules | detection true; trailing silence2,4/1,2s, min utterance20s | vorhandene engine_options, getrennt von V2-Activationtimern | zunächst unverändert; Wechselwirkung mit VAD/Finalisierung prüfen |
| Paste delay / Clipboard | 50 ms / Restore false, Restore delay 300 ms, retries 5×20 ms | Client-YAML | zunächst unverändert; keine UI-Einstellung für beliebige Felder behaupten |
| Overlay fade | 2,0 s; ≥0 | Client-YAML | 1,5 / 2,0 / 3,0 s |
| LED brightness | effektiv 192/255; 0..255 | Client-YAML und lokale UI | 64 / 128 / 192 |
| LED FPS/USBtimeout | 30 Hz / 1000 ms; 1..120 / 50..5000 | technische lokale Ausgabegrenzen | zunächst unverändert |
| LED-Effektparameter | 14 tatsächlich aufgelöste Effekte, Defaults/Ranges im Inventar | vorhandene feedback_mappings und LEFX-Kataloge | nur angebotene Felder vergleichen; kein erfundener globaler Blinktimer |
| Sound | effektiv eingeschaltet, acht gebündelte WAVs; Cuevolumen in Mapping | Client/Qt, Ereigniszeit aus Server-/Domainpfad | Original / leiser; keine frei konfigurierbare Soundverzögerung vorhanden |

Die Legacywerte `session.*` / `dictation_window.*` werden im V2-Betrieb nicht als
zweite Timingautorität benutzt. Beispielsweise ist die frühere extension_seconds
kein zusätzlicher wirksamer V2-Refreshknopf. Der Server legt Refresh je Phase fest.

## Technische aktive Grenzen

V2Transport: Connect15, Admission30, Bootstrap30, Ack5, Close3, Ping20/Timeout20 Sekunden;
1 byteidentischer Commandretry, max16 Pending; Backoff0,5..30 s, Kapazitätswartezeit≥10 s.
Mirror: 512 Events/4MiB, Snapshot5 s, höchstens2 Versuche. Media: 500ms Audioqueue,
Geräteretry0,25 s, Shutdown3 s; Capturequeue floor(500/40)=12 Chunks.

Nur die tatsächlich von V2Runtime weitergereichten YAML-Reconnectwerte beeinflussen
den V2Transport. Die sonstigen `server.hello_timeout`, `ready_timeout`, `ping_interval`
und `start_confirmation_timeout` sind **keine** wirksamen YAML-V2-Drehregler.
Transport-/Mirror-/Media-Konstruktorwerte sind nicht frei verfügbare Produkteinstellungen.
Änderungen daran würden Produktcode und eine gesonderte Freigabe benötigen.

LED-Dataclassdefault64 und Sound-Dataclassdefaultfalse sind durch die Paket-YAML auf
192 bzw. true übersteuert. Für die Kalibrierung gelten die effektiven Werte.

## Mess- und Entscheidungsverfahren

Pro Variante im tatsächlichen Versuch speichern: ID, Client-/Server-/Buildhash,
Konfigurationshash, Ausgangswert, legaler Variantenwert, Samplehash und Score-/Boundarytrace,
Zeit-/Latenzmessung, menschliche Bewertung, gewählter Wert und Begründung.
Jeweils nur eine relevante Parametergruppe ändern; gleiche Audio-/Hardwarebedingungen
vergleichen, NA/NS-Grenzen respektieren. Wiederholung bei Fehlbefund nach autonomer Diagnose.

Vorhandene Profile/Mappings können Testkonfiguration dauerhaft reproduzieren.
Geänderte ausgelieferte Defaults in `voice_stt_client/config.yaml`, native Constructor-
Defaults oder Serverproduktcode werden gebündelt mit konkreten Stellen zur Freigabe
vorgelegt. Ohne diese Freigabe bleibt Produktcode unverändert und die gewählte
Konfiguration wird als reproduzierbare Paketkonfiguration gesichert.

Pro-Modell: erster lokaler Pro16-Versuch scheiterte am Lizenzlimit „Maximum connections
reached“ und wurde beendet. Community-DE64 ist real bereit. Dieser Unterschied wird
nicht als gleichwertige Pro16-Qualifikation ausgegeben; Modellentscheidung vor Finalgate.

## Nachtrag nach Reconnectkorrektur

[Neues Parameterinventar](EVIDENCE/recovery-audit/native/parameter-inventory.json)
und [effektiver Serverstand](EVIDENCE/recovery-audit/native/real-server-inventory.json)
gehören zum korrigierten Produkt. Keine Timingdefaults geändert. 4000ms Follow-up
im Recoveryharness und 60000/30000/5000ms Watchdog im Medien-Stallversuch sind
wegwerfbare Session-Testwerte, keine gewählte Kalibrierung.

Der [Medien-Stallnachweis](EVIDENCE/recovery-audit/real-watchdog-stalled-media.json)
belegt reale Warnung, Ablauf und ASR-Finalisierung ohne Änderung der Servergrenzen.
Bei durchgehendem PCM präemptiert weiterhin der 30s-Hardcut die 60s-Frist;
Grenz-/Dauersprach- und menschliche Wahrnehmungsaussagen werden daraus nicht erfunden.
Die Produktausnahme erlaubt ausschließlich Recoverykorrekturen; eine etwaige
spätere Änderung ausgelieferter UX-Defaults bleibt gebündelt gesondert vorzulegen.

## Erste reale Bedienprobe / Follow-up

[Baselinebeleg](EVIDENCE/human/manual-followup-3000.json): echter Windows-Sourceclient
(Produktbaum41ca761), ReSpeaker, lokaler ada13b0 und reale DE-ASR. Vier vom
Auftraggeber bestätigte Wiederholungen, sieben Finals, jeweils genau ein automatischer
Einfügeversuch `command_sent`. Beide vereinbarten Sätze korrekt im nativen Testeditor.
Kein vollständiger M-01-PASS: Overlap noch offen.

Bewertung3000ms: beim Durchsprechen passend, für Denkpausen möglicherweise eng.
Auf ausdrücklichen Wunsch Vergleich5000ms im isolierten Profil als
`activation.followupTimeoutMs=5000` gespeichert; Sessionbootstrap bestätigt.
[Konfigurationsbindung](EVIDENCE/human/manual-followup-5000-configuration.json).
Variante mit ungefähr vier Sekunden Denkpause und automatischem Ablauf erfolgreich;
menschliche Wahl5000ms unten dokumentiert.

[Zusatzbefund IV2-020-UX01](EVIDENCE/human/ux-findings.json): Zwischen den Finals fehlt ein Leerzeichen, obwohl
`text_injection.append_space=true` eingestellt ist. Kein Verbraucher dieses
Parameters im aktuellen Produktpfad gefunden; Queue schreibt `job.text` unverändert.
Außerhalb der Recoveryfreigabe: keine stille Produktkorrektur. Reproduzierbarer
Nachweis und eng begrenzter Vorschlag werden mit weiteren UX-Befunden gebündelt.

**Menschlich gewählter Follow-up-Wert:5000ms.** Rückmeldung: „Fertig – fünf
Sekunden passen“. [Variantenbeleg](EVIDENCE/human/manual-followup-5000.json):
3,906s reale Segmentpause blieb in einer Activation, automatisches Inputclose
5,015s nach Aufnahmeende; zwei Finals jeweils einmal eingefügt. Der Wert wird
in den isolierten Manual/Wake/Both-Profilen reproduzierbar hinterlegt. Keine
Änderung ausgelieferter oder serverseitiger Defaults; endgültige Gesamtqualifikation
und gegebenenfalls gebündelte Defaultfreigabe bleiben offen.

## Wake-/Nutzsprachgrenze: echte Aufnahmen und vorhandener Pre-Roll

[Sechs bewusst aufgenommene, ausdrücklich zur Wiederverwendung freigegebene WAVs](EVIDENCE/human/samples/README.md)
mit Herkunft/Hashes versioniert. Erste Datei enthält laut menschlicher Bestätigung
kein Wakewort: vor Countdownende gesprochen. Drei gültige positive und drei
negative Samples. Kein falsches Detector-FAIL für die fehlende Wakeaufnahme.

[Echte Scores/Predictionframes](EVIDENCE/human/wake-scores-summary.json) und
[ASR-/Wirevergleich](EVIDENCE/human/wake-replay-calibration.json): bei Pre-Roll0
fehlen im direkten Jarvissatz „der“ und bei Alexa „die gelbe“. Vollständige
Manual-ASR desselben Audios enthält beide vollständigen Nutzsätze.160ms
behebt Jarvis, Alexa beginnt weiterhin mit „Elbe“.320 und480ms erhalten beide
Nutzsätze vollständig, ohne Wakewort im Final. Kleinster bisher erfolgreicher
Versuchswert320ms wird als **Live-Testkandidat**, noch nicht als endgültiger
Wert, in den isolierten Manual/Wake/Both-Profilen hinterlegt. Kein Serverdefault
oder Produktcode verändert; dieser vorhandene Sessionparameter ist zulässige
Kalibrierung. Menschliche Livebewertung und phonetische Annotation bleiben offen.

Drei Negativproben ohne Wake/Activation; drei gültige positive Samples mit
jeweils genau einer echten Activation. Mehrere qualifizierte Alexa-Scoreregionen
im Offlineharness sind keine doppelten Runtimeactivations. Schwelle0,5, Frames1,
Cooldown0 und Gain1 bleiben mangels belegtem Änderungsbedarf zunächst bestehen.

## Fortschreibung am korrigierten Produkt17261e6

Die zusätzliche [UX01-Freigabe006](ZUSATZPROMPTS/006_UX01_FREIGABE.md) betrifft nur die bestehende Ausgabepräferenz, keine Timingdefaults. Alle drei isolierten Profile behalten5000ms Follow-up (menschlich gewählt),320ms Pre-Roll (gemessener Kandidat) und append_space=True; [Save/Load-Roundtrip](EVIDENCE/ux01/config-roundtrip.json) erfolgreich. Globale Produkt-/Serverdefaults bleiben unverändert. [Echter Modellreplay](EVIDENCE/ux01/real-wake-replay320.json): Jarvis/Alexa direkt jeweils eine Activation, vollständiger Nutzsatz ohne Rufwort, keine Aktivierung der drei Negativclips. Alexa-Pausenaufnahme verfehlt die geplante exakte Zielphrase; [manuelle Baseline](EVIDENCE/ux01/alexa-pause-differential.json) enthält denselben Nutztext. Tatsächlich gesprochene Wörter werden bei der gebündelten Annotation bestätigt; kein stilles Umdefinieren der Erwartung. Keine finale allgemeine Wake-/ASR-Qualifikation aus sechs Clips.


## Strengere Wake-Anforderungen,21.10.2026

[Sechs Varianten und unveränderte Baselines](35_DAUERLAUF_WAKEANFORDERUNGEN_UND_AUFRAEUMEN.md):0,75/2,0,85/2und0,90/2 erhalten beide realen positiven Fixtures;3/5Frames verfehlen Jarvis.0,90/2 ist der stärkste erfolgreiche Testkandidat, nicht dauerhaft übernommen oder menschlich gewählt. W02 unverändert0/2reproduziert; historische2FAIL bleiben offen, keine nachgewiesene Heilung. Follow-up5000ms/Pre-Roll320ms unverändert.
