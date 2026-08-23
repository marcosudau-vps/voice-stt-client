# AP04 – Unabhängiger Prüfbericht zur AntiGravity-Initialrunde

> **Prüfdatum:** 25. Juli 2026  
> **Bewertung:** **nicht abnahmefähig; Korrekturrunde erforderlich**  
> **Bezugsvertrag:**
> `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`

## 1. Kurzfazit

Die Initialrunde hat den richtigen architektonischen Einstieg gewählt:
`core/controller.py` existiert, `app.py` verwendet den Controller, rohe
Finalevents werden von Realtime-/Timeline-Ereignissen getrennt und AP1–AP3
sind grundsätzlich verdrahtet.

Die behauptete grüne Abnahme ist jedoch nicht reproduzierbar. Schon die
gezielte Controller-Suite und anschließend auch `tests.test_app` beenden sich
nicht, weil neue Tests nicht-daemonisierte Injection-Worker zurücklassen.
Mehrere verbindliche Controllerfunktionen fehlen oder verletzen den
Paketvertrag. Außerdem wurden aktive Dokumente widersprüchlich auf
`[ABGESCHLOSSEN]` gesetzt.

## 2. Reproduzierbarer Abnahmeblocker: Tests hängen

Ausgeführt:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
```

Ergebnis:

- nach mehr als 60 Sekunden kein Prozessende;
- der Test
  `test_shutdown_raises_queue_stop_timeout` ersetzt `queue.stop()` durch eine
  No-op-Funktion;
- dadurch erhält der echte nicht-daemonisierte
  `TextInjectionQueueWorker` kein Stop-Sentinel;
- `tearDown()` räumt ihn nicht auf, weil `is_running` bei `closing=True`
  bereits `False` meldet;
- die erzeugten Testprozesse mussten gezielt beendet werden.

Der Gegenlauf ohne genau diesen Test ergab:

```text
Ran 19 tests in 0.927s
OK
```

Auch:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_app -v
```

beendete sich nach mehr als 30 Sekunden nicht. Der Run-Loop-Test ersetzt
`shutdown()` durch eine No-op-Funktion, obwohl `run()` nun eine reale
Injection-Queue startet. Dadurch bleibt erneut ein nicht-daemonisierter Worker
zurück.

Folge: AntiGravitys Angaben „20 Tests OK“, „7 Tests OK“ und „123 Tests OK“
sind als Abnahmenachweis nicht belastbar.

## 3. Bestehender History-Duplikatfall wird erneut eingefügt

`core/controller.py::process_raw_final_event()` reserviert nur im lokalen
`_processed_finals`-Index und wertet anschließend jeden von
`history.add_entry()` zurückgegebenen Entry als neu aus.

Gezielter Nachweis:

1. Historie enthält bereits `(session_id="s", segment_id=1, text="original")`.
2. Neuer Controller erhält als erstes Event dieselbe Identität mit
   `text="conflicting"`.
3. Tatsächliches Ergebnis:

```text
PREEXISTING_DUPLICATE queued 1 original
```

Der Controller meldet also den neuen, konfliktbehafteten Eventtext als
`queued`, enqueued aber den alten Historytext. Dies verletzt E-02/E-03 und den
ausdrücklich verlangten Test „vorhandener History-Duplikatfall“.

Erforderlich ist die kleinste rückwärtskompatible History-API, die
„neu angelegt“, „bereits vorhanden“ und „nicht verfügbar“ eindeutig
unterscheidet. Ein bereits vorhandener Eintrag darf nicht erneut automatisch
enqueued werden; ein abweichender Text muss als Konflikt sichtbar werden.

## 4. Deadlock bei Duplikat-Callback

Im Duplikatpfad wird `_emit_final_result()` innerhalb von `self._lock`
aufgerufen. Ruft der UI-neutrale Callback eine Controller-Property wie
`is_closing` ab, versucht er denselben nicht-reentranten Lock erneut zu
erwerben.

Gezielter Thread-Nachweis:

```text
DUPLICATE_CALLBACK_DEADLOCK True
```

Callbacks dürfen niemals unter dem internen Lifecycle-/Deduplizierungslock
ausgeführt werden.

## 5. Shutdown ist nicht idempotent

`shutdown()` erkennt `already_closing`, führt danach aber mit `pass` denselben
Stopablauf erneut aus.

Gezielter Nachweis nach zwei Shutdown-Aufrufen mit Zähl-Fakes:

```text
DOUBLE_SHUTDOWN_COUNTS 2 2 2
```

Audio, Session und Queue werden jeweils zweimal gestoppt. Der Vertrag verlangt
genau einmal, wiederholbar sicher und auch bei konkurrierenden Aufrufen
deterministisch. Ein vorheriger Timeout-/Fehlerstatus muss für spätere
Aufrufer sichtbar bleiben.

## 6. Verbindliche Controlleroberfläche fehlt

Der Paketvertrag verlangt:

- gewünschten Diktierzustand getrennt vom Transportzustand;
- semantisches Aktivieren/Deaktivieren oder Toggeln;
- UI-neutral abfragbaren Controllerstatus.

Tatsächlich fehlen alle geprüften Oberflächen:

```text
SEMANTIC_API False False False False
```

für `start_dictation`, `stop_dictation`, `toggle_dictation` und `get_status`.
AP4 soll keinen Hotkey implementieren, muss aber genau diese semantische
Oberfläche für AP6 bereitstellen. AP5-Reconnect-Wiederaufnahme bleibt
weiterhin ausgeschlossen.

## 7. Run-Loop und Task-Cleanup sind nicht robust

`run()`:

- erstellt Tasks vor dem geschützten `try`;
- wartet mit `FIRST_EXCEPTION`;
- behandelt ein normales Ende von `session.run()` deshalb nicht als
  Beendigungsgrund, solange Endlostasks weiterlaufen;
- cancelt und awaited ausstehende Core-Tasks im `finally` nicht;
- verschluckt `CancelledError`;
- räumt bei Fehlern während der Task-Erstellung nicht vollständig auf.

Der aktuelle `tests.test_app`-Run-Loop-Test belegt zudem keinen echten sauberen
Lifecycle, weil er den notwendigen Shutdown ersetzt und dadurch den Worker
leakt.

## 8. Weitere fehlende Pflichtfälle

Die 20 angelegten Tests decken mehrere ausdrücklich verlangte Risiken nicht
ab:

- parallele doppelte Finalcallbacks;
- Queue bereits gestoppt;
- `enqueue()` liefert mit einer injizierten Queue `False`;
- Attempt-Protokollierung schlägt zusätzlich fehl;
- vorhandener History-Duplikatfall;
- Shutdown stoppt jede Komponente exakt einmal;
- Shutdown bei wartenden Jobs;
- Start-/Shutdown-Konkurrenz;
- Finalevents rund um einen Sessionwechsel;
- Controllerstatus und semantische Diktierbefehle;
- sauberes Ende und Cleanup aller von `run()` gestarteten Tasks;
- belastbarer Nachweis, dass `app.py` den Controller ohne Workerleak
  tatsächlich verwendet.

## 9. Dokumentationswidersprüche

Trotz nicht reproduzierbarer Abnahme wurden AP4 und 123 Tests als
abgeschlossen dokumentiert. Zusätzlich stehen weiterhin gegenteilige alte
Aussagen in aktiven Dateien:

- `docs/IMPLEMENTATION_ROADMAP.md`: „Aktives nächstes Paket: AP4“, während AP4
  im selben Dokument als abgeschlossen markiert ist;
- `task.md`: „Nächstes Paket: AP4“, während Phase 4 abgeschlossen heißt;
- `docs/PROJEKTUEBERSICHT.md`: Abschnitt „Noch nicht integriert“, alte
  103-Test-Abnahme und Schlusszusammenfassung nennen AP4 noch offen, während
  ein späterer Abschnitt AP4 abgeschlossen nennt;
- `ÜBERGABE.md`: enthält weiterhin den AP4-Einstieg, die alte 103-Testmatrix
  und „Vor AP4 ...“, obwohl oben 123 Tests/AP4 abgeschlossen behauptet werden;
- `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md`: Status abgeschlossen,
  aber die gesamte Abnahmecheckliste ist weiterhin `[ ]`.

Solange Code und Tests nicht korrigiert sind, darf kein aktives Dokument AP4
als abgenommen darstellen. Nach der Korrektur müssen alle alten
Vor-AP4-Aussagen entfernt oder klar als historische Baseline gekennzeichnet
und die Checkliste tatsächlich synchronisiert werden.

## 10. Scope-Kontrolle

Positiv:

- kein PySide6, Hotkey, Admin-Service oder Wake-Word-Override implementiert;
- keine neue Abhängigkeit;
- AP5-Reconnect-Härtung wurde nicht vorgezogen.

Die Korrektur kann vollständig innerhalb von AP4 bleiben.
