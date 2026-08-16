# AP04 – Korrekturrunde 2

AP4 ist nach Korrekturrunde 1 noch nicht abnahmefähig. Behebe ausschließlich
die reproduzierten Restmängel aus:

`docs/2026-07-25_AP04_ANTIGRAVITY/PRUEFBERICHT_01_KORREKTUR.md`

Lies außerdem die betroffenen Abschnitte in
`docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md` und
die tatsächlich zu ändernden Module/Tests. Öffne keine Archive oder E-07.
Beginne weder AP5 noch AP6. Verwende nur `.\venv\Scripts\python.exe`.

## 1. Reale Run-Loop-Semantik reparieren

Der erfolgreiche Abschluss von `_auto_start_when_ready()` darf `run()` nicht
beenden. Implementiere und teste folgende Semantik:

- Solange `session.run()` regulär läuft, bleibt der Controller aktiv.
- Erfolgreiches einmaliges Ende des Auto-Start-Helpers wird aus der aktiven
  Taskmenge entfernt und ansonsten ignoriert.
- Normales Ende von `session.run()` beendet `run()` kontrolliert.
- Unerwartetes normales Ende des Audio-Senders oder eine Exception eines
  Hilfstasks wird als auswertbarer Fehler sichtbar und löst Cleanup aus.
- Task-Erzeugung gehört in den geschützten Lifecyclebereich; auch ein Fehler
  nach nur einem oder zwei erzeugten Tasks räumt alles Erzeugte auf.
- Im `finally` werden alle verbleibenden Tasks gecancelt und awaited.
- `_loop` wird in jedem Pfad freigegeben.
- `shutdown()` wird genau einmal über den gemeinsamen Mechanismus ausgeführt.

Pflichttest: Eine Fake-Session bleibt offen, Auto-Start wird erfolgreich
abgeschlossen, und `run()` muss danach nachweislich weiterlaufen. Erst ein
kontrolliertes Sessionende oder Cancel darf den Run-Task beenden. Der Test
darf nicht mit unkontrollierten Sleeps arbeiten; nutze Events.

## 2. Wirklich idempotenter konkurrierender Shutdown

Zwei oder mehr überlappende `shutdown()`-Aufrufe müssen dieselbe laufende
Shutdown-Operation beobachten, statt sie doppelt auszuführen.

- Jede gestartete Komponente exakt einmal stoppen.
- Alle wartenden Aufrufer erhalten dasselbe erfolgreiche Ergebnis oder
  denselben gespeicherten Fehler.
- Kein blockierendes Warten unter `threading.Lock`.
- Funktioniert für konkurrierende Tasks auf der besitzenden asyncio-Loop.
- Wiederholter späterer Aufruf bleibt ebenfalls sicher.
- Queue-Timeout bleibt für alle Aufrufer sichtbar.

Ergänze einen deterministischen Event-gesteuerten Test, der den ersten
`session.stop()` blockiert, während ein zweiter Shutdown startet. Erwartung:
Audio-/Session-/Queue-/Cleanup-Zähler jeweils exakt 1.

## 3. Finalidentität vor History atomar reservieren

Reserviere `(sessionId, segmentId)` logisch atomar unter dem Controllerlock,
bevor irgendein potentiell langsamer oder fehlschlagender History-Aufruf
beginnt.

Verbindlich:

- Der erste gültige Callback besitzt die Identität.
- Jeder parallele oder spätere gleiche Servercallback ist Duplikat und darf
  den History-/Queuepfad nicht erneut betreten.
- Das gilt auch, wenn der erste History-Aufruf blockiert, `UNAVAILABLE`
  liefert oder wirft.
- Konflikttext bleibt sichtbar.
- Externe Callbacks weiterhin nie unter Lock.

Ergänze genau den deterministischen Fehler-Race-Test aus dem Prüfbericht:
erster History-Aufruf blockiert und schlägt später fehl; ein paralleles
Duplikat darf keinen zweiten History-Aufruf und keinen Enqueue auslösen.

## 4. Asynchron ehrliche semantische Diktierbefehle

Entferne die fehlerhafte Fire-and-forget-Hilfslogik. Die Controllerbefehle
sollen als klare asyncio-Core-API erst dann ein `CommandResult` liefern, wenn
der zugehörige `send_start()`-/`send_stop()`-Vorgang abgeschlossen oder
fehlgeschlagen ist. Eine spätere AP6-Brücke kann diese Coroutinen per
`run_coroutine_threadsafe` einreichen; diese Brücke selbst gehört nicht zu
AP4.

Empfohlene und bevorzugte Form:

```python
async def start_dictation(...) -> CommandResult
async def stop_dictation(...) -> CommandResult
async def toggle_dictation(...) -> CommandResult
```

Anforderungen:

- keine unbeobachteten Hintergrundtasks;
- kein `success=True` vor einem späteren `send_start`-/`send_stop`-Fehler;
- `start`-Fehler wird als Fehlerresultat sichtbar und Audio wird kontrolliert
  zurückgebaut;
- der gewünschte Diktierzustand bleibt getrennt und eindeutig;
- Startwunsch bei noch nicht bereitem Transport bleibt als Wunsch merkbar,
  liefert aber einen klaren Status;
- Stop vor `READY` verhindert späteren Auto-Start;
- `_auto_start_when_ready()` startet nur, wenn der gewünschte Zustand aktiv
  ist;
- das bisherige Headless-Autostartverhalten bleibt erhalten, indem
  `RealtimeSTTClient` den initialen Wunsch explizit setzt – nicht indem der
  neutrale Controller jeden Stop-Wunsch überschreibt;
- keine AP5-Reconnect-Wiederaufnahme implementieren.

Ergänze Tests innerhalb einer laufenden Event-Loop für Erfolg, asynchronen
Fehler, Audio-Rollback, Stop vor READY und Headless-Initialwunsch.

## 5. History-Randfall korrekt klassifizieren

Wenn `add_entry_with_status()` `ALREADY_EXISTS` mit `entry=None` zurückgibt,
ist dies ein bekanntes, nach Retention nicht mehr auflösbares Duplikat:

- kein Enqueue;
- `FinalProcessingStatus.DEDUPLICATED`;
- `entry_id=None`;
- klarer Reason wie `duplicate_entry_evicted`;
- nicht fälschlich `history_unavailable`.

Ein echtes `UNAVAILABLE` bleibt davon getrennt. Ergänze History- und
Controller-Test mit kleiner Memory-Grenze und ohne Persistenz.

## 6. App-Tests vollständig von Benutzerdaten isolieren

Erweitere `RealtimeSTTClient` minimal um eine saubere
Dependency-Injection-Oberfläche für die bereits vom Controller akzeptierten
Komponenten, oder verwende eine gleichwertig kleine Lösung.

Alle Tests in `tests/test_app.py` müssen:

- vor der Konstruktion einen temporären DB-Pfad verwenden;
- Session, Audio, History, Queue und Reinsertion konsistent injizieren;
- keine echte `%LOCALAPPDATA%`-History öffnen/erzeugen;
- kein Mikrofon, Netzwerk, Clipboard oder Win32 verwenden;
- die echte Headless-Controllerverdrahtung und das Lifecycleverhalten dennoch
  prüfen.

Teste zusätzlich, dass Queue und Reinsertion dieselbe injizierte History
verwenden.

## 7. Dokumente wirklich synchronisieren

Während der Korrektur AP4 als `[IN ARBEIT]` behandeln. Erst nach allen grünen
Tests:

- Roadmap: nächstes Paket AP5, nicht AP4;
- `task.md`: nächstes Paket AP5; alte „folgt in AP4“-Punkte korrigieren;
- Projektübersicht: Vor-AP4-Abschnitt entweder klar historisch kennzeichnen
  oder auf Iststand bringen; falsche Schlusszusammenfassung ersetzen;
- Übergabe: alten AP4-Einstieg in aktuellen AP5-/Weiterarbeitseinstieg
  umwandeln; 103 nur klar als Vor-AP4-Baseline;
- AP4-Paketdatei: erfüllte Abnahmecheckliste tatsächlich `[x]` markieren und
  gewählte API/Lifecycle-Semantik dokumentieren;
- überall dieselbe tatsächlich unabhängig reproduzierbare Testzahl;
- E-07 unverändert lassen.

Suche nach der Aktualisierung gezielt mit `rg` nach alten aktiven Aussagen:

```text
Nächstes Paket: AP4
Aktives nächstes Paket: AP4
folgt in AP4
AP4 ist deshalb das nächste Paket
Vor AP4
[ ] in der AP4-Abnahmecheckliste
```

## 8. Verifikation

Jeder Prozess muss selbst enden:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_history -v
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
.\venv\Scripts\python.exe -m unittest tests.test_app -v
.\venv\Scripts\python.exe -m unittest tests.test_text_injector tests.test_reinsertion
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Danach `py_compile` gemäß AP4-Ausführungsauftrag. Melde echte Zahlen und
Laufzeiten.

## 9. Rundenartefakte

Speichere unter
`docs/2026-07-25_AP04_ANTIGRAVITY/02_korrektur/`:

- `KORREKTURPLAN.md`
- `WALKTHROUGH.md`
- `ABSCHLUSSBERICHT.md`

Der Abschlussbericht ordnet jeden Befund aus
`PRUEFBERICHT_01_KORREKTUR.md` einer konkreten Änderung und einem Test zu.

Stoppe danach. Beginne nicht mit AP5 oder AP6.
