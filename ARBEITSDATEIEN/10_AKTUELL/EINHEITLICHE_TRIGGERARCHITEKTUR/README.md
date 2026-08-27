# Einheitliche Triggerarchitektur

Aktive Arbeitsakte für die gemeinsame Triggerarchitektur von Server, Client
und ReSpeaker-Feedback.

**Aktuelle Phase:** Implementierung. `AP-SRV-000`, `AP-CLI-000`,
`AP-SRV-010`, `AP-SRV-020`, `AP-SRV-030` (canonical), `AP-SRV-040`
(canonical) und `AP-SRV-050` (canonical) sind abgenommen und gepusht;
`AP-SRV-060` ist das nächste Serverpaket. Der letzte freigegebene
Serverproduktstand ist `c901cda3f2c19eeb78c468524161728498b6e27e`
(`AP-SRV-050` canonical). Die Clientreihe ist technisch entblockt, wird aber
bewusst bis zum Abschluss der Serverlinie (AP-SRV-060 → AP-SRV-070)
deferred.

## Einstieg

1. `NACHVERFOLGUNG/WIEDEREINSTIEG.md` – kontextunabhängige operative
   Übergabe mit Repositories, Branches, SHAs, Lesereihenfolge und nächstem AP.
2. `STATUS.md` und `NACHVERFOLGUNG/AUSFUEHRUNGSSTATUS.md` – aktueller Gate-
   und Dependency-Stand.
3. `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md` – fachliches
   Entscheidungsregister, überholte Annahmen und noch offene technische
   Verträge.
4. `PLANUNG/ZIELBILD.md` – auf den aktuellen fachlichen Stand konsolidiertes
   Zielbild.
5. `NACHVERFOLGUNG/README.md` – kompakter Überblick über Stand, Verlauf,
   Funde und spätere Nachweise.
6. `PLANUNG/ANALYSEN/` – belegte Ist-Analysen. Sie sind Evidence, aber keine
   automatische fachliche Entscheidung.
7. `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md` – verbindlicher technischer
   Vertrag.
8. `PLANUNG/IMPLEMENTIERUNGSPLAN.md` – finaler Plan mit getrennten
   `AP-SRV-*`- und `AP-CLI-*`-Paketen.
9. `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md` – exakte Nachrichtenformen,
   Result-Codes und Transportgrenzen; gemeinsame Beispiele unter
   `PLANUNG/VERTRAGSVEKTOREN/`.
10. `PLANUNG/AUSFUEHRUNGS_WORKFLOW.md` – Ausführungswellen, Modellzuordnung,
   Dokumentationspflicht und Endabnahme.

## Weitere Bereiche

- `ARBEITSPAKETE/` enthält bestehende organisatorische und vorbereitende
  Pakete sowie die Auftragsschablone. Konkrete Implementierungs-Prompts werden
  erst unmittelbar vor dem jeweiligen Run mit aktuellen SHAs erstellt.
- `QUELLEN/` enthält übernommene Rohquellen und Referenzen.
- `IDEEN/` ist ausdrücklich kein Projektwissen und wird nur verwendet, wenn
  ein Auftrag eine konkrete Datei daraus nennt.

## Geltungsregel

Direkt besprochene Entscheidungen werden zuerst in
`PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md` festgehalten und anschließend in
`PLANUNG/ZIELBILD.md` konsolidiert. Der aktuelle fachliche Stand ist dort
übernommen. Technischer Contract und finaler Implementierungsplan sind jetzt
eingefroren; Integrationspakete dürfen keinen gemischten Produktcode besitzen.
