# Prüfbericht nach AP04-Korrekturrunde 2

## Ergebnis

Korrekturrunde 2 hat die zuvor nachgewiesenen Hauptfehler weitgehend
behoben. Die unabhängigen Zieltests liefen erfolgreich:

```text
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
Ran 32 tests in 1.745s
OK

.\venv\Scripts\python.exe -m unittest tests.test_app -v
Ran 9 tests in 0.223s
OK
```

AP4 ist dennoch noch nicht abnahmefähig. Die folgende Liste enthält die
verbleibenden, unabhängig reproduzierten Restmängel. Sie ist die Grundlage
für die dritte und letzte AntiGravity-Korrekturrunde.

## 1. Teilweise Task-Erzeugung wird nicht aufgeräumt

`ClientController.run()` weist die drei neu erzeugten Tasks erst nach allen
drei erfolgreichen `create_task()`-Aufrufen der lokalen Liste `tasks` zu.
Schlägt der dritte Aufruf fehl, bleiben die ersten beiden Tasks außerhalb der
Cleanup-Liste aktiv.

Reproduktion mit einem Fehler beim dritten `create_task()`:

```text
PARTIAL_TASK_CREATION_PENDING 2 loop_cleared True queue_stops 1
```

Erwartet sind keine übrig gebliebenen Tasks. Jeder erfolgreich erzeugte Task
muss unmittelbar in die Cleanup-Sammlung aufgenommen werden.

## 2. Fehler beim Queue-Start lässt `_loop` gesetzt

`self._loop = asyncio.get_running_loop()` und `start_queue()` liegen derzeit
vor dem geschützten `try/finally`. Wirft `start_queue()`, wird `_loop` nicht
zurückgesetzt.

Reproduktion:

```text
QUEUE_START_FAILURE_LOOP_CLEARED False queue_stops 1
```

Auch der Queue-Start muss im vollständigen Lifecycle-Schutz liegen. Nach
jedem Ausgang von `run()` muss `_loop is None` gelten.

## 3. Gemeinsamer Shutdown ist gegen Caller-Cancellation ungeschützt

Mehrere normale Aufrufer teilen inzwischen dieselbe Shutdown-Task. Ein
Abbruch eines wartenden Aufrufers propagiert jedoch in diese Task, weil sie
direkt awaited wird. Dadurch wird das eigentliche Cleanup mitten im Ablauf
abgebrochen und ein späterer Aufruf erhält ebenfalls `CancelledError`.

Reproduktion:

```text
CANCELLED_SHUTDOWN 1 1 0 0 completed False second CancelledError
```

Die gemeinsame interne Shutdown-Task muss mit `asyncio.shield()` gegen die
Cancellation einzelner Waiter geschützt werden. Ein späterer Aufrufer muss
das laufende Cleanup weiter abwarten und dessen Ergebnis erhalten können.

## 4. SIGINT-Handler kann die Shutdown-Task selbst abbrechen

`app.py` cancelt über `asyncio.all_tasks(client._loop)` pauschal sämtliche
Tasks. Darunter kann auch die gemeinsam genutzte `_shutdown_task` sein.
Der Handler darf nur die steuernde Run-/Main-Task abbrechen oder die normale
`asyncio.run()`-/`KeyboardInterrupt`-Semantik nutzen. Die Cleanup-Task selbst
darf nicht pauschal gecancelt werden.

## 5. Auto-Start-Fehler wird verschluckt

`_auto_start_when_ready()` rollt einen fehlgeschlagenen Start zwar zurück,
protokolliert den Fehler aber nur und kehrt regulär zurück. `run()` entfernt
den erfolgreich beendeten Helper und bleibt anschließend unbegrenzt mit einer
verbundenen, aber nicht aufnehmenden Session aktiv.

Reproduktion:

```text
AUTO_START_FAILURE_RUN_DONE False start_calls 1 audio_rollbacks 1
RUN_CANCEL_RESULT None
```

Der Fehler muss nach dem Audio-Rollback erneut ausgelöst oder über einen
gleichwertig verlässlichen, UI-neutral auswertbaren Fehlerpfad gemeldet
werden. `run()` darf danach nicht unbemerkt im falschen Zustand weiterlaufen.

## 6. Aufnahmeübergänge sind nicht serialisiert

`start_dictation()`, `stop_dictation()`, `toggle_dictation()` und der
Auto-Start-Helper teilen keinen asynchronen Transition-Lock. Damit kann ein
Stop eintreffen, nachdem Auto-Start seine Sollzustandsprüfung bestanden hat,
aber bevor `send_start()` beendet ist. Möglich sind ein gestoppter
Audio-Capture bei serverseitigem Streaming oder doppelte Startbefehle.

Alle Aufnahmeübergänge einschließlich Toggle-Entscheidung müssen durch
denselben asynchronen Lock serialisiert werden. Event-gesteuerte Tests müssen
mindestens Start/Stop sowie Auto-Start/manuellen Stop deterministisch
überlappen lassen.

## 7. Lifecycle-Testabdeckung reicht für diese Fehlerpfade nicht

Es fehlen deterministische Tests für:

- Fehlschlag nach ein oder zwei erfolgreich erzeugten Run-Tasks,
- Fehler von `start_queue()`,
- Cancellation nur eines Shutdown-Waiters,
- Auto-Start-Fehler mit Rollback und sichtbarer Run-Exception,
- konkurrierende Aufnahmeübergänge.

Die Tests dürfen nicht von willkürlichen `sleep()`-Zeitfenstern abhängen.

## 8. Nicht saubere Typimporte in `app.py`

Die Annotationen nennen unter anderem `Optional`, `STTSession`,
`AudioCapture`, `TranscriptHistoryManager`, `TextInjectionQueue`,
`TranscriptReinsertionService` und `WindowsInjectionBackend`, ohne diese
Namen sauber zu importieren. `from __future__ import annotations` verdeckt
dies nur zur Laufzeit. Außerdem sind `sys` und `Path` ungenutzt.

## 9. Kanonische Dokumentation ist weiterhin widersprüchlich

Der Abschlussbericht der Korrekturrunde behauptet, die veralteten Stellen
seien beseitigt. Die unabhängige Suche findet weiterhin unter anderem:

```text
docs/IMPLEMENTATION_ROADMAP.md: Aktives nächstes Paket: AP4 Controller-Integration
task.md: Nächstes Paket: AP4 Controller-Integration
docs/PROJEKTUEBERSICHT.md: Noch nicht integriert
docs/PROJEKTUEBERSICHT.md: Ran 103 tests
docs/PROJEKTUEBERSICHT.md: AP4-Integration
ÜBERGABE.md: Ran 103 tests
ÜBERGABE.md: zusätzliche Tests ... AP4-Integration
ÜBERGABE.md: AP4-Einstieg
ÜBERGABE.md: Vor AP4 ...
```

Diese Stellen müssen inhaltlich auf den tatsächlich verifizierten
AP4-Abschluss und AP5 als nächstes Paket gebracht werden. Zukünftige offene
AP5-/AP6-/E-07-Punkte dürfen dabei nicht irrtümlich abgehakt werden.

## 10. Ein neuer Race-Test ist unnötig zeitabhängig und erzeugt Lograuschen

`test_atomic_reservation_race_prevents_duplicate_history_calls` verwendet
`time.sleep()`. Außerdem initialisiert die dortige Fake-History mit
`db_path=":memory:"`, was von der Implementierung als Dateipfad behandelt
wird und einen unerwarteten SQLite-Fehler protokolliert.

Der Test ist auf Events/Barriers umzustellen und muss eine kontrollierte
Fake-Persistenz oder ein temporäres Verzeichnis verwenden. Der erwartete
Fehlerpfad darf kein unbeabsichtigtes Datenbank-Initialisierungsproblem
enthalten.

## Abnahmebedingung für Korrekturrunde 3

Alle genannten Punkte müssen implementiert, deterministisch getestet und in
den kanonischen Dokumenten tatsächlich aktualisiert sein. Nach der Runde
erfolgt eine erneute unabhängige Quellcode-, Test- und Dokumentationsprüfung.

