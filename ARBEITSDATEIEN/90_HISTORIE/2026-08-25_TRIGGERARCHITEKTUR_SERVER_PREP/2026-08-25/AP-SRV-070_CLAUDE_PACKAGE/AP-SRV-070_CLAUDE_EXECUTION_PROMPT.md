# AP-SRV-070 – SERVER LEGACY CUT / CLAUDE EXECUTION PACKAGE

## 0. Rolle und Auftrag

Du übernimmst `AP-SRV-070 – Server-Legacyabbau und Protokollgrenze`.

Das Paket ist bewusst zweistufig:

- **PHASE A – PREPARATION / CUT MAP:** darf sofort ausgeführt werden.
- **PHASE B – MUTATION / LEGACY CUT:** darf erst starten, wenn ein von der Koordination
  festgelegter integrierter Prep-Stack aus SRV-040/050/060 mit exaktem Commit und Tree
  vorliegt.

Du bist in dieser Runde:
- Senior Debugging-/Refactoring-Agent,
- Runtime-/Callgraph-Prüfer,
- Testautor,
- Implementierer des kontrollierten Legacy-Cuts.

Du bist **nicht** Root-Abnahme und darfst keine kanonische PASS-Entscheidung treffen.

Das Ziel ist **kein großer Architekturumbau**, sondern:

```text
neuen v2-Runtimepfad als einzige Autorität übrig lassen
→ alte Runtimeautoritäten nachweisbar entfernen
→ Compatibility/Migration nur dort erhalten, wo sie bewusst benötigt wird
→ Negativtests verhindern Wiederbelebung alter Pfade
```

---

# 1. Exakte Repositories / Ownership

## Serverrepo – Arbeitsrepo

```text
P:\GithubRepos\marcosudau-vps\voice-stt-server
```

## Zentrale Planung – nur lesen

```text
P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur
```

Planungsbereich:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur\
ARBEITSDATEIEN\10_AKTUELL\EINHEITLICHE_TRIGGERARCHITEKTUR
```

Keine Clientdatei verändern.

---

# 2. Kanonische Abhängigkeit

Die kanonische Reihenfolge ist:

```text
SRV-030
→ SRV-040
→ SRV-050
→ SRV-060
→ SRV-070
```

SRV-070 darf die vorangehenden Pakete nicht neu implementieren.

Es darf nur:
- deren jetzt vorhandene Runtimepfade als neue Autorität verwenden,
- alte parallele Autoritäten abbauen,
- notwendige Migrations-/Compatibility-Seams sauber begrenzen,
- Dokumentation und Tests auf den neuen Zustand bringen.

---

# 3. PHASE-A-START – darf sofort ausgeführt werden

Phase A darf auch dann laufen, wenn der finale Prep-Stack-SHA noch nicht feststeht.

Sie ist **read-only bezüglich Produktcode**.

Erlaubt:
- Code lesen,
- grep/search/callgraph,
- Tests lesen,
- Planungsdokumente lesen,
- Analyse-/Evidence-Dateien unter einer separaten Debug-/Prep-Akte erzeugen.

Nicht erlaubt in Phase A:
- Produktcode ändern,
- Tests ändern,
- Runtimepfade löschen,
- Branches mergen,
- rebasen,
- pushen.

## Arbeitsordner für Phase A

Verwende den aktuellsten verfügbaren Server-Worktree, den die Koordination für reine
Analyse benennt.

Wenn kein anderer Pfad genannt wurde, verwende ausschließlich lesend:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\einheitliche-triggerarchitektur-distributed
```

Dort nichts verändern.

---

# 4. PHASE-B-STARTSPERRE – absolut verbindlich

Bevor irgendeine Produktdatei für SRV-070 geändert wird, müssen diese Werte von der
Koordination geliefert worden sein:

```text
PREP_STACK_SHA=<MUSS_GESETZT_SEIN>
PREP_STACK_TREE=<MUSS_GESETZT_SEIN>
```

Zusätzlich:

```text
AP-SRV-040 Prep/Future-Port geprüft
AP-SRV-050 Prep/Future-Port geprüft
AP-SRV-060 Prep/Future-Port geprüft
```

Phase-B-Worktree:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\prep-srv-070
```

Branch:

```text
prep/AP-SRV-070/legacy-cut
```

Dieser Worktree muss exakt aus `PREP_STACK_SHA` erzeugt werden.

Wenn `PREP_STACK_SHA` oder `PREP_STACK_TREE` fehlt:

```text
PHASE B: BLOCKED
```

Nicht raten.
Nicht C1, C2, C3 oder irgendeinen Prep-Branch als Ersatz verwenden.

---

# 5. Normative Quellen – vollständig lesen

Im Client-Planungsrepo mindestens:

```text
PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md
PLANUNG/ZIELBILD.md
PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md
PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md
PLANUNG/IMPLEMENTIERUNGSPLAN.md
PLANUNG/AUSFUEHRUNGS_WORKFLOW.md
NACHVERFOLGUNG/TRACEABILITY.md
NACHVERFOLGUNG/FUNDE.md
```

Zusätzlich sämtliche tatsächlich vorhandenen Analysen zu:
- Legacy,
- Dead Code,
- Runtimepfaden,
- Protocol v1/v2,
- Wake-Word-Follow-up,
- Settingsmigration.

Serverseitig mindestens:

```text
AGENTS.md
docs/.archiv/README.md
docs/einheitliche-triggerarchitektur.md
docs/module-map.md
```

Und selbstverständlich:
- tatsächlicher Produktcode,
- tatsächliche Tests,
- tatsächliche 040/050/060-Prep-Änderungen des späteren Prep-Stacks.

Priorität bei Widersprüchen:

```text
1. bestätigte Entscheidungen / Frozen Contract
2. Frozen Wire-Schema
3. finaler Implementierungsplan
4. implementierte neue Runtimepfade 040/050/060
5. Produktcode
6. Tests
7. alte Analysen / Alt-Dokumentation
```

Tests können Alt-Soll enthalten.

---

# 6. Frozen Zielbild nach SRV-070

Nach SRV-070 gilt serverseitig:

## Eine Runtimeautorität

Es existiert genau ein serverautoritärer Lifecycle für:

```text
Activation
Recording/VAD
Segment
Input-Close
Finalization/Drain
```

Manual und Wake Word sind Trigger, keine eigenen Modi.

## Foregroundphasen exakt

```text
idle
waiting_first_speech
segment_active
followup_wait
closing_input
```

`finalizing` ist keine Foregroundphase.

## Session/Stream/Activation getrennt

```text
Session-Lifecycle
!= Audio-Stream-Lifecycle
!= Activation-Lifecycle
```

Alte Pfade dürfen diese Ebenen nicht wieder vermischen.

## First accepted trigger wins

Kein:
- Source-Merge,
- Quellenwechsel während Activation,
- zweiter Activation-Lifecycle,
- zweites Wake-Follow-up-System.

## v2 ist die neue Desktop-Protokollgrenze

Inkompatible Clients scheitern vor Sessionadmission.

Kein stiller Fallback auf alte Triggersemantik.

---

# 7. PHASE A – vollständige Legacy-/Reachability-Map

Erstelle zunächst eine **tatsächliche** Cut-Map gegen den realen Code.

Für jeden Kandidaten:

```text
Symbol / Datei
Callsites
Tests
aktueller Nutzer
Runtime erreichbar?
ersetzt durch
Kategorie
Lösch-/Migrationsentscheidung
Risiko
```

Kategorien:

```text
A = sicher ersetzt / löschen
B = nur Compatibility / bewusst begrenzen
C = Migrationseingang, Runtime danach canonical
D = weiterhin produktiv erforderlich
E = unklar / BLOCKER
```

Kein Symbol allein wegen seines Namens löschen.

---

# 8. Pflichtkandidaten – alle prüfen

Mindestens folgende Themen vollständig untersuchen.

## 8.1 session.mode / Mode-Autorität

Prüfe:
- Query-/Sessionparameter,
- Configfelder,
- ServerSettings,
- Runtimeentscheidungen,
- Tests,
- Doku.

Ziel:
`session.mode` darf nach SRV-070 keine fachliche Runtimeautorität mehr sein.

Falls Bestandsconfig noch alte Keys enthält:
- optional begrenzte Migration beim Lesen,
- intern danach nur canonical Activation-/Triggersemantik.

Kein dauerhaftes duales Verhalten.

---

## 8.2 RealtimeSession / alter Inline-Lifecycle

Prüfe Klassen/Pfade wie:

```text
RealtimeSession
VoiceActivityDetector
alte inline recording/finalization logic
```

Nicht blind löschen.

Beweise:
- FastAPI-/Desktop-v2 nutzt sie nicht mehr,
- keine noch unterstützte Server-API hängt daran,
- Browserclient ist außerhalb dieses APs.

Öffentliche Bibliotheksfunktion ≠ automatisch Server-Legacy.

Nur Server-Runtime im Scope löschen.

---

## 8.3 finalizing

Suche:
- Statuswerte,
- Phasen,
- UI-/Wirewerte,
- Tests,
- Doku,
- Helfer.

Ziel:
`finalizing` darf keine Foregroundphase sein.

Backgrounddrain darf natürlich weiterexistieren.

---

## 8.4 alte Triggeradapter

Prüfe:
- v1 `trigger`,
- `trigger_ack`,
- Legacy-Commandparser,
- Transportadapter,
- Aliasadapter.

Ziel:
v2 Desktoppfad darf alte Triggeradapter nicht benötigen.

Wenn ein Compatibility-Seam absichtlich bleibt:
- klar isolieren,
- nicht als neuer Desktop-Runtimepfad,
- negative Tests gegen unbeabsichtigte Nutzung.

---

## 8.5 `extend` / additive Zeitgutschrift

Suche:
- `extend`,
- `extensionSeconds`,
- Timerverlängerung,
- additive credit semantics,
- Doku,
- Tests.

Frozen Ziel:
Refresh setzt Deadline nach definierter SRV-030-Semantik;
kein altes additives Guthaben.

Nach SRV-070 darf `extend` nicht mehr als aktives Runtimecommand für den neuen Pfad
akzeptiert werden.

---

## 8.6 Source-Merge

Suche:
- `merged`,
- `already_active`,
- Source-Listenmutation,
- Manual+Wake-Kombination,
- alte Replay-/Ackgründe.

Frozen:
First accepted trigger wins.
Keine zweite Quelle wird in laufende Activation eingemischt.

---

## 8.7 Legacy Wake-Word Follow-up

Prüfe insbesondere vorhandene/ähnliche Symbole wie:

```text
_start_wakeword_followup_window
_finish_wakeword_followup
_clear_recorder_followup_gate_locked
_wakeword_followup_generation
_wakeword_voice_window
```

Wichtig:
Nicht nur nach Namen löschen.

Entscheide je Symbol:
- ist es noch für Recorder-/Audio-Hygiene erforderlich?
- oder bildet es einen zweiten serverseitigen Wake-Lifecycle?

Ziel:
Wake Word eröffnet denselben ActivationController-Pfad.
Follow-up wird vom kanonischen Activation-Lifecycle kontrolliert.

Kein zweiter Wake-Timer als fachliche Autorität.

---

## 8.8 alte Settingsnamen

Suche Settings, die alte Semantik ausdrücken:

```text
mode
dictation window
extension
wake followup as separate lifecycle
legacy trigger enablement
```

Nutze die SRV-050-Registry als canonical authority.

Falls Migration nötig:
- alter Key nur am Einleserand,
- canonical Key intern,
- Warn-/Migrationstest,
- keine doppelte Ownership.

---

## 8.9 alte Protokoll-/Sessionadmission

Prüfe:
- erste WebSocketnachricht,
- v1/v2-Auswahl,
- Sessionerstellung,
- Session-ID-Erzeugung,
- Admission,
- Fallback.

Frozen:
Keine gemeinsame v2-Version / inkompatibler Client:
- keine teilweise Session,
- kein Domaintraffic,
- sauberer Protokollfehler.

Kein alter Client darf zufällig über v1 in eine halbneue Session gelangen.

---

# 9. Dead-Code-Beweis

Vor jeder produktiven Löschung nachweisen:

```text
keine relevante Runtimecallsite
kein benötigter neuer v2-Adapter
kein bewusst unterstützter Bibliotheksexport im Scope
kein Test, der nur wegen echter verbleibender Funktionalität existiert
```

Tools:
- repo search,
- AST falls sinnvoll,
- import graph,
- test references,
- runtime dispatch tables.

Keine riesige automatische Dead-Code-Aktion.

---

# 10. PHASE-A-ARTEFAKT

Phase A erzeugt:

```text
docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-070/prep/
2026-08-26_LEGACY_CUT_MAP.md
```

Falls Datum bei Ausführung abweicht, aktuelles Datum verwenden.

Inhalt:

```text
Executive Summary
Runtime Entry Points
Legacy Candidate Matrix
Reachability
040/050/060 Replacement Mapping
Deletion Set A
Compatibility Set B
Migration Set C
Keep Set D
Blockers E
Negative-Test Plan
Recommended Phase-B Order
```

Phase A committen? **Nein.**
Push? **Nein.**

Wenn Phase B noch blockiert ist:
Bericht ausgeben und stoppen.

---

# 11. PHASE B – Preflight

Nur nach gesetztem `PREP_STACK_SHA/TREE`.

Im `prep-srv-070`-Worktree:

```powershell
git branch --show-current
git rev-parse HEAD
git rev-parse "HEAD^{tree}"
git status --short
```

Erwartet exakt:

```text
branch = prep/AP-SRV-070/legacy-cut
HEAD   = PREP_STACK_SHA
tree   = PREP_STACK_TREE
working tree = clean
```

Bei Abweichung:

```text
BLOCKED
```

---

# 12. PHASE-B-Reihenfolge

Nicht „alles löschen und dann Tests reparieren“.

Verbindliche Reihenfolge:

```text
1. negative guards für unerwünschte Legacyautorität
2. Replacementpfade 040/050/060 erneut bestätigen
3. aktive Legacycallsites entfernen
4. Adapter/Branches entfernen
5. tote Implementierung entfernen
6. Settingsmigration begrenzen
7. Protokollgrenze härten
8. Alt-Solltests ersetzen
9. Doku bereinigen
10. Dead-code/AST guards
11. Vollvalidierung
```

---

# 13. Negative Guards – vor Löschung

Tests müssen mindestens beweisen:

## Protocol
- alte v1 Triggernachricht erzeugt keine neue Desktop-v2-Session,
- inkompatible Version erzeugt keine Session,
- kein stiller Legacyfallback,
- v2 Hello funktioniert.

## Activation
- kein Source-Merge,
- kein `extend`,
- `finalizing` nicht Foreground,
- Controls laufen ausschließlich canonical.

## Wake
- kein zweiter fachlicher Wake-Follow-up-Timer,
- Wake öffnet canonical Activation,
- laufende Activation bleibt source-stabil.

## Settings
- `session.mode` ist keine Runtimeautorität,
- Legacy-Key ggf. nur Migrationseingang,
- interne Runtime verwendet canonical Registry.

---

# 14. AST-/Textguards

Gezielte Guards sind erwünscht, aber nicht naiv.

Nicht:
```text
assert "mode" nowhere in repo
```

Sondern:
- bestimmte aktive Runtimeklasse,
- bestimmte Dispatchmap,
- bestimmte Parserroute,
- bestimmte Settingsauthority.

Historische Doku/Akte/Migrationstabellen dürfen den Begriff enthalten.

---

# 15. Protokollgrenze nach Cut

Nach SRV-070:

```text
Desktop Runtime → v2
```

Handshake liefert mindestens:
- Serverversion,
- Servercommit,
- unterstützte Protokollversionen.

Inkompatibel:
- Fehler vor Sessionadmission,
- kein Fallback.

Browserclient:
- ausdrücklich außerhalb des AP-Scope,
- nicht ungefragt migrieren oder löschen.

---

# 16. Settingsmigration

Falls alte persisted Config vorhanden sein kann:

Akzeptabel:

```text
read legacy key
→ validate/migrate
→ canonical internal representation
→ optional deprecation warning
```

Nicht akzeptabel:

```text
legacy key and canonical key remain co-authoritative forever
```

Wenn Konflikt:
- canonical explicit value gewinnt gemäß bestehender Migrationspolicy,
- oder Konfiguration wird klar abgelehnt,
- keine stille nichtdeterministische Auswahl.

---

# 17. Wake-Word-Cut

Besonders sorgfältig.

SRV-060 besitzt:
- canonical catalog,
- selected-only loading,
- accepted detection,
- semantic latch,
- canonical wakeWordId/score,
- shared ActivationController admission.

Nach SRV-070 darf keine alte Wake-Logik:
- Activation separat eröffnen,
- Follow-up separat autorisieren,
- Quelle verschmelzen,
- zweite Timersemantik besitzen.

Audio-/Recorder-Helfer dürfen bleiben, wenn sie nur technische Funktion haben.

Im Bericht explizit unterscheiden:

```text
technical recorder helper
vs.
domain lifecycle authority
```

---

# 18. Segment-/Drain-Sicherheit

Legacyabbau darf SRV-020/SRV-030 nicht beschädigen.

Weiterhin:
- session-wide segmentSequence,
- terminal holes release later finals,
- acceptedSegmentCount == terminalSegmentCount am Activationterminal,
- alte Finals korrelieren über immutable context,
- kein global-current-activation lookup.

Regressionen verpflichtend.

---

# 19. Lock-/Concurrency-Invarianten

SRV-030-Invarianten bleiben vollständig:

```text
_ledger_dispatch_lock → self.lock → SegmentLedger._lock
```

Kein reverse.

Recorder callback-capable operations nicht unter Session-/Dispatchlock.

Legacyabbau darf nicht „vereinfachen“, indem alte Locks/Barrieren entfernt werden, die
jetzt canonical Safety tragen.

Vor Löschung eines scheinbar alten Synchronisationshelpers beweisen, dass er nicht mehr
Teil des neuen Pfads ist.

---

# 20. Dokumentation

Aktualisieren:
- `docs/einheitliche-triggerarchitektur.md`
- `docs/module-map.md`
- relevante Protocol-/Compatibility-Doku
- Settings-/Wake-Doku soweit durch Cut betroffen.

Nicht:
- historische AP-Akten rückwirkend umschreiben,
- bereits archivierte Reports verfälschen.

Neue AP-SRV-070-Akte gemäß `docs/.archiv/README.md` anlegen.

Keine finale `ABNAHME.md`, solange Root nicht abgenommen hat.

---

# 21. Pflichtvalidierung

Mindestens:

## Fokustests
- v2 Protocol/Handshake
- Activation commands
- Ledger
- Settings v2
- Wake catalog/detection
- Snapshot/events
- Legacy negative guards

## SRV-030 Regression
Komplette relevante Controlled-/Timer-/Ledger-Suites.

## Vollsuite

```powershell
python -m pytest -q --basetemp=.pytest-tmp\pt tests/unit
```

## Diff

```powershell
git diff --check
```

## Legacy guard scan
Maschinenlesbar dokumentieren:
- aktive Legacyparser,
- `extend`,
- source merge,
- `finalizing`,
- session.mode runtime authority,
- legacy wake lifecycle.

Keine falschen Positives aus Archiv/Doku als FAIL zählen.

---

# 22. Keine verbotenen Seiteneffekte

- kein Clientcode,
- kein Browserclientumbau,
- keine neue Settings-Control-Plane,
- keine neue Wake-Engine,
- kein neuer Protocol-v3-artiger Entwurf,
- kein Hardwarethema,
- kein Push.

---

# 23. Commitregel für Phase B

Wenn Phase B vollständig grün ist:

Genau **ein lokaler Prep-Commit**.

Empfohlene Message:

```text
prep(server): implement AP-SRV-070 legacy cut
```

Kein Push.

Kein Rebase.
Kein Amend fremder Commits.

---

# 24. Abschlussbericht

Verbindliches Format:

```text
STATUS: PREP PASS / BLOCKED

PRECHECK
Branch:
PREP_STACK_SHA:
PREP_STACK_TREE:
Working Tree vor Start:

PHASE A
Legacy Cut Map:
Runtime Entry Points:
A – Delete:
B – Compatibility:
C – Migration:
D – Keep:
E – Blockers:

PHASE B
Removed Runtime Authorities:
Removed Adapters:
Kept Compatibility Seams:
Migration Seams:
Protocol Boundary:
Wake Cut:
Settings Cut:
Dead Code:

NEGATIVE GUARDS
- ...

SRV-020/030 SAFETY
- Ledger
- Ordering
- Cancel boundary
- Close boundary
- Lock order
- Lifecycle epoch

TESTS
Focused:
SRV-030 regression:
Settings:
Wake:
Protocol:
Full suite:
Legacy guard:
git diff --check:

CHANGED FILES

PREP COMMIT:
<sha>

PREP TREE:
<tree>

WORKING TREE:
clean / details

PUSH:
no

REMAINING FOR CANONICAL SRV-070:
- ...
```

---

# 25. Wenn du auf einen echten Konflikt stößt

Nicht improvisieren.

`BLOCKED`, wenn z.B.:
- 040/050/060 Replacement fehlt,
- ein vermeintlicher Legacy-Pfad noch produktiv notwendig ist,
- Frozen Contract und reale neue API widersprechen,
- Entfernen einen außerhalb Scope liegenden öffentlichen API-Contract brechen würde.

Dann:
- konkreter Symbolpfad,
- Callsite,
- Test,
- Entscheidung, die fehlt,
- minimaler Lösungsvorschlag.

Keine Ersatzarchitektur erfinden.

---

# 26. Qualitätsmaßstab

SRV-070 ist erfolgreich, wenn nach dem Cut nicht einfach „weniger Dateien“ existieren,
sondern die Runtime-Autorität eindeutig geworden ist.

Der gewünschte Endzustand ist:

```text
v2 transport
→ eine server-authoritative session/domain boundary
→ eine Activation state machine
→ ein segment ledger
→ eine settings authority
→ eine wake-word admission/detection authority
```

und **keine zweite Legacylogik kann denselben fachlichen Zustand mehr verändern**.
