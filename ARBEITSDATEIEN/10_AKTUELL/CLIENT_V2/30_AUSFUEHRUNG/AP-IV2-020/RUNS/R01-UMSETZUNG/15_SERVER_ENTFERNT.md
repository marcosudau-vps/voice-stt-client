# Zusätzliche Serverinstanz auf menschlichen Wunsch entfernt

18.10.2026, derselbe AP-IV2-020/R01/Paketbranch/Draft-PR15.

Der Auftraggeber hat ausdrücklich die sofortige Entfernung der zusätzlich
angelegten Serverinstanz verlangt. Diese Anweisung ist umgesetzt. Die frühere
Auslegung von „Server lokal einrichten“ als Einrichtung einer eigenen
Qualifikationsinstanz wird nicht als Freigabe für deren erneute Anlage verwendet.

## Entfernte Dockerressourcen

- `voicestt-qualification-iv2-020` wurde geordnet gestoppt und entfernt.
- Zugehöriger gestoppter Fehler-Testcontainer
  `voicestt-qualification-iv2-020-logfault` entfernt.
- Beide eigenen Images `voicestt-qualification:iv2-020-ada13b0-free` und
  `voicestt-qualification:iv2-020-ada13b0` entfernt.
- Die beiden benannten AP020-Datenvolumes und das nachweislich zum entfernten
  Hauptcontainer gehörende unreferenzierte anonyme Volume entfernt.

Vor Volume-/Imageentfernung wurden bestehende Containerreferenzen geprüft.
Keine globale Dockerbereinigung, kein Force-Prune. Andere Server, Images,
Volumes und die nur lesbar eingebundenen gemeinsamen ASR-Modelle wurden nicht
verändert. Nachkontrolle: keine AP020-Qualifikationscontainer, passenden
benannten Datenvolumes oder Images mit dem AP020-Qualifikationstag mehr vorhanden.

[Exakte IDs, Entfernung und Nachkontrolle](EVIDENCE/server-removal-20261018/removed-resources.json).
Erhaltene Quellenarchive und Belege sind keine laufende Serverinstanz. Sie werden
für den anschließend ausdrücklich verlangten historischen Commit-Audit nur
gelesen; keine neue Instanz wird daraus erstellt.

## Starter deaktiviert

`EVIDENCE/human/test_instance_launcher.py` ist ein Informationsfenster ohne
Dockeroperationen, Profilzugriffe, Prozessstarts oder IPC. Der Startknopf ist
gesperrt. Die bestehende externe Verknüpfung wurde nicht neu geschrieben;
bei ihrem nächsten Aufruf wird der deaktivierte Starter geladen.

Ein bereits geöffnetes älteres Starterfenster kann den entfernten Container
ebenfalls nicht neu anlegen: sein alter Code konnte nur einen vorhandenen
Container prüfen/starten; nach dessen Entfernung scheitert die Prüfung.

[Drei gezielte Prüfungen PASS](EVIDENCE/server-removal-20261018/retired-launcher.json),
[vollständiger Log](EVIDENCE/server-removal-20261018/retired-launcher.txt.gz).
Keine Clientproduktänderung, daher kein neuer Produktbuild/PASS behauptet.

## Fortgeltende Grenze

Keine Wiederherstellung dieses Servers oder Verwendung eines anderen Ziels als
stillschweigende Ersatzlösung. Vor weiteren Server-/Realtests müssen das
tatsächlich gewünschte Ziel, sein erforderlicher Commit und die zulässige
Laufzeitablage feststehen. Der neue [Commit-Audit](16_SERVER_COMMIT_AUDIT.md)
bewertet historische Tests; er startet oder ändert keinen Server.

W01/Server-Issue7 und die übrigen offenen Qualifikationsgates bleiben erhalten.
AP-IV2-020 ist weiterhin BLOCKED, kein REVIEW_READY.
