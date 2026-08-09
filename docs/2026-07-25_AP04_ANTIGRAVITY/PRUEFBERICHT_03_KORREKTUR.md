# Prüfbericht nach AP04-Korrekturrunde 3

## Ergebnis

Die dritte AntiGravity-Korrekturrunde verbesserte den Controller erneut und
brachte ihre eigene Suite auf 142 grüne Tests. Sie war trotzdem noch nicht
abnahmefähig. Der erzeugte Abschlussbericht wurde deshalb nicht ungeprüft
übernommen.

## Behobene Punkte der dritten Runde

- Tasks werden während `run()` unmittelbar nach erfolgreicher Erzeugung in die
  Cleanup-Sammlung aufgenommen.
- Queue-Start und Loop-Bindung liegen im geschützten Lifecycle.
- Der gemeinsame Shutdown wird mit `asyncio.shield()` gegen die Cancellation
  einzelner Waiter geschützt.
- Auto-Start-Fehler werden nach Audio-Rollback bis zu `run()` propagiert.
- Start, Stop, Toggle und Auto-Start verwenden einen gemeinsamen
  Transition-Lock.
- Die pauschale Cancellation aller Eventloop-Tasks im SIGINT-Pfad wurde
  entfernt.
- Annotationstypen in `app.py` werden sauber importiert.

## Verbliebene Abnahmebefunde

### 1. Dokumentationsnachweis war sachlich falsch

Der AntiGravity-Abschlussbericht behauptete für die alten Formulierungen
„0 Treffer“. Die unmittelbar danach ausgeführte unabhängige Suche fand
weiterhin:

```text
task.md: Nächstes Paket: AP4 Controller-Integration
docs/IMPLEMENTATION_ROADMAP.md: Aktives nächstes Paket: AP4 Controller-Integration
ÜBERGABE.md: Vor AP4 ...
docs/PROJEKTUEBERSICHT.md: 138 automatische Tests
```

Zusätzlich enthielt `ÜBERGABE.md` einen beschädigten Markdown-Codeblock und
doppelt eingefügte Zeilen.

### 2. Queue-Rollback wurde beim Run-Cleanup doppelt gestoppt

Bei fehlgeschlagenem `queue.start()` stoppte `start_queue()` die Queue bereits.
Der `finally`-Pfad von `run()` rief anschließend über `shutdown()` nochmals
`queue.stop()` auf. Der neue Test verlangte nur „mindestens ein“ Stop und
übersah damit den Exakt-einmal-Vertrag.

### 3. Shutdown und Aufnahmeübergang waren gegeneinander nicht serialisiert

Der Transition-Lock schützte die Diktierbefehle untereinander, aber
`_do_shutdown()` verwendete ihn nicht. Ein bereits laufender Start konnte
deshalb gleichzeitig mit Audio-/Session-Stop fortgesetzt werden.

### 4. Finalannahme besaß noch ein Closing-Zeitfenster

`process_raw_final_event()` prüfte `closing` vor der Validierung, reservierte
die Finalidentität aber erst später unter dem Lock. Dazwischen konnte Shutdown
beginnen und das Final trotzdem noch neu angenommen werden.

### 5. Race-Tests waren teilweise nicht deterministisch

Mehrere neu hinzugefügte Tests nutzten weiterhin feste
`asyncio.sleep()`-Zeitfenster. Der Start/Stop-Race-Test startete beide Tasks
nur direkt hintereinander und belegte keine echte kontrollierte Überlappung.

### 6. Semantische Befehle glaubten stille Serverbefehle

`STTSession.send_start()` und `send_stop()` können bei einer inzwischen
geschlossenen Verbindung ohne Exception zurückkehren. Der Controller meldete
dann Erfolg, ohne zu prüfen, ob `is_streaming` tatsächlich umgeschaltet wurde.

### 7. Injizierte Komponenten konnten verschiedene History-Instanzen nutzen

Der Produktionsdefault verdrahtete History, Queue und Reinsertion korrekt.
Bei Dependency Injection wurde der im AP4-Vertrag geforderte gemeinsame
Instanzbesitz jedoch nicht validiert.

### 8. Unerwartete Cancellation eines Hilfstasks wurde verschluckt

`task.exception()` auf einer gecancelten Task löst selbst
`CancelledError` aus. Der äußere Handler behandelte dadurch auch eine
unerwartete Cancellation des Audio-Senders wie eine normale Cancellation von
`run()`.

### 9. Ein verlangter Testmodulname existiert nicht

Der von der prüfenden Seite erstellte dritte Korrekturprompt nannte
`tests.test_audio`. Eine solche Datei gibt es nicht. Die sieben
Audio-Thread-Bridge-Tests liegen in `tests.test_app`. AntiGravity ließ den
nicht ausführbaren Teilbefehl im Abschlussbericht ohne Hinweis weg.

Dieser Fehler betrifft den Nachweisbefehl, nicht den Produktcode. Die korrekte
reale Suite wurde anschließend vollständig über Test-Discovery ausgeführt.

## Konsequenz

Da die vereinbarten drei AntiGravity-Korrekturrunden ausgeschöpft waren, wurden
die Restmängel anschließend direkt und testgetrieben fertiggestellt. Der
Nachweis steht in `SELBSTFERTIGSTELLUNG.md` und `GESAMTABNAHME.md`.

