# T03: Fortschrittsanzeige der Testoberfläche

19.10.2026 · derselbe AP-IV2-020/R01, Paketbranch und Draft-PR15.
Status: **technisch korrigiert, menschliche Bestätigung offen**.
Produktquellen weiterhin identisch zu7bb5646; Änderungen ausschließlich Testhilfen,
Regressionen und Arbeitsakten. Kein Eigenreview, kein REVIEW_READY.

## Nachgewiesener Fehler

Der aktuelle menschliche Versuch stand in Aufgabe1/Review, ohne übernommene
Ergebnisentscheidung. Zwei reale F8-Activations, zwei ASR-Finals und zwei native
Einfügungen sind belegt. Beide Inputs schlossen mit `timed_out`; kein nativer
Secondary-/F9-Callback ist protokolliert. Daraus wird kein erfolgreicher
Finish-Pflichtfall abgeleitet.

Die Ursache des gemeldeten UI-Verhaltens ist im Testprogramm eindeutig:
`tick()` aktualisierte den Live-Status, aber keine Aufgabenzeile. Diese folgte
nur dem manuellen Schrittknopf. `review_controls()` setzte anschließend die letzte
Zeile; die Darstellung behandelte sämtliche vorherigen Zeilen als erledigt.
Damit war die Anzeige während der Handlung veraltet und danach irreführend.

Der ganze bisherige Lauf wurde in die Git-ignorierte Projektablage
`build/ap-iv2-020-suite/private-archive/suite-20261019-155758-b75d0c/` kopiert und
bis auf den laufenden UI-Heartbeat hashgeprüft. Der beendete externe Laufordner
wurde anschließend entfernt. Öffentliche Belege enthalten nur Metadaten/Hashes.

## Korrektur

- Passiver, begrenzter Beobachter sammelt tatsächliche Aktivierungs-, Aufnahme-,
  Eingabeschluss-, Terminal- und Hotkeyereignisse im Testclient. Alte Generationen
  und doppelte Event-IDs führen zu keinem neuen Fortschritt.
- Status-JSON transportiert diese Beobachtungen zum Qt-Testfenster. Kurze Phasen
  bleiben erhalten, auch wenn sie zwischen zwei UI-Abfragen bereits enden.
- Die Markierung folgt den Ereignissen ohne Schrittknopf. Timer für Cancel/None/
  USB beruhen auf beobachteten Startpunkten. Wahrnehmung und nicht automatisch
  feststellbare Geräte-/Dialoghandlungen bleiben explizite menschliche Bestätigungen.
- Ein Häkchen benötigt eine passende Beobachtung; beendete, aber nicht bestätigte
  Schritte bleiben offen. Insbesondere erzeugt Timeout ohne F9 kein Finish-Häkchen.
- Eigener Start, Wiederholung und Übernehmen/Weiter bleiben erhalten. Es wird kein
  Produktcommand zusätzlich gesendet und kein nächster Versuch automatisch gestartet.
- Schrittwechsel und ihre Herkunft werden in `operator-events.jsonl` aufgezeichnet;
  der UI-Heartbeat nennt aktiven Schritt und bestätigte Schritte.

Beim echten Vorcheck trat zusätzlich ein Windows-Sharingfehler beim atomaren
Ersetzen des Heartbeats auf. Der Helfer wiederholt jetzt ausschließlich das durch
`PermissionError` verhinderte Rename höchstens2s; ein alter vollständiger Snapshot
bleibt erhalten. Permanente Fehler werden weiter ausgelöst. Kein pauschales
Exception-Catch und keine wiederholte Produktmutation.

## Nachweise und Grenzen

[Evidenz und Kandidatenbindung](EVIDENCE/guided-progress-20261019/validation.json):
27 Helfertests PASS; Qt-Integration prüft den tatsächlichen Statusdatei→`tick()`→
Zeilenwechsel ohne Weiter-Klick sowie fehlende F9-Häkchen bei Review. Echte alte
Wireereignisse wurden zusätzlich durch den neuen Beobachter wiedergegeben.
Vollständige1398Windows-Tests ohne Skips PASS, compileall PASS. Erneuter echter
Source-Desktop-/Audio-Vorcheck134Frames, neue Fortschrittsdaten vorhanden,
keine Activations. Dies ersetzt keine menschliche Bestätigung der neuen Anzeige.

[Ursprünglicher Versuch und Replay](EVIDENCE/guided-progress-20261019/finding-and-replay.json)
bleiben als eigener alter Stand erhalten. [Windows-Sharingbefund](EVIDENCE/guided-progress-20261019/sharing-failure.json)
wird nicht nachträglich als erfolgreicher Elternprozesslauf umgedeutet.

Die alte Bedienablage und beide neuen Vorprüfungsordner sind nach Sicherung entfernt.
Die automatische Freigabeprüfung blockierte jedoch trotz Pfadprüfung und privat
hashgeprüfter Sicherung das Entfernen von
`C:\Users\marco\.voice-stt\qualification\AP-IV2-020\progress-regression-20261019-162446`.
Begründung ausschließlich „blocked by policy“. Dieser Ordner bleibt ausdrücklich
als **Aufräumrest** bestehen; keine heimliche Umgehung oder Behauptung vollständiger
Bereinigung. Auch der nachfolgende menschliche Wiederholungslauf ist anschließend
auszuwerten, ins Projekt zu sichern und aufzuräumen.

Nächste Aktion: Aufgabe1 mit der korrigierten Oberfläche erneut selbst starten.
IV2-020-T03 bleibt bis zur menschlichen UI-Bestätigung offen. M-01..M-12,
W01 und übrige offene Pflichten werden durch diese Helferprüfungen nicht geschlossen.
