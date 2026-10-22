# Teststarter auf menschlichen Wunsch deaktiviert

Die zusätzliche Qualifikationsserverinstanz wurde am18.10.2026 auf ausdrücklichen
Wunsch entfernt, einschließlich zugeordneter Docker-Testcontainer, Images und
benannter Datenvolumes. Der Starter enthält keine Dockeroperationen, Profilzugriffe,
Prozessstarts oder Steuerbefehle mehr. Die bestehende Verknüpfung bzw.
`Start-V2-Testinstanz.cmd` öffnet nur einen Hinweis; der Startknopf ist gesperrt.
Die externe Verknüpfung wurde nicht verändert.

Keine automatische Wiederherstellung/Neuanlage der Testinfrastruktur. Vor einer
späteren Fortsetzung müssen tatsächlich gewünschter Server, vorgeschriebener
Commit und zulässige Laufzeitablage ausdrücklich feststehen. Vorhandene
Qualifikationsskripte bleiben historische/reproduzierbare Werkzeuge; ihre bloße
Existenz erteilt keine Freigabe, erneut einen Server anzulegen.

[Entfernung](../../15_SERVER_ENTFERNT.md),
[Commit-Audit](../../16_SERVER_COMMIT_AUDIT.md).
Drei gezielte Prüfungen des deaktivierten Starters PASS; keine Clientproduktänderung.
