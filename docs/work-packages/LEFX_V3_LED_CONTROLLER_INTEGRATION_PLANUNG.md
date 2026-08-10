# LEFX V3 LED-Controller — Integrationsplanung

Stand: 2026-08-09 · Status: **Planung, nichts implementiert** · AP-Nummer offen

Ziel: Das in AP07 eingeführte Feedback-Mapping treibt den **LEFX V3 LED-Controller**
(`led-controller-version-3`, Entwicklung in `C:\Users\marco\source\repos\respeaker-led-v3`,
Bezug über PyPI) an. Der Controller-Service läuft **im selben Python-Prozess als
eigener Thread**. Der bisherige direkte USB-Adapter entfällt ersatzlos.

---

## 1. Vokabular

Zwei Projekte, zwei gewachsene Begriffswelten, mehrere Kollisionen. Diese Festlegung
gilt für **Prosa und Dokumentation**; Code-Bezeichner werden **nicht** umbenannt.

| Begriff | Bedeutung hier | Anmerkung |
|---|---|---|
| **Ereignis** | eingehender Fakt des Clients (`CanonicalEventType`, z. B. `server.transcription.completed`) | im Code weiterhin `Event*` — `CanonicalEventType`, `NormalizedFeedbackEvent`, `event_stream` |
| **Regel** | Zuordnung Ereignis → Wirkung, im YAML-Block `feedback_mappings` | |
| **State** | LEFX-Lebenszyklusform: dauerhafter Zustand in einem Slot | unübersetzt |
| **Event** | LEFX-Lebenszyklusform: einmalige Anzeige mit fester Dauer, höchste Priorität | unübersetzt — **nicht** das Client-Ereignis |
| **Overlay** | LEFX-Lebenszyklusform: überlagernde Anzeige, zeit-, parameter- oder funktionsgesteuert | unübersetzt |
| **Slot / Channel / Preset / Sink / Invocation** | LEFX-Begriffe | unübersetzt |
| ~~Impuls~~ | gestrichen | war das Client-Wort für ein LEFX-Event |
| ~~`LedEffectId`~~ | gestrichen | siehe Abschnitt 5 |

**Beobachtungsliste — dieselben Wörter, andere Bedeutung, kontextuell trennbar:**

- *Overlay*: UI-Transkriptfenster des Clients ↔ LEFX-Lebenszyklusform
- *Channel*: Log-Kanal des Clients ↔ Kanalname eines Controlled Overlay in LEFX.
  In der YAML deshalb `lefx_channel`, nicht `channel`.

---

## 2. Entschiedene Vorgaben

Diese Punkte sind entschieden und werden im Plan nicht mehr aufgeworfen.

| # | Entscheidung | Folge |
|---|---|---|
| 1 | Beide Sets laden: `core` **und** `smartspeaker` | Voller Katalog zum Ausprobieren. Namenskollisionen zwischen den Sets sind möglich (`AmbiguousTargetError`) → Regeln dürfen `source::id` schreiben; die Startprüfung deckt es sofort auf. Ein eigens abgestimmtes Set folgt später |
| 2 | Overlays sind **Folgepaket** | Hier nur State und Event. Die Datenflüsse (Pegel, Countdown, DoA, Verbindungsstatus) werden im Folgepaket **einmalig und endgültig** gelöst — als eigener größerer Block, siehe Abschnitt 9 |
| 3 | `direct`-Backend **sofort raus** | LEFX beherrscht die USB-Verbindung des LED-Teils allein. Der Client greift dort nicht mehr ein. Das Audiogerät bleibt unberührt |
| 4 | Upstream-Fixes sind **Teil dieses Pakets** | Arbeit in beiden Repos, mit Reihenfolge: PyPI-Release **vor** Client-Pin |
| 5 | Startprüfung, danach nur Gültiges ersetzt Gültiges | Ungültige Einstellungen werden intern nie gesetzt; die letzten gültigen bleiben in Kraft |

### Was Entscheidung 3 konkret entfernt

- `ui/led_feedback.py`: `ReSpeakerXvf3800Adapter`, `IsolatedReSpeakerAdapter`,
  `_respeaker_process_worker`, `_windows_usb_device_present`, der gesamte
  `multiprocessing`-Helferprozess
- `core/config.py`: `LedConfig.vendor_id`, `.product_id`, `.speed`, `.usb_timeout_ms`
  verlieren ihren Ort (VID/PID und Timeout werden LEFX-seitig konfiguriert)
- `requirements.txt`: `pyusb` und `libusb-package` entfallen als direkte
  Abhängigkeiten — sie kommen transitiv über `led-controller-version-3`
- `voice-stt-client.spec`: `collect_dynamic_libs("libusb_package")` und die
  `usb.*`-`hiddenimports` werden von der LEFX-Bündelung abgelöst
- `tests/test_led_feedback.py` (330 Zeilen) wird weitgehend neu geschrieben
- **ADR-003 wird historisch**; ADR-004 tritt an seine Stelle

### Was Entscheidung 5 konkret bedeutet

Zwei Fehlerarten, die strikt auseinandergehalten werden müssen — sonst startet der
Client nicht mehr, nur weil kein ReSpeaker eingesteckt ist:

| Lage | Bewertung | Reaktion |
|---|---|---|
| Regel nennt ein Ziel, das im geladenen Katalog nicht existiert | **Konfigurationsfehler** | Start abbrechen, Fehler melden |
| Regel nennt ein unbekanntes Verb, oder `config` ist kein Mapping | **Konfigurationsfehler** | Start abbrechen |
| Ziel ist zwischen `core` und `smartspeaker` mehrdeutig | **Konfigurationsfehler** | Start abbrechen, `source::id` verlangen |
| Hardware nicht angeschlossen, Kabel gezogen, Gerät belegt | **kein** Konfigurationsfehler | Start läuft weiter, Selbstheilungsschleife übernimmt |
| Simulator-Fenster nicht offen | **kein** Konfigurationsfehler | wie oben |

Zur Laufzeit (`apply_runtime_config`): Kandidat wird **vollständig gegen den
geladenen Katalog geprüft, bevor** er gesetzt wird. Fällt er durch, bleibt die
letzte gültige Konfiguration in Kraft und nichts wird angefasst. Der Pfad in
[ui/application.py:315](ui/application.py:315) stellt heute schon die vorherige
Konfigurationsdatei wieder her — die Prüfung wird davor gehängt.

**Lazy bleibt lazy — mit genau einer Ausnahme.** USB-Verbindung und Renderschleife
werden weiterhin erst bei Bedarf gebraucht. Eager sein muss allein der **Katalog**,
weil ohne Registry keine Startprüfung möglich ist. Der Katalogaufbau liest nur die
`.lefxset`-Archive von der Platte, fasst kein USB an, blockiert nicht. Nennt keine
Regel ein LED-Ziel, wird der Katalog nicht gebraucht und nichts schlägt fehl —
„nichts konfiguriert" ist gültig.

---

## 3. Ausgangslage

### 3.1 Client

Eine einzige Übergabestelle an die LEDs:

```
EventStream / STT-Fallback / lokale Fakten
  └─► core/event_normalizer.py     → NormalizedFeedbackEvent
      └─► core/feedback_reducer.py → FeedbackDecision{rule, impulse, publish, replay}
          └─► core/feedback_mapping.py  (YAML `feedback_mappings`)
              └─► ui/application.py:174 → led_feedback.submit(...)
```

| Baustein | Datei | Zustand |
|---|---|---|
| Mapping-Schema | [core/feedback_mapping.py](core/feedback_mapping.py) | `schema_version: 1`, 10 feste `LedEffectId` → **wird ersetzt** |
| Ausgabeschicht | [ui/led_feedback.py](ui/led_feedback.py) | Worker-Thread, Coalescing, Impulslogik, drei Adapter → **wird umgebaut** |
| Konfiguration | [core/config.py:635](core/config.py:635) | `LedConfig` → **wird neu geschnitten** |
| Rekonfiguration | [ui/application.py:315](ui/application.py:315) | Neuaufbau bei geändertem `led`-Block → bleibt, Prüfung davor |
| Fehlermeldung | [ui/application.py:187](ui/application.py:187) | `on_failure` → `client.led.unavailable` → bleibt |
| Reducer / Normalizer / Eventprotokoll | `core/event_*.py`, `core/feedback_reducer.py` | **unverändert** |

### 3.2 LEFX (`led-controller-version-3` 3.0.2)

| Baustein | Kernaussage |
|---|---|
| `ControllerService` | Für Einbettung gebaut. Daemon-Thread `lefx-render`, alles über `RLock`, `start()/stop()` |
| Verben | `set_state`, `clear_state`, `set_overlay`, `update_overlay`, `clear_overlay`, `emit_event`, `set_output`, `clear_all` |
| Statusmeldungen | `add_listener` → `sink_changed{sink, available, detail}` |
| Hardware | `UsbTransport` mit eigenem Reconnect-Thread (`retry_interval_s = 3.0`) und `VERSION`-Heartbeat (2 s); `ReSpeakerFrameSink` schreibt nur bei Änderung |
| Simulator | `SimulatorFrameSink` ist ein **Loopback-Socket-Client**, kein Qt im Client-Prozess. Das Ringfenster ist ein eigenes Programm, das sich einwählt |
| Entdeckung | Sinks, Provider und Sets über `importlib.metadata.entry_points()` |
| Kataloge | `core-set` 13 Effekte / 24 Presets · `smartspeaker-set` 23 Effekte / 47 Presets |
| Python | `>=3.12,<3.13` — Client-venv 3.12.10 ✅ |

---

## 4. Zielarchitektur

```
FeedbackDecision.rule.led  (Liste von LEFX-Aufrufen)
  └─ LedFeedback.submit(calls, live=...)            [umgebaut: Queue statt Slot]
       └─ Worker-Thread "RealtimeSTT-LED"
            └─ LedController-Port  (6 Verben)       [NEU: schmale Naht]
                 └─ InProcessLedController
                      └─ ControllerService
                           └─ Thread "lefx-render" (30 fps)
                                └─ ReSpeakerFrameSink | SimulatorFrameSink
                                     └─ Thread "respeaker-usb-monitor"
```

**Warum der eigene Port `LedController`:** Dein Versprechen „derselbe Kern in allen
Varianten" — eingebettet, eigener Prozess, eigenständiger Service — soll auch
clientseitig halten. Spricht der Client gegen eine schmale Naht mit genau den sechs
Verben, lässt sich `InProcessLedController` später gegen `ControllerClient` (HTTP)
tauschen, **ohne** dass YAML, Reducer oder `application.py` etwas davon merken.
Kostet fast nichts, wenn man es von Anfang an so schneidet.

**Warum der Worker-Thread bleibt:** Siehe Blocker B1 — LEFX rendert synchron im
aufrufenden Thread. Kein Aufruf darf je aus dem Qt-Main-Thread kommen.

Zusätzliche Threads im Client-Prozess, alle Daemon: `lefx-render`,
`respeaker-usb-monitor`, kurzlebige `respeaker-on_connected/on_disconnected`.

---

## 5. Mapping-Schema `schema_version: 2`

`LedEffectId` entfällt. Die Regel spricht direkt LEFX.

```yaml
feedback_mappings:
  schema_version: 2
  events:
    <ereignis-id>:
      led:  <aufruf> | [<aufruf>, ...]
      sound: {cue: ..., volume: ...}     # unverändert
      app:   {action: ...}               # unverändert
```

Ein `<aufruf>` ist ein Mapping mit **genau einem Verb** als Schlüssel:

| Form | Zusatzschlüssel |
|---|---|
| `{set_state: <ziel>}` | `config`, `slot` (`primary`\|`background`), `action` (`on`\|`off`) |
| `{clear_state: <slot>}` | — |
| `{emit_event: <ziel>}` | `config`, `duration_ms`, `priority` |
| `{set_output: {}}` | `brightness`, `enabled` |
| *(Folgepaket)* `{set_overlay: <ziel>}` | `config`, `lefx_channel`, `inputs` |
| *(Folgepaket)* `{clear_overlay: <kanal>}` | — |

**Warum eine Liste erlaubt ist:** Ein Wake-Word soll aufblitzen **und** den Zustand
wechseln. In Schema 1 war pro Regel nur eine Wirkung möglich; mit zwei
Lebenszyklusformen ist die Liste der natürliche Weg. Aufrufe werden in
Reihenfolge abgesetzt.

**`<ziel>` ist ein Effekt- oder Presetname** — beide liegen im selben Namensraum
(`registry.resolve`). Damit greift dein Baukastenprinzip bis in die Client-YAML
durch: `{set_state: listening}` nimmt das Default-Preset, `{set_state: listening_cyan}`
nimmt ein fertiges, `{set_state: listening, config: {speed: 1.8}}` verstellt gezielt
einen Parameter. Alles konfigurierbar, nichts konfigurationspflichtig.

**Der Client validiert LEFX-Parameter nicht inhaltlich.** Er prüft Struktur (Verb
bekannt, genau ein Verb, Ziel nicht leer, `config` ist ein Mapping) und lässt das
Ziel von LEFX auflösen. Ob `speed: 1.8` zulässig ist, entscheidet LEFX. Das steht
bewusst quer zur sonst strikten Typprüfung von AP07: Eine zweite Parametervalidierung
im Client veraltet in dem Moment, in dem ein Set aktualisiert wird.

---

## 6. Vorschlag: vollständige Mapping-Referenz

Alle 30 Ereignisse, abgeleitet aus dem heutigen `config.yaml`, übersetzt auf
`core` + `smartspeaker`. `sound` und `app` bleiben wie sie sind und stehen hier
nur, wo sie das Verständnis stützen.

```yaml
feedback_mappings:
  schema_version: 2
  events:

    # -- Server: Diktierablauf ------------------------------------------------
    server.wakeword.detected:
      led: [{emit_event: wakeword_detected}, {set_state: waiting}]
      sound: {cue: wake_word}
      app: {action: indicator.waiting_for_speech}
    server.recording.started:
      led: {set_state: listening}
      sound: {cue: start}
      app: {action: indicator.recording}
    server.recording.ended:
      led: {set_state: thinking}
      sound: {cue: stop}
      app: {action: indicator.finalizing}
    server.transcription.started:
      led: {set_state: thinking}
      app: {action: indicator.finalizing}
    server.transcription.completed:
      led: [{emit_event: success_event, duration_ms: 700}, {set_state: ready_state}]
      sound: {cue: complete}
      app: {action: indicator.success}
    server.transcription.discarded:
      led: {set_state: ready_state}
      app: {action: indicator.idle}
    server.transcription.failed:
      led: [{emit_event: error_event, duration_ms: 1200}, {set_state: ready_state}]
      sound: {cue: error}
      app: {action: indicator.error}
    server.transcription.cancelled:
      led: [{emit_event: reject_event}, {set_state: ready_state}]
      sound: {cue: cancel}
      app: {action: indicator.idle}
    server.transcription.rejected:
      led: [{emit_event: reject_event}, {set_state: ready_state}]
      sound: {cue: error}
      app: {action: indicator.error}

    # -- Client: Bedienung ----------------------------------------------------
    client.hotkey.accepted:
      led: {set_state: waiting}
      app: {action: indicator.waiting_for_speech}
    client.action.blocked:
      led: {emit_event: warn_event}
      sound: {cue: warning}
      app: {action: indicator.warning}
    client.dictation.interrupted:
      led: [{emit_event: warn_event, duration_ms: 1000}, {set_state: ready_state}]
      sound: {cue: warning}
      app: {action: indicator.warning}

    # -- Client: Verbindung ---------------------------------------------------
    client.transport.disconnected:
      led: {set_state: reconnect_network_state}
      app: {action: indicator.warning}
    client.event_stream.connecting: {}
    client.event_stream.replaying: {}
    client.event_stream.live: {}
    client.event_stream.degraded:
      app: {action: indicator.warning}

    # -- Client: Mikrofon -----------------------------------------------------
    client.microphone.lost:
      led: {set_state: reconnect_mic_state}
      sound: {cue: warning}
      app: {action: indicator.warning}
    client.microphone.recovered:
      led: {set_state: ready_state}

    # -- Client: Texteinfügung ------------------------------------------------
    client.injection.accepted: {}
    client.injection.succeeded: {}
    client.injection.failed:
      led: {emit_event: error_event}
      sound: {cue: error}
      app: {action: indicator.error}

    # -- Client: Sprachausgabe ------------------------------------------------
    client.tts.started:
      led: {set_state: speaking}
    client.tts.stopped:
      led: {set_state: ready_state}
    client.tts.failed:
      led: {emit_event: error_event}
      sound: {cue: error}
      app: {action: indicator.error}

    # -- Client: Selbstauskunft -----------------------------------------------
    client.led.unavailable:
      app: {action: indicator.warning}      # kein led — der Ring ist ja gerade weg
    client.sound.failed:
      app: {action: indicator.warning}
    client.configuration.invalid:
      led: {emit_event: error_event}
      app: {action: indicator.error}

    # -- Client: Lebenszyklus -------------------------------------------------
    client.lifecycle.started:
      led: [{emit_event: init_event}, {set_state: ready_state}]
    client.lifecycle.stopping:
      led: {clear_state: primary}
      app: {action: indicator.idle}
```

**Offene Detailfragen zu dieser Referenz** (klein, in M4 zu klären):

- `waiting` vs. `breathing_ring` für die Wartephase — `waiting` ist semantisch
  passend (gelb/orange), `breathing_ring` verhaltenstreu zum heutigen weißen Atmen
- `thinking` ist zweifarbig (`color_a`/`color_b`); wer Farbe anpassen will, muss
  wissen welchen Parameter — gehört in die Client-Doku
- `client.led.unavailable` bekommt bewusst **kein** `led`: Wenn der Ring nicht
  erreichbar ist, kann er es nicht selbst anzeigen. Die Meldung geht über Tray
  und Overlay
- Alle Zielnamen sind gegen den tatsächlich geladenen Katalog zu verifizieren
  (`service.list_definitions()`), nicht gegen die Doku

---

## 7. Probleme

### Gelöst durch die Entscheidungen

| war | erledigt durch |
|---|---|
| USB-Exklusivität, kein Parallelbetrieb zweier Adapter | Entscheidung 3 — es gibt nur noch einen |
| Semantiklücke `LedEffect` ↔ LEFX-Katalog | Schema 2 |
| Doppelte Wiederherstellung nach Puls | Entfällt: LEFX-Events stellen selbst wieder her |
| `LedConfig`-Felder ohne Wirkung | Entscheidung 3 — `LedConfig` wird neu geschnitten |
| Qt-Konflikt mit dem Simulator | Geprüft: Simulator-Sink ist ein Loopback-Socket, kein Qt im Client-Prozess |

### Offen

**B1 — LEFX rendert synchron im aufrufenden Thread.**
`ControllerService._command()` nimmt `self._lock` und ruft `runtime.render_once()`
im Aufruferthread; der Aufrufer schreibt also selbst auf den USB. Zusätzlich
serialisiert `UsbTransport._io_lock` gegen den Heartbeat.
→ **Nur der Worker-Thread ruft LEFX auf.** Nicht verhandelbar.

**B2 — USB-Timeout 100 Sekunden.**
`xvf.py:186` setzt `TIMEOUT = 100000`, von pyusb als Millisekunden gelesen. Bei einem
Gerät, das nicht mehr antwortet, dessen Handle aber noch existiert (Hub im Suspend,
Treiberhänger, Sleep/Wake), wartet libusb die vollen 100 s. Worst Case: erst 100 s
hinter einem hängenden Heartbeat, dann 100 s auf den eigenen Schreibvorgang.
Die Selbstheilungsschleife existiert bereits — sie greift nur bis zu 100 s zu spät.
→ **Upstream konfigurierbar machen, Zielwert ~500 ms.** Teil dieses Pakets (M1).

**B3 — Keine Prozessisolation mehr.**
ADR-003 hatte den killbaren Helferprozess bewusst gewählt. In-Process gibt es diesen
Not-Aus nicht. `ControllerService.stop()` joint 2,0 s, `UsbTransport.stop()` 4,0 s —
beide laufen durch, ohne dass ein hängender Thread wirklich endet.
→ Bewusste Entscheidung, gehört in **ADR-004**. Schadensbegrenzung: B2-Timeout,
Watchdog auf dauerhaft `degraded`, und `LedFeedback.shutdown()` meldet bereits
`False`, wenn der Worker nicht endet ([ui/application.py:381](ui/application.py:381)).

**B4 — PyInstaller findet Sink und Katalog nicht über Entry Points.**

Zur Klarstellung, weil das leicht schlimmer klingt als es ist: **Dateien lassen
sich sehr wohl mitbündeln.** PyInstaller packt beliebige Daten über `datas` in
die EXE; zur Laufzeit liegen sie unter `sys._MEIPASS` und sind über einen
eindeutigen Pfad ansprechbar. Die `.lefxset`-Archive sind also kein Problem —
Built-in-Effekte bleiben built-in.

Das Problem ist ausschließlich der **Entdeckungsweg**: LEFX findet Sinks,
Provider und Sets über `importlib.metadata.entry_points()`, und ein Onefile-Build
enthält standardmäßig keine `dist-info`-Metadaten. Ergebnis wäre: im venv grün,
im Release `LookupError` und eine leere Registry.

→ **Lösung: den Entdeckungsweg umgehen.** Sink direkt instanziieren,
`search_paths` explizit auf das gebündelte Archivverzeichnis unter `sys._MEIPASS`
zeigen lassen. Dann hängt nichts an Metadaten. Verifikation **nur** im gefrorenen
Build, nie im venv.

→ **Zusätzliche Rückfallebene: `led.effect_paths`.** Eine Liste von Ordnerpfaden
in der Client-Konfiguration, die den Suchbereich erweitert. Damit lassen sich
globale `.lefxset`-Ordner festlegen, die nicht mitgeschleppt werden müssen.
LEFX bringt das Gegenstück bereits mit — `package_path` in
`lefx/interfaces/config.py`, das `paths.package_search_paths()` zusätzlich zu den
installierten Sets scannt. Es fehlt nur der Durchgriff aus der Client-Konfiguration.
Gedacht als Sicherheitsnetz und für Sonderfälle, **nicht** als Ersatz für die
gebündelten Kataloge.

**B5 — FastAPI/Pydantic/Uvicorn sind Importzeit-Pflicht.** ✅ **erledigt in M1**

`lefx/interfaces/__init__.py` importierte `.api` in der Importliste. Da beim Import
eines Untermoduls immer erst das Paket-`__init__` läuft, zog auch
`import lefx.interfaces.service` die komplette FastAPI-Kette nach.

Beim Beheben kam ein **zweiter, verdeckter Importpfad** zum Vorschein, den der
neue Test aufgedeckt hat: `client.py` — der reine Standardbibliothek-HTTP-Client —
importierte `API_PREFIX` aus `api.py` und lud damit den gesamten *Server*-Stack
für eine sieben Zeichen lange Zeichenkette. `API_PREFIX` ist der Vertrag zwischen
beiden Enden der Leitung und gehört keinem von beiden; er liegt jetzt in einem
eigenen, abhängigkeitsfreien Modul `lefx/interfaces/contract.py`.

Messergebnis nach der Änderung:

| | Module | Importzeit | HTTP-Stack |
|---|---|---|---|
| eingebettet (`ControllerService`) | **232** | **260 ms** | keiner |
| Server (`create_app`) | 435 | 650 ms | wie bisher |

**B6 — Konfigurationskollision auf `config.yaml`.**
`lefx/interfaces/config.py:165` sucht ohne `LEFX_CONFIG` nach `Path.cwd()/config.yaml` —
im Client-Betrieb die Client-Konfiguration. Heute kollidiert kein Schlüssel, aber
ein künftiger Client-Schlüssel `port`, `host` oder `log_level` würde stillschweigend
als LEFX-Einstellung gelesen.
→ Alle Werte explizit am Konstruktor übergeben (`led_count`, `fps`, `search_paths`,
`state_file`, `sink`) und `LEFX_CONFIG`/`LEFX_STATE_ROOT` gezielt setzen.

**B7 — `LedFeedback` braucht eine Queue statt eines Slots.**
Die heutige Coalescing-Logik „ein ausstehendes Update, neues ersetzt altes" ist
richtig, solange alles ein einziger persistenter Effekt ist. Mit zwei
Lebenszyklusformen wird sie falsch: States dürfen zusammengefasst werden,
**Events dürfen nicht verworfen werden**.
→ Kleine beschränkte Queue; States dürfen ältere States gleicher Art überholen,
Events nie. Der Replay-Schutz aus ADR-003 bleibt und knüpft künftig an
`emit_event` statt an eine Effektmenge.

**B8 — Ringgröße nicht konfigurierbar.**
`ReSpeakerFrameSink` meldet bei `led_count != xvf.RING_LED_COUNT` (=12) dauerhaft
`available=False`.
→ `led_count` nicht in die Client-Konfiguration, sondern aus `xvf.RING_LED_COUNT`.

**B9 — Fremder Zustandsspeicher.**
`ControllerService` schreibt `background_state.json` unter `state_root`
(Default `%TEMP%/lefx-runtime`), geteilt mit jeder anderen LEFX-Instanz.
→ `state_file=` explizit in den Client-Zustandsordner.

**B10 — Dauerlast im Leerlauf.**
Renderthread mit 30 fps permanent, dazu ein USB-Read alle 2 s. USB-Writes nur bei
Änderung, die Kompositionsarbeit nicht.
→ `fps` konfigurierbar; Messung im Langlauftest (M9). Service **nicht** bedarfsweise
starten/stoppen — jeder Zyklus kostet Reconnect-Zeit.

**B11 — DoA-Provider ungewollt aktiv.**
`ControllerService` setzt `input_device = sink_name`, startet also `respeaker.doa`
und dessen zusätzliche USB-Reads.
→ `autostart_providers=False`, bis das Overlay-Folgepaket sie braucht.

---

## 8. Selbstheilung und Simulationsangebot

`UsbTransport` bringt die Schleife mit: Reconnect alle 3 s, Heartbeat alle 2 s,
`session_dirty` beim Wiederverbinden (der Sink sendet Ringmodus neu). Der Client
muss sie nicht bauen, nur nutzbar machen — dafür sorgt B2.

**Angebot zur Simulationsumschaltung.** Nach anhaltend erfolglosem Reconnect bietet
der Client an, auf den Simulator-Sink zu wechseln.

- **Schwelle zeitbasiert**, nicht versuchsbasiert: 10 Versuche sind bei
  `retry_interval_s = 3.0` erst 30 s. Vorschlag **120 s**, konfigurierbar
- **Kein Tastendruck im Client** — der ist eine Tray-Anwendung mit `console=False`.
  Ein globaler Hotkey scheidet aus, weil der Client Text injiziert. Also:
  **Tray-Benachrichtigung + Menüeintrag „Auf Simulation umschalten"**
- Der Tastendruck (`"S"`) ist die passende Form für `lefx serve` — Upstream, optional
- **Nur Diagnosepfad:** Der Menüeintrag erscheint nur, wenn das Simulator-Paket
  installiert ist. Der Simulator-Sink selbst ist billig und Qt-frei, aber das
  Ringfenster ist ein eigenes Programm, das sich einwählen muss — ohne laufendes
  Fenster bringt die Umschaltung nichts. **Der Simulator kommt nicht in den
  Release-Build**
- Umschaltung = `ControllerService` stoppen und mit anderem Sink neu bauen
  (`reset_shared_transport()` davor). Kein Sink-Tausch zur Laufzeit nötig
- Rückweg genauso: Menüeintrag „Zurück auf Hardware"
- **Beobachten:** Der Simulator-Link lauscht auf einem Socket im Client-Prozess.
  Bind auf `127.0.0.1` erzwingen, damit keine Firewallabfrage entsteht

---

## 9. Folgepaket: Overlays und Datenflüsse

Bewusst **nicht** Teil dieses Pakets, aber hier festgehalten, damit es als
zusammenhängender Block geplant wird statt schrittweise anzuwachsen.

**Das Problem:** Eine Regel feuert einmal pro Ereignis. Sie kann ein Overlay
*starten* und *beenden* — ein Progressring, Pegel oder DoA-Winkel braucht aber
laufendes `update_overlay(lefx_channel, inputs)`. Das ist eine zweite,
kontinuierliche Verdrahtung neben dem Mapping.

**Zielsetzung des Folgepakets — einmalig und endgültig lösen:**

- Ein benannter Port für Live-Datenquellen im Client, mit definierter Rate,
  Rückstaubehandlung und Verhalten bei fehlender Quelle
- Kandidaten: Audiopegel (`core/audio_capture.py`), Countdown des Diktierfensters,
  Verbindungsgüte des Eventstreams, DoA aus `respeaker.doa`
- Kanalverwaltung: wer besitzt welchen `lefx_channel`, wer räumt ihn auf,
  was passiert bei Sitzungsende oder Absturz einer Quelle
- Erweiterung des Schemas um `set_overlay`/`update_overlay`/`clear_overlay`
  (in Abschnitt 5 bereits vorgesehen, hier scharf geschaltet)
- Aktivierung von `respeaker.doa` (`autostart_providers`), inklusive Kalibrierung
- Erst danach ist der Weg frei für das eigens abgestimmte Effekt-Set

---

## 10. Implementierungsplan

### M0 — ADR-004 entwerfen *(kein Code)*
Festhalten: Wegfall der Prozessisolation (B3), Schema 2 statt `LedEffectId`,
`direct` ersatzlos entfernt, Verzicht auf clientseitige Parametervalidierung,
Umgehung der Entry-Point-Entdeckung im gefrorenen Build (B4).
ADR-003 als „in Teilen abgelöst" markieren.

**Abnahme:** ADR-004 im Entwurf, ADR-003 gekennzeichnet.

### M1 — Upstream: `respeaker-led-v3` *(vorgelagert)* — **Code fertig**
1. ✅ `create_app` lazy über `__getattr__` (PEP 562); `API_PREFIX` in neues
   `lefx/interfaces/contract.py` verschoben, weil `client.py` darüber den ganzen
   Server-Stack nachzog (B5)
2. ✅ `xvf.DEFAULT_TIMEOUT_MS = 1000` statt 100 000; `ReSpeaker(dev, timeout_ms=…)`
   und `xvf.find(…, timeout_ms=…)` (B2)
3. ✅ VID/PID und Timeout über `sink_options` durchgereicht — als vorbereitete
   `finder`-Closure in `registration._transport_options`, damit `UsbTransport`
   keinen neuen Parameter braucht. Ohne Angabe wird kein Finder übergeben, eine
   gewöhnliche Installation bleibt unberührt
4. ✅ `uv run pytest -m "not hardware"`: **1520 grün, 3 übersprungen**,
   Architekturtest grün; `lefx --help` und `lefx config` unverändert
5. ✅ `uv run python scripts/release.py` → **PyPI 3.0.3 veröffentlicht**
   (Tag `v3.0.3`, Commit `16fd33f`, CI grün, alle drei Distributionen hochgeladen)

Mitgelaufen: ein Testfehler, der nichts mit dem Paket zu tun hatte —
`test_a_running_service_is_reported_rather_than_fought_with` zeigte die
Instanzdatei auf `os.getppid()`. Unter Windows gibt es keine Eltern-Kind-Beziehung;
der Elternprozess kann bereits beendet sein, und ob er es ist, hängt allein davon
ab, wie der Testlauf gestartet wurde. Der Test startet jetzt einen eigenen Prozess.
Produktivcode war nicht betroffen.

**Abnahme:** ✅ Aus einer frischen PyPI-Installation von 3.0.3 verifiziert:

| Prüfung | Ergebnis |
|---|---|
| HTTP-Stack beim Einbetten | keiner |
| USB-Timeout | 1000 ms (vorher 100 000) |
| VID/PID-Durchgriff | vorhanden |
| Katalog | 36 Effekte, 71 Presets |
| `create_app` weiterhin erreichbar | ja |

### M2 — Abhängigkeit im Client
`requirements.txt`: `led-controller-version-3==3.0.3` rein, `pyusb`/`libusb-package`
raus (kommen transitiv mit).

Stand: In der Client-venv liegt derzeit noch die **editierbare Workspace-Installation**
aus der Entwicklungsphase. Sie ist auf die PyPI-Version umzustellen, sobald die
Client-Arbeit beginnt — sonst hängt der Build an einem lokalen Pfad.

Rauchprobe bereits bestätigt: beide Sets sichtbar, 36 Effekte, 71 Presets,
kein HTTP-Stack. Zusätzlich vorab verifiziert: **alle 13 Ziele der
Mapping-Referenz aus Abschnitt 6 lösen auf**, jedes in der erwarteten Form
(Event vs. State), ohne Mehrdeutigkeit zwischen `core` und `smartspeaker` —
damit ist auch M4s Abnahmekriterium vorweggenommen.

### Stand der Umsetzung (2026-08-10)

| Meilenstein | Stand |
|---|---|
| M1 Upstream + Release 3.0.3 | ✅ auf PyPI |
| M2 Abhaengigkeit im Client | ✅ `led-controller-version-3==3.0.3` |
| M3 Schema 2 | ✅ inkl. Serialisierung zurueck in die YAML-Form |
| M4 Mapping-Referenz | ✅ alle 30 Ereignisse in `config.yaml` |
| M5 `LedController`-Port | ✅ `core/led_controller.py` |
| M6 `LedFeedback`-Umbau | ✅ Queue, Replay-Schutz, Entprellung |
| M7 Konfiguration + Startpruefung | ✅ inkl. „nur Gueltiges ersetzt Gueltiges" |
| M8 Simulationsangebot | ✅ Tray-Eintrag + Umschaltung zur Laufzeit |
| M9 Packaging | ✅ gefrorener Build verifiziert (siehe unten) |
| M9 Abnahme | Hardware-Smoke, Trennung/Wiederverbindung und Langlauf gruen |
| M0 ADR-004 | ✅ geschrieben, ADR-003 als teilweise abgeloest markiert |

**Trennung und Wiederverbindung** — ohne Kabelzug geprueft, weil beim Simulator
das "Geraet" ein Ringfenster ueber einen Loopback-Socket ist: Es zu schliessen
ist eine echte Trennung und es zu oeffnen eine echte Wiederverbindung. Geprueft
wird damit genau der Teil, der dieser Anwendung gehoert — Sink-Meldung,
einmalige Benachrichtigung je Ausfall, die Uhr fuer das Simulationsangebot und
die Erholung. Der Reconnect ueber USB ist LEFX' eigene Sache.
Ergebnis: eine Meldung beim Verlust, Uhr laeuft trotz gelungener Befehle weiter,
Erholung ohne Zutun, beim zweiten Verlust eine **eigene** zweite Meldung statt
einer Dublette, danach zweite Erholung. `tests/manual_test_ap07_led_disconnect.py`

**Offen bleibt der physische Kabelzug am ReSpeaker.** Den kann nur ein Mensch
machen; die Codestrecke darueber ist durch das Obige abgedeckt.

Testsuite **402 gruen** (Ausgangswert 396). Hardware-Smoke auf echtem ReSpeaker
ohne Ausfall; Simulator loest den Katalog auf, Umschaltung in beide Richtungen
sauber.

### Zwei Fehler, die nur der gefrorene Build gezeigt hat

**Der halb geladene Katalog.** Der erste Build startete durch, aber `core-set`
fehlte: `random_sparkle` importiert `colorsys`, und Effekte werden zur Laufzeit
aus dem `.lefxset` entpackt und importiert — kein statischer Analyselauf kann
das sehen. Sichtbar war es nur an einer WARNING-Zeile im Protokoll; die
Startpruefung schwieg, weil alle benutzten Ziele aus dem `smartspeaker-set`
stammen. `colorsys`, `math` und `random` stehen jetzt in `hiddenimports`.
**Wer ein Set aktualisiert, muss diese Liste mitfuehren.**

**Die Uhr, die nie lief.** `unavailable_seconds` wurde von jedem gelungenen
Befehl zurueckgesetzt — das Simulationsangebot haette nie ausgeloest. Grund:
Weder der reSpeaker- noch der Simulator-Sink wirft je aus `apply_frame`. Ein
Bild kommt dreissig Mal pro Sekunde, ein gezogenes Kabel ist ein normaler
Zustand, also melden beide den Fehler ueber `status()`. Ein Befehl, der
zurueckkehrt, sagt deshalb nur, dass LEFX ihn angenommen hat. Der Sink ist die
Instanz fuer Verfuegbarkeit; ein gelungener Befehl loescht eine stehende
Sink-Stoerung nicht mehr.

**Gefrorener Build — B4 erledigt.** Das Risiko mit der hoechsten
Eintrittswahrscheinlichkeit ist ausgeraeumt und im Bundle nachgewiesen:

| Pruefung | Ergebnis |
|---|---|
| `lefx\sets\core_set\core-set.lefxset` | vorhanden, genau wo `package_file()` sucht |
| `lefx\sets\smartspeaker_set\smartspeaker-set.lefxset` | vorhanden |
| lefx-Module im PYZ | 46, inkl. der drei per Name importierten |
| fastapi / pydantic / uvicorn / starlette | je 0 Eintraege |
| `lefx.interfaces.api` / `.cli` / Simulator | je 0 Eintraege |
| Binaergroesse | 75 012 649 B (vorher 74 758 009 B, **+249 KB**) |

Der Zuwachs faellt so klein aus, weil der HTTP-Stack ausgeschlossen ist und die
beiden Kataloge zusammen nur rund 94 KB wiegen.

**Noch nicht geprueft:** ein Lauf der fertigen EXE. Sie registriert globale
Hotkeys und beansprucht den Single-Instance-Mutex; das gehoert beaufsichtigt
gestartet, nicht nebenbei.

**Testsuite:** 399 gruen (Ausgangswert 396). **Hardware-Smoke auf echtem
ReSpeaker:** alle 13 Zustaende und Meldungen, sauberes Beenden, keine Ausfaelle.

**Was der Hardware-Smoke gefunden hat.** `emit_event(duration_ms=…)` ist in LEFX
eine *Uebersteuerung*, die nur Effekte annehmen, die sie ausdruecklich anbieten.
Die Meldungseffekte des Smartspeaker-Sets fuehren ihre Dauer stattdessen als
*Parameter*. Zwei gleich benannte Dinge mit verschiedener Bedeutung — die
Mapping-Referenz schreibt die Dauer jetzt nach `config: {duration_ms: …}`.
Gefunden wurde das nur, weil der Smoke auf echter Hardware lief; die
Startpruefung sieht es nicht, weil das Ziel sehr wohl aufloest.

### M3 — Schema 2
- `core/feedback_mapping.py` neu: Verben statt `LedEffectId`, Liste erlaubt,
  Strukturvalidierung ohne Parametersemantik
- `schema_version: 1` wird **abgelehnt** mit klarer Fehlermeldung und Verweis
  auf die Migration (es gibt keine automatische Migration — der Wertevorrat
  ist ein anderer)
- `tests/test_feedback_mapping.py` neu

**Abnahme:** Schema-Tests grün; jedes Verb hat Positiv- und Negativfall.

### M4 — Mapping-Referenz und `config.yaml`
Abschnitt 6 in `config.yaml` überführen, offene Detailfragen entscheiden,
Zielnamen gegen den echten Katalog verifizieren.

**Abnahme:** Jede der 30 Regeln löst gegen `core`+`smartspeaker` auf; keine
Mehrdeutigkeit ungelöst.

### M5 — `LedController`-Port und In-Process-Implementierung
```python
class LedController(Protocol):          # die schmale Naht
    def set_state(...) -> None: ...
    def clear_state(...) -> None: ...
    def emit_event(...) -> None: ...
    def set_output(...) -> None: ...
    def resolve(target: str) -> None: ...   # für die Startprüfung
    def close(self) -> None: ...
```
- `InProcessLedController` baut `ControllerService(sink=<Objekt>, led_count=RING_LED_COUNT,
  fps=..., search_paths=[...], state_file=<Client-Zustand>, autostart_providers=False)`
- Katalog **eager**, Renderschleife und USB **lazy**
- Einmalig `set_output(brightness=...)`
- `add_listener` → `sink_changed(available=False)` in denselben `on_failure`-Pfad
  mit derselben Entprellung
- Jede LEFX-Ausnahme wird zu `OSError` normalisiert

**Abnahme:** Unit-Tests gegen einen Fake-Service; Integrationstest mit `sink="null"`.

### M6 — `LedFeedback` umbauen
Queue statt Slot (B7), Impuls-/Wiederherstellungslogik raus, Replay-Schutz
an `emit_event` geknüpft, drei Adapter raus, Fehler-Entprellung bleibt.

**Abnahme:** Kein Event geht unter Last verloren; States werden zusammengefasst;
Replay setzt kein Event.

### M7 — Konfiguration und Startprüfung
- `LedConfig` neu: `enabled`, `sink` (`respeaker`\|`simulator`\|`null`), `fps`,
  `brightness`, `shutdown_timeout`, `simulation_offer_after_s`,
  `usb_timeout_ms`, `effect_paths`
- `effect_paths: list[str]` — zusätzliche Ordner für die Effektsuche (B4).
  Validierung: Liste von Zeichenketten; nicht existierende Ordner sind eine
  **Warnung**, kein Startfehler, weil ein Wechseldatenträger legitim fehlen darf.
  Wird zusammen mit dem gebündelten Archivverzeichnis an `search_paths` gereicht
- Startprüfung als Gate nach Abschnitt 2 — Konfigurationsfehler brechen ab,
  Hardwarelage nie
- `apply_runtime_config`: Kandidat vollständig prüfen **vor** dem Setzen; bei
  Fehler bleibt die letzte gültige Konfiguration unangetastet
- `core/settings_metadata.py` nachziehen

**Abnahme:** Unbekanntes Ziel → Start bricht ab mit lesbarer Meldung.
Kein Gerät → Start läuft. Ungültige Laufzeitkonfiguration → alte bleibt aktiv.

### M8 — Selbstheilung und Simulationsangebot
Nach Abschnitt 8: Schwelle, Tray-Benachrichtigung, Menüeintrag, Umschaltung
durch Neuaufbau, Rückweg.

**Abnahme:** Kabel ziehen → Angebot nach Schwelle → Umschaltung → Ringfenster
zeigt an → zurück auf Hardware ohne Neustart.

### M9 — Packaging und Abnahme
- `voice-stt-client.spec`: `.lefxset`-Archive rein, libusb-Reste raus
- **Onefile-Smoke ohne venv:** Start, Katalog da, Effekt sichtbar, sauber beendet
- Hardware-Smoke: alle Zustände aus Abschnitt 6, plus `success_event → listening → off`
- Kabel ziehen/stecken: `sink_changed` kommt, genau **ein** `client.led.unavailable`,
  automatische Rückkehr
- Langlauf ≥ 2 h Leerlauf: CPU, Handles, Speicher
- Binärgröße vorher/nachher
- ADR-004 finalisieren, Roadmap und Projektübersicht fortschreiben

---

## 11. Testmatrix

| Ebene | Was | Ohne Hardware |
|---|---|---|
| Unit | Schema 2: Verben, Liste, genau ein Verb, Ablehnung von `schema_version: 1` | ✅ |
| Unit | `LedConfig` inkl. Sink-Auswahl | ✅ |
| Unit | Queue: Event geht nie verloren, State wird zusammengefasst | ✅ |
| Integration | Alle 30 Regeln lösen gegen `core`+`smartspeaker` auf | ✅ |
| Integration | Startprüfung: Konfigurationsfehler bricht ab, fehlende Hardware nicht | ✅ |
| Integration | Laufzeitkonfiguration ungültig → alte bleibt aktiv | ✅ |
| Integration | Replay setzt kein Event (ADR-003) | ✅ (Bestand) |
| Integration | `sink_changed(available=False)` → genau ein `client.led.unavailable` | ✅ |
| Visuell | Simulator-Sink, alle Regeln durchspielen | ✅ Simulatorpaket |
| Hardware | Vollständiger Diktierablauf am Ring | ❌ |
| Hardware | Kabel ziehen/stecken, Selbstheilung, Simulationsangebot | ❌ |
| Build | Onefile ohne venv | ❌ |

---

## 12. Risiken

| Risiko | Eintritt | Wirkung | Gegenmaßnahme |
|---|---|---|---|
| Onefile findet Katalog nicht (B4) | **hoch**, wenn nur im venv getestet | Feature im Release tot | M9 ohne venv, Sink direkt instanziieren |
| UI-Freeze durch USB (B1/B2) | mittel | Anwendung wirkt hängend | Nur Worker-Thread; Timeout upstream senken |
| Upstream-Release verzögert sich | mittel | M2 blockiert | M0/M3/M4 laufen parallel, sie brauchen kein Release |
| Hängender USB-Aufruf ohne Not-Aus (B3) | niedrig–mittel | LED tot bis Neustart | Timeout, Watchdog, ADR-004 |
| Binärgröße (B5) | mittel nach Upstream-Fix | Release größer | messen und ausweisen |
| Namenskollision `core` ↔ `smartspeaker` | niedrig | Start bricht ab | Startprüfung deckt es sofort auf; `source::id` |

---

## 13. Nicht vorgesehen

- Keine Änderung an Reducer, Normalizer, Eventprotokoll, Cursor-Speicher
- Kein HTTP: eingebettet, **kein** `lefx serve`, kein Port, keine Instanzdatei
- Keine Overlays und keine Live-Datenflüsse (Folgepaket, Abschnitt 9)
- Kein DoA im Client (`autostart_providers=False`)
- Keine automatische Migration von `schema_version: 1`
- Kein Code-Rename der Client-Bezeichner (`CanonicalEventType` bleibt)
- Kein Eingriff in die USB-Verbindung des LED-Teils außerhalb von LEFX
- Simulator nicht im Release-Build
