# AP-IV2-020/R01 – W01-Kontrolle bestätigt, übrige Pflichtgates offen

20.10.2026, gleicher R01/Paketbranch/Draft-PR15. Status **BLOCKED** für das
Gesamtpaket, Workflow **IMPLEMENTATION_IN_PROGRESS**. Keine Produktkorrektur,
Serveränderung, Eigenabnahme oder Promotion in diesem Nachtrag.
[Menschlicher Abschluss](ZUSATZPROMPTS/028_SOUND_AUS_KONTROLLE_FERTIG.md).

## Auswertung der tatsächlichen Wiederholung

Nur Alexa ohne Sound wurde wiederholt. Quellenstand des Testprogramms
`67470d04c64eb0696ca1438eff46168633048968`, bytegleiches Clientprodukt
`0f6c85e0ecf971e596aae1b7d265dad7132754e2`, Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, kanonischer Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.

- Versuch `5a7126c15423462db947e131580d87cd`, echter ReSpeaker/Source-Desktop,
  aktuelle bewusste menschliche Phrase; Sound im isolierten Profil ausgeschaltet.
- Genau eine Alexa-Detection, Score **0,9873819351**, genau eine Activation
  `507e5200-45b4-4d41-8178-da10d20ab5c9`, reguläres `timed_out`, ein Terminal.
- Tatsächliche Hello-Session `ef58c967-8558-4490-a5a7-160d197022b6` mit richtigem
  Servercommit. Frische vollständige öffentliche Info nach Durchführung identisch
  zur vorab gespeicherten Serveridentität.
- Letzter echter Audiomesspunkt vor Stop **29,765 Sekunden nach Eingabeschluss**;
  Stopauftrag erst nach30,328s.1543Audiopakete insgesamt, Audio während der
  ausgewerteten Ruhephase verfügbar. Keine zweite Detection/Activation,
  kein Sprachsegment/Final, keine Einfügequeue und keine native Einfügung.
- Menschlich „Wie erwartet“ übernommen, regulärer Exit0. Ergebnis **PASS_SCOPED**.

[Einzelfall mit allen Checks](EVIDENCE/wake-silent-confirmed-20261020/attempt.json),
[Quell-/Konfigurationsidentität](EVIDENCE/wake-silent-confirmed-20261020/source-identity.json),
[Info nach Durchführung](EVIDENCE/wake-silent-confirmed-20261020/server-info-after.json),
[vollständiger redigierter Ereignisverlauf](EVIDENCE/wake-silent-confirmed-20261020/events.jsonl.gz).
Scores bleiben Modellausgaben, keine kalibrierten Wahrscheinlichkeiten.

## Schluss zu IV2-020-W01

**CLOSED_VERIFIED_SCOPED:** Der ursprüngliche stale-Wake-Folgetrigger ist am
nachgewiesenen deployed Fix in den vorgesehenen Kontrollen nicht mehr aufgetreten.
Zusammen mit den beiden [aktuellen Sound-an-Proben](28_WAKE_LIVEAUSWERTUNG_UND_RUHEKONTROLLE.md)
sind nun alle drei vorgesehenen aktuellen Mikrofon-/Schweige-/Soundvergleiche
erfolgreich: Alexa Sound an20,625s, Hey Jarvis Sound an6,954s, Alexa Sound aus
29,765s weitere tatsächliche Audiobeobachtung ohne automatische Folgeactivation.
Die [13realen Modell-/Transportfälle](27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md)
mit18Activations ergänzen Timeout/Finish/Cancel/Reconnect sowie begrenzte
Negativ-/Direktsprachefälle. Die frühere zu kurze Sound-aus-Probe bleibt historisch
NOT_PROVEN und wird nicht umgeschrieben.

Dies schließt das konkrete Client-Finding und seinen Serverfix-Rückkehrblocker;
es behauptet keine generelle Fehlalarmfreiheit bei Fernsehen/anderen Stimmen,
vollständige M-02/M-03/M-10/M-12-Abnahme, Frozenparität oder30min100-Erfüllung.
Die getrennte historische TV-/Hintergrundbeobachtung O01 bleibt zu untersuchen.
[Externes Server-Issue7](https://github.com/marcosudau-vps/voice-stt-server/issues/7)
wurde durch diesen Agenten weder kommentiert noch geschlossen.

## Jetzt tatsächlich noch offen

| Block | Konkreter Rest | Durchführung |
|---|---|---|
| Diktat/Controls, M-01/04 | Altfinal/Neuaufnahme-Überlappung, vollständige Finish/Cancel/Refresh/NONE-/Phasenmatrix, reale Watchdogwarnung und Ablauf | Agent bereitet Ereignis-/Timingauswertung vor; bewusste Sprache und echte Hotkeys durch den Menschen. Nur zulässige vorhandene Serverwerte, keine globalen Änderungen. |
| Fehler/Settings, M-05/06/07/08 | Pausen mit aktiver Wakeengine, offener Input/Altfinal bei LED-/Netz-/Logstorefehlern, Settings cancel/finish/vormerken und Drain | Kontrollierte eigene Clientfehler automatisieren; Hardware-Mute/USB und Sprache gebündelt manuell. Serverrestart nur abgestimmt durch Berechtigte. |
| Windows/Frozen, M-09/10/11 | Admin-/Dialog-/Exportfälle, finale EXE am neuen Paar samt Tray/Overlay/Feedback, Clipboardkonflikt/Reinsert/Abbruch nahe Paste und erhöhte Anwendung | Agent prüft technische Anteile; gültiger Adminzugang nur sicher im Dialog, erhöhte Anwendung/UAC und Wahrnehmung durch den Menschen. |
| Wake/Both/Dauer, M-02/03/12 | Weitere positive/negative Umgebungen, unmittelbare Nutzsprachgrenze und Schwelle, Trigger-Rennen/Both; mindestens30Minuten/100gemischte Activations mit Ressourcen/Recovery | Nach jetzt geschlossenem W01 technisch fortsetzbar. Geführter manueller Sprech-/Bedienblock und gemessener Dauerlauf; kein PASS aus kurzen Replays. |
| Dokumentabschluss | T01/T02/T03 und O01 fallgenau erledigen, finale Matrix/Build-/Konfigurationsbindung, Aufräumpflicht, dann REVIEW_READY | Derselbe R01/PR15, anschließend frische unabhängige Abnahme. |

Kein erneuter allgemeiner Fortsetzungsauftrag nötig. Bereits bestätigte UX01/02/03,
R11-USB-Recovery,5sFollow-up, Stoppton und direkter weißer Idle-Puls30–100%
werden nicht ohne technische Änderung erneut dem Menschen vorgelegt.

## Validierung und Datenablage

Produkt und Testverhalten unverändert seit dem letzten belegten Stand; keine neue
Vollsuite als erneut ausgeführt ausgegeben. Vorhandene **1400Windows/0Skips**,
**48Helfer und tatsächliche Qt-Stopprüfung** bleiben gebunden
([Vorlauf](EVIDENCE/wake-live-20261020/validation.json)). Neue Auswertung verwendet
denselben dauerhaften Prüfer und dessen bestehende Regressionen. Dieser Nachtrag
prüft tatsächliche Lauf-/Hash-/Redaktions-/Aktenkonsistenz.
[Validierung/Quellhashes](EVIDENCE/wake-silent-confirmed-20261020/validation.json).

Eigene Testinstanz regulär über die vorhandene IPC geschlossen. Alle14Dateien
des Laufordners einschließlich Profil/History/Logs privat im Git-ignorierten
Projektarchiv kopiert und byteweise per SHA256 geprüft. Öffentliche Exporte
enthalten keine PCM-Datei, Rohtranskripte, Datenbanken oder Credentialwerte.
Das Löschen genau dieses neuen, beendeten und gesicherten Ordners wurde durch
die automatische Freigabeprüfung mit **„blocked by policy“** abgelehnt.
Insgesamt19gesicherte beendete Aufräumreste; alte Ziele nicht erneut angefasst,
keine Umgehung. [Zuordnung](EVIDENCE/wake-silent-confirmed-20261020/cleanup.json).


Die Seitenleiste der Testoberfläche nennt W01 jetzt ebenfalls als konkret
verifiziert; nur Beschreibungstext angepasst. Nach dieser Textpflege erneut
**33gezielte Helferregressionen und tatsächliche Qt-Selbstprüfung PASS**
([Log](EVIDENCE/wake-silent-confirmed-20261020/helpers-33.log.gz),
[Qt](EVIDENCE/wake-silent-confirmed-20261020/qt-stop-deferral.log.gz)).
Keine neue Vollsuite für diese reine Beschriftungs-/Auswertungsänderung.

## Nächster gebündelter Bedienblock

Vorbereitet mit vorhandenen Aufgaben: `followup`, `cancel`, `refresh`, `settings`.
Jede Aufgabe vorab lesbar, eigener Start/10sVorbereitung/Wiederholen/Übernehmen;
kein automatischer Client-/Mikrofonstart beim Öffnen. Neues Profil/Logs nur im
freigegebenen Qualifikationsnamensraum; Child-Hello an denselben bestätigten
Servercommit gebunden. Kein Serverrestart oder globale Defaultsänderung.
Das ist ein weiterer Teil der Restqualifikation, kein Ersatz für die oben
getrennt ausgewiesenen Fault-/Watchdog-/Frozen-/Dauergates.
