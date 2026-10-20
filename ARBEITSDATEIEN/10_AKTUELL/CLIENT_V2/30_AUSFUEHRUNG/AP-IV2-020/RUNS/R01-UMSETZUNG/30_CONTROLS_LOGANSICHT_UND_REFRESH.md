# AP-IV2-020/R01 – Controls/Logansicht ausgewertet, Refresh gezielt ergänzt

20.10.2026, gleicher R01/Paketbranch/Draft-PR15, Status **BLOCKED**,
Workflow **IMPLEMENTATION_IN_PROGRESS**. Quellenstand der menschlichen
Durchführung `f4489e24e47dd7ec58b550c974511e9b13b03991`, Produkt unverändert
`0f6c85e0ecf971e596aae1b7d265dad7132754e2`, Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, kanonischer Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
[Originalantworten](ZUSATZPROMPTS/029_VIER_AUFGABEN_UND_LOGANSICHT.md).

## Was tatsächlich passiert ist

Sechs Versuche für vier Aufgaben, davon vier ausdrücklich übernommen.
Alle sechs Helloidentitäten bestätigen denselben Servercommit; frische Info
nach Durchführung stimmt mit der gespeicherten Identität überein. Alle
Clientprozesse Exit0, keine lokalen Issues an den Messpunkten, Profile unverändert.
[Fallbewertung](EVIDENCE/controls-live-20261020/attempts.json),
[Quellherkunft](EVIDENCE/controls-live-20261020/source-identity.json),
[Info nach Durchführung](EVIDENCE/controls-live-20261020/server-info-after.json).

| Aufgabe | Tatsächlicher Nachweis | Ergebnis |
|---|---|---|
| Denkpause, übernommener Versuch283fedef | Eine Activation, zwei Sprachsegmente/Finals, zwei passende native Hashes einschließlich Leerzeichen, F9 in followup_wait und bestätigtes Finish, wirksames Follow-up5000ms | PASS_SCOPED; genaue akustische Vier-Sekunden-Pause ohne PCM nicht gemessen |
| Cancel, facd08af | F9 während segment_active, akzeptiertes cancel, cancelled/input_closed; weitere82,969s echtes Audio ohne Final/History/Injections/Paste | PASS_SCOPED |
| Refresh,3f9f3ed8 | Kein Refreshcommand. F9 beendet A; explizites F8 erst in idle startet B. Zwei Finals korrekt zu A gehörend eingefügt | NOT_PROVEN für den verlangten nativen Refresh; keine unerklärte Doppelactivation |
| Einstellungen,ef78fb55 | Mensch bestätigt richtiges Ziel, drei Tabs und echte Logs;131persistierte Client-/LED-Logrecords,32Keepalives/54Pongs,0Rawpayloads. Keine Activation/History/Client-Injection | PASS_SCOPED; T01 im Source-Teststarter geschlossen |

Die37Zeichen im letzten Editor sind laut ausdrücklicher Klarstellung die eigene
Nachricht des Menschen. Der Client hat dafür weder einen Final noch einen
Injectionversuch protokolliert; kein neues Produktfinding.

Zwei nicht übernommene erste Denkpausenversuche bleiben NOT_PROVEN: der erste
hatte ein angenommenes ASR-Job, aber bis Stop keinen Final/Terminal, der zweite
nur ein Sprachsegment. Spätere Annahme wird nicht auf sie übertragen. Ein
dauerhafter ASRfehler ist daraus ohne Reproduktion nicht bewiesen.

Der Refresh-Versuch liefert zusätzlich einen echten begrenzten Overlapbeleg:
Final von A/Segment2 kam203ms nach dem Beginn von B an und wurde mit seinen
ursprünglichen A-/Segment-IDs exakt einmal nativ eingefügt. In B wurde vor Stop
keine neue Sprache aufgenommen; das ersetzt nicht die vollständige Overlapmatrix.

Die Einstellungsinstanz sendete28Minuten lang42108Audiopakete, Tasks am warmen
Anfang/Ende10, Maximum12, maximale Einfügequeue0. Das ist ein gemessener
idle-Ausschnitt, kein30min100-Dauer-PASS und kein umfassender Leaknachweis.
T02 bleibt für stillgelegten Starter/fehlschlagendes Erstladen getrennt offen;
die verbundene richtige Serveranzeige ist jetzt ausdrücklich bestätigt. O01s
historisch fehlender Hintergrundterminal ist nicht identisch mit diesem Cancel.

## T04 – unberechtigtes Refresh-Häkchen in der Testoberfläche

Reproduzierbarer Helferfehler: `guide_progress('refresh', ...)` konnte allein
aus zwei Segmenten/Finals plus Secondary/Terminal alle drei Schritte abhaken,
obwohl kein Refreshcommand existierte. Neue Regression vor Korrektur FAIL
([Originalnachweis](EVIDENCE/controls-live-20261020/progress-before.log.gz)).

Korrektur ausschließlich in Testhelfern: Schrittbestätigung braucht zusätzlich
ein akzeptiertes Refresh der aktuellen Activation. Ablehnung, falsche ID und
alte Generation zählen nicht. Der tatsächliche Qt-Status-/Poll-/Zeilenpfad
wurde ohne Mikrofon geprüft: ohne Ack kein Häkchen, mit passendem Ack wird es
sichtbar. T04 technisch durch Regression/Qt geschlossen; native Wiederholung
des fachlichen Refreshfalls bleibt gesondert offen. Kein Produktcode geändert.

## Refresh ohne erneute menschliche Belastung technisch geprüft

[Dauerhafter realer Prüfer](../../../../../../../tests/manual/v2/verify_server_fix.py)
ergänzt `--controls-refresh-only`. Zwei zuvor ausdrücklich freigegebene echte
Sprachfixtures werden über reale Produktions-Controls/Settings/Mirror/TLS an
den tatsächlich identifizierten ASRserver gegeben. Nach echtem VAD-Sprachende
wird bei5000msFollow-up nach zwei Sekunden Primary gedrückt, sofort noch einmal,
die alte Deadline überschritten und der neue natürliche Timeout abgewartet.
Kein neuer Server, keine globalen Einstellungen, kein PCM aus Mikrofonaufnahme,
kein Clipboard-/Sound-/physischer Hotkeynachweis aus diesem Prüfer.

Beide Fälle **PASS_SCOPED**: je eine Activation mit nichtleerem echtem ASRfinal,
zwei akzeptierte Refreshcommands für dieselbe ID, neue ungefähr fünfsekündige
Frist, zweites Refresh addiert keine fünf Sekunden, alte Frist überschritten
ohne Eingabeschluss, danach ein natürlicher Timeout/Terminal und leerer Tracker.
[Vollständiger Realnachweis](EVIDENCE/controls-live-20261020/refresh-confirmed.json).

Erste Diagnose bleibt mit einem FAIL erhalten: Im zweiten Fall wurde direkt
beim Terminal eine gerade gestartete Snapshotanforderung als Pending gemessen,
während alle Refresh-/Fristchecks bereits richtig waren. Der Prüfer wartet
jetzt begrenzt auf tatsächlichen Ack-/Snapshotabschluss; kein pauschales Catch,
keine erzwungene erfolgreiche Bewertung und keine Produktkorrektur.
[Erste Diagnose](EVIDENCE/controls-live-20261020/refresh-first.json).

## Entspanntere einzelne native Wiederholung

Nur `refresh` wird neu angeboten; Denkpause, Cancel und Einstellungen bleiben
erfolgreiche aktuelle Teilnachweise. Alle Schritte/Sätze vorab sichtbar, eigener
Start,10sVorbereitung, Wiederholen/Übernehmen. Nur dieses isolierte Testprofil
verwendet15sFollow-up innerhalb des vorhandenen erlaubten Sessionbereichs;
gewählte Bedienkonfiguration und übrige Testfälle bleiben5000ms.
Nach erstem Sprachende F8 erneut; erst nach echtem Refresh-Ack startet der
Drei-Sekunden-Countdown, danach erscheint „JETZT ZWEITEN SATZ SPRECHEN“.
Das ist Testkonfiguration, keine Änderung von Produktdefaults oder Servergrenzen.

## Sicherung, Regression und Restgates

[Validierung](EVIDENCE/controls-live-20261020/validation.json),
[Helfer-/Qt-Nachweise](EVIDENCE/controls-live-20261020/helpers.log.gz),
[Qt](EVIDENCE/controls-live-20261020/qt.log.gz),
[Windows-Vollsuitenlog](EVIDENCE/controls-live-20261020/windows-confirmed.log.gz).
Erster Vollsuitenlauf bleibt FAIL: gesetztes `VOICESTT_CLIENT_CONFIG` widersprach
dem Legacy-Fallbacktest. Isolierter Wiederholungslauf verwendet eigenes
VOICESTT_CLIENT_HOME/config.yaml und lässt diesen Override ungesetzt; kein
geänderter oder übersprungener Produkt-/Regressionstest.
[Erster Lauf](EVIDENCE/controls-live-20261020/windows-first.log.gz).

Konkreter W01 bleibt verifiziert geschlossen. Vollständige M-01..12, insbesondere
Watchdog-/Fault-/Settings-/Runpausekombinationen, finale Frozen-/Admin-/Windows-
Prüfungen und30min100 bleiben offen. Keine Teilbelege zu einem Gesamtpass
erweitert, kein REVIEW_READY/Eigenreview/Merge/Servereingriff.
Alle benötigten privaten Daten werden im Projekt hashgesichert;
[Aufräumstand](EVIDENCE/controls-live-20261020/cleanup.json) und
[Exportmanifest](EVIDENCE/controls-live-20261020/export-manifest.json) sind bindend.


Validierung abgeschlossen: **1400Windows-Tests/0Skips/PASS/194,744s**,
**52Helferregressionen und tatsächliche Qt-Refresh-Ack-Prüfung PASS**;
compileall/diffcheck PASS. Bytegleichheit aller Produktquellen zum tatsächlich
menschlich geprüften Produktstand per gespeicherten Quellhashes geprüft.
Alle108Dateien des beendeten menschlichen/Regressionslaufs privat ins
Git-ignorierte Projektarchiv kopiert und dateiweise SHA256-verifiziert.
Der einmalige Löschversuch für genau diesen neuen beendeten Ordner wurde
automatisch mit „blocked by policy“ abgelehnt: insgesamt20beendete,
gesicherte Aufräumreste. Keine Umgehung oder erneuten Versuche alter Ziele.
