> [!WARNING]
> Dieses Dokument ist ein archivierter früher Planungsstand.
> Es ist nicht mehr verbindlich und darf nicht als Implementierungsgrundlage verwendet werden.
> Maßgeblich ist `docs/IMPLEMENTATION_ROADMAP.md`.


# RealtimeSTT Windows Desktop Client – Architekturplan

## Zusammenfassung

Ein Windows-Desktop-Client, der dauerhaft im Hintergrund läuft, sich per WebSocket mit dem STT-Server (`wss://stt.voice.marcosudau.com/ws/transcribe`) verbindet, Mikrofon-Audio streamt und den erkannten Text in die aktuell fokussierte Anwendung am Textcursor einfügt.

---

## Deine Ideen – Meine Einschätzung

Dein Instinkt ist genau richtig. Ich stimme mit deiner Richtung voll überein und möchte sie an einigen Stellen konkretisieren:

### ✅ „Erst den rohen funktionierenden Kern"
Absolut der richtige Ansatz. Gerade bei einem Dauerläufer, der „bei Wind und Wetter funktionieren" soll, ist ein dünner, testbarer Core das Fundament. Die Server-Doku liefert uns ein sauberes Protokoll mit klarem Zustandsmodell – das können wir 1:1 in eine Core-Library übersetzen, die **null UI-Abhängigkeiten** hat.

### ✅ „PySide6 als Tray-App ohne MainWindow"
Guter Ansatz. PySide6 hat sich als Tray-Backend unter Windows bewährt, ist stabil und hat einen relativ kleinen Footprint. Und ohne MainWindow wird es schlank. Aber: PySide6 zieht **~150 MB** an Dependencies und ist für eine reine Tray-App + Overlay aus meiner Sicht overkill. Dazu gleich mehr als Alternative.

### ⚠️ „Kleines Overlay für Feedback"
Hier wird es architektonisch spannend. Ein natives Overlay, das über allen Fenstern schwebt, **ohne** den Fokus zu stehlen, ist machbar – aber der Teufel steckt im Detail (DPI-Awareness, Multi-Monitor, Always-on-Top ohne Fokus). Dazu habe ich einen konkreteren Vorschlag unten.

### ⚠️ „Helper-Service im Admin-Modus für Text-Einfügen"
Das ist tatsächlich der Knackpunkt, den du richtig identifiziert hast. Aber die gute Nachricht: **Ein Admin-Service ist in den meisten Fällen nicht nötig.** Dazu gleich eine detaillierte Analyse.

---

## Die Texteingabe-Herausforderung – Detailanalyse

Dies ist das technisch komplexeste Problem und verdient eine gründliche Betrachtung.

### Welche Methoden gibt es?

| Methode | Wie es funktioniert | Vorteile | Nachteile |
| --- | --- | --- | --- |
| **`SendInput` / `keybd_event`** | Simuliert echte Tastatureingaben auf OS-Ebene | Funktioniert in 95% aller Apps; kein Admin nötig; wird als „echte" Eingabe erkannt | Langsam bei langen Texten; Sonderzeichen/Unicode brauchen Sonderbehandlung; UIPI blockiert bei Admin-Fenstern |
| **Clipboard + `Ctrl+V`** | Text in Zwischenablage → simuliertes Paste | Schnell auch für lange Texte; Unicode-sicher | Überschreibt Clipboard; einige Apps verarbeiten Paste anders; muss altes Clipboard sichern/wiederherstellen |
| **UI Automation** | Windows UI Automation API, um direkt auf TextPattern/ValuePattern zuzugreifen | Sauber; respektiert Applikationsstruktur | Nicht alle Apps exponieren IValueProvider; langsam; inkonsistente Unterstützung |
| **Windows-Service + Named Pipe** | Separater Service mit SYSTEM-Rechten injiziert über SendInput auch in elevated Windows | Überwindet UIPI komplett | Komplexität; Installationsaufwand; Service muss gepflegt werden |

### Mein Vorschlag: Hybrid-Ansatz (kein Admin-Service nötig)

```
┌─────────────────────────────────────────────────┐
│              TextInjector                       │
│                                                 │
│  1. Versuch: SendInput (Zeichen-für-Zeichen)    │
│     → für streaming realtime-Text ideal         │
│     → funktioniert in ~95% aller Fenster        │
│                                                 │
│  2. Für final-Text: Clipboard-Paste             │
│     → schneller für den ganzen Satz             │
│     → Clipboard sichern → einfügen → restore    │
│                                                 │
│  3. Fallback-Erkennung:                         │
│     → Prüfe ob Zielfenster elevated ist         │
│     → Wenn ja: Warnung loggen + Notification    │
│     → Kein stiller Fehler                       │
└─────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **UIPI (User Interface Privilege Isolation)** blockiert `SendInput` nur dann, wenn das Zielfenster mit höheren Rechten läuft (z.B. ein als Admin gestartetes CMD oder eine Admin-IDE). Das betrifft im normalen Desktop-Alltag **sehr wenige** Fenster. Ein Admin-Helper-Service wäre eine Phase-2-Optimierung, aber kein Blocker für ein funktionierendes Produkt.

### Realtime vs. Final – zwei verschiedene Einfüge-Strategien

Das ist ein Punkt, der aus der Server-Doku direkt hervorgeht und den wir architektonisch berücksichtigen müssen:

```
Server sendet:  realtime(segmentId=1, text="Hallo W")     ← revidierbarer Zwischentext
                realtime(segmentId=1, text="Hallo Welt")   ← ersetzt vorigen komplett  
                final(segmentId=1, text="Hallo Welt!")     ← endgültig
```

Zwei Optionen für Realtime-Text:

**Option A – „Nur Final einfügen" (empfohlen für Phase 1):**
- Realtime-Text wird **nur im Overlay** angezeigt
- Erst bei `final` wird der Text per Clipboard-Paste oder SendInput ins Zielfenster eingefügt
- Einfacher, robuster, kein Rückgängig-Problem

**Option B – „Live-Tippen mit Korrektur":**
- Realtime-Text wird zeichenweise getippt
- Bei Revision: alte Zeichen mit Backspace löschen, neue tippen
- Beeindruckend, aber fragil (was wenn der User währenddessen tippt oder klickt?)

> [!NOTE]
> **Meine klare Empfehlung: Option A für den Start.** Das Overlay zeigt den Zwischentext live, der finale Text wird dann sauber eingefügt. Das ist zuverlässig und deckt den Hauptanwendungsfall ab. Option B kann später als „Premium-Feature" optional hinzugefügt werden.

---

## Vorgeschlagene Architektur

### Schichtenmodell

```
┌───────────────────────────────────────────────────────┐
│                    Tray-Shell (UI-Host)                │
│  System Tray Icon · Kontextmenü · Overlay-Fenster     │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│  pystray + Pillow (Tray)                              │
│  tkinter (Overlay – stdlib, kein Install)             │
├───────────────────────────────────────────────────────┤
│                   Controller / App                    │
│  Startet/stoppt Core · reagiert auf UI-Events         │
│  Verbindet Core-Callbacks mit UI-Updates              │
├───────────────────────────────────────────────────────┤
│                    Core (Blackbox)                     │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ STTSession   │ │ AudioCapture │ │ TextInjector   │  │
│  │ WS-Protokoll │ │ Mikrofon     │ │ SendInput/     │  │
│  │ Reducer      │ │ PCM-Stream   │ │ Clipboard      │  │
│  │ Reconnect    │ │ Resampling   │ │ Ziel-Erkennung │  │
│  └─────────────┘ └──────────────┘ └────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Shared: Config · Logging · Events       │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

### Warum pystray + tkinter statt PySide6?

| Kriterium | PySide6 | pystray + tkinter |
| --- | --- | --- |
| Installationsgröße | ~150 MB | pystray: ~50 KB, Pillow: ~5 MB, tkinter: stdlib |
| Tray-Unterstützung | `QSystemTrayIcon` – solide | pystray – etabliert, genau dafür gebaut |
| Overlay-Fenster | QWidget (frameless, transparent) | tkinter Toplevel (overrideredirect, transparent) |
| Event-Loop-Modell | Qt Event Loop (eigener Thread oder Main) | pystray in eigenem Thread, tkinter hat eigenen Mainloop |
| Lernkurve/Wartung | höher, viel API-Fläche | minimal, wenige hundert Zeilen |
| Zukunftsfähig für mehr UI? | ja, aber dann echtes Fenster | für Tray + Overlay mehr als genug |

> [!TIP]
> tkinter ist in der CPython-Standardbibliothek enthalten. Für ein rahmenloses, transparentes Overlay-Fenster reicht es vollkommen aus, und wir sparen uns eine ~150 MB schwere Qt-Distribution. Wenn wir später mal ein volles Settings-Fenster brauchen, können wir immer noch PySide6 einführen – oder ein Web-basiertes Settings-UI per localhost öffnen.

### Warum nicht direkt PySide6?

PySide6 wäre nicht *falsch*, aber für das, was wir brauchen (Tray-Icon + Floating-Overlay), ist es wie mit Kanonen auf Spatzen zu schießen. Du hast ja selbst gesagt: Abhängigkeiten gering halten. pystray + tkinter gibt uns genau das.

> [!NOTE]
> Wenn du trotzdem PySide6 bevorzugst – zum Beispiel weil du es schon kennst oder perspektivisch mehr UI planst – bin ich damit auch einverstanden. Die Core-Architektur bleibt identisch, nur die UI-Shell ändert sich.

---

## Detaillierter Komponentenplan

### 1. Core-Schicht (`core/`)

Rein Python, keine UI-Dependencies. Testbar ohne Display.

#### `core/stt_session.py` – WebSocket-Protokoll & Zustandsmodell

- WebSocket-Client (via `websockets` Library)
- Implementiert den Handshake: `connect → hello → ready → start`
- Event-Reducer nach dem Muster aus [05-client-zustandsmodell.md](file:///p:/DockerProjekte/RealtimeSTT_client/server-docs-for-client-development/05-client-zustandsmodell.md)
- Zwei getrennte Automaten: Transport + Session/Recorder
- Reconnect-Automat mit exponentiellem Backoff + Jitter
- Ping/Pong-Health-Monitoring
- Callback-basierte Schnittstelle nach oben (Events wie `on_realtime`, `on_final`, `on_status_change`, `on_error`)

#### `core/audio_capture.py` – Mikrofon-Zugriff & PCM-Stream

- Audio-Capture über `sounddevice` (PortAudio-Binding, ~2 MB)
- Mono, konfigurierbare Samplerate (bevorzugt 16 kHz direkt, Fallback mit Resampling)
- Binäres Audiopaket gemäß Serverprotokoll: `4 Byte Length + JSON-Metadata + PCM s16le`
- Paketierung in ~40ms Chunks (Referenz aus Browserclient)
- Geräte-Enumeration und Hot-Swap-Erkennung
- Robustes Error-Handling bei Geräteverlust

#### `core/text_injector.py` – Text in Zielanwendung einfügen

- `SendInput`-basierte Zeicheneingabe über `ctypes` (Win32 API, keine Dependency)
- Clipboard-basiertes Paste für finale Texte (mit Backup/Restore)
- Erkennung des Zielfensters (Foreground Window + elevated Check via `ctypes`)
- UIPI-Warnung wenn Zielfenster elevated ist
- Konfigurierbare Strategie: "nur final", "nur clipboard", "sendkeys"

#### `core/config.py` – Konfiguration

- YAML oder TOML-basierte Konfigurationsdatei
- Server-URL, Geräte-ID, Hotkeys, Einfüge-Modus, Log-Level
- Sinnvolle Defaults für alles

#### `core/logging_setup.py` – Strukturiertes Logging

- Rotating File Log + optionaler Stdout
- Strukturiertes Format (JSON Lines) für Maschinenlesbarkeit
- Separate Kanäle: `connection`, `audio`, `text`, `app`
- Log-Level pro Kanal konfigurierbar

---

### 2. UI-Shell (`ui/`)

#### `ui/tray.py` – System Tray

- pystray-basiertes Tray-Icon
- Kontextmenü: Start/Stop · Mute · Status · Logs öffnen · Beenden
- Icon-Zustandswechsel (Farbe/Symbol) je nach Status:
  - 🔴 Disconnected
  - 🟡 Connecting / Wakeword Wait
  - 🟢 Ready / Listening
  - 🔵 Recording / Transcribing
  - ⚪ Muted

#### `ui/overlay.py` – Floating-Feedback-Overlay

- tkinter Toplevel-Fenster: frameless, transparent, always-on-top, click-through
- Zeigt Realtime-Text als Live-Feedback
- Position: konfigurierbar (unten-mitte, oben-rechts, etc.)
- Fade-in/Fade-out-Animationen
- Auto-Hide nach Final
- DPI-aware

---

### 3. Controller / App (`app.py`)

- Main Entry Point
- Erstellt und verbindet Core-Komponenten mit UI
- Globaler Hotkey (z.B. `Ctrl+Shift+Space`) zum Aktivieren/Deaktivieren über `pynput` oder `keyboard`
- Graceful Shutdown (SIGTERM, Tray-Quit)
- Single-Instance-Guard (Mutex)

---

## Dependency-Budget

| Paket | Zweck | Größe |
| --- | --- | --- |
| `websockets` | WebSocket-Client | ~300 KB |
| `sounddevice` | Mikrofon-Zugriff (PortAudio) | ~2 MB |
| `numpy` | Audio-Buffer/Resampling | ~15 MB (oft schon vorhanden) |
| `pystray` | System Tray | ~50 KB |
| `Pillow` | Icon-Erzeugung für pystray | ~5 MB |
| `pynput` | Globale Hotkeys | ~200 KB |
| `pyyaml` | Konfigurationsdatei | ~600 KB |
| **tkinter** | **Overlay (stdlib)** | **0 – im Python enthalten** |
| **ctypes** | **Win32 API (stdlib)** | **0 – im Python enthalten** |

**Gesamt: ~23 MB** (vs. ~170 MB+ mit PySide6)

---

## Projektstruktur

```
RealtimeSTT_client/
├── app.py                          # Entry Point
├── config.yaml                     # User-Konfiguration
├── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── stt_session.py              # WebSocket + Protokoll + Reducer
│   ├── audio_capture.py            # Mikrofon + PCM-Paketierung
│   ├── text_injector.py            # SendInput / Clipboard
│   ├── config.py                   # Konfigurationsmodell
│   └── logging_setup.py            # Strukturiertes Logging
│
├── ui/
│   ├── __init__.py
│   ├── tray.py                     # System Tray (pystray)
│   └── overlay.py                  # Floating Overlay (tkinter)
│
├── server-docs-for-client-development/  # Deine Doku (bleibt)
│   └── ...
│
└── tests/
    ├── test_stt_session.py
    ├── test_audio_capture.py
    └── test_text_injector.py
```

---

## Phasenplan

### Phase 1 – Laufender Kern (Ziel: funktioniert headless)
1. `core/config.py` + `core/logging_setup.py`
2. `core/stt_session.py` – WebSocket-Verbindung, Handshake, Reducer, Reconnect
3. `core/audio_capture.py` – Mikrofon-Stream, Paketierung
4. Integration: Audio → WebSocket → Events empfangen → Console-Logging
5. **Meilenstein:** Text wird in der Konsole angezeigt

### Phase 2 – Texteinfügung
6. `core/text_injector.py` – SendInput + Clipboard-Paste
7. Integration mit `final`-Events
8. **Meilenstein:** Diktierter Text erscheint im Notepad

### Phase 3 – UI-Shell
9. `ui/tray.py` – Tray-Icon mit Status und Menü
10. `ui/overlay.py` – Realtime-Feedback
11. `app.py` – Hotkey, Single-Instance, Graceful Shutdown
12. **Meilenstein:** Kompletter Client mit Tray + Overlay

### Phase 4 – Härtung & Polish
13. Reconnect-Stresstests
14. Multi-Monitor / DPI-Handling
15. Autostart-Registry-Eintrag
16. Logging-Review und Error-Reporting

---

## Open Questions

> [!IMPORTANT]
> **1. Texteinfüge-Strategie:** Soll Phase 1 nur `final`-Text einfügen (meine Empfehlung)? Oder soll auch Realtime-Text live ins Zielfenster getippt werden?

> [!IMPORTANT]
> **2. UI-Toolkit:** Bist du mit pystray + tkinter einverstanden? Oder bevorzugst du PySide6 aus bestimmten Gründen?

> [!IMPORTANT]
> **3. Hotkey-Modell:** Wie soll die Aktivierung funktionieren?
> - **Push-to-Talk:** Taste gedrückt halten → Audio wird gestreamt, loslassen → stop
> - **Toggle:** Einmal drücken → an, nochmal → aus
> - **Always-on:** Immer aktiv, Wake-Word (`hey_jarvis`) aktiviert die Erkennung
> - Eine Kombination? (z.B. Always-on mit Wake-Word als Default, aber Hotkey als Override)

> [!IMPORTANT]
> **4. Server-URL:** Ist `wss://stt.voice.marcosudau.com/ws/transcribe` die einzige Ziel-URL, oder soll der Client auch gegen localhost/andere Server konfigurierbar sein?

> [!IMPORTANT]
> **5. Python-Version:** Welche Python-Version nutzt du auf deinem Windows-System? (Minimum wäre 3.10 für moderne async-Features)

---

## Verification Plan

### Automatisierte Tests
- Unit-Tests für den Event-Reducer (`test_stt_session.py`)
- Unit-Tests für Audio-Paketierung (`test_audio_capture.py`)
- Unit-Tests für Text-Injection-Strategien (`test_text_injector.py`)
- Integration-Test gegen den echten Server (WebSocket connect → hello → ready)

### Manuelle Verifikation
- Mikrofon-Aufnahme → Text in Konsole (Phase 1)
- Text-Einfügung in Notepad, VS Code, Browser (Phase 2)
- Tray-Icon Statuswechsel, Overlay-Anzeige (Phase 3)
- Reconnect bei Netzwerkverlust, Server-Neustart (Phase 4)
- Dauerlauf über mehrere Stunden (Phase 4)
