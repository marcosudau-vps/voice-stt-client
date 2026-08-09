# AP06 – Abnahmebericht Windows UI-Shell

> **Status:** vollständig umgesetzt und abgenommen  
> **Datum:** 25. Juli 2026  
> **Vor-AP06-Baseline:** 197 Tests  
> **Abnahmestand:** 238 Tests, `py_compile` und zwei Laufzeit-Smokes erfolgreich

## 1. Ergebnis

AP06 stellt die erste vollständige Windows-Bedienschicht auf den vorhandenen
AP1–AP5-Core. Der reguläre Start führt jetzt in eine PySide6-Anwendung mit
Tray, passivem Overlay, nativen globalen Hotkeys, Verlauf/Reinsertion und
Single-Instance-Schutz. Der bisherige Konsolenbetrieb bleibt über
`app.py --headless` erhalten.

AP07-Funktionen wurden nicht vorweggenommen. Insbesondere wurden keine
Gerätewechsel-, Sleep/Wake-, Multi-Monitor-, DPI-, Autostart-, Packaging-,
Admin- oder Wake-Word-Modusfunktionen ergänzt.

## 2. Umgesetzte Bedienung

| Aktion | Bedienweg |
|---|---|
| Diktierung starten/stoppen | `Ctrl+Shift+Space` oder Tray-Aktion |
| Letzten Finaltext erneut einfügen | `Ctrl+Alt+Space` oder Tray-Aktion |
| Älteren Finaltext erneut einfügen | dynamischer, ID-gebundener Tray-Verlauf |
| Status prüfen | farbiges Tray-Icon, Tooltip und Statuszeile |
| Anwendung beenden | Tray-Aktion „Beenden“ |

Realtime-Text ersetzt nur den Inhalt des Overlays. Er wird niemals in die
fokussierte Anwendung eingefügt. Finaltexte durchlaufen unverändert die
Controllergrenze: Deduplizierung, Historie und danach Injection-Queue.

Passive Reconnectversuche bleiben still. Sie erzeugen keine
Systembenachrichtigungen und keine wiederholten Overlays. Aktionsbezogene
Netzwerk-, Mikrofon- oder Protokollprobleme werden kurz und nicht modal im
Overlay signalisiert.

## 3. Architektur- und Threadgrenzen

### Qt Main Thread

Im Main Thread liegen ausschließlich:

- `QApplication`,
- Tray, Menüs und Aktionen,
- Overlay,
- nativer Qt-Eventfilter für `WM_HOTKEY`,
- UI-Darstellung und Lifecycle-Komposition.

### asyncio-Core-Thread

`ui/core_bridge.py` erzeugt einen eigenen nicht-daemonisierten Thread
`RealtimeSTT-AsyncCore`. Dieser Thread besitzt:

- eine eigene asyncio-Event-Loop,
- genau einen `STTController`,
- die asynchronen Start-/Stop-/Togglebefehle,
- die synchronen Reinsertion-/Historienabfragen innerhalb derselben
  Core-Eigentumsgrenze.

Core-Callbacks werden als Qt-Signale in den Main Thread transportiert.
UI-Befehle werden thread-sicher in die Core-Loop geplant. Befehle vor dem Start
oder nach dem Stop werden nicht vorgemerkt, sondern kontrolliert abgelehnt.

Der Shutdown meldet zunächst die Hotkeys ab, blendet das Tray aus, fährt den
Controller in seiner Loop herunter, beendet die Loop, wartet begrenzt auf den
Core-Thread und gibt den Single-Instance-Mutex frei.

## 4. Implementierte Module

### Neu

- `ui/application.py`: Komposition, Main-Thread-Prüfung, Start- und
  Shutdownpfade sowie definierte Exit-Codes.
- `ui/core_bridge.py`: Qt-/asyncio-Brücke und Core-Thread.
- `ui/hotkeys.py`: Parser, Win32-Backend, `RegisterHotKey`,
  `MOD_NOREPEAT`, Qt-Native-Eventfilter und Konflikt-Rollback.
- `ui/single_instance.py`: benannter lokaler Win32-Mutex.
- `ui/presentation.py`: reine Status-, Feedback- und Verlaufsabbildung.
- `ui/overlay.py`: passives, nicht aktivierendes und maustransparentes Overlay.
- `ui/tray.py`: Status, Bedienaktionen und dynamischer Verlauf.

### Angepasst

- `app.py`: GUI als Standardstart, `--headless` als Diagnosepfad.
- `core/config.py` und `config.yaml`: kanonische Hotkey- und
  Overlaykonfiguration, Validierung und Migration des alten Hotkeyfelds.
- `core/controller.py`: kleine öffentliche, vor dem Run erlaubte
  `request_initial_auto_start()`-Integrationsschnittstelle; keine fachliche
  Core-Neuimplementierung.

### Tests

- `tests/test_hotkeys.py`
- `tests/test_single_instance.py`
- `tests/test_ui_widgets.py`
- `tests/test_core_bridge.py`
- `tests/test_ui_application.py`
- erweiterte `tests/test_config.py`

## 5. Kontrollierte Fehlerpfade

- Kann der Single-Instance-Mutex nicht erzeugt werden, startet keine
  Teilkomponente.
- Eine zweite Instanz beendet sich unterscheidbar, bevor Core, Tray oder
  Hotkeys gestartet werden.
- Ist kein System-Tray verfügbar, wird kontrolliert beendet.
- Bei einem Hotkeykonflikt werden bereits in demselben Versuch registrierte
  Hotkeys zurückgerollt; die Bedienung über das Tray bleibt möglich.
- Scheitert der Corestart, werden UI-Ressourcen und Mutex freigegeben.
- Eine Ausnahme in einem UI-Callback darf den Core nicht beenden.
- Mehrfacher Shutdown und Abmeldung sind idempotent.

## 6. Automatisierte Verifikation

Gezielter AP06-/Härtungslauf:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\venv\Scripts\python.exe -m unittest tests.test_config tests.test_hotkeys tests.test_single_instance tests.test_ui_widgets tests.test_core_bridge tests.test_ui_application tests.test_app tests.test_controller.TestSTTControllerAP05Hardening
```

Ergebnis:

```text
Ran 74 tests in 0.836s
OK
```

Vollständige Regression:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Ergebnis:

```text
Ran 238 tests in 6.181s
OK
```

Aufteilung:

| Bereich | Tests |
|---|---:|
| Historie | 30 |
| Textinjektion | 41 |
| Reinsertion | 26 |
| Controller/AP5-Härtung | 62 |
| Konfiguration | 18 |
| STTSession | 18 |
| `app.py` | 10 |
| native Hotkeys | 6 |
| Single Instance | 3 |
| Präsentation, Tray und Overlay | 11 |
| Core-Brücke | 6 |
| GUI-Komposition | 7 |
| **Gesamt** | **238** |

Die während der Suite sichtbaren Error-Logs stammen aus absichtlich
simulierten Negativpfaden.

Syntaxprüfung:

```powershell
.\venv\Scripts\python.exe -m py_compile app.py <alle Python-Dateien unter core, ui und tests>
```

Ergebnis: erfolgreich, Exit-Code 0.

## 7. Laufzeit-Smoke-Tests

### Nativer Windows-Ressourcen-Smoke

Ohne Mikrofon oder Textinjektion wurde mit dem echten Win32-Backend geprüft:

1. erster Mutex wird erworben,
2. zweiter Guard erkennt `already_running`,
3. beide globalen Hotkeys werden registriert,
4. echte `WM_HOTKEY`-Nachrichten werden korrekt zu Toggle und Reinsertion
   geleitet,
5. Hotkeys und Mutex werden vollständig freigegeben.

Ergebnis: `NATIVE_RESOURCE_SMOKE: PASS`.

### Vollständige AP06-Komposition zum produktiven Server

Mit echter `QApplication`, System-Tray, Mutex, Hotkeys, produktiver
`CoreBridge` und `auto_start=False` wurde geprüft:

1. der benannte Mutex wird erworben,
2. das Windows-System-Tray ist verfügbar,
3. beide nativen Hotkeys werden registriert,
4. Core läuft in einem separaten Thread,
5. WebSocket-Verbindung erreicht `READY`,
6. Statussnapshots gelangen über die Qt-Brücke in den Main Thread,
7. Shutdown beendet Controller, Loop und Thread und gibt Hotkeys sowie Mutex
   sauber frei.

Es wurden bewusst weder Diktat, Audioaufnahme noch Textinjektion gestartet.

Ergebnis: `FULL_AP06_LIVE_SMOKE: PASS`.

## 8. Noch offene Grenzen

AP06 ist innerhalb seines Vertrags abgeschlossen. Für AP07 bleiben:

- reale Langzeit- und Reconnect-Stresstests,
- Mikrofonverlust, Hot-Plug und Gerätewechsel,
- Windows-Sleep/Wake und tatsächlicher Audiowiederanlauf,
- Multi-Monitor- und DPI-Verhalten des Overlays,
- Autostart, Packaging und Release-Hygiene,
- abschließende sichtbare Bedien- und End-to-End-Prüfungen unter
  Alltagsbedingungen.

Der Client enthält weiterhin keinen Wake-Word-/Direct-Modusselector und keinen
administrativen Serverzugang. Das Wake-Word-Verhalten bleibt serverseitig.

## 9. Abnahmeentscheidung

Alle AP06-Scopepunkte und Abnahmekriterien sind erfüllt. Die Vor-AP06-Suite
blieb vollständig grün, die neuen vulnerablen Thread-, Hotkey-, Mutex-,
Lifecycle- und Darstellungsgrenzen sind automatisiert abgesichert und die
Windows-/Server-Smokes waren erfolgreich.

**AP06 ist abgenommen. AP07 wurde nicht begonnen.**
