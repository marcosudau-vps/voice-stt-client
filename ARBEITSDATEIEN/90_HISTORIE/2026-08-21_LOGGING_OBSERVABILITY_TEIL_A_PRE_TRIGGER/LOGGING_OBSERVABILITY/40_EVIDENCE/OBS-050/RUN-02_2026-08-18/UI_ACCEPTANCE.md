# OBS-050 RUN-02 – UI_ACCEPTANCE (Nachtrag zur Reihenfolge)

Dieses Dokument **ergänzt** `RUN-01_2026-08-17/UI_ACCEPTANCE.md`. Die
RUN-01-Fassung und die Gate-FAIL-Evidence bleiben unverändert erhalten; hier
stehen die Punkte, die der Gate-Review als **W-2** beanstandet hat, sowie die
neuen Nachweise zu B-1 und B-2.

## 1. Richtiggestellte Punkte

Der Gate-Review hält fest, dass A-11 („Historie lädt die neueste Seite zuerst,
**chronologisch dargestellt**") nur die erste Seite abdeckte und zusammen mit
A-12 nicht haltbar war. Die drei betroffenen Zeilen lauten jetzt:

| # | Punkt | Ergebnis | Nachweis |
|---|---|---|---|
| A-11 *(neu formuliert)* | Historie zeigt die **neueste Seite zuerst, neueste Zeile oben**, in genau der Reihenfolge, die der Provider geliefert hat (`newest_first=True`) — **keine** Umkehrung in der Ansicht | erfüllt | `test_history_mode_shows_the_newest_page_first_newest_on_top`; Probe A1 |
| A-12 *(neu formuliert)* | „Weitere laden" hängt die **ältere** Folgeseite unten an; die Anzeige bleibt über **beliebig viele** Seiten streng monoton absteigend, ohne Duplikat und ohne Rückwärtssprung an einer Seitengrenze | erfüllt | `test_display_order_stays_monotone_across_three_history_pages`; Probe A und A' |
| A-13 *(neu formuliert)* | dasselbe über das **automatische** Nachladen am Listenende, ohne Knopfdruck | erfüllt | `test_automatic_load_at_the_list_end_keeps_the_order`; Probe A2 |

## 2. Neue Abnahmepunkte

| # | Punkt | Ergebnis | Nachweis |
|---|---|---|---|
| A-34 | Live-Modus auf **leerem** Ergebnis: keine Zeile, kein Fehler, Timer läuft | erfüllt | `test_live_start_on_an_empty_result_set_then_records_arrive`; Probe B0 |
| A-35 | erster Record nach leerem Ergebnis erscheint **aufsteigend** und in korrekter Reihenfolge | erfüllt | derselbe Test; Probe B1 |
| A-36 | der zweite und jeder weitere Tail liefert **keine** bereits dargestellte Zeile erneut | erfüllt | derselbe Test; Probe B2 |
| A-37 | mehrere aufeinanderfolgende Tails setzen die Reihenfolge fort; `_live_cursor` steht auf dem **neuesten** Record | erfüllt | `test_further_records_after_an_empty_start_extend_the_tail`; Probe B' und B'' |
| A-38 | Filter ohne Treffer, danach Treffer: wie A-35/A-36 | erfüllt | `test_live_start_with_a_filter_that_matches_nothing_then_matches` |
| A-39 | Filterwechsel im laufenden Live-Modus (setzt den Cursor zurück): keine Duplikate, Reihenfolge hält | erfüllt | `test_filter_change_during_live_reseeds_without_duplicates`; Probe D |
| A-40 | Live auf bereits befülltem Store bleibt korrekt (Gate-Gegenprobe C) | erfüllt | `test_live_start_on_a_populated_store_stays_correct`; Probe C |
| A-41 | die Art einer Antwort folgt aus der **Anfrage**; eine wiederholt zugestellte Antwort ändert nichts | erfüllt | `test_a_response_is_interpreted_by_its_request_not_by_the_cursor`; Contract-Test `test_every_query_records_the_kind_of_request_it_was` |
| A-42 | die Anzeigerichtung des aktiven Modus ist in der Statuszeile benannt („neueste oben" / „neueste unten") | erfüllt | `refresh_status`; sichtbar in der Laufzeitprobe |

## 3. Die Ordnungsregel in einem Satz

> Die Tabelle ist **immer** monoton in `logs.id` und zeigt jede Seite in genau
> der Richtung, in die ihre Abfrage gelaufen ist: **Historie absteigend**
> (neueste oben, „Weitere laden" verlängert nach unten in die Vergangenheit),
> **Live aufsteigend** (neueste unten, Auto-Scroll folgt ihnen).

Beide Richtungen sind vertraglich verankert: `QueryFilter.newest_first`
ist mit `True` vorbelegt und die Historie fragt genau so; der Live-Tail ist in
`§9.2` als `WHERE id > :last ORDER BY id` eingefroren, und die Regel
„Auto-Scroll schaltet sich beim Hochscrollen ab" (`§9.3`) setzt voraus, dass
neue Zeilen unten erscheinen. Die einzige Umkehrung im Modul dreht die
absteigende Seed-Seite des Live-Modus in dessen aufsteigende Richtung.

## 4. Unverändert gültig aus RUN-01

A-01 bis A-10 und A-14 bis A-33 aus `RUN-01_2026-08-17/UI_ACCEPTANCE.md`
bleiben unverändert gültig; sie sind von dieser Korrektur nicht berührt und
wurden mit der vollständigen `-k obs050`-Suite (179 Tests) erneut bestätigt.

## 5. Manuelle Restpunkte

Die fünf manuellen Punkte aus `RUN-01_2026-08-17/UI_ACCEPTANCE.md`
Abschnitt 4 gelten weiter (Optik, Kontextmenü als echtes Popup, Dauerlast,
Geometrie über einen echten Prozessneustart, Mehrschirmbetrieb). Neu
hinzugekommen ist ein sechster Punkt:

6. Der Wechsel der Leserichtung beim Umschalten zwischen Historie und Live
   sollte am echten Desktop einmal bewusst angesehen werden. Er ist
   beabsichtigt, in der Statuszeile benannt und folgt der jeweiligen
   Abfragerichtung — aber ob die Beschriftung ausreicht, entscheidet sich am
   laufenden Programm, nicht offscreen.
