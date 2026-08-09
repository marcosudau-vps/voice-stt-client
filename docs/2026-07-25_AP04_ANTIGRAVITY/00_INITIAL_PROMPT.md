# AP04 – Initialauftrag an AntiGravity

Arbeite im Projektroot
`P:\DockerProjekte\RealtimeSTT_client` als verantwortlicher
Implementierungsagent. Setze ausschließlich **Arbeitspaket 4 –
Controller-Integration** vollständig, produktionsnah und testgestützt um.
Stoppe nach AP4. Beginne weder AP5 noch AP6 oder ein anderes Folgepaket.

Dies ist ein Ausführungsauftrag, kein reiner Planungsauftrag. Du sollst nach
der vorgeschriebenen Einarbeitung und Baseline die Implementierung, Tests,
Fehlerkorrekturen und Abschlussdokumentation selbstständig vollständig
durchführen.

## 1. Verbindlicher Hauptvertrag

Die operative, bereits fachlich geklärte Spezifikation steht vollständig in:

`docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`

Lies diese Datei vollständig und behandle insbesondere die Entscheidungen
E-01 bis E-04, den Implementierungsvertrag, die Fehlersemantik, die
Testmatrix, den Dokumentationsabschluss und das Abgabeformat als
verbindlich. Erfinde keine alternative AP4-Architektur und öffne keine dort
ausdrücklich ausgeschlossenen historischen oder evaluierenden Quellen.

## 2. Pflichtlektüre und Kontextdisziplin

Halte die in `AGENTS.md` und in Abschnitt 3 des Ausführungsauftrags
vorgegebene, kontextschonende Lesereihenfolge exakt ein:

1. kanonische Orientierung vollständig;
2. Ausführungsauftrag vollständig;
3. nur die ausdrücklich benannten Abschnitte des Paketvertrags;
4. Server-README und nur die ausdrücklich benannten
   Serverprotokollabschnitte;
5. die ausdrücklich benannten Implementierungs- und Testdateien vollständig.

Lade nicht pauschal Archive, Chat-Exporte, datierte Übergabeordner,
`docs/evaluations/`, sämtliche Serverdokumente oder das gesamte Repository in
den Kontext. Nutze zunächst `rg`, Überschriften- und Symbolsuche.

Die Dateien in `docs/2026-07-25_AP04_ANTIGRAVITY/` sind Belege dieser
Ausführung und keine fachliche Quelle. Der vorliegende Prompt darf die
kanonischen Projektverträge nicht durch eine abweichende zweite Wahrheit
ersetzen.

## 3. Unverhandelbare Arbeitsregeln

- Verwende für jeden Python-Befehl ausschließlich
  `.\venv\Scripts\python.exe`.
- Führe vor der ersten Codeänderung die im AP4-Ausführungsauftrag verlangte
  Baseline aus. Erwartet sind 103 grüne Tests. Weicht sie ab, untersuche den
  Grund vor Änderungen.
- Schütze den vorhandenen Core. Keine vorsorglichen Refactorings und keine
  Neuimplementierung funktionierender AP1–AP3-Komponenten.
- Keine Tests löschen, überspringen, abschwächen oder auf interne
  Implementierungsdetails zurechtbiegen, um die Suite grün zu bekommen.
- Keine neuen Abhängigkeiten ohne nachgewiesene, unvermeidbare Notwendigkeit.
- `.env`, Zugangsdaten und lokale Nutzerdaten weder lesen noch ausgeben.
- Keine echten Tastatureingaben, Clipboard-Pastes, Mikrofon- oder
  Serververbindungen in automatisierten Tests.
- Bestehende fremde Änderungen respektieren. Keine Dateien außerhalb des
  AP4-Umfangs bereinigen oder zurücksetzen.

## 4. Fachlicher Kern von AP4

Implementiere einen UI-neutralen Controller unter `core/` und binde ihn in
den tatsächlich verwendeten Headless-Startpfad in `app.py` ein. Ein gültiges,
neues rohes Serverevent `type == "final"` muss genau diesen Weg nehmen:

```text
final
  → validierte (sessionId, segmentId)-Identität
  → stabile History-Auflösung
  → höchstens ein automatischer Queue-Job
  → vorhandener Queue-Worker
  → genau ein finaler InjectionAttempt für den angenommenen Job
```

Besonders kritisch und vollständig testpflichtig:

- `on_event` mit dem rohen `final` ist die einzige autoritative
  Identitätsquelle;
- `realtime`, `on_text` und Timeline-`final_transcript` dürfen keinen
  History-Eintrag und keinen automatischen Enqueue erzeugen;
- Deduplizierung erfolgt logisch atomar pro `(sessionId, segmentId)`;
- identisches Duplikat und widersprüchliches Duplikat erzeugen niemals einen
  zweiten automatischen Queue-Job;
- eine fehlgeschlagene oder abgelehnte erste automatische Verarbeitung wird
  nicht durch ein Serverduplikat automatisch wiederholt;
- gleiche Segment-ID in anderer Session ist ein eigener Text;
- History-before-enqueue; ohne stabilen HistoryEntry kein automatischer
  Paste-Versuch;
- Queue-Ablehnung, Queue-Exception und zusätzliche Fehler beim
  Attempt-Protokollieren bleiben unterscheidbar und dürfen den
  Sessioncallback nicht hochreißen;
- Reinsertion verwendet den bestehenden Service, dieselbe History und
  denselben Queuepfad, erzeugt aber keinen neuen HistoryEntry;
- Start, Teilstartfehler, Shutdown, wiederholter Shutdown und
  Queue-Stop-Timeout sind deterministisch und testbar;
- nach `closing` werden keine neuen Finals oder Benutzerbefehle angenommen;
- alle sieben bestehenden Audio-Bridge-Regressionen bleiben semantisch
  erhalten;
- `app.py` verwendet den Controller tatsächlich und nicht nur nominell.

Beachte sämtliche feineren Anforderungen und zulässigen Statusnamen aus dem
Ausführungsauftrag. Die selektive SQLite-Politik bleibt bestehen; AP4 baut
keine Outbox. Implementiere keinen Hotkey, kein PySide6, kein Admin-Interface,
keinen Wake-Word-Override, keine neue Serverfunktion und keine
AP5-Reconnect-Härtung.

## 5. Qualitäts- und Testanspruch

Lege mindestens `tests/test_controller.py` an. Teste nicht nur Erfolgsfälle,
sondern gezielt die vulnerablen Übergänge:

- konkurrierende doppelte Finalcallbacks;
- reservierte Identität bei History-/Queuefehlern;
- Konflikttext derselben Identität;
- Sessionwechsel;
- Callback-Exceptions;
- Teilstart und Rollback;
- Stop-Reihenfolge, Idempotenz und Timeout;
- Finals/Befehle während Shutdown;
- gemeinsame Objektidentität von History in Queue und Reinsertion;
- keine Seiteneffekte aus Realtime/Timeline;
- echter `app.py`-Verdrahtungsnachweis ohne Netzwerk, Mikrofon oder Win32.

Nutze injizierbare Fakes und deterministische Synchronisation. Vermeide
zeitabhängige Flaky-Tests. Prüfe Observable Behavior, nicht zufällige
Implementierungsdetails.

Nach jeder relevanten Korrektur führe zuerst die gezielten Befehle aus
Abschnitt 8 des Ausführungsauftrags aus. Danach zwingend:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Führe abschließend außerdem den dort angegebenen `py_compile`-Befehl für
`app.py`, alle Core-Module und alle Testmodule aus. Debugge iterativ, bis
sämtliche ausführbaren Tests grün sind. Melde tatsächliche Testzahlen und
Laufzeiten, nicht erwartete Zahlen.

## 6. Dokumentationsabschluss

Synchronisiere nach grüner Gesamtsuite ausschließlich die im
AP4-Ausführungsauftrag verlangten aktiven Dokumente:

- `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md`
- `task.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `ÜBERGABE.md`
- `docs/PROJEKTUEBERSICHT.md`
- `README.md` nur, falls sich der reguläre Benutzerstart tatsächlich ändert

Markiere AP4 nur dann als abgeschlossen, wenn der tatsächliche Code und alle
Abnahmekriterien dies belegen. Entscheide oder implementiere E-07 nicht.

## 7. Runde-spezifische AntiGravity-Artefakte

Speichere deine eigenen Arbeitsartefakte dieser Initialrunde zusätzlich und
ohne andere Belege zu überschreiben unter:

`docs/2026-07-25_AP04_ANTIGRAVITY/00_initial/`

Erstelle dort mindestens:

1. `IMPLEMENTIERUNGSPLAN.md` – kurze, konkrete Skizze nach Einarbeitung und
   Baseline, einschließlich betroffener Schnittstellen und Teststrategie;
2. `WALKTHROUGH.md` – tatsächlich ausgeführter Ablauf, wesentliche
   Entscheidungen, aufgetretene Fehler und deren Korrekturen;
3. `ABSCHLUSSBERICHT.md` – vollständiger Bericht nach dem in Abschnitt 10 des
   AP4-Ausführungsauftrags verlangten Format, mit Befehlen, Testzahlen,
   Laufzeiten, geänderten Dateien, Scope-Abgrenzung und Restgrenzen.

Diese Dateien sind Belege, nicht kanonische Projektdokumentation. Schreibe
keine Zugangsdaten oder `.env`-Inhalte hinein.

## 8. Abschlussausgabe

Gib in deiner finalen CLI-Antwort zusätzlich kompakt an:

- ob AP4 nach deiner Einschätzung vollständig abnahmefähig ist;
- alle neu angelegten und geänderten Dateien;
- die konkrete Controller-API und Final-/Deduplizierungssemantik;
- gezielte Testbefehle mit Zahl und Laufzeit;
- Gesamtsuite mit Zahl und Laufzeit;
- `py_compile`-Ergebnis;
- ausdrücklich nicht implementierte Folgepakete;
- bekannte Restrisiken und manuelle Prüfungen.

Stoppe danach. Beginne nicht mit AP5 oder AP6.
