# AP04 – Korrekturrunde 1

Setze ausschließlich die nachfolgend belegten Mängel der AP4-Initialrunde
sauber und vollständig instand. Beginne weder AP5 noch AP6. Verwende dieselbe
AntiGravity-Sitzung und das Modell `gemini-3.6-flash-high`.

Lies zuerst vollständig:

1. `docs/2026-07-25_AP04_ANTIGRAVITY/PRUEFBERICHT_00_INITIAL.md`
2. `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`
3. die tatsächlich betroffenen Implementierungs- und Testdateien

Historische Archive, Chat-Exporte und E-07 nicht öffnen. Verwende für alle
Python-Befehle nur `.\venv\Scripts\python.exe`.

## 1. Zuerst falschen Abschlussstatus zurücknehmen

Bis alle nachstehenden Korrekturen reproduzierbar grün sind, behandle AP4 als
`[IN ARBEIT]`. Lass keine aktive Datei einen nicht belegten Abschluss oder
123 grüne Tests behaupten.

## 2. Tests dürfen niemals Prozesse oder Worker hängen lassen

Korrigiere `tests/test_controller.py` und `tests/test_app.py` so, dass jeder
Test unabhängig vom Ergebnis alle gestarteten nicht-daemonisierten Worker und
Async-Tasks sicher beendet.

Insbesondere:

- teste Queue-Stop-Timeout mit einem kontrollierten Fake, nicht durch
  irreversibles Abklemmen des Stop-Signals eines echten Workers;
- ersetze bei Lifecycle-/Run-Loop-Tests reale Win32-/Queue-Komponenten durch
  injizierte, zählende Fakes;
- kein Test darf auf echte Clipboard-, Mikrofon- oder Netzwerkfunktionen
  zugreifen;
- nach jedem gezielten Testkommando muss der Python-Prozess von selbst enden;
- ergänze einen expliziten Nachweis, dass kein Test-Worker zurückbleibt.

## 3. E-02/E-03: History-Ergebnis eindeutig machen

Führe die kleinstmögliche rückwärtskompatible History-Erweiterung ein, die
mindestens unterscheidet:

- Entry neu angelegt;
- Entry bereits vorhanden/aufgelöst;
- History nicht verfügbar.

Die bestehende öffentliche `add_entry()`-Semantik muss erhalten bleiben.
Controller und neue Tests sollen die eindeutige API verwenden.

Verbindliches Verhalten:

- nur ein wirklich neu angelegter zulässiger Finaltext darf automatisch
  enqueued werden;
- ein bereits in der History vorhandenes `(sessionId, segmentId)` wird nicht
  erneut enqueued;
- identischer vorhandener Text wird als Duplikat gemeldet;
- abweichender vorhandener Text wird als Konflikt gemeldet;
- Resultattext, Entry-ID und tatsächlich enqueued Text dürfen sich nicht
  widersprechen;
- „nicht verfügbar“ bleibt `history_unavailable`, ohne Enqueue;
- die reservierte Finalidentität bleibt auch nach History-/Queuefehlern
  reserviert, sodass ein Serverduplikat keinen automatischen Retry auslöst.

Ergänze gezielte AP1-Regressionstests für die neue History-API und
Controller-Tests für identischen sowie widersprüchlichen, bereits vorhandenen
Historyeintrag.

## 4. Lock- und Parallelitätssicherheit

- Führe niemals externe Callbacks aus, während ein interner
  Lifecycle-/Deduplizierungslock gehalten wird.
- Ergänze einen deterministischen Test, in dem der Duplikat-Callback
  Controllerstatus abfragt; der Thread muss innerhalb eines festen Timeouts
  enden.
- Ergänze einen deterministischen Barrier-/Event-basierten Test für zwei
  parallele gleiche Finalcallbacks: genau ein History-Create und höchstens ein
  automatischer Enqueue.
- Vermeide schlafzeitbasierte Flaky-Tests.
- Schütze `start_queue()` gegen konkurrierende Doppelinitialisierung.

## 5. Vollständige semantische Controller-API und Status

Implementiere UI-neutral und ohne Hotkey-/Qt-Wissen:

- Controllerstatus abfragen;
- gewünschten Diktierzustand getrennt vom Transportzustand halten;
- Diktierwunsch aktivieren;
- Diktierwunsch deaktivieren;
- optional semantisch toggeln, falls dies die API konsistent hält.

Die API muss:

- während `closing` Befehle eindeutig abweisen;
- bei nicht bereitem Transport einen klaren UI-neutralen Status liefern;
- im Headless-Modus das bisherige automatische Startverhalten erhalten;
- Audio und vorhandene `STTSession.send_start()`/`send_stop()` sinnvoll
  koordinieren;
- keine AP5-Wiederaufnahme nach Reconnect implementieren oder vortäuschen;
- thread-/asyncio-kompatibel für die spätere AP6-Brücke beschrieben und
  getestet sein.

Nutze ein klares Ergebnis-/Statusmodell. Ein nacktes `bool` ohne Grund ist
nicht ausreichend.

## 6. Deterministischer Lifecycle und Run-Loop

Korrigiere Controller und Tests so, dass:

- Start genau einmal erfolgt, auch bei parallelen Aufrufen;
- Teilstartfehler alle bereits gestarteten Komponenten kontrolliert abbauen;
- Shutdown jede gestartete Komponente genau einmal stoppt;
- wiederholte und konkurrierende Shutdown-Aufrufe dasselbe abgeschlossene
  Ergebnis beziehungsweise denselben Fehler beobachten;
- Queue-Stop-Timeout sichtbar bleibt, ohne dass der Testprozess einen echten
  Worker leakt;
- alle von `run()` erzeugten Tasks im `finally` gecancelt und awaited werden;
- normales Ende von `session.run()` den Run-Loop kontrolliert beendet;
- Fehler eines Hilfstasks sichtbar werden und Cleanup auslösen;
- Fehler während Task-Erstellung ebenfalls Cleanup auslösen;
- `_loop` immer freigegeben wird;
- das Headless-SIGINT-/KeyboardInterrupt-Verhalten keinen nur geplanten
  Shutdown durch sofortiges `sys.exit()` abschneidet.

Verwende präzise Fakes und zählende Aufrufsnachweise. Verändere
`core/stt_session.py`, `core/audio_capture.py` oder AP1–AP3 nur, soweit die
rückwärtskompatible History-Ergebnis-API dies zwingend erfordert.

## 7. Fehlende Fehler- und Integrationsfälle

Ergänze mindestens Tests für:

- Queue bereits gestoppt;
- injizierte Queue liefert `False`;
- `enqueue()` wirft;
- Attempt-Protokollierung wirft zusätzlich;
- Final während Shutdown;
- Sessionwechsel vor/während/nach Finalevents;
- Reinsertionstatusfälle einschließlich `queue_unavailable` und `failed`;
- Reinsertion erzeugt keinen neuen Entry, darf aber zusätzliche Jobs/Attempts
  am bestehenden Entry erzeugen;
- Realtime, Timeline und `on_text` bleiben ohne History-/Enqueue-Seiteneffekt;
- `app.py` verwendet den Controller und beendet einen Fake-Lifecycle sauber;
- alle sieben Audio-Bridge-Regressionen bleiben semantisch erhalten.

## 8. Dokumentation erst nach echter grüner Abnahme

Nach erfolgreicher Korrektur:

- entferne alle im Prüfbericht genannten aktiven Widersprüche;
- setze Roadmap/Task/Übergabe/Projektübersicht und Paketvertrag auf denselben
  tatsächlichen Stand;
- markiere die AP4-Abnahmecheckliste nur für wirklich belegte Kriterien;
- kennzeichne die frühere 103-Testzahl klar als Vor-AP4-Baseline oder entferne
  sie dort, wo sie als aktueller Stand missverständlich ist;
- benenne das nächste Paket erst nach echter AP4-Abnahme als AP5;
- dokumentiere API, Lifecycle, History-Ergebnissemantik, konkrete Testzahlen
  und bekannte Grenzen;
- E-07 bleibt unberührt.

## 9. Verifikation

Führe einzeln aus und stelle sicher, dass jeder Prozess selbst endet:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_history -v
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
.\venv\Scripts\python.exe -m unittest tests.test_app -v
.\venv\Scripts\python.exe -m unittest tests.test_text_injector tests.test_reinsertion
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Danach den vollständigen `py_compile`-Befehl aus dem AP4-Ausführungsauftrag.
Melde echte Zahlen und Laufzeiten. Ein Testlauf, der nur wegen externem
Timeout endet, ist fehlgeschlagen.

## 10. Rundenartefakte

Speichere ohne Überschreiben früherer Belege unter:

`docs/2026-07-25_AP04_ANTIGRAVITY/01_korrektur/`

mindestens:

- `KORREKTURPLAN.md`
- `WALKTHROUGH.md`
- `ABSCHLUSSBERICHT.md`

Der Abschlussbericht muss jeden Befund aus
`PRUEFBERICHT_00_INITIAL.md` einer konkreten Code-/Testkorrektur zuordnen,
alle geänderten Dateien nennen und ausdrücklich erklären, ob AP4 nun
abnahmefähig ist.

Stoppe danach. Beginne nicht mit AP5 oder AP6.
