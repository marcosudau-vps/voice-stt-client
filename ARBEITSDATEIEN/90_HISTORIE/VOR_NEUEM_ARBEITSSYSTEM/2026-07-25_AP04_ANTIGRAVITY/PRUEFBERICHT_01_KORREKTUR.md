# AP04 – Unabhängiger Prüfbericht nach Korrekturrunde 1

> **Prüfdatum:** 25. Juli 2026  
> **Bewertung:** **weiterhin nicht abnahmefähig; Korrekturrunde 2 erforderlich**

## 1. Was erfolgreich korrigiert wurde

Die erste Korrekturrunde hat wichtige Befunde wirksam behoben:

- alle gezielten Testprozesse beenden sich jetzt selbst;
- `30` History-Tests, `27` Controller-Tests, `7` App-Tests und `67`
  AP2-/AP3-Tests wurden unabhängig wiederholt und sind grün;
- vollständige Discovery-Suite: `131 Tests`, `OK`, 4,094 s;
- `py_compile` für App, Core und Tests: Exitcode 0;
- die History besitzt nun eine grundsätzlich geeignete rückwärtskompatible
  Ergebnis-API;
- vorhandene History-Einträge werden im normalen seriellen Fall nicht mehr
  automatisch erneut enqueued;
- der belegte Callback-Lock-Deadlock wurde beseitigt;
- sequenziell wiederholter Shutdown stoppt Komponenten nicht erneut;
- eine erste semantische Befehls- und Statusoberfläche existiert.

Diese Fortschritte reichen nicht zur Abnahme, weil mehrere neu eingeführte
Lifecycle- und Parallelitätsfehler im realen Headless-Pfad bestehen.

## 2. Kritisch: Der reale Client beendet sich direkt nach dem Start

`STTController.run()` wartet mit `asyncio.FIRST_COMPLETED` auf:

- `session.run()`,
- `_audio_sender()`,
- `_auto_start_when_ready()`.

`_auto_start_when_ready()` kehrt nach dem ersten erfolgreichen `send_start()`
planmäßig zurück. Damit gilt der Wait sofort als abgeschlossen; `run()`
cancelt Session und Audio-Sender und führt Shutdown aus.

Deterministischer Nachweis mit einer weiterhin laufenden Fake-Session:

```text
RUN_RETURNED_AFTER_AUTO_START 0.203 start_calls 1 stop_calls 1
```

Der tatsächliche Headless-Client würde somit rund 200 ms nach `READY` und
`start` wieder herunterfahren. Der bestehende App-Test übersieht das, weil er
alle drei Fake-Coroutinen absichtlich sofort beenden lässt.

## 3. Konkurrierender Shutdown ist weiterhin doppelt

In `shutdown()` steht bei bereits laufendem Shutdown weiterhin nur:

```python
if self._closing:
    pass
```

Ein zweiter Task führt danach den vollständigen Stopablauf parallel aus.
Deterministischer Event-gesteuerter Nachweis:

```text
CONCURRENT_SHUTDOWN_COUNTS 2 2 2
```

Audio, Session und Queue werden bei zwei überlappenden Shutdown-Aufrufen
jeweils zweimal gestoppt. Die Runde testet nur zwei nacheinander ausgeführte
Aufrufe, nicht den ausdrücklich beauftragten konkurrierenden Fall.

## 4. Finalidentität wird vor History nicht atomar reserviert

Die Korrektur prüft `_processed_finals` unter Lock, gibt den Lock aber frei,
bevor die Identität reserviert wird. Erst nach dem History-Ergebnis wird der
Schlüssel eingetragen.

Wenn zwei gleiche Finals parallel eintreffen, kann:

1. Aufruf A die History betreten und dort blockieren/fehlschlagen;
2. Aufruf B denselben noch unreservierten Schlüssel ebenfalls annehmen;
3. Aufruf B erfolgreich einen neuen Entry enqueuen;
4. Aufruf A anschließend `history_unavailable` melden.

Deterministischer Nachweis:

```text
FAILURE_RACE_STATUSES ['history_unavailable', 'queued']
history_calls 2
enqueues 1
```

Damit bewirkt das Serverduplikat in genau einem Fehlerfenster doch einen
automatischen Retry. Der vorhandene Paralleltest verwendet nur eine
fehlerfreie, intern serialisierende echte History und deckt diese Race
Condition nicht ab.

## 5. Diktierbefehle melden Erfolg vor asynchronem Fehler

`start_dictation()` und `stop_dictation()` sind synchrone Methoden. Läuft
bereits eine Event-Loop, erzeugt `_run_coro_sync_or_async()` nur einen
Hintergrundtask. Dieser Rückgabewert wird verworfen; die Methode meldet sofort
`success=True, status="listening"` beziehungsweise `"stopped"`.

Nachweis mit einem asynchron fehlschlagenden `send_start()`:

```text
ASYNC_COMMAND_REPORTED True listening
background_errors 1
audio_started 1
```

Die UI erhielte also eine falsche Erfolgsmeldung, während im Hintergrund eine
unbeobachtete Task-Exception entsteht und Audio weiterläuft. Die vorhandenen
Tests rufen die Methoden außerhalb einer Event-Loop auf; dort blockiert
`asyncio.run()` und verdeckt den Produktionsfall.

Zusätzlich ignoriert `_auto_start_when_ready()` den gewünschten
Diktierzustand: Es setzt `_dictation_requested` selbst auf `True` und startet
immer. Ein vor `READY` erteilter Stop-Wunsch kann den Autostart nicht
verhindern. Gewünschter Zustand und Transportzustand sind damit noch nicht
wirklich getrennt.

## 6. Run-Loop-Fehlersemantik und Teilstart

Weiter offen:

- Task-Erzeugung liegt weiterhin vor dem `try`; ein Fehler während
  Teil-Task-Erstellung durchläuft das Cleanup nicht zuverlässig.
- Hilfstask-Exceptions werden nur geloggt, nicht als auswertbarer Run-Fehler
  weitergereicht.
- Der App-Test belegt weder eine dauerhaft laufende Session nach erfolgreichem
  Autostart noch Helper-Fehler oder Teilstart.
- Die erfolgreiche Beendigung des Auto-Start-Helpers muss ignoriert werden,
  während normales Ende von `session.run()` den Controller beenden soll.

## 7. Tests greifen auf reale Benutzerhistorie zu

`tests/test_app.py` erzeugt `RealtimeSTTClient(AppConfig())`. Seit AP4 erzeugt
dies im Konstruktor einen echten `TranscriptHistoryManager` mit dem
standardmäßigen Pfad unter `%LOCALAPPDATA%`. Erst danach wird teilweise nur
`client.queue` ersetzt; der Reinsertion-Service behält sogar die alte Queue.

Die App-Tests sind daher nicht vollständig isoliert und können die echte
lokale History-Datenbank öffnen oder initialisieren. Der AP4-Vertrag verbietet
genau diese Kopplung. `RealtimeSTTClient` benötigt eine testbare
Dependency-Injection-Oberfläche oder die Tests müssen vor Konstruktion einen
temporären Historypfad einsetzen und alle zusammengehörigen Komponenten
konsistent injizieren.

## 8. History-Randfall falsch klassifiziert

`add_entry_with_status()` liefert bei „bereits verarbeitet, aber aus Memory
rotiert und nicht persistiert“:

```text
status=ALREADY_EXISTS, entry=None
```

Der Controller prüft jedoch zuerst `entry is None` und meldet
`history_unavailable`. Fachlich ist die Identität ein bekanntes Duplikat,
nur der Entry wurde nach der bestehenden Retention-Politik verworfen.
Es darf weiterhin keinen Enqueue geben, aber der Status muss
`deduplicated` statt eines falschen History-Ausfalls sein.

## 9. Dokumentation wurde entgegen dem Abschlussbericht nicht bereinigt

Die nach Korrekturrunde 1 gemeldete Synchronisierung ist nicht erfolgt:

- Roadmap und `task.md` nennen AP4 weiterhin als nächstes Paket;
- `docs/PROJEKTUEBERSICHT.md` enthält weiterhin „Noch nicht integriert“, die
  alte 103-Testdarstellung, „AP4-Integration nicht geprüft“ und eine
  Schlusszusammenfassung, nach der die drei Komponenten nicht integriert und
  AP4 als nächstes auszuführen seien;
- `ÜBERGABE.md` enthält weiterhin die alte 103-Testmatrix,
  „AP4-Einstieg“ und „Vor AP4 ...“;
- die Abnahmecheckliste in
  `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md` ist vollständig
  ungeprüft `[ ]`.

Damit widersprechen sich aktive Quellen weiterhin direkt.

## 10. Erforderliche zweite Korrektur

Die zweite Runde muss sich ausschließlich auf die vorstehenden konkreten
Befunde konzentrieren. Die jetzt grünen AP1–AP3-Funktionen und bereits
behobenen Callback-/History-Duplikatfälle dürfen nicht erneut breit
refaktoriert werden.
