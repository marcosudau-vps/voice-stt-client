# AP04 – Korrekturrunde 3 (letzte AntiGravity-Korrekturrunde)

AP4 ist nach Korrekturrunde 2 noch nicht abnahmefähig. Dies ist die dritte und
letzte AntiGravity-Korrekturrunde. Arbeite ausschließlich die unabhängig
reproduzierten Restmängel aus folgendem Bericht vollständig ab:

`docs/2026-07-25_AP04_ANTIGRAVITY/PRUEFBERICHT_02_KORREKTUR.md`

Lies außerdem nur die betroffenen Abschnitte des verbindlichen Auftrags
`docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`,
die tatsächlich betroffenen Module und deren Tests. Öffne keine historischen
Archive und keine Evaluation E-07. Beginne weder AP5 noch AP6. Verwende für
alle Python-Befehle ausschließlich `.\venv\Scripts\python.exe`.

## Verbindliche Korrekturen

### 1. Vollständig exception-sicherer Run-Lifecycle

- Nimm jeden erfolgreich erzeugten Task sofort in die Cleanup-Sammlung auf.
- Ein Fehler beim zweiten oder dritten `create_task()` muss alle zuvor
  erzeugten Tasks canceln und awaiten.
- Nimm auch Queue-Start und alle davor liegenden Lifecycle-Schritte in einen
  äußeren `try/finally` auf.
- Nach jedem Ausgang gilt `_loop is None`.
- Stoppe nur tatsächlich gestartete Komponenten und jede davon höchstens
  einmal.
- Erfolgreiches Ende des einmaligen Auto-Start-Helpers beendet `run()` nicht.
- Ein Fehler dieses Helpers muss nach einem nötigen Audio-Rollback für den
  Aufrufer von `run()` sichtbar sein und Cleanup auslösen.

Ergänze deterministische Tests für Fehler beim zweiten und dritten
Task-Erzeugen, Queue-Startfehler und Auto-Startfehler. Prüfe dabei explizit
keine liegen gebliebenen Tasks, freigegebene Loop, exakt einmaliges Cleanup
und die sichtbare ursprüngliche Exception.

### 2. Cancellation-sicherer gemeinsamer Shutdown

- Schütze die einmal erzeugte interne Shutdown-Task mit `asyncio.shield()`
  gegen Cancellation einzelner wartender Aufrufer.
- Wird Waiter A gecancelt, läuft das Cleanup weiter.
- Waiter B oder ein späterer Aufruf kann dasselbe Cleanup erfolgreich
  abwarten.
- Audio, Session, Queue und Cleanup laufen weiterhin exakt einmal.
- Bewahre die bestehende einheitliche Fehler- und Timeout-Semantik.
- Der SIGINT-Pfad in `app.py` darf die interne Shutdown-Task niemals über
  ein pauschales Cancel aller Loop-Tasks abbrechen.

Ergänze einen Event-gesteuerten Test, der Waiter A während eines blockierten
Cleanup-Schritts cancelt, danach freigibt und über Waiter B den erfolgreichen
Abschluss sowie alle Exakt-einmal-Zähler beweist.

### 3. Aufnahmeübergänge atomar serialisieren

Nutze einen gemeinsamen, lazy an die aktive Eventloop gebundenen
`asyncio.Lock` oder eine gleichwertige Lösung für:

- `start_dictation()`,
- `stop_dictation()`,
- `toggle_dictation()` einschließlich Zustandsentscheidung,
- den automatischen Start nach READY.

Vermeide verschachteltes erneutes Akquirieren desselben Locks; verwende
gegebenenfalls interne `*_locked`-Hilfsmethoden. Sollzustand, Audio-Start bzw.
-Stop und Serverbefehl müssen einen konsistenten Übergang bilden. Bei
Fehlern muss der lokale Audiozustand passend zurückgerollt werden. Die
Semantik `start` = Audio vor Serverstart und `stop` = Serverstop vor
Audiostop bleibt erhalten.

Ergänze deterministische Event-gesteuerte Race-Tests:

- manueller Start gegen Stop,
- Auto-Start gegen manuellen Stop,
- paralleles Toggle.

Die Tests müssen Endzustand und genaue Befehls-/Audiozähler prüfen und dürfen
nicht auf zufällige Sleeps vertrauen.

### 4. Tests und Typimporte bereinigen

- Ersetze die `time.sleep()`-Synchronisation des atomaren History-Race-Tests
  durch Events oder Barriers.
- Vermeide dort den falschen `":memory:"`-Dateipfad und unerwartete
  SQLite-Initialisierungsfehler.
- Ergänze in App-/Lifecycle-Tests vollständige Fakes für Session und Audio,
  wo deren Konstruktion Teil des geprüften Pfads ist.
- Importiere alle in `app.py` verwendeten Annotationstypen sauber und entferne
  ungenutzte Imports.

### 5. Kanonische Dokumentation tatsächlich synchronisieren

Aktualisiere mindestens:

- `task.md`,
- `docs/IMPLEMENTATION_ROADMAP.md`,
- `docs/PROJEKTUEBERSICHT.md`,
- `ÜBERGABE.md`,
- `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`,

sofern der jeweilige Inhalt betroffen ist.

Verbindlicher Inhalt:

- AP4 als abgeschlossen nur nach vollständig grüner Abnahme,
- Controllerintegration, Finalpfad, Deduplizierung, History-before-enqueue,
  Lifecycle und semantische Diktatbefehle korrekt beschreiben,
- AP5 als nächstes noch nicht begonnenes Paket nennen,
- keine Behauptung eines Hotkey- oder GUI-Abschlusses,
- aktuelle tatsächlich reproduzierte Testanzahl und Testbefehle,
- zukünftige AP5-/AP6-/E-07-Punkte offen lassen.

Führe anschließend eine exakte Suche nach den im Prüfbericht genannten
veralteten Formulierungen aus und übernimm das Suchergebnis in den
Abschlussbericht. Eine bloße Behauptung „bereinigt“ reicht nicht.

## Verbindliche Prüfung

Führe mindestens aus:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_history -v
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
.\venv\Scripts\python.exe -m unittest tests.test_app -v
.\venv\Scripts\python.exe -m unittest tests.test_connection tests.test_audio tests.test_text_injector tests.test_reinsertion -v
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe -m py_compile app.py core\controller.py core\history.py
```

Kein Testlauf darf hängen. Behebe jede Regression iterativ. Ändere keine
produktiven Servereinstellungen und führe keine Mikrofon-, Clipboard- oder
Tastatureingabe-Automation aus.

## Nachweisartefakte

Speichere während dieser Runde unter
`docs/2026-07-25_AP04_ANTIGRAVITY/03_korrektur/`:

1. `KORREKTURPLAN.md`
2. `WALKTHROUGH.md`
3. `ABSCHLUSSBERICHT.md`

Der Abschlussbericht muss enthalten:

- geänderte Dateien und konkrete Begründung,
- Zuordnung jedes Prüfberichtpunkts zur Korrektur und zu Tests,
- exakte Testbefehle, Testanzahlen und Ergebnisse,
- exakte Suche nach den alten Dokumentationsformulierungen,
- verbleibende Risiken oder ausdrücklich „keine bekannten“,
- Bestätigung, dass AP5/AP6/E-07 nicht implementiert wurden.

Beginne jetzt mit der Analyse, implementiere die Korrekturen vollständig,
teste alles und aktualisiere die Nachweisartefakte. Stoppe nach AP4.

