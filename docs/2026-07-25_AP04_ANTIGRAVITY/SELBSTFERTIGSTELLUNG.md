# AP04 – unabhängige Selbstfertigstellung nach Korrekturrunde 3

## Anlass

Nach Initialauftrag und drei AntiGravity-Korrekturrunden verblieben die in
`PRUEFBERICHT_03_KORREKTUR.md` dokumentierten Mängel. Entsprechend dem
Benutzerauftrag wurden sie anschließend direkt fertiggestellt.

## Codekorrekturen

### `core/controller.py`

- Queue-Start-Rollback wird erfasst; `shutdown()` stoppt eine bereits
  erfolgreich zurückgerollte Queue nicht nochmals.
- Shutdown verwendet denselben Transition-Lock wie Start, Stop, Toggle und
  Auto-Start.
- Ein Final prüft `closing` unmittelbar und atomar bei der
  Identitätsreservierung erneut.
- Ein fehlgeschlagener Start setzt den Diktierwunsch nach Audio-Rollback
  zurück.
- Start- und Stop-Befehle verifizieren nach dem Await den tatsächlichen
  `session.is_streaming`-Zustand; stille Nichtausführung wird als Fehler
  gemeldet.
- Unerwartet gecancelte Hilfstasks werden als Lifecycle-Fehler sichtbar.
- Injizierte Queue und Reinsertion-Service werden auf dieselbe History- und
  Queue-Instanz geprüft.

### `tests/test_controller.py`

Die Controller-Suite wurde auf 46 Tests erweitert. Neu beziehungsweise
verschärft abgesichert sind:

- Fehler beim zweiten und dritten Task-Erzeugen ohne Task-Leak,
- Queue-Startfehler mit genau einem Queue-Rollback,
- Cancellation eines Shutdown-Waiters bei weiterlaufendem Cleanup,
- Shutdown während eines blockierten Startübergangs,
- Closing-Beginn zwischen Finalprüfung und Identitätsreservierung,
- deterministisch überlappender manueller Start/Stop,
- deterministisch überlappender Auto-Start/Stop,
- paralleles Toggle mit atomarer Zustandsentscheidung,
- stille Nichtumschaltung von `is_streaming` nach Start und Stop,
- unerwartete Cancellation eines Hilfstasks,
- Ablehnung inkonsistent injizierter History-/Queue-Abhängigkeiten.

Die Überlappungen werden mit Events und kontrollierten Freigabepunkten
erzeugt, nicht mit zufälligen Zeitfenstern.

## Dokumentationskorrekturen

Synchronisiert wurden:

- `task.md`,
- `docs/IMPLEMENTATION_ROADMAP.md`,
- `docs/PROJEKTUEBERSICHT.md`,
- `ÜBERGABE.md`,
- `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md`,
- `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`.

Dabei wurden AP4 als abgeschlossen und AP5 als nächstes Paket gekennzeichnet,
Testzahlen auf den realen Endstand gebracht, die AP5-Lesereihenfolge
klargestellt und der beschädigte Markdown-Block in `ÜBERGABE.md` repariert.

## Finale Tests

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
# Ran 46 tests in 1.908s
# OK

.\venv\Scripts\python.exe -m unittest tests.test_app -v
# Ran 9 tests
# OK

.\venv\Scripts\python.exe -m unittest tests.test_history tests.test_text_injector tests.test_reinsertion
# Ran 97 tests
# OK

.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
# Ran 152 tests in 4.996s
# OK
```

Danach:

```powershell
$ap4CompileTargets = @((Resolve-Path -LiteralPath app.py).Path)
$ap4CompileTargets += (Get-ChildItem -LiteralPath core -Filter *.py -File).FullName
$ap4CompileTargets += (Get-ChildItem -LiteralPath tests -Filter "test_*.py" -File).FullName
.\venv\Scripts\python.exe -m py_compile @ap4CompileTargets
# Exit-Code 0
```

Die während der Suite sichtbaren Fehlerlogs stammen aus bewusst provozierten
Negativtests.

## Scope

AP5, AP6 und E-07 wurden nicht implementiert. Es wurden weder reale
Servereinstellungen geändert noch unangekündigte Mikrofon-, Clipboard- oder
Tastatureingabetests ausgeführt.

