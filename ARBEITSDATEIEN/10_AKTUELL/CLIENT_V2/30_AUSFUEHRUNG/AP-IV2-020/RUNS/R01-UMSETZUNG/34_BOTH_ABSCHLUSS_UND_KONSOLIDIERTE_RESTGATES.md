# AP-IV2-020/R01 – BOTH bestätigt, Wiederholungen beenden

20.10.2026. Gleicher R01/Paketbranch/Draft-PR15; Gesamtstatus **BLOCKED**,
Workflow **IMPLEMENTATION_IN_PROGRESS**. Produkt unverändert
`0f6c85e0ecf971e596aae1b7d265dad7132754e2`, menschlicher Source-HEAD
`8833f360f7e8c849abaecc90809edfe3e51fc9ce`, Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`. Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
[Bedienantwort und Wunsch nach Abschluss](ZUSATZPROMPTS/032_BOTH_FERTIG_UND_WIEDERHOLUNGEN_BEENDEN.md).

## Aktueller Bedienblock abgeschlossen

[Vier tatsächliche Versuche](EVIDENCE/both-live-20261020/attempts.json),
[Sourceherkunft](EVIDENCE/both-live-20261020/source-identity.json),
[stabile vollständige Serverinfo](EVIDENCE/both-live-20261020/server-info-after.json).
Alle Prozesse Exit0, derselbe qualifizierte Produktstand, bestätigte Helloidentität,
beide Triggerquellen und beide Modelle aktiviert; wirksam5000msFollow-up/320msPre-Roll,
Profile unverändert, keine lokalen Issues. Normales eigenes Sourceeditorfenster.

| Aufgabe | Tatsächlicher Nachweis | Urteil |
|---|---|---|
| Manual,0630512f | Genau1manuelle Activation, akzeptierte F8activate/F9finish,1Final/1passende native Einfügung, Mensch „Wie erwartet“ | PASS_SCOPED für Controls/Transport/Injektion. Erkannter Compound von Hotkeyprobe enthält Schreibvariante; kein behaupteter wortgetreuer ASR-Qualitätspass. |
| Alexa erster Versuch,3f57a080 | Genau1Wake/Activation/Final,336Finalzeichen und passende337Zeichen-Paste, später38Editorzeichen; Finishcommand; Mensch wählte Wiederholen | NOT_PROVEN_OPERATOR_REPEAT. Sollsatz plus zusätzlicher Inhalt erkannt; genaue Herkunft/Bearbeitung ohne PCM/Bedienangabe offen. Kein Doppeltrigger oder doppelte Clientpaste belegt. |
| Alexa übernommene Wiederholung,964a4c2e | Genau1Wake/Activation/Segment/Final; vollständiger Nutzsatz ohne Rufwort genau einmal eingefügt, natürlicher Timeout,18,782s weitere echte Audio-Ruhephase | PASS_SCOPED; Score0,999900043. |
| Hey Jarvis,596fedfb | Genau1Wake/Activation/Segment/Final; vollständiger Nutzsatz ohne Rufwort genau einmal eingefügt, natürlicher Timeout,23,313s weitere echte Audio-Ruhephase | PASS_SCOPED; Score0,996868789. |

Die Endbewertung gilt den drei übernommenen Aufgaben, nicht rückwirkend dem
ersten Alexa-Versuch. Scores sind Modelloutputs, keine kalibrierte Wahrscheinlichkeit
korrekter Erkennung. Ohne PCM keine Aussage über den exakten akustischen Abstand
zwischen Rufwort und Nutzsprache. M-03s Trigger-Rennen und W02 bleiben getrennt.
**Keine erneute identische Manual-/Alexa-/Jarvis-Sprechprobe anfordern.**

## Autonomer realer Watchdog statt weiterer Bedienaufgabe

[Unveränderter Rohdurchlauf](EVIDENCE/both-live-20261020/watchdog-raw.json) und
[vollständiges Log](EVIDENCE/both-live-20261020/watchdog.log.gz): echtes TLS/ASR,
nur vorhandene Sessionparameter Initial60000/Refresh30000/Warning5000ms;
kein Serverdefault-/Produktcode-/Lebenszykluseingriff. Freigegebenes echtes
Sprachfixture: energiestärkster1sAusschnitt unverändert65mal wiederholt. Dieser
künstliche Kontinuitätsstimulus ist weder neues menschliches Dauersprechen noch
TV-Audio oder eine physische Mikrofonqualifikation.

Server lieferte drei saubere Segmente/Finals derselben Activation. Warnung bezog
sich auf Segment3: **55,062s nach dessen Aufnahmebeginn**, bestätigter Eingabeschluss
wegen segment_watchdog_timeout nach **60,015s**, anschließend letzte ASRverarbeitung
und activation.completed. Alle drei aufgenommenen Audios liefern ihren eigenen
nichtleeren Final; keine doppelten IDs oder ausstehenden Commands.

Ursprünglicher Hilfstest erwartete fälschlich genau ein Segment für den gesamten
Stimulus und meldete deshalb **FAIL**, obwohl Warnung/Ablauf/Finals korrekt waren.
Dieser Rohstatus bleibt erhalten. Die korrigierte phasengenaue Auswertung bindet
Warnung und Frist an deren tatsächliche Segment-ID und verlangt sämtliche Finals;
Regression mit mehreren Segmenten sowie fehlendem/falsch gebundenem Final ergänzt.
[Nachauswertung desselben tatsächlichen Laufs](EVIDENCE/both-live-20261020/watchdog-reassessment.json):
**PASS_SCOPED für real warning→expiry→Audioverarbeitung**. Kein zweiter Lauf
behauptet. Gleichbleibendes Voicing ohne Segmentwechsel über volle60s bleibt
NOT_PROVEN; M-04s übrige Phasen/Actions werden damit nicht abgeschlossen.

## Restgates ohne doppelte Sprechaufgaben

Die bestehende Matrix wird nach verlangter Wirkung statt nach wiederholten
Oberflächenaufgaben konsolidiert. Frühere bestandene Teilfälle und heutige
Ergebnisse werden gemeinsam verwendet, soweit Produkt/Server/Mode tatsächlich
passen. Kein kartesisches Durchtesten jeder Hardware-/UIkombination als neues
Pflichtkriterium eingeführt. Pflichtumfang bleibt der Abschnitt5 des
[Testplans](../../../../PLANUNG/REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md).

| Restblock | Noch fehlender Nachweis / Zuständigkeit |
|---|---|
| Automatisierbarer technischer Abschluss | Controls-/NONE-/Kollisionsreste, Wake-only-Controlroute, Netzverlust bei Preview/Final, unabhängiger Logstoreausfall, Settings cancel/finish/vormerken und Drain. Agent bereitet/führt mit vorhandenen Sprachfixtures durch; keine weiteren gleichen menschlichen Sätze. M-01s Manualstart/2Segmente/Finish/Neustart vor Altfinal bereits aus bestehenden passenden Sourcebelegen kombinierbar; aktives B-Diktat mit Altfinal gehört zum Frozen-/M-10-Rest. |
| Ein gebündelter Windows-/EXE-Abschluss | Endgültige EXE am aktuellen Serverpaar mit Tray/Overlay/Feedback und Manual/Wake-Parität, erhöhte Zielanwendung/UAC, Clipboard-Konflikt/Crashgrenzen; richtiger/falscher Admincheck im vorgesehenen sicheren Dialog. Mensch nur für tatsächliche native Handlungen/Wahrnehmung/gegebenenfalls Credentialeingabe. Keine Secrets im Chat. Aktuell kein gültiger Pro-V2-Key im Windowsvault vorhanden; Standardclientmutex frei. |
| Dauer-/Kombinationsabschluss | Ein zusammenhängender realer30min/100gemischte-Activations-Lauf mit Ressourcen-/Latenz-/Recoverymessung und den tatsächlich noch fehlenden Geräte-/Pausenkombinationen. Agent automatisiert mit bewussten vorhandenen Sprachproben, bündelt nötige USB-/Muteaktionen. Kein30minPASS aus vielen kurzen Einzelläufen. |
| Externer Serverbefund W02 | Überlagerte Pause/Recovery/manual-Wakeaudio/Cancelfolge zweimal FAIL bei digitaler Stille. Konkreter [Issueentwurf33](33_W02_SERVER_ISSUE_ENTWURF.md) liegt vor; serverseitige Ursachen-/Korrekturentscheidung gesondert, keine Freigabe zum Serverfix erfunden. Einfacher erfolgreicher BOTH-Durchlauf schließt W02 nicht. |
| Administrative Endabgabe | T02/T03/O01 fallgenau abschließen oder begründet abgrenzen, Endkonfiguration/Buildbezug/Matrix und Evidenz abschließen, externe Aufräumsperre klären; erst danach REVIEW_READY und unabhängige Abnahme. Keine Eigenabnahme/Übernahme. |

Die genannten technischen Reste sind Agentenarbeit, keine neue Liste identischer
Sprechaufgaben für den Menschen. Der30minMindestlauf und W02 lassen keinen
ehrlichen sofortigen Gesamt-PASS zu. Keine neue Testoberfläche automatisch geöffnet.

## Sicherung und Validierung

61Helferregressionen und tatsächlicher Qt-Selbstcheck, compileall/Diffprüfung PASS.
Produktquellhashes unverändert; vorhandene vollständige1400Windows/0Skips/PASS-
Regression bleibt separat gebunden, keine erneute Vollsuite behauptet.
[Validierung](EVIDENCE/both-live-20261020/validation.json),
[61Helfer](EVIDENCE/both-live-20261020/helpers.log.gz), [Qt](EVIDENCE/both-live-20261020/qt.log.gz),
[native Voraussetzungen](EVIDENCE/both-live-20261020/native-prerequisites.json).

Oberfläche regulär geschlossen,44Dateien privat Git-ignoriert archiviert und
pro Datei SHA256-geprüft. Neuer Löschversuch im genehmigten Namensraum automatisch
mit „blocked by policy“ abgelehnt:23beendete gesicherte Aufräumreste, keine
alten Ziele erneut versucht oder Umgehung. [Archivbindung](EVIDENCE/both-live-20261020/private-archive-binding.json),
[Aufräumen](EVIDENCE/both-live-20261020/cleanup.json), [Manifest](EVIDENCE/both-live-20261020/export-manifest.json).
