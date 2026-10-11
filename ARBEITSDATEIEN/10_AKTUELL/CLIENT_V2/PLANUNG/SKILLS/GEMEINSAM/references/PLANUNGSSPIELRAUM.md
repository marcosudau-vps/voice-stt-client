# Verbindlichkeit und Umsetzungsspielraum

Stand: 2026-10-05, Revision 4. Diese Regel gilt für Gesamtplan, Kontrakte, Paketdateien, Matrix und Vorlagen. Die Planung beschreibt überprüfbare Ergebnisse und bietet einen Umsetzungspfad. Sie schreibt keine zusätzliche Architektur vor, wenn vorhandene Komponenten dasselbe Ergebnis verlässlich liefern.

## 1. Vier Arten von Vorgaben

| Art | Beispiele | Umgang während der Umsetzung |
| --- | --- | --- |
| SERVER-IST / Schnittstellenvertrag | Wirefelder, UUIDs, Events, Ackcodes, Byteaudio, Settingsscopes, tatsächliche Serverlimits | Am gepinnten Serverstand unverändert einhalten. Eine Änderung benötigt belegten Befund, eigene Serverkorrektur und aktualisierte Paarqualifikation. |
| Produkt- und Arbeitsanforderung | keine Interim-Injektion, keine doppelten Finals, Datenmigration, erhaltenes Feedback, Benutzerwahl bei Ergebnisverlust; unabhängige Abnahme und menschliche Übernahmefreigabe | Ergebnis und Schutzwirkung sind verbindlich. Änderungen am Nutzerverhalten, Plattformumfang oder Freigabeverfahren benötigen eine ausdrückliche Entscheidung des Auftraggebers. |
| Umsetzungsvorschlag | neue Modul-/Klassennamen, interne Maps, Future oder Callback, SQLite-Spaltennamen, Testdateien, Seitenlayout, interne Reihenfolge der Arbeitsschritte | Agent darf eine einfachere oder besser zum Bestand passende Lösung selbst wählen. Kurze Begründung und tatsächliche Schnittstellen im Runreport; Requirements und Tests müssen vollständig erfüllt bleiben. |
| Technischer Startwert | lokale Audioqueue 500 ms, Paketgröße 40 ms, Resyncpuffer 512 Events / 4 MiB, lokale Ack-/Snapshot-/Connecttimeouts und Backoff | Ausgangspunkt für die erste Umsetzung, keine Servergarantie. Mit begründeter Messung bzw. Fehler-/Lasttest anpassbar. Tatsächliche Werte und Bound-Verhalten dokumentieren. |

`CLIENT-SOLL` allein sagt noch nicht, ob ein interner Lösungsweg oder ein Produktverhalten gemeint ist. In den Kontrakten gelten lokale Startwerte und interne Repräsentationen nach dieser Tabelle; exakte Wirewerte und explizite Produktregeln behalten ihre Verbindlichkeit. Die Matrix enthält die fachliche Pflicht und beim betreffenden Tuningrequirement ausdrücklich den Startwertcharakter.

## 2. Was der Agent selbst entscheiden darf

- Bestehende Parser-, Session-, Logging-, Feedback-, UI- und Testkomponenten erweitern, statt für jeden im Plan genannten Namen eine neue Datei anzulegen.
- Interne Klassen, Funktionen, Module, Callbackformen und Testaufteilung wählen. Öffentliche Übergaben klar dokumentieren; nur tatsächlich betroffene Folgepaketstellen anpassen.
- Zustand intern anders darstellen, sofern Herkunft, Session-/Generationguards, Finalität, deduplizierte Nebenwirkungen und sichere Threadübergaben nachweisbar erhalten bleiben. `ActivationMirror` bezeichnet die fachliche Serverzustandsprojektion, keine vorgeschriebene Klasse.
- SQLite-Spalten, Versionsmechanismus und lokale Configorganisation an den vorhandenen Bestand anpassen. Verlustfreie, transaktionale, idempotente Migration und korrekte V1-/V2-Unterscheidung bleiben Pflicht.
- Qt-Seiten, Gruppen und Dialoge passend zur bestehenden Oberfläche anordnen. Lokale, Session- und Serverwerte müssen verständlich unterscheidbar bleiben; keine feste Zahl neuer Seiten erzwingen.
- Lokale Timeouts, Queues, Retrygrenzen und Retention anhand von Last-, Ausfall- und Latenztests einstellen. Speicher und Wiederholungen bleiben begrenzt; kein Reconnect allein wegen langer ASR-Inferenz.

Solche Entscheidungen benötigen weder einen zusätzlichen Agentenlauf noch eine Vorabfreigabe. Der unabhängige Reviewer beurteilt Funktionsnachweise und Wartbarkeit; eine Abweichung von einem vorgeschlagenen Namen oder Startwert ist für sich kein FAIL.

## 3. Grenzen des Spielraums

Keine stillen Änderungen an Wirevertrag, Nutzerverhalten, Datenbestand, Credentialschutz oder Abnahme. Keine pauschale Neuentwicklung von Logging oder Feedback. Kein Abschwächen von Pflichtnachweisen und kein Umdeklarieren von NOT_RUN zu PASS.

Die Paketfolge bleibt seriell. Kleine technisch notwendige Anschlussänderungen an gemeinsamen Dateien sind im Paket erlaubt und werden im Diff begründet. Ein selbstständiges Folgefeature bleibt dem späteren Paket zugeordnet. Soll eine ganze Anforderung den Paketowner wechseln, wird dies vor dem Paket-PASS ausdrücklich mit dem Auftraggeber abgestimmt und in Matrix/Paketdateien festgehalten; kein zusätzlicher Gate für Routineentscheidungen.

Die nummerierten Umsetzungsschritte sind ein fachlicher Leitfaden. Der Agent kann intern in anderer Reihenfolge arbeiten. Die Paketgrenzen sichern reviewbare Ergebnisse; sie sollen keine provisorischen APIs erzwingen, die der Bestand bereits besser bereitstellt.

## 4. Schlanke Entscheidungsdokumentation

Ein lokaler Dateiname, eine Testaufteilung oder ein kleiner Parameterentscheid gehört kurz in den Runreport. Nur paketübergreifende oder dauerhafte Entscheidungen kommen zusätzlich in die Paketentscheidungsdatei: Ausgangsfrage, gewählte Lösung, Grund, berührte Requirements, Testbeleg und Folgen. Keine doppelte Vollbeschreibung.

Änderungen an der Planung erhalten Datum und Begründung. Original-Prompts und abgeschlossene Reports bleiben unverändert; spätere Erkenntnisse ergänzen einen Nachtrag oder neuen Run. Ein uncommitteter Planstand wird beim Start mit relevanten Dateihashes erfasst. Die Ausführung darf ohne passende Gitfreigabe keinen Plancommit erzwingen.

## 5. Prüfergebnis dieser Überarbeitung

| Zu starre Stelle | Korrektur |
| --- | --- |
| Fehlendes vorgeschlagenes `test_v2_*`-Modul bedeutete FAIL | Fehlende Funktionsabdeckung bedeutet FAIL; vorhandene Tests dürfen erweitert werden. |
| Geplante neue Dateien galten als Pflichtlieferung | Dateiliste ist Einstieg/Zuordnung; tatsächliche Umsetzung und Testmethoden werden übergeben. |
| Maps, konkrete FinalResult-Klasse, Future und immutable Objekte vorgegeben | Fachliche Trennung, Herkunft, Finalität und sichere Veröffentlichung bleiben Pflicht; Repräsentation ist frei. |
| SQLite-Namen und drei feste Settingsseiten | Migrations- und Bedienergebnis bleibt Pflicht, interne Struktur/Layout frei. |
| Lokale 500-ms-/5-s-/512-Event-Werte als Abnahmegrenze | Begründete Startwerte; tatsächliche Konfiguration samt Bound-/Fehlertests abnehmen. |
| Jede Runakte verlangte vier getrennte Berichte | Ein rollenbezogener Report plus Original-Prompt und Evidenzindex; Zusatzdateien nur bei Bedarf. |

Serverbaselines, Wirevokabular, Vertragsvektoren, Produktziele, Paketanzahl und bestätigte Freigaberegeln wurden dabei nicht geändert.
