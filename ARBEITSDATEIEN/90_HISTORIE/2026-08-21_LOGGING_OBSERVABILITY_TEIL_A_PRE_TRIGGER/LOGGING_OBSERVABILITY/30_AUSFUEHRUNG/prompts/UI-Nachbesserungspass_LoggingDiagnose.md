# Auftrag: Logging-&-Diagnose-UI gezielt nachbessern

## 1. Arbeitsbereich

Arbeite ausschließlich im Client-Workspace:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Gegenstand dieses Auftrags ist ausschließlich die bereits vorhandene Oberfläche **„Logs & Diagnose“** einschließlich der unmittelbar dafür benötigten UI-nahen Query-/Persistenzfunktionalität.

Der bestehende Logging-/Observability-Unterbau ist bereits umfangreich implementiert und geprüft.

## 2. Arbeitsweise

Dies ist bewusst **kein neues formales Work Package**.

Deshalb:

- keinen neuen Implementation Plan erstellen;
- keine neue Run-/Evidence-Struktur anlegen;
- keine Gate-Dokumentation erstellen;
- keine neuen Architektur- oder Freeze-Dokumente erstellen;
- `CURRENT_STATE.md`, `LOG_VERLAUF.md`, Checklisten und normative Unterlagen nicht verändern;
- nicht zuerst einen Plan zur Genehmigung vorlegen.

Lies den tatsächlichen bestehenden UI-Code, die unmittelbar zugehörigen Query-Schnittstellen und die vorhandenen OBS-050-UI-Tests, verschaffe dir daraus den nötigen technischen Kontext und **beginne anschließend direkt mit der Implementierung**.

Treffe innerhalb des nachfolgend klar abgegrenzten UI-Sollbildes selbständig sinnvolle PySide6-Detailentscheidungen.

Wenn mehrere technisch saubere Varianten möglich sind, wähle diejenige, die:

1. dem üblichen Windows-/Desktop-Verhalten am nächsten kommt;
2. wenig Sonderlogik erzeugt;
3. vorhandene Qt-Model/View-Mechanismen nutzt;
4. den bestehenden Logging-Unterbau möglichst wenig verändert.

---

# 3. Ziel

Die vorhandene Logging-Oberfläche funktioniert grundsätzlich, ist bei der manuellen Sichtprüfung aber noch unnötig breit, teilweise missverständlich beschriftet und in mehreren Bereichen funktional zu eingeschränkt.

Ziel ist ein **produktiver Diagnose-Viewer**, der sich ähnlich selbstverständlich bedienen lässt wie Explorer- oder Tabellenansichten unter Windows.

Prioritäten:

1. **Fehler und inkonsistente Darstellung beheben**
2. **Tabellenbedienung und Sortierung**
3. **Layout sinnvoll verdichten**
4. **Filterbedienung verbessern**
5. **Auswahl, Copy und Export**
6. **Ansicht persistent konfigurierbar machen**
7. **optische Verfeinerung**

---

# 4. Layout vollständig überarbeiten

## 4.1 Aktuelles Problem

Die beiden oberen GroupBoxen `Filter` und `Kontext` beanspruchen jeweils ungefähr eine halbe Fensterbreite, obwohl ihr tatsächlicher Inhalt nur einen kleinen Teil davon benötigt.

Auch der untere Detailbereich wird unnötig über die gesamte Fensterbreite gezogen.

Zusätzlich werden aktuell Informationen des ausgewählten Records als freier Text **außerhalb** des darunterliegenden `Details`-/`Raw`-TabWidgets dargestellt.

Diese Raumaufteilung soll überarbeitet werden.

## 4.2 Zielaufbau

Die Tabelle bleibt der große zentrale Hauptbereich.

Unterhalb der Tabelle soll folgen:

1. eine kompakte **Toolbar** über die verfügbare Breite;
2. darunter eine horizontale Arbeitszeile aus vier Bereichen:

   - **Filter**
   - **Kontext**
   - **Aktionen**
   - **Details / Raw**

Sinngemäß:

```text
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                         LOG-TABELLE                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌────────────────────────── TOOLBAR ────────────────────────────┐
│ Ansicht | Live/History | Auto-Scroll | Refresh | Navigation   │
└───────────────────────────────────────────────────────────────┘

┌──── Filter ────┐ ┌── Kontext ──┐ ┌ Aktionen ┐ ┌─ Details/Raw ──────────┐
│                │ │             │ │          │ │                       │
└────────────────┘ └─────────────┘ └──────────┘ └───────────────────────┘
```

Die Bereiche sollen **nicht gleich breit** gestreckt werden:

- Filter: kompakt;
- Kontext: kompakt;
- Aktionen: schmal;
- Details/Raw: erhält den größten verbleibenden Anteil.

Ein horizontaler `QSplitter` ist ausdrücklich sinnvoll, wenn dadurch die Größen vom Benutzer komfortabel angepasst werden können.

---

# 5. Fehler in der Record-Detaildarstellung beheben

Aktuell werden oberhalb des `Details`-/`Raw`-TabWidgets freie Record-Metadaten dargestellt, während insbesondere der `Raw`-Tab bei den geprüften Einträgen leer erscheint.

Prüfe die tatsächliche Datenbindung.

Ziel:

- kein redundanter loser Record-Text außerhalb der vorgesehenen Detailansicht;
- `Details` zeigt die strukturierten bzw. menschenlesbaren Recorddetails;
- `Raw` zeigt den tatsächlich vorhandenen vollständigen Raw-/JSON-Inhalt des Records;
- wenn kein Raw-Payload vorhanden ist, wird dort ausdrücklich und sauber ein entsprechender Hinweis angezeigt;
- beim Wechsel des ausgewählten Records müssen Details und Raw garantiert zum aktuell ausgewählten Record gehören;
- niemals Inhalte des vorherigen Records stehenlassen.

---

# 6. Filterbereich überarbeiten

## 6.1 Tooltips

Jedes Filter- und Kontextfeld erhält einen kurzen verständlichen Tooltip:

- was wird gefiltert;
- welche Werte werden erwartet;
- welche Besonderheiten gelten.

Der Benutzer soll die Bedeutung nicht aus internen Feldnamen erraten müssen.

## 6.2 Benennungen

Mindestens folgende Beschriftungen ändern:

- `other` → `Andere`
- `Text` → `Suche`
- `Typ (Präfix)` → verständlichere Bezeichnung, bevorzugt **`Ereignistyp`**

`Ereignistyp` beschreibt Werte wie:

- `client.trigger.sent`
- `inference.completed`
- `transcription.realtime_emitted`

deutlich verständlicher als `Typ`.

## 6.3 Quelle / Channel / Level als Multi-Select

Die derzeitigen einfachen ComboBoxen für geeignete kategoriale Filter sollen durch eine kompakte, direkt sichtbare Mehrfachauswahl ersetzt werden.

Bevorzugtes Bedienkonzept:

```text
Quelle
[ Alle ] [ Client ] [ Server ] [ LED ] [ Andere ]

Channel
[ Alle ] [ System ] [ Audit ] [ Transcription ] [ Performance ]

Level
[ Alle ] [ Debug ] [ Info ] [ Warning ] [ Error ] [ Critical ]
```

Technisch können dafür checkbare Buttons, ToolButtons oder eine andere kompakte Qt-Lösung verwendet werden.

Verhalten:

- mehrere konkrete Werte dürfen gleichzeitig aktiv sein;
- `Alle` ist exklusiv;
- wird `Alle` aktiviert, werden Einzelwerte deaktiviert;
- wird ein Einzelwert aktiviert, wird `Alle` deaktiviert;
- wenn kein Einzelwert gewählt ist, muss das Ergebnis semantisch wieder `Alle` entsprechen.

## 6.4 Unmögliche bzw. leere Kombinationen verhindern

Die Filter sollen sich gegenseitig sinnvoll einschränken.

Beispiel:

Wenn `Quelle = Server` aktiv ist, sollen Werte, die grundsätzlich nur für Clientrecords existieren, nicht als scheinbar sinnvolle Auswahl angeboten werden.

Darüber hinaus sollen Werte, die unter dem aktuellen restlichen Filterzustand **0 Treffer** ergeben würden, disabled dargestellt werden.

Beispiel:

Wenn im vorhandenen Datenbestand unter `Quelle = LED` bestimmte Channels niemals vorkommen, sollen diese Channels nicht auswählbar bleiben.

Das soll möglichst als facettierte Filterung auf Basis real vorhandener Records umgesetzt werden.

Keine hartcodierte lange Liste von zufälligen Sonderfällen erzeugen, sofern dieselbe Information sauber aus Query-/Datenbestand ableitbar ist.

UI-nahe Erweiterungen des Query-Layers sind hierfür erlaubt.

---

# 7. Ereignistyp verbessern

`Ereignistyp` soll kein reines blindes Freitextfeld bleiben.

Gewünscht ist eine Auswahl aller tatsächlich bekannten bzw. im Datenbestand vorhandenen Ereignistypen.

Bevorzugt:

- durchsuchbare/editierbare ComboBox oder vergleichbares Control;
- vorhandene Ereignistypen im Dropdown;
- Tippen/Filtern weiterhin möglich;
- Präfixsuche weiterhin möglich, soweit dies dem bestehenden Contract entspricht.

Die Auswahl soll mit den übrigen Filtern sinnvoll zusammenspielen.

---

# 8. Allgemeine Suche verbessern

Das Feld `Suche` soll breiter und eindeutig als allgemeine Freitextsuche erkennbar sein.

Es muss mindestens berücksichtigen:

- Meldung;
- Ereignistyp;
- Component.

Falls weitere bereits indexierte/geeignete textuelle Felder ohne Raw-Payload-Scanning sinnvoll einbezogen werden können, ist das zulässig.

Nicht den gesamten Raw-Payload für jede Suchanfrage ungefiltert durchsuchen und dadurch den Query-Layer unnötig teuer machen.

---

# 9. Kontextbereich verständlicher machen

Beschriftungen:

- `Session` → `Session-ID`
- `Activation` → `Activation-ID`
- `Segment` → `Segment-ID`
- `Korrelation` → `Korrelations-ID`

Weitere vorhandene IDs entsprechend eindeutig benennen.

## 9.1 Activation-Hinweis

Der derzeit dauerhaft sichtbare gelbe Warnhinweis zu `Activation` ist an dieser Stelle zu dominant und erklärt die Einschränkung zugleich nicht ausreichend.

Verschiebe diese Information in:

- Tooltip;
- optional kleines Info-/Warnsymbol neben `Activation-ID`.

Der Tooltip soll verständlich erklären:

- weshalb die Activation-ID diagnostisch eingeschränkt bzw. serverseitig nicht zuverlässig genug für fachliche Gruppierung ist;
- wofür sie dennoch nützlich ist;
- welche ID/Korrelation stattdessen für belastbare Gruppierung verwendet werden sollte, soweit dies aus dem bestehenden Contract eindeutig hervorgeht.

## 9.2 Replay verständlich benennen

Die bisherige Formulierung `Replayte Records anzeigen` ersetzen.

Bevorzugt beispielsweise:

**`Wiederholte Serverereignisse anzeigen`**

Tooltip sinngemäß:

> Zeigt zusätzlich Ereignisse an, die der Server beispielsweise nach einem Reconnect aus seiner Ereignishistorie erneut übertragen hat.

Die genaue Formulierung darf verbessert werden, muss aber für einen Benutzer verständlich sein, der den internen Begriff `Replay` nicht kennt.

---

# 10. Toolbar über der unteren Arbeitszeile

Die derzeitige Zeile oberhalb der Tabelle soll in eine echte kompakte Toolbar überführt werden.

## 10.1 „Quelle: Lokale Diagnosehistorie“

Aktuell existiert dort ein Dropdown mit nur einem Eintrag.

Das ist nicht sinnvoll.

Wenn zurzeit tatsächlich nur ein Provider existiert:

- das Control aus der sichtbaren UI entfernen.

Falls die vorhandene Architektur bereits mehrere echte Datenprovider vorsieht:

- fachlich korrekt **`Datenquelle`** nennen;
- nur dann als Auswahl anzeigen, wenn mindestens zwei sinnvolle Optionen existieren.

Nicht denselben Begriff `Quelle` sowohl für `client/server/...` als auch für den Datenprovider verwenden.

---

# 11. Modus: Live / Historie / Live + Historie

Der Benutzer soll drei Zustände verwenden können:

1. **Live**
2. **Historie**
3. **Live + Historie**

Die jetzige ComboBox kann durch einen kompakten zyklischen Button oder eine ähnlich platzsparende Bedienung ersetzt werden.

Wichtig ist die eindeutige Erkennbarkeit des aktuellen Modus.

`Live + Historie` soll beide Datenarten in einer gemeinsamen Tabellenansicht darstellen können.

## 11.1 Optische Unterscheidung

Live- und Historieneinträge müssen augenscheinlich unterscheidbar sein.

Mögliche Mittel:

- dezente unterschiedliche Hintergrundtönung;
- dezente Schriftvariation;
- kleines Herkunftskennzeichen.

Dabei haben semantische Warn-/Fehlerfarben Vorrang:

- ERROR/CRITICAL
- WARNING

dürfen durch die Live-/History-Kennzeichnung nicht unlesbar oder überdeckt werden.

Die Lösung soll zurückhaltend, aber unmittelbar erkennbar sein.

---

# 12. Automatisch scrollen

Die derzeitige Checkbox soll als kompakter **checkbarer Button/ToolButton** umgesetzt werden.

Auto-Scroll soll nur dann tatsächlich scrollen, wenn die aktive Sortierung auf einer **Zeitspalte** basiert.

Verhalten:

- zeitlich aufsteigend → neueste Einträge liegen unten → Ansicht folgt unten;
- zeitlich absteigend → neueste Einträge liegen oben → Ansicht folgt oben;
- Sortierung nach einer Nicht-Zeitspalte → Auto-Scroll bleibt zwar als Benutzeroption gesetzt, hat aber temporär keinen Scroll-Effekt.

Das Verhalten muss sowohl für Live als auch `Live + Historie` konsistent sein.

---

# 13. Refresh und Nachladen

`Neu laden` durch eine übliche Desktop-Darstellung ersetzen:

- bevorzugt Refresh-Icon;
- Tooltip `Aktualisieren`.

`Weitere laden` ist zu unbestimmt.

Ersetze die Bezeichnung durch etwas, das die tatsächliche Aktion eindeutig ausdrückt, beispielsweise:

- `Ältere laden`
- `Ältere Einträge laden`

Die Aktion darf nur dort sichtbar/aktiv sein, wo sie fachlich sinnvoll ist.

Wenn es keine weitere Seite gibt, soll sie disabled sein.

---

# 14. Tabellen-Sortierung

Die Tabelle soll sich wie eine übliche Desktop-Tabelle verhalten.

## 14.1 Header-Klick

Klick auf einen Header:

- sortiert nach dieser Spalte;
- erneuter Klick auf denselben Header kehrt die Richtung um.

Immer nur **eine aktive Sortierspalte**.

## 14.2 Sortierindikator

Aktuelle Sortierung sichtbar kennzeichnen:

- `↑` aufsteigend
- `↓` absteigend

Bevorzugt die native Qt-SortIndicator-Funktion verwenden, wenn sie sauber zum vorhandenen Header passt.

## 14.3 Typgerechte Sortierung

Nicht blind nach den angezeigten Strings sortieren.

Insbesondere:

- Datetime → tatsächlicher Zeitwert / Timestamp;
- numerische IDs/Zahlen → numerisch;
- Boolean → logisch;
- Text → textuell.

## 14.4 Zeitformat

Aktuell:

`2026-08-19T18:53:49.070Z`

Gewünschte Darstellung:

`2026-08-19, 18:53:49.070`

Die Anzeigeformatierung darf nicht die interne Sortiersemantik bestimmen.

---

# 15. Verhalten neuer Records bei Sortierung

Neue Live-Records müssen entsprechend der aktiven Sortierung in die Tabelle eingeordnet werden.

Insbesondere bei Zeit:

- Zeit ↑ → neue Records am unteren Ende;
- Zeit ↓ → neue Records am oberen Ende.

Bei anderen Sortierspalten sollen neue Records korrekt entsprechend dem aktuellen Sortierkriterium einsortiert werden.

Kein bloßes Append, das die aktive Sortierung sichtbar zerstört.

---

# 16. Spalten frei konfigurierbar machen

## 16.1 Header-Kontextmenü

Rechtsklick auf einen Tabellenheader öffnet ein Kontextmenü mit allen sinnvoll darstellbaren Recordfeldern.

Beispielsweise:

```text
☑ Zeit
☑ Quelle
☑ Channel
☑ Level
☑ Ereignistyp
☑ Component
☑ Meldung
☐ Session-ID
☐ Activation-ID
☐ Segment-ID
☐ Command-ID
☐ Event-ID
...
```

Jeder Eintrag ist checkbar.

Damit kann der Benutzer Spalten ein- und ausblenden.

Sorge dafür, dass die Tabelle nicht in einen vollständig unbrauchbaren Zustand gebracht werden kann; mindestens eine sinnvolle Spalte muss sichtbar bleiben.

## 16.2 Spalten verschieben

Header sollen per Drag & Drop frei umgeordnet werden können.

## 16.3 Spaltenbreite

Die bereits vorhandene manuelle Breitenänderung muss erhalten bleiben.

---

# 17. Tabellenzustand persistent speichern

Die persönliche Tabellenkonfiguration muss beim nächsten Öffnen wiederhergestellt werden.

Mindestens speichern:

- sichtbare Spalten;
- Spaltenreihenfolge;
- Spaltenbreiten;
- aktive Sortierspalte;
- Sortierrichtung;
- sinnvollerweise Splittergrößen.

Nutze die bereits im Projekt vorhandene Persistenzstrategie, sofern es dafür einen etablierten Mechanismus gibt.

Kein neues großes Konfigurationssystem erfinden.

Bei ungültigen/veralteten gespeicherten Einstellungen muss die UI auf einen sicheren Default zurückfallen.

---

# 18. Freie rechteckige Zellbereichsauswahl

Die Tabelle soll nicht nur ganze Zeilen oder ganze Spalten auswählen können.

Gewünscht ist eine freie zusammenhängende rechteckige Zellselektion ähnlich einer Tabellenkalkulation:

Beispiel:

- Zeilen 5–12;
- nur Spalten `Zeit` bis `Ereignistyp`.

Der ausgewählte Bereich soll sichtbar markiert sein.

Nutze soweit möglich die nativen Qt-Selection-Mechanismen.

---

# 19. Kopieren

## 19.1 Ctrl+C

`Ctrl+C` kopiert den aktuell markierten rechteckigen Zellbereich als **TSV**.

Ziel:

Direktes Einfügen in:

- Excel;
- LibreOffice Calc;
- Google Sheets;
- Texteditor.

Dabei:

- Zeilen bleiben Zeilen;
- Spalten bleiben Spalten;
- keine unnötige JSON-Darstellung;
- vorhandene Anzeigeformatierung sinnvoll übernehmen.

## 19.2 Kontextmenü „Als JSON kopieren“

Tabellen-Kontextmenü ergänzen:

**`Als JSON kopieren`**

Semantik:

Sobald mindestens eine Zelle einer Tabellenzeile markiert ist, gilt diese Zeile für JSON als ausgewählt.

JSON enthält **den vollständigen kanonischen Record dieser Zeile**, nicht nur die sichtbar markierten Zellen.

Sind Zellen aus mehreren Records/Zeilen markiert:

- jeden Record genau einmal aufnehmen;
- Ergebnis als JSON-Array.

Keine Duplikate, wenn mehrere Zellen derselben Zeile ausgewählt sind.

---

# 20. Aktionen / Export

Im neuen kompakten Aktionsbereich geeignete Funktionen anbieten.

Mindestens sinnvoll:

- Auswahl kopieren;
- Als JSON kopieren;
- CSV exportieren;
- JSON exportieren.

Zusätzlich dürfen dieselben Funktionen über:

- Kontextmenü;
- Tastenkürzel

erreichbar sein.

Beim Export muss klar sein, ob:

- aktuelle Auswahl;
- aktuelle gefilterte Ansicht

exportiert wird.

Bevorzugt eine einfache, verständliche Lösung wählen und eindeutig beschriften.

Keine komplexe neue Exportarchitektur bauen.

---

# 21. Verhalten bei großen Datenmengen

Die UI-Verbesserungen dürfen nicht dazu führen, dass für jede kleine Interaktion die gesamte Logging-Datenbank vollständig in den Speicher geladen werden muss.

Insbesondere:

- Pagination/Keyset-Grundprinzip erhalten;
- Live-Verhalten erhalten;
- große Historien weiterhin brauchbar;
- Filter-Facetten effizient bestimmen;
- keine permanente Raw-Payload-Massenbeladung.

Wenn lokale Sortierung über nicht vom Query-Layer unterstützte Felder nicht über den vollständig paginierten Datenbestand korrekt möglich wäre, erweitere die Query-Schicht minimal und sauber, statt nur die bereits geladenen 250 Records irreführend als „gesamte Historie“ zu sortieren.

**Die sichtbare Sortierung muss semantisch ehrlich sein.**

---

# 22. Bestehende funktionale Garantien erhalten

Die bisherigen gate-geprüften Eigenschaften dürfen nicht regressieren:

- History-Pagination ohne Duplikate/Auslassungen;
- Live nach leerem Ausgangsergebnis;
- korrekter Live-Cursor;
- Filterwechsel im Live-Modus;
- keine Raw-Daten in der normalen Tabellenquery, wenn sie dort bisher bewusst nicht geladen werden;
- Query-Layer read-only;
- Logging funktioniert ohne geöffnete UI;
- UI darf Logging-Worker und Hauptanwendung nicht blockieren;
- Warning/Error-Darstellung;
- Redaction/Privacy;
- Replay-Semantik;
- bestehende Korrelation;
- keine neue Runtime-Autorität aus der Diagnose-UI.

---

# 23. Explizite Nicht-Ziele

Nicht Gegenstand dieses Auftrags sind:

- Triggerarchitektur;
- Hotkey-/Wake-Word-Lifecycle;
- Serververhalten;
- Servercode;
- LED-Controller-Architektur;
- Sound-/Feedback-Architektur;
- Audioaufnahme;
- STT-Verarbeitung;
- Textinjektion;
- SQLite-Schema der Observability-Historie, sofern keine zwingende UI-nahe Ergänzung erforderlich ist;
- Ingress-Architektur;
- Worker-/Queue-Architektur;
- Redaction;
- Retention;
- Server-Event-Hooks;
- Event-Normalisierung;
- Logging-Contracts;
- normative Freeze-Dokumente;
- allgemeine Projektbereinigung;
- Refactoring fremder Bereiche;
- bekannte Fehler der noch nicht abgeschlossenen Triggerarchitektur.

Wenn du während der Arbeit einen Fehler außerhalb dieses Scopes findest:

- nicht nebenbei reparieren;
- im Abschlussbericht kurz nennen;
- UI-Auftrag fortsetzen.

---

# 24. Änderungsscope

Primär erwarteter Scope:

- `ui/logs/**`
- unmittelbar dazugehörige OBS-050-UI-Tests
- gegebenenfalls UI-nahe Settings-/View-State-Persistenz
- gegebenenfalls `core/observability/query/**`, wenn für Filterfacetten, vollständige Sortierung oder Export zwingend erforderlich

Änderungen außerhalb dieses Bereichs müssen technisch zwingend begründbar sein.

Keine Cross-Workstream-Dateien anfassen.

Die bereits bewusst unversionierten Prompt-/Pipeline-Dateien unter `ARBEITSDATEIEN/.../30_AUSFUEHRUNG/` nicht aufnehmen oder verändern.

---

# 25. Tests

Nach der Implementierung selbständig testen.

Mindestens gezielte Tests für:

## Filter

- Mehrfachauswahl;
- `Alle`-Semantik;
- deaktivierte unmögliche Werte;
- deaktivierte 0-Treffer-Werte;
- Ereignistyp-Auswahl;
- allgemeine Suche einschließlich Ereignistyp.

## Tabelle

- Zeit ↑ / Zeit ↓;
- numerische vs. textuelle Sortierung;
- Sortierindikator;
- korrektes Einordnen neuer Records;
- Auto-Scroll nur bei Zeit;
- History-Pagination weiterhin korrekt;
- Live weiterhin korrekt;
- Live + Historie.

## Spalten

- Sichtbarkeit;
- Reihenfolge;
- Persistenz;
- Restore nach Neustart;
- robust bei veralteter gespeicherter Konfiguration.

## Auswahl / Copy

- rechteckige Auswahl;
- TSV;
- mehrere Zeilen;
- mehrere Spalten;
- JSON vollständiger Record;
- mehrfach markierte Zellen derselben Zeile erzeugen keinen doppelten Record.

## Details

- Details folgen Auswahl;
- Raw folgt Auswahl;
- fehlendes Raw korrekt dargestellt;
- kein stale Content.

Danach:

- relevante OBS-050-/Logging-UI-Suite;
- komplette Client-Testsuite;
- `git diff --check`.

Bestehende bekannte, nachweislich scope-fremde Testfehler nicht nebenbei reparieren.

---

# 26. Manuelle Sichtprüfung vorbereiten

Nach erfolgreicher Implementierung soll die Anwendung für eine kurze manuelle Sichtprüfung bereit sein.

Stelle sicher, dass der Benutzer anschließend ohne technische Zusatzschritte mindestens prüfen kann:

- neues Layout;
- Filter;
- Live;
- Historie;
- Live + Historie;
- Sortierung;
- Spaltenkonfiguration;
- Persistenz;
- rechteckige Auswahl;
- Copy/Paste nach Excel/Calc;
- JSON-Kopieren;
- Details/Raw;
- Auto-Scroll;
- Export.

---

# 27. Git-Regeln

Kein Commit.

Kein Push.

Kein Merge.

Kein Rebase.

Kein Tag.

Kein PR.

Nichts automatisch stagen.

Der Stand soll nach Abschluss bewusst als Working-Tree-Diff für die anschließende manuelle Sichtprüfung verbleiben.

---

# 28. Keine zusätzliche Dokumentationsrunde

Für diesen UI-Pass keine umfangreichen Dokumentationsartefakte erzeugen.

Insbesondere nicht neu erstellen:

- Implementation Plan;
- Run Report;
- Evidence Matrix;
- Gate Review;
- Traceability Matrix;
- neue ADRs;
- neue Work Packages.

Falls vorhandene Benutzer-/UI-Dokumentation durch die geänderte Bedienung unmittelbar falsch würde, ändere sie **nur dann minimal**, wenn das wirklich erforderlich ist. Ansonsten bleibt Dokumentation außerhalb dieses UI-Passes.

---

# 29. Abschlussbericht

Nach vollständiger Umsetzung nur einen kompakten Abschlussbericht liefern:

1. welche UI-Bereiche geändert wurden;
2. welche funktionalen Punkte umgesetzt wurden;
3. welche Dateien geändert wurden;
4. welche Tests ausgeführt wurden und Ergebnis;
5. verbleibende kleine UI-Punkte, falls vorhanden;
6. gefundene scope-fremde Probleme, ohne sie zu beheben;
7. `git status --short`;
8. Bestätigung: kein Commit/Push.

Keinen neuen Plan für eine nächste Runde erzeugen.

Abschlussstatus bei erfolgreicher Umsetzung:

**LOGGING UI POLISH IMPLEMENTED – READY FOR MANUAL VISUAL REVIEW**