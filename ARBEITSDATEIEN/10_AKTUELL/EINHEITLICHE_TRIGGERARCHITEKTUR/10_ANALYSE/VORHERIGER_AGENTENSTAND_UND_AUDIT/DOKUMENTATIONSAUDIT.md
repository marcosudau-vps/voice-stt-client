# Dokumentationsaudit – alle drei Repositories

**Datum:** 2026-08-14
**Ziel:** Nach dem Umbau darf keine aktive Dokumentation mehr die alte
Architektur als aktuellen Zustand beschreiben.

**Methode:** gezielte Suche nach den Begriffen der alten Architektur
(`Betriebsmodus`, `Hotkey-Modus`, `Wake-Word-Modus`, `session.mode`,
`fullSentence`, alte Queryparameter, alte Capability-/Eventnamen) in Markdown,
READMEs, Guides, Beispielkonfigurationen, Settings-Metadaten und
Codekommentaren — anschließend **jede Fundstelle gegen den tatsächlichen Code
geprüft**, statt Texte mechanisch zu ersetzen.

---

## Repository: voice-stt-server

**Geprüfte relevante Dokumentationsbereiche**

- `docs/` vollständig (ohne `docs/.archiv/`, siehe unten)
- `docs/client-development/` (10 Dateien, der Client-Vertrag)
- `README.md`, `AGENTS.md`
- `app_browserclient/` (Beispielclient: `client.js`, `index.html`)
- Codekommentare und Docstrings in `VoiceSTT/` und `api_fastapi_server/`

**Aktualisierte Dateien**

| Datei | Änderung |
| --- | --- |
| `docs/einheitliche-triggerarchitektur.md` | **neu** – die vollständige Architekturbeschreibung mit Mermaid-Diagrammen |
| `docs/README.md` | verlinkt die neue Architekturdokumentation |
| `docs/client-development/09-betriebsmodi-und-serverkonfiguration.md` | Kopf vollständig neu: „Triggerquellen statt Betriebsmodi", drei gültige Kombinationen, expliziter Legacy-Abschnitt; Restabschnitte entstaubt |
| `docs/client-development/02-websocket-protokoll.md` | **neu:** Triggerparameter, Capability-Vertrag, Triggerkommandos mit vollständiger `reason`-Tabelle, Idempotenz, Clientregel, Kollisionsdiagramm; `trigger` in der Befehlstabelle |
| `docs/client-development/03-server-events-kurzreferenz.md` | `trigger_ack` als zwölfter Typ; `activation_started/extended/closed`; Korrelationsfelder `activationId`, `primarySource`, `sources` |
| `docs/client-development/04-server-events-katalog-und-chronologie.md` | `activationConfig` in der `hello`-Feldtabelle; `sessionCapabilities` nennt `activationTriggers`; „Wake-Word-Modus" → „Wake-Word-Profil" |
| `docs/client-development/README.md` | Regel 6 ersetzt (Triggerquellen statt Wake-Word-Modus), Index angepasst |
| `docs/session-wakeword-erweiterung.md` | „Wake-Word-Modus" → „Wake-Word-Profil"; Satz über den „einzigen Betriebsmodus" korrigiert |
| `docs/stt-server-specification.md` | kontinuierliches Streaming nicht mehr an einen Modus gebunden, Verweis auf die neue Architektur |
| `app_browserclient/client.js` | **funktional repariert**: `/ws/transcribe`, `start`, `realtime`/`final`, vollständige Audiometadaten |
| `app_browserclient/index.html` | unbenutztes socket.io entfernt, unvollständiges `div` geschlossen |
| `docs/.archiv/einheitliche_triggerarchitektur/2026-08-14_SOLL_IST_PRUEFUNG.md` | **neu** – von `AGENTS.md` verlangte Soll-/Ist-Prüfung und Abweichungsbegründung |

**Entfernte beziehungsweise korrigierte veraltete Aussagen**

- „Der Server unterstützt zwei typische Desktop-Betriebsarten" als aktueller
  Zustand.
- Die Gegenüberstellungstabelle „Hotkey-Modus gegen Wake-Word-Modus" als
  Architekturbeschreibung (jetzt ausdrücklich als Legacy gekennzeichnet).
- „Im Hotkeymodus ereignisgesteuert, im Wake-Word-Modus einmalig `start`".
- „Der Wake-Word-Modus wird beim Verbindungsaufbau festgelegt."
- „Nach `start` muss der Client **im Wake-Word-Modus** kontinuierlich Audio
  übertragen."
- Im Beispielclient: Verbindung auf den Wurzelpfad, fehlender `start`,
  Nachrichtentyp `fullSentence`, unvollständige Audiometadaten.

**Neu dokumentierte Architekturthemen**

Gesamtarchitektur, Stream- und Activation-Lifecycle, Activation-Daten
(`activationId`, `generation`, `version`, `primarySource`, `sources`),
Kollisionssemantik, Controlled Recorder Gate mit Generationsbindung,
Trigger-/Ack-Vertrag mit Idempotenz und Fehlersemantik, Capability-Vertrag,
IDs und Korrelation, Events, Legacykompatibilität, Migration, Rollback,
Privacy des kontinuierlichen Streamings, Troubleshooting.

**Bewusst erhaltene Legacy-Dokumentation**

- `docs/client-development/09-…`: eigener Abschnitt „Legacy-Verhalten" —
  eine Session ohne Triggerparameter verhält sich unverändert.
- `docs/.archiv/`: historische Planungen bleiben unverändert; die Archivregel
  verbietet ausdrücklich das stillschweigende Umschreiben. Ergänzt wurde nur
  eine **neue datierte** Soll-/Ist-Prüfung.
- Der Beispielclient bleibt bewusst ein Legacyclient (sendet keine
  Triggerparameter) und ist damit zugleich die Kompatibilitätsreferenz.

**Offene Dokumentationspunkte**

Keine.

---

## Repository: voice-stt-client

**Geprüfte relevante Dokumentationsbereiche**

- `README.md`, `AGENTS.md`
- `docs/guides/`, `docs/decisions/`, `docs/archive/`, `docs/evaluations/`
- `server-docs-for-client-development/` (die gespiegelte Serververtragsdoku)
- `config.yaml` als ausgelieferte Beispielkonfiguration
- `core/settings_metadata.py` (die im Einstellungsdialog sichtbaren Texte)
- Codekommentare in `core/` und `ui/`

**Aktualisierte Dateien**

| Datei | Änderung |
| --- | --- |
| `README.md` | Bedienung, Trayfarben und Sessionaufbau auf Triggerquellen umgestellt; Migrationsregel ergänzt |
| `config.yaml` | Triggerschalter, Activation-Zeitwerte und Migrationsregel dokumentiert; `mode` ausdrücklich als Legacy-Feld gekennzeichnet; Kommentar am Diktatfenster korrigiert |
| `core/settings_metadata.py` | `session.mode` heißt jetzt „Legacy-Betriebsmodus" und liegt in der Gruppe „Legacy" |
| `docs/guides/feedback_konfigurieren.md` | Indikatorfarbe hängt an den Triggerflags, nicht an `session.mode` |
| `docs/guides/feedback_system.md` | dieselbe Korrektur im Erklärtext |
| `docs/decisions/ADR-001_BETRIEBSMODI_HOTKEY_UND_WAKE_WORD.md` | als **abgelöst** markiert, mit Verweis auf die neue Architektur; Inhalt unverändert erhalten |
| `server-docs-for-client-development/*` (11 Dateien) | vollständig aus dem Serverrepo gespiegelt |

**Dabei gefundene und behobene Code-Inkonsistenz**

Die Guides beschrieben korrekt, was der Code tat — und der Code war falsch:
`ui/presentation.py` verzweigte über `snapshot.operating_mode`, gespeist aus dem
Legacy-Feld `session.mode`. Eine Session mit `wake_word_trigger_enabled=true`
bei unverändertem `mode: hotkey` hätte „Wartet auf Hotkey" angezeigt. Ergänzt
wurde `SessionConfig.presentation_mode`, das die Anzeige aus den **effektiven
Triggerflags** ableitet; `core/controller.py` und `ui/application.py` benutzen
es jetzt.

**Entfernte beziehungsweise korrigierte veraltete Aussagen**

- „im Hotkeymodus Diktierung starten … im Wake-Word-Modus Betrieb aktivieren".
- „dunkelgrün / hellgrün: Hotkeymodus wartet / nimmt auf" (analog blau).
- „Der Hotkeymodus fordert `wakeWordEnabled=false`; der Wake-Word-Modus fordert
  `wakeWordEnabled=true`."
- „Die Farbe hängt zusätzlich am Betriebsmodus (`session.mode`)."
- „Ausschließlich im Hotkeymodus" als Kommentar über `dictation_window`.

**Bewusst erhaltene Legacy-Dokumentation**

- `docs/archive/` und `docs/evaluations/`: datierte historische Dokumente,
  teils bereits im Dateinamen als `VERWORFEN` gekennzeichnet. Sie beschreiben
  ausdrücklich vergangene Stände und bleiben unverändert.
- `docs/decisions/ADR-001`: bleibt als Entscheidungshistorie erhalten, ist aber
  jetzt sichtbar als abgelöst markiert.
- `session.mode` bleibt als Feld erhalten, weil alte Konfigurationsdateien
  weiterhin korrekt migriert werden müssen.

**Offene Dokumentationspunkte**

Keine.

---

## Repository: led_controller_respeaker-v3

**Geprüfte relevante Dokumentationsbereiche**

- `README.md`, `HANDOFF.md`, `PLAN.md`
- `docs/` vollständig, insbesondere `docs/guides/` und `docs/konzepte/`
- `config.example.yaml`

**Aktualisierte Dateien**

Keine.

**Begründung**

Die Suche nach Begriffen der alten Triggerarchitektur (`Betriebsmodus`,
`Hotkey-Modus`, `Wake-Word-Modus`, `session.mode`, `trigger_ack`,
`activationId`) liefert im gesamten LED-Repository **keinen Treffer**.

`wakeword_detected` kommt vor, ist dort aber ein **Effekt- beziehungsweise
Eventname des LED-Katalogs**, kein Triggerbegriff der Sprachanwendung. Dieser
Name ist unverändert gültig: die Triggerarchitektur führt kein neues LED-Verb,
kein neues Preset und kein neues Effektziel ein. Der Manualtrigger benutzt über
das Client-Mapping (`client.hotkey.accepted`) denselben bestehenden
LED-Effekt — diese Zuordnung ist im Clientrepo dokumentiert, nicht hier.

Damit gilt: Das LED-Repository beschreibt keine veraltete Architektur, und der
Auftrag sieht dort auch keine Produktcodeänderungen vor. Es blieb während der
gesamten Aktion unverändert (`git status --short` liefert null Zeilen).

**Offene Dokumentationspunkte**

Keine.

---

## Cross-Repository-Konsistenz

> **Sind Trigger-, Config-, Lifecycle-, Event- und Feedbackverträge über alle
> drei Repositories konsistent?**

**Ja**, mit den folgenden geprüften Belegen:

| Vertragsteil | Server | Client | LED |
| --- | --- | --- | --- |
| Triggernamen `manual` / `wake_word` | `ACTIVATION_SOURCES_PUBLIC`, Doku 02/09 | `SessionConfig`, README, `config.yaml` | n/a |
| Actions `activate/extend/finish/cancel` | `TRIGGER_ACTIONS`, Doku 02 | `send_trigger`, `request_trigger` | n/a |
| Queryparameter | `SESSION_ACTIVATION_QUERY_FIELDS`, Doku 02/09 | `SessionConfig.query_parameters()` | n/a |
| Capability `activationTriggers` | `session_capabilities()`, Doku 02 | `supports_activation_triggers` | n/a |
| Ack-Format und `reason`-Werte | `handle_trigger_command`, Doku 02 | `TriggerAck`, Pendingverwaltung | n/a |
| IDs `activationId` / `generation` / `commandId` | Doku 02/07 der Architekturdatei | Ack-Korrelation, Generationsprüfung | n/a |
| Eventnamen `activation.*` | Timeline- und Structured-Mapping, Doku 03 | Reducer nutzt bestehende kanonische Events | n/a |
| Lifecycle-Semantik (`start`/`stop` bleiben Streambefehle) | Doku 02/09 | `_begin_stream_and_trigger`, README | n/a |
| Legacy-Verhalten | Doku 09 Abschnitt „Legacy-Verhalten" | README-Migrationsregel, `config.yaml` | n/a |
| Feedback-/LEFX-Vertrag | – | `feedback_mapping`, `config.yaml` | Effekt-/Presetnamen unverändert |

**Mechanisch abgesichert:** Die 11 Dateien unter
`voice-stt-client/server-docs-for-client-development/` sind **inhaltlich
identisch** mit `voice-stt-server/docs/client-development/` (verifiziert per
`diff` nach Normalisierung der Zeilenenden). Dieselbe Schnittstelle wird damit
nicht in zwei Repositories unterschiedlich beschrieben.

**Automatisch geprüft:** `tests/unit/test_browser_client_contract.py` hält den
ausgelieferten Beispielclient gegen den tatsächlichen Serververtrag; ein
Zurückfallen auf die alte Beschreibung würde 12 Prüfungen rot machen.


---

## Nachtrag: Cleanup der Abschlussdokumentation

Nach dem Einfrieren der Implementierung wurden die Abschlussdokumente noch
einmal gegeneinander geprüft. Bereinigt wurden:

| Fundstelle | veraltete Aussage | jetzt |
| --- | --- | --- |
| `CONTRACTS.md` C-09 | Browserclient „verbindet auf den Wurzelpfad … vorbestehend" | Client ist angepasst und automatisiert abgesichert; offen ist allein der Browserlauf |
| `CONTRACTS.md` C-06 | „Simulator … hier nicht ausführbar" | **PASS**, automatisiert mit echtem `QApplication` |
| `CONTRACTS.md` C-06 | „echter ReSpeaker … Hardware nicht vorhanden" | Gerät **angeschlossen**, wegen Zugriffsrechten/Treiber nicht erreichbar |
| `CONTRACTS.md` Übersicht | „Simulator und ReSpeaker offen" | „echter ReSpeaker offen" |
| `REPORT.md` Risiko 2 | „Browserclient nicht geprüft … Wurzelpfad" | realer Browserlauf offen, Rest automatisiert abgesichert |
| `VALIDATION.md` M-4 | LED-Simulator in der Liste der manuellen Szenarien | entfernt, mit Verweis auf den automatisierten Nachweis |
| `VALIDATION.md` M-5 | Browserclient als unrepariert beschrieben | Verweis auf GATE 5 / M-B1 |
| `VALIDATION.md`, `REPORT.md` | Buildangaben eines früheren Zwischenbuilds | der tatsächlich letzte finale Build mit Pfad, Größe, SHA-256 und Smoke-Test |
| `VALIDATION.md` | Darstellungsfehler `distoice-stt-client.exe` | korrigiert |
| `voice-stt-client/docs/decisions/ADR-001_…md` | zwei abschließende Leerzeichen in Zeile 3 | entfernt |

Alle sieben Abschlussdokumente nennen denselben Gesamtstatus
`MANUELLE RESTABNAHME ERFORDERLICH` und dieselben Gate-Werte.
