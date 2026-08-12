# Feedback konfigurieren — praktische Rezepte

Alles Sichtbare und Hörbare am Client wird in `config.yaml` entschieden, nicht im
Code. Dieser Guide zeigt an konkreten Aufgaben, wie.

Wie es intern zusammenhängt, steht in [feedback_system.md](feedback_system.md).

---

## Der schnellste Weg: was gibt es überhaupt?

Bevor du einen Effektnamen in die Konfiguration schreibst, lass dir zeigen, was
installiert ist:

```bash
venv\Scripts\python.exe -c "from lefx.interfaces import ControllerService; s=ControllerService(sink=None, autostart_providers=False); print('\n'.join(sorted(s.list_definitions())))"
```

Und die fertigen Presets:

```bash
venv\Scripts\python.exe -c "from lefx.interfaces import ControllerService; s=ControllerService(sink=None, autostart_providers=False); print('\n'.join(sorted(s.list_presets())))"
```

Beschreibungen aller Effekte samt Parametern stehen in den Katalogen des
LED-Controllers (`core_effects.md`, `smartspeaker_effects.md`).

**Du musst nichts auswendig wissen:** Nennt eine Regel einen Namen, den es nicht
gibt, startet der Client nicht und sagt beim Start, welche Namen falsch sind.

---

## Aufbau einer Regel

```yaml
feedback_mappings:
  schema_version: 2
  events:
    server.recording.started:      # welches Ereignis
      led: {set_state: listening}  # was der Ring tut
      sound: {cue: start}          # was zu hören ist
      app: {action: indicator.recording}   # was die Anwendung zeigt
```

Alle drei Zeilen sind optional. `client.event_stream.live: {}` ist ein bewusst
wirkungsloses Ereignis — bekannt, aber ohne Anzeige.

> **`schema_version: 2` ist nicht die LEFX-Version.** In diesem Projekt laufen
> mehrere Zahlen nebeneinander, die alle „Version" heißen und nichts miteinander
> zu tun haben:
>
> | Zahl | Versioniert | Stand |
> | --- | --- | --- |
> | `feedback_mappings.schema_version` | **diesen** Konfigurationsabschnitt | **2** |
> | `led-controller-version-3` | das Effektsystem (Paketversion 3.0.x) | **V3** |
> | `background_state.json` | LEFX' eigener Zustandsspeicher | 3 |
> | `set.yaml` `version` | das Format eines Effektpakets | 1 |
>
> Hier gilt nur die erste. Sie stand auf 1, solange der Client zehn feste
> LED-Wirkungen kannte, und steht auf 2, seit er LEFX-Verben spricht. Eine 3
> gibt es für diesen Abschnitt nicht.

Es gibt **30 Ereignisse**. Die vollständige Liste steht in `config.yaml`; sie
teilt sich in `server.*` (was der Server meldet) und `client.*` (was die
Anwendung selbst feststellt).

---

## LED: die vier Verben

Ein Aufruf nennt **genau ein** Verb. Der Wert des Verbs ist sein Hauptargument.

```yaml
led: {set_state: listening}                      # Zustand setzen
led: {clear_state: primary}                      # Zustand räumen
led: {emit_event: success_event}                 # einmalige Meldung
led: {set_output: {brightness: 0.4}}             # Helligkeit / Stummschaltung
```

### Rezept: Effekt anders einfärben

```yaml
server.recording.started:
  led: {set_state: listening, config: {color: "#FF00AA"}}
```

`config` reicht Parameter unverändert an den Effekt weiter. Welche er kennt,
entscheidet der Katalog — der Client prüft das nicht nach, damit er nicht
veraltet, sobald ein Effektpaket aktualisiert wird. Ein unbekannter Parameter
wird beim Anzeigen abgelehnt und einmal protokolliert.

### Rezept: fertiges Preset statt eigener Werte

```yaml
server.recording.started:
  led: {set_state: listening_calm_cyan}
```

Presets liegen im selben Namensraum wie Effekte. Das ist der bequemste Weg:
nichts konfigurieren zu müssen, aber alles zu können.

### Rezept: aufblitzen **und** danach in einen Zustand wechseln

Zwei Aufrufe als Liste, in dieser Reihenfolge:

```yaml
server.wakeword.detected:
  led: [{emit_event: wakeword_detected}, {set_state: waiting}]
```

Genau dafür gibt es die Liste — ein Wake-Word blitzt auf und der Ring bleibt
danach in einem anderen Zustand stehen.

### Rezept: Dauer einer Meldung ändern

```yaml
server.transcription.completed:
  led: [{emit_event: success_event, config: {duration_ms: 1500}}, {set_state: ready_state}]
```

**Achtung, eine Stolperstelle:** Die Dauer gehört in `config`. Das
Geschwisterfeld `duration_ms` ist eine *Übersteuerung*, die nur Effekte annehmen,
die sie ausdrücklich anbieten — die Meldungseffekte des `smartspeaker-set` tun
das nicht und lehnen sie ab.

### Rezept: dauerhafter Hintergrund unter allem

```yaml
client.lifecycle.started:
  led: [{set_state: solid_fill, slot: background, config: {color: "#050510", brightness: 0.2}}]
```

Der `background`-Slot liegt unter dem `primary`-Slot und überlebt einen Neustart —
LEFX stellt ihn wieder her.

### Rezept: Ring bei Programmende dunkel

```yaml
client.lifecycle.stopping:
  led: {clear_state: primary}
```

---

## Sound: acht Anlässe

Erst die Dateien hinterlegen, dann in Regeln benutzen:

```yaml
feedback:
  sounds_enabled: true
  wake_word_sound: C:\Sounds\wake.wav
  start_sound: C:\Sounds\start.wav
  stop_sound: C:\Sounds\stop.wav
  complete_sound: C:\Sounds\done.wav
  cancel_sound: null           # nicht gesetzt = still
  warning_sound: C:\Sounds\warn.wav
  error_sound: C:\Sounds\error.wav
  timeout_tick_sound: C:\Sounds\tick.wav
```

```yaml
server.transcription.completed:
  sound: {cue: complete, volume: 0.6}
```

`volume` gilt pro Regel, nicht pro Datei — derselbe Ton darf bei einer
Bestätigung leiser sein als bei einem Fehler. Ein nicht gesetzter Cue ist still,
eine fehlende Datei wird einmal gemeldet und bricht nichts ab.

Die ausgelieferte Diagnosekonfiguration verwendet relative Pfade unter
`assets/feedback_sounds/debug/`. Sie werden in der Sourcekopie und im
PyInstaller-Onefile-Build gegen den stabilen Anwendungsroot aufgelöst. Der Cue
`timeout_tick` unterstützt zusätzlich `action: stop`, damit neue Sprache oder
eine Verlängerung ein laufendes Ticken sofort beendet.

```yaml
client.dictation.timeout_warning:
  led: {set_overlay: countdown_ring, config: {duration_ms: 3000}}
  sound: {cue: timeout_tick, volume: 0.85}
client.dictation.timeout_warning_cleared:
  sound: {cue: timeout_tick, action: stop}
```

---

## In-App: acht Indikatoren

```yaml
server.recording.started:
  app: {action: indicator.recording}
```

| Aktion | Wirkung |
| --- | --- |
| `indicator.idle` | Grundzustand, Text je nach Betriebsmodus |
| `indicator.waiting_for_wake_word` | wartet auf das Aktivierungswort |
| `indicator.waiting_for_speech` | wartet auf Sprache, weiße Umrandung |
| `indicator.recording` | nimmt auf, Signalfarbe |
| `indicator.finalizing` | transkribiert |
| `indicator.success` | grün, 900 ms, danach zurück |
| `indicator.warning` | gelb, 1200 ms, danach zurück |
| `indicator.error` | rot, 1400 ms, danach zurück |

Die Farbe hängt zusätzlich am Betriebsmodus (`session.mode`): blau im
Wake-Word-Modus, grün im Hotkey-Modus. Das ist Absicht — man soll auf einen Blick
sehen, in welchem Modus der Client läuft.

---

## Der LED-Abschnitt

```yaml
led:
  enabled: true
  sink: respeaker         # respeaker | simulator | null
  fps: 30.0
  brightness: 192         # 0..255; auffällige Diagnoseeinstellung
  usb_timeout_ms: 1000
  shutdown_timeout: 1.5
  effect_paths: []
  simulation_offer_after_s: 120.0
```

### Ohne Hardware arbeiten

```yaml
led:
  sink: simulator
```

Dann in einem zweiten Fenster:

```bash
venv\Scripts\lefx-simulator.exe
```

Das Ringfenster zeigt dieselben Bilder wie die Hardware. Nützlich, um ein Mapping
zu bauen, ohne ein Gerät zur Hand zu haben. Läuft der Ring über zwei Minuten ins
Leere, bietet der Client die Umschaltung von selbst im Tray an.

### Eigene Effektpakete einbinden

```yaml
led:
  effect_paths:
    - C:\Effekte\eigene
    - D:\Gemeinsam\lefxsets
```

Ergänzt die mitgelieferten Kataloge, ersetzt sie nicht. Ein Ordner, der nicht da
ist, ist eine Warnung und kein Startfehler — ein Wechseldatenträger darf fehlen.

### Ring dunkler stellen

`brightness` ist ein globaler Faktor über alles. Für einen einzelnen Effekt
nimmt man stattdessen dessen eigenen Parameter:

```yaml
led: {set_state: listening, config: {brightness: 0.3}}
```

---

## Umgang mit Fehlern

**Der Client startet nicht und nennt Effektnamen.** Ein Name in
`feedback_mappings` steht in keinem geladenen Katalog. Tippfehler prüfen oder
`led.effect_paths` auf das Paket zeigen lassen, das ihn mitbringt. Absicht: Ein
Fehler in der Konfiguration soll auffallen, bevor er mitten im Diktat auffällt.

**Der Client startet, aber der Ring bleibt dunkel.** Kein Konfigurationsfehler —
das Gerät ist nicht erreichbar. Im Tray steht eine Meldung, LEFX verbindet
selbstständig weiter, und nach zwei Minuten wird der Simulator angeboten. Manuell
geht es über *Neu verbinden ▸ ReSpeaker*.

**Ein Effekt zeigt nichts, obwohl der Name stimmt.** Meist ein Parameter, den
dieser Effekt nicht kennt. Das Protokoll nennt ihn beim Namen.

**Es ist nichts zu hören.** `feedback.sounds_enabled` steht auf `false`, oder der
Cue hat keinen Pfad.

**Änderungen an `config.yaml` greifen nicht.** Es gibt eine Benutzerüberlagerung
unter `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml`, die über der Projektdatei
liegt. Enthält sie einen unbekannten Schlüssel, wird sie **komplett** verworfen
und das steht im Protokoll.

---

## Was noch nicht geht

**Overlays** — Fortschrittsringe, Pegelanzeigen, Richtungsanzeige. Die Verben
gibt es im Katalog, aber sie brauchen laufende Eingangsdaten, und dieser Datenweg
ist bewusst ein eigenes Folgepaket statt einer schnellen Ergänzung.

**Stummschalten per Software ohne ReSpeaker** — ohne Gerät gibt es keine
Mute-LED. Der Client schaltet trotzdem stumm und sagt im Menü „nur Client".
