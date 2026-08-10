# Das Feedbacksystem — wie es aufgebaut ist

Der Client sagt seinem Benutzer auf drei Wegen, was gerade passiert: über den
**LED-Ring** des ReSpeaker, über **Töne** und über die **Anwendung selbst** (Tray
und Overlay). Dieser Guide erklärt, wie diese drei zusammenhängen, wo entschieden
wird was gezeigt wird, und was davon durch Tests abgesichert ist.

Wer nur konfigurieren will, ist mit
[feedback_konfigurieren.md](feedback_konfigurieren.md) schneller bedient.

---

## 1. Der Weg vom Ereignis zur Anzeige

```
Serverereignisse ──┐
lokale Ereignisse ─┼─► Normalizer ──► Reducer ──► Regel ──┬─► LED   (LEFX V3)
STT-Fallback ──────┘        │            │               ├─► Sound (Qt)
                            │            │               └─► In-App (Tray/Overlay)
                     Kanonisches      eine
                      Vokabular    Entscheidung
```

Fünf Stationen, jede mit einer Aufgabe:

**Quellen.** Fakten kommen aus drei Richtungen: dem Ereignisstrom des Servers,
dem STT-Transport als Rückfallebene, und der Anwendung selbst (Hotkey gedrückt,
Mikrofon verloren, Text eingefügt).

**Normalizer** (`core/event_normalizer.py`). Übersetzt alle drei in **ein**
Vokabular: 30 `CanonicalEventType`-Werte, sauber getrennt in `server.*` und
`client.*`. Ab hier weiß niemand mehr, woher ein Fakt kam.

**Reducer** (`core/feedback_reducer.py`). Entscheidet, was gelten soll. Er ist
deterministisch und kennt kein einziges Gerät. Hier wohnt die schwierige Logik:

- **Doppelte Fakten** aus zwei Quellen werden als einer erkannt.
- **Wiedergabe** (Replay) baut den Zustand wieder auf, ohne alte Meldungen
  erneut abzuspielen — was vorbei ist, wird nicht noch einmal angekündigt.
- **Der Wechsel auf „live"** stellt den authoritativen Zustand her, spielt aber
  keine Töne nach.
- **Lokale Störungen** (Mikrofon weg) überlagern den Serverzustand, ohne ihn zu
  löschen.

**Regel** (`core/feedback_mapping.py`). Die Übersetzung von „was gilt" nach „was
zeigen" — und zwar als Konfiguration, nicht als Code. Jedes Ereignis darf bis zu
drei Wirkungen haben: `led`, `sound`, `app`.

Dieser Abschnitt trägt `schema_version: 2`. Das ist die Version **des
Konfigurationsabschnitts** und hat nichts mit der Version des Effektsystems zu
tun, das darunter läuft — dort steht V3 (`led-controller-version-3` 3.0.x).
Beide Zahlen treffen in denselben Zeilen aufeinander und meinen Verschiedenes:
Schema 1 war der Stand mit zehn festen LED-Wirkungen, Schema 2 spricht
LEFX-Verben. Für diesen Abschnitt gibt es keine 3.

**Adapter.** Drei Empfänger, die nichts voneinander wissen und einander nicht
blockieren. Fällt einer aus, laufen die anderen weiter.

---

## 2. Die drei Kanäle

### LED — über LEFX V3

Der Ring wird nicht mehr direkt angesteuert. Der Client bettet den
**LEFX-V3-Controller** (`led-controller-version-3`) als Thread in seinen eigenen
Prozess ein und spricht mit ihm über einen schmalen Port mit sechs Verben
(`core/led_controller.py`).

Damit steht der komplette Katalog zur Verfügung: **36 Effekte und 71 Presets**
aus `core-set` und `smartspeaker-set`, in drei Lebenszyklusformen:

| Form | Was sie ist | Verb |
|---|---|---|
| **State** | dauerhafter Zustand in einem Slot | `set_state`, `clear_state` |
| **Event** | einmalige Meldung mit fester Dauer, höchste Priorität | `emit_event` |
| **Overlay** | überlagernde Anzeige mit laufenden Eingangsdaten | *(Folgepaket)* |

Zwei Regeln, die dabei nicht verhandelbar sind:

- **Nur ein Thread ruft LEFX auf.** Ein Befehl rendert im aufrufenden Thread, und
  ein Rendern kann auf einem USB-Transfer stehen. Aus dem Qt-Thread aufzurufen
  hieße, eine hängende Hardware in eine hängende Oberfläche zu übersetzen.
- **Zustände dürfen zusammengefasst werden, Meldungen nie.** Zwei Zustände für
  denselben Slot enden ohnehin beim zweiten; zwei Meldungen sind zwei Aussagen.

### Sound — sieben Cues

Sieben benannte Anlässe (`wake_word`, `start`, `stop`, `complete`, `cancel`,
`warning`, `error`), jeder mit einem konfigurierbaren Pfad zu einer Audiodatei
und einer Lautstärke pro Regel. Nicht gesetzte Cues sind still — das ist kein
Fehler, sondern die Voreinstellung.

Fehlt eine Datei oder scheitert die Wiedergabe, wird das **einmal je
Fehlerphase** gemeldet und das Diktat läuft weiter.

### In-App — acht Indikatoren

Acht Aktionen (`indicator.idle`, `.waiting_for_wake_word`, `.waiting_for_speech`,
`.recording`, `.finalizing`, `.success`, `.warning`, `.error`) steuern Trayfarbe,
Statustext und das Overlay.

Die Darstellung hängt zusätzlich vom **Betriebsmodus** ab: Im Wake-Word-Modus ist
die Grundfarbe blau, im Hotkey-Modus grün. Der Text bleibt in beiden Modi gleich
lang gültig — nur die Farbe unterscheidet sie.

Drei der acht sind **flüchtig** (`success`, `warning`, `error`): Sie melden
etwas und geben den Indikator danach zurück. Die anderen fünf bleiben stehen.

---

## 3. Mikrofon-Stummschaltung

Der Tray-Eintrag „Mikrofon stummschalten" setzt die GPO-Leitung **X0D30** am
Gerät. Das ist dieselbe Leitung, die der Knopf am ReSpeaker zieht, und sie tut
beides zugleich: Mute-LED an und Mikrofon in Hardware stumm.

Zusätzlich verwirft der Client die aufgenommenen Pakete. Das ist kein Ersatz,
sondern die Zusicherung, die auch ohne angeschlossenen ReSpeaker gilt.

**Der Client folgt der Leitung, statt sie zu besitzen.** X0D30 liest gleich, egal
wer sie gesetzt hat — wer am Gerät drückt, schaltet damit auch die Anwendung
stumm. Der LED-Worker liest sie im Sekundentakt; aus dem Qt-Thread wird sie nie
gelesen, aus demselben Grund wie oben.

Zwei Fallstricke, an denen wir Zeit verloren haben und die dokumentiert bleiben
sollen:

- `GPO_READ_VALUES` adressiert die fünf Pins über ihre **Position**,
  `GPO_WRITE_VALUE` über die **Pin-Nummer**. Ein Schreibzugriff mit der Position
  wird über USB angenommen und bewirkt nichts — auf jedem Pin.
- Wer nachmisst, ob die Stummschaltung greift, muss nach dem Setzen **eine
  Sekunde warten**. Die Aufnahmewarteschlange hält mehrere Sekunden Ton; wer
  sofort misst, misst die Zeit davor.

---

## 4. Was abgesichert ist

**432 automatisierte Tests**, dazu vier manuelle Prüfungen am Gerät.

| Kanal | Automatisiert | Am Gerät geprüft |
|---|---|---|
| LED | 30 (`test_led_feedback`) + 9 (`test_feedback_mapping`) | alle 13 Wirkungen, Trennung/Wiederverbindung, 24-min-Langlauf |
| Sound | 6 (`test_feedback_ui`) | — |
| In-App | 20 (`test_ui_widgets`) + 19 (`test_ui_application`) | — |
| Reducer | 19 (`test_feedback_reducer`) | — |
| Ereignisstrom | 41 (`test_event_*`) | — |
| Zusammenspiel | 7 (`test_feedback_integration`) | — |
| Stummschaltung | 4 (`test_audio_capture`) + 11 im LED-Weg | X0D30 gemessen, Angleichung an die Taste |

**Vollständigkeit wird erzwungen, nicht gehofft.** Für alle drei Kanäle gibt es
Tests, die über den ganzen Wertevorrat laufen: jede der 30 Ereignisarten ist im
Katalog, jeder der 7 Cues löst auf, jede der 8 Indikatoraktionen ergibt in beiden
Betriebsmodi eine Darstellung. Ein neuer Enum-Wert ohne Eintrag bricht damit den
Test, statt zur Laufzeit als `KeyError` aufzuschlagen.

Beim LED-Kanal kommt eine Prüfung beim **Programmstart** hinzu: Jedes in der
Konfiguration genannte Effektziel wird gegen den geladenen Katalog aufgelöst. Ein
Tippfehler verhindert den Start (Exitcode 7) — ein fehlendes Gerät niemals.

### Was nicht abgesichert ist

- **Ende-zu-Ende gegen den echten Server.** Der antwortete während der gesamten
  Abnahme mit HTTP 502. Alles Serverseitige ist gegen Doubles geprüft.
- **Physischer Kabelzug** am ReSpeaker. Die Codestrecke darüber ist über den
  Simulator geprüft, dessen Ringfenster sich echt trennen lässt.
- **Ton und Indikator am laufenden System.** Beide sind gut in Einzeltests
  abgedeckt, aber niemand hat sie über eine lange Sitzung beobachtet.
- Ein **einzelner Testfehlschlag** trat einmal in rund zwanzig Vollläufen auf und
  ließ sich nie reproduzieren; die Diagnose ging verloren.

---

## 5. Ausfallverhalten

Jeder Kanal fällt für sich aus:

| Was ausfällt | Was passiert |
|---|---|
| ReSpeaker abgezogen | LEFX verbindet selbstständig neu; einmal `client.led.unavailable`; Ton und Indikator laufen weiter |
| Sounddatei fehlt | einmalige Meldung, Diktat läuft weiter |
| Effektname falsch | **Start verweigert** mit Nennung aller falschen Namen |
| LED-Ring dauerhaft weg | nach 120 s Angebot, auf den Simulator umzuschalten |
| Server weg | Reducer bleibt auf dem letzten gültigen Zustand; Reconnect im Tray |

---

## Weiterführend

- [feedback_konfigurieren.md](feedback_konfigurieren.md) — praktische Rezepte
- `docs/decisions/ADR-004_LED_AUSGABE_UEBER_LEFX_V3.md` — warum es so gebaut ist
- `docs/work-packages/LEFX_V3_LED_CONTROLLER_INTEGRATION_PLANUNG.md` — der Weg dorthin
