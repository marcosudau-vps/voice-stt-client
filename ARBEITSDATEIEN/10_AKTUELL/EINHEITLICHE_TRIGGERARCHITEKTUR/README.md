# Einheitliche Triggerarchitektur

Aktive Arbeitsakte für die gemeinsame Triggerarchitektur von Server, Client
und ReSpeaker-Feedback.

**Aktuelle Phase:** Plan- und Contract-Freeze abgeschlossen; bereit für die
getrennten Server-/Client-Baselinepakete. Es wird derzeit noch kein
Implementierungs-Arbeitspaket ausgeführt.

## Einstieg

1. `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md` – fachliches
   Entscheidungsregister, überholte Annahmen und noch offene technische
   Verträge.
2. `PLANUNG/ZIELBILD.md` – auf den aktuellen fachlichen Stand konsolidiertes
   Zielbild.
3. `NACHVERFOLGUNG/README.md` – kompakter Überblick über Stand, Verlauf,
   Funde und spätere Nachweise.
4. `PLANUNG/ANALYSEN/` – belegte Ist-Analysen. Sie sind Evidence, aber keine
   automatische fachliche Entscheidung.
5. `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md` – verbindlicher technischer
   Vertrag.
6. `PLANUNG/IMPLEMENTIERUNGSPLAN.md` – finaler Plan mit getrennten
   `AP-SRV-*`- und `AP-CLI-*`-Paketen.
7. `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md` – exakte Nachrichtenformen,
   Result-Codes und Transportgrenzen; gemeinsame Beispiele unter
   `PLANUNG/VERTRAGSVEKTOREN/`.
8. `PLANUNG/AUSFUEHRUNGS_WORKFLOW.md` – Ausführungswellen, Modellzuordnung,
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
