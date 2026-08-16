---
id: EV-OBS-000-02
status: FINAL
authority: evidence
workstream: OBS
run: RUN-OBS-000-01_2026-08-15_CLAUDE
---

# EV-02 – Gezielte Codeprüfungen für den Freeze

**Regel für diesen Run.** Keine neue breite Analyse. Geprüft wurde
ausschließlich das, was eine konkrete Freeze-Entscheidung trägt und ohne dessen
Bestätigung die Entscheidung nicht belastbar wäre. Sämtliche Zugriffe waren
**lesend**. Kein Produkt-, Test- oder Configcode wurde verändert.

**Warum diese Prüfungen überhaupt nötig waren.** Die Vorarbeit ist gegen einen
Arbeitsbaum entstanden, der **nicht committet** ist (siehe `EV-03`). Betroffen
sind ausgerechnet die Dateien, die V1 anfasst: `core/controller.py`,
`core/stt_session.py`, `core/config.py`, `core/settings_metadata.py`,
`ui/application.py`, `ui/settings_dialog.py`. Bevor Zeilenverweise eingefroren
werden, mussten sie am tatsächlichen Zustand bestätigt werden.

**Basis aller Prüfungen:**
`voice-stt-client`, Branch `feat/einheitliche-triggerarchitektur`,
HEAD `178d32bdf17d4709307e7a2a944888d2cf294e42`, **mit** den 22 nicht
committeten Änderungen aus `EV-03`.

---

## C-01 – Dateigrößen decken sich mit der Vorarbeit

```bash
wc -l core/controller.py core/stt_session.py core/session_coordinator.py \
      core/event_stream.py core/event_protocol.py core/event_cursor_store.py \
      core/logging_setup.py core/config.py core/settings_metadata.py \
      ui/core_bridge.py ui/application.py ui/settings_dialog.py app.py
```

```text
  2724 core/controller.py
  1446 core/stt_session.py
   517 core/session_coordinator.py
   369 core/event_stream.py
   532 core/event_protocol.py
   194 core/event_cursor_store.py
   119 core/logging_setup.py
  1011 core/config.py
   340 core/settings_metadata.py
   413 ui/core_bridge.py
   730 ui/application.py
   433 ui/settings_dialog.py
   160 app.py
```

`LOGGING_V1_IMPLEMENTATION_PLAN.md §18.1` nennt `controller.py 2724 Z.`,
`stt_session.py 1446 Z.` und `config.py 1011 Z.` — **exakte Übereinstimmung**.

**Ergebnis:** Die Vorarbeit ist gegen genau diesen Arbeitsbaum entstanden. Alle
Zeilenverweise der Vorarbeitsdokumente sind gültig, **solange dieser
Arbeitsbaum nicht verändert wird**. Konsequenz für die Planung: siehe
`RISIKO R-3` im Run Report.

---

## C-02 – Der Beobachterhook liegt richtig und ist frei

```bash
grep -n "_handle_event\|_handle_control\|_handle_state\|on_observation" core/session_coordinator.py
```

```text
226:                on_event=lambda result: self._handle_event(binding, result),
227:                on_control=lambda result: self._handle_control(binding, result),
228:                on_state_change=lambda state: self._handle_state(binding, state),
308:    async def _handle_event(
340:    def _handle_control(
356:    def _handle_state(
```

**Ergebnis:** `_handle_event` (:308) und `_handle_control` (:340) existieren wie
in `LOGGING_CODE_INTEGRATION_AUDIT.md §2.4` beschrieben. Ein Attribut
`on_observation` existiert **noch nicht** — der Beobachterschlitz ist frei und
rein additiv einzuziehen. **Freeze-Entscheidung FD-A3 bestätigt.**

---

## C-03 – Warum `STTController.on_event_stream_event` verboten bleibt

```bash
sed -n '270,290p' core/event_stream.py
```

```python
    async def _dispatch(self, result: EventProtocolResult) -> None:
        self._set_state(result.connection_state)
        if result.kind is EventResultKind.EVENT:
            if result.duplicate:
                await self._call(self._on_control, result)
                return
            try:
                accepted = await self._call(self._on_event, result)
                if accepted is not True:
                    raise EventProcessingRejected(
                        "event processing wasn't explicitly confirmed"
                    )
                self._processor.confirm_event(result)
            except BaseException:
                self._processor.reject_event(result)
                raise
            return

        await self._call(self._on_control, result)
```

**Ergebnis, drei bestätigte Fakten:**

1. Der Rückgabewert von `on_event` entscheidet über `confirm_event`, also über
   den Cursor-Commit. Ein Logger in dieser Kette wäre fachliche
   Runtime-Autorität. **Das Verbot aus Audit §2.4 gilt.**
2. **Duplikate gehen an `on_control`**, nicht an `on_event` (`:273-275`). Der
   Hook im Coordinator sieht sie deshalb nur über `_handle_control`. Bestätigt
   die Hookwahl an **beiden** Methoden.
3. Neu und über die Vorarbeit hinausgehend: `except BaseException: reject_event;
   raise`. Eine Ausnahme, die aus dem Beobachter nach oben durchschlüge, würde
   das Event **aktiv verwerfen** und die Verbindung recyceln. Damit ist
   `except Exception` im Beobachterwrapper **nicht Vorsicht, sondern Pflicht** —
   und `BaseException` darf dort weiterhin nicht gefangen werden, weil
   `asyncio.CancelledError` das Abbrechen des Eventstream-Tasks trägt.
   **Verschärft AR-8 zu einer harten Regel; eingefroren als `FD-A6`.**

---

## C-04 – Der Replay-Kostenfall ist real

```bash
sed -n '68,82p' core/event_cursor_store.py
```

```python
            expected_endpoint, expected_instance, expected_protocol, maximum = binding
            if (
                record.endpoint != expected_endpoint
                or record.server_instance_id != expected_instance
                or record.protocol_version != expected_protocol
            ):
                logger.info("Ignoring event cursor with a different server binding")
                return None
```

**Ergebnis:** Wechselt die `server_instance_id` (Serverneustart), wird der
gespeicherte Cursor still verworfen → `resume_cursor = 0` → voller Replay.
**Persistenz-Dedupe ist Pflicht, nicht Kür. `FD-C7` bestätigt.**

---

## C-05 – Defekt D-1 ist real und schwerer als beschrieben

```bash
grep -n "MappingProxyType\|_freeze_value\|payload=" core/event_protocol.py
```

```text
  9:from types import MappingProxyType
136:def _freeze_value(value: Any) -> Any:
138:        return MappingProxyType({
139:            str(key): _freeze_value(item) for key, item in value.items()
142:        return tuple(_freeze_value(item) for item in value)
144:        return frozenset(_freeze_value(item) for item in value)
148:def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
345:            payload=_freeze_mapping(raw),
…  (acht Aufrufstellen insgesamt)
```

**Ergebnis:** `EventProtocolResult.payload` ist rekursiv eingefroren, und zwar
in **drei** Typen: `MappingProxyType`, `tuple` **und `frozenset`**.

Das adversariale Review (D-1) nennt nur `MappingProxyType` und Tupel. `frozenset`
ist der schwerere Fall: `json.dumps` kennt weder `MappingProxyType` noch
`frozenset`. Mit `default=str` würde ein `frozenset` zu `"frozenset({...})"`
kollabieren — genau der Effekt, der die schlüsselbasierte Redaction aushebelt
(SP-2a).

**Konsequenz, eingefroren als `FD-C11` / Regel `R-11`:** Der `unfreeze()`-Helfer
muss **alle drei** Typen behandeln (`MappingProxyType → dict`, `tuple → list`,
`frozenset → sortierte list`), und ein `default=str`-Rückfall ist nur je
**Blattwert** zulässig, nie auf Container-Ebene.

---

## C-06 – Die Qt-Grenze hält ohne Umbau

```bash
grep -rn "PySide6\|QtCore\|QObject" core/
```

```text
(kein Treffer)
```

**Ergebnis:** `core/` ist vollständig frei von Qt. Invariante O-10/Zielbild §38
ist ohne Umbau haltbar. Ein Contract-Test dieser Art ist in OBS-010 verbindlich.

---

## C-07 – Der Injektionsweg bricht keinen bestehenden Test

```bash
grep -n "ControllerFactory\|controller_factory" ui/core_bridge.py
```

```text
20:ControllerFactory = Callable[[AppConfig], STTController]
40:        controller_factory: Optional[ControllerFactory] = None,
45:        self._controller_factory = controller_factory or STTController
97:            controller = self._controller_factory(self.config)
```

**Ergebnis:** Die Factory ist einstellig und wird einstellig aufgerufen. Der
Vorschlag aus AR-3 — Default-Factory zu
`lambda cfg: STTController(cfg, observability=observability)` — hält die
öffentliche Signatur unverändert; eine von außen übergebene Factory bleibt
einstellig und erhält im Controller `NULL_INGRESS`. **`FD-A5` bestätigt.**

---

## C-08 – Der Settings-Dialog trägt einen sechsten Tab additiv

```bash
grep -n "TAB_NAMES" -A 12 ui/settings_dialog.py
grep -rn "sensitive" core/settings_metadata.py ui/settings_dialog.py
```

```text
57:    TAB_NAMES = (
58-        "Verlauf",
59-        "Allgemein",
60-        "Verbindung & Betriebsmodus",
61-        "Geräte & Audio",
62-        "Erscheinungsbild & Feedback",
63-    )
88:        for name in self.TAB_NAMES[1:]:
89-            self.tabs.addTab(self._build_settings_tab(name), name)

core/settings_metadata.py:46:    sensitive: bool = False
```

**Ergebnis:**

- Fünf Tabs, metadatengetrieben. Ein sechster Tab kostet **eine** Zeile in
  `TAB_NAMES` plus `SettingDefinition`-Einträge. **`FD-U1` bestätigt.**
- `SettingDefinition.sensitive` existiert, wird aber von **keiner** Definition
  gesetzt und von **keinem** UI-Code gelesen. Befund S-4 bestätigt: das Feld ist
  heute wirkungslos und muss, bevor es je einen Admin-Key trägt, erst
  tatsächlich wirken. Als Auflage nach OBS-110 übernommen.

---

## C-09 – Die verschachtelte Konfig-Dataclass braucht eine Sonderbehandlung

```bash
grep -n "history=\|_build(\|def _build" core/config.py
```

```text
916:        def _build(dc_class, section: dict):
926:            memory_data = _build(HistoryMemoryConfig, history_data.get("memory", {}))
927:            persistent_data = _build(HistoryPersistentConfig, history_data.get("persistent", {}))
944:            history=history_cfg,
945:            logging=_build(LoggingConfig, data.get("logging", {})),
```

**Ergebnis:** `_build` löst verschachtelte Dataclasses **nicht** auf; `history`
wird deshalb bei `:926-927` gesondert gebaut. `logging` läuft heute durch das
einfache `_build`. Ein Unterabschnitt `logging.observability` erfordert
dieselbe Sonderbehandlung wie `history`. Bestätigt die Auflage in OBS-050 und
verhindert einen stillen Fehler („Feld vorhanden, Werte immer Default").

---

## C-10 – Der Datenverzeichnis-Anker existiert

```bash
grep -n "DEFAULT_LOCAL_APP_DIR" -A3 core/config.py
```

```text
33:DEFAULT_LOCAL_APP_DIR = Path(os.environ.get("LOCALAPPDATA", APP_DIR)) / "RealtimeSTT Client"
34:DEFAULT_LOG_DIR = DEFAULT_LOCAL_APP_DIR / "logs"
36:    DEFAULT_LOCAL_APP_DIR / "config.yaml"
```

**Ergebnis:** `%LOCALAPPDATA%\RealtimeSTT Client\` ist die einzige zentral
definierte Datenverzeichniskonstante. Der Store gehört dorthin. **`FD-C9`
bestätigt**; der abweichende Historienpfad (`RealtimeSTT_Client`) bleibt
unangetastet (OD-11).

---

## C-11 – Transkripttext steht heute schon im Klartext im Log

```bash
sed -n '1292,1310p' core/stt_session.py
grep -n "existing=%r, new=%r" core/controller.py
```

```text
core/stt_session.py:1297   logger.info("Final [seg=%s]: %s", …, event.get("text","")[:80])
core/stt_session.py:1303   logger.debug("Realtime [seg=%s]: %s", …, text[:80])
core/controller.py:2078    "Contradictory duplicate final event for %s: existing=%r, new=%r"
core/controller.py:2146    "Contradictory pre-existing history entry for %s: existing=%r, new=%r"
```

**Ergebnis:** Befund P-2 bestätigt. Der `INFO`-Fall passiert den
Handler-Levelfilter (Default INFO) ungehindert; die beiden `WARNING`-Fälle
tragen **vollständige** Texte. Regel `R-10` muss deshalb zwingend auch für
**unstrukturierte** Logtexte gelten, nicht nur für Serverevents.

---

## C-12 – Der bestehende Handleraufbau nimmt einen dritten Handler auf

```bash
sed -n '70,119p' core/logging_setup.py
```

Bestätigt: Root-Level fest `DEBUG` (`:74`), `handlers.clear()` (`:77`),
Rotating-File-Handler und optionaler Stdout-Handler, beide mit
`setLevel(root_level)`. Ein dritter Handler ist additiv; die vorhandenen bleiben
als Rückfallebene unverändert (OD-13).

Bestätigt zugleich `HP-1`: Weil der Root-Logger auf `DEBUG` steht, entsteht der
`LogRecord` ohnehin; `Logger.callHandlers` prüft je Handler
`record.levelno >= hdlr.level`. Ein Handlerlevel `INFO` verhindert also, dass
`emit` für DEBUG-Records überhaupt läuft — es entsteht **kein** zusätzlicher
Aufwand, aber auch **keine** Ersparnis.

---

## C-13 – W-16 geschlossen: die Roadmap widerspricht dem Plan nicht

Das adversariale Review nennt als **einzige** verbliebene Informationslücke die
Frage, ob `voice-stt-client/docs/IMPLEMENTATION_ROADMAP.md` eine dem Plan
widersprechende Aussage zum Logging enthält.

```bash
ls -la docs/IMPLEMENTATION_ROADMAP.md      # 24118 Bytes, vorhanden
grep -n -i "log|observab|diagnos" docs/IMPLEMENTATION_ROADMAP.md
```

Alle Treffer betreffen `/ws/logs` als **Feedbackquelle**, nicht als
Observability-Store. Die beiden einschlägigen Sätze:

```text
:17-19   "/ws/logs wird im Normalbetrieb die einzige serverseitige Quelle für
          persistierte fachliche Feedback- und Lebenszyklusereignisse."
:370-373 "/ws/logs ist im Zustand LIVE die einzige serverseitige Feedbackquelle.
          … Bei nachgewiesener Eventstromdegradation greift ein begrenzter,
          duplikatsicherer /ws/transcribe-Fallback."
```

**Ergebnis: kein Widerspruch.** Beide Aussagen betreffen den **Feedbackpfad**,
den V1 ausdrücklich nicht anfasst; der Beobachter hängt parallel daneben. Die
Roadmap enthält **keine** Aussage über einen clientseitigen Observability-Store,
eine Logansicht oder ein kanonisches Recordmodell.

Zwei Nebenbefunde, beide unschädlich:

- Die Roadmap nennt „fünf Dialogtabs" (`:282`). Der sechste Tab ist additiv und
  ändert keine der fünf bestehenden.
- Die Abnahme von AP7 nennt „HTTP-Stack ausgeschlossen" im gefrorenen Build.
  Nachgeprüft in `voice-stt-client.spec:62-75`: ausgeschlossen sind
  `fastapi`, `starlette`, `uvicorn`, `pydantic`, `lefx.interfaces.api|cli` —
  also der **Server**-Stack innerhalb von LEFX, kein HTTP-**Client**.
  Ein HTTP-Client existiert heute gar nicht (`requirements.txt` kennt nur
  `websockets`, `sounddevice`, `numpy`, `PySide6`, `PyYAML`,
  `led-controller-version-3`). Für V1 ist das folgenlos; für OBS-120 ist es eine
  **benannte Zukunftsauflage**, siehe `LOGGING_ARCHITEKTUR_FREEZE_V1.md §10.3`.

**Damit ist die letzte offene Informationslücke der Vorbereitung geschlossen.**

---

## Zusammenfassung

| # | Prüfung | Ergebnis |
|---|---|---|
| C-01 | Vorarbeit gegen diesen Arbeitsbaum | bestätigt, Zeilenverweise gültig |
| C-02 | Hookstelle frei und additiv | bestätigt |
| C-03 | Rückgabewertsemantik `_dispatch` | bestätigt, **verschärft** (`reject_event` bei Ausnahme) |
| C-04 | Cursorverwurf bei Serverneustart | bestätigt |
| C-05 | D-1 Serialisierung | bestätigt, **schwerer** als beschrieben (`frozenset`) |
| C-06 | Qt-Grenze | bestätigt |
| C-07 | Injektionsweg ohne Testbruch | bestätigt |
| C-08 | Sechster Settings-Tab additiv | bestätigt; `sensitive` heute wirkungslos |
| C-09 | Verschachtelte Configdataclass | bestätigt, Sonderbehandlung nötig |
| C-10 | Datenverzeichnis | bestätigt |
| C-11 | Transkripttext im Klartext | bestätigt |
| C-12 | Dritter Handler additiv | bestätigt |
| C-13 | W-16 Roadmap | **geschlossen, kein Widerspruch** |

Zwei Prüfungen haben die Vorarbeit **korrigiert** (C-03, C-05); beide Korrekturen
sind in die normativen Artefakte eingearbeitet.
