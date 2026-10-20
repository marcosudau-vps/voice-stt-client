# AP-IV2-020/R01 – Serverfix-Rückkehr und Requalifikation

20.10.2026. Gleicher Umsetzer, Branch `work/client-v2/ap-iv2-020`, Draft-PR15.
Status **BLOCKED** für die Gesamtqualifikation, Workflow **IMPLEMENTATION_IN_PROGRESS**.
[Prüfauftrag](ZUSATZPROMPTS/026_SERVERFIX_UND_INFO_PRUEFEN.md). Clientprodukt
unverändert `0f6c85e0ecf971e596aae1b7d265dad7132754e2`; Start-HEAD
`403a745c053a35a9e3849db0da1eaf5e64e84c1f`, kanonischer Parent weiterhin
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.

## Tatsächlicher neuer Serverstand

`https://pro.v2.voice-stt-server.marcosudau.com/api/v2/info` meldet:

| Feld | Beobachteter Wert |
|---|---|
| serverCommit | `67f3ce45f6ea1ff659382e40c194c70bd33d58ff` |
| build.sourceTree | `74f37cad84c5be9e74d880a4b10c3d9623de7da3` |
| build.sourceDirty | `false` |
| build.sourceDate | `2026-10-20T12:50:26Z` |
| serverVersion / packageVersion | `2.0.0` / `2.0.0` |
| distribution / krokoVariant | `voicestt` / `pro` |
| schemaVersion / protocolVersion / identityStatus | `1` / `2` / `complete` |
| serverInstanceId | `793c2cf377d2439d98a7aac719cc1d3f` |

[Info vor](EVIDENCE/server-return-20261020/server-info-before.json) und
[nach](EVIDENCE/server-return-20261020/server-info-after.json) der gesamten
Modellmatrix sind identisch. [Öffentliche Git-/Merge-/CI-Zuordnung](EVIDENCE/server-return-20261020/server-provenance.json):
Baum und Commitdatum stimmen exakt mit dem veröffentlichten Commit überein.
Dieser besitzt den Wakefix-Merge `e761b97334f263a6c51e84314bf3688599b84169`
aus [Server-PR8](https://github.com/marcosudau-vps/voice-stt-server/pull/8)
als direkten Elterncommit. Der weitere Elterncommit ist die Identitätserweiterung
aus [PR10](https://github.com/marcosudau-vps/voice-stt-server/pull/10).
CI auf dem tatsächlich deployed gemeldeten Commit67f3ce45 erfolgreich:
[Serverlauf39425422514](https://github.com/marcosudau-vps/voice-stt-server/actions/runs/39425422514).

Der neue Stand liegt25Commits vor der alten Referenzada13b0. Die Änderung umfasst
Wake-Lifecycle, Build-/Paket-/Kroko-Provenienz und Identität. Unter
`api_fastapi_server/protocol_v2/` ist ausschliesslich `identity.py` verändert;
die bisherigen Wire-/Command-/Eventschemas wurden nicht umgeschrieben.
Die neue öffentliche HTTP-Route ist additiv. Versions-/Commitfelder werden nun
aus installierter Buildidentität gefüllt. Die tatsächlichen Nachrichten wurden
vom unveränderten Clientdecoder/Mirror akzeptiert; kein Client-Protokollpatch.
Der clientseitige SettingsHTTP-Port behält seine bestehende Routenbegrenzung;
die separate Diagnose liest `/info` über einen eigenen begrenzten GET.

Die alte Pinbindungada13b0 und zugehörigen Belege bleiben historische Herkunft.
Für die **neue Paarqualifikation** gilt der obige konkrete Servercommit.
Buildidentität und echter Hello wurden geprüft; ein vollständiger Vergleich
aller Containerdateien/Imageintegrität wird aus `/info` nicht behauptet.
Kein VPS-Eingriff, Serverrestart, Modell-/Globaldefaultwechsel oder Servercode
durch diesen Clientlauf.

## Reale Modell-/Transportmatrix – 13/13 PASS_SCOPED

[Dauerhafter Prüfer](../../../../../../../tests/manual/v2/verify_server_fix.py)
verwendet die sechs ausdrücklich freigegebenen menschlichen ReSpeaker-WAVs
mit geprüftem SHA256 und16kHz/mono/int16. Tatsächliche TLS-Verbindung zum
bestehenden Pro-V2, Produktions-Transport/Settings/ActivationMirror, reale
deployed Wake-/ASRmodelle, Echtzeit-Pacing. Connect/Admission/Bootstrap/HTTP180s.
Eigene Sessionpräferenzen: Follow-up5000ms und Pre-Roll320ms; keine globalen PATCHes.

| Fall | Alexa | Hey Jarvis |
|---|---|---|
| Wake → realer15s-Timeout →5s digitale Stille → neue Phrase →Cancel→5s Stille | PASS | PASS |
| Wake →Finish→5s Stille→neue Phrase→Cancel→5s Stille | PASS | PASS |
| Wake →Cancel→5s Stille→neue Phrase→Cancel→5s Stille | PASS | PASS |
| Wake →Cancel→Stille→neue Verbindung/Generation→Stille→neue Phrase→Cancel→Stille | PASS | PASS |
| Direkte Wakephrase plus Nutzsprache →Finaltext | PASS_SCOPED | PASS_SCOPED |

Drei Negativclips (`negative_speech`, nicht ausgewählte Phrase,
früher ausdrücklich als Wake-ausgelassen annotierter `jarvis_pause`) bleiben
ohne Wake/Activation/Final. Insgesamt18autoritative Activations, keine zusätzliche
Aktivierung in den geprüften Stillephasen, IDs und Eingabeschlüsse stimmen.
Jeder Hello meldet exakt den neuen Servercommit; vor/nach unveränderte Infoidentität.
Ergebnisse: [kompakte Matrix](EVIDENCE/server-return-20261020/summary.json),
[vollständige erlaubte Ereignisse und Konfiguration](EVIDENCE/server-return-20261020/replay-matrix.json),
[kompletter Prozesslog](EVIDENCE/server-return-20261020/replay-matrix.log.gz).

Digitale Stille ist ein gezielter Stimulus; diese Wiederholung ist **kein**
aktueller physischer Raum-/Mikrofon- oder Soundrückkopplungstest. Finaltexte werden
nur über Länge/Hash erfasst. Vollständigkeit des Wortlauts und phonetische
Wake-/Nutzsprachgrenze bleiben ohne neue Bewertung NOT_PROVEN. Scores sind
Modellscores, keine kalibrierten Wahrscheinlichkeiten. M-02/M-03/M-12 sind damit
noch nicht vollständig qualifiziert, kein30min100-Beleg.

## Nativer Client-/Servervorcheck und Regression

Unveränderte tatsächliche Source-Desktopkomposition mit Qt/Bridge/Runtime,
realem ReSpeaker und eigenem Profil:5s READY/Audio, **133Pakete**,
keine Activation. Der zusätzliche redigierte Hello-Beobachter bestätigt
`67f3ce45…` und `2.0.0` in Session `6867345e-c24e-4acc-86bc-945c7d173e52`.
[Native Helloidentität](EVIDENCE/server-return-20261020/native-hello.json),
[nativer Vorcheck](EVIDENCE/server-return-20261020/native-smoke.json).
Das ist Source/idle; Frozenpaar und menschliches Feedback bleiben separat offen.

Erneute volle Windows-Regression **1400PASS/0Skips,191,933s**;
[vollständiger Log](EVIDENCE/server-return-20261020/windows-1400.log.gz).
**43Helfertests PASS**, normale und dreiteilige Wake-Qt-Vorschau/Selbstprüfung
ohne Mikrofon-/Clientstart PASS, compileall/diffcheck und Aktenkonsistenz PASS.
Kein Produktcode geändert, bestehende EXE/Wheel/sdist0f6c85e bleiben ihre
Artefaktidentitäten. Ihre alten Paarbelege werden nicht automatisch auf den
neuen Server übertragen; neuer vollständiger Frozen-/Feedbackfall bleibt offen.

Erster neuer Diagnoseversuch scheiterte vor dem Replay an einem doppelten
`sessionId`-Keyword im eigenen Beobachter, nicht am Server. Fehler und Rohbeleg
[erhalten](EVIDENCE/server-return-20261020/first-observer-failure.json);
getrenntes `bindingSessionId` und dauerhafte Regression ergänzen die13grünen Fälle.
Eine weitere reine Eingangsvalidierung lehnt unvollständige/ungültige erwartete
SHAs und boolesche Versionsfelder ab; die gespeicherten tatsächlichen Infoantworten
werden zusätzlich gegen den endgültigen Prüfer erneut geprüft. Kein geänderter
Replay-/Client-/Serverproduktpfad aus dieser Diagnosehärtung.

## Jetzt vorbereitete reale Wiederholung

Die bestehende geführte Oberfläche bietet optional drei ausdrücklich ausgewählte
Aufgaben: **Alexa mit Sound, Hey Jarvis mit Sound, Alexa ohne Sound**.
Alle Schritte/Rufwörter vorher sichtbar, jede Aufgabe eigener Start,
10s Vorbereitung, reale Ereignisfortschritte, fünf Sekunden angezeigte Ruhephase
nach tatsächlichem Eingabeschluss, Wiederholen/Übernehmen. Kein automatischer
Folgestart. Die bisherigen elf Manualaufgaben bleiben die Standardauswahl.
Die gespeicherte aktuelle Infoidentität bindet jeden gestarteten Child-Hello;
abweichender Servercommit blockiert vor Bootstrap/Audio. LED-Kalibrierung30–100%
und normale Feedbackregeln bleiben erhalten, nur der dritte Test deaktiviert
Sound im eigenen Testprofil.

W01: **SERVER_FIX_DEPLOYED_REPLAY_PASS_LIVE_PENDING**. Issue7 bleibt offen,
bis die dort geforderten aktuellen Mikrofon-/Schweige-/Sound-/Paarbelege
tatsächlich erbracht sind. Diese Phase benötigt die bewusste menschliche
Äusserung und Wahrnehmung. Andere Restfälle aus
[Bericht26](26_AUTONOME_RESTPRUEFUNG_UND_OFFENE_PUNKTE.md) bestehen fort;
deren ehemalige Voraussetzung „Serverfix fehlt“ ist jetzt ersetzt durch
„neues Paar und reale Wakequalifikation abschliessen“.

[Gesamtvalidierung](EVIDENCE/server-return-20261020/validation.json).


Zwei zusätzliche beendete Windows-/native Laufordner wurden vollständig privat
im Projekt kopiert und dateiweise hashgeprüft. Der begrenzte native Löschbefehl
wurde erneut automatisch mit „blocked by policy“ verweigert. Damit17beendete
gesicherte externe Aufräumreste, keine Umgehung/erneuten Versuche alter Ziele.
Die spätere aktive menschliche Testsitzung bleibt bis zu ihrer Auswertung separat
erhalten. [Aufräumzuordnung](EVIDENCE/server-return-20261020/cleanup.json).
