# Ausführungsauftrag – AP05 Fehlerverhalten und stille Selbstheilung

Status: ausgeführt; unabhängig korrigiert und abgenommen  
Datum: 2026-07-25  
Verbindlicher Paketvertrag:
`docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md`

> **Nummerierungsnachtrag vom 2. August 2026:** Historische Hinweise auf AP7
> als Geräte-/Sleep-Wake-Härtung meinen nach der Neuplanung AP8. AP7 ist nun das
> Feedback- und Eventsystem.

## 1. Auftrag

Setze ausschließlich AP5 vollständig um. Härte Transport, Ping/Pong,
Startbestätigung, Sessiongrenzen und Controllerstatus entsprechend dem
Paketvertrag. Beende die Arbeit erst, wenn die vulnerablen Fehler- und
Race-Pfade deterministisch getestet, alle Regressionstests grün und die
kanonischen Dokumente auf den tatsächlichen Stand gebracht sind.

Nicht mit AP6 oder AP7 beginnen.

## 2. Nicht verhandelbare Kernaussagen

1. Ein durch Transportverlust unterbrochenes Diktat ist beendet.
2. Nach Reconnect wird es niemals automatisch fortgesetzt.
3. Audio einer alten Session wird verworfen und niemals wiedergegeben.
4. Ein Benutzerstart bei nicht bereitem Transport wird sofort abgelehnt und
   niemals vorgemerkt.
5. Transport-Reconnect läuft unauffällig, mit gedeckeltem Backoff und
   theoretisch unbegrenzt bis Shutdown.
6. Ein gesendeter `start` ist erst nach passender Serverstatusbestätigung
   erfolgreich.
7. Die Bestätigungsfrist beträgt standardmäßig 10 Sekunden.
8. Passive Fehler erzeugen keine Popup- oder Ereignisflut.
9. Mikrofon-Hot-Plug, Gerätewechsel und Sleep/Wake gehören zu AP7.
10. Der bestehende AP1–AP4-Core wird nur soweit geändert, wie AP5 dies
    zwingend erfordert.

## 3. Pflichtlektüre in kontextschonender Reihenfolge

### Stufe A – kanonische Orientierung

Vollständig und in der Reihenfolge aus `AGENTS.md`:

1. `AGENTS.md`
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`
3. `docs/PROJEKTUEBERSICHT.md`
4. `docs/IMPLEMENTATION_ROADMAP.md`
5. `ÜBERGABE.md`
6. `task.md`

### Stufe B – AP5-Vertrag

1. dieser Ausführungsauftrag,
2. `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md`,
3. `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`.

### Stufe C – nur relevante Originalquellen

1. Serverindex `server-docs-for-client-development/README.md`,
2. die in Abschnitt 3 des Paketvertrags genannten Teile aus Kapitel 02, 03,
   04 und 07,
3. `core/stt_session.py`, `core/controller.py`, `core/audio_capture.py`,
   `core/config.py`, `app.py` und `config.yaml`,
4. direkte Tests dieser Module.

Archive, datierte Übergabeordner, alle übrigen Serverkapitel und sämtliche
Tests werden nicht pauschal vorab in den Kontext geladen.

## 4. Baseline vor der ersten Codeänderung

Führe aus:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Der letzte verifizierte Stand sind 152 erfolgreiche Tests. Bei einer
Abweichung zuerst Ursache und tatsächlichen Ausgangszustand dokumentieren.

Erstelle danach eine kurze Umsetzungsskizze, die mindestens benennt:

- gewünschte Zustands- und Ereignistypen,
- Sessiongeneration und Audiogrenze,
- Startbestätigungsmechanismus,
- neuen Pingzustand,
- Backoff-Resetkriterium,
- geplante neue/angepasste Tests.

## 5. Erwartete Änderungsschwerpunkte

### `core/stt_session.py`

- Pingzustand pro Verbindung, höchstens ein ausstehender Ping.
- Aufeinanderfolgende Misses ohne historischen RTT-Scheinbeleg.
- kontrollierte Verbindungsinvalidierung nach Schwellwert.
- Generationstrennung für Pongs, Events und Timer.
- Backoff erst nach erstem gültigen Pong zurücksetzen.
- Backoff einschließlich Jitter hart deckeln.
- 1013 als `server_busy` und mit längerer Mindestwartezeit.
- Reconnectwarteschleife sauber und sofort durch Shutdown abbrechen.
- Start nicht bereits durch erfolgreiches Senden als aktiv markieren.
- Serverstatus für die aktuelle Generation an den Controller vermittelbar
  machen.

### `core/controller.py`

- öffentlicher Benutzerstart setzt bei Nicht-`READY` keinen Wunsch.
- klarer Diktatzustand `idle` / `starting` / `active`.
- serverbestätigter Start mit 10-Sekunden-Timeout.
- genau einmalige Abbruchbehandlung bei Sessionverlust.
- Audioqueue und pending Startzustand an der Sessiongrenze bereinigen.
- keine automatische Wiederaufnahme nach Reconnect.
- headless Initialstart höchstens einmal separat behandeln.
- persistenter UI-neutraler Status und transiente Feedbackereignisse.
- bestehende AP4-Garantien, Locks, History-before-enqueue und
  Shutdown-Sicherheit erhalten.

### `app.py` und Audio-Brücke

- Audio nur für die bestätigte aktuelle Session freigeben.
- Fremdthread-Pakete einer alten Generation nach Stop/Abbruch sicher
  verwerfen.
- headless Verhalten weiterhin nutzbar halten, ohne Resume-Semantik.
- keine PySide- oder Hotkey-Abhängigkeit einführen.

### `core/config.py` und `config.yaml`

- `start_confirmation_timeout: 10.0`,
- `server_busy_min_delay: 10.0`,
- bestehende Reconnect-/Pingwerte validieren,
- sinnvolle Bereichs- und Konsistenzprüfung,
- keine Wake-Word- oder Adminoption ergänzen.

## 6. Empfohlene Umsetzungsreihenfolge

1. Baseline und relevante Codepfade erfassen.
2. UI-neutrale Enums, Reason-Codes und Snapshots festlegen.
3. Transportgeneration, Backoff und Ping/Pong isoliert korrigieren.
4. Transporttests vollständig grün bringen.
5. Startbestätigung und Diktat-Lifecycle im Controller umsetzen.
6. Audiogrenze und Abbruchsemantik integrieren.
7. Status-/Feedbackpfad ergänzen.
8. Konfiguration und Validierung vervollständigen.
9. gezielte Race-, Ressourcen- und Negativtests ergänzen.
10. volle Suite und Syntaxprüfung ausführen.
11. optionalen Live-Test nur nach automatischer Abnahme durchführen.
12. Dokumentation auf den tatsächlichen Stand aktualisieren.

Die Reihenfolge darf technisch angepasst werden. Der Scope darf nicht
ausgeweitet werden.

## 7. Pflichtprüfungen

Die vollständige Matrix steht in Abschnitt 17 des Paketvertrags. Besonders
streng zu prüfen sind:

- alter RTT darf einen aktuellen Ping-Miss nicht maskieren,
- kein zweiter ausstehender Ping,
- alter Pong/Status darf neue Session nicht verändern,
- `ready` allein setzt Backoff nicht zurück,
- Diktatabbruch erzeugt genau ein Ereignis,
- Start bei nicht `READY` wird nicht nachgeholt,
- Starttimeout und Disconnect während `starting` hinterlassen keinen
  Audioproducer und keine Queuepakete,
- Reconnect nach aktivem Diktat erreicht `ready + idle`,
- Shutdown unterbricht Backoff und Starttimeout,
- Callbackfehler sind nicht fatal,
- Wiederholungsversuche wachsen weder Tasks noch sessionlokale Mengen
  unbeschränkt,
- bestehender AP4-Final-, History- und Injection-Pfad bleibt unverändert
  korrekt.

Zeitabhängige Tests müssen mit kontrollierter Uhr, Events oder injizierbarer
Wartefunktion deterministisch sein. Keine Stabilitätsbehauptung darf allein
auf kurzen realen `sleep`-Aufrufen beruhen.

## 8. Test- und Abschlussbefehle

Mindestens:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_stt_session
.\venv\Scripts\python.exe -m unittest tests.test_controller
.\venv\Scripts\python.exe -m unittest tests.test_app
.\venv\Scripts\python.exe -m unittest tests.test_config
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\venv\Scripts\python.exe -m py_compile app.py core\stt_session.py core\controller.py core\audio_capture.py core\config.py
```

Falls `tests.test_stt_session` oder `tests.test_config` noch nicht existiert,
sind passende fokussierte Testmodule anzulegen oder die tatsächlichen
äquivalenten Modulnamen zu dokumentieren.

Der Abschlussbericht nennt:

- jeden ausgeführten Befehl,
- Exit-Code,
- Testanzahl,
- bewusst ausgelassene Live-Prüfungen,
- bekannte Restgrenzen,
- alle gegenüber diesem Auftrag notwendigen Abweichungen.

## 9. Dokumentationspflicht bei Abschluss

Nach erfolgreicher Implementierung:

- `task.md`: AP5-Unterpunkte und tatsächliche Testzahlen,
- `docs/IMPLEMENTATION_ROADMAP.md`: AP5 auf abgeschlossen, falls vollständig,
- `docs/PROJEKTUEBERSICHT.md`: tatsächliche neue Schnittstellen und Grenzen,
- `ÜBERGABE.md`: verifizierter Betriebs-, Start- und Reconnectstand,
- Paketvertrag nur dann ändern, wenn eine ausdrücklich genehmigte fachliche
  Entscheidung geändert wurde.

Die Dokumente dürfen nicht behaupten, Mikrofon-Hot-Plug oder Sleep/Wake seien
bereits gelöst. Diese Punkte bleiben AP7.

## 10. Stop-Regel

Nach vollständiger Umsetzung, Testabnahme und Dokumentation von AP5 stoppen.
Nicht automatisch AP6 beginnen. Nicht nebenbei UI, Hotkeys, Adminfunktionen,
Wake-Word-Umschaltung oder AP7-Härtung implementieren.
