# OBS-060 – DIFF_SUMMARY

Run: `RUN-OBS-060-01_2026-08-18`
Ausgangscommit: `7fc6ca6`
**Kein Commit in diesem Lauf.**

---

## 1. Der vollständige Diff

```text
$ git diff --stat
 app.py                              | 11 +++-
 core/audio_capture.py               |  8 ++-
 core/observability/ingress.py       | 10 ++++
 core/observability/manager.py       | 59 +++++++++++++++++++---
 core/observability/query/local.py   |  7 ++-
 core/observability/worker.py        | 38 ++++++++++++++
 (dazu zwei vorbestehende, laufsfremde Dateien – siehe Abschnitt 4)

$ git diff --check
(leer, exit 0)
```

Neu und noch unversioniert:

```text
?? tests/test_obs060_v1_hardening.py
?? ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-060/
```

**Sechs Produktdateien, +131/−13.** Keine davon liegt außerhalb der
Logging-Domäne oder ihrer Kompositionswurzel. Kein Cross-Workstream-Diff.

## 2. Änderung für Änderung

### `core/observability/worker.py` (+38)

Zwei Eingriffe.

**a) `_resume_store_if_due()`, neu, gerufen als erster Schritt von
`_iteration()`** — Befund **B-1**. Ist der Store ausgesetzt und die Pause
abgelaufen, läuft der von `ARCH §8.3` verlangte leere Testschreibvorgang aus der
Schleife heraus statt nur aus einem ankommenden Batch. Gelingt er, geht der Weg
durch das **bestehende** `_on_store_write_success()`; scheitert er, verlängert
sich die Aussetzung um ein Intervall.

Warum das nötig war: die Aussetzung wird zusammen mit `FAILED_STORE` gesetzt, und
ab da lehnt der Ingress jeden Record ab (`health.is_failed()`). Ohne Batch kein
`_write_with_policy`, ohne `_write_with_policy` keine Probe — die als
„automatisch" zugesagte Erholung (`CONTRACTS §11.2`) war unerreichbar.

**b) Reset von `_consecutive_loop_failures` vor der Schleife** — OBS-030
Gate-Beobachtung **N-2**. `ARCH §8.3` zählt aufeinanderfolgende Fehler **der
Schleife**; die beiden Startupguards davor sind keine Schleifendurchläufe und
dürfen ihr Budget nicht anknabbern.

Kein neuer Zähler, kein neuer Health-Zustand, kein neues Konfigfeld, kein
zweiter Erholungspfad.

### `core/observability/manager.py` (+51/−8)

Drei zusammenhängende Eingriffe an `_on_config_applied`, alle aus den
OBS-050-Gate-Beobachtungen **N-1** und **N-2**.

- **Drei eigene Guards statt eines gemeinsamen.** Vorher brach ein werfendes
  `_build_sink` (die P-8-Pfadprüfung) den ganzen Block ab, und eine im selben
  Apply mitgeschickte `enabled`-Änderung fiel still aus — eine Einstellung, die
  nichts tut und nichts sagt.
- **Ein neuer Sink nur bei geänderter Sinkkonfiguration** (`_sink_signature`,
  aus `file_sink_enabled` und `file_sink_dir`). Vorher wurde bei **jedem** Apply
  ein neuer `JsonlSink` gebaut, die offene Datei geschlossen und eine neue
  geöffnet.
- **`sink` wird weiterhin bei jedem Apply mitgegeben**, nur eben dieselbe
  Instanz, wenn sich nichts geändert hat. Der Worker vergleicht nach Identität
  (`new_sink is not old_sink`), also findet keine Rotation statt — und der
  bestehende, gate-geprüfte Test
  `test_worker_receives_retention_entry_limit_and_sink` bleibt gültig. Der erste
  Zuschnitt ließ den Schlüssel weg und machte diesen Test rot; statt den Test
  anzupassen wurde die Korrektur geändert (siehe `V1_REGRESSION.md` Abschnitt 3).

### `core/observability/ingress.py` (+10)

Befund **B-2**: `self.health.record_malformed()` auf dem Pfad, auf dem
`from_client_event` `None` liefert. `CONTRACTS §3` legt diese Zählpflicht
wörtlich dem **Aufrufer** auf. Der Serverpfad bleibt bewusst unverändert, weil
`None` dort auch „bildet auf keinen Record ab" heißen kann.

Zehn Zeilen, davon neun Kommentar mit Normzitat und der Begründung, warum der
Serverpfad ausgenommen ist.

### `core/observability/query/local.py` (+6/−1)

OBS-050 Gate-Beobachtung **N-4**: `complete=False` bedeutet nach `CONTRACTS §8`
„der Provider hat abgeschnitten". Das tut nur die `MAX_LIMIT`-Klemme. Ein
Aufrufer mit `limit=0` bekommt die Standardseitengröße, bei der nichts
abgeschnitten wird — die Seite als unvollständig zu melden erzählte der
Statuszeile von einer Kürzung, die nie stattgefunden hat.

### `app.py` (+9/−2)

OBS-030 Gate-Beobachtung **N-3**: `observability.start()` und `setup_logging(...)`
liegen jetzt **innerhalb** des `try`, dessen `finally` `observability.stop(2.0)`
ruft. `ARCH §6.2` verlangt das `try/finally` „um den GESAMTEN Ablauf". Nur der
Konstruktor bleibt außerhalb — vor seiner Rückkehr gibt es keinen Manager, den
man stoppen könnte.

Vorher konnte ein Fehler in `setup_logging` den bereits gestarteten Worker
ungeflusht zurücklassen.

### `core/audio_capture.py` (+7/−1)

**Nur Kommentar, kein Code.** OBS-040 Gate-Beobachtung **N-4**: der Kommentar an
`client.audio.stream_stopped` sprach von „die Summen einer Session". Die
Hot-Path-Zähler werden nie zurückgesetzt (ein Reset wäre ein zweiter Schreiber,
und `ARCH §8.6` erlaubt am Hot Path nur das Erhöhen einfacher `int`-Attribute),
es sind also die laufenden Summen der `AudioCapture`-**Instanz**. Der Kommentar
sagt das jetzt.

## 3. Was ausdrücklich **nicht** geändert wurde

- **`00_NORMATIV/`** – byte-identisch zu `7fc6ca6`. Kein Freeze-Dokument, kein
  Entscheidungsregister, keine `DECISION REQUIRED`-Eintragung.
- **`20_PLANUNG/`** – unverändert. Auch die als sachlich unzutreffend erkannte
  Begründungsspalte der Mutationstabelle (O-2) bleibt stehen; ihre
  Richtigstellung ist eine planerische Entscheidung.
- **Kein bestehender Test.** Die einzige Testdatei dieses Laufs ist die neue
  `tests/test_obs060_v1_hardening.py`.
- **Keine Signatur** einer eingefrorenen Funktion, kein neuer Zähler, kein neuer
  Recordtyp, kein neues Konfigfeld, kein neuer Health-Zustand.
- **`voice-stt-client.spec`** und `scripts/pyinstaller_runtime_platform.py` –
  unverändert, geprüft in `probe_obs060_packaging.py` P-4.
- **Server- und LED-Workspace** – nicht berührt.

## 4. Zwei laufsfremde Dateien im Arbeitsbaum

`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/20_PLANUNG/planung_migration/15_OFFENE_FUNDE_UND_AENDERUNGSLOG.md`
(+9) und `…/16_TRACEABILITY_MATRIX.md` (1 Zeile) lagen **schon vor Beginn dieses
Laufs** uncommittet im Baum; inhaltlich sind es reine Markdown-Formatierungen.
Sie gehören zum Triggerarchitektur-Workstream und wurden weder angefasst noch
zurückgenommen. Sie gehören **nicht** in einen Logging-Commit (siehe
`V1_OPEN_POINTS.md` O-3).

## 5. Eine Anmerkung zu Zeilenenden

Die Quelldateien dieses Repositoriums benutzen LF. Der Mutationschecklauf
schreibt Dateien vorübergehend um; sein erster Zuschnitt hätte sie dabei nach
CRLF konvertiert. Das Skript arbeitet deshalb jetzt byte-genau: es merkt sich
die Zeilenendekonvention jeder Datei, schreibt sie so zurück und **belegt** die
Wiederherstellung per SHA-256. Der letzte Lauf meldet für alle sechs berührten
Dateien `restored byte-identical`. Zwei Dateien, die ein abgebrochener früherer
Laufversuch auf CRLF umgestellt hatte, wurden auf LF zurückgeführt; `git diff`
weist für sie nur die fachlichen Zeilen aus.
