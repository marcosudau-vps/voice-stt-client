---
id: EV-OBS-000-03
status: FINAL
authority: evidence
workstream: OBS
run: RUN-OBS-000-01_2026-08-15_CLAUDE
---

# EV-03 – Produktrepo-Baseline und Git-Zustand

**Zweck.** Der Gesamtplan verlangt in OBS-000 ausdrücklich
„Produktrepo-Baseline/Git-Zustand sichern". Diese Datei hält fest, gegen welchen
Produktzustand der Freeze gilt.

**Erhebung:** rein lesend (`git rev-parse`, `git log`, `git status`,
`git diff --stat`). Keine Änderung, kein Commit, kein Stash.

---

## 1. Der Workspace selbst ist kein Git-Repository

```bash
cd "P:/GithubRepos/marcosudau-vps-worktrees/einheitliche-triggerarchitektur-claude"
git rev-parse --show-toplevel
```

```text
fatal: not a git repository (or any of the parent directories): .git
```

`ARBEITSDATEIEN/` unterliegt damit **keiner** Versionskontrolle. Die
Freeze-Artefakte sind nur durch die Prüfsummen in `EV-01` und im
`PAKETMANIFEST.md` gegen unbemerkte Änderung gesichert. Das ist eine benannte
Grenze, keine Beanstandung.

Die drei Produktrepositories sind jeweils eigenständige Git-Arbeitsbäume.

## 2. `voice-stt-client` – das einzige Repository, das V1 anfasst

```text
Branch : feat/einheitliche-triggerarchitektur
HEAD   : 178d32bdf17d4709307e7a2a944888d2cf294e42
Datum  : 2026-08-13 01:49:11 +0200
Betreff: fix(feedback): debug LED and sound feedback
```

**Arbeitsbaum nicht sauber: 22 Einträge.**

```text
 M README.md
 M config.yaml
 M core/config.py
 M core/controller.py
 M core/settings_metadata.py
 M core/stt_session.py
 M docs/decisions/ADR-001_BETRIEBSMODI_HOTKEY_UND_WAKE_WORD.md
 M docs/guides/feedback_konfigurieren.md
 M docs/guides/feedback_system.md
 M server-docs-for-client-development/02-websocket-protokoll.md
 M server-docs-for-client-development/03-server-events-kurzreferenz.md
 M server-docs-for-client-development/04-server-events-katalog-und-chronologie.md
 M server-docs-for-client-development/09-betriebsmodi-und-serverkonfiguration.md
 M server-docs-for-client-development/README.md
 M server-docs-for-client-development/session-wakeword-erweiterung.md
 M tests/test_ap06_followup.py
 M tests/test_config.py
 M tests/test_stt_session.py
 M ui/application.py
 M ui/settings_dialog.py
?? tests/test_trigger_feedback_contract.py
?? tests/test_trigger_lifecycle.py
```

```bash
git diff --stat
```

```text
20 files changed, 1140 insertions(+), 138 deletions(-)
```

### Warum das für OBS-000 wichtig ist

Fünf der geänderten Dateien — `core/controller.py`, `core/stt_session.py`,
`core/config.py`, `core/settings_metadata.py`, `ui/application.py`,
`ui/settings_dialog.py` — sind **exakt die Dateien, die V1 additiv anfassen
wird**, und **exakt die Dateien, auf deren Zeilennummern die Vorarbeit
verweist**.

`EV-02 / C-01` belegt über die Zeilenzahlen, dass die Vorarbeit gegen **diesen**
Arbeitsbaum entstanden ist, also einschließlich der nicht committeten
Änderungen. Die Zeilenverweise sind damit gültig — **aber nur, solange dieser
Arbeitsbaum nicht verändert wird**.

Daraus folgt eine verbindliche Auflage, die im Run Report als **R-3** und im
Work Package OBS-010 als Vorbedingung geführt wird:

```text
Vor Beginn von OBS-010 wird der Zustand des Clients festgeschrieben --
entweder durch einen Commit der 22 offenen Aenderungen oder durch eine
ausdrueckliche Bestaetigung, dass der Arbeitsbaum unveraendert bleibt.
Andernfalls verschieben sich Zeilenverweise und die Hookstellen muessen
erneut lokalisiert werden.

Diese Festschreibung ist KEIN Bestandteil von OBS-000 -- OBS-000 darf nicht
committen -- sondern eine Vorbedingung von OBS-010.
```

**Ausdrücklich nicht betroffen** ist die inhaltliche Gültigkeit des Freezes:
Kein einziger eingefrorener Vertrag hängt an einer Zeilennummer. Zeilenverweise
sind Auffindhilfen, die Verträge stehen für sich.

## 3. `voice-stt-server` – nur lesend untersucht

```text
Branch : feat/einheitliche-triggerarchitektur
HEAD   : 13c162950b944dc715fdd81983a7465f8eb0fd79
Datum  : 2026-08-12 04:10:40 +0000
Betreff: docs(archive): close build deployment action
Arbeitsbaum: 24 Eintraege (15 geaendert, 9 unversioniert)
```

Der Server wird von V1 **nicht** verändert. Er ist ausschließlich Quelle von
Ist-Aussagen (Channels, `event_id`, Cursor, `server_instance_id`,
Admin-Contract). Die eingefrorenen Aussagen über den Server stammen aus der
Vorarbeit und aus `docs/structured-logging.md`; sie wurden in diesem Run nicht
erneut breit geprüft, weil OBS-000 keine neue Analyse eröffnet.

## 4. `led_controller_respeaker-v3` – sauber, unverändert

```text
Branch : feat/einheitliche-triggerarchitektur
HEAD   : aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0
Datum  : 2026-08-10 02:18:14 +0200
Betreff: revert(tests): restore the full assertion on the offered outputs
Arbeitsbaum: sauber
```

Bestätigt Befund LED-1: Der LED-Controller wird für V1 **nicht** angefasst.
LEFX läuft in-process und loggt nach `lefx.*`; eine Normalizer-Regel genügt.

## 5. Einhaltung der harten Verbote aus `PRM-OBS-000-01 §12`

| Verbot | Status |
|---|---|
| keine Produktcodeänderung | eingehalten |
| keine Produkt-Testcodeänderung | eingehalten |
| keine aktive Produktconfig geändert | eingehalten |
| keine Triggerarchitektur repariert | eingehalten |
| keine Logging-Implementierung begonnen | eingehalten |
| kein Commit / Push / Merge / Rebase / Tag / PR | eingehalten |
| `voice-stt-client`, `voice-stt-server`, `led_controller_respeaker-v3` nur lesend | eingehalten |

Sämtliche Schreibvorgänge dieses Runs liegen unterhalb von
`ARBEITSDATEIEN/AP_THEMA_LOGGING/` sowie in `ARBEITSDATEIEN/LOG_VERLAUF.md`.
