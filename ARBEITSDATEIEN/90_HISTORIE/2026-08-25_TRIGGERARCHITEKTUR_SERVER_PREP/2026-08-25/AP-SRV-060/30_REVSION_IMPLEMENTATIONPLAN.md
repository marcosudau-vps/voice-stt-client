AP-SRV-060 – VERBINDLICHE PLANREVISION VOR IMPLEMENTIERUNG
ROOT REVIEW / SPECULATIVE PREP CORRECTION

Dein bisheriger Implementierungsplan für AP-SRV-060 enthält brauchbare
Grundelemente, ist aber in der vorliegenden Form NOCH NICHT zur Umsetzung
freigegeben.

Bevor du irgendeine Produktdatei veränderst, überarbeite den Plan anhand der
folgenden verbindlichen Korrekturen.

Danach darfst du – sofern kein echter technischer/vertraglicher Blocker
auftaucht – direkt mit der spekulativen Implementierung auf dem vorbereiteten
Worktree fortfahren.

============================================================
0. ARBEITSKONTEXT
============================================================

Worktree:

P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\prep-srv-060

Branch:

prep/AP-SRV-060/wakeword

Startbasis:

db3d2b49539afbf4812d90e13f26f099b9314fe9

Dieser Stand ist SPEKULATIVE VORBEREITUNG.

Er ist:
- kein kanonisches AP-SRV-060,
- keine Root-Abnahme,
- keine Attestation,
- nicht zu pushen.

Kein:
- Push
- Rebase
- Merge in kanonische Branches
- Amend fremder Commits
- neues venv
- Client-Produktcode

Am Ende maximal genau ein lokaler Prep-Commit:

prep(wakeword): implement speculative AP-SRV-060 contract

============================================================
1. NORMATIVE QUELLEN
============================================================

Vor Planrevision vollständig gegen die realen Quellen prüfen:

Client-Planung, nur lesen:

P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur\
ARBEITSDATEIEN\10_AKTUELL\EINHEITLICHE_TRIGGERARCHITEKTUR\PLANUNG\
TECHNISCHER_CONTRACT_FREEZE.md

IMPLEMENTIERUNGSPLAN.md

ZIELBILD.md

ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md

PROTOKOLL_V2_WIRE_SCHEMA.md

sowie vorhandene Analysen/Vertragsvektoren.

Server:
- tatsächlicher Code
- tatsächliche Tests
- AGENTS.md
- docs/.archiv/README.md
- bestehende Wake-/Recorder-/Preroll-/Activation-Control-Implementierung

Bei Widerspruch gilt:

Frozen Decisions / Contract
> Wire Schema
> Implementierungsplan
> tatsächlich bereits akzeptierte neue Architektur
> alte Tests / Legacycode / alte Dokumente.

Nichts allein deshalb übernehmen, weil es im bisherigen Code existiert.

============================================================
2. PUBLIC CATALOG CONTRACT ≠ INTERNAL MODEL METADATA
============================================================

Der Frozen PUBLIC Wake-Word-Katalog besitzt verbindlich:

id
displayName
aliases
artifactVersion
available
optional unavailableReason
catalogRevision

Dein bisheriger Plan fügt zusätzlich hinzu:

availableFormats
default
source
path
paths

Diese Felder dürfen NICHT automatisch zum öffentlichen v2-Katalogvertrag
erklärt werden.

Trenne ausdrücklich:

A) Public WakeWordCatalogEntry
B) interne Discovery-/Load-Metadaten

Interne Metadaten dürfen weiterhin enthalten:

backend
availableFormats
source
path
paths
default
filesystem diagnostics

ABER:

GET /api/v2/wake-words darf insbesondere keine lokalen Dateipfade leaken.

Keine:
path
paths
absolute model directories
interne Buildpfade

im öffentlichen REST-/Wireobjekt.

Wenn `availableFormats`, `default` oder `source` öffentlich werden sollen,
muss dafür eine normative Quelle vorhanden sein.

Sonst intern lassen.

============================================================
3. KANONISCHE ID NICHT DURCH NORMALISIERUNG ZERSTÖREN
============================================================

Deine Formulierung

"id: kanonische stabile ID (normalisiert via Unicode-Trim + case-insensitive)"

ist zu unpräzise.

Frozen Contract:

- kanonische ID wird erhalten,
- Lookup/Vergleich erfolgt mit Unicode-Trim + case-insensitive Vergleich.

Daraus folgt:

NICHT:

canonical_id = input.lower()

oder andere Transformation als neue öffentliche ID.

Stattdessen:

canonical ID aus autoritativer Katalogquelle behalten.

Für Lookup einen separaten Normalisierungsschlüssel verwenden, sinngemäß:

trimmed.casefold()

Keine zusätzliche NFKC-/NFKD-/Heuristik einführen, sofern sie nicht normativ
festgelegt ist.

Canonical output muss immer dieselbe Katalog-ID zurückgeben.

============================================================
4. ARTIFACTVERSION NICHT ERFINDEN
============================================================

Dein Plan nennt beispielhaft:

"0.1"
"1.0.0"

Das darf NICHT als Platzhalterimplementierung enden.

`artifactVersion` muss aus einer realen autoritativen Quelle stammen.

Zulässig:
- explizite Manifestmetadaten,
- bereits vorhandene eindeutige Artefaktversionierung.

Nicht zulässig:
- frei gewählte Versionsnummer,
- zufällige Defaultversion,
- "1.0.0", weil nichts anderes bekannt ist.

Wenn der aktuelle models.json-/Filesystem-Bestand keine belastbare
artifactVersion liefert:

- Implementierungsseam vorbereiten,
- im Prep-Bericht explizit als Evidence-/Binding-Gap dokumentieren,
- keine falsche Public-Version veröffentlichen.

Keine neue Hash-basierte Versionssemantik erfinden, ohne normative Entscheidung.

============================================================
5. ALIAS-MODELL
============================================================

Nur explizit deklarierte Aliase.

Keine Heuristik wie:

Jarvis ↔ Hey Jarvis
Alexa ↔ Hey Alexa

außer genau dieser Alias ist explizit hinterlegt.

Ein Alias darf nicht mehrdeutig aufgelöst werden.

Prüfe mindestens:

- Alias ↔ Alias Kollision
- Alias ↔ kanonische ID Kollision
- Case-insensitive Kollision
- Whitespace-normalisierte Kollision

Kollision muss deterministisch als Katalogfehler/Resolution-Fehler sichtbar
werden.

Keine zufällige Auswahl.

ABER:

Erfinde nicht eigenmächtig einen neuen öffentlichen Enum-Katalog für
`unavailableReason`.

Wenn machine-readable interne Gründe gebraucht werden, zentral definieren
und klar zwischen internem Diagnostic Code und frozen Public Contract
unterscheiden.

============================================================
6. EINE KATALOGAUTORITÄT
============================================================

`OpenWakeWordCatalog` soll die eigentliche Catalog-/Resolution-Autorität sein.

`WakeWordRegistry` in operations.py darf ein dünner Service-/API-Adapter sein.

Keine zweite unabhängige:
- Aliasmap,
- Revision,
- Availabilityberechnung,
- Resolutionlogik

in WakeWordRegistry aufbauen.

catalogRevision besitzt genau eine Ownership.

============================================================
7. GLOBALE DISABLELISTE
============================================================

Der Provider-Seam für die globale Disableliste ist richtig.

Beibehalten:

REQUIRES_FINAL_SRV_050_BINDING

Aber SRV-060 baut dafür KEINE zweite Settings-Control-Plane.

Der Provider liefert canonical IDs / Disablepolicy.

Wake-Katalog interpretiert sie für neue Sessions.

Apply Policy bleibt:

new sessions

Eine laufende Session wird durch spätere globale Disableänderung nicht
rückwirkend umgebaut, sofern Frozen Settings Contract nichts anderes sagt.

============================================================
8. ATOMARE ADMISSION – JA, ABER LEGACY NICHT VORZEITIG ZERSTÖREN
============================================================

Die bisherige Serverimplementierung besitzt Legacy-/Fallbacksemantik in
`resolve_session_wake_word_config()`.

Der neue Frozen-v2-Vertrag verlangt dagegen:

eine problematische angeforderte ID
→ gesamte Auswahl abgelehnt
→ kein Partial Load
→ kein Fallback auf Serverdefault
→ machine-readable problematische IDs

Das ist richtig.

ABER:

AP-SRV-070 ist der geplante Legacy-Cut.

Daher darf die spekulative SRV-060-Implementierung nicht einfach sämtliche
Legacy-/v1-Fallbackpfade global entfernen und dadurch alte Serverpfade
vorzeitig brechen.

Bevorzugte Architektur:

strict canonical wake admission
    ↓
schmaler neuer Resolver / Domainport
    ↓
später durch SRV-040/v2 genutzt

Legacy Adapter
    ↓
bleibt bis SRV-070 isoliert

Kein doppelter Domain-Lifecycle.

Falls `resolve_session_wake_word_config()` selbst geändert wird, muss sauber
zwischen canonical strict admission und Legacycompat unterschieden werden.

Keine stille Fallbacksemantik im neuen v2-Pfad.

============================================================
9. SELECTED-ONLY – HIER MUSS DER BESTAND WIRKLICH KORRIGIERT WERDEN
============================================================

Der aktuelle Bestand muss kritisch geprüft werden.

Insbesondere:

`_resolve_openwakeword_paths()`

darf nicht bei expliziten `openwakeword_model_paths` einfach alle Classifier
laden, wenn die Session nur bestimmte canonical WakeWordIds ausgewählt hat.

Frozen:

[A, C]
→ exakt A und C initialisieren
→ niemals B

Das gilt auch bei:
- Manifestpfaden,
- expliziten Pfaden,
- gemischtem Catalog-/Filesystem-Bestand.

Die Loader-Grenze muss eine eindeutige Zuordnung tragen:

canonicalWakeWordId
→ classifier artifact

Nicht nur eine positionsbasierte Liste von Dateipfaden.

Tests mit Fakes müssen exakt beweisen, welche Modelle an OpenWakeWord.Model
übergeben werden.

============================================================
10. SENSITIVITY-OWNERSHIP
============================================================

Frozen:

Range 0.0–1.0
Default 0.5
Apply = next_activation
Session mit Serverdefault

SRV-060 darf defensiv Range-validieren.

Aber:

die autoritative Settings-/Effective-Value-Ownership liegt bei SRV-050.

Deshalb:

REQUIRES_FINAL_SRV_050_BINDING

Keine zweite Settingsregistry in wakeword.py.

Eine Activation erhält den bereits effektiven Sensitivity-Wert über ihren
Settings-Snapshot / Provider.

Während laufender Activation keine rückwirkende Änderung.

============================================================
11. RAW SCORE UND ACCEPTED DETECTION TRENNEN
============================================================

Dein geplantes:

WakeWordDetection(..., raw: bool)

ist abzulehnen.

Raw Scores und akzeptierte Domain-Detection sind zwei verschiedene Dinge.

Bevorzugt:

interne Raw Candidate/Score Observation
    ↓ threshold/admission/latch
immutable accepted WakeWordDetection

Accepted Detection enthält mindestens:

wake_word_id
score

Optional internes monotonic observed_at für Scheduling/Diagnose.

Aber:

- kein `raw: bool` zur Vermischung der Ebenen,
- Raw Score ist kein Domain-Ereignis,
- Raw Score öffnet keine Activation,
- Raw Score setzt keinen fachlichen Latch.

Wire `occurredAtUnixMs` gehört später in SRV-040s Eventprojektion und ist
nicht mit intern monotonic time zu verwechseln.

============================================================
12. MULTI-CANDIDATE
============================================================

Wenn mehrere ausgewählte Modelle im selben Detectorstep die Schwelle
überschreiten:

1. höchsten Score wählen,
2. Ergebnis deterministisch machen.

Ein alphabetischer canonical-ID Tie-Break bei exakt gleichem Score ist als
interne deterministische Implementationsregel akzeptabel.

Aber nicht als neuen öffentlichen Contract darstellen.

Wichtig:

Detection muss danach die canonical WakeWordId tragen.

Kein positionsbasierter `max_index` als Domainidentität.

============================================================
13. DER FACHLICHE LATCH DARF NICHT IN activation_control.py
============================================================

Das ist eine zentrale Korrektur.

`activation_control.py` ist bewusst source-neutral.

Der Controlled Gate kennt:

open / closed
activationId
generation

Er kennt ausdrücklich NICHT:

manual
wake_word
WakeWordId
Wake Detection Latch

Dort keinen fachlichen Wake-Latch einbauen.

Auch der Recorder soll nicht zur zweiten Domain-State-Machine werden.

Der fachliche Wake-Latch gehört an eine serverseitige Wake-Admission-
Koordinationsgrenze, z.B. kleine dedizierte WakeAdmission-Komponente oder
Session-/Server-Domainlayer.

Er muss an die SRV-030 Activation gekoppelt sein.

Prinzip:

raw accepted threshold hit
→ versuche wake activation admission
→ NUR wenn ActivationController die Wake-Activation wirklich akzeptiert:
     latch = activationId / generation / wakeWordId
     genau ein wakeword.detected Domainereignis
→ bei rejection:
     kein Domain-Latch
     kein wakeword.detected

Beispiele für Rejection:
- Wake source suppressed
- andere Activation besitzt Triggerlock
- Session/Stream nicht aktiv
- stale detector generation
- Session geschlossen

Raw Diagnose darf weiterlaufen.

============================================================
14. LATCH-LIFETIME
============================================================

Frozen:

erster akzeptierter Treffer
→ Latch bis sicherem Eingabeschluss / Trigger-Unlock

Nicht:

bis Recorder stoppt

Nicht:

bis VAD stoppt

Nicht:

fester Cooldown ersetzt Activation-Lifetime

Nicht:

bis Final-Inferenz fertig

Freigabe muss an die kanonische SRV-030-Close-/Unlock-Grenze gebunden werden:

REQUIRES_FINAL_SRV_030_BINDING

Bis zum finalen Binding in Prep:

- klarer Port,
- deterministische Fake-Tests,
- keine erfundene Parallel-Lifetime.

============================================================
15. WAKE WORD WÄHREND BEREITS OFFENER ACTIVATION
============================================================

Wenn eine Activation bereits offen ist und der Nutzer erneut ein Wake Word sagt:

- kein zweiter Activationversuch mit Wirkung,
- kein Source-Merge,
- kein Source-Wechsel,
- kein Refresh,
- kein Finish,
- kein Cancel,
- kein zweites wakeword.detected Domainereignis.

Das Audio selbst ist in dieser Situation gewöhnliches Activationaudio.

Insbesondere darf der Recorder eine erneute Phrase nicht als Steuercommand
interpretieren.

============================================================
16. EVENTSEMANTIK
============================================================

`wakeword.detected` ist ein DOMAIN-Ereignis für eine akzeptierte Detection.

Es muss mit der dadurch angenommenen Activation korrelieren.

Später über SRV-040 mindestens:

activationId
wakeWordId
score
primarySource = wake_word

REQUIRES_FINAL_SRV_040_BINDING

Wichtig:

Detectorhit ≠ Domainevent.

Wenn Activationadmission scheitert:
- Raw Diagnose möglich,
- kein `wakeword.detected`.

Genau ein Event je accepted wake activation.

============================================================
17. LATE CALLBACK / SESSION LIFECYCLE
============================================================

SRV-030 hat bereits gezeigt, dass verspätete Wakecallbacks gefährlich sind.

Darum Pflichtfälle:

- Detection nach stop_streaming
- Detection nach session close
- Detection aus alter Detector-/Lifecyclegeneration
- Detection nach Restart einer neuen Generation

müssen inert sein.

Vorhandene Lifecycle-/Wake-Epoch-Mechanik aus finalem SRV-030 verwenden bzw.
über einen schmalen Binding-Port vorbereiten.

Keine zweite parallele Epocharchitektur erfinden.

============================================================
18. AUDIOGRENZE – KEIN PAUSCHALES ABSCHNEIDEN
============================================================

Der aktuelle Recorder besitzt noch eine grobe Logik nach dem Muster:

wakeword_samples_to_remove =
    sample_rate * wake_word_buffer_duration

und entfernt danach eine feste Audiomenge.

Das darf nicht einfach als finale Frozen-Lösung übernommen werden.

Frozen:

Wake-Word-Audio fehlt im Nutztranskript.
Unmittelbar folgende Sprache bleibt vollständig erhalten.

Daher braucht die Implementierung eine echte Audio-/Sample-Grenze zwischen:

Detector History
und
Transcript Audio

Bevorzugt wird eine Sample-/Frame-identifizierbare Boundary beim accepted
Wake-Hit.

Die genaue Kalibrierung darf nur evidenzbasiert erfolgen.

Keine willkürlichen zusätzlichen Millisekunden.

============================================================
19. GENERIC PREROLL NICHT MIT WAKE-GRENZE VERMISCHEN
============================================================

`preroll.py` besitzt bereits eine allgemeine konservative VAD-/Silence-basierte
Pre-Roll-Auswahl.

Diese Logik ist nicht automatisch identisch mit der Wake-Word-Audiogrenze.

Deshalb vor Änderung sauber trennen:

A) generischer Pre-Recording/Pre-Roll-Selector
B) Wake-Detector-History
C) accepted Wake transcript boundary

Nur dort integrieren, wo Datenfluss tatsächlich gemeinsam ist.

Keine zweite VAD-Passage.

Kein heuristisches erneutes Speech Detection Processing nur für Wake.

Bei Unsicherheit konservativ Sprache ERHALTEN.

Es ist schlimmer, den ersten Nutzsatz abzuschneiden, als diagnostisch etwas
zusätzliches Audio zu behalten.

============================================================
20. 0 MS
============================================================

0 ms muss als legitimer konfigurierter Pre-Roll-/Boundary-Wert technisch
unterstützt bleiben, soweit Frozen Settings Contract dies vorsieht.

Das bedeutet NICHT:

Wake Word darf dann zwangsläufig im Transcript verbleiben.

Wake-exclusion boundary und optionaler user-speech Pre-Roll sind getrennte
Begriffe.

Diese Semantik im revidierten Plan explizit erklären.

============================================================
21. KEINE 2-AUS-3-REGEL
============================================================

Keine Multi-Chunk-/2-aus-3-Regel implementieren.

Frozen:

nur nach Score-/Audio-Charakterisierung, wenn Bedarf belegt.

Der Prep-Code darf:
- Scoretraces erfassen,
- Evidence erzeugen,
- Hook vorbereiten.

Er darf nicht:
- neuen Confirmation Algorithmus aktivieren,
- Schwellen empirisch erfinden.

============================================================
22. COOLDOWN
============================================================

Cooldown/Rearm ist im Implementierungsplan Scope, aber nicht frei zu erfinden.

Der fachliche Latch ist die primäre Schutzgrenze.

Cooldown darf höchstens eine klar getrennte Detector-/Noise-Hygiene sein.

Er darf nicht:
- den Activation-Latch ersetzen,
- Input-Close verzögern,
- Triggerlock kontrollieren,
- neue Domainsemantik erzeugen.

Falls kein belastbarer vorhandener Wert / Contract / Messwert existiert:
- Provider/Setting-Seam vorbereiten,
- keine neue magische Zahl.

============================================================
23. EVIDENCE HARNESS
============================================================

Die Grundidee ist richtig.

Aber:

"Maximalmenge (z.B. 5 Modelle)" ist falsch.

Max bedeutet:

tatsächlich maximal verfügbare/zulässige Auswahl der getesteten Umgebung.

Harness protokolliert die tatsächliche Anzahl.

Pflicht:

1 Modell
3 Modelle, sofern mindestens 3 verfügbar
Max = alle verfügbaren testbaren ausgewählten Modelle

Wenn reale Artefakte fehlen:

ENVIRONMENT_EVIDENCE_PENDING

Keine Zahlen erfinden.

============================================================
24. RESSOURCENMESSUNG KORREKT INTERPRETIEREN
============================================================

`process_memory_snapshot()` misst Prozesswerte.

Peak RSS ist ggf. process-lifetime-wide und nicht automatisch "Wake-Modell Peak".

Darum mindestens dokumentieren:

before RSS
after RSS
delta RSS

before/after peak RSS, soweit verfügbar

initialization elapsed time über monotonic/perf_counter

loaded canonical model IDs

framework

artifact versions, sofern belastbar

Kein falsches "Modell X verbraucht exakt Y MB", wenn Messung nur Prozessdelta ist.

============================================================
25. REAL EVIDENCE VS UNIT TESTS
============================================================

Zwei Ebenen trennen:

A) deterministische Unit/Fake-Tests
- selected-only
- IDs
- aliases
- admission
- latch
- score selection

B) reale Environment Evidence
- Startzeit
- RSS
- reale Modelle
- Audio-/Score traces

Fehlende B-Evidence darf A nicht blockieren.

Aber fehlende B-Evidence muss klar mit

ENVIRONMENT_EVIDENCE_PENDING

im Report stehen.

============================================================
26. TESTS – BISHERIGER VERIFICATION PLAN IST ZU KLEIN
============================================================

Nicht nur:

test_wakeword.py
test_preroll.py
test_wakeword_contract.py
test_wakeword_evidence_harness.py

Pflicht zusätzlich:

- bestehende Server-Wake-/Sessiontests
- Controlled Activation Integration
- relevante SRV-030 Regression
- vollständige tests/unit Suite

Mindestens nach Implementierung:

python -m pytest -q -p no:warnings --basetemp=.pytest-tmp\pt \
  tests/unit/test_wakeword.py \
  tests/unit/test_preroll.py \
  tests/unit/test_wakeword_contract.py \
  tests/unit/test_wakeword_evidence_harness.py

plus relevante serverseitige Controlled-/Activation-/Sessiontests.

Danach:

python -m pytest -q --basetemp=.pytest-tmp\pt tests/unit

und:

git diff --check

============================================================
27. PFLICHT-RACE-/LIFECYCLE-TESTS
============================================================

Deterministisch testen:

- Manual Activation vs Wake Detection gleichzeitig
  → first accepted trigger wins

- zwei Wake Detections gleichzeitig
  → genau eine accepted

- zweiter Wakehit während offener Wake-Activation
  → kein zweites Event / keine zweite Activation

- Wakehit während Manual-Activation
  → kein Source-Merge / kein Domainevent

- Wake source suppressed
  → raw score möglich, keine Domainadmission

- Input-Close
  → Latch erst NACH safe-close/unlock wieder frei

- late detector callback nach stop
  → inert

- late detector callback nach session close
  → inert

- alte detector generation nach restart
  → inert

Keine Sleeps als Ordnungsmechanismus.

threading.Event / Barrier / Hookpoints verwenden.

Diese Raceklasse mehrfach laufen lassen, bevorzugt 20x.

============================================================
28. SELECTED-ONLY-PFLICHTTESTS
============================================================

Fake catalog:

A
B
C
D

Selection:

[A]

→ Loader erhält exakt A

[A, C, D]

→ exakt A, C, D

[A, X, C]

→ komplette Admission rejected
→ Loader wird überhaupt nicht aufgerufen

[A, disabled-C]

→ komplette Admission rejected

Alias zu C:

[A, alias-C]

→ Loader erhält canonical C

Collision alias:

→ reject
→ keine zufällige Auswahl
→ kein Loadercall

============================================================
29. AUDIOBOUNDARY-PFLICHTTESTS
============================================================

Nicht nur "Text sieht ungefähr richtig aus".

Mit synthetisch identifizierbaren Audioframes/Samplemarkern testen:

[history][WAKE][first-user-word][following-speech]

Erwartung:

WAKE nicht im transcript payload

first-user-word vollständig vorhanden

following-speech vollständig vorhanden

Zusätzlich:

- 0ms
- kurze Lücke
- unsichere Boundary
- Chunkgrenze mitten in Wake/User-Übergang
- konservativer Fallback

Kein zweiter VAD-Pass.

============================================================
30. DOKUMENTATION
============================================================

Dokumentiere klar:

Public Catalog Contract
Internal Artifact Metadata
Strict v2 Admission
Legacy compatibility boundary
Selected-only Loader
Raw score vs accepted Detection
Wake Admission / Latch Ownership
Audio boundary
Evidence status

Keine Aussage als "fertig integriert" markieren, wenn sie noch:

REQUIRES_FINAL_SRV_030_BINDING
REQUIRES_FINAL_SRV_040_BINDING
REQUIRES_FINAL_SRV_050_BINDING

ist.

============================================================
31. NEUER REVIDIERTER IMPLEMENTIERUNGSPLAN
============================================================

Bevor du Code veränderst, gib jetzt zuerst einen vollständig revidierten Plan
zurück.

Der revidierte Plan muss je Arbeitsschritt enthalten:

- konkrete Datei(en)
- tatsächliche bestehende Ausgangslage
- konkrete Änderung
- Ownership
- Public vs Internal API
- relevante Frozen-Invariante
- Tests
- Binding-Markierung

Besonders explizit darstellen:

1. Wo liegt Catalog Authority?
2. Wo liegt Strict Session Admission?
3. Wo liegt Accepted Wake Admission?
4. Wo liegt der fachliche Latch?
5. Wie wird Latch an SRV-030 safe input close gebunden?
6. Wie wird canonical WakeWordId bis zum Event erhalten?
7. Wie werden Raw Scores getrennt?
8. Wie wird selected-only auch bei explicit paths garantiert?
9. Wie wird Wake-Audio von folgendem Nutzspeech getrennt?
10. Welche Teile bleiben Legacy bis SRV-070?
11. Welche Teile sind erst mit SRV-040/050 vollständig bindbar?

============================================================
32. IMPLEMENTIERUNGSFREIGABE NACH PLANREVISION
============================================================

Nach Ausgabe des revidierten Plans:

Wenn du KEINEN echten Frozen-Contract-/Bestandsblocker gefunden hast,
darfst du danach direkt mit der spekulativen Umsetzung fortfahren.

Keine weitere Freigaberückfrage nötig.

Wenn echter Blocker:

STATUS: BLOCKED

mit:
- exakter Quelle,
- exaktem Symbol,
- widersprechenden Contracts,
- kleinstem Lösungsvorschlag.

Nicht wegen bloßer Implementierungskomplexität blockieren.

============================================================
33. ABSCHLUSS / REPORT
============================================================

Am Ende mindestens:

STATUS: PREP PASS / BLOCKED

BASE
Branch:
Start SHA:
Start Tree:

PLAN REVISION
- welche Punkte des ursprünglichen Plans verworfen/geändert wurden

IMPLEMENTATION
Catalog:
Admission:
Selected-only:
Detection model:
Latch:
Lifecycle guards:
Audio boundary:
Evidence harness:
REST port:
Bindings:

PUBLIC CONTRACT
genaue public fields:
keine geleakten internal fields:

TESTS
Wake focus:
Preroll:
Admission:
Race:
SRV-030 regression:
Full tests/unit:
20x race repetition:
git diff --check:

REAL EVIDENCE
1 model:
3 models:
max models:
oder ENVIRONMENT_EVIDENCE_PENDING

CHANGED FILES

BINDINGS
REQUIRES_FINAL_SRV_030_BINDING:
REQUIRES_FINAL_SRV_040_BINDING:
REQUIRES_FINAL_SRV_050_BINDING:

PREP COMMIT:
<sha>

PREP TREE:
<tree>

WORKING TREE:
clean

PUSH:
no

============================================================
34. WICHTIGSTE ARCHITEKTURREGEL
============================================================

Der Endzustand dieses Prep-Pakets darf nicht sein:

Recorder
+ ActivationControl
+ Session
haben drei verschiedene Wake-Word-Lifecycles.

Sondern:

Detector
→ Raw candidates
→ Wake Admission
→ EIN serverautoritärer ActivationController
→ source-neutral Controlled Gate
→ genau ein accepted wakeword.detected
→ Latch bis safe input close
→ Release

Recorder bleibt Audiopipeline.

ActivationControl bleibt source-neutrales Gate.

Wake Admission besitzt Wake-spezifische Domainlogik.

ActivationController bleibt Activation-Autorität.
