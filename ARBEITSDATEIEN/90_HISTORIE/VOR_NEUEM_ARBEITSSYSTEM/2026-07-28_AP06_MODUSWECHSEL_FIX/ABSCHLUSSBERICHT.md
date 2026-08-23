# AP6 – Robuster Fix des Betriebsmoduswechsels

> **Stand:** 28. Juli 2026  
> **Ergebnis:** Die beiden im manuellen Abschlusstest nachgewiesenen
> Clientfehler F-01 und F-02 sind behoben und lokal sowie gegen den
> produktiven Server reproduzierbar verifiziert.  
> **Automatischer Stand:** 264 Tests erfolgreich; `compileall` erfolgreich.

## 1. Behobenes Fehlerbild

Der fehlgeschlagene Bedienlauf bestand aus zwei zusammenhängenden
Lifecyclefehlern:

1. Bei einem Laufzeitwechsel vom Hotkey- in den Wake-Word-Modus wurde kein
   Wake-Word-Maintainer erzeugt. Die neue Session war zwar `READY`, aber der
   notwendige Hintergrundstream blieb bis zu einer manuellen Hotkeybetätigung
   aus.
2. Beim Rückwechsel beendete sich ein vorhandener Maintainer regulär. Der
   allgemeine Run-Loop wertete dieses normale Ende als unerwarteten
   Helperfehler und beendete den gesamten Core.

Die ursprüngliche Beweiskette steht unter
`docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md`.

## 2. Technische Korrektur

### 2.1 Ein persistenter Maintainer für den gesamten Core-Lifecycle

Der Wake-Word-Maintainer wird jetzt unabhängig vom Startmodus immer genau
einmal zusammen mit den übrigen langfristigen Core-Tasks erzeugt.

Er beendet sich bei einem Moduswechsel oder während eines kontrollierten
Shutdowns nicht mehr selbst. Außerhalb eines aktiven Wake-Word-Modus bleibt er
ruhend und wird erst durch den gemeinsamen Run-Lifecycle abgebrochen.

Damit existiert kein Sonderfall mehr, in dem:

- ein im Hotkeymodus gestarteter Prozess später keinen Maintainer besitzt;
- ein notwendiges normales Maintainer-Ende als fataler Taskabschluss
  fehlinterpretiert werden kann.

### 2.2 Atomare Aktivierung des Wake-Word-Modus

Ein Session-Reconnect bis `READY` genügt nicht mehr, um den Wechsel als
erfolgreich zu melden. Der Apply-Vorgang verlangt nun vollständig:

```text
neue Konfiguration installieren
  → neue Sessiongeneration anfordern
  → effektiven Sessionvertrag bis READY bestätigen
  → Audioaufnahme starten
  → start an Server senden
  → serverseitigen Recorderstatus abwarten
  → erst dann Erfolg an die UI melden
```

Der Einstellungsdialog kann daher keinen erfolgreichen Wake-Word-Wechsel mehr
anzeigen, während der Hintergrundstream tatsächlich noch inaktiv ist.

### 2.3 Definierter gewünschter Wake-Zustand

Beim echten Moduswechsel gilt:

- Hotkey → Wake Word: Hintergrundstream soll aktiv sein;
- Wake Word → Hotkey: Hintergrundstream soll inaktiv sein;
- Profiländerung innerhalb eines bereits pausierten Wake-Word-Modus:
  bewusste Pause bleibt erhalten.

Während der atomaren Neukonfiguration wird die automatische Maintenance kurz
ausgesetzt. Dadurch kann sie nicht mit Stop, Reconnect, Streamaktivierung oder
Rollback konkurrieren.

### 2.4 Bestätigter Rollback

Scheitert Session-Reconnect oder Wake-Stream-Aktivierung, wird nicht nur ein
alter Python-Wert zurückgeschrieben. Der Client:

1. beendet einen eventuell teilweise gestarteten Kandidaten;
2. installiert die letzte gültige Konfiguration und das letzte Audiogerät;
3. fordert dafür eine neue Server-Session an;
4. wartet erneut auf deren bestätigtes `READY`;
5. stellt bei einem zuvor aktiven Wake-Word-Modus auch dessen Stream wieder
   her.

Erst danach wird der Fehler an die UI gemeldet. Falls selbst die
Wiederherstellung fehlschlägt, wird dies im Resultat ausdrücklich kenntlich
gemacht; der persistente Maintainer bleibt für spätere Selbstheilung erhalten.

## 3. Automatisierte Reproduktion

Der frühere Bedienablauf ist als eigener Lifecycle-Regressionstest
materialisiert:

1. Core startet im Hotkeymodus.
2. Wechsel nach Wake Word.
3. Test prüft ohne Hotkeybetätigung:
   - neue Sessiongeneration,
   - `DictationState.ACTIVE`,
   - gestartetes Audio,
   - aktives Sessionstreaming,
   - weiterhin laufenden Core.
4. Rückwechsel in den Hotkeymodus.
5. Test prüft:
   - gestopptes Audio und Streaming,
   - `DictationState.IDLE`,
   - weiterhin laufenden Core nach zusätzlicher Wartezeit.
6. Die komplette Folge wird dreimal wiederholt.

Zwei weitere Härtungstests prüfen:

- absichtlich fehlschlagende Wake-Stream-Aktivierung mit bestätigtem Rollback
  auf den Hotkeymodus;
- automatische Wiederaktivierung des erst zur Laufzeit eingeschalteten
  Wake-Word-Modus nach einem heilbaren Transport-Reconnect.

Ergebnis:

```text
Ran 3 tests in 1.009s
OK
```

## 4. Reproduktion gegen den produktiven Server

`tests/manual_test_ap06_runtime_mode_switch.py` führt genau den
problematischen Wechsel mit echter `STTSession` gegen
`wss://stt.voice.marcosudau.com/ws/transcribe` aus. Aus Sicherheitsgründen
werden Mikrofon und Clipboard durch lokale Lifecycle-Doubles ersetzt; der
WebSocket, die Sessiongenerationen, der effektive Vertrag sowie
`start`-/`stop`-Bestätigungen sind echt.

Ausgabe:

```text
✓ initial hotkey session READY
✓ cycle 1: hotkey → wake_word, generation=2, stream armed
✓ cycle 1: wake_word → hotkey, generation=3, Core still alive
✓ cycle 2: hotkey → wake_word, generation=4, stream armed
✓ cycle 2: wake_word → hotkey, generation=5, Core still alive
AP06 LIVE RUNTIME MODE-SWITCH REGRESSION PASSED (12.7s)
```

Damit wurde der frühere Absturzpfad nicht nur simuliert, sondern über vier
echte produktive Session-Reconnects provoziert. Der Core blieb nach beiden
Rückwechseln aktiv.

## 5. Gesamttest

Nach der gezielten Reproduktion bestand die vollständige Regression:

```text
Ran 264 tests in 7.621s
OK
```

Zusätzlich bestand:

```text
compileall app.py core ui tests
PY_COMPILE_OK
```

Die während der Gesamtsuite sichtbaren Fehlerlogs gehören zu absichtlich
simulierten Negativtests; der Testprozess endete mit Exit-Code 0.

## 6. Warum derselbe Fehler nicht wieder auftreten kann

Der frühere Fehler war kein zufälliges Timingproblem, sondern eine
strukturelle Lücke. Diese beiden auslösenden Bedingungen existieren nicht
mehr:

- Der Maintainer hängt nicht mehr davon ab, in welchem Modus der Prozess
  gestartet wurde.
- Der Maintainer beendet sich nicht mehr aufgrund eines Moduswechsels und kann
  daher vom Task-Wächter nicht mehr als normal beendeter Helper zum fatalen
  Corefehler gemacht werden.

Zusätzlich verhindert der neue Aktivierungsvertrag einen stillen
Teil-Erfolg: Ohne bestätigten Wake-Word-Stream gibt es keinen erfolgreichen
Settings-Apply. Der dreifach wiederholte lokale Test, der Rollbacktest, der
Reconnecttest und zwei vollständige produktive Wechselzyklen sichern genau
diese Grenzen dauerhaft ab.

## 7. Auswirkung und verbleibende Grenze

Der sichtbare Einfluss ist:

- Ein Moduswechsel wartet etwas länger, weil nicht nur `READY`, sondern auch
  die tatsächliche Streamaktivierung bestätigt wird.
- Der Wechsel nach Wake Word benötigt keine zusätzliche Hotkeybetätigung.
- Der Rückwechsel beendet den alten Stream, nicht den Core.
- Fehlgeschlagene Aktivierungen lassen keine halb aktive Konfiguration zurück.

Nicht verändert wurde die vereinbarte Hotkeysemantik im Wake-Word-Modus:
Die primäre Aktion pausiert oder aktiviert den Hintergrundstream und ist kein
Direct-Hotkey zur Umgehung der Wake-Word-Schranke.

Der sichere Live-Test sendet absichtlich kein Mikrofon-Audio. Die tatsächliche
Erkennung des gesprochenen `hey_jarvis` bleibt daher ein kurzer manueller
Hardware-/Server-Bediennachweis. Der zuvor clientseitig fehlende Stream ist
jedoch behoben und seine Aktivierung wird jetzt technisch bestätigt.

