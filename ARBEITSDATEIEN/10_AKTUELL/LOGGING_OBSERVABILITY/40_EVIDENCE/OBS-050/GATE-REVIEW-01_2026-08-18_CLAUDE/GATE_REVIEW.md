# OBS-050 – Gate Review (unabhängig, frische Session)

Datum: 2026-08-18
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-050_GATE_REVIEW.md`
Geprüfter Run: `RUN-OBS-050-01_2026-08-17`
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Branch: `feat/einheitliche-triggerarchitektur`, HEAD bei Reviewbeginn `91a7b7f`
Interpreter: Python 3.12.10, PySide6 offscreen (`QT_QPA_PLATFORM=offscreen`)

## Ergebnis

**OBS-050 GATE FAIL**

Geprüft wurde der tatsächliche Repositoryzustand — Produktcode, `git diff`/
`git status`/`git diff --check`, eigenständige Testläufe mit beiden Runnern,
ein Vergleichslauf gegen einen frisch aus `91a7b7f` ausgepackten Baum, das
Diagnoseskript des Runs und **zwei eigene Laufzeitproben gegen den echten
Stack** (echter `SQLiteLogStore`, echter `LocalLogProvider`, echter
`LogQueryService`, echtes Qt-`LogPage`) — nicht die Abschlussberichte.

Der **Query-Layer** ist belastbar: kurzlebige Leseverbindungen mit
`PRAGMA query_only = ON`, Keyset-Pagination über `logs.id`, `raw_json` nicht
in der Liste, ausschließlich Platzhalterbindung, LIKE-Escaping, die Datei wird
vom Leser nie angelegt, keine Verbindung bleibt offen, `query()` wirft nie.
Auch **Settings, Apply-Kette, Ownership-Trennung, Löschfunktion am Store,
Managerlebensdauer, Importrichtung und „Logging läuft ohne UI"** sind
nachvollzogen und in Ordnung.

Das ausdrückliche Gate-Kriterium **„Filter/Cursor/Sortierung verhalten sich
deterministisch"** ist jedoch **nicht erfüllt**. Nicht im Provider — dort
stimmt es —, sondern in der Ansicht: `LogPage` verarbeitet die vom Provider
korrekt gelieferten Seiten in zwei Fällen falsch. Beide Fälle sind mit dem
echten Stack reproduziert und nicht theoretisch.

---

## 1. Blockierende Befunde

### B-1 „Weitere laden" erzeugt eine nicht monotone Anzeigereihenfolge

**Datei:** `ui/logs/log_page.py:301-317` (`_on_page_ready`, Historiezweig),
zusammen mit `ui/logs/log_page.py:254-269` (`load_more`) und
`ui/logs/log_page.py:397-406` (`_on_scrolled`, automatisches Nachladen).

**Norm:** `LOGGING_CONTRACTS_FREEZE_V1.md §9.3` („Pagination: Keyset über
`id`, Seitengröße 200, ‚Weitere laden‘ **und** automatisches Nachladen am
Listenende") und das Gate-Kriterium „Filter/Cursor/Sortierung verhalten sich
deterministisch". Zusätzlich der selbst formulierte Anspruch des Moduls:
*„a log is read top-down, so the page is reversed into chronological order"*
(`log_page.py:303-304`).

**Befund:** Jede Historieseite kommt absteigend (`newest_first=True`) und wird
mit `tuple(reversed(records))` in aufsteigende Reihenfolge gedreht. Die erste
Seite wird mit `set_records` gesetzt, **jede Folgeseite mit `append_page`
unten angehängt**. Eine Folgeseite enthält aber ausschließlich **ältere**
Zeilen (`id < :after_id`). Das Ergebnis ist eine Tabelle, deren Zeitspalte in
der Mitte rückwärts springt: innerhalb eines Blocks aufsteigend, zwischen den
Blöcken absteigend.

**Nachweis (eigene Laufzeitprobe, echter Store + echter Provider + echtes
`LogPage`, `gate_probe_obs050_ordering.py`, Fall A, 12 Zeilen, Seitengröße 5):**

```text
A1 first page (top->bottom): ['r0007', 'r0008', 'r0009', 'r0010', 'r0011']
A2 after 'Weitere laden'  : ['r0007', 'r0008', 'r0009', 'r0010', 'r0011',
                             'r0002', 'r0003', 'r0004', 'r0005', 'r0006']
A  chronologically monotone after load_more: False
```

Derselbe Pfad läuft beim automatischen Nachladen am Listenende
(`_on_scrolled` → `load_more`), also auch ohne jeden Knopfdruck.

**Minimale erforderliche Korrektur** (eine von beiden, nicht beide):

1. Die Umkehrung je Seite entfällt; die Tabelle zeigt durchgehend absteigend
   (neueste oben). Das passt ohne weitere Änderung zum bestehenden
   Nachladen-am-Listenende, weil „unten" dann „älter" bedeutet. Oder
2. die umgekehrte Folgeseite wird **oben eingefügt** statt unten angehängt;
   dann muss `_on_scrolled` das Nachladen am **oberen** Rand auslösen.

Dazu je ein Test, der die Reihenfolge **über zwei Seiten hinweg** prüft
(heute prüft `test_load_more_pages_backwards_with_the_cursor` nur Zeilenzahl
und dass ein Cursor mitging).

---

### B-2 Live-Modus auf einer zunächst leeren Ergebnismenge: verkehrte Reihenfolge und Duplikate

**Datei:** `ui/logs/log_page.py:294-310` (`_on_page_ready`, Verzweigung
`if self._mode == MODE_LIVE and self._live_cursor is not None`), zusammen mit
`ui/logs/log_page.py:271-284` (`_tail`) und `ui/logs/log_page.py:224-252`
(`reload`).

**Norm:** `LOGGING_CONTRACTS_FREEZE_V1.md §9.2` (Live als tailende Abfrage
`WHERE id > :last ORDER BY id LIMIT 500`), `LOGGING_DECISIONS_FREEZE_V1.md`
`FD-S1`, und das Gate-Kriterium „Filter/Cursor/Sortierung verhalten sich
deterministisch".

**Befund:** Die Ansicht entscheidet **nicht anhand der abgeschickten Anfrage**,
ob eine Antwort eine aufsteigende Tail-Antwort ist, sondern anhand des
Zustands `self._live_cursor is not None`. Liefert die Startabfrage des
Live-Modus **keine** Zeile — leerer Store, oder ein Filter, auf den gerade
nichts passt —, bleibt `_live_cursor` `None`. Der erste Tail (`newest_first
= False`, `cursor=None`) liefert dann aufsteigende Zeilen, wird aber im
absteigenden Zweig verarbeitet:

* die Zeilen werden mit `reversed(...)` **umgedreht** angezeigt (neueste oben,
  entgegen der Live-Konvention dieses Widgets samt `scrollToBottom`), und
* `_live_cursor` wird aus `records[0]` gesetzt — das ist in einer aufsteigenden
  Liste die **älteste** Zeile. Der nächste Tail fragt `id > <älteste>` und
  liefert dieselben Zeilen erneut, die dann **angehängt** werden.

**Nachweis (dieselbe Probe, Fall B, leerer Store, danach fünf Records):**

```text
B0 rows after switching to live on an empty store: 0
B1 after first tail : ['r0004','r0003','r0002','r0001','r0000',
                       'r0001','r0002','r0003','r0004']
B2 after second tail: ['r0004','r0003','r0002','r0001','r0000',
                       'r0001','r0002','r0003','r0004']
B  ascending: False   duplicates present: True
```

**Abgrenzung, damit der Befund nicht größer wirkt als er ist:** Der
Normalfall — Live-Modus auf einer nicht leeren Ergebnismenge — ist korrekt.
Eigene Gegenprobe (`gate_probe_obs050_live_happy_path.py`):

```text
C1 after switching to live (non-empty): ['r0000','r0001','r0002']
C2 after tail                         : ['r0000','r0001','r0002','r0007','r0008']
C  ascending=True duplicates=False
```

Der Fehlerfall ist trotzdem alltäglich erreichbar: frische Installation,
Live-Modus mit einem Filter, auf den noch nichts passt, und jeder
Filterwechsel im Live-Modus (er ruft `reload()` und setzt `_live_cursor`
zurück).

**Minimale erforderliche Korrektur:** Die Richtung einer Antwort aus der
**Anfrage** ableiten statt aus `_live_cursor` — zum Beispiel, indem sich
`LogPage` zur reservierten `request_id` merkt, ob es eine Seed- oder eine
Tail-Abfrage war —, und `_live_cursor` in beiden Fällen aus der **jüngsten**
gelieferten Zeile setzen. Dazu ein Test „Live-Modus auf leerem Store".

---

## 2. Nicht blockierende Beobachtungen

| # | Beobachtung | Ort |
|---|---|---|
| W-1 | **Testlücke, die B-1 und B-2 überleben ließ.** Kein Test prüft die Anzeigereihenfolge über zwei Seiten hinweg, und kein Test startet den Live-Modus auf einer leeren Ergebnismenge. `test_load_more_pages_backwards_with_the_cursor` prüft `rowCount()` und die Cursorübergabe, nicht die Ordnung. | `tests/test_obs050_ui.py:410-427` |
| W-2 | **Evidenzformulierung.** `UI_ACCEPTANCE.md` A-11 („Historie lädt die neueste Seite zuerst, **chronologisch dargestellt**") gilt nur für die erste Seite; zusammen mit A-12 hält die Aussage nicht. Mit der B-1-Korrektur ist die Zeile neu zu formulieren. | `40_EVIDENCE/OBS-050/RUN-01_2026-08-17/UI_ACCEPTANCE.md` |
| N-1 | `_on_config_applied` baut bei **jedem** Apply einen neuen `JsonlSink`, auch wenn sich die Sink-Konfiguration nicht geändert hat; der alte wird dadurch jedes Mal geschlossen und ein neuer geöffnet. Funktional korrekt, aber vermeidbar. | `core/observability/manager.py` (`_on_config_applied`, `_build_sink`) |
| N-2 | Wirft `_build_sink` (P-8-Pfadprüfung), bricht `_on_config_applied` vor `_follow_enabled_state` ab; eine gleichzeitige `enabled`-Änderung fiele still aus. Über den Dialog nicht erreichbar, weil `build_candidate` vorher `validate()` ruft. | `core/observability/manager.py` |
| N-3 | Schlägt `apply_runtime_config` **nach** dem Observability-Apply fehl (`reconfigure`-Fehler), stellt `_restore_runtime_config` die alte Konfiguration wieder her, **nicht** aber den alten Observability-Zustand. `§10.4` verlangt das nicht; für OBS-060 vormerken. | `core/controller.py:1400-1440` |
| N-4 | `LocalLogProvider.query` meldet für `limit <= 0` `complete=False`, obwohl nichts abgeschnitten wurde (Standardgröße greift). Kosmetisch. | `core/observability/query/local.py:199-201` |
| N-5 | `LogTableModel.max_rows = 5000` schneidet auch in der Historie die ältesten Zeilen ab. O-04-konform und gewollt, aber in der Statuszeile nicht sichtbar. | `ui/logs/log_table_model.py` |
| N-6 | Die `.gitignore`-Negation `!ui/logs/` ist korrekt und notwendig; `__pycache__` bleibt weiterhin ignoriert (mit `git check-ignore -v` verifiziert). Sie bedeutet aber, dass künftige *Laufzeit*-Artefakte unter `ui/logs/` versioniert würden. | `.gitignore:23-27` |
| N-7 | In `LOGGING_V1_CHECKLISTE.md` steht „OBS-010 – Implementierung" unangehakt, während „OBS-010 – Gate Review" angehakt ist. **Vorbestehend**, nicht aus diesem Run, und nach der Regel „bestehende frühere Häkchen nicht verändern" hier nicht angefasst. | `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` |

---

## 3. Was belastbar geprüft und in Ordnung ist

### 3.1 Repository- und Scopezustand

```text
HEAD bei Reviewbeginn und -ende:  91a7b7f  (kein Commit erstellt)
git diff --check                  leer
git diff --stat                   13 Dateien, +669/-30
00_NORMATIV/  vs 91a7b7f          byte-identisch (git diff --stat leer)
20_PLANUNG/   vs 91a7b7f          byte-identisch
core/settings_metadata.py         byte-identisch
Cross-Workstream-Diff             keiner (kein Server-/LED-Workspace berührt)
kein bestehender Test geändert    bestätigt (git status zeigt keine geänderte Testdatei)
```

Die geänderten Bestandsdateien sind ausnahmslos additiv: jeder neue Parameter
hat einen Default (`observability_manager=None`, `on_show_logs=None`), und
`core/settings_metadata.py` bleibt unberührt, weil die neun Definitionen
bewusst in `core/logging_settings_metadata.py` liegen (`CONTRACTS §12.7`,
`ARCH §12`). Das in `ARCH §5.1` ausgeschlossene Modul
`ui/settings/logging_settings.py` existiert nicht.

### 3.2 Eigenständige Testläufe

```text
$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q -k obs050
170 passed, 959 deselected, 316 subtests passed                     (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -p "test_obs050_*.py"
Ran 170 tests ... OK                                                (exit 0)

$ QT_QPA_PLATFORM=offscreen python -m pytest tests -q
1 failed, 1128 passed, 856 subtests passed
```

Vorbestandsnachweis unabhängig wiederholt: `git archive 91a7b7f` in ein
separates Verzeichnis ausgepackt und dort unverändert getestet →
`1 failed, 958 passed, 531 subtests passed`, **derselbe** Fehlschlag
(`tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'`, außerhalb des Diffs).
Differenz exakt **170** Tests — die neuen OBS-050-Tests. Keine Regression.

Das Diagnoseskript des Runs wurde unabhängig erneut ausgeführt:
**12/12 PASS, exit 0.**

### 3.3 Besondere Gate-Kriterien

| Kriterium | Ergebnis | Nachweis dieses Reviews |
|---|---|---|
| UI greift ausschließlich über die Query-Schicht zu | **erfüllt** | `grep` über alle sechs `ui/logs/`-Module: kein `sqlite3`, kein `observability.storage`, kein `ingress`/`worker`/`manager`; einzige Coreimporte sind `core.observability.query.base`. Die beiden Nicht-Query-Zugriffe (`manager.clear_history`, `manager.health_snapshot`) sind normativ gefordert (`FD-S4`/`§5.8`, `§11.2`). |
| kein Memory-Ringbuffer | **erfüllt** | Live-Quelle ist ausschließlich die tailende Store-Abfrage; `LogTableModel` ist das begrenzte Anzeigemodell, kein Puffer zwischen Ingress und Ansicht. `live_buffer_size` existiert nirgends. |
| Live-Ansicht tailt den lokalen Store | **erfüllt** (Bauform), siehe B-2 für den Fehlerfall | `QTimer` 250 ms → `_tail` → dieselbe Providerschnittstelle, `newest_first=False`, `LIMIT 500`, kein Signal je Record. Probe C oben. |
| Filter/Cursor/Sortierung deterministisch | **NICHT erfüllt** | B-1 und B-2. Der **Provider** ist deterministisch (eigene Prüfung + `QUERY_CASES.md` Q-30…Q-37 nachvollzogen); die **Ansicht** ist es nicht. |
| UI ist kein Infrastruktur-/Runtime-Owner | **erfüllt** | `DesktopApplication` erhält den Manager, stoppt ihn nie (`shutdown()` ruft nur `log_window.shutdown()`); die Managerlebensdauer bleibt im `try/finally` von `app.py::main()` (`ARCH §6.2(b)`). `apply_config` liefert nichts zurück und wirft nicht. |
| Logging funktioniert ohne geöffnete UI | **erfüllt** | Manager, Worker und Store hängen an `app.py::main()`, nicht an der Ansicht; Probe P-7 unabhängig wiederholt (drei Records ohne Fenster geschrieben, von einem später geöffneten Fenster gezeigt). |
| Ownership-Domänen der Settings nicht vermischt | **erfüllt** | Ingress: `enabled`, `level`, `store_raw_payload`, `store_transcription_content`. Kompositionswurzel: Handler-Level (`ARCH §8.7`). Worker (auf seinem eigenen Thread, `request_settings` → `_apply_pending_settings` als erste Anweisung von `_iteration`): Retention, Anzahlgrenze, Datei-Sink. `store_enabled`/`db_path` werden zur Laufzeit ausdrücklich nicht angewandt (`APP_RESTART`). |
| keine Remote-History/Admin-Funktionen vorgezogen | **erfüllt** | `grep -niE "admin\|remote\|http\|capabilit"` über die neuen Module: einziger Treffer ist ein erklärender Kommentar in `service.py`. Kein `query/server_history.py`, kein `ProviderCapabilities`, kein Export. |
| bestehende UI-/Settings-Funktionen regressieren nicht | **erfüllt** | Volle Suite gegen Baseline: identischer Fehlschlagsatz, +170 Tests. `_editor_value` wurde nur um den neuen Editornamen `optional_path` erweitert, `SETTING_DEFINITIONS` in `core/settings_metadata.py` ist unverändert. |

### 3.4 Query-Layer im Einzelnen

Nachvollzogen an `core/observability/query/local.py`:

* `_connect` setzt `busy_timeout` und `PRAGMA query_only = ON`, **nie**
  `mode=ro` (`CONTRACTS §5.4`, `W-13`); jede Verbindung wird in `finally`
  geschlossen.
* Die Datei wird vom Leser nie angelegt: `self._db_path.exists()` wird vor
  `sqlite3.connect` geprüft, ein fehlender Store ist `UNAVAILABLE`, kein
  Fehler (O-14).
* Keyset über `logs.id` mit `LIMIT :limit + 1`; `next_cursor` nur, wenn die
  Zusatzzeile existiert — damit ohne `COUNT` (`§8.1`).
* `_LIST_COLUMNS` enthält `raw_json` nicht; `fetch_raw` lädt es einzeln über
  `record_id` (`§5.7`).
* Jeder Filterwert wird als Platzhalter gebunden; das einzige formatierte
  SQL-Fragment ist die Spaltenliste und die Platzhalteranzahl. LIKE-Wildcards
  in Freitext und Typpräfix werden mit `ESCAPE '\'` neutralisiert — über den
  Vertrag hinaus, aber in seinem Sinn.
* `query()` wirft auf keinem Pfad; `status()` ist gecacht und macht kein I/O.

`LogQueryService` ist eine Registry mit Lock, erhält die Registrierungs-
reihenfolge, macht einen unbekannten `provider_id` zu einem `UNAVAILABLE`-
Zustand und fängt einen werfenden Fremdprovider ab (O-05).

---

## 4. Fazit und nächster zulässiger Schritt

**`OBS-050 GATE FAIL`.** Kein Commit erstellt (Vorgabe des Review-Prompts:
Commit nur bei `PASS`). HEAD steht unverändert auf `91a7b7f`.

Der Umfang der Korrektur ist klein und liegt vollständig in **einer** Datei
(`ui/logs/log_page.py`) plus zwei Tests in `tests/test_obs050_ui.py`. Weder
der Query-Layer noch die Settings, die Apply-Kette, der Manager oder der
Worker sind betroffen; an ihnen ist nichts zu ändern.

Nächster zulässiger Schritt: **OBS-050 Korrekturlauf** für B-1 und B-2
(einschließlich W-1 und W-2), danach ein **erneuter unabhängiger Gate-Review
in frischer Session**. Ein Korrekturlauf vergibt sein eigenes Gate nicht.
**OBS-060 darf nicht beginnen.**

---

## 5. Artefakte dieses Reviews

| Datei | Inhalt |
|---|---|
| `gate_probe_obs050_ordering.py` | Fälle A und B gegen echten Store, echten Provider, echten Service und echtes `LogPage` (offscreen). Exit 1, solange B-1/B-2 offen sind. |
| `gate_probe_obs050_live_happy_path.py` | Fall C: Live-Modus auf nicht leerer Ergebnismenge — Gegenprobe, die den Umfang von B-2 eingrenzt. |
