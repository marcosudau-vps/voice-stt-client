# AP-IV2-020/R01 – reale Wakeproben und unvollständige Ruhekontrolle

20.10.2026, gleicher R01/Paketbranch/Draft-PR15. Status **BLOCKED** für die
Gesamtqualifikation, Workflow **IMPLEMENTATION_IN_PROGRESS**.
[Menschlicher Abschluss](ZUSATZPROMPTS/027_DREI_WAKE_LIVEPROBEN_FERTIG.md).
Tatsächlich ausgeführt an Clientspitze `7d4331ae2ca84e1fdb18c2e3d02c1cdbdcbe9e37`,
Produkt unverändert `0f6c85e0ecf971e596aae1b7d265dad7132754e2`, Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`. Kein Server-/Produktcode geändert.

## Aktuelle reale Ergebnisse

Eigener ReSpeaker, bewusste aktuelle menschliche Wakephrase, tatsächlicher
Source-Desktop/Qt-Sound/LED/Overlay, jeweils ausdrücklicher Start und Übernahme.
Alle drei Helloidentitäten stimmen mit dem Servercommit überein;
[Info nach Durchführung](EVIDENCE/wake-live-20261020/server-info-after.json)
identisch zur vorab gespeicherten Identität.
[Client-/Konfigurationsherkunft](EVIDENCE/wake-live-20261020/source-identity.json).

| Aufgabe | Wake-Modellscore | Activations | Nachgewiesene Audiobeobachtung nach Timeout | Ergebnis |
|---|---:|---:|---:|---|
| Alexa, Sound an | 0,995067 | 1 | 20,625s | PASS_SCOPED |
| Hey Jarvis, Sound an | 0,996497 | 1 | 6,954s | PASS_SCOPED |
| Alexa, Sound aus | 0,999471 | 1 | 1,875s | NOT_PROVEN für vollständige5sKontrolle |

Alle Eingaben autoritativ `timed_out`, jeweils ein passender Terminal, keine
zusätzliche Wake-/Activation, kein Sprachsegment/Final, keine Einfügung.
Audio blieb während der ausgewerteten Nachphasen verfügbar, keine Queue-/
Captureüberläufe oder lokalen Issues. Alle Clientprozesse regulär mit Exit0
beendet. Menschliche Beobachtung jeweils **„Wie erwartet“**.
Scores sind Modellausgaben, keine kalibrierten Wahrscheinlichkeiten.
[Vollständige Einzelfallbewertung](EVIDENCE/wake-live-20261020/attempts.json).

Der ursprüngliche W01-Folgeaktivierungsfall ist in beiden aktuellen Proben mit
normalem Soundfeedback nicht wieder aufgetreten. Zusammen mit den
[13realen Modell-/Transportfällen](27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md)
stützt dies den tatsächlich deployed Fix. Keine erneute Serverkorrektur aus
diesen Versuchen erforderlich; die vollständige geplante Sound-aus-Kontrolle
wird dennoch nicht aus einer zu kurzen Beobachtung als bestanden erklärt.

## Weshalb nur die dritte Aufgabe wiederholt wird

Bei Alexa ohne Sound lag der Stopauftrag2,110s nach dem empfangenen Input-Close.
Der letzte echte Audiomesspunkt liegt konservativ nur1,875s danach; die spätere
Prozessbeendigung erweitert diese Beobachtungszeit nicht. Die Anleitung verlangte
fünf Sekunden, der letzte Status enthielt noch `postCloseQuietRemaining=3`.
Die Oberfläche erlaubte bereits „Versuch beenden / auswerten“. Deshalb bleibt
die menschliche Annahme erhalten, die technische vollständige Ruhekontrolle
aber **NOT_PROVEN**. Kein nachgewiesener erneuter Serverfehler.

Reine Testoberfläche angepasst: Ein ausdrücklich angefordertes Beenden während
einer bereits laufenden, konsistent beobachteten Wake-Ruhephase wird vorgemerkt.
Erst nach deren Ablauf sendet die Oberfläche den vorhandenen Stopauftrag.
Keine neue Aufgabe startet automatisch. Fenster schließen bleibt sofortiges
Abbrechen; fehlende/inkonsistente Telemetrie kann keinen PASS oder unendliches
Warten erzeugen. Der Button benennt das Abwarten vorab.
Die neue Oberfläche beobachtet sieben Sekunden mit zwei Sekunden Messreserve:
Bei sekündlichen Audiomesspunkten muss auch der letzte Messpunkt mindestens
fünf Sekunden nach Eingabeschluss liegen. Der Bewertungsmaßstab bleibt fünf
tatsächlich belegte Sekunden; Shutdownzeit ersetzt keine Audiomessung.

[Dauerhafte Auswertung](../../../../../../../tests/manual/v2/wake_live_assessment.py)
und [Regressionen](../../../../../../../tests/manual/v2/test_wake_live_assessment.py)
prüfen echten Hello-/Session-/Activationbezug, Timeout/Terminal, weiterlaufendes
Audio und mindestens fünf Sekunden bis zum letzten echten Audiomesspunkt vor
Stop. Menschliche Bestätigung allein oder ein langes Shutdown ergeben keinen
PASS. `wake_stop_delay` und tatsächlicher Qt-Button/Status-/Commandpfad wurden
ohne Mikrofon geprüft: vorzeitig angefordertes Ende sendet noch keinen Stop,
bei abgelaufener Ruhephase genau einen. Nur Helfer-/UI-Code, keine Produktänderung.

## Status und nächste Aktion

W01: **LIVE_SOUND_ON_PASS_SILENT_CONTROL_INCOMPLETE**. Nur `wake_silent`
erneut bereitstellen; Alexa/Hey Jarvis mit Sound bleiben erfolgreiche aktuelle
Teilnachweise. Vollständige M-02/M-10-/Frozen-/Nutzsprachgrenze-/Both-/30min100-
Qualifikation bleibt weiterhin offen. Keine neue API-/Server-/Produktfreigabe
für diesen rein diagnostischen Nachtrag nötig, kein REVIEW_READY/Eigenreview.

Vor erneuter menschlicher Beteiligung: Helfer-/Qt-/Windowsregression,
Belegexport/Hashprüfung und aktuelle Akten-/PR-Sicherung. Nach der Wiederholung
die tatsächlichen Daten auswerten; einen Schlussstatus erst daraus ableiten.


Validierung abgeschlossen: **48Helfertests und echte Qt-Selbstprüfung PASS**,
erneut **1400Windows-Tests/0Skips/209,903s PASS**, compileall/diffcheck PASS.
[Vollsuitenlog](EVIDENCE/wake-live-20261020/windows-1400.log.gz),
[Validierung/Quellhashes](EVIDENCE/wake-live-20261020/validation.json).
Vollständige menschliche/technische Laufdaten samt Regression privat im Projekt
kopiert und dateiweise hashgeprüft; öffentliche Ereignisse/Identitäten ohne
PCM/Rohtranskript/DB/Credentialwerte. Der beendete Laufordner konnte nicht entfernt
werden: automatische Freigabeprüfung „blocked by policy“. Insgesamt18gesicherte
beendete externe Aufräumreste; keine Umgehung/erneuten Versuche alter Ziele.
[Aufräumzuordnung](EVIDENCE/wake-live-20261020/cleanup.json).
