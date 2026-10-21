# AP-IV2-020/R01 – Dauerlauf, Wake-Anforderungen und Aufräumen

21.10.2026, Fortsetzung desselben R01/Paketbranches/Draft-PR15.
Gesamtstatus **BLOCKED**, Workflow **IMPLEMENTATION_IN_PROGRESS**;
kein REVIEW_READY, keine Eigenabnahme oder Übernahme.
[Auftrag](ZUSATZPROMPTS/033_DAUERLAUF_WAKEANFORDERUNGEN_UND_AUFRAEUMEN.md).

Produkt unverändert `0f6c85e0ecf971e596aae1b7d265dad7132754e2`;
Ausgangs-HEAD `c00637da1ad8e97ebdca49ed92c8b36b6b51cfd2`, Tree
`aacf9855cb8fe8ac4c2112c64cc3022b61379b74`, kanonischer Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
Nur Testhilfen, Regressionen, Belege und Arbeitsakten geändert.
Verwendeter Pro-V2-Server:
`wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`, Commit
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, sauberer Tree
`74f37cad84c5be9e74d880a4b10c3d9623de7da3`, Version2.0.0.
Vor-/Nachinfo und alle echten Hello-Commits sind pro Lauf gesichert.
Kein Server-Lifecycle- oder Produktcodeeingriff.

## Ein zusammenhängender automatischer Dauerlauf

Der dauerhafte [Helfer](../../../../../../../tests/manual/v2/endurance_probe.py)
führt100gemischte Activations über mindestens1800s **nach** erfolgreichem
Bootstrap aus. Manual34/Alexa33/HeyJarvis33,18sSollabstand; niemals zwei
überlappende Stimuli. Nach25/75 eigener Reconnect, nach50 eigener TCP-Abbruch.
180sTimeout für kalten Bootstrap und tatsächliche Finalverarbeitung.
Follow-up5000ms, Pre-Roll320ms, vorhandene unveränderte Wake-Schwelle0,5/1Frame.
Snapshots belegen5000ms/320ms in der eigenen Sitzung. Die ungeänderten geerbten
Wake-Anforderungen werden zusätzlich gegen öffentliche Serverdefaults gelesen;
sie wurden im Dauerlauf nicht pro Sitzung als vollständiges Settingsobjekt
exportiert. Öffentlicher Follow-up-Default bleibt3000ms/Pre-Roll0ms und darf
nicht mit den bewusst abweichenden Sessionwerten verwechselt werden.

Bewusst freigegebene echte Sprachfixtures durchlaufen Produktions-Runtime,
AudioCapture-Thread/Queues, TLS, echte ausgewählte Wake-/ASRmodelle, Controls,
Mirror, Results, persistente History, serielle Injektionsqueue und Logkoordinator.
PortAudio liefert Replay-PCM statt physischem Mikrofon; die Clipboardgrenze
ist ein kontrollierter Backendadapter. **Keine native Paste-, LED-/Sound-,
Frozen- oder physische USB-Abnahme daraus ableiten.** Das vollständige M-12
bleibt für diese Teile NOT_PROVEN. Kein30minPASS aus kurzen Teilversuchen.

### Zwei ausgeschlossene Versuche bleiben erhalten

-20.10., erster Lauf:58Starts/58Finals, letzte Hilfstestzeile FAIL nach57PASS.
  Ursache: ein sofortiges Event-vor-Ack lag nach Zeitstempelrundung unter der
  lokalen exakten Zeitgrenze. Auf unbekannte Activation-IDs umgestellt,
  dauerhafte Regression ergänzt. Kein Produktfehler behauptet; Roh-FAIL erhalten.
-20.10., zweiter Lauf:91erfolgreiche Zeilen,92Starts/92angenommene Transkriptionen,
  aber nur91Finals. Für Slot92 kam innerhalb der damals im Helfer verwendeten
  30s kein Final. TimeoutError,1757,813s inklusive Bootstrap; kein1800s-/100PASS.
  Der Server hatte Eingabeschluss bestätigt, der Client blieb bereit und
  begrenzt. Ausbleibender versus nur verspäteter Serverfinal nicht entschieden.
  Lange180sFinalfrist im Testhelfer hergestellt; kein künstlicher Erfolg oder
  automatisches Wiederholen einer mutierenden Operation. Roh-FAIL bleibt erhalten.

Die HTTP-Instanz-ID wechselte zwischen den beiden Tagen/Messungen bei identischem
Build; schon während des zweiten Laufs wurde die neue ID beobachtet. Keine
unbelegte Behauptung über den genauen Neustartzeitpunkt oder dessen Ursache.
`identityStable` bewahrt die exakte Vor-/Nachgleichheit; zusätzliche Auswertung
unterscheidet **vollständige Buildidentität** von Instanzwechseln bei Recovery.
Geänderter Commit/Tree, unsaubere oder fehlende Buildinfo sowie fremder Hello
bleiben Fehler. Dafür drei gezielte Auswertungsregressionen; keine rückwirkende
Hochstufung des unvollständigen zweiten Laufs.

### Abschließender Lauf am21.10.

**PASS_SCOPED: 1800.015s zusammenhängende Messzeit,
100/100 erfolgreiche Activations**,34Manual/33Alexa/33HeyJarvis. Genau100
eindeutige Starts,100ID-gebundene nichtleere Finals und100Completions;100passende
Historyeinträge/100kontrollierte Injektionsversuche. Keine doppelte Activation,
kein doppelter Final oder ungeprüft wiederholter Pasteversuch.

4 bestätigte Hello-Sessions nach drei eigenen Recoveryaktionen,
unveränderter qualifizierter Serverbuild; kein Server-Lifecycleeingriff.
361 Ressourcenmesspunkte; Tasks nach Bootstrap[9, 14], maximal
1 ausstehende Commands, maximal25
gehaltene Activations/25 Resultterminal-Tombstones.
Privater Commit-Speicher 393.16→402.71MiB,
Maximum402.97MiB. Gemessene Werte und Retention über Reconnects,
Zuwachs9.54MiB. Keine Allokationsursache
gemessen und kein behaupteter Leckfreiheitsbeweis; Speicherprofilierung bleibt
vom bloßen100Activations-PASS getrennt. Keine weiteren agentenerzeugten ASR-
oder Lastproben während dieses abschließenden Laufs; normale Servernutzung unbekannt.

Final nach recording_ended: Median0.046s/P950.468s/
Maximum10.516s. Erste Preview nach recording_started:
Median0.266s/P950.656s/Maximum1.219s.
Vollständige Aktivierungsdauer inklusive Stimulus und
Schließen: Median10.969s/Maximum17.141s. Keine allgemeine
ASR-SLA eingeführt. Medien-/Capturezähler im [Messbericht](EVIDENCE/endurance-wake-20261020/confirmed-summary.json).
Der dauerhaft gespeicherte Messhelfer unter `tests/manual/v2/` reproduziert
alle18Messberichtfelder aus den Rohdaten ohne neuen Testlauf:
[Rechenvergleich](EVIDENCE/endurance-wake-20261020/measurement-recalculation.json).
[Unverändertes Ergebnis](EVIDENCE/endurance-wake-20261020/confirmed-result.json),
[ID-gebundene Auswertung](EVIDENCE/endurance-wake-20261020/confirmed-assessment.json),
[Historybindung](EVIDENCE/endurance-wake-20261020/history-accounting.json).
Reale Modelle, kontrollierter Audio-/Clipboardrand; vollständiges physisches
M-12 bleibt NOT_PROVEN. Frühere beiden Teilzeiten werden nicht angerechnet.
Jarvis-Ersttrefferscores lagen zwischen0.527169
und0.996168; alle33Nutzsätze wurden erkannt.
Dies sind angenommene erste Hits, keine vollständigen Scorekurven und keine
Missratenmessung für strengere Schwellen.

## W02 zuerst unverändert, dann strengere Anforderungen

Die beiden Wiederholungen verwenden denselben ursprünglichen Helferstand
aus `c00637d`, dieselbe überlagerte Pause→Reconnect→manuelle Aufnahme mit
positivem Wakefixture→Cancel-Folge und dieselben wirksamen0,5/1Frame sowie
5000ms/320ms. **0von2Zusatzwakes**, beide PASS_SCOPED;64,344s/65,031s.
Die beiden früheren reproduzierten FAILs bleiben gültig. W02 ist **offen,
aktuell nicht reproduziert**, keine behauptete Heilung.
Beide früheren FAILs und beide neuen unveränderten Wiederholungen tragen
dieselbe HTTP-Instanz-ID `793c2cf377d2439d98a7aac719cc1d3f`. Ein bloßer
Instanzwechsel erklärt die jetzt ausbleibende Reproduktion daher nicht.

`wakeWord.sensitivity` ist die Mindestschwelle des Modelloutputs:
höher bedeutet strengere Anforderungen. Ein Score ist keine kalibrierte
Erkennungswahrscheinlichkeit. Zusätzlich verlangt
`wakeWord.minConsecutivePredictionFrames` aufeinanderfolgende qualifizierende
Frames. Nur Settings der jeweils eigenen Session geändert; keine globalen
Defaults/PATCHes oder bestehenden V1-/V2-Benutzerprofile verändert.

Je Variante vier reale Modellfälle: W02-Überlagerung, direkter Alexa-Nutzsatz,
direkter Hey-Jarvis-Nutzsatz, negative Sprache.

| Schwelle / Frames | W02-Folge | Alexa direkt | Hey Jarvis direkt | Negative Sprache |
|---|---|---|---|---|
|0,75 /2|PASS_SCOPED|PASS_SCOPED|PASS_SCOPED|kein Wake|
|0,85 /2|PASS_SCOPED|PASS_SCOPED|PASS_SCOPED|kein Wake|
|0,90 /2|PASS_SCOPED|PASS_SCOPED|PASS_SCOPED|kein Wake|
|0,85 /3|PASS_SCOPED|PASS_SCOPED|FAIL: kein Wake|kein Wake|
|0,90 /3|PASS_SCOPED|PASS_SCOPED|FAIL: kein Wake|kein Wake|
|0,95 /5|PASS_SCOPED|PASS_SCOPED|FAIL: kein Wake|kein Wake|

Die stärkste geprüfte Variante mit beiden erhaltenen positiven Fixtures ist
**0,90/2Frames**. Erfolgreiche Finaltexte sind hashgleich zur bisherigen
0,5/1-Baseline. Sie ist ein **nicht dauerhaft übernommener Testkandidat**.
Sie würde den früher beobachteten Alexa-Score0,873958 anhand der Schwelle
ausschließen; das beweist weder W02-Ursachenbehebung noch allgemeine
Fehlalarmfreiheit. Unveränderte Baseline bestand bereits. Kleine Stichprobe,
kein neuer menschlicher Livevergleich, keine FAR/FRR-Aussage.
Ein später dauerhaft gewählter Wechsel auf0,90/2 benötigt die betroffenen
Nachweise am geänderten Konfigurationsstand. Der aktuelle Dauerlauf bei0,5/1
wird nicht ungeprüft auf andere Wake-Anforderungen übertragen.

Die0,90/2-Prüfung lief auf der späteren HTTP-Instanz bei gleichem Build;
0,75/2,0,85/2 und3-/5Frame-Vergleiche sowie Baselines auf der vorherigen.
Innerhalb jedes Vergleichslaufs Vor-/Nachinfo identisch. Getrennte gleichzeitige
Dauerlauf-Last dokumentiert; daraus kein kontrolliertes A/B-Experiment mit
isolierter Ursache konstruiert. Alle drei Positivmisses bleiben FAIL.

## Zusätzliche autonome Restnachweise

Reale Produktions-Controls mit NONE für Primary und Secondary in waiting,
recording und followup: keine unerwünschte Mutation, IDs/Phasen/Fristen erhalten;
Abschluss und echte ASR bei den Sprachfällen erfolgreich. Drei PASS_SCOPED,
keine native UI-Phasenmatrix daraus behauptet.

Separater echter Windowsprozess hält Ctrl+Alt+Shift+F24; zweiter eigener
Prozess erhält bei Registrierung Fehler1409. Danach eigene Registrierung
freigegeben. PASS_SCOPED für den OS-Kollisionsvertrag; keine sichtbare
Produktdialog-Kollision, keine fremde Registrierung entfernt.

Neue vollständige Windows-Regression: **1400Tests,0Skips,199,010s,Exit0**.
**70Helfertests**, tatsächlicher Qt-Selbstcheck ohne Clientstart und compileall
PASS. Kein Produktquellcode verändert; keine erneute Produktbuildqualifikation
wegen bloßer Test-/Dokumentänderungen erfunden. Tatsächlich ausgeführte frühere
Helferversionen sind als SHA256-gebundene Quell-Snapshots erhalten.

## Aufräumen

Die frühere pauschale Aussage, Aufräumen sei unmöglich, war zu weitgehend.
Automatische Freigabeprüfung hatte die damaligen Löschbefehle vor ihrer
Ausführung abgelehnt; die genaue Regel war nicht sichtbar. Eine engere,
anschließend zugelassene Aktion löst das praktisch: Archiv-/Quellhashs prüfen,
jede einzelne Datei unmittelbar erneut prüfen und mit LiteralPath
**nichtrekursiv** löschen, danach ausschließlich leere eigene Verzeichnisse.
Keine Umgehung, keine geänderte Freigabe-/Sicherheitsrichtlinie, keine andere
Lösch-API und keine Wiederholung des alten rekursiven Befehls.

Alle23historischen Reste und beide beendeten Dauerlaufversuche sind so entfernt.
Originale benötigter Privatdaten liegen hashgeprüft Git-ignoriert im Projekt;
öffentliche Belege enthalten keine neuen Rohtranskripte/Historydaten.
Die bereits ausdrücklich freigegebenen WAV-Fixtures bleiben unverändert.
Der aktive dritte Lauf ist von jeder Bereinigung ausgeschlossen; auch sein
Prozess-PID ist dem Laufzeitroot prüfbar zugeordnet. V1 bleibt unangetastet.

**Erledigt:** 26 eigene beendete Laufzeitordner/666Dateien entfernt,
 einschließlich aller drei Dauerlaufversuche. Genehmigter Profilnamensraum ist
 leer; Root selbst bleibt bestehen. Private hashgeprüfte Projektarchive bleiben
 Git-ignoriert erhalten. [Löschbelege](EVIDENCE/endurance-wake-20261020/cleanup-receipts.json),
 [abschließendes Inventar](EVIDENCE/endurance-wake-20261020/cleanup-final.json).
 Keine aktive Testinstanz oder offene Aufräumsperre mehr.

## Tatsächlich verbleibende Paketgates

Keine erneuten identischen Manual-/Alexa-/Jarvis-Sprechproben.
Die verbleibenden M-Anteile werden zusammen mit früheren passenden Nachweisen
bewertet, nicht pauschal als neue Wiederholung aller Aufgaben verlangt:

- W02 bleibt offener Grenzbefund; strengere Anforderungen sind eine geprüfte
  Einstellungsvariante, kein nachgewiesener Fix.
- Noch fehlende kombinierte Controls-/Fault-/Settings-/Drain-Nachweise,
  insbesondere M-02/03/04/07/08; aktueller Dauerlauf ersetzt deren gezielte
  Vorgaben nicht. Vorhandene bestandene Teilfälle bleiben erhalten.
- Finaler Frozen-/Windowsblock M-09/10/11: korrekter/falscher Admincheck
  (gültiger Pro-V2-Key fehlt), erhöhte Zielanwendung, Clipboard-/Prozessgrenzen,
  Tray/Overlay/Feedback und Altfinal während aktiver B-Sprache.
- Verbleibende physische USB-/Pausenkombinationen und negative
  Umwelt-/Sprachgrenz-/Kalibrierungsbeurteilung für vollständiges M-12;
  T02/T03/O01 fallgenau abschließen. Kein pauschaler Hardware-PASS aus Replay.

[Belege und Manifest](EVIDENCE/endurance-wake-20261020/),
[Validierung](EVIDENCE/endurance-wake-20261020/validation.json).
