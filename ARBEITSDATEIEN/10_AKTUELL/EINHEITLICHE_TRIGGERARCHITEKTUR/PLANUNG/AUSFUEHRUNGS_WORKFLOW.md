# Ausführungsworkflow – parallele Server-/Client-Reihe

**Status:** PREPARED

**Stand:** 2026-08-25

Dieses Dokument legt fest, wie die Arbeitspakete mit genau einem
GPT-Implementierungsagenten und höchstens einem parallelen Claude-Code-CLI-Lauf
ausgeführt und durch die Koordination abgenommen werden. Es ersetzt nicht die
fachlichen oder technischen Contracts.

## 1. Rollen und feste Grenzen

### Koordination und Endabnahme

Die koordinierende Hauptsession:

- erstellt den konkreten Auftrag unmittelbar vor jedem AP;
- pinnt Repository, Branch, Start-SHA, freigegebene Abhängigkeiten und
  Contractabschnitte;
- startet und überwacht die beiden zulässigen Ausführungslanes;
- nimmt jedes AP selbst anhand von Diff, Tests, Dokumentation und Contract ab;
- gibt bei Befunden nur das betroffene AP zur Korrektur zurück;
- pflegt nach PASS zentrale Status-, Traceability- und Kompatibilitätsdaten.

Die Koordination implementiert nicht gleichzeitig einen dritten
Produktcodepfad, während beide Ausführungslanes aktiv sind.

### GPT-Lane

- genau ein Codex-Sub-Agent zurzeit;
- Standardmodell: `gpt-5.6-sol`;
- erhält exklusiven Datei-/Repositorybesitz für sein aktuelles AP;
- Folgekorrekturen werden möglichst an denselben Agenten zurückgegeben.

### Claude-Lane

- genau ein separater Claude-Code-CLI-Lauf zurzeit;
- Modell je AP: `sonnet` oder gezielt `opus`;
- wird im Repository des APs gestartet und erhält denselben strukturierten
  Paketauftrag wie die GPT-Lane;
- Session-ID, Start-SHA und Ergebnis werden für gezielte Fortsetzungen
  festgehalten.

Es laufen niemals zwei GPT-Implementierungsagenten oder zwei Claude-Läufe
parallel. Zulässig sind gleichzeitig genau ein GPT-AP und ein Claude-AP, wenn
deren Dependencies freigegeben und ihre Datei-/Repositorybereiche getrennt
sind.

## 2. Dokumentationspflicht innerhalb jedes APs

Dokumentation ist Bestandteil des Implementierungsergebnisses und kein
nachgelagerter Sammelblock.

Der ausführende Agent muss:

1. dauerhaft gültige Produktdokumentation im eigenen Repository anpassen;
2. öffentliches Wire-, Settings-, Konfigurations- oder Bedienverhalten in den
   einschlägigen Referenzen dokumentieren;
3. Tests, Migrationseinschränkungen und bekannte temporäre
   Client-/Server-Inkompatibilität im AP-Bericht aufführen;
4. die repositoryeigenen Governance-Pflichten vollständig erfüllen;
5. im Abschlussbericht geänderte Dokumente, Testbefehle, Resultate,
   Abweichungen und Commit-SHA nennen.

Für Server-APs gelten insbesondere die Archiv-/Aktionspflichten aus dem
serverseitigen `AGENTS.md` sowie je nach Scope `docs/einheitliche-triggerarchitektur.md`,
`docs/client-development/`, `docs/configuration.md`, `docs/wake-words.md` und
`docs/api-compatibility.md`.

Für Client-APs gelten insbesondere `task.md`, `ÜBERGABE.md`,
`docs/PROJEKTUEBERSICHT.md`, die einschlägigen Guides und – ab AP-CLI-010 –
die mit Protokoll v2 synchronisierten `server-docs-for-client-development/`.

Nicht jede Datei wird in jedem AP geändert. Der konkrete Auftrag nennt die
erwarteten Dokumentziele; der Agent ergänzt weitere tatsächlich betroffene
kanonische Dokumentation. Normative Planungsdateien, zentrale Gate-Status und
die Commitpaar-Kompatibilitätsmatrix bleiben Eigentum der Koordination. Ein
Implementierungsagent darf sie nicht eigenmächtig umdeuten.

## 3. Abnahme-Gate je Arbeitspaket

Ein AP darf erst als PASS gelten, wenn die Koordination:

1. Branch, Start-SHA und tatsächlich erzeugten Commit verifiziert hat;
2. den vollständigen Diff gegen den Start-SHA auf Scope und Seiteneffekte
   geprüft hat;
3. fokussierte Tests sowie die komplette Suite des geänderten Repositorys
   selbst erneut ausgeführt hat;
4. bei Protokollpaketen zusätzlich die gemeinsamen v2-Vertragsvektoren
   ausgeführt hat;
5. neue Race-, Replay-, Timeout- und Fehlerpfade gegen die Akzeptanzkriterien
   geprüft hat;
6. Produktdokumentation gegen den tatsächlichen Code abgeglichen hat;
7. Working Tree, `git diff --check`, Flakes und nicht versionierte Artefakte
   geprüft hat;
8. den AP-Status zentral auf PASS gesetzt und die freigegebene Commit-SHA als
   Dependency für nachfolgende Aufträge gepinnt hat.

Bei FAIL erhält derselbe Agent eine konkrete Befundliste. Er darf nicht mit
dem nächsten AP beginnen. Ein Scopefehler in einem bereits abgenommenen AP
wird als eindeutig server- oder clientseitiges Korrektur-AP geführt.

### 3.1 Repositorylokale AP-Akte

Jedes AP besitzt vor Agentenstart einen eigenen Ordner im Repository, dessen
Produktcode es ändert:

```text
Server: docs/.archiv/einheitliche_triggerarchitektur/AP-SRV-.../
Client: ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/
        ARBEITSPAKETE/AP-CLI-.../
Integration: ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/
             ARBEITSPAKETE/AP-INT-.../
```

Mindestens enthalten sind:

```text
README.md
PLAN.md
runs/01_<RUNNAME>/
├── PROMPT.md       # unverändertes Original des erteilten Auftrags
├── REPORT.md       # Abschlussbericht des ausführenden Agents
├── ABNAHME.md      # Befunde und finales PASS/FAIL der Koordination
└── evidence/       # notwendige reproduzierbare Nachweise oder Index
```

Im Serverarchiv erhalten diese Dateien gemäß serverseitiger Governance einen
Datumspräfix, beispielsweise `2026-08-25_PROMPT.md`. Inhalt und Ownership
bleiben identisch.

Weitere Runs erhalten `02_...`, `03_...` usw. Der Originalprompt eines Runs
wird nach Start nicht umgeschrieben. Korrekturaufträge werden als datierter
Abschnitt in `ABNAHME.md` und als eigener Folgeprompt im nächsten Run
gespeichert, sofern nicht dieselbe Session lediglich einen eindeutig
dokumentierten Amend ausführt.

### 3.2 Ein Commit und Push pro bestandenem AP

1. Der Agent erstellt nach seinen grünen Tests einen lokalen Commit, der
   Produktcode, Produktdokumentation, `PROMPT.md`, `REPORT.md` und Evidence des
   APs enthält.
2. Die Koordination prüft diesen Commit vollständig. Solange das Gate nicht
   besteht, erfolgt kein Push.
3. Bei einem Befund arbeitet derselbe Agent nach Möglichkeit weiter und
   amended den noch ungepushten AP-Commit. Dadurch bleibt es bei genau einem
   finalen Commit je AP.
4. Bei PASS ergänzt die Koordination `ABNAHME.md`, führt die notwendigen
   abschließenden Dokument-/Diffprüfungen aus und amended diese Endabnahme in
   denselben Commit.
5. Erst danach pusht die Koordination den finalen Commit auf
   `github/feat/einheitliche-triggerarchitektur` des jeweiligen Repositorys.
6. Die gepushte Commit-SHA wird als einzige freigegebene Dependency für das
   nächste AP und bei Schnittstellengates als Client-/Server-Paar vermerkt.

Ein Agent pusht niemals selbst. Die Koordination erstellt keinen zweiten
inhaltlichen Commit für dasselbe AP; ihr Amend macht sie zum finalen Committer
des einen freigegebenen AP-Commits.

## 4. Parallelisierungswellen

| Welle | GPT-Lane | Claude-Lane | Freigabebedingung / Ergebnis |
|---:|---|---|---|
| 0 | Koordination: Contract-/Vektor-Freeze | – | vorliegende Planungsunterlagen PREPARED |
| 1 | AP-SRV-000 | AP-CLI-000 mit Sonnet | beide Baselines einzeln abgenommen |
| 2 | AP-SRV-010 | keine sichere Client-Produktänderung | SRV-010 PASS |
| 3 | AP-SRV-020 | keine sichere Client-Produktänderung | SRV-020 PASS |
| 4 | AP-SRV-030 | keine sichere Client-Produktänderung | SRV-030 PASS |
| 5 | AP-SRV-040 | danach Opus: kontradiktorischer Contract-Review ohne Produktedit | Wire-Gate und Vektoren PASS |
| 6 | AP-SRV-050 | AP-CLI-010 mit Opus | beide bauen auf akzeptiertem SRV-040 auf |
| 7 | AP-SRV-060 | AP-CLI-030 mit Sonnet | SRV-050 und CLI-010 müssen PASS sein |
| 8 | AP-SRV-070 | AP-CLI-020 mit Sonnet | SRV-060 muss PASS sein |
| 9 | frei für Korrektur/Evidence | AP-CLI-040 mit Sonnet | CLI-020 und CLI-030 PASS |
| 10 | frei für Korrektur/Evidence | AP-CLI-050 mit Sonnet | CLI-040 PASS |
| 11 | Koordination: AP-INT-010 | Opus: unabhängiger Vertragsaudit | festes SRV-070-/CLI-050-Commitpaar |
| 12 | Koordination: AP-INT-020 | Sonnet nur als Evidence-Hilfe bei Bedarf | INT-010 PASS |

### Warum die Servervorleistung nicht künstlich parallelisiert wird

AP-CLI-010 benötigt einen getesteten Wire-Contract aus AP-SRV-040. Würde der
Client vorher gegen bloße Annahmen implementiert, entstünden doppelte
Korrekturen genau an der kritischsten Schnittstelle. Deshalb folgen nach den
parallelen Baselines zunächst vier serielle Serverpakete. Die Claude-Lane kann
in dieser Zeit Aufträge, Fixtures oder Reviews vorbereiten, ändert aber keinen
Client-Produktcode vor dem Gate.

Der optionale Opus-Review in Welle 5 startet erst nach der GPT-Abgabe von
AP-SRV-040 und liest einen stabilen Diff. Er arbeitet nicht gleichzeitig
schreibend im Server-Repository.

Ab Welle 6 entstehen wieder echte, sichere Parallelfenster:

```text
SRV-040 PASS
├── SRV-050 ──→ SRV-060 ──→ SRV-070
└── CLI-010 ──→ CLI-030 ─┐
             SRV-060 ──→ CLI-020 ─┴→ CLI-040 → CLI-050
```

## 5. Modellempfehlung je Arbeitspaket

Die Empfehlung ist kapazitätsbewusst. Opus wird nur dort eingesetzt, wo eine
zweite hochkomplexe Schnittstellen- oder Invariantenprüfung den knappen Anteil
voraussichtlich rechtfertigt. Sonnet ist der Standard für klar abgegrenzte
Client-, UI-, Dokumentations- und Aufräumpakete. GPT-5.6 Sol trägt die
serverseitige Architektur- und Concurrency-Reihe.

| AP | Primärmodell | Begründung | Fallback |
|---|---|---|---|
| SRV-000 | GPT-5.6 Sol | Ist-Charakterisierung als Basis der Serverreihe | Sonnet |
| CLI-000 | Sonnet 5 | klarer Inventar-/Testauftrag | GPT-5.6 Sol |
| SRV-010 | GPT-5.6 Sol | zentrale State-Machine und Invarianten | Opus nur bei Abnahmebefund |
| SRV-020 | GPT-5.6 Sol | Concurrency, Ledger, Exactly-once und Ordnung | Opus als gezielter Review |
| SRV-030 | GPT-5.6 Sol | Timer-/Race-/Recoverylogik | Sonnet für isolierte Korrektur |
| SRV-040 | GPT-5.6 Sol | öffentliche Protokollgrenze | Opus als unabhängiger Review |
| SRV-050 | GPT-5.6 Sol | Auth-, Scope- und Apply-Policy-Vertrag | Sonnet |
| SRV-060 | GPT-5.6 Sol | Wake-Detection, Ressourcen und Audiogrenze | Opus nur bei Messdatenproblem |
| SRV-070 | GPT-5.6 Sol | serverseitiger Cut bei parallelem Claude-Clientpaket | Sonnet, falls allein ausgeführt |
| CLI-010 | Opus 5 | kritischster Client-Vertrag: Mirror, Resync, Background Finals | Sonnet mit verstärktem Root-Review |
| CLI-020 | Sonnet 5 | lokale Bedien-/Geräteadapter gegen stabile Commands | GPT-5.6 Sol |
| CLI-030 | Sonnet 5 | UI, Credential Manager und definierte Apply-Policies | GPT-5.6 Sol |
| CLI-040 | Sonnet 5 | klarer Feedback-/Resultatumbau | GPT-5.6 Sol |
| CLI-050 | Sonnet 5 | Legacyabbau, Build und Dokumentabgleich | GPT-5.6 Sol |
| INT-010 | Koordination + Opus-Review | hoher Wert eines unabhängigen Contract-Audits | Koordination allein |
| INT-020 | Koordination, optional Sonnet | Tests/Hardware-Evidence wichtiger als Maximalmodell | GPT-5.6 Sol |

Opus ist damit regulär nur für AP-CLI-010 und den Audit von AP-INT-010
eingeplant. Der Review von AP-SRV-040 ist die erste optionale Reserve und wird
nur verwendet, wenn das Nutzungslimit dies erlaubt.

## 6. Operativer Start und Rückgabe

Vor jedem Run wird aus `ARBEITSPAKETE/AUFTRAGSVORLAGE.md` ein konkreter
`PROMPT.md` erzeugt. Noch nicht benötigte AP-Prompts werden nicht im Voraus
ausformuliert, damit Start-SHAs, Ist-Code und Abnahmebefunde aktuell bleiben.

Claude Code ist lokal als CLI verfügbar. Der konkrete Lauf wird aus dem
Repository des APs mit explizitem Modell, Auftragsdatei und strukturierter
Ausgabe gestartet. Die Koordination verwendet keinen
`--dangerously-skip-permissions`-Modus. Session-ID und Resultat werden für
eine mögliche gezielte Fortsetzung über `--resume` festgehalten.

Der Codex-Sub-Agent erhält denselben Auftrag mit explizitem Repositorybesitz
und dem Hinweis, dass parallel in einem anderen Repository gearbeitet wird.
Keiner der Agents darf fremde Änderungen zurücksetzen oder das nächste AP
vorwegnehmen.

Beide Repositories verwenden den Branch
`feat/einheitliche-triggerarchitektur`. Der Serverbranch wird vor Welle 1 mit
der GitHub-Remote verbunden. Bereits dort vorhandene lokale Änderungen werden
als geerbter, ausdrücklich inventarisierter Baseline-Diff in AP-SRV-000
übernommen und nicht verworfen.

## 7. Startentscheidung

Nach separater Sicherung des Planungsstands kann Welle 1 ohne weitere
Architekturrunde beginnen. Die ersten beiden konkreten Aufträge werden erst
dann erzeugt und enthalten die unmittelbar vorher ermittelten HEAD-SHAs und
Baselinebefehle der jeweiligen Projektumgebung.
