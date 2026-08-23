# RESULT – RUN-OBS-060-01_2026-08-18

## Ergebnis

**`OBS-060 IMPLEMENTED – READY FOR V1 GATE`**

Kein Gate-PASS in diesem Lauf. Kein Commit, kein Push, kein Merge, kein Rebase,
kein Tag, kein PR.

---

## Was dieser Lauf getan hat

OBS-060 fügt keine Funktionalität hinzu. Er härtet Logging V1 und belegt es —
und dabei sind **drei echte Befunde** aufgefallen, alle innerhalb des
V1-Scopes, alle geschlossen.

### B-1 – Die Store-Erholung nach `ARCH §8.3` war unerreichbar

`ARCH §8.3` setzt einen wiederholt scheiternden Store für 60 s aus und verlangt,
ihn *„danach mit einem leeren Testschreibvorgang"* zu prüfen; `CONTRACTS §11.2`
nennt diese Erholung *„automatisch und still"*.

Die Aussetzung wird zusammen mit `FAILED_STORE` gesetzt — und ab diesem Moment
lehnt der Ingress **jeden** Record ab (`health.is_failed()`). Ohne neuen Record
kein Batch, ohne Batch kein `_write_with_policy`, und genau dort saß die einzige
Prüfung der Pause. Der vorgeschriebene Testschreibvorgang fand nie statt:
`FAILED_STORE` war im laufenden Prozess **endgültig**. Reproduziert mit
`probe_obs060_b1_reproduction.py` — nach drei Sekunden mit längst wieder
gesundem Store: `probe_write calls: 0`, `state: FAILED_STORE`.

Behoben durch einen Schritt am Anfang der Worker-Schleife, der die abgelaufene
Aussetzung selbst prüft. **Kein neuer Zähler, kein neuer Health-Zustand, kein
zweiter Erholungspfad** — `logging.recovered` schreibt weiterhin derselbe Code
wie nach einem geglückten Batch.

### B-2 – Ein `None` des Client-Normalizers wurde nicht gezählt

`CONTRACTS §3` sagt wörtlich: *„Der Normalizer wirft nie. Im Zweifel liefert er
`None`, und der **Aufrufer** zählt `malformed`."* Der Aufrufer tat das nicht.
`from_client_event` hat genau ein `return None`, und es steht in seinem
`except`-Zweig — der Fall war also immer eine verschluckte Ausnahme, und er war
vollständig unsichtbar: kein Zähler, kein Health-Signal, nichts.

Eine Zeile behebt das. Der **Serverpfad** bleibt bewusst ausgenommen, weil `None`
dort auch „bildet auf keinen Record ab" heißen kann — das dort mitzuzählen würde
den Zähler bei jedem nicht abgebildeten Controlframe verfälschen.

### B-3 – Die Mutation M-6 hatte keinen Wächter

Und sie konnte auch keinen der erwarteten Art haben: die Mutationstabelle
begründet sie damit, dass Clientrecords „fälschlich dedupliziert" würden. In
SQLite sind `NULL`-Werte in einem UNIQUE-Index immer verschieden — gemessen,
mit beiden Indexformen, gleiches Ergebnis. Der Wächter sitzt deshalb dort, wo
die Norm wirklich etwas festlegt: `FD-C7` nennt den Index **partiell**,
`CONTRACTS §5.2` friert die DDL ein.

## Der Runtime-Isolationsnachweis, in der verbindlichen Form

Das Work Package verlangt keinen Satz Einzelbehauptungen, sondern einen
**Protokollvergleich** — mit echtem `STTController`, echter `FeedbackEngine`,
echtem `DualSessionCoordinator` und echtem `EventProtocolProcessor`; Doubles nur
für WebSocket und Ausgabegeräte.

Ein vollständiger Diktatzyklus, aufgezeichnet werden Frames samt Längen,
`CommandResult`-Folge, `FeedbackDecision`-Folge, die vollständige Snapshotfolge,
das `FinalProcessingResult`, Injektionen, Textrückrufe, Transportwechsel,
angenommene Eventstream-Events, Resume-Cursor und Cursordatei.

**Alle sechs Störungsläufe liefern das Protokoll des Referenzlaufs, Byte für
Byte** — auch der mit einem Ingress, dessen sämtliche Methoden werfen, und der
mit einem `on_observation`, das bei jedem der drei Aufrufe wirft. Für R-7 stimmt
zusätzlich der Endstand der Cursordatei. Die einzige Normalisierung ist
`updated_at`, der Wanduhrzeitpunkt des Schreibvorgangs; sie ist benannt.

Und R-2 zeigt, dass der Vergleich etwas wert ist: die funktionierende
Observability hat den Zyklus mit sechs Records tatsächlich aufgezeichnet.

## Die acht Mutationschecks

**Alle acht machen einen Test rot.** Vorher laufen alle betroffenen Auswahlen
grün (143 passed), nachher ist jede berührte Datei per SHA-256 als
byte-identisch wiederhergestellt belegt. Bei M-3 (`put_nowait` → blockierendes
`put`) endet der Lauf nicht mehr — das zählt als rot, und das ist die richtige
Lesart: ein blockierter Producer-Thread schlägt nicht fehl, er hängt.

## Übernommene Gate-Beobachtungen

Sechs der für OBS-060 vorgemerkten Punkte sind behoben: OBS-030 N-2 und N-3,
OBS-040 N-4 (Kommentar), OBS-050 N-1, N-2 und N-4. Die übrigen sind in
`V1_OPEN_POINTS.md` einzeln begründet — darunter drei, die ausdrücklich **nicht**
repariert werden, weil sie eingefrorene Verträge erweitern würden oder
historische Evidence umschreiben müssten.

## Zahlen

| | vorher (`7fc6ca6`) | nachher |
|---|---|---|
| volle Suite, `pytest` | 1137 passed / 1 failed | **1164 passed / 1 failed** |
| volle Suite, `unittest` | Ran 1138, 1 error | **Ran 1165, 1 error** |
| V1-Kette OBS-010…060 | – | **652 passed** |
| neue Tests | – | **27**, grün unter beiden Runnern |

Differenz exakt +27. Der eine Fehlschlag ist in beiden Ständen derselbe,
vorbestehende, umgebungsbedingte `ModuleNotFoundError: lefx.interfaces`.
**Kein bestehender Test geändert.** `git diff --check` leer.

Produktseitig: **sechs Dateien, +131/−13**, alle in der Logging-Domäne oder
ihrer Kompositionswurzel. `00_NORMATIV/` byte-identisch. Kein
Cross-Workstream-Diff.

## Ehrlich benannt: was aussteht

Die **manuelle Abnahme M-1…M-11** am realen Produktionspfad ist nur teilweise
erledigt. Neun der elf Punkte sind gegen den echten Stack automatisiert belegt,
M-11 (Dateirechte, `icacls`) ist protokolliert — aber der Durchlauf auf einem
Installationssystem mit laufendem Server, mit Datum, Serveradresse und
Clientversion, steht aus. Das Work Package erklärt ihn zur Pflicht und sagt
ausdrücklich, dass V1 ohne ihn als „teilweise" gilt. Dieser Lauf ersetzt ihn
nicht und behauptet das auch nicht.

Ebenfalls benannt: die Testumgebung dieser Maschine blockiert ohne einen
externen Shim, weil `platform._wmi_query` nicht antwortet. Der ausgelieferte
Client ist nicht betroffen — der gefrorene Build neutralisiert dieselbe Sonde
bereits selbst. Keine Projektdatei wurde dafür angefasst.

## Nächster Schritt

Unabhängiger **OBS-060 Logging V1 Final Gate Review** in frischer Session
(`Prompts/OBS-060_V1_GATE_REVIEW.md`). Der lokale Abschlusscommit darf erst
danach und nur bei `PASS` entstehen.
