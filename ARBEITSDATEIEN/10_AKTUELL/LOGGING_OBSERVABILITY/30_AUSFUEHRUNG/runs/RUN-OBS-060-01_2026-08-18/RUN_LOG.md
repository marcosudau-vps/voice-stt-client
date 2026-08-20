# RUN_LOG – RUN-OBS-060-01_2026-08-18

Work Package: **OBS-060 – V1 Hardening, Evidence & Baseline**
Auftrag: `30_AUSFUEHRUNG/Prompts/OBS-060_IMPLEMENTIERUNGSAUFTRAG.md`
Ausgangscommit: `7fc6ca6`
Kein Commit, kein Push.

---

## 1. Ausgangszustand, selbst geprüft

Der Auftrag nennt als Session-Root `P:\GithubRepos\marcosudau-vps`. Dort liegt
**kein** Git-Repository; die Repositories liegen eine Ebene tiefer. Maßgeblich
für diesen Lauf ist
`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`.

```text
$ git branch --show-current
feat/einheitliche-triggerarchitektur

$ git log --oneline -5
7fc6ca6 feat(observability): complete OBS-050 local log view
91a7b7f feat(observability): complete OBS-040 observation hooks
cb0b81f feat(observability): complete OBS-030 persistence and worker
b363346 feat(observability): complete OBS-010 and OBS-020 foundation
f3908cf chore: establish OBS-010 project baseline and work archive
```

OBS-050 ist damit als gate-geprüfter Endstand committet — die Voraussetzung des
Auftrags ist erfüllt. `CURRENT_STATE.md` weist `OBS-050 GATE PASS – OBS-060 MAY
PROCEED` aus (Re-Review vom 2026-08-18).

Der Arbeitsbaum trug **vor** Beginn zwei uncommittete Dateien aus dem
Triggerarchitektur-Workstream (reine Markdown-Formatierungen) und die acht
bewusst unversionierten Prompt-/Pipeline-Einträge. Beides blieb unberührt.

## 2. Verlauf

### 2.1 Pflichtlektüre

`ARBEITSDATEIEN/README.md`, `AGENTS.md`, `00_STEUERUNG/CURRENT_STATE.md`,
`MASTERPLAN.md`, `ARBEITSPROZESS.md`, die Themen-`AGENTS.md` und `README.md`,
`20_PLANUNG/LOGGING_GESAMTPLAN/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md` §13,
`01_WORKPACKAGE_INDEX.md`, `WP-OBS-060_V1_HARDENING_EVIDENCE_BASELINE.md`, die
drei Freeze-Dokumente unter `00_NORMATIV/` sowie die
Gate-Review-Dokumente von OBS-030, OBS-040 und OBS-050 (für die dort für
OBS-060 vorgemerkten Beobachtungen).

### 2.2 Ein Blocker der Testumgebung, zuerst

Der erste Versuch, die volle Suite zu fahren, hing. Nach zwölf Minuten stand der
Prozess bei 1,67 s CPU-Zeit. Ein `faulthandler`-Stackdump zeigte die Ursache:

```text
File "…\Lib\platform.py", line 327 in _wmi_query
File "…\site-packages\sounddevice.py", line 75 in <module>
File "…\core\audio_capture.py", line 22 in <module>
File "…\core\controller.py", line 24 in <module>
```

`platform._wmi_query` antwortet auf dieser Maschine nicht, und `sounddevice`
ruft es beim Import. Damit hängt jeder Testlauf, der `core.controller` importiert.

Das ist eine Eigenschaft der Maschine, nicht des Produkts — und das Projekt
kennt sie: `voice-stt-client.spec` installiert für den gefrorenen Build den
Runtime-Hook `scripts/pyinstaller_runtime_platform.py` mit exakt derselben
Begründung. Für die Testläufe wurde deshalb **außerhalb des Projektbaums** ein
`sitecustomize.py` auf den `PYTHONPATH` gelegt, das `_wmi_query` einen `OSError`
werfen lässt (der Fall, den CPython selbst als „WMI nicht verfügbar" abfängt).
**Keine Projektdatei wurde dafür verändert.** Danach: 80,9 s für die volle Suite,
und die Zahlen decken sich mit denen des OBS-050-Gates.

Baseline auf `7fc6ca6`: **1137 passed / 1 failed** (`lefx.interfaces`,
vorbestehend).

### 2.3 Evidence aufgebaut, dabei zwei echte Befunde

Die Probeskripte wurden in dieser Reihenfolge gebaut und gefahren:

1. `probe_obs060_e2e_chain.py` – die ganze Kette. Grün auf Anhieb (24 Prüfungen).
2. `probe_obs060_failure_injection.py` – zehn Fehlerfälle. Erster Lauf:
   **zehn Fehlschläge**. Triage:
   - F-1 und F-5 waren **Fehler der Probe** (zu wenige Batches für die
     Fünferschwelle; `DEBUG`-Records, die schon der Levelfilter abfing).
   - F-7.3/F-7.4 und F-10.2…F-10.5 waren **echt** → Befunde B-2 und B-1.
3. Beide Befunde vor jeder Korrektur reproduziert und als
   `failure_injection_BEFORE_FIX.txt` und `probe_obs060_b1_reproduction.py`
   festgehalten.
4. Korrekturen umgesetzt (siehe `DIFF_SUMMARY.md`), Proben erneut gefahren.
5. `probe_obs060_runtime_isolation.py` – R-1…R-7 als Protokollvergleich.
6. `probe_obs060_performance.py`, `probe_obs060_privacy.py`,
   `probe_obs060_mutation_checks.py`, `probe_obs060_packaging.py`.

### 2.4 Zwei Zwischenfälle, beide behoben und beide erwähnenswert

**Der Mutationschecklauf blieb beim ersten Versuch hängen** — an genau der
Mutation, die er prüft: `put_nowait` → blockierendes `put` lässt den Testlauf
nie enden. Der Lauf wurde nach zehn Minuten abgebrochen und ließ
`core/observability/ingress.py` **mutiert** zurück. Der Zustand wurde sofort
wiederhergestellt und gegen `git diff` verifiziert. Das Skript hat seitdem ein
Zeitbudget je Mutation und wertet ein Timeout ausdrücklich als „rot" — das ist
die richtige Lesart, denn das Symptom eines blockierten Producer-Threads ist
kein fehlschlagendes Assert.

**Das Skript hätte LF-Dateien nach CRLF konvertiert.** `Path.write_text`
übersetzt unter Windows in `os.linesep`. Es arbeitet jetzt byte-genau und
**belegt** die Wiederherstellung per SHA-256. Zwei Dateien, die der abgebrochene
Lauf umgestellt hatte, wurden auf LF zurückgeführt.

### 2.5 Eine Zwischenregression, absichtlich anders gelöst

Der erste Zuschnitt der N-1-Korrektur ließ den `sink`-Schlüssel weg, wenn sich
die Sinkkonfiguration nicht geändert hatte. Damit wurde
`test_worker_receives_retention_entry_limit_and_sink` rot — ein bestehender,
gate-geprüfter Test.

Statt den Test anzupassen wurde die **Korrektur** geändert: der Manager merkt
sich die zuletzt übergebene Sinkinstanz und reicht sie unverändert weiter. Der
Worker vergleicht nach Identität, also findet keine Rotation statt, und der Test
bleibt gültig. Ein bestehender Test wird nicht passend gemacht.

### 2.6 M-6: eine Erwartung, die sich nicht halten ließ

Die Mutation „`WHERE event_id IS NOT NULL` aus dem Index entfernen" machte
keinen Test rot. Eine gezielte Messung zeigt warum: in SQLite sind `NULL`-Werte
in einem UNIQUE-Index immer verschieden, also werden Clientzeilen ohne
`event_id` auch mit einem vollen Index nicht dedupliziert. Die Begründung der
Mutationstabelle trifft nicht zu.

Statt einen künstlich roten Test zu bauen, wurde der Wächter dort angesetzt, wo
die Norm tatsächlich etwas festlegt: `FD-C7` nennt den Index ausdrücklich
**partiell**, `CONTRACTS §5.2` friert die DDL ein. Zwei Tests prüfen jetzt
genau das. Die Frage, ob die Begründungsspalte im Plan richtigzustellen ist,
bleibt als **O-2** offen — planerische Dokumente ändert ein
Implementierungslauf nicht.

## 3. Entscheidungen dieses Laufs

| # | Entscheidung | aufgelöst aus |
|---|---|---|
| 1 | Die Store-Erholung wird aus der Worker-**Schleife** getrieben, nicht aus einem ankommenden Batch | `ARCH §8.3` („danach mit einem leeren Testschreibvorgang prüfen") + `CONTRACTS §11.2` („Recovery automatisch") |
| 2 | Der Erholungspfad bleibt der bestehende `_on_store_write_success()`; kein zweiter Pfad, kein neuer Zähler | `ARCH §7.3` (Zähler eingefroren), `CONTRACTS §11.2` (genau **ein** `logging.recovered`) |
| 3 | `malformed++` nur auf dem **Client**pfad, nicht auf dem Serverpfad | `CONTRACTS §3` („im Zweifel `None`, und der Aufrufer zählt `malformed`") gegen die Serversemantik, wo `None` eine Entscheidung ist |
| 4 | Kein Ersatzrecord für eine verschluckte Normalizer-Ausnahme | bräuchte den Ausnahmetyp und damit eine Signaturänderung an einer eingefrorenen Funktion → **O-1**, Entscheidung ausstehend |
| 5 | Der Wächter für M-6 prüft die eingefrorene DDL, nicht eine Dedupe-Folge | `FD-C7`, `CONTRACTS §5.2`; die Dedupe-Folge existiert nachweislich nicht → **O-2** |
| 6 | `sink` wird bei jedem Apply mitgegeben, nur dieselbe Instanz bei unveränderter Konfiguration | `CONTRACTS §10.3` (IMMEDIATE) und die Regel „kein bestehender Test wird geändert" (`ARCH §12`) |
| 7 | Nur der Manager-Konstruktor bleibt außerhalb des `try` | `ARCH §6.2` („um den GESAMTEN Ablauf") – vor der Rückkehr des Konstruktors gibt es nichts zu stoppen |
| 8 | Die historische Evidence von OBS-040 wird **nicht** korrigiert | der Nachweiswert der Kette hängt daran, dass abgeschlossene Läufe nicht nachträglich umgeschrieben werden → **O-6** |
| 9 | Der Umgebungs-Shim liegt außerhalb des Projektbaums | ein Implementierungslauf entscheidet nicht über die dauerhafte Testinfrastruktur → **O-13** |

**Kein `DECISION REQUIRED` in einem normativen Dokument.** Sämtlicher
Entscheidungsbedarf steht in `V1_OPEN_POINTS.md`. `00_NORMATIV/` ist
byte-identisch zu `7fc6ca6`.

## 4. Tests und Evidence

Zusammengefasst in `40_EVIDENCE/OBS-060/RUN-01_2026-08-18/V1_TEST_RESULTS.md`.
Kurz: 27 neue Tests, volle Suite **1164 passed / 1 vorbestehender Fehlschlag**
(vorher 1137 / 1 — Differenz exakt die 27 neuen), V1-Kette 652 passed,
`git diff --check` leer, alle sieben Probeskripte exit 0.

## 5. Blocker

**Keine.** Die drei Befunde B-1, B-2 und B-3 sind geschlossen und mit
Regressionstests versehen. Die offenen Punkte O-1…O-13 sind in
`V1_OPEN_POINTS.md` einzeln begründet; keiner berührt ein V1-Gate-Kriterium.

Ausdrücklich benannt bleibt: die **manuelle Abnahme M-1…M-11** am realen
Produktionspfad ist nur teilweise erledigt. Neun der elf Punkte sind gegen den
echten Stack automatisiert belegt und M-11 ist protokolliert, aber der Durchlauf
auf einem Installationssystem mit laufendem Server — mit Datum, Serveradresse
und Clientversion — steht aus. Das Work Package erklärt ihn zur Pflicht; dieser
Lauf kann ihn nicht ersetzen und tut auch nicht so.

## 6. Gate-Empfehlung

`OBS-060 IMPLEMENTED – READY FOR V1 GATE`.

**Kein Gate-PASS in diesem Lauf** — ein Implementierungslauf vergibt sein
eigenes Gate nicht.

## 7. Nächster Schritt

Unabhängiger **OBS-060 Logging V1 Final Gate Review** in frischer Session
(`Prompts/OBS-060_V1_GATE_REVIEW.md`). Der lokale Abschlusscommit darf erst
danach und nur bei `PASS` entstehen.
