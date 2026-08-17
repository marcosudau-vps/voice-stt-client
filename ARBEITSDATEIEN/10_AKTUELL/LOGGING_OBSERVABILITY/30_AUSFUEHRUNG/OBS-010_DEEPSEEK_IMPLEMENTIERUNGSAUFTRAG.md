# OBS-010 – Implementierungsauftrag für DeepSeek

## Rolle

Du implementierst **OBS-010 – Canonical Model & Contracts** für das Logging-/Observability-V1 des `voice-stt-client`.

Die Architektur- und Readiness-Phase ist bereits abgeschlossen:
- OBS-000: PASS
- OBS-010: READY FOR IMPLEMENTATION
- OBS-010 READINESS REVIEW: PASS

Du sollst **nicht erneut grundlegend planen**, sondern den freigegebenen OBS-010-Scope umsetzen, testen und belastbare Evidence erzeugen.

---

## Session-Root

`P:\GithubRepos\marcosudau-vps`

## Schreibbarer Projektbereich

Ausschließlich:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Die folgenden Repositories sind für diesen Auftrag **read-only**, sofern du sie überhaupt zur Referenz brauchst:

- `P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\einheitliche-triggerarchitektur`
- `P:\GithubRepos\marcosudau-vps\led_controller_respeaker-v3\workspaces\einheitliche-triggerarchitektur`

Keine Änderungen an deren Working Trees.

---

## Verbindliche Arbeitsgrundlagen

Lies zuerst im Client-Workspace:

`ARBEITSDATEIEN\README.md`

`ARBEITSDATEIEN\AGENTS.md`

`ARBEITSDATEIEN\00_STEUERUNG\CURRENT_STATE.md`

`ARBEITSDATEIEN\00_STEUERUNG\MASTERPLAN.md`

`ARBEITSDATEIEN\00_STEUERUNG\ARBEITSPROZESS.md`

und vollständig die für OBS-010 relevanten Unterlagen unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\`

Insbesondere normative Grundlagen, Planungsunterlagen und das freigegebene Work Package für OBS-010.

Wenn Dateien einander widersprechen, gilt die dokumentierte Authority-Hierarchie aus `ARBEITSDATEIEN`. Historische, Draft- oder Analyseunterlagen dürfen normative Vorgaben nicht überschreiben.

---

# Verbindlicher OBS-010-Scope

OBS-010 implementiert das **kanonische Logging-/Observability-Datenmodell und die Contracts**.

Folgende bereits eingefrorenen Architekturentscheidungen sind verbindlich:

1. Logging ist strikt beobachtend und **niemals Runtime-/Lifecycle-Autorität**.
2. Canonical Record enthält mindestens die bereits spezifizierten Identitäts-, Zeit-, Producer-, Channel-/Level-/Type-/Component- und Korrelationsfelder.
3. Strukturierte Server-Events müssen verlustarm/lossless innerhalb der festgelegten Redaction-/Privacy-Grenzen repräsentierbar sein.
4. `raw` muss die in OBS-000 freigegebenen Typen unterstützen, einschließlich `frozenset`.
5. Für Python-Logs ist die festgelegte `session_id`-Quelle einzuhalten.
6. Für Controlframes ist die festgelegte `component`-Zuordnung einzuhalten.
7. `scope` muss gemäß Freeze korrekt und konsistent modelliert werden, einschließlich `led`.
8. Logging darf keine Business-Lifecycle-Logik nachbauen.
9. Keine Rekonstruktion von Lifecycle-Zuständen aus menschenlesbarem Logtext.
10. Bestehende Event-/Feedback-Pfade dürfen durch OBS-010 nicht funktional verändert werden.

Halte dich exakt an die im Projekt bereits vorhandenen OBS-010-Verträge, Feldnamen, Typen, Defaults, Enums und Validierungsregeln. Erfinde keine parallele zweite Schemawelt.

---

# Umsetzung

## 1. Vorher-Zustand festhalten

Vor Änderungen:

- `git status --short`
- aktuellen HEAD notieren
- vorhandene relevante Tests erfassen
- sicherstellen, dass der bekannte Baseline-Commit vorhanden ist

Erwarteter Client-HEAD zu Beginn:

`f3908cff01cebf54db76a492e0a95ae882a98a4d`

Wenn der HEAD davon unerwartet abweicht, **nicht resetten**. Befund dokumentieren und nur stoppen, wenn dadurch die sichere Umsetzung nicht mehr eindeutig ist.

---

## 2. Run-Verzeichnis

Lege für diesen Lauf an:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\RUN-OBS-010-01_2026-08-17_DEEPSEEK\`

Darin mindestens:

- `RUN_LOG.md`
- `RESULT.md`

`RUN_LOG.md` enthält kurz und fortlaufend:
- Startzustand
- umgesetzte Teilpunkte
- Tests
- Abweichungen/Entscheidungen
- Endzustand

Kein Roman, aber so vollständig, dass ein nachfolgender Reviewer den Lauf nachvollziehen kann.

---

## 3. Implementieren

Implementiere den freigegebenen OBS-010-Scope im bestehenden Client-Code.

Bevorzugt:
- vorhandene Module/Abstraktionen erweitern,
- klare Typen,
- deterministische Normalisierung,
- explizite Validierung,
- keine impliziten Nebenwirkungen,
- keine Logging-Selbstrekursion,
- keine Runtime-Abhängigkeit vom neuen Logging-Modell.

Keine Implementierung aus späteren Work Packages vorziehen, außer eine minimale Schnittstelle ist zwingend nötig, damit OBS-010 sauber kompiliert/testbar ist. Solche minimalen Vorgriffe explizit dokumentieren.

---

## 4. Tests

Erstelle/aktualisiere die für OBS-010 notwendigen Tests.

Mindestens abdecken:

- Canonical Record Konstruktion/Validierung
- Pflichtfelder und optionale Felder
- Enum-/Typvalidierung
- Zeit-/ID-Felder
- Producer-/Channel-/Level-/Type-/Component-/Scope-Semantik
- `raw` mit den freigegebenen Typen einschließlich `frozenset`
- strukturierte Details/Raw-Daten ohne unerlaubte Datenverluste
- Python-Log-Mapping gemäß Freeze
- Controlframe-Mapping gemäß Freeze
- Session-/Correlation-Felder
- ungültige Eingaben
- keine Mutation der übergebenen Payloads
- Regression: bestehende betroffene Tests weiterhin grün

Keine Tests schreiben, die nur die eigene Implementierung nacherzählen. Die Tests sollen die verbindlichen Contracts prüfen.

---

## 5. Evidence

Lege Evidence ab unter:

`ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\40_EVIDENCE\OBS-010\RUN-01_2026-08-17_DEEPSEEK\`

Mindestens:

- `TEST_RESULTS.md`
- `DIFF_SUMMARY.md`
- `CONTRACT_COVERAGE.md`

`CONTRACT_COVERAGE.md` soll die OBS-010-Anforderungen den konkreten Implementierungsstellen und Tests zuordnen.

---

## 6. Steuerungsdateien aktualisieren

Am Ende aktualisieren:

`ARBEITSDATEIEN\00_STEUERUNG\CURRENT_STATE.md`

`ARBEITSDATEIEN\00_STEUERUNG\LOG_VERLAUF.md`

`CURRENT_STATE.md` nur knapp:
- OBS-010 Implementierung abgeschlossen / Review ausstehend
- nächster Schritt: Claude Review / Gate

`LOG_VERLAUF.md` append-only um diesen Run ergänzen.

Nicht bereits abgeschlossene Historie umschreiben.

---

# Harte Grenzen

Nicht erlaubt:

- `git reset`
- `git clean`
- Rebase
- Merge
- Push
- Tag
- PR
- Commit
- Änderungen in Server-/LED-Repo
- Triggerarchitektur weiterbauen
- OBS-020 oder spätere Work Packages vollständig vorziehen
- Produktdokumentation außerhalb des notwendigen Arbeits-/Evidence-Trackings unnötig ändern

Der Working Tree darf am Ende bewusst Änderungen enthalten; diese werden erst nach Review/Gate weiterbehandelt.

---

# Abschlussprüfung

Vor Abschluss mindestens:

- vollständige relevante Tests
- `git diff --check`
- `git status --short`
- `git diff --stat`
- gezielte Prüfung, dass nur OBS-010-Scope verändert wurde

Wenn Tests wegen einer bereits vorhandenen, eindeutig fachfremden Störung nicht laufen, genaue Ursache und reproduzierbaren Befehl dokumentieren. Nicht einfach als PASS markieren.

---

# Abschlussbericht

Berichte kompakt:

1. Welche Dateien wurden geändert/neu erstellt?
2. Welche OBS-010-Contracts wurden umgesetzt?
3. Welche Tests wurden ausgeführt und mit welchem Ergebnis?
4. Welche Evidence-Dateien wurden erzeugt?
5. Gibt es offene Punkte oder Scope-Abweichungen?
6. Git-Status am Ende.
7. Bestätigung: kein Commit, kein Push, keine Änderungen an Server/LED.

Wenn vollständig:

`OBS-010 IMPLEMENTED – READY FOR CLAUDE GATE REVIEW`

Wenn ein echter fachlicher Blocker besteht:

`OBS-010 BLOCKED`

mit exakter Ursache.
