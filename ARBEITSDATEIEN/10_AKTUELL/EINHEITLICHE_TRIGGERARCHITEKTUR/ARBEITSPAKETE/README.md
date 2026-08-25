# Arbeitspakete

Arbeitspakete sind die agentengerechten Umsetzungseinheiten dieses Arbeitsblocks.

Die verbindlichen Grundregeln für Aufbau, prüfbare Ziele, Akzeptanzkriterien, Validierung und Commit-Verhalten stehen in `../PLANUNG/README.md`.

Konkrete Agentenaufträge werden unmittelbar vor dem jeweiligen Run aus
`AUFTRAGSVORLAGE.md` erzeugt. Parallelisierungswellen, Modellwahl und
Endabnahme stehen in `../PLANUNG/AUSFUEHRUNGS_WORKFLOW.md`.

## Empfohlene Struktur

```text
AP-.../
├── README.md
├── PLAN.md
└── runs/
    └── 01_IMPLEMENTATION/
        ├── PROMPT.md
        ├── REPORT.md
        ├── ABNAHME.md
        └── evidence/
```

`runs/` wird erst mit dem ersten tatsächlichen Run angelegt. Weitere Runs können danach ohne Strukturwechsel ergänzt werden.

Abgeschlossene Arbeitspakete bleiben an ihrem Platz und werden über ihren Status als abgeschlossen gekennzeichnet.

Der Originalprompt wird nach Runstart nicht verändert. Der ausführende Agent
pflegt `REPORT.md`; die koordinierende Endabnahme pflegt `ABNAHME.md`.

Serverpakete werden wegen Repository- und Commitreinheit in der
serverseitigen Aktionsakte unter
`docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-.../` abgelegt. Dieser
Client-Arbeitsblock führt dafür Index und freigegebene SHA, aber keine zweite
Kopie des Reports. Client- und Integrationspakete liegen hier unter
`ARBEITSPAKETE/`.

## Repositorytrennung dieses Arbeitsblocks

- `AP-SRV-*` besitzt ausschließlich Dateien und Produktänderungen im
  Server-Repository.
- `AP-CLI-*` besitzt ausschließlich Dateien und Produktänderungen im
  Desktop-Client-Repository.
- `AP-INT-*` führt koordinierte Tests, Hardwareabnahme und gemeinsame
  Kompatibilitätsdokumentation aus, ändert aber keinen Produktcode.

Schlägt ein Integrationspaket wegen Produktcode fehl, wird ein neues,
eindeutig einem Repository zugeordnetes Korrektur-AP angelegt. Die Korrektur
wird nicht im Integrationspaket versteckt.

## Dokumentationsownership

- Der ausführende Agent aktualisiert im selben AP die tatsächlich betroffene
  kanonische Produktdokumentation seines Repositorys und liefert einen
  strukturierten Abschlussbericht.
- Server-Agents erfüllen zusätzlich die serverseitige Aktions-/Archivpflicht;
  Client-Agents aktualisieren die einschlägigen Fortschritts-, Übergabe- und
  Clientreferenzen.
- Normative Planungsunterlagen, zentrale Gate-Status, Traceability und
  freigegebene Commitpaare werden ausschließlich durch die Endabnahme
  fortgeschrieben. Dadurch schreiben parallele Agents nicht in dieselben
  Steuerungsdateien.

## Commit- und Push-Gate

- Der Agent erstellt den lokalen AP-Commit, pusht ihn aber nicht.
- Bei Abnahmebefunden amended der Agent denselben ungepushten Commit.
- Bei PASS ergänzt die Endabnahme `ABNAHME.md`, amended sie in diesen einen
  Commit und pusht anschließend auf den GitHub-Feature-Branch.
- Folgepakete starten nur auf der tatsächlich gepushten und zentral
  vermerkten SHA.
