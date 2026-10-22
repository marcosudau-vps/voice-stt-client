## 2026-10-22 – AP-IV2-020 / unabhängiges R02-Review: CHANGES_REQUIRED

Frische unabhängige Prüfung von PR15/Head29fb0e159c69051bedba6d097f69a5974fc09528: bestehende reale Windows-/Wake-/ASR-/Frozen- und 1400-Testevidenz anerkannt im jeweils ausgewiesenen Scope. Zwei Pflichtfindings IV2-020-R02-F01 und F02 zur kombinierten 30min/100-/USB-Recovery sowie zur fehlenden Begrenzung des Sessionledgers. [R02-Abnahmebericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R02-ABNAHME/01_REPORT.md). Kein Merge, keine Release-/Serverpromotion; nächste Aktion Korrektur durch Umsetzer und unabhängige Nachabnahme.

## 2026-10-15 – AP-IV2-020 / R01 fortgesetzt: Recovery technisch requalifiziert

Ausdrückliche enge Scope-Ausnahme gesichert; derselbe Branch/R01/Draft-PR15.
Zehn nachgewiesene Client-Reconnect-/Recoveryfehler korrigiert, rote Repros und
Regressionen dokumentiert. Produkt41ca761, neue EXE/Wheel/sdist identitätsgebunden.
1373 Windows-Tests,11 Prozessfälle,1964 Server-Unit-Tests/14 optionale Skips,
native und reale lokale Modell-/Recoveryprüfungen grün. Drei Serverneustarts,
kein vorzeitiges PCM/Triggerfenster, Run-Pausen erhalten. V1/VPS unberührt.
Phase C vorbereitet; echte M-Gates/Kalibrierung/30min100 offen, kein REVIEW_READY.
[Audit](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/05_RECONNECT_AUDIT.md).

## 2026-10-15 – AP-IV2-020 / R01-UMSETZUNG: BLOCKED

AP010-Squash b80ed8b nach PASS/Freigabe tatsächlich verifiziert. Lokaler Serverada13b0
mit555 exakten Blobs, echten Community-/ONNX-Modellen und isolierten Daten bereit;
V1/VPS geschützt. Windowsbaseline1354, finale1360 und11 Prozessprüfungen PASS.
Echte Restart-Recovery zweimal FAIL: IV2-020-F01, temporärer HTTP-Vorcheck latcht
permanent BLOCKED. Noch nicht angewandter enger Clientpatch und gebündelte Realtest-
und Kalibrierungsabläufe gesichert. Produktänderungsfreigabe nötig. Reale Pflichtgates
offen; kein REVIEW_READY/PASS. R01 bleibt für dieselbe Fortsetzung zuständig.

## 2026-10-14 – AP-CV2-110 / R03-UEBERNAHME: menschliche Mergefreigabe gesichert

Wörtlicher Auftrag „Hiermit wird die Freigabe zun Merge von PR #13, Arbeitspaket AP-CV2-110 erteilt. Bitte führe den Merge durch.“ in [R03-Originalprompt](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) gesichert. Unabhängiger R02-PASS auf `44cf9a8fd1669242c00997966addc3667d448aa0` / Tree `46a4e6205b735ac202dcd611494d306936f8edc3`, freigegebener Head `84b72e11b64d0d6220fe239614301dfd569d8256` / Tree `b1fa7e771b8c19ae9865eecabc5134d84497f2f9`, kanonischer Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`. Vorfreigabe-CI 38531198371 erfolgreich. R03-Nachtrag nur administrativ; endgültige PR-Spitze braucht grüne CI. **READY_FOR_CANONICALIZATION**, noch keine Übernahme/kein AP-IV2-010 vor tatsächlichem Squash und Baumprüfung.

## 2026-10-14 – AP-CV2-110 / R02-ABNAHME: unabhängiger ROOT_PASS

PR #13, geprüfter Head `44cf9a8fd1669242c00997966addc3667d448aa0`, Tree `46a4e6205b735ac202dcd611494d306936f8edc3`, Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`, Server `ada13b0...`: sieben FINAL-Requirements unabhängig PASS; keine Pflichtfindings. 1353 lokale Windows-, 234 gezielte Tests und 17 Serverchecks als externe Belege validiert, finaler CI-Run 38440922508 auf geprüftem Head erfolgreich. [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md). **WAITING_FOR_APPROVAL**, kein Merge, Tag, Release oder Start AP-IV2-010 ohne menschlichen Auftrag und tatsächliche kanonische Übernahme.

## 2026-10-13 – AP-CV2-090 / R03-UEBERNAHME: menschliche Squash-Freigabe gesichert

PR #11 auf `work/client-v2/ap-cv2-090` gegen `feat/client-v2`, kanonischer Parent `1bc5be893060e0d6a80e1d890102bfffebb73a17`. Tatsächlicher Nutzerauftrag „Hiermit wird die Freigabe zun Merge von PR #11, Arbeitspaket AP-CV2-090 erteilt. Bitte führe den Merge durch.“ in [R03-Originalprompt](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-090/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) unverändert gesichert. Unabhängiger R02-PASS auf `51d20aa24b41a125acbf2a3cd50df1477eb0c79b`; freigegebener Head beim Auftrag `04ad97c1d58d24a0b9f76ad1cd9cdb4841f0e92e` / Tree `b9968a3f71738b97c27eafe4b7f39cb427390f02`; CI #38335152161 completed/success. R03 ist rein administrative Freigabedokumentation, technischer Status weiter ROOT_PASS, Workflow READY_FOR_CANONICALIZATION. Vor GitHub-Squash finalen Head/Base/CI, allein administrative R03-Änderungen und Treegleichheit nach Merge prüfen. Keine vorweggenommene ACCEPTED-Aussage und kein AP100-Autostart.

## 2026-10-13 – AP-CV2-090 / R02-ABNAHME: unabhängiger ROOT_PASS

PR #11, geprüfter Kandidat `51d20aa24b41a125acbf2a3cd50df1477eb0c79b`, Tree `d52aeda488d55b61b9d1c1d744ad0ab09fdf69d4`, Parent `1bc5be893060e0d6a80e1d890102bfffebb73a17`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`: neun FB-Anforderungen unabhängig PASS, keine offenen Pflichtfindings. Windows-R01-Fremdbelege 1552 Tests und 377 gezielte, 18 echte gepinnte Domain-/Log-/Qtcheckpointchecks sowie 13/13 eigene Kandidaten-Gitblobstichproben geprüft, GitHub-CI 38331762953 erfolgreich. Eigene Windowswiederholung NOT_RUN (zulässig). [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-090/RUNS/R02-ABNAHME/01_REPORT.md). Workflow WAITING_FOR_APPROVAL, kein Merge oder AP100 ohne menschliche Freigabe.

## 2026-10-12 – AP-CV2-050: unabhängige technische Abnahme R02

PR #7; geprüfter Kandidat `55d6ca6b4d222fac9bba66a4911c7a6b8c236a0a`, Tree `3b0dc469a1a3e577eb4dda0a67e2f3746b9c92cd`, kanonischer Parent `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`: **ROOT_PASS** für CONTROL-01 bis CONTROL-14, keine offenen Pflichtfindings. 1397 Windows-, 297 gezielte, 79 echte lokale TCP/WS-Server- und 16 native Win32-Checks als Fremdbelege geprüft; eigene Windows-Wiederholung NOT_RUN. [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-050/RUNS/R02-ABNAHME/01_REPORT.md). Workflow WAITING_FOR_APPROVAL; kein Merge und kein AP060 ohne menschliche Übernahmefreigabe.

## 2026-10-12 – AP-CV2-030: unabhängige Abnahme R02

PR #5, geprüfter Kandidat `d062ce2ec8d6d9c0683dc6be09397e11cdbd7e61`, Tree `7123984bb4b382919e557f4ecef1400de4eced29`, Parent `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0`: **ROOT_PASS** für 35/35 FG-/SYNC-IDs nach unabhängiger Code- und Fremdevidenzprüfung; 1339 Windows-, 106 Targeted-Tests und 35 gepinnte Serverchecks grün, GitHub-CI grün. Eigene Windows-Suite regelkonform NOT_RUN. [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-030/RUNS/R02-ABNAHME/01_REPORT.md). Status WAITING_FOR_APPROVAL; menschliche Übernahme noch offen, AP040 nicht begonnen.

# Verlaufs-Log

## Hinweise / Beginn

- Vorher gab es eine Implementierungs-Serie mit Antigravity.  (Liegt unter "P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur")
- Das Ergebnis davon hatte schwerwiegende Lücken und vieles was geplant war nicht richtig umgesetzt.
- Da aber schon viel gute Arbeit dadurch vorhanden war, wurde darauf aufbauend eine Implementierungs-Serie mit Claude gestartet.
  in der geschaut werden sollte was übernommen wird und der Rest final fertig gestellt werden sollte.
- An dieser Stelle setzt dieser Ablauf-Log ein.
- Zeiten sind teilweise Schätzungen oder Rekonstruiert und können deshalb ungenau sein.

## Verlauf

- 14.08.2026 02:18, 001_VerbindlicherAusführungsauftrag_EinheitlicheServerseitigeTriggerarchitektur_UrsprünglicherAgyPrompt.md, 001_2026-08-14_Prompt.md
  - Beschreibung: Hier hat Claude das Übernommen und ausführliche Anweisungen zu der Vorgeschichte mit Anti-Gravity erhalten. Daraufhin Begann er mit der  Haupt-Implmentierungs-Phase.

- 14.08.2026 09:03, 002_2026-08-14_Prompt_Restarbeiten,_belastbareEndabnahme_und_vollständigeDokumentationsprüfung.md
  - Beschreibung: Die Ergebnisse nach der ersten Implementierungsphase sahen bereits so gut aus und die Tests waren alle grün, dass wir dachten, es wäre nur noch weniger   vervollständigende Restarbeiten und Vorbereitungen auf den Release-Push, z.B: Docs, letzte Nachweise, etc..

- 14.08.2026 15:56, Manueller Test
  - Beschreibung:
    Es wurde ein echter Test mit Hardware und Liveaufnahme gemacht.
    Dabei sind dann die Fehler der Claude-Implementierung aufgefallen.
    Zunächst war noch nicht klar, welchen Umfang sie haben.

- 14.08.2026 15:56, 003_CLAUDE_DIAGNOSEAUFTRAG_TRIGGERARCHITEKTUR.md
  - Beschreibung:
    Um herauszufinden, wie weit die Fehler in die Architektur greifen und wo überhaupt die Fehlerquellen sind oder ein Diagnoseauftrag gegeben.
    Der sollte erstmal analysieren, was los ist.Dabei kam heraus, dass die Änderungen bzw. Fehler tiefgreifender sind als ursprünglich gedacht und auch wirklich weit in die Architektur hineingehen.
    Alte Komponenten wurden entdeckt, die noch nicht komplett entfernt wurden.
    Ab diesem Zeitpunkt war klar, dass eine größere Umbauaktion noch erforderlich sein würde.

- 14.08.2026 16:43, 004_Opus-Sonderauftrag - Code-Only Architekturaufnahme vor Limit-Reset.md
  - Beschreibung:
    Als nächstes wurde jetzt ein Auftrag erteilt, um den Ist-Stand des tatsächlichen Codes zu analysieren.
    Es ging darum, festzustellen wo die Fehler-Schwerpunkte liegen und welche Komponenten wie stark betroffen sind.
    Es wurde explizit darauf geachtet, dass die Analyse nur am Code stattfindet und beispielsweise nicht die Dokumentation mit zur Rate gezogen wird, um ein realistisches Bild zu erhalten.

- 14.08.2026 23:00
  - Beschreibung:
    Nach Auswertung der Informationen zum Istzustand des Codes wurde analysiert, wo die Missverständnisse und falschen Interpretationen des Ziel-Zustandes aufgetreten sein könnten und welche Formulierungen gegebenenfalls nicht deutlich oder scharf genug waren.
    Es wurde daraufhin eine neue Fassung der Gesamtspezifikation und des Endgültigen Zielmodell's formuliert, In der die Aspekte, die mutmaßlich zum Missverständnissen geführt haben, nochmal deutlich hervorgehoben und klargestellt wurden.
    Es wurde begonnen einen grundlegenden Plan zur Migration aufzustellen. Dabei stand zuerst nicht der inhaltliche Teil im Fokus, sondern eher das methodische Vorgehen. Dazu wurden einige Planungsdateien erstellt, z.B. Checklisten.

- 14.08.2026 23:26, 005_2026-08-14_Prompt_LetzteGezielteArchitekturklarungVorPlanFreeze.md
  - Beschreibung:
    Nach Sichtung der letzten Analyseergebnisse und einigen Beratungen wurden die Migrations-Schwerpunkte genauer untersucht.
    Es wurde dann herausgearbeitet, welche Informationen aus dem Code konkret noch fehlen.
    In diesem Auftrag ging es darum die letzten benötigten spezifischen Detailinformationen.Zu den Schwerpunkten zu erhalten.
    Im Laufe der Beratungen und der Planungen wurde beschlossen, dass es sinnvoll sei, vor der eigentlichen Migrationsarbeit noch ein Loggingmodul hinzuzufügen in einem seperaten Arbeitsprozess, da dies die Migration und den Arbeitsprozess dort deutlich erleichtern würde.
    Da ist schon eine konkrete Planung zu dem Loggingmodul gab, An die angeknüpft werden konnte.Musste das Logging-Modul einmal komplett mit der gesamten Architektur geplant werden und es wurde eine Zielspezifikation dafür formuliert.
     Diese soll jedoch nicht komplett vor der Migration umgesetzt werden, sondern es soll gesplittet werden in einen Teil der vorher kommt, der die Basics enthält, die erstmal für die Arbeit der Migration reichen.
    Ein anschließender Teil, in dem die Comfort Features dann noch hinzugefügt werden. Dieser soll aber erst nach der Migration umgesetzt werden.

- 15.08.2026, RUN-OBS-000-01_2026-08-15_CLAUDE, PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md
  - Workstream: OBS (Logging / Observability), Work Package: OBS-000 – Plan Freeze & Baseline
  - Ergebnis / Gate: **OBS-000 PASS**, zusätzlich **OBS-010 READY FOR IMPLEMENTATION** (Readiness-Review: PASS)
  - Beschreibung:
    Damit ist der Logging-Workstream aus der Planungsphase heraus. Die vorher verstreuten Grundlagen — die Zielspezifikation, die V1-Abgrenzung, die sieben Claude-Codeanalysen und das adversariale Review — sind zu einer einzigen, widerspruchsfreien Sollgrundlage zusammengeführt worden.
    Alle Architekturentscheidungen sind geschlossen; die einzige wirklich blockierende (der Paketname) ist zugunsten von `core/observability/` entschieden. Neunzehn Widersprüche zwischen den Quellen wurden benannt und aufgelöst, drei davon in diesem Lauf neu gefunden. Die letzte offene Informationslücke — ob die Client-Roadmap dem Logging-Plan widerspricht — ist geprüft und geschlossen: sie tut es nicht.
    Vier Entscheidungen weichen bewusst von einer ausdrücklich benannten Anforderung der Entwürfe ab und sind deshalb gesondert ausgewiesen. Die sichtbarste: der geplante Memory-Ringbuffer entfällt: die Live-Ansicht bleibt vollständig erhalten, wird aber als tailende Datenbankabfrage gebaut. Das spart eine Komponente und entkoppelt die Oberfläche vom Schreibprozess.
    Es wurde ausschließlich gelesen und geplant. Kein Produktcode, kein Testcode und keine Produktconfig wurden verändert, kein Commit gesetzt.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/30_AUSFUEHRUNG/runs/RUN-OBS-000-01_2026-08-15_CLAUDE/RUN_REPORT.md`
    - `ARBEITSDATEIEN/AP_THEMA_LOGGING/40_EVIDENCE/OBS-000/`
  - Nächster Schritt: Arbeitsbaum des Clients festschreiben, danach OBS-010 umsetzen.

- 17.08.2026, Repository-/Workspace-Reorganisation und Baseline
  - Ergebnis / Gate: **Reorganisation abgeschlossen**, **Baseline-Commit erstellt**
  - Beschreibung:
    Der gesamte Workspace-Root wurde aus `marcosudau-vps` + `marcosudau-vps-worktrees`
    (mit parallelen Bereichen main / aktivem Trigger-Workspace / Antigravity-Referenz /
    manuellem Testbestand / Backups) in eine einheitliche Struktur unter
    `P:\GithubRepos\marcosudau-vps\<projekt>\{main,workspaces\einheitliche-triggerarchitektur}`
    überführt. Vorher wurde eine vollständige, validierte Vollsicherung angelegt
    (`P:\GithubRepos\_BACKUP_BEFORE_REORG_20260817\`); die ursprüngliche physische
    Struktur wurde danach unverändert (nicht gelöscht) nach
    `P:\GithubRepos\_LEGACY_BEFORE_REORG_20260817\` verschoben.
    Der aktive Client-Workspace liegt jetzt unter
    `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`.
    Die bereits begonnene ARBEITSDATEIEN-Migration wurde am neuen Pfad abgeschlossen:
    leere Alt-Ordner unter `docs/` entfernt, `docs/archive/..._VERWORFEN.md` nach
    `ARBEITSDATEIEN/90_HISTORIE/VOR_NEUEM_ARBEITSSYSTEM/archive/` verschoben. Der frühere
    Ordner `docs/2026-08-12_led-sound-debugfeedback` war über die Git-Historie dieses
    Repos nicht auffindbar und wurde daher nicht rekonstruiert (nur dokumentiert, kein
    OBS-010-Blocker). Anschließend genau ein lokaler Baseline-Commit
    ("chore: establish OBS-010 project baseline and work archive") auf dem technischen
    Vorgänger `5f2ee4bfceda2cec5bb6ddd0e8c28b2c6c371e1c` erstellt. Kein Push, kein Merge,
    kein Rebase, kein Tag, keine Produktcodeänderung.
  - Nächster Schritt: OBS-010 Implementierung.

- 17.08.2026, RUN-OBS-010-01_2026-08-17_DEEPSEEK, OBS-010_DEEPSEEK_IMPLEMENTIERUNGSAUFTRAG.md
  - Workstream: OBS (Logging / Observability), Work Package: OBS-010 – Canonical Model, Redaction, Normalizer & Contracts
  - Ergebnis / Gate: **OBS-010 IMPLEMENTED – READY FOR CLAUDE GATE REVIEW**
  - Beschreibung:
    Der freigegebene OBS-010-Scope wurde vollständig umgesetzt. Es entstehen
    ausschließlich neue Dateien: das Paket `core/observability/` (models.py,
    redaction.py, normalizer.py, ingress.py-Protokoll, storage/base.py,
    sinks/base.py, query/base.py) sowie 127 Contract-Tests unter
    `tests/test_obs010_*.py`. Kein bestehender Test und keine bestehende
    Produktdatei wurden geändert.
    Die drei Normalizer-Eingänge, die Redaction (R-3/8/9/10/11/12, `unfreeze`,
    hello-Whitelist R-6) und das kanonische Recordmodell entsprechen den
    eingefrorenen Verträgen (CONTRACTS §1–§4, §8; ARCH §5). Die zwei Pflicht-
    Mutationschecks (Redaction entfernen → rot, `unfreeze` entfernen → N-01 rot)
    wurden ausgeführt und belegt.
    Tests: vollständige Client-Suite 640 passed (513 Baseline + 127 neue), beide
    Runner grün; `git diff --check` leer; kein Commit/Push; Server-/LED-Repo
    unberührt. Evidence unter `40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/`,
    Run-Dokumentation unter `30_AUSFUEHRUNG/RUN-OBS-010-01_2026-08-17_DEEPSEEK/`.
  - Wichtigste Artefakte:
    - `core/observability/{models,redaction,normalizer,ingress}.py`
    - `core/observability/{storage,sinks,query}/base.py`
    - `tests/test_obs010_*.py` (7 Dateien)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/RUN-OBS-010-01_2026-08-17_DEEPSEEK/`
  - Nächster Schritt: Claude Review / Gate OBS-010 in frischer Session; danach OBS-020.

- 17.08.2026, OBS-010 Gate Review, `Prompts/OBS-010_GATE_REVIEW.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-010 – Canonical Model, Redaction, Normalizer & Contracts
  - Ergebnis / Gate: **OBS-010 GATE PASS – OBS-020 MAY PROCEED**
  - Beschreibung:
    Unabhängiger Review in frischer Session, gegen den tatsächlichen Repository-
    zustand, `git diff`/`git status`, einen eigenständigen Testlauf und die
    Evidence geprüft — nicht nur gegen `RUN_REPORT.md`. Feldliste/Typen/Defaults
    von `CanonicalLogRecord` stimmen exakt mit `CONTRACTS §1.1/§1.4` überein
    (inkl. Ausschlussliste); Prioritätsableitung (§1.5, inkl. `not replayed`),
    `scope`-Herleitung (§1.3, inkl. `led`/`other` → `instance`), die drei
    Normalizer-Eingänge (§3.1–§3.3, u. a. `LOGGER_CHANNEL_MAP`, `session_id`/
    `generation`/`segment_id` ausschließlich aus `record.__dict__`, `component`
    bei Controlframes fest `"eventstream"`) sowie Redaction R-1..R-12
    (`unfreeze`, hello-Whitelist R-6, Transkript-Zeichenzahl R-10, Tiefen-/
    Knotengrenze R-12) wurden Feld für Feld gegen den Code geprüft, nicht nur
    gegen die Test-Coverage-Tabelle. Eigenständiger pytest-Lauf: 640/640 grün
    (513 Baseline + 127 neu, isoliert `-k obs010`: 127/127); `git diff --check`
    leer; nur `core/observability/**` und `tests/test_obs010_*.py` neu, keine
    bestehende Produktdatei verändert. Diagnoseskript
    (`OBS-010_RUN-01_hello_redaction_diagnose.py`) unabhängig erneut ausgeführt:
    Exit 0, `accessToken` auf keiner Ebene im Ergebnis.
    Gesondert geprüfter Punkt aus dem Implementierungsbericht: „Server-`raw`
    ohne Kopie/Redaction im Normalizer". Befund: **keine Verletzung** der
    Immutability-/Non-Mutation-Anforderung. `models._freeze` gibt eine bereits
    als `MappingProxyType` übergebene `raw`-Payload unverändert per Identität
    zurück (kein rekursives erneutes Einfrieren) — das ist wörtlich durch
    `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.2` gefordert ("Der Ingress nimmt die
    bereits eingefrorene Referenz entgegen und kopiert nichts"). Verifiziert
    wurde zusätzlich am Code, dass `EventProtocolResult.payload`
    (`core/event_protocol.py::_freeze_value`, acht Aufrufstellen) beim Bau
    rekursiv **neue** `MappingProxyType`/`tuple`/`frozenset`-Objekte aus einer
    Dict-Comprehension erzeugt und nirgends die ursprüngliche mutierbare
    Struktur referenziert — es existiert also keine lebende, von außen
    mutierbare Referenz, über die eine spätere Mutation in den Record
    durchschlagen könnte. Für `details` bleibt es unabhängig davon bei einer
    echten Kopie/Neuaufbau (Redaction baut immer eine neue Struktur); für
    `from_client_event` existiert `raw` als Parameter ohnehin nicht. Damit ist
    „ohne Kopie" ein bewusster, vertragskonformer Performance-Entscheid und
    keine Lücke. Kein `FAIL`-Befund in keiner der Pflichtprüfungen (Contract-/
    Anforderungsabdeckung, Scope-Treue, Implementierungsqualität, Fehler-/
    Randfälle, Regressionen, Testqualität — Tests nutzen den echten
    `EventProtocolProcessor` und reale `test_event_protocol.py`-Fixtures statt
    reiner Testdoubles —, Evidence-Konsistenz, `git diff --check`, finaler
    Git-Status, keine unzulässigen Änderungen außerhalb des Work Packages).
    Readiness-Check OBS-020 (verbleibende Zeit genutzt, keine Implementierung
    begonnen): Voraussetzung „OBS-010 Gate PASS" jetzt erfüllt;
    `core/observability/ingress.py` enthält bislang nur das für OBS-020
    vorgesehene `Ingress`-Protokoll (kein `ObservabilityIngress`, kein
    `NullIngress`) und `core/logging_setup.py` ist unverändert — beides wie von
    WP-OBS-020 vorausgesetzt.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/` (erneut geprüft)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-010 Gate Review abgehakt)
  - Nächster Schritt: OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler (Implementierung, frische Session).

- 17.08.2026, RUN-OBS-020-01_2026-08-17_CLAUDE, `Prompts/OBS-020_IMPLEMENTIERUNGSAUFTRAG.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler
  - Ergebnis / Gate: **OBS-020 IMPLEMENTED – READY FOR REVIEW** (kein Gate PASS in diesem Run)
  - Beschreibung:
    Voraussetzung (OBS-010 GATE PASS) laut `CURRENT_STATE.md` erfüllt. Der
    freigegebene Scope wurde vollständig umgesetzt: `core/observability/health.py`
    neu (`LoggingHealthState`, `LoggingHealthSnapshot`, `LoggingInternalHealth`
    mit einem Lock für alle Zähler inkl. `deduplicated`, der eigene
    nicht-propagierende Logger `observability.internal` mit ratenbegrenztem
    Emergency-stderr-Kanal, G-2/G-4); `core/observability/ingress.py` additiv um
    `ObservabilityIngress` (`submit`/`observe_server_result`/`event`/`drain`,
    CONTRACTS §6, eine bounded Queue mit Wasserstandsregel bei 75 %),
    `NullIngress`, `NULL_INGRESS` erweitert — das OBS-010-`Ingress`-Protocol
    blieb unverändert; `core/observability/adapters/python_logging.py` neu
    (`UnifiedLogHandler` mit Wiedereintrittssperre G-1, Health-basiertem
    `handleError` G-3, No-Op `flush()`/`close()` G-7, internem-Logger-Filter);
    `core/logging_setup.py` additiv um den optionalen Parameter
    `observability=None` und einen optionalen dritten Handler erweitert.
    Einzige geänderte Zeile in `core/logging_setup.py` ist die
    Funktionssignatur (exakt der Sollzustand-Codeblock des Work Packages);
    der gesamte bisherige Funktionskörper ist byte-identisch erhalten.
    75 neue Tests über sechs Dateien (Positiv/Negativ/Failure/
    Nebenläufigkeit-und-Zeit/Integration/Contract sowie ein gesonderter
    End-zu-Ende-Nachweis, dass die OBS-010-Redaction durch die neue Pipeline
    unverändert wirkt — Secrets, nicht-sensible Struktur, Audio-Payload-Abwehr,
    Transkript-Policy, keine Mutation der Eingangsdaten). Vollständige
    Client-Suite danach 715/715 grün (640 Baseline + 75 neu), kein
    bestehender Test geändert. `git diff --check` leer; `git diff --stat`
    zeigt nur `core/logging_setup.py` als geänderte Produktdatei; kein
    Cross-Workstream-Diff. Ein eigenständiges Diagnoseskript lädt die
    Vor-Änderungs-Fassung von `core/logging_setup.py` direkt aus
    `git show HEAD:...` (ohne den Arbeitsbaum anzufassen) und bestätigt:
    `client.log` (Datei-Sink) ist mit und ohne den neuen `observability`-
    Parameter byte-identisch (Exit 0). Nebenläufigkeitsnachweis: acht Threads
    × 5000 Submits reconciliieren exakt, keine doppelten `record_id`; die
    100.000-Submits-bei-voller-Queue-Zeitmessung (~15,6–18,5 µs/Aufruf, zwei
    Läufe) ist als Regressionsbasis im Testprotokoll festgehalten, bewusst
    ohne absoluten Grenzwert (ARCH §6.3). Kein Commit, kein Push. Beobachtet,
    nicht behoben: ein vorbestehender, vom `observability`-Parameter
    unabhängiger `UnicodeEncodeError` des Stdout-Handlers unter einer
    `cp1252`-Konsole (außerhalb des WP-OBS-020-Scopes).
  - Wichtigste Artefakte:
    - `core/observability/health.py`, `core/observability/adapters/python_logging.py`
    - `core/observability/ingress.py`, `core/observability/__init__.py` (additiv erweitert)
    - `core/logging_setup.py` (additiv erweitert)
    - `tests/test_obs020_*.py` (6 Dateien, 75 Tests)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/Runs/RUN-OBS-020-01_2026-08-17_CLAUDE/`
  - Nächster Schritt: OBS-020 Gate Review (frische Session), danach OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink.

- 17.08.2026, OBS-020 Gate Review, `Prompts/OBS-020_GATE_REVIEW.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler
  - Ergebnis / Gate: **OBS-020 GATE PASS – OBS-030 MAY PROCEED**
  - Beschreibung:
    Unabhängiger Review in frischer Session, gegen den tatsächlichen
    Repository-Zustand, `git diff`/`git status`, einen eigenständigen
    Testlauf, das Diagnoseskript und die Evidence geprüft — nicht nur gegen
    `RESULT.md`/`RUN_LOG.md`. `git diff --stat` bestätigt: von den
    Produktdateien ist ausschließlich `core/logging_setup.py` geändert
    (+23/-1, einzige geänderte Bestandszeile ist die Funktionssignatur, der
    restliche Funktionskörper byte-identisch), alles Übrige unter
    `core/observability/{health.py, adapters/python_logging.py}` neu bzw.
    `ingress.py`/`__init__.py` additiv erweitert (unverändert seit OBS-010:
    das `Ingress`-Protocol, `models.py`, `redaction.py`, `normalizer.py`).
    Code Feld für Feld gegen `LOGGING_CONTRACTS_FREEZE_V1.md §6/§11.2` und
    `LOGGING_ARCHITEKTUR_FREEZE_V1.md §6.3/§7/§8.1/§8.2/§8.7` geprüft:
    Wasserstandsregel (75 %, `queue_size=8192`), Prioritätsregel inkl.
    `not replayed` (N-04 im Code nachvollzogen), `LoggingHealthState`
    (7 Zustände) und `LoggingHealthSnapshot` (alle Zähler inkl.
    `deduplicated`) exakt wie eingefroren, `UnifiedLogHandler` mit
    Wiedereintrittssperre (G-1), Health-`handleError` (G-3), No-Op
    `flush`/`close` (G-7) und Filter gegen `observability.internal`, Emergency-
    Kanal mit hartem Pro-Code-Ratenlimit (G-4) und `sys.stderr`-Abwehr (G-2).
    Eigenständiger pytest-Lauf: `-k obs020` → 75/75 grün; volle Suite →
    714/715 grün. Der eine Fehlschlag
    (`test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
    `ModuleNotFoundError: No module named 'lefx.interfaces'`) ist **keine
    Regression dieses Pakets**: `git diff --stat` zeigt weder
    `core/led_controller.py` noch `tests/test_ap06_followup.py` als geändert,
    die Datei ist eine vorbestehende, unveränderte Testdatei außerhalb des
    WP-OBS-020-Scopes, und der Fehler stammt aus einer in dieser
    Prüfumgebung unvollständigen `lefx`-Paketinstallation (fehlendes
    `lefx.interfaces`-Submodul), nicht aus dem geprüften Diff. Diagnoseskript
    (`OBS-020_RUN-01_client_log_before_after_diagnose.py`) unabhängig erneut
    ausgeführt: Exit 0, `client.log` vorher/nachher byte-identisch mit und
    ohne `observability`-Parameter. `git diff --check` leer (nur harmloser
    CRLF-Hinweis zu `LOG_VERLAUF.md`).

    Gesondert geprüfter Punkt aus dem Implementierungsbericht: „raw-Referenz
    ohne Kopie". Befund: **keine Verletzung** der Immutability-/
    Non-Mutation-Anforderung, und OBS-020 öffnet dafür **keinen neuen Pfad**.
    Der einzige Ort, an dem OBS-020 `raw` überhaupt berühren könnte, ist
    `ObservabilityIngress.observe_server_result` → `normalizer.from_server_result`
    (unverändert seit OBS-010) — dieser Pfad ist in OBS-020 selbst nicht
    verdrahtet (Non-Scope laut WP-OBS-020: "keine strukturierten
    Client-Hooks, das ist OBS-040") und wird von keinem realen Aufrufer
    erreicht. Der tatsächlich in OBS-020 aktive Pfad
    (`UnifiedLogHandler` → `normalizer.from_log_record`) setzt `raw`
    überhaupt nicht (kein `raw=`-Argument beim Bau des `CanonicalLogRecord`).
    Zusätzlich neu gegenüber OBS-010 geprüft: OBS-020 führt erstmals eine
    echte `queue.Queue` ein, in der ein Record — anders als in OBS-010 — nun
    unbestimmt lange liegen kann, bevor ein künftiger Worker (OBS-030) ihn
    entnimmt. Das ändert am Befund nichts, weil die Unveränderlichkeit von
    `raw` nicht von der Verweildauer in der Queue abhängt, sondern davon, dass
    `result.payload` bereits bei seiner Konstruktion in
    `core/event_protocol.py::_freeze_value` rekursiv aus frischen Objekten
    aufgebaut wird (durch OBS-010 bereits verifiziert, durch OBS-020
    unverändert) — es existiert keine lebende, von außen mutierbare Referenz
    auf die Ausgangsstruktur, unabhängig davon, wie lange das Objekt in der
    Queue wartet. `models._freeze` gibt eine bereits als `MappingProxyType`
    übergebene Referenz wörtlich normativ gedeckt durch
    `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.2` ("Der Ingress nimmt die bereits
    eingefrorene Referenz entgegen und kopiert nichts") unverändert per
    Identität zurück. `details` bleibt davon unberührt: `_redact`/`_freeze`
    bauen dafür immer eine neue Struktur, end-to-end bestätigt durch
    `test_obs020_redaction_end_to_end.py::TestNoMutationOfInputData`
    (eigenständig nachvollzogen). §8.2 hält zusätzlich fest, dass Entfrieren,
    Serialisieren und Redigieren von `raw` bewusst erst im künftigen Worker
    geschehen (inkl. der dort fälligen 64-KiB-Größengrenze) — das ist eine
    für OBS-030 vorgemerkte, keine für OBS-020 fällige Pflicht.

    Weitere Gate-Kriterien: Ingress bleibt rein beobachtend (kein
    Rückkanal in die Runtime-Autorität), Exceptions an der
    Handler-/Normalizer-Grenze sicher isoliert (kein `reject_event`- oder
    sonstiger Laufzeitfehler durch Logging-Fehler auslösbar), Health/Counter
    erzeugen keine Rekursion (G-1..G-4 durch Tests belegt, eigenständig
    nachvollzogen), Redaction entfernt Secrets/Tokens zuverlässig
    (`test_obs020_redaction_end_to_end.py`, eigenständig grün), keine
    Audio-Payloads (Quellcode-Scan der Hot-Path-Funktionen plus
    Abwehrtest), Transcript-Inhalt folgt der Policy in beiden Richtungen,
    strukturierte nicht-sensible Daten bleiben nutzbar, OBS-030 wurde nicht
    vorgezogen (kein Worker/Store/Sink/UI/Settings-Code; `drain()` ist
    vorhanden, aber nur für den künftigen Worker reserviert und in OBS-020
    ungenutzt). Kein `FAIL`-Befund in keiner der Pflichtprüfungen.

    Readiness-Check OBS-030 (verbleibende Zeit genutzt, keine Implementierung
    begonnen): Voraussetzung „OBS-020 Gate PASS" jetzt erfüllt.
    `ObservabilityIngress.drain(max_items, timeout)` sowie alle von einem
    künftigen Worker benötigten `LoggingInternalHealth`-Zähler
    (`written`, `deduplicated`, `store_errors`, `sink_errors`,
    `retention_errors`, `db_bytes`) sind bereits im Zählerschema vorhanden,
    aber unbenutzt — der `LoggingHealthSnapshot` muss beim Bau des Workers
    keine Formänderung mehr erfahren. `ObservabilityManager` (Kompositions-
    wurzel) existiert bewusst noch nicht, wie von WP-OBS-030 vorausgesetzt.
    Kleinere, für OBS-030 vorzumerkende Beobachtung (kein Blocker): Die
    64-KiB-Größengrenze für `raw` sowie das Entfrieren/Redigieren von
    Serverpayloads im Worker (`ARCH §8.2`) sind noch nirgends implementiert —
    laut Freeze normativ dem Worker zugewiesen, also fällig in OBS-030, nicht
    in OBS-020.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/` (erneut geprüft)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-020 Gate Review abgehakt)
  - Nächster Schritt: OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink (Implementierung, frische Session).

- 17.08.2026, OBS-030 Implementierung (`RUN-OBS-030-01_2026-08-17_CLAUDE`)
  - Beschreibung:
    OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink implementiert.
    Neue Module: `core/observability/storage/sqlite.py` (`SQLiteLogStore`:
    DDL/Migration/Indizes nach `CONTRACTS §5.2`, `write_batch` mit
    Replay-Dedupe über den partiellen UNIQUE-Index und `(eingefügt,
    dedupliziert)`-Rückgabe, `run_retention` blockweise/zeitbudgetiert,
    `clear()`, `measure_db_bytes()`), `core/observability/sinks/jsonl_file.py`
    (`JsonlSink`: `schemaVersion` zuerst, Tagesrotation, Größenlimit),
    `core/observability/worker.py` (`LoggingWorker`: dedizierter Daemon-
    Thread, Batching/Flush, raw-Redaction+64-KiB-Truncation **im Worker**
    nach `ARCH §8.2`, Retry-einmal-dann-verwerfen plus Circuit-Breaker bei
    5 aufeinanderfolgenden Fehlschlägen, `disk full` setzt `FAILED_STORE`
    und pausiert Retention, Backpressure-Zustandsübergänge `DROPPING`↔`OK`
    inkl. synthetischer `logging.records_dropped`/`logging.recovered`-
    Records nach `ARCH §7.3`/`G-6`, `request_clear` für „Diagnosehistorie
    löschen"), `core/observability/manager.py` (`ObservabilityManager` als
    Kompositionswurzel inkl. `_NullStore`-Fallback für `store_enabled=False`).
    Additiv erweitert: `core/observability/health.py`
    (`reset_drop_counters`, `record_written`, `record_deduplicated`,
    `record_dropped_shutdown` mit optionalem `count`), `core/observability/__init__.py`
    (vier neue Re-Exports), `app.py::main()` (Manager wird nach
    `AppConfig.load()` gebaut/gestartet, `setup_logging(...,
    observability=...)`, `stop(2.0)` im `finally`, nach `run_gui`s internem
    `bridge.stop(10.0)` — AR-5/AR-6). `core/config.py` erhielt zusätzlich
    `LoggingObservabilityConfig` (Schema nach `CONTRACTS §10.1`) und die
    zugehörige `_from_dict`-Sonderbehandlung analog `history` — als für
    diesen Run zwingend erforderliche minimale Schnittstelle (die
    `app.py`-Verdrahtung braucht eine echte Konfiguration), ausdrücklich als
    solche dokumentiert; die volle Settings-**UI**-Integration (Nachweis
    N-12) bleibt OBS-050.

    Während der Ausführung zwei reale Befunde behoben, nicht nur geplant:
    (1) `ON CONFLICT (producer_id, event_id) DO NOTHING` schlug gegen den
    partiellen Index fehl, bis die `WHERE event_id IS NOT NULL`-Klausel auch
    im `ON CONFLICT`-Ziel wiederholt wurde (SQLite-Pflicht bei partiellen
    Unique-Indizes als Arbiter). (2) Ohne die `_from_dict`-Sonderbehandlung
    für `logging.observability` brach `AppConfig.save()` → `AppConfig.load()`
    für **bestehende** Tests (`test_history.py`, `test_text_injector.py`,
    `test_feedback_mapping.py`, `test_ap06_followup.py::TestSettingsDialog`),
    weil `save()` das neue Feld vollständig serialisiert und der generische
    `_build`-Pfad die verschachtelte Dataclass nicht auflöst — behoben durch
    dieselbe Sonderbehandlung wie bei `history`, siehe `RUN_LOG.md` für die
    vollständige Herleitung.

    82 neue Tests (`tests/test_obs030_*.py`, 7 Dateien): SQLite-Store
    (DDL/Round-Trip/Dedupe/Migration/Retention/N-05-Fremdthread/
    Nebenläufiger-Leser/Neustart, 24), Worker (Ende-zu-Ende
    `logger.info -> SQLite`, Batching, HIGH-Sonderregel/N-04,
    Worker-/Store-/Sink-Fehler, raw-Redaction+Truncation, Retention-Kadenz,
    `request_clear`, Health-Zähler, Shutdown-Flush, Thread-Aufräumung, 20),
    JSONL-Sink (7), Manager (Lifecycle/Ende-zu-Ende/deaktiviert/
    Neustart-über-zwei-Instanzen, 8), Contracts/Isolation (11 + 10 Subtests),
    Config (Defaults/Validierung/Save-Load-Roundtrip, 10),
    App-Wiring (2). Vollständige Suite: 796/797 grün (pytest: 796 passed +
    1 vorbestehender Fehlschlag; `unittest discover`: 797 Tests, derselbe eine
    Fehlschlag) = 715 (Baseline nach OBS-020) + 82 neue. Kein bestehender Test
    geändert. Der eine Fehlschlag (`test_ap06_followup.py`, `lefx.interfaces`
    fehlt lokal) ist identisch zum vorbestehenden, dokumentierten
    Umgebungsbefund und außerhalb des Diffs. Nach `stop()` bleibt in keinem
    Test ein `RealtimeSTT-Observability`-Thread aktiv, geprüft unter `pytest`
    **und** `unittest discover`. `git diff --check` leer;
    `git diff --stat` zeigt ausschließlich `app.py`, `core/config.py`,
    `core/observability/__init__.py`, `core/observability/health.py` als
    geänderte bestehende Dateien — kein Cross-Workstream-Diff
    (`core/controller.py`, `core/session_coordinator.py`,
    `ui/application.py`, `ui/core_bridge.py` unverändert).

    **Kein Gate-PASS in diesem Run** — laut Work Package erfordert das Gate
    einen separaten Review.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-01_2026-08-17_CLAUDE/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-01_2026-08-17_CLAUDE/`
  - Nächster Schritt: OBS-030 Gate Review (frische Session, unabhängig).

- 17.08.2026, OBS-030 Gate Review, `Prompts/OBS-030_GATE_REVIEW.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Ergebnis / Gate: **OBS-030 GATE FAIL**
  - Beschreibung:
    Unabhängiger Review in frischer Session gegen den tatsächlichen
    Repository-Zustand, `git diff`/`git status`, eigenständige Testläufe und
    zusätzlich eigene Laufzeitproben — nicht gegen `RESULT.md`/`RUN_LOG.md`.
    Die Kernmechanik ist belastbar und wurde nachgemessen: Nebenläufigkeit
    (8 Producer-Threads x 1500 Records plus gleichzeitig pollender Leser mit
    `PRAGMA query_only = ON` → `enqueued = written = 12000 Zeilen`,
    `integrity_check ok`, keine Drops, ~22 µs/`submit`, kein Thread-Leck),
    Shutdown-Buchhaltung (1000 eingereiht = 20 geschrieben + 980
    `dropped_shutdown`, genau eine ratenbegrenzte stderr-Zeile, kein Thread
    übrig), Persistenz und Dedupe-Identität über Prozessläufe hinweg
    (identisches `(producer_id, event_id)` im zweiten Manager-Lauf →
    `deduplicated=1`, weiterhin eine Zeile), Retention blockweise/
    zeitbudgetiert ohne `VACUUM`, Migration (`user_version = 99` → Nur-Lesen,
    Fehlschlag → Rollback), Prioritäts-/Wasserstandsregel exakt nach Freeze
    inkl. `not replayed`, kein Memory-Ringbuffer, Überlast sichtbar (genau ein
    Record `logging.records_dropped` mit korrekten Zählern nach der Erholung).
    `git diff --check` leer; geänderte Bestandsdateien ausschließlich `app.py`,
    `core/config.py`, `core/observability/__init__.py`,
    `core/observability/health.py`; kein Cross-Workstream-Diff; kein
    bestehender Test geändert; `-k obs030` 82/82 grün im eigenen Lauf.

    **Drei blockierende Befunde:**
    (B-1) `LoggingWorker.run()` klammert `self._iteration()` nicht in
    `try/except`. Eigene Probe: eine Ausnahme in der Schleife beendet den
    Worker still, `LoggingHealthState.FAILED_WORKER` und
    `record_worker_error` haben null Produktionsaufrufer, Health meldet
    weiterhin `OK`, `Ingress.is_failed()` bleibt `False`, `submit()` liefert
    weiter `True`, Records stranden in der Queue — und Pythons
    `threading`-Excepthook schreibt einen vollständigen, unratenbegrenzten
    Traceback nach stderr, entgegen `ARCH §8.1 G-2/G-4` und `§8.4`. Verstoß
    gegen `ARCH §8.3` („Worker-Ausnahme in der Schleife") und gegen das
    Gate-Kriterium „interne Worker-/DB-Fehler bleiben isoliert". Zusätzlich
    liegt `dataclasses.replace(...)` in `_prepare_record` außerhalb des
    eigenen `try`.
    (B-2) `CONTRACT_COVERAGE.md` behauptet genau dieses Verhalten als
    umgesetzt und setzt die Health-Spalte auf „—" statt `FAILED_WORKER` —
    Verstoß gegen das Gate-Kriterium „Evidence-Konsistenz".
    (B-3) `LoggingObservabilityConfig.validate()` prüft `db_path` und
    `file_sink_dir` nur auf den Typ; der Manager übernimmt jeden absoluten
    Pfad ungeprüft. Nachweis: ein Pfad unter `C:\ProgramData\...` wird
    akzeptiert. `CONTRACTS §4.3 P-8` verlangt ausdrücklich „KEIN Pfad
    ausserhalb des Benutzerprofils akzeptiert"; OBS-030 ist das erste Paket,
    das diese Pfade tatsächlich auflöst und benutzt.

    Weitere, nicht allein gate-entscheidende Befunde: ein defekter Store legt
    den intakten JSONL-Sink mit still (`_write_sink` nur `if ok`, Probe: 0 von
    20 Zeilen); `logging.retention_pressure` entsteht nur als stderr-Zeile,
    nicht als Record (`§5.6`/`§12.4`); Records, die wegen ausgesetztem Store
    verworfen werden, sind nirgends gezählt; kein „leerer Testschreibvorgang"
    nach der 60-s-Pause; `LoggingHealthState.DISABLED` wird nie erzeugt;
    `clear_history()` blockiert den Aufrufer bis zu 5 s (für OBS-050
    vormerken). Vorbestehend und außerhalb des Diffs: neben dem bekannten
    `lefx.interfaces`-Fehlschlag ist
    `test_core_bridge.py::test_async_and_sync_commands_execute_in_worker_loop`
    intermittierend rot (Wartebedingung deckt die `local_feedback`-Zustellung
    nicht ab) — keine Regression dieses Pakets.

    Kein Commit erstellt (Gate FAIL).
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review **nicht** abgehakt)
  - Nächster Schritt: Korrekturlauf `RUN-OBS-030-02` (B-1, B-2, B-3 sowie
    Entscheidung zu W-1/W-2), danach erneutes unabhängiges OBS-030 Gate.
    OBS-040 darf nicht beginnen.

- 17.08.2026, OBS-030 Korrekturlauf, `Prompts/OBS-030_FIX_RUN.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Run: `RUN-OBS-030-02_2026-08-17`
  - Ergebnis / Gate: **OBS-030 CORRECTED – READY FOR RE-REVIEW**
    (kein Gate-PASS; der Gate-Punkt bleibt offen und wurde nicht abgehakt)
  - Beschreibung:
    Gezielter Korrekturlauf zu `OBS-030 GATE FAIL`. Grundlage waren die
    vollständig gelesenen Freeze-Dokumente, WP-OBS-030, der ursprüngliche
    Implementierungsauftrag, der tatsächliche Produktcode und das vollständige
    Gate-Review-Dokument einschließlich W-1 bis W-7 — nicht die
    Zusammenfassungen.

    **B-1 Worker-Fehlerisolation – behoben.** `LoggingWorker.run()` ist
    vollständig geklammert: `_open_store()`, der erste Retentionslauf und
    jeder `_iteration()`-Durchlauf liegen in eigenen `try/except
    Exception`-Blöcken (`BaseException` bewusst nicht, `ARCH §7.3`). Neues
    `_record_loop_failure` erhöht `worker_errors` über
    `LoggingInternalHealth.record_worker_error` und damit über den
    ratenbegrenzten, nicht propagierenden Notausgang (G-2/G-4); die Schleife
    läuft weiter. Erst nach fünf aufeinanderfolgenden Fehlern
    (`WORKER_FAILURE_THRESHOLD`) gibt sie endgültig auf — **kein
    Neustartversuch** (`ARCH §8.3`). Das neue `_finish()` setzt dann
    `FAILED_WORKER` **vor** dem Shutdown-Flush, sodass `Ingress.is_failed()`
    greift und kein Producer mehr ein `True` für einen strandenden Record
    bekommt; `submit()` verwirft **und zählt** (neuer Zähler
    `dropped_failed`, siehe DECISION REQUIRED); Queue-Reste werden als
    `dropped_shutdown` gezählt, notfalls über `qsize()`, wenn selbst `drain`
    defekt ist. `dataclasses.replace(...)` in `_prepare_record` liegt jetzt
    im `try`. Laufzeitprobe (Gegenstück zur Gate-Probe): Worker tot →
    `state = failed_worker`, `worker_errors = 6`, `submit()` → `[False×5]`,
    `dropped_failed = 5`, `dropped_shutdown = 1`, keine Traceback-Zeile auf
    stderr, nur `[observability] …`.

    **B-2 Evidence-Konsistenz – behoben.** Korrigierte
    `CONTRACT_COVERAGE.md` unter `RUN-02_2026-08-17`. Die RUN-01-Evidence und
    die Gate-FAIL-Historie wurden **nicht** gelöscht und **nicht**
    umgeschrieben; stattdessen tragen RUN-01-`CONTRACT_COVERAGE.md`,
    RUN-01-`TEST_RESULTS.md` und RUN-01-`RESULT.md` je einen angehängten,
    ausdrücklich gekennzeichneten Korrekturvermerk.

    **B-3 P-8 – behoben.** `LoggingObservabilityConfig.validate()` prüft
    `db_path` und `file_sink_dir` gegen den **aufgelösten** Pfad
    (`os.path.realpath` + `os.path.normcase`); `..`, absolute Pfade
    außerhalb, relative, laufwerksrelative und UNC-Pfade werden abgelehnt.
    Befund während der Ausführung: `app.py::main()` ruft **kein**
    `AppConfig.validate()`, weshalb `ObservabilityManager._resolve_profile_path()`
    die Prüfung zur Laufzeit wiederholt — ein abgelehnter Pfad wird nicht
    akzeptiert, benutzt wird der eingefrorene Standardort plus eine
    ratenbegrenzte stderr-Zeile. 23 Tests inkl. des im Gate genannten
    `C:\ProgramData\...`-Falls.

    **W-1 bis W-7 entschieden:** W-1 FIXED (Sink läuft unabhängig vom
    Store-Ergebnis; Reihenfolge Store→Sink nach `§11.1` unverändert),
    W-2 FIXED (`logging.retention_pressure` als kanonischer Record,
    `performance`/`WARNING`/`is_internal`, flankengesteuert, `§12.4`/`§5.6`/
    FD-D8), W-3 NOT A DEFECT (Zählersatz `ARCH §7.3` eingefroren, keine
    Normzeile verlangt ein Zählen; Lücke ausdrücklich benannt), W-4 FIXED
    (`SQLiteLogStore.probe_write()` als leerer Testschreibvorgang nach der
    60-s-Pause), W-5 FIXED (`DISABLED` bei `enabled=False`), W-6 DEFERRED
    nach OBS-050 (kein Qt-Aufrufer in OBS-030; Auflage O-03 notiert),
    W-7 FIXED (PRAGMA-Reihenfolge nach `§5.2`, Retentionstakt nach
    *geschriebenen* Records, `stop()` ohne Start zählt Queue-Reste).

    **DECISION REQUIRED `DR-OBS-030-01`:** Der Zähler `dropped_failed`
    erweitert `ARCH §7.3` und `CONTRACTS §11.2` additiv (letztes
    Snapshot-Feld mit Default). Grund: `ARCH §8.3` verlangt „verwerfen **und
    zählen**", der eingefrorene Zählersatz kennt dafür keinen Zähler, und
    eine Abbildung auf `dropped_watermark`/`dropped_queue_full` hätte den
    Record `logging.records_dropped` verfälscht. Offen ausgewiesen und in
    `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (neuer Abschnitt 11)
    nachgetragen — keine stille Planänderung.

    **Tests:** 47 neue Tests in drei Dateien
    (`test_obs030_worker_fault_injection.py` 6,
    `test_obs030_path_boundaries.py` 23, `test_obs030_gate_corrections.py`
    18). `-k obs030`: 129/129 grün unter `pytest` **und** `unittest`.
    `-k "obs010 or obs020 or obs030"`: 331 grün. Volle Client-Suite:
    843 passed / 1 Fehlschlag (`pytest`), `unittest discover` 844 Ran /
    1 error. `git diff --check` leer. Der eine Fehlschlag ist der
    vorbestehende, umgebungsbedingte `lefx.interfaces`-Fehler
    (`core/led_controller.py` außerhalb des Diffs, erneut verifiziert). Der
    vom Gate benannte intermittierende
    `test_core_bridge`-Befund trat nicht auf (fünf isolierte Läufe grün),
    bleibt vorbestehend und wurde bewusst nicht repariert.

    **Scope:** Geändert wurden `core/observability/{worker,storage/sqlite,
    manager,health,ingress}.py` und `core/config.py`.
    `core/observability/ingress.py` ist die einzige Datei außerhalb des
    RUN-01-Diffs; zwingender Grund ist dieselbe Zeile `ARCH §8.3`, die B-1
    einfordert („verwerfen **und zählen**"). Genau ein Test aus RUN-01 wurde
    geändert (`test_obs030_config.py`: das Pfadliteral `C:/tmp/obs-sink`
    widersprach P-8 direkt); kein Test außerhalb von `tests/test_obs030_*.py`
    wurde angefasst. Kein OBS-040, kein OBS-050, kein Refactoring ohne
    Gate-Bezug, kein Cross-Workstream-Diff.

    **Ablage-Auffälligkeit:** `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` war
    im Arbeitsbaum gelöscht, während im nicht versionierten
    `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` eine leere Zweitfassung
    liegt. Der kanonische Pfad wurde mit dem bisherigen Inhalt als Textdatei
    wiederhergestellt und fortgeschrieben (kein `git reset`, kein
    `git clean`); die Zweitfassung blieb unangetastet. Ein bewusster Umzug
    ist offen.

    Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (Abschnitt 11, `DR-OBS-030-01`, offen)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review weiterhin **nicht** abgehakt)
  - Nächster Schritt: erneutes unabhängiges OBS-030 Gate Review in frischer
    Session. OBS-040 darf nicht beginnen.

- 17.08.2026, OBS-030 Cleanup des Korrekturlaufs, `Prompts/OBS-030_FIX_RUN_II.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Run: `RUN-OBS-030-02_2026-08-17` (derselbe Run, nachgelagerter Cleanup)
  - Ergebnis / Gate: **OBS-030 CLEANUP COMPLETED – READY FOR INDEPENDENT
    RE-REVIEW** (kein Gate-PASS; der Gate-Punkt bleibt offen und ist nicht
    abgehakt)
  - Beschreibung:
    Eng begrenzte Rücknahme zweier Änderungen des Korrekturlaufs, die ich in
    der Stellungnahme zu den drei Prüfproblemen selbst als nicht eindeutig
    autorisiert bzw. als echte Contract-Erweiterung eingeordnet hatte. **Kein
    neuer Implementierungslauf, keine neue Architekturarbeit.**

    **Vorab nachgeholte Pflichtlektüre.** Der Korrekturlauf hatte
    `ARBEITSDATEIEN/README.md`, `ARBEITSDATEIEN/AGENTS.md`,
    `00_STEUERUNG/MASTERPLAN.md`, `00_STEUERUNG/ARBEITSPROZESS.md` und
    `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md` ausgelassen; sie sind vor
    diesem Cleanup vollständig gelesen worden (`START_HIER.md` existiert
    nicht; an seiner Stelle das Themen-`README.md`). Zwei Stellen sind
    unmittelbar einschlägig: die Scope-Regel des Themen-`AGENTS.md` („Neue
    Funde nicht automatisch reparieren. Fund → dokumentieren → Blocker?")
    und die Autoritätshierarchie mit `00_NORMATIV/` an der Spitze, zusammen
    mit `LOGGING_DECISIONS_FREEZE_V1.md §10`, dessen `DECISION
    REQUIRED`-Verfahren mit **`anhalten`** beginnt.

    **Korrektur 1 – `dropped_failed` vollständig zurückgenommen.** Entfernt
    aus `LoggingHealthSnapshot` (Feld), `LoggingInternalHealth`
    (Initialisierung, `record_dropped_failed()`, `snapshot()`-Argument) und
    aus `ObservabilityIngress.submit()`. `core/observability/ingress.py` ist
    damit wieder byte-identisch zu `HEAD` und aus dem Diff heraus;
    `core/observability/health.py` steht wieder auf dem vom Gate-Review
    festgehaltenen RUN-01-Stand `+21/-2`. Im Fault-Injection-Test wurde die
    Assertion auf `dropped_failed` durch die Prüfung ersetzt, dass
    abgewiesene Records den Queue-Füllstand nicht verändern; das Probeskript
    und die betroffenen Evidence-Aussagen sind entsprechend angepasst.
    **Kein Ersatzzähler**, und **keine** Abbildung auf `dropped_watermark`,
    `dropped_queue_full` oder `dropped_shutdown`.

    **Korrektur 2 – `DR-OBS-030-01` aus der Freeze-Datei entfernt.** Der vom
    Korrekturlauf angehängte Abschnitt 11 in
    `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` wurde vollständig entfernt;
    die Datei ist byte-identisch zum Stand vor `RUN-OBS-030-02`
    (`git diff`/`git status` für `00_NORMATIV/` leer). Umgesetzt als reine
    Textkürzung — kein `git reset`, kein `git checkout`, kein `git clean`,
    keine History-Aktion. Bestehende Entscheidungen der Abschnitte 1–10
    unverändert. **Damit verändert dieser Run kein normatives Dokument.**

    **Der Entscheidungsbedarf bleibt bestehen und wird nicht entschieden.**
    `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md` ist neu
    gefasst als offene Entscheidung mit Ausgangsproblem, der maßgeblichen
    Formulierung aus `ARCH §8.3` („nur verwerfen und zählen"), dem Konflikt
    mit dem eingefrorenen Zählersatz `ARCH §7.3` / `CONTRACTS §11.2`, beiden
    auslegbaren Lesarten, dem ausdrücklichen Hinweis, dass `dropped_failed`
    **nicht** Bestandteil des finalen Implementierungsstands ist, und dem
    Status „Entscheidung durch unabhängige Prüf-/Entscheidungsinstanz
    ausstehend".

    **B-1 bleibt vollständig bestehen.** Laufzeitprobe nach dem Cleanup:
    Worker tot → `state = failed_worker`, `worker_errors = 6`,
    `is_failed() = True`, `submit()` → `[False×5]`, Queue-Füllstand durch die
    abgewiesenen Submits unverändert, bereits eingereihter Record als
    `dropped_shutdown = 1` gezählt, keine Traceback-Zeile auf stderr (nur
    `[observability] …`), kein Observability-Thread übrig. Ebenso unverändert:
    B-3/P-8, W-1 (Sink-Unabhängigkeit), W-2
    (`logging.retention_pressure`), W-4 (`probe_write`), W-5 (`DISABLED`),
    W-7a/b/c.

    **Tests nach dem Cleanup:** Fault-Injection 6/6, `-k obs030` 129/129
    (`pytest` **und** `unittest`), `obs010+020+030` 331, volle Client-Suite
    843 passed / 1 vorbestehender `lefx.interfaces`-Fehlschlag außerhalb des
    Diffs, `unittest discover` 844 Ran / 1 error, `test_core_bridge` 3×
    grün, `git diff --check` leer. Die Testanzahl ist unverändert — es wurde
    kein Test entfernt, nur eine Assertion ersetzt.

    **Nicht angefasst:** die nachträglichen Korrekturvermerke in der
    RUN-01-Evidence (laut Cleanup-Auftrag ausdrücklich Gegenstand des
    unabhängigen Gate-Reviews), die historische Gate-FAIL-Evidence, die
    fachlichen B-1-/B-3-/W-Korrekturen und der bestehende RUN-02-Eintrag
    dieses Verlaufs (append-only).

    Zusätzlich aus der nachgeholten Pflichtlektüre umgesetzt: `RUN_REPORT.md`
    des Runs folgt jetzt der in `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`
    vorgeschriebenen Gliederung (Run-ID … Gate-Empfehlung, nächster Schritt);
    der fachliche Inhalt ist derselbe.

    Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/RUN_LOG.md` (Abschnitt 8: Cleanup)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md` (offene Entscheidung)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (**unverändert**, Nachtrag entfernt)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review weiterhin **nicht** abgehakt)
  - Nächster Schritt: erneutes unabhängiges OBS-030 Gate Review in frischer
    Session; dort auch über die offene Auslegungsfrage zu `ARCH §8.3`
    entscheiden. OBS-040 darf nicht beginnen.

- 17.08.2026, OBS-030 Gate Review II, `Prompts/OBS-030_GATE_REVIEW_II.md`
  - Workstream: OBS (Logging / Observability), Work Package: OBS-030 – Worker,
    SQLite-Store, Retention & JSONL-Sink
  - Ergebnis / Gate: **OBS-030 GATE PASS – OBS-040 MAY PROCEED**
  - Beschreibung:
    Zweiter unabhängiger Review in frischer Session über den gesamten
    OBS-030-Endstand seit dem letzten freigegebenen Commit `b363346` — also
    RUN-01, Gate-FAIL, Korrekturlauf `RUN-OBS-030-02` und Cleanup zusammen,
    nicht nur den letzten Diff. Geprüft wurde ausschließlich der tatsächliche
    Repositoryzustand: Code, `git diff`/`git status`, eigene Testläufe mit
    beiden Runnern, eigene Fault-Injection- und Laufzeitproben sowie ein
    Vergleichslauf gegen einen aus `b363346` frisch ausgepackten Baum. Die
    Abschluss-, Korrektur- und Cleanup-Berichte dienten als Hinweis, nicht
    als Nachweis.

    **B-1 geschlossen.** Eigene Fault-Injection: eine injizierte Ausnahme im
    Schleifenrumpf → Worker lebt, `worker_errors = 1`, Schleife verarbeitet
    weiter; vier aufeinanderfolgende Fehler mit anschließendem Erfolg →
    weiterhin `ok`; dauerhaft werfende Schleife → `failed_worker`,
    `worker_errors = 6`, `submit()` liefert `[False×5]`, Queue-Reste als
    `dropped_shutdown = 5` gezählt, `store.close()`/`sink.close()` gelaufen,
    kein Observability-Thread übrig und **kein** `Traceback` auf stderr,
    ausschließlich `[observability] …`-Zeilen. Ebenfalls geprüft:
    `_prepare_record`-Austrittspfad, `qsize`-, `run_retention`- und
    `store.open()`-Ausnahmen, `stop()` auf nie gestartetem Worker (7 von 7
    Records gezählt).

    **Schwelle `WORKER_FAILURE_THRESHOLD = 5` ausdrücklich geprüft und als
    normativ gedeckt begründet** — nicht wegen vorhandener Tests: `ARCH §8.3`
    regelt nur, *was* bei einem Schleifenabbruch geschieht, nicht *wann*;
    dieselbe Zeile liefert die Prämisse („ein Worker, der zweimal stirbt,
    stirbt beim dritten Mal auch"); die beobachtbare Semantik bleibt exakt
    die eingefrorene (`FAILED_WORKER`, kein Neustart, `FAILED`-Zweig aus
    `ARCH §5`); es entsteht kein Zähler, kein Zustand, kein Konfigfeld und
    keine DDL-Änderung.

    **B-2 geschlossen.** Alle prüfbaren Zahlen der RUN-02-Evidence wurden
    eigenständig reproduziert. Die Gate-FAIL-Evidence ist vollständig
    unverändert; kein Befund gelöscht oder verschleiert.

    **B-3 geschlossen.** P-8 gegen den real aufgelösten Profilpfad
    (`C:\Users\marco`) geprüft, für `db_path` **und** `file_sink_dir`, an der
    Config-Grenze **und** im produktiven Managerpfad: gültiger Profilpfad,
    absoluter Fremdpfad, `..`-Escape, Fremdprofil (inkl. Präfixfalle),
    Windows-Laufwerkspfad, UNC, laufwerksrelativ, relativ, leer sowie
    Separator-/Groß-Klein-/Doppelseparator-Normalisierung. Feindliche
    Konfiguration landet im eingefrorenen Standardort; `C:\ProgramData\…`
    wird nicht angelegt. P-9 belegt (`-wal`/`-shm` im selben Verzeichnis).

    **W-1 bis W-7 unabhängig nachgeprüft.** W-1: die Entkopplung von Sink und
    Store ist vertragstreu (`CONTRACTS §11.1` fixiert eine Reihenfolge, keine
    Bedingung; `O-05`); gemessen 20/20 Sinkzeilen bei degradiertem Store,
    Reihenfolge `['store', 'sink']`; die Abweisung bei `FAILED_STORE` ist
    durch das eingefrorene Komponentenbild `ARCH §5` gedeckt. W-2:
    `logging.retention_pressure` Feld für Feld aus der SQLite gelesen
    (Channel `performance`, Level `WARNING`, `observability.worker`,
    `is_internal`, flankengesteuert — bei 2600 Records genau ein Record).
    W-3: Lücke bestätigt und benannt, **kein** neuer Zähler verlangt.
    W-4: `probe_write()` kostet beim Resume 0 `write_batch`-Aufrufe.
    W-5: `disabled` bei `enabled=False`, `ok` bei `store_enabled=False`.
    W-6: zu Recht OBS-050. W-7a/b/c nachgemessen.

    **Entscheidung zu `ARCH §8.3` „nur verwerfen und zählen": Variante 1.**
    Die Frage ist aus dem bestehenden Freeze lösbar; ein neuer Zähler ist
    nicht erforderlich. Tragende Normstellen: `ARCH §5` friert die
    Ingressreihenfolge wörtlich ein und markiert das Zählen ausschließlich am
    Queue-voll-Schritt, während der `FAILED`-Zweig ein reines `return False`
    ist; `§8.3` definiert nirgends Zähler, sondern nennt sie beim Namen, wo
    es sie meint (`worker_errors++` in derselben Zeile, `dropped_shutdown`,
    `malformed++`) und kann daher gegen die als „eingefroren" überschriebene
    Liste in `§7.3` keinen neuen erzeugen; `§8.5 GRENZE 3` benennt den
    Totalverlust nach einem Workerausfall ausdrücklich als
    Architektureigenschaft und „keinen Mangel" und verweist auf den
    RotatingFileHandler als Rückfallebene. Was `§8.3` an Zählung nennt,
    geschieht nachweislich. **Kein Contract-Widerspruch, kein
    DECISION-REQUIRED-Bedarf für die Abnahme; der Reviewer hat keinen Zähler
    implementiert und keine Freeze-Datei angefasst.** Eine spätere
    autorisierte Entscheidung zugunsten der Gegenlesart bliebe möglich und
    gehört sinnvoll mit W-3 zu OBS-060.

    **Freeze-Integrität:** `git diff --stat HEAD -- 00_NORMATIV/` ist leer;
    alle vier Dateien sind byte-identisch zu `b363346`. `DR-OBS-030-01` kommt
    in `00_NORMATIV/` nirgends vor. `LoggingHealthSnapshot` hat wieder exakt
    die 16 Felder aus `CONTRACTS §11.2`, `LoggingObservabilityConfig` exakt
    die 14 Schlüssel aus `§10.1`, die DDL exakt `§5.2`; `ingress.py` ist
    unverändert gegenüber `HEAD`; kein `dropped_failed` im Repository.

    **Historische RUN-01-Evidence:** transparente, datierte und abgesetzte
    Korrekturvermerke; die beanstandeten Originalaussagen stehen wörtlich
    weiterhin da. Kein materielles Evidence-Problem.

    **Teststand:** `-k obs030` 129 passed (`pytest`) und `Ran 129, OK`
    (`unittest`), `obs010+020+030` 331 passed, volle Suite 843 passed /
    1 failed, `unittest discover` 844 Ran / 1 error, `git diff --check` leer.
    Der eine Fehlschlag wurde **gemessen** als vorbestehend nachgewiesen: im
    frisch aus `b363346` ausgepackten Baum 714 passed / derselbe eine
    `lefx.interfaces`-Fehlschlag; die Differenz 843 − 714 = 129 entspricht
    exakt den neuen OBS-030-Tests. Die früher beobachtete Flakiness in
    `test_core_bridge.py` trat in sechs isolierten Läufen und in keinem
    Volllauf auf.

    Nicht-blockierende Beobachtungen N-1 bis N-5 sind im Gate-Review
    dokumentiert (u. a. N-1: `logging.record_rejected` aus `ARCH §8.3` /
    `CONTRACTS §12.4` existiert nirgends im Code — Auslöser liegt im
    OBS-010/020-Normalizerpfad, nicht im OBS-030-Scope; für OBS-040/060).

    Genau ein lokaler Commit für den geprüften OBS-030-Endstand.
    Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/GATE_REVIEW.md`
    - dieselbe Ablage: `probe_gate2_b1_worker.py`, `probe_gate2_w_findings.py`, `probe_gate2_b3_paths.py`, `probe_gate2_e2e.py`, `probe_gate2_sink.py`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-030 Gate Review jetzt abgehakt)
  - Nächster Schritt: OBS-040 – Server Live Adapter & Client Observation
    Hooks (Implementierung, frische Session). Readiness geprüft: keine
    Blocker. **OBS-040 MAY PROCEED.**

- 17.08.2026, OBS-040 Implementierung (`RUN-OBS-040-01_2026-08-17`),
  `Prompts/OBS-040_IMPLEMENTIERUNGSAUFTRAG.md`
  - Beschreibung:
    OBS-040 – Server Live Adapter & Client Observation Hooks implementiert.
    Voraussetzung geprüft: OBS-030 steht mit `GATE PASS – OBS-040 MAY
    PROCEED` in `CURRENT_STATE.md` und in der Checkliste.

    **Zwei neue Module**, beide in `ARCH §5.1` eingefroren vorgesehen:
    `core/observability/adapters/server_live.py` (`ServerLiveAdapter` – der
    passive Konsument des Fan-outs; fängt selbst nach `ARCH §7.3` Ebene 1,
    meldet an `LoggingInternalHealth`, fängt nie `BaseException`) und
    `core/observability/adapters/client_events.py` (`ClientEventEmitter` –
    die eine nie werfende Grenze, durch die jede Client-Hook-Aufrufstelle
    geht).

    **Fan-out-Hook** in `core/session_coordinator.py` nach `CONTRACTS §7.1`:
    `on_observation`, `_notify_observer` mit bewusst leerem
    `except Exception`, je **erste Anweisung** in `_handle_event` und
    `_handle_control`. Der Feedbackzweig läuft unverändert über `on_event`
    weiter – ein echtes Fan-out (O-02), kein Durchleiten.

    **Zweiter Beobachtungspunkt** (FD-R3, `CONTRACTS §7.5`): eine Zeile im
    `except`-Zweig von `EventStreamTransport.run()` →
    `client.eventstream.protocol_error`, ohne Rohframe.

    **42 Recordtypen aus `CONTRACTS §12`** über `ui/hotkeys.py`,
    `ui/core_bridge.py`, `ui/application.py`, `ui/led_feedback.py`,
    `ui/settings_dialog.py`, `core/audio_capture.py`, `core/stt_session.py`,
    `core/controller.py`, `core/text_injector.py`,
    `core/session_coordinator.py`, `core/event_stream.py` – umgesetzt in der
    von `§12.6` vorgeschriebenen Reihenfolge nach aufsteigendem Risiko, mit
    einem Testlauf nach jeder Stufe. Korrelationsketten: Trigger send/ack
    über `command_id` + `trigger:<cmd>`, Kommandos über `command:<cmd>`,
    Settings-Apply über `settings:<id>` von `apply_started` über
    `runtime_apply` bis `apply_completed`, Injection über
    `injection:<entryId>`.

    **Gate-Befund N-1 geschlossen:** `logging.record_rejected` existiert
    jetzt (`ingress.emit_record_rejected`), erzeugt an allen vier Stellen,
    die eine Normalizer-Ausnahme sehen können, mit Komponente und
    Ausnahmetyp und **ohne** Originaldaten; Health bleibt `OK`,
    `malformed++` – exakt die Zeile „Normalizer-Ausnahme" aus `ARCH §8.3`.

    **Hot Path und Aggregat nach `ARCH §8.6`:** die neun genannten
    Funktionen erhöhen ausschließlich `int`-Attribute (Quelltextnachweis über
    alle neun); der **Worker** liest sie über eine read-only-Registry am
    Ingress und erzeugt `client.audio.stream_stats`, Channel `performance`,
    Level `DEBUG`, höchstens alle 5 s und nur während aktiven Streamings. Die
    Registry ist der einzige Weg, der `§8.6` („der Worker liest die Zähler")
    und `§5.2` (Importrichtung) gleichzeitig hält.

    **Der wichtigste Nachweis (N-07) erbracht:** ein werfender Beobachter
    verändert weder den Rückgabewert von `_handle_event` noch den Cursorstand
    – gemessen mit dem **echten** `EventProtocolProcessor` und dem **echten**
    `EventCursorStore` auf einer temporären Datei, kein Double. Die vom Work
    Package verlangten Suiten `test_session_coordinator.py`,
    `test_event_stream.py`, `test_feedback_integration.py` und
    `test_trigger_feedback_contract.py` laufen unverändert grün.

    **Fünf reale Befunde während der Ausführung** (Details in `RUN_LOG.md`
    Abschnitt 5): der bestehende OBS-020-Hot-Path-Test hat einen Kommentar
    abgelehnt, der das Wort `ingress` enthielt (Kommentar umformuliert, nicht
    der Test); `run_headless`, `CoreBridge.apply_runtime_config` und die
    Transport-Factory des Coordinators sind durch bestehende Test-Doubles auf
    ihre alten Signaturen fixiert, weshalb der Ingress dort über
    Signaturinspektion bzw. die von `CONTRACTS §6` blessierte Default-Factory
    reist – bewusst **nicht** über `try/except TypeError`, das einen Aufruf
    doppelt ausgeführt hätte; `logging.record_rejected` ist nur defensiv
    erreichbar, weil der Normalizer konstruktiv nie wirft;
    `envelope["meldung"]` liegt auf der Envelope-Oberfläche, nicht in einem
    verschachtelten `extra`.

    **Neun Entscheidungen, alle aus dem bestehenden Freeze auflösbar, kein
    `DECISION REQUIRED`, keine Erweiterung eines eingefrorenen Vertrags.**
    Insbesondere **kein neuer Zähler** in `LoggingHealthSnapshot` – der
    Zählersatz aus `ARCH §7.3` ist unverändert und jetzt durch einen
    Contract-Test fixiert (die Lektion aus dem OBS-030-Cleanup zum
    zurückgenommenen `dropped_failed`). **Kein normatives Dokument ist durch
    diesen Run verändert**; `00_NORMATIV/` erscheint nicht in
    `git status --short`.

    **Teststand:** 115 neue Tests in sechs Dateien; `-k obs040` 115 passed
    (`pytest`) und `Ran 115, OK` (`unittest`); `obs010+020+030+040` 446
    passed; volle Suite 958 passed / 1 vorbestehender, umgebungsbedingter
    Fehlschlag (`test_ap06_followup.py`, `lefx.interfaces` fehlt lokal,
    außerhalb des Diffs), `unittest discover` Ran 959 / 1 error. Differenz
    zur Baseline (843) exakt die 115 neuen Tests. **Kein bestehender Test
    geändert.** `git diff --check` leer, `git diff --stat` 16 Dateien
    +1324/−57, kein Cross-Workstream-Diff. Ende-zu-Ende-Diagnoseskript mit
    echtem Manager, echtem SQLite-Store, echtem Protokollprozessor und
    echtem Cursorstore: P-1 bis P-7 alle PASS, exit 0 – darunter der Nachweis,
    dass 1000 Audiopakete **keine** Zeile erzeugen, das Worker-Aggregat aber
    schon, und dass in **keiner** gespeicherten Zeile das Session-Log-Token
    auftaucht, obwohl der `log.hello`-Payload es nachweislich enthielt.

    **Kein Gate-PASS in diesem Run** – laut Work Package erfordert das Gate
    einen separaten Review in frischer Session. Kein Commit, kein Push, kein
    Merge, kein Rebase, kein Tag, kein PR.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-040-01_2026-08-17/` (`RUN_LOG.md`, `RESULT.md`, `OUTPUT_INDEX.md`)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-040/RUN-01_2026-08-17/` (`TEST_RESULTS.md`, `DIFF_SUMMARY.md`, `CONTRACT_COVERAGE.md`, `OBSERVATION_HOOK_MATRIX.md`, `SERVER_EVENT_MAPPING.md`, `probe_obs040_end_to_end.py`)
    - `core/observability/adapters/server_live.py`, `core/observability/adapters/client_events.py`
    - `tests/test_obs040_server_live_adapter.py`, `tests/test_obs040_fanout_hook.py`, `tests/test_obs040_client_hooks.py`, `tests/test_obs040_hot_path.py`, `tests/test_obs040_failure_isolation.py`, `tests/test_obs040_contracts.py`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (OBS-040 Implementierung jetzt abgehakt)
  - Nächster Schritt: OBS-040 Gate Review in frischer Session,
    `Prompts/OBS-040_GATE_REVIEW.md`. Offen für spätere Pakete:
    `apply_config` und die Manager-Übergabe an `DesktopApplication` (OBS-050,
    Befund N-4), N-2/N-3/W-3 und der Lauf gegen den echten Server (OBS-060).

- 17.08.2026, OBS-040 Gate Review (unabhängig, frische Session),
  `Prompts/OBS-040_GATE_REVIEW.md`
  - Ergebnis: **`OBS-040 GATE PASS – OBS-050 MAY PROCEED`**.
  - Beschreibung:
    Geprüft wurde ausschließlich der tatsächliche Repositoryzustand über dem
    Commit `cb0b81f`: Produktcode, `git diff`/`git status`, eigene Testläufe
    mit **beiden** Runnern, ein Vergleichslauf gegen einen frisch aus
    `cb0b81f` ausgepackten Baum (`git archive`) und zwei **eigene**
    Laufzeitproben. Die Abschlussberichte des Implementierungslaufs wurden als
    Hinweis gelesen und an keiner Stelle als Nachweis übernommen. Auflage
    dieses Laufs: keine Produktänderung, kein Commit, kein Push.

    **N-07 eine Ebene tiefer nachgemessen.** Der Implementierungslauf belegt
    ihn an `DualSessionCoordinator._handle_event`; dieser Review fährt den
    echten `EventStreamTransport._dispatch`, also die Stelle, die
    `confirm_event`/`reject_event` besitzt und deren `except BaseException`
    ein Event bei durchschlagender Ausnahme aktiv verwerfen würde. Aufbau ohne
    jedes Double (echter Prozessor, echter `EventCursorStore` auf temporärer
    Datei, echter Transport, echter Coordinator): ein werfender Beobachter
    wird genau einmal gerufen, das Ergebnis wird bestätigt, der Resume-Cursor
    steht identisch zum Lauf ohne Beobachter (5/5), keine Ausnahme verlässt
    den Dispatch, und der Feedbackzweig läuft unverändert. `asyncio.Cancelled
    Error` kommt durch — `Exception` wird gefangen, `BaseException` nirgends.

    **Eigenständig belegt, nicht nachgelesen:** unabhängiges Fan-out (der
    Beobachter sieht auch das vom Runtimepfad wegen Bindings-Mismatch
    verworfene Event, das Duplikat und die Controlframes, der Feedbackzweig in
    diesen drei Fällen nichts); Serverabbildung Feld für Feld nach
    `CONTRACTS §3.2` inkl. `component` aus dem Namensraumpräfix, `message` aus
    `extra["meldung"]`, `segment_id` als `int` und `generation` aus dem
    `SessionContext`; `raw` als Identitätsreferenz statt Kopie (`ARCH §8.2`);
    Replayidentität und Dedupe im echten `SQLiteLogStore` („die erste,
    live empfangene Fassung gewinnt", `deduplicated` steigt); **kein**
    Session-Log-Token in irgendeiner gespeicherten Zeile, obwohl der
    `log.hello`-Payload nachweislich zwei trägt, und `hello` nie `raw` (R-6);
    1000 Hot-Path-Inkremente → 0 Records bei genau einem Worker-Aggregat
    (`performance`/`DEBUG`); ein Ingress, dessen sämtliche Methoden werfen,
    stört den echten Dispatch nicht (O-05). Kein Beobachtungsthread bleibt
    übrig.

    Die sechs benannten Auslegungen A-1 bis A-6 und die drei
    Signaturinspektionen tragen; `inspect.signature` statt
    `try/except TypeError` ist die richtige Wahl, weil ein `TypeError` aus dem
    Inneren des Aufrufs einen Clientlauf bzw. ein Apply doppelt ausgeführt
    hätte. Der `session_coordinator.py`-Diff ändert zwei weitere bestehende
    Zeilen (Default-Transport-Factory) — offen benannt, durch `CONTRACTS §6`
    gedeckt und die kleinstmögliche Abweichung, weil sonst ein bestehender
    Test hätte geändert werden müssen (`ARCH §12`). Alle 57 Löschungen des
    Diffs einzeln durchgesehen: jede erscheint in geänderter Form wieder, kein
    Verhalten entfernt. Kein OBS-050/OBS-100+-Vorgriff, kein neues Konfigfeld,
    `00_NORMATIV/` byte-identisch zu `cb0b81f`, `git diff --check` leer, kein
    Cross-Workstream-Diff, kein bestehender Test geändert.

    **Teststand (eigene Läufe):** volle Suite 958 passed / 1 vorbestehender,
    umgebungsbedingter Fehlschlag (`test_ap06_followup.py`,
    `lefx.interfaces`); Vorbestand gegen den sauberen `cb0b81f`-Baum
    nachgewiesen (dort 843 passed / 1 identischer Fehlschlag), Differenz exakt
    die 115 neuen Tests. `-k obs040` 115/115 grün unter `pytest` (178
    Subtests) **und** `unittest`. Ende-zu-Ende-Probe des Runs unabhängig
    erneut ausgeführt: P-1 bis P-7 PASS, exit 0. Eigene Proben: 21 Prüfungen,
    alle PASS.

    **Befund F-1 (nicht die Implementierung betreffend).**
    `LOGGING_V1_CHECKLISTE.md` enthielt im Arbeitsbaum bereits **vor** diesem
    Review den Haken `- [x] OBS-040 – Gate Review` und einen
    Gate-PASS-Absatz, der mit „Ein lokaler Commit für den geprüften
    OBS-040-Endstand wurde erstellt" endet. `git log` widerlegt das: HEAD ist
    `cb0b81f` (OBS-030), ein OBS-040-Commit existiert nicht. Ebenso fehlten
    Gate-Evidence unter `40_EVIDENCE/OBS-040/`, ein Eintrag hier und ein
    Eintrag in `CURRENT_STATE.md`, das den Gate Review weiterhin als nächsten
    Schritt nannte. Der Eintrag stammt nicht aus `RUN-OBS-040-01`, dessen
    Berichte an fünf Stellen ausdrücklich „Kein Gate-PASS in diesem Run"
    sagen. Der Absatz ist durch das tatsächliche Ergebnis dieses Reviews
    ersetzt worden, ohne die falsche Commit-Behauptung und mit Hinweis auf den
    vorgefundenen Zustand; frühere Häkchen sind unverändert.

    **Sieben nicht-blockierende Beobachtungen N-1 bis N-7** im Gate-Review
    dokumentiert, darunter N-1 (`_enqueue_audio_packet` liest auf dem Hot Path
    zusätzlich `qsize()`, um das von `ARCH §8.6` selbst geforderte
    `max_send_queue_depth` führen zu können — unvermeidbar, aber nicht unter
    A-1…A-6 benannt) und N-2 (`RESULT.md` nennt 175 statt 178 Subtests).

    **Kein Commit erstellt.** Der Gate-Prompt sieht bei PASS genau einen
    lokalen Commit vor; für diesen Lauf war „keine Produktänderungen und kein
    Commit/Push" ausdrücklich angeordnet. Der Commit für den geprüften
    OBS-040-Endstand ist damit offen und bleibt einer ausdrücklichen Freigabe
    vorbehalten. Am Produktcode wurde nichts geändert.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-040/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
    - `.../GATE-REVIEW-01_2026-08-17_CLAUDE/gate_probe_obs040_independent.py` (14 Prüfungen)
    - `.../GATE-REVIEW-01_2026-08-17_CLAUDE/gate_probe_obs040_server_mapping.py` (7 Prüfungen)
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` (Gate-Absatz korrigiert, Befund F-1)
    - `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`
  - Nächster Schritt: **OBS-050 – Local Query, Log View & Settings**
    (Implementierung, frische Session,
    `Prompts/OBS-050_IMPLEMENTIERUNGSAUFTRAG.md`). Readiness geprüft: keine
    Blocker; offen und OBS-050-Scope sind `query/local.py`,
    `query/service.py`, `ui/logs/**`, die Settings-Einträge nach
    `CONTRACTS §10.3`, `apply_config` nach `§10.4` und die Übergabe des
    Managers an `DesktopApplication` (N-4).

- 17.08.2026, OBS-040 Abschlussvermerk (lokaler Gate-Checkpoint-Commit)
  - Nach ausdruecklicher Freigabe wurde genau ein lokaler Checkpoint-Commit
    fuer den gate-geprueften OBS-040-Endstand auf
    `feat/einheitliche-triggerarchitektur` erstellt: Produktstand, die 115
    OBS-040-Tests, die RUN- und Evidence-Unterlagen sowie das Gate-Review samt
    Probeskripten. Die bewusst unversionierten Prompt- und Pipeline-Dateien
    unter `30_AUSFUEHRUNG/` blieben unversioniert.
  - **OBS-040 ist damit vollstaendig abgeschlossen** — Implementierung,
    unabhaengiger Gate Review (`GATE PASS`) und lokaler Checkpoint.
  - **OBS-050 ist freigegeben** (`OBS-050 MAY PROCEED`); die Implementierung
    beginnt in einer frischen Session.
  - **Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**

- 17.08.2026, OBS-050 Implementierung (Run `RUN-OBS-050-01_2026-08-17`)
  - Ergebnis: **`OBS-050 IMPLEMENTED – READY FOR REVIEW`**. Kein Gate-PASS in
    diesem Run — das Work Package verlangt einen separaten, unabhaengigen
    Review in frischer Session.
  - **Query-Layer.** `core/observability/query/local.py`
    (`LocalLogProvider`) und `core/observability/query/service.py`
    (`LogQueryService`) schliessen die letzte Luecke der in `ARCH §5.1`
    eingefrorenen Modulstruktur. Eigene kurzlebige Leseverbindungen mit
    `PRAGMA query_only = ON` (nie `mode=ro`, W-13), Keyset-Pagination ueber
    `logs.id` nach `CONTRACTS §5.7`, `raw_json` grundsaetzlich nicht in der
    Listenabfrage, jeder Filterwert als Platzhalter. Drei getestete
    Eigenschaften tragen O-14: der Leser **legt die Datenbankdatei nie an**,
    er **wirft nie** (jeder Fehler ist ein Anzeigezustand) und er **laesst
    keine Verbindung offen**.
  - **Logansicht.** `ui/logs/**` mit den sechs eingefrorenen Modulen. Live und
    Historie sind **derselbe** Abfragepfad mit anderen Parametern: Historie
    `newest_first=True` mit `next_cursor`, Live alle 250 ms
    `newest_first=False` ab dem zuletzt gesehenen Cursor, `LIMIT 500`.
    **Kein Ringbuffer, kein Signal je Record** (FD-S1). Eigener
    `ThreadPoolExecutor(max_workers=1)`, ausdruecklich nicht ueber
    `CoreBridge`.
  - **Einstellungen.** Die neun Eintraege aus `CONTRACTS §10.3` im sechsten Tab
    „Logging & Diagnose", dazu „Diagnosehistorie loeschen" (am **Store**, ueber
    den Manager — nicht am Query-Provider, O-14) und „Logs anzeigen". Die
    Ownership-Domaenen sind getrennt: der Ingress wendet die vier Felder an,
    die er besitzt, die Kompositionswurzel den Handler-Level (`ARCH §8.7`: ein
    Konfigwert, zwei Filter), der Worker Retention, Anzahlgrenze und
    Datei-Sink auf **seinem eigenen** Thread. `store_enabled`/`db_path`
    bleiben `APP_RESTART` und werden zur Laufzeit nicht angewandt.
  - **Apply-Kette.** Eine Zeile in `core/controller.py::apply_runtime_config`
    an der von `§10.4` genannten Stelle. Die harte Regel ist **gemessen**: eine
    reine Observability-Aenderung erreicht eine Fake-Session, deren
    `reconfigure` durchfaellt, nicht — kein Reconnect, kein Audio-Neustart.
  - **Drei reale Befunde, alle behoben.** F-1: `.gitignore` verbarg mit der
    Regel `logs/` das gesamte neue Paket `ui/logs/` — der in `ARCH §5.1`
    eingefrorene Pfad der Logansicht; ohne Korrektur waere das Ergebnis dieses
    Work Packages nicht versionierbar gewesen und ein spaeterer Commit haette
    lautlos eine unvollstaendige Fassung enthalten (behoben mit einer
    begruendeten Negation `!ui/logs/`; die Regel fuer Laufzeitdaten bleibt
    wirksam). F-2: eine Abfrage, die schneller antwortet als `request_page`
    zurueckkehrt, veroeffentlicht synchron im aufrufenden Thread — die Seite
    verwarf dadurch ihre eigene frische Antwort als „veraltet" (behoben durch
    Reservierung der Anfrage-ID vor dem Absetzen). F-3: ein sofort
    zurueckkehrendes `shutdown()` liess eine laufende Abfrage in ein bereits
    zerstoertes `QObject` veroeffentlichen — in PySide6 eine
    Zugriffsverletzung (behoben durch `shutdown(wait=True)`).
  - **F-4 / bewusste Ablage.** Die neun Settings-Eintraege liegen in
    `core/logging_settings_metadata.py` statt in `core/settings_metadata.py`,
    weil `CONTRACTS §12.7` letzteres „bewusst rein" haelt und ein bestehender
    OBS-040-Contract-Test das prueft. `ARCH §12` verlangt in genau diesem Fall
    anzuhalten und die Architektur zu pruefen statt den Test zu aendern; das
    Ergebnis der Pruefung ist diese Trennung. `core/settings_metadata.py` ist
    byte-identisch geblieben. Das in `ARCH §5.1` ausgeschlossene Modul
    `ui/settings/logging_settings.py` entsteht **nicht**.
  - **Zehn Entscheidungen, alle aus dem bestehenden Freeze aufloesbar**: kein
    `DECISION REQUIRED`, **kein neuer Zaehler**, **kein neuer Recordtyp**
    (`§12` ist die verbindliche Liste — auch das Loeschen der Historie erzeugt
    bewusst keinen), kein neues Konfigurationsfeld, **kein normatives Dokument
    veraendert**.
  - **Teststand:** 170 neue Tests in fuenf Dateien, gruen unter `pytest`
    **und** `unittest`; volle Suite 1128 passed / 1 vorbestehender,
    umgebungsbedingter Fehlschlag (`lefx.interfaces`), dessen Vorbestand gegen
    einen frisch aus `91a7b7f` ausgepackten Baum nachgewiesen ist (dort 958
    passed / 1 identischer Fehlschlag; Differenz exakt die 170 neuen Tests).
    **Kein bestehender Test geaendert.** `git diff --check` leer, kein
    Cross-Workstream-Diff. Ende-zu-Ende-Diagnoseskript mit echtem Manager,
    echtem Store, echtem Query-Layer und echtem Qt-Fenster: **12/12 PASS,
    exit 0** — darunter 750 Zeilen paginiert waehrend der Worker
    weiterschreibt (keine Luecke, kein Duplikat), `raw` nur ueber `fetch_raw`,
    „Diagnosehistorie loeschen" mit 765 entfernten Zeilen bei nachweislich
    schreibmethodenfreiem Query-Layer, und drei Records, die **ohne geoeffnetes
    Fenster** geschrieben und von einem spaeter geoeffneten Fenster gezeigt
    werden.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-050-01_2026-08-17/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/RUN-01_2026-08-17/`
      (`TEST_RESULTS.md`, `DIFF_SUMMARY.md`, `CONTRACT_COVERAGE.md`,
      `QUERY_CASES.md`, `UI_ACCEPTANCE.md`, `probe_obs050_end_to_end.py`)
  - **Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**
  - Naechster Schritt: **OBS-050 Gate Review** (unabhaengig, frische Session,
    `Prompts/OBS-050_GATE_REVIEW.md`).

- 18.08.2026, `Prompts/OBS-050_GATE_REVIEW.md` — **OBS-050 Gate Review
  (unabhaengig, frische Session)**
  - Ergebnis: **`OBS-050 GATE FAIL`**. Evidence:
    `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/`
    (`GATE_REVIEW.md`, `gate_probe_obs050_ordering.py`,
    `gate_probe_obs050_live_happy_path.py`).
  - Geprueft wurde ausschliesslich der tatsaechliche Repositoryzustand:
    Produktcode, `git diff`/`git status`/`git diff --check`, eigene
    Testlaeufe mit beiden Runnern, ein Vergleichslauf gegen einen frisch aus
    `91a7b7f` ausgepackten Baum, das Diagnoseskript des Runs (unabhaengig
    wiederholt, 12/12 PASS, exit 0) und **zwei eigene Laufzeitproben gegen den
    echten Stack** — echter `SQLiteLogStore`, echter `LocalLogProvider`,
    echter `LogQueryService`, echtes Qt-`LogPage` (offscreen). Nicht die
    Abschlussberichte.
  - **Belastbar und in Ordnung:** der Query-Layer (kurzlebige
    Leseverbindungen mit `PRAGMA query_only = ON` statt `mode=ro`, Keyset ueber
    `logs.id`, `raw_json` nicht in der Listenabfrage, ausschliesslich
    Platzhalterbindung samt LIKE-Escaping, die Datei wird vom Leser nie
    angelegt, keine Verbindung bleibt offen, `query()` wirft nie, `status()`
    gecacht ohne I/O), die `LogQueryService`-Registry inkl. Failure-Isolation,
    die neun Settings-Eintraege nach `CONTRACTS §10.3` mit getrennten
    Ownership-Domaenen, die eine Zeile in `apply_runtime_config` nach `§10.4`,
    „Diagnosehistorie loeschen" am **Store** ueber den Manager (`FD-S4`,
    O-14), die Managerlebensdauer (`ARCH §6.2(b)`), die Importrichtung und
    „Logging laeuft ohne UI". `00_NORMATIV/`, `20_PLANUNG/` und
    `core/settings_metadata.py` byte-identisch zu `91a7b7f`, kein bestehender
    Test geaendert, volle Suite 1128 passed / 1 vorbestehender,
    umgebungsbedingter Fehlschlag; Baseline aus `91a7b7f` unabhaengig
    nachgemessen: 958 passed / 1 identischer Fehlschlag, Differenz exakt die
    170 neuen Tests.
  - **Blockierend ist ausschliesslich das Gate-Kriterium
    „Filter/Cursor/Sortierung verhalten sich deterministisch"** — nicht im
    Provider, sondern in der Ansicht `ui/logs/log_page.py`:
    - **B-1:** „Weitere laden" und das automatische Nachladen am Listenende
      haengen die umgekehrte, **aeltere** Folgeseite unten an; die Zeitspalte
      springt in der Mitte rueckwaerts. Reproduziert: erste Seite `r7…r11`,
      danach `r7…r11, r2…r6`.
    - **B-2:** startet der Live-Modus auf einer **leeren** Ergebnismenge
      (frische Installation, ein Filter auf den noch nichts passt, jeder
      Filterwechsel im Live-Modus), wird die erste aufsteigende Tail-Antwort
      im absteigenden Zweig verarbeitet: verkehrte Reihenfolge, und
      `_live_cursor` wird aus der **aeltesten** statt der juengsten Zeile
      gesetzt, sodass der naechste Tail dieselben Zeilen als Duplikate
      anhaengt. Reproduziert: `r4,r3,r2,r1,r0,r1,r2,r3,r4`. Der Normalfall —
      Live auf nicht leerer Ergebnismenge — ist korrekt und gegengeprueft.
  - Dazu W-1 (keine Tests fuer die Reihenfolge ueber zwei Seiten und fuer
    „Live auf leerem Store"; deshalb sind B-1/B-2 unentdeckt geblieben), W-2
    (`UI_ACCEPTANCE.md` A-11 „chronologisch dargestellt" gilt nur fuer die
    erste Seite) und sieben nicht blockierende Beobachtungen N-1 bis N-7.
  - Korrekturumfang: **eine** Produktdatei (`ui/logs/log_page.py`) plus zwei
    Tests in `tests/test_obs050_ui.py`. An Query-Layer, Settings, Apply-Kette,
    Manager und Worker ist nichts zu aendern.
  - **Kein Commit erstellt** (Commit nur bei `PASS`); HEAD unveraendert
    `91a7b7f`. **Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**
  - Naechster Schritt: **OBS-050 Korrekturlauf** fuer B-1 und B-2
    (einschliesslich W-1 und W-2), danach ein **erneuter unabhaengiger
    Gate-Review in frischer Session**. **OBS-060 darf nicht beginnen.**

- 18.08.2026, OBS-050 Gate Review (unabhaengig, frische Session)
  - Ergebnis: **`OBS-050 GATE FAIL`**. Geprueft wurde der tatsaechliche
    Repositoryzustand — Produktcode, `git diff`/`git status`/`git diff --check`,
    eigenstaendige Testlaeufe mit beiden Runnern, ein Vergleichslauf gegen einen
    frisch aus `91a7b7f` ausgepackten Baum, das Diagnoseskript des Runs und
    **zwei eigene Laufzeitproben gegen den echten Stack** — nicht die
    Abschlussberichte.
  - **In Ordnung**: Query-Layer (kurzlebige Leseverbindungen mit
    `PRAGMA query_only = ON`, Keyset ueber `logs.id`, `raw_json` nicht in der
    Liste, ausschliesslich Platzhalterbindung, LIKE-Escaping, die Datei wird vom
    Leser nie angelegt, keine Verbindung bleibt offen, `query()` wirft nie),
    Settings, Apply-Kette, Ownership-Trennung, Loeschfunktion am Store,
    Managerlebensdauer, Importrichtung, „Logging laeuft ohne UI", kein
    Ringbuffer, keine vorgezogenen Remote-/Admin-Funktionen.
  - **Blockierend**: das Gate-Kriterium „Filter/Cursor/Sortierung verhalten sich
    deterministisch" ist in der **Ansicht** nicht erfuellt. **B-1** —
    `_on_page_ready` drehte jede Historieseite um und hing die aeltere
    Folgeseite unten an; die sichtbare Zeitachse sprang an jeder Seitengrenze
    zurueck (`r7 … r11, r2 … r6`). **B-2** — die Art einer Antwort wurde aus
    `_live_cursor` statt aus der Anfrage bestimmt; nach einem leeren
    Ausgangsergebnis fiel die erste aufsteigende Tail-Antwort in den
    absteigenden Zweig, wurde umgedreht angezeigt und der Cursor aus der
    **aeltesten** Zeile gesetzt, worauf der naechste Tail dieselben Records
    erneut lieferte (`r4,r3,r2,r1,r0,r1,r2,r3,r4`). Dazu W-1 (Testluecke),
    W-2 (Evidenzformulierung) und sieben nicht blockierende Beobachtungen
    N-1 bis N-7.
  - Kein Commit erstellt; HEAD blieb `91a7b7f`.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`
    - `.../GATE-REVIEW-01_2026-08-18_CLAUDE/gate_probe_obs050_ordering.py`
    - `.../GATE-REVIEW-01_2026-08-18_CLAUDE/gate_probe_obs050_live_happy_path.py`
  - Naechster Schritt: OBS-050 Korrekturlauf fuer B-1 und B-2 (einschliesslich
    W-1 und W-2), danach ein erneuter unabhaengiger Gate-Review.

- 18.08.2026, OBS-050 Korrekturlauf (Run `RUN-OBS-050-02_2026-08-18`)
  - Ergebnis: **`OBS-050 CORRECTED – READY FOR RE-REVIEW`**. **Das Gate bleibt
    offen** — ein Korrekturlauf vergibt sein eigenes Gate nicht.
  - **Eigene Reproduktion vor jeder Aenderung.** Die unveraenderte Gate-Probe
    lief gegen den echten Stack und bestaetigte beide Befunde exakt
    (`FAILURES: 2`, exit 1); anschliessend wurden beide Ursachen am Code
    verifiziert.
  - **B-1 behoben** ueber die vom Gate ausdruecklich angebotene **Variante 1**:
    die Umkehrung je Historieseite entfaellt. Die Ansicht zeigt jede Seite so,
    wie der Provider sie geliefert hat (`newest_first=True`, neueste oben), und
    die aeltere Folgeseite gehoert damit folgerichtig nach unten. `_on_scrolled`
    bleibt unveraendert am unteren Rand — das eingefrorene „automatisches
    Nachladen am Listenende" (`CONTRACTS §9.3`) trifft so buchstaeblich die
    Stelle, an der die naechste Seite hingehoert. Die Keyset-/Cursor-Semantik
    des Providers ist unberuehrt. Variante 2 („Folgeseite oben einfuegen")
    haette den Nachladepunkt an den oberen Rand verlegt und entweder eine
    zweite Produktdatei oder einen Modell-Reset je Seite gebraucht, der Auswahl
    und Detailansicht verwirft.
  - **B-2 behoben**, indem die Semantik einer Antwort aus der **Anfrage** folgt:
    vier benannte Anfragearten, ein einziger Abfragetrichter `LogPage._issue`,
    der Anfrage-ID **und** Art in demselben Schritt festhaelt, eine Verzweigung,
    die die Art beim Verarbeiten **verbraucht** (eine wiederholte Zustellung
    bleibt folgenlos), und ein `_live_cursor`, der in beiden Live-Faellen aus
    der **juengsten** gelieferten Zeile stammt. Der fehlerhafte Zweig ist nicht
    repariert, sondern entfernt: die Fallunterscheidung kann gar nicht mehr aus
    dem Cursorstand entstehen. Keine neue Abfragearchitektur — dieselbe
    Provider-Schnittstelle, derselbe 250-ms-`QTimer`, derselbe
    `ThreadPoolExecutor(max_workers=1)`, kein Ringbuffer.
  - **Umfang**: produktseitig **ausschliesslich** `ui/logs/log_page.py`
    (456 → 526 Zeilen). Tests in `tests/test_obs050_ui.py` und — mechanisch
    bedingt, weil er den Quelltext von `_tail` liest —
    `tests/test_obs050_contracts.py`. Query-Layer, Settings, Apply-Kette,
    Manager, Worker, Tabellenmodell, Filterleiste, Detailansicht und Fenster
    sind unveraendert; `git diff --stat` zeigt fuer die versionierten
    Bestandsdateien exakt denselben Stand wie am Ende von RUN-01.
  - **W-1 geschlossen** mit neun Regressionstests, die die tatsaechliche
    UI-Verarbeitung ueber den echten `LogQueryController` samt Executor-Thread
    pruefen: Reihenfolge ueber drei Seiten, automatisches Nachladen am
    Listenende, Live-Start auf leerem Ergebnis, mehrere aufeinanderfolgende
    Tails, Filter ohne Treffer, Filterwechsel im laufenden Live-Modus,
    befuellter Normalfall und die Antwortzuordnung. Zwei RUN-01-Erwartungen,
    die das fehlerhafte Verhalten festgeschrieben hatten, sind richtiggestellt.
    **W-2** ist in `40_EVIDENCE/OBS-050/RUN-02_2026-08-18/UI_ACCEPTANCE.md`
    behandelt (A-11 bis A-13 neu formuliert, A-34 bis A-42 ergaenzt);
    RUN-01- und Gate-FAIL-Evidence bleiben unveraendert erhalten.
  - **Teststand**: 170 → **179 OBS-050-Tests**, gruen unter `pytest` **und**
    `unittest`; OBS-010…050 625 gruen; volle Suite 1137 passed / 1
    vorbestehender, umgebungsbedingter Fehlschlag (`lefx.interfaces`), dessen
    Lage **ausserhalb des Diffs** fuer diesen Lauf erneut nachgemessen ist
    (weder `tests/test_ap06_followup.py` noch `core/led_controller.py` liegen im
    Diff; derselbe Test schlaegt im frisch ausgepackten `91a7b7f`-Baum identisch
    fehl). Laufzeitproben: `probe_obs050_ordering_fix.py` 8/8 und
    `probe_obs050_end_to_end.py` 12/12, beide exit 0. Die unveraenderte
    Gate-Probe meldet fuer B-2 jetzt `ascending: True, duplicates: False`; fuer
    Fall A meldet sie erwartungsgemaess `False`, weil sie hart auf
    *aufsteigende* Monotonie prueft, die Tabelle nach Variante 1 aber
    durchgehend absteigend ist — der richtungsbewusste Ersatznachweis und die
    Einordnung stehen in `FIX_SUMMARY.md` Abschnitt 1.3.
  - `git diff --check` leer, HEAD unveraendert `91a7b7f`.
  - Wichtigste Artefakte:
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-050-02_2026-08-18/`
    - `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/RUN-02_2026-08-18/`
      (`FIX_SUMMARY.md`, `TEST_RESULTS.md`, `UI_ACCEPTANCE.md`,
      `probe_obs050_ordering_fix.py`)
  - **Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.** Die
    acht bewusst unversionierten Prompt- und Pipeline-Eintraege unter
    `30_AUSFUEHRUNG/` sind unangetastet.
  - Naechster Schritt: **erneuter unabhaengiger OBS-050 Gate Review** in
    frischer Session. **OBS-060 nicht beginnen.**

- 18.08.2026, `Prompts/OBS-050_GATE_REVIEW.md` (Re-Review-Auftrag) —
  **OBS-050 Gate Review II (gezielter Re-Review des Korrekturlaufs)**
  - Ergebnis: **`OBS-050 GATE PASS – OBS-060 MAY PROCEED`**. Evidence:
    `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-050/GATE-REVIEW-02_2026-08-18_CLAUDE/`
    (`GATE_REVIEW.md`, `gate2_probe_obs050_b1_b2.py`).
  - **Kein vollstaendiger neuer Gate-Review.** Die im ersten Gate bestandenen
    Bereiche wurden nicht erneut auditiert, weil sie nachweislich unveraendert
    sind: der versionierte Anteil ist **stat-identisch** zum ersten Gate (zehn
    Dateien, +475/−25), und nach Aenderungszeitpunkt sind allein
    `ui/logs/log_page.py`, `tests/test_obs050_ui.py` und
    `tests/test_obs050_contracts.py` beruehrt. RUN-01-Evidence und die
    Gate-FAIL-Evidence sind unangetastet; W-2 ist in einer eigenen
    RUN-02-Datei richtiggestellt statt durch Ueberschreiben.
  - **B-1 geschlossen.** Die gewaehlte **absteigende** Historiedarstellung ist
    normativ gedeckt (`CONTRACTS §5.7` friert `ORDER BY id DESC` und
    `AND id < :after_id` ein, `§8` `newest_first=True` als Default, `§9.3`
    verlangt das Nachladen am **Listenende** — mit absteigender Anzeige genau
    der aeltere Rand). Eine aufsteigende Historieanzeige wird nirgends
    gefordert; die gegenteilige Erwartung der ersten Gate-Probe ist damit
    aufgehoben, **ohne neue Contract-Entscheidung**. Eigene Laufzeitprobe ueber
    **fuenf** Seiten: streng absteigend, kein Richtungsbruch, keine Duplikate,
    keine Auslassungen, letzte Seite ohne Folgecursor; automatisches Nachladen
    ueber das echte Scrollbar-Ereignis mit demselben Ergebnis. Provider- und
    Keyset-Cursor unveraendert. Richtung jetzt: **Historie absteigend (neueste
    oben), Live aufsteigend (neueste unten)** — jeweils die Richtung der
    eingefrorenen Abfrage, in der Statuszeile benannt.
  - **B-2 geschlossen.** Jede Abfrage laeuft durch den einen Trichter
    `LogPage._issue(kind, …)`, der Anfrage-ID **und** Anfrageart in demselben
    Schritt festhaelt; `_on_page_ready` verzweigt darueber und verbraucht sie.
    Die Ableitung aus `_live_cursor` existiert nicht mehr, der Cursor stammt in
    beiden Live-Faellen aus der **juengsten** Zeile. Nachgemessen: Leerstart
    bleibt leer, erster Tail aufsteigend und duplikatfrei, Cursor auf dem
    neuesten Record, Folgetails setzen dahinter fort, Filter ohne Treffer und
    Filterwechsel im Live-Modus korrekt, befuellter Normalfall unveraendert,
    und ein absichtlich vergifteter `_live_cursor` aendert die Deutung einer
    Antwort nicht mehr (15/15 PASS, exit 0).
  - **Tests:** neun neue, die vollstaendige Anzeigesequenzen ueber den echten
    `LogQueryController` pruefen und **W-1** genau dort schliessen, wo B-1
    durchgerutscht war; das Double `FakeService` ist unveraendert. Die
    Aenderung in `tests/test_obs050_contracts.py` bildet nur den neuen
    `_issue`-Trichter ab und **schwaecht keine Contract-Anforderung ab** —
    dieselbe Zusicherung an beiden Enden geprueft, plus eine strukturelle
    Verschaerfung.
  - **Regression:** `-k obs050` **179/179** unter `pytest` **und** `unittest`;
    volle Suite 1137 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag
    (`lefx.interfaces`, ausserhalb des Diffs). Ein in einem von drei
    Vollaeufen zusaetzlich auftretender Fehlschlag
    (`test_ui_widgets.py::TestTranscriptOverlay::test_realtime_replaces_text_and_final_fades`)
    ist als **lastabhaengig flatterhaft, nicht als Regression** eingeordnet:
    zwei weitere Vollaeufe gruen, die Datei allein zweimal gruen, Testdatei und
    `ui/overlay.py` vom 2026-08-14 und damit ausserhalb von RUN-01 und RUN-02.
    `git diff --check` leer.
  - Die nicht blockierenden Beobachtungen N-1 bis N-7 des ersten Gates bleiben
    fuer OBS-060 vorgemerkt.
  - **Genau ein lokaler Commit** fuer den gate-geprueften OBS-050-Endstand
    erstellt: `feat(observability): complete OBS-050 local log view` auf
    `feat/einheitliche-triggerarchitektur`, mit Produktstand, den 179
    OBS-050-Tests, den RUN-01-/RUN-02-Unterlagen, der OBS-050-Evidence und
    beiden Gate-Reviews samt Probeskripten. Die **acht** bewusst
    unversionierten Prompt- und Pipeline-Eintraege unter `30_AUSFUEHRUNG/`
    sind **nicht** aufgenommen. **Kein Push, kein Merge, kein Rebase, kein
    Tag, kein PR.**
  - Naechster Schritt: **OBS-060 – V1 Hardening, Evidence & Baseline –
    Implementierung** (`Prompts/OBS-060_IMPLEMENTIERUNGSAUFTRAG.md`, frische
    Session). In diesem Lauf nicht begonnen.

- 18.08.2026, OBS-060 Implementierung (Run `RUN-OBS-060-01_2026-08-18`),
  Auftrag `Prompts/OBS-060_IMPLEMENTIERUNGSAUFTRAG.md`
  - Ergebnis: **`OBS-060 IMPLEMENTED – READY FOR V1 GATE`**. **Kein Gate-PASS
    in diesem Lauf**, **kein Commit, kein Push** — ein Implementierungslauf
    vergibt sein eigenes Gate nicht. Ausgangscommit `7fc6ca6`, HEAD unveraendert.
  - **Ausgangszustand selbst geprueft.** Der im Auftrag genannte Session-Root
    `P:\GithubRepos\marcosudau-vps` ist kein Git-Repository; maszgeblich ist
    `voice-stt-client\workspaces\einheitliche-triggerarchitektur`. Dort steht
    HEAD auf dem gate-gepruften OBS-050-Endstand. Selbst gemessene Baseline:
    **1137 passed / 1 vorbestehender Fehlschlag**.
  - **Zuerst ein Umgebungsblocker.** Der erste Suitelauf hing; nach zwoelf
    Minuten stand der Prozess bei 1,67 s CPU-Zeit. Ein
    `faulthandler`-Stackdump zeigt die Ursache: `platform._wmi_query`
    (Python 3.12, Windows) antwortet auf dieser Maschine nicht, und
    `sounddevice` ruft es beim **Import** — also haengt jeder Lauf, der
    `core.audio_capture` und damit `core.controller` importiert. Das ist keine
    Eigenschaft des Produkts: `voice-stt-client.spec` neutralisiert dieselbe
    Sonde fuer den gefrorenen Build laengst selbst
    (`scripts/pyinstaller_runtime_platform.py`). Fuer die Testlaeufe wurde ein
    `sitecustomize.py` **ausserhalb** des Projektbaums auf den `PYTHONPATH`
    gelegt; **keine Projektdatei ist dafuer angefasst worden**. Danach 80,9 s
    fuer die volle Suite — dieselbe Groeszenordnung wie im OBS-050-Gate.
  - **Drei echte Befunde, alle im V1-Scope, alle geschlossen.**
  - **B-1 – die Store-Erholung nach `ARCH §8.3` war unerreichbar.** Die
    60-Sekunden-Aussetzung wird zusammen mit `FAILED_STORE` gesetzt, und ab
    diesem Moment lehnt der Ingress **jeden** Record ab
    (`health.is_failed()`). Ohne Record kein Batch, ohne Batch kein
    `_write_with_policy` — und dort sasz die einzige Pruefung der Pause. Der von
    `§8.3` verlangte leere Testschreibvorgang fand nie statt, und die von
    `CONTRACTS §11.2` als „automatisch und still" zugesagte Erholung war im
    laufenden Prozess unmoeglich. Vor jeder Aenderung reproduziert
    (`probe_obs060_b1_reproduction.py`: drei Sekunden nach Gesundung des Stores
    `probe_write calls: 0`, `state: FAILED_STORE`, ein neues Producerevent wird
    nicht einmal eingereiht). Behoben durch `_resume_store_if_due()` am Anfang
    der Worker-Schleife. **Kein neuer Zaehler, kein neuer Health-Zustand, kein
    neues Konfigfeld, kein zweiter Erholungspfad** — `logging.recovered` schreibt
    weiterhin genau der Code, der es nach einem geglueckten Batch schreibt.
  - **B-2 – ein `None` des Client-Normalizers wurde nicht gezaehlt.**
    `CONTRACTS §3` legt die Pflicht woertlich dem Aufrufer auf;
    `from_client_event` besitzt genau ein `return None`, und es steht in seinem
    `except`-Zweig. Der Fall war vollstaendig unsichtbar — kein Zaehler, kein
    Health-Signal. Eine Zeile behebt es. Der **Serverpfad** bleibt bewusst
    ausgenommen, weil `None` dort auch „bildet auf keinen Record ab" heiszt; ein
    eigener Test haelt das fest.
  - **B-3 – die Mutation M-6 hatte keinen Waechter**, und konnte keinen der
    erwarteten Art haben: in SQLite sind `NULL`-Werte in einem UNIQUE-Index
    stets verschieden, Clientzeilen ohne `event_id` werden also auch mit vollem
    Index nicht dedupliziert (gemessen mit beiden Indexformen, SQLite 3.49.1).
    Statt einen kuenstlich roten Test zu bauen, prueft der neue Waechter das,
    was die Norm festlegt: `FD-C7` nennt den Index **partiell**,
    `CONTRACTS §5.2` friert die DDL ein. Die Richtigstellung der
    Begruendungsspalte im Plan bleibt als **O-2** offen — planerische Dokumente
    aendert ein Implementierungslauf nicht.
  - **Der Runtime-Isolationsnachweis liegt in der verbindlichen Form vor** —
    als Protokollvergleich ueber einen vollstaendigen Diktatzyklus mit
    **echtem** `STTController`, **echter** `FeedbackEngine`, **echtem**
    `DualSessionCoordinator`, **echtem** `EventProtocolProcessor` und **echtem**
    `EventStreamTransport._dispatch`; Doubles nur fuer WebSocket und
    Ausgabegeraete. Aufgezeichnet werden gesendete Frames samt Laengen,
    `chunks_dropped_send_queue`/`max_send_queue_depth`, die
    `CommandResult`-Folge, die `FeedbackDecision`-Folge, die vollstaendige
    Snapshotfolge, das `FinalProcessingResult`, Injektionen, Textrueckrufe,
    Transportwechsel, die angenommenen Eventstream-Events, der Resume-Cursor und
    die Cursordatei. **R-2 bis R-7 liefern das Referenzprotokoll R-1 Byte fuer
    Byte** — einschlieszlich des Laufs mit einem Ingress, dessen saemtliche
    Methoden werfen, und des Laufs mit einem dreimal werfenden
    `on_observation`, fuer den zusaetzlich der Endstand der Cursordatei stimmt.
    Einzige Normalisierung: `updated_at`, der Wanduhrzeitpunkt des
    Schreibvorgangs. **R-2 belegt, dass der Vergleich etwas wert ist** — die
    funktionierende Observability hat den Zyklus mit sechs Records
    aufgezeichnet.
  - **Alle acht Mutationschecks machen einen Test rot.** Vorlauf und
    Wiederherstellung gehoeren zum Nachweis: vor der ersten Mutation laufen alle
    betroffenen Auswahlen gruen (143 passed), nach jedem Schritt ist jede
    beruehrte Datei per SHA-256 als **byte-identisch wiederhergestellt** belegt.
    Bei M-3 (`put_nowait` → blockierendes `put`) endet der Lauf nicht mehr; ein
    Timeout zaehlt hier zu Recht als rot, denn ein blockierter Producer-Thread
    schlaegt nicht fehl, er haengt.
  - **Sechs uebernommene Gate-Beobachtungen geschlossen:** OBS-030 N-2
    (Schleifenbudget) und N-3 (`try/finally` um den gesamten Ablauf in
    `app.py`), OBS-040 N-4 (Kommentar zu den kumulativen Hot-Path-Zaehlern),
    OBS-050 N-1 (kein Sink-Neubau ohne Grund), N-2 (drei eigene Guards statt
    eines gemeinsamen) und N-4 (`complete` nur bei echter Kuerzung).
  - **Eine Zwischenregression wurde bewusst anders geloest.** Der erste
    Zuschnitt der N-1-Korrektur liesz den `sink`-Schluessel weg und machte damit
    den bestehenden, gate-gepruften Test
    `test_worker_receives_retention_entry_limit_and_sink` rot. Statt den Test
    anzupassen wurde die **Korrektur** geaendert: der Manager reicht dieselbe
    Sinkinstanz weiter, der Worker vergleicht nach Identitaet, also findet keine
    Rotation statt und der Test bleibt gueltig. Ein bestehender Test wird nicht
    passend gemacht.
  - **Teststand:** 27 neue Tests in `tests/test_obs060_v1_hardening.py`, gruen
    unter `pytest` **und** `unittest`; V1-Kette OBS-010…060 **652 gruen**; volle
    Suite **1164 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag**
    (`lefx.interfaces`, auszerhalb des Diffs) gegenueber 1137 / 1 in der
    Baseline — Differenz **exakt** die 27 neuen Tests. **Kein bestehender Test
    geaendert.** `git diff --check` leer, `00_NORMATIV/` byte-identisch zu
    `7fc6ca6`, kein Cross-Workstream-Diff. Produktseitig **sechs Dateien,
    +131/−13**.
  - **Ausdruecklich offen und nicht beschoenigt:** die **manuelle Abnahme
    M-1…M-11 am realen Produktionspfad**. Neun der elf Punkte sind gegen den
    echten Stack automatisiert belegt und M-11 (Dateirechte, `icacls`) ist
    protokolliert — aber der Durchlauf auf einem Installationssystem mit
    laufendem Server, mit Datum, Serveradresse und Clientversion, steht aus.
    `WP-OBS-060` erklaert ihn zur Pflicht und sagt, dass V1 ohne ihn als
    „teilweise" gilt. Dreizehn offene Punkte sind in `V1_OPEN_POINTS.md`
    einzeln begruendet; sieben brauchen eine Entscheidung der unabhaengigen
    Instanz, darunter **O-1** (ein Ersatzrecord `logging.record_rejected` fuer
    eine vom Normalizer selbst verschluckte Ausnahme braeuchte den Ausnahmetyp
    und damit eine Signaturaenderung an einer in `CONTRACTS §3` eingefrorenen
    Funktion; der Kernbefund B-2 ist ohne diese Erweiterung vollstaendig behoben,
    also ist sie kein Blocker und wurde nicht mitgeliefert). **Keiner der
    offenen Punkte beruehrt ein V1-Gate-Kriterium oder gefaehrdet die
    Triggerarchitektur-Phase.**
  - **Kein `DECISION REQUIRED`** in einem normativen Dokument, kein neuer
    Zaehler, kein neuer Recordtyp, kein neues Konfigfeld, keine geaenderte
    Signatur einer eingefrorenen Funktion.
  - Evidence: `40_EVIDENCE/OBS-060/RUN-01_2026-08-18/` (sieben `V1_*.md`,
    `DIFF_SUMMARY.md`, acht Probeskripte, Rohausgaben unter `output/`), Run:
    `30_AUSFUEHRUNG/runs/RUN-OBS-060-01_2026-08-18/`.
  - Naechster Schritt: **OBS-060 – Logging V1 Final Gate Review**, unabhaengig,
    in frischer Session (`Prompts/OBS-060_V1_GATE_REVIEW.md`). Der lokale
    Abschlusscommit darf erst danach und **nur bei `PASS`** entstehen.

## 2026-08-18 – OBS-060 Logging V1 Final Gate Review: FAIL

- Unabhaengiger Review gegen Produktcode, vollstaendigen Git-Diff, normative
  Freezes, alle Work Packages OBS-010…060, alle 13 Punkte aus
  `V1_OPEN_POINTS.md`, Tests und Evidence; Abschlussbericht nicht als
  Wahrheitsquelle verwendet.
- Ergebnis: **`G-OBS-V1 FAIL`**. Das nach `WP-OBS-060` zwingende manuelle,
  datierte Produktionsprotokoll M-1…M-11 fehlt. Automatisierte Pendants wurden
  anerkannt, aber nicht als Ersatz fuer die manuelle Abnahme gewertet.
- Neuer blockierender Repositorybefund: `logging.observability.enabled` ist
  als `IMMEDIATE` eingefroren, aber ein mit `enabled=False` gestarteter
  `ObservabilityManager` besitzt nur `NULL_INGRESS` und keinen Worker/Store;
  ein spaeteres `apply_config(enabled=True)` bleibt wirkungslos. Reproduziert
  gegen den Produktcode; Korrektur oder Apply-Policy-Entscheidung erforderlich.
- O-1 und O-7 bleiben **DECISION REQUIRED**. Das Gate hat weder Signaturen noch
  Freeze-/Contract-Dateien veraendert und keine der sieben offenen
  Entscheidungen stillschweigend aufgeloest.
- Evidence-Befunde: Traceability markiert Failure Isolation als erfuellt,
  obwohl die eigene Failure-Probe F-7.4 als `OPEN` ausweist; Performance-B-4.2
  behauptet „zweite Seite nicht langsamer“, prueft tatsaechlich aber nur
  `< max(50 ms, 5× erste Seite)`.
- Unabhaengige Verifikation: V1-Auswahl 652 passed; volle Suite 1165 passed
  unter `pytest`; 1165 Tests `OK` unter `unittest`; E2E-, Runtime-Isolations-,
  Failure-, Performance-, Privacy- und Packaging-Probes wiederholt; alle acht
  Mutationen machen Tests rot und alle sechs beruehrten Dateien wurden
  byte-identisch wiederhergestellt. `git diff --check` leer.
- Gate-Haken und Abschlusskriterium bleiben ungesetzt. **Kein Commit, kein
  Push.** Die acht bewusst unversionierten Prompt-/Pipeline-Eintraege wurden
  nicht aufgenommen.
- Evidence:
  `40_EVIDENCE/OBS-060/GATE-REVIEW-01_2026-08-18_CODEX/GATE_REVIEW.md`.
- Naechster zulaessiger Schritt: Entscheidungen und Korrekturlauf,
  vollstaendige M-1…M-11-Abnahme am Installationssystem, danach neuer
  unabhaengiger OBS-060 Final Gate Review. Triggerarchitektur bleibt gesperrt.

## 2026-08-20 – Kontrollierter Abschluss der vorgezogenen Logging-/Observability-Phase vor Trigger-Migration

- **Ausgangslage und Kontext:** Die Logging-/Observability-V1-Phase wurde vor den ausstehenden großen Arbeiten an der einheitlichen Triggerarchitektur vorgezogen und umfasst:
  - OBS-010 bis OBS-050 mit bestandenen Gates und lokalen Checkpoint-Commits (`b363346`, `cb0b81f`, `91a7b7f`, `7fc6ca6`),
  - OBS-060-Hardening und Evidence (`8eea774`),
  - nachfolgende Diagnose-UI-Nachbesserungen (`d9369c5`),
  - praktische Sicht- und Bedienprüfungen der neuen Logging-Oberfläche,
  - reale Nutzung des Clients mit aktiver Logging-Infrastruktur.
- **Ergebnis der praktischen Prüfung:** Die praktische Sicht- und Bedienprüfung verlief erfolgreich. Im realen Betrieb des Clients zeigten sich keine grundlegenden Probleme der neuen Logging-Architektur. Logging-Ansicht, Filterung, Live-/History-Darstellung und Logging-Infrastruktur funktionieren plausibel und stabil.
- **Projektentscheidung:**
  - Die vorgezogene Logging-/Observability-Phase wird an dieser Stelle kontrolliert abgeschlossen.
  - Der erreichte Logging-Stand ist als belastbarer Arbeitsstand für die Fortsetzung des Gesamtprojekts akzeptiert.
  - Es existieren noch kleinere Rest-, Rand- bzw. vollständige formale Produktionsabnahmepunkte (u. a. M-1…M-11 am Installationssystem).
  - Diese werden bewusst **nicht** mehr isoliert vorgezogen. Da wesentliche Kernbereiche des Clients im unmittelbar folgenden Umbau der einheitlichen Triggerarchitektur ohnehin erneut angefasst werden, werden die verbleibenden Punkte nach bzw. im Zuge der Triggerarchitektur-Migration erneut betrachtet und gegen den dann maßgeblichen Gesamtzustand validiert.
  - Es wird ausdrücklich **kein formal vollständiges `G-OBS-V1 PASS`** behauptet, da die normativ geforderten formalen Restbedingungen noch nicht vollständig erfüllt sind. Das Nichtvergeben des Siegels ist eine bewusste Projektentscheidung und kein übersehener Fehler.
- **Nächster Hauptarbeitsbereich:** Wiederaufnahme und Durchführung der Arbeiten zur einheitlichen Triggerarchitektur (`feat/einheitliche-triggerarchitektur`).

## 2026-08-23 – OBS-CLOSE-001: Logging / Observability Teil A konsolidiert, archiviert und für Trigger-Fortsetzung abgeschlossen

- **Run:** `OBS-CLOSE-001` (organisatorischer Abschluss- und Archivierungsrun, kein Produktcode, keine Triggerplanung verändert, kein Commit/Push in diesem Run selbst).
- **Ergebnis:** Logging / Observability Teil A – Pre-Trigger Foundation ist organisatorisch abgeschlossen. Verbindliche Statusaussage: **`CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`**. Ausdrücklich **nicht** behauptet: `G-OBS-V1 PASS`. Formal gilt weiterhin **`G-OBS-V1 NOT PASSED`** — bestimmte manuelle/formale Restabnahmen (u. a. `M-1…M-11`) bleiben bewusst auf den nach der Trigger-Migration maßgeblichen Gesamtzustand verschoben (unverändert gegenüber der Entscheidung vom 2026-08-20).
- **Archivpfad:** `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/`, bestehend aus `LOGGING_OBSERVABILITY/` (vollständige, verlustfrei überführte Arbeitsakte inkl. Normativ, Analyse, Planung, Ausführung/Runs/Prompts, Evidence, 80_DOCS, Zwischenarchiv) und `STEUERUNG_SNAPSHOT/` (byte-identische Kopien von `LOG_VERLAUF.md`, `CURRENT_STATE.md`, `MASTERPLAN.md` zum Abschlusszeitpunkt).
- **Kanonische Produktdokumentation:** dauerhaft unter `docs/observability/` (21 Markdown-Dateien plus `MANIFEST.json`, Fassung vom 2026-08-21 als vollständigere Quelle gegenüber der Fassung vom 2026-08-20 identifiziert und verwendet; die fehlende Datei `13_HEALTH_BACKPRESSURE_FAILURE_ISOLATION.md` wurde aus dem zugehörigen ZIP-Paket rekonstruiert und Hash-geprüft ergänzt).
- **Konsolidierung:** Zwei parallele Prompt-Bestände (`30_AUSFUEHRUNG/Prompts/` aktiv, `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` als nachweislich unbenutzte, aber inhaltlich teils abweichende zweite Pipeline) wurden geprüft; die aktive Struktur ist auf das kanonische Namensschema `prompts/` (lowercase) vereinheitlicht, die zweite Pipeline bleibt unverändert als historische Draft-Akte erhalten (mehrere Gate-Review-Dateien unterscheiden sich inhaltlich trotz gleichen Namens und wurden **nicht** dedupliziert).
- **Logging Teil B (deferred, nicht verloren):** `OBS-100` bis `OBS-180` sind im `MASTERPLAN.md` ausdrücklich als `DEFERRED / BLOCKED BY TRIGGER ARCHITECTURE` verankert. Planungsquelle vollständig archiviert unter `LOGGING_OBSERVABILITY/20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-100_*.md` bis `WP-OBS-180_*.md`. Nächster Logging-Einstieg nach der Trigger-Migration: `OBS-100`.
- **Triggerarchitektur:** ist mit diesem Run wieder alleiniger aktiver Hauptworkstream unter `ARBEITSDATEIEN/10_AKTUELL/`. Keine fachlichen Triggerentscheidungen und keine Änderung an der Triggerplanung durch diesen Run.
- **Details:** vollständiger `RUN_REPORT.md` und `OUTPUT_INDEX.md` in
  `LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-CLOSE-001_2026-08-23/`
  innerhalb des oben genannten Archivpfads.

## 2026-08-23, 17:18 Uhr (UTC+02:00) – WS-NORM-001: Logging-Merge nach main und Workspace-Normalisierung abgeschlossen

- **Run:** `WS-NORM-001` (Abschluss der gesamten Logging-/Branch-Separations-/
  CI-/Workspace-Aufräumphase: `OBS-CLOSE-001`, `OBS-CLOSE-002`, `BS-001`,
  `BS-002`, `BS-003`, `WS-NORM-001`).
- **Ergebnis:** PR `#1 – feat(observability): establish pre-trigger logging
  baseline` wurde per Merge-Commit `136679a2b441172aee7ef43b28635348af45b91b`
  nach `main` gemergt (vormaliger PR-HEAD `11e3421`, GitHub-CI davor grün
  unter Run `32647574177`). GitHub-CI auf `main` für den Merge-Commit
  selbst ebenfalls grün unter Run `32647846124`. `main` enthielt vor diesem
  Merge keine `ARBEITSDATEIEN`; die vollständige Logging-/Observability-
  Arbeitsakte (inkl. `90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/`)
  liegt damit ausschließlich über Git-Historie, nicht über manuelles Kopieren,
  dauerhaft auf `main`.
- **Workspace-Endzustand:**
  - `P:\GithubRepos\marcosudau-vps\voice-stt-client\main` = Branch `main` /
    Baseline (Checkout dort unverändert bei `wip/led-sound-debugfeedback-sicherung`
    belassen; nur der lokale `main`-Branch-Ref wurde per Fetch aktualisiert).
  - `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`
    = aktiver Entwicklungs-Workspace, in diesem Run vollständig read-only
    belassen.
  - `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`
    = per `git worktree remove` git-seitig vollständig entfernt (kein
    Worktree mehr, keine Dateien mehr, kein Prompt-/Report-/Evidence-
    Verlust). Der dadurch leere Verzeichnis-Stub selbst konnte in diesem
    Run wegen eines von außen gehaltenen Dateisystem-Locks (Ursache nicht
    identifizierbar, keine andere Claude-Code-Session betroffen) nicht
    physisch gelöscht werden und erfordert eine manuelle Löschung durch
    den Benutzer; siehe Blocker-Abschnitt im `RUN_REPORT.md`.
- **Dauerhafter Standard-Startordner** für normale Agenten-Sessions ab
  sofort:
  `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`.
- **Nicht Teil dieses Runs:** Merge von `main`/Logging-Stand nach
  `feat/einheitliche-triggerarchitektur` (separater, nachfolgender Schritt
  "Trigger Main-Integration"); keine fachliche Änderung an Produktcode.
- **Details:** vollständiger `RUN_REPORT.md` (inkl. Blocker-Abschnitt) in
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-WS-NORM-001_2026-08-23/RUN_REPORT.md`
  und zentraler Index in `ARBEITSDATEIEN/00_STEUERUNG/AUFRAEUMPHASE_INDEX.md`.
- **Schlussurteil:** `WORKSPACE NORMALIZED – READY FOR TRIGGER MAIN-INTEGRATION`
  (mit kosmetischem Restpunkt: leerer Verzeichnis-Stub manuell zu löschen).

## 2026-08-23 18:26:43 +02:00 – WS-NORM-002: Governance- und Workspace-Endbereinigung

- **Run:** `WS-NORM-002` (kurzer Maintenance-Run zum vollständigen Abschluss
  der noch offenen organisatorischen Punkte aus `WS-NORM-001`). Session
  absichtlich außerhalb aller Git-Worktrees gestartet
  (`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS`); alle
  Git-Operationen über absolute Pfade bzw. `git -C <pfad>`.
- **Ausgangsbefund nach WS-NORM-001:** Der RUN_REPORT.md von `WS-NORM-001`
  ging noch davon aus, dass der Standalone-Main-Clone
  (`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`) auf
  `wip/led-sound-debugfeedback-sicherung` ausgecheckt sei und der leere
  Verzeichnis-Stub `workspaces\logging-observability-pre-trigger` noch
  physisch existiere. Zu Beginn von `WS-NORM-002` wurde tatsächlich
  festgestellt: Der Main-Clone war bereits sauber auf Branch `main`
  ausgecheckt (`git status --short` leer) und exakt auf dem bekannten
  GitHub-`main`-Stand `8428dade9a418960956bcc41b8f53c9b552db509`; der
  Verzeichnis-Stub war laut `Test-Path` bereits physisch entfernt. Es waren
  daher keine Fast-Forward- oder Checkout-Operationen mehr nötig, nur
  Verifikation.
- **GitHub-`main` verifiziert:** `main`-SHA `8428dad...db509`, identisch mit
  `origin/main`; PR `#1` bestätigt `MERGED`
  (`mergeCommit 136679a2b441172aee7ef43b28635348af45b91b`); GitHub-CI für den
  aktuellen `main`-HEAD grün (Run `32649017902`, `success`).
- **Governance-Dateien vervollständigt:** `WORKSPACE_KONVENTION.md` neu
  angelegt; `CURRENT_STATE.md` und `MASTERPLAN.md` minimal um
  Workspace-Status bzw. Abschluss der Branch-Separation/Merge-Phase ergänzt;
  `AUFRAEUMPHASE_INDEX.md` um den `WS-NORM-002`-Eintrag und den korrigierten
  Workspace-Endzustand ergänzt.
- **OUTPUT_INDEX ergänzt:** Fehlender
  `RUN-WS-NORM-001_2026-08-23/OUTPUT_INDEX.md` neu erstellt (Zuordnung aller
  tatsächlich vorhandenen Artefakte, nichts erfunden); `RUN_REPORT.md`
  desselben Runs um einen sachlichen Nachtrag ergänzt (Stub-Entfernung
  `Test-Path`-verifiziert, korrekter `main`-SHA-Verlauf, Main-Clone-Checkout
  bestätigt).
- **Lokale Workspace-Hinweise (außerhalb Git):**
  `P:\GithubRepos\marcosudau-vps\voice-stt-client\WORKSPACE_MAP.md` und
  `...\ACTIVE_SESSION_ROOT.txt` neu angelegt (existierten zuvor nicht).
- **Status des leeren Logging-Stubs:** `workspaces\logging-observability-pre-trigger`
  ist git-seitig entfernt und laut `Test-Path` (2026-08-23) auch physisch
  nicht mehr vorhanden. Kein kosmetischer Restpunkt mehr offen.
- **Trigger-Worktree:** `workspaces\einheitliche-triggerarchitektur`
  (`feat/einheitliche-triggerarchitektur`) in diesem Run ausschließlich
  lesend verifiziert (`branch --show-current`, `rev-parse HEAD`,
  `status --short`); keine Schreiboperation, kein Commit, kein Merge.
- **Endgültiger Default Session Root:**
  `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`.
- **Nicht Teil dieses Runs:** Main→Trigger-Integration und jegliche
  Trigger-Facharbeit; keine Produktcodeänderungen.
- **Nächster Schritt:** `Main-Baseline kontrolliert in
  feat/einheitliche-triggerarchitektur integrieren`.
- **Details:** vollständiger `FINALIZATION_REPORT.md` und `OUTPUT_INDEX.md`
  in
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-WS-NORM-002_2026-08-23/`.
- **Schlussurteil:** siehe `FINALIZATION_REPORT.md`.

- 23.08.2026 23:47, DOC-ARCH-002 COPY-ONLY Vorbereitung (Run `AP-ORG-001_ARBEITSSTRUKTUR_COPY_PREP/01_COPY_PREP`)
  - Beschreibung: `arbeitsstruktur_toolkit_v2` nach Checksum-Prüfung (SHA-256
    verifiziert) unter `.agents/skills/arbeitsstruktur/` installiert.
    `Initialize-Arbeitsstruktur.ps1` ausgeführt (nur ergänzend: `AGENTS.md`
    und `CLAUDE.md` um markierten Abschnitt erweitert, `ARBEITSDATEIEN/20_ZURUECKGESTELLT/README.md`
    neu angelegt; bestehende Dateien nicht überschrieben).
    `Test-Arbeitsstruktur.ps1` bestätigt PASS (0 Fehler, 0 Warnungen).
  - **Nicht Teil dieses Runs:** kein Commit, kein Push, keine
    Main→Trigger-Integration; das folgt in einem separaten Prüfauftrag.

## 2026-08-24 10:26:57 +02:00 – PLAN-ORG-001: Triggerplanung vereinfacht und Entscheidungsstand konsolidiert

- Aktiven Arbeitsblock auf einen flachen `PLANUNG/`-Bereich und einen
  separaten `NACHVERFOLGUNG/`-Bereich vereinfacht; doppelte Altpfade nach
  vorherigem Inhalts-/Hashabgleich entfernt.
- Zentrale Planungsarbeitsdatei
  `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md` angelegt und die aktuelle
  fachliche Runde zu Wake-Word-Katalog, Sessionauswahl, Detection-Bündelung,
  Pause/Reconnect, ReSpeaker-Mute, Pre-Roll sowie konfigurierbaren
  Activation-Control-Hotkeys dokumentiert.
- Nicht kumulatives `refresh` als aktuelle Sollrichtung festgehalten und
  widersprechende ältere `Active = Finish`-/Extend-Aussagen als überholt
  gekennzeichnet.
- Noch keine Implementierungs-APs aktualisiert oder ausgeführt; kein
  Produktcode geändert, kein Commit erstellt.

## 2026-08-24 11:14:03 +02:00 – PLAN-CONS-001: Bereits besprochene Triggerentscheidungen in aktive Unterlagen übernommen

- Bekannte Widersprüche zwischen zentraler Entscheidungsdatei, Zielbild und
  älteren Analyse-/Migrationsfolgerungen bereinigt.
- Konfigurierbare Hotkey-Active-Aktionen, nicht kumulatives `refresh`,
  reconnect-feste Wake-Word-Pause innerhalb der Client-Laufzeit, ungepauster
  App-Neustart und erlaubter Laufzeitzustand mit null effektiven Triggern in
  den aktiven Solltext übernommen.
- Wake-Word-Buildkatalog, globales Disable, Sessionauswahl, Aliase,
  gemeinsame Empfindlichkeit und Detection-ID konsolidiert.
- Historische Ist-Codebefunde in den Analysen erhalten; widersprechende
  Sollfolgerungen ausdrücklich als ersetzt markiert. Keine AP-Zuordnung,
  keine Produktcodeänderung und kein Commit.

## 2026-08-24 11:32:38 +02:00 – PLAN-CONS-002: Weitere Bedien- und Lifecycle-Entscheidungen übernommen

- Mehrere serielle Sprachsegmente innerhalb einer Activation als bestehendes
  und beizubehaltendes Soll bestätigt; `refresh` ausschließlich für
  `followup_wait` festgelegt.
- Dritten optional belegbaren Wake-Pause-Hotkey sowie Finish-/Cancel-
  Außenwirkung einschließlich verpflichtender Lifecycle-Rückmeldung und
  terminalem Ausgang je angenommenem Segment dokumentiert.
- Wake-Word-Katalog von der Laufzeitinitialisierung getrennt: verfügbarer
  Build-Katalog bleibt vollständig auswählbar, je Session werden nur die
  ausgewählten Modelle geladen.
- Einzel-Score-Verhalten des aktuellen OpenWakeWord-Adapters und ungefähr
  32-ms-Audiotakt belegt; fehlender Detection-Guard nach dem ersten Treffer
  als Mehrfachsignalpfad bestätigt. Fachlicher Latch bis zum Unlock
  festgelegt; eine zusätzliche Fehlalarm-Bestätigung bleibt an reale
  Score-/Audio-Messungen gebunden.
- Aktive Planungs-, Zielbild-, Analyse-, Status- und Traceability-Unterlagen
  widerspruchsarm aktualisiert. Kein Namespace-Inhalt gelesen, kein
  Produktcode geändert und kein Commit erstellt.

## 2026-08-24 12:19:15 +02:00 – PLAN-CONS-003: Finish-/Cancel- und Wake-Word-Admission fachlich eingefroren

- Finish-/Cancel-Wirkung je Activation-Phase und Exactly-once-/Retry-Regel
  bestätigt; wirksame Transition erzeugt genau ein Lifecycle-Ereignis,
  Command-Replays kein Duplikat.
- Cancel verwirft bzw. unterdrückt nur noch nicht veröffentlichte Resultate;
  bereits ausgegebener oder eingefügter Text wird nicht zurückgenommen.
- Atomare Wake-Word-Admission bestätigt: eine problematische ID lehnt die
  gesamte Auswahl maschinenlesbar ab; Teilerfolg und stiller Fallback sind
  unzulässig.
- Entscheidungen in Zielbild, zentraler Entscheidungsdatei,
  Implementierungsreihenfolge, Traceability, Status und technischer Analyse
  konsolidiert. Kein Namespace-Inhalt gelesen, kein Produktcode geändert und
  kein Commit erstellt.

## 2026-08-24 23:17:21 +02:00 – PLAN-CONS-004: Reconnect-, Settings- und Dauerschutzentscheidungen übernommen

- Serververlust verwirft die aktive Activation und startet nach Reconnect eine
  neue Idle-Session; ReSpeaker-/Geräteverlust cancelt die Activation, lässt
  die Serversession für lokale Wiederverbindung aber bestehen.
- Persistierte Basis verlangt mindestens einen Trigger; null effektive
  Trigger dürfen nur während derselben Client-Laufzeit Reconnects, neue
  Sessions und Geräteverlust überstehen.
- Serverautorisierte Settings-Control-Plane mit Session-/Server-Scope,
  Adminschutz, Effective Values und Apply-Policies als Teil der
  Triggerarchitektur festgelegt. Triggerdomäne und erweiterbare
  Servereinstellungsseite werden jetzt umgesetzt, fachfremde Vollmigration
  später.
- Wake-Word-Ausschluss bei lückenlosem unmittelbar folgendem Sprachfluss sowie
  großzügiger Daueraufnahme-Watchdog mit Hotkey-Reset, Vorwarnung und Ende der
  gesamten Activation dokumentiert. Abschlusswirkung des Schutzablaufs bleibt
  offen.
- Browserclient aus dem Scope genommen; versionierte Desktop-/Server-/
  Protokoll-Kompatibilitätsmatrix als Repositoryartefakt vorgesehen.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert und kein Commit
  erstellt.

## 2026-08-25 00:17:14 +02:00 – PLAN-CONS-005: Zweite fachliche Härtungsrunde abgeschlossen

- Daueraufnahme-Watchdog mit zehn Minuten Default, 30 Sekunden Vorwarnung und
  regulärer Verarbeitung des bis dahin erfassten Audios vollständig
  entschieden; Schutzabläufe dürfen Anwenderarbeit nicht still verwerfen.
- Manual-/Wake-Suppression getrennt und clientlaufzeitweit bestätigt; keine
  zusätzliche Pause-all-Aktion.
- Client-/Server-Grenze festgezogen: Hotkeys, Hardware-/Gerätelogik, Mute und
  Feedbackkonfiguration clientseitig; Server verarbeitet semantische Commands,
  generische Audioverfügbarkeit und erzeugt Domain-Events.
- Activation-Settings-Snapshot und bewusste Reconnect-Auswahl bei laufender
  Activation bestätigt.
- Windows Credential Manager als dauerhafter Admin-Key-Speicher festgelegt;
  UI kann Credentials anlegen, ersetzen und löschen, `QSettings` bleibt frei
  vom Secret und ein Klartext-Fallback ist verboten.
- Klarer Desktop-Protokoll-Cut mit Versions-/Commit-Kompatibilitätsmatrix und
  verständlicher Handshake-Ablehnung bestätigt; Browserclient bleibt
  nachgelagert.
- Aktive Planungs-, Zielbild-, Traceability-, Status- und Analyseunterlagen
  konsolidiert. Kein Namespace-Inhalt gelesen, kein Produktcode geändert und
  kein Commit erstellt.

## 2026-08-25 01:20:27 +02:00 – PLAN-FREEZE-001: Technischer Contract und finaler Implementierungsplan

- Vordergrund-Lock und Hintergrund-Finalisierung getrennt: Lockfreigabe nach
  sicherem Eingabeschluss, Finalresultate älterer Activations werden über
  stabiles Ledger und Reihenfolge nachgereicht.
- Fünf Vordergrundphasen einschließlich `closing_input` sowie Hintergrund-
  `draining` festgelegt.
- Watchdogwerte 600/180/30 Sekunden samt nicht kumulativer, nicht
  verkürzender Refreshformel eingefroren.
- Protokoll-v2-, ID-, Event-, Snapshot-, Resync-, Settings-, Wake-Word- und
  Recoveryvertrag als normative Planungsgrundlage erstellt.
- Finalen Implementierungsplan repositoryrein zerlegt: `AP-SRV-*` nur Server,
  `AP-CLI-*` nur Desktop-Client, `AP-INT-*` ohne Produktcodeänderung.
- Traceability vollständig auf die getrennten AP-Reihen abgebildet und
  überholten Reihenfolgeentwurf entfernt.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert und kein Commit
  erstellt.

## 2026-08-25 02:03:42 +02:00 – PLAN-EXEC-001: Parallelausführung und Agentenaufträge vorbereitet

- Normatives Protokoll-v2-Wire-Schema und gemeinsame maschinenlesbare
  Positiv-/Negativvektoren für Server-, Client- und Integrationsgate ergänzt.
- Mehrdeutigkeit der Triggerquelle geschlossen: Der Desktop-Client sendet
  `activate` ausschließlich als `manual`; Wake-Word-Admission entsteht
  serverintern und wird nur als bestätigter Serverzustand gespiegelt.
- Ausführungsworkflow für maximal einen GPT-5.6-Sol-Sub-Agenten und einen
  parallelen Claude-Code-CLI-Lauf mit Wellen, Dependency-Gates,
  Modellempfehlungen und Root-Endabnahme erstellt.
- Dokumentationspflicht in jedes Implementierungs-AP aufgenommen und
  agentengerechte Auftragsschablone mit Ownership, Tests, Dokumentzielen,
  Commit- und Rückgabeformat angelegt.
- Kein Namespace-Inhalt gelesen, kein Produktcode geändert, kein Agentenlauf
  gestartet und kein Commit erstellt.

## 2026-08-25 02:51:08 +02:00 – PLAN-EXEC-002: Traceability und Commit-/Push-Gates vollständig vorbereitet

- Aktive Triggerunterlagen vollständig gegeneinander auditiert und
  Traceability auf 129 eindeutige Summary-/Einzelanforderungen erweitert.
- Live-/Early-Final-Parallelität normativ eingefroren; Wake-Auswahl,
  Activation-Admission/-Sequence, Command-Korrelation und
  Pending-Snapshot-Sortierung eindeutig gemacht.
- Hotkey-Kollision sowie Wake-Cooldown-/Pre-Roll-Kalibrierwerte sichtbar als
  spätere technische Entscheidungen erhalten.
- Vorhandenen lokalen Server-Feature-Branch samt unverändertem geerbtem
  Baseline-Diff bestätigt und GitHub-Remote des Serverrepositorys ergänzt.
- Repositorylokale AP-Akten und genau ein finaler AP-Commit festgelegt:
  Agent commit lokal, Korrektur per Amend, Root-Endabnahme im selben Commit,
  Push erst nach PASS.
- Kein Namespace-Inhalt gelesen, kein Produktcode verändert und noch kein
  Implementierungsagent gestartet.

## 2026-08-25 03:28:14 +02:00 – EXEC-W1-001: Baselinewelle abgenommen und gepusht

- Serverbaseline `AP-SRV-000` nach Agentenkorrektur und unabhängiger
  Root-Validierung (`3 passed`; Vollsuite `492 passed, 13 skipped`) als
  `71a35e074eb90d75f8f91f5ed7cb46accd4b6498` auf den Server-Feature-Branch
  gepusht.
- Clientbaseline `AP-CLI-000` nach dokumentierten Claude-Code-Korrekturen und
  unabhängiger Root-Validierung (`24 passed`; Vollsuite `1192 passed`) als
  `042fcd203c873d6f84a270413c47bc5da1fbf1ed` auf den Client-Feature-Branch
  gepusht.
- Beide APs besitzen eine vollständige Akte und genau einen abgenommenen
  Commit. `AP-SRV-010` ist als nächstes Paket freigegeben; `AP-CLI-010` bleibt
  bis zum PASS von `AP-SRV-040` blockiert.

## 2026-08-25 03:55:20 +02:00 – EXEC-SRV-010-START: State-Machine-Paket gestartet

- AP-SRV-010 auf der GPT-Lane gegen
  `71a35e074eb90d75f8f91f5ed7cb46accd4b6498` gestartet.
- Datierten Serverplan und vollständige AP-Akte vor Umsetzung angelegt;
  Originalprompt-SHA-256:
  `3A7A3AA0D84AC59C6509B334275F8AC66816D307491B4D2A84E4280F7AFEC073`.
- Claude wegen des gegenüber dem letzten Baselinelauf höheren
  Architekturaufwands und des verbleibenden Zeitbudgets nicht eingesetzt.
- Client-Lane bleibt bis AP-SRV-040 dependency-bedingt frei.

## 2026-08-25 04:31:35 +02:00 – EXEC-SRV-010-001: State Machine abgenommen und gepusht

- AP-SRV-010 nach einer dokumentierten Korrekturrunde und vollständiger
  Alt→Neu-Zuordnung aller 41 Controller-Baselinetests abgenommen.
- Root-Nachweise: fokussiert `101 passed, 15 subtests passed`, Vollsuite
  `490 passed, 13 skipped`, Range-Diff-Check PASS, genau ein AP-Commit.
- Freigegebener Server-SHA:
  `3262079c62c58677cfd6506cd09d020b5b27ef44`.
- AP-SRV-020 ist READY; AP-CLI-010 bleibt bis AP-SRV-040 blockiert.

## 2026-08-25 04:42:48 +02:00 – DOC-RESUME-001: Kontextunabhängigen Wiedereinstieg gehärtet

- Veraltete Einstiegsaussagen in Arbeitsblock-README, `task.md`,
  `ÜBERGABE.md` und kompakter Projektübersicht gegen den tatsächlichen
  AP-/Dependency-Stand korrigiert.
- Neue kanonische Übergabe `NACHVERFOLGUNG/WIEDEREINSTIEG.md` dokumentiert
  beide Repositories, Branches, freigegebene Produkt-SHAs, Lesereihenfolge,
  AP-SRV-020-Grenzen, Testbefehle und Gateprozess ohne Chatkontext.
- Struktur-/Statusquellen bleiben getrennt; kein Produktcode und kein
  IDEEN-/Namespace-Inhalt geändert oder ausgewertet.

## 2026-08-25 04:46:30 +02:00 – EXEC-SRV-020-START: Segmentledger-Paket gestartet

- AP-SRV-020 auf der GPT-Lane gegen
  `3262079c62c58677cfd6506cd09d020b5b27ef44` gestartet.
- Datierten Plan und vollständige Serverakte vor Umsetzung angelegt;
  Originalprompt-SHA-256:
  `B43DA4544262C5A3CDCB049AE14F89B26AFA222662DB1531FD6E1AA4A1B76B6A`.
- Scope auf Ledger, unveränderliche Finaljobkontexte, Exactly-once-Terminals,
  geordnete Publikation und vollständige Faultterminalisierung begrenzt;
  Folgepakete und Clientcode werden nicht vorweggenommen.

## 2026-08-25 05:38:46 +02:00 – EXEC-SRV-020-001: Segmentledger abgenommen und gepusht

- AP-SRV-020 nach einer dokumentierten Root-Korrekturrunde gegen zwei
  reproduzierte Nebenläufigkeitsbefunde abgenommen.
- Korrigiert sind die sessionsweite sichtbare Dispatchreihenfolge und das
  atomare Cancel-all ohne Freigabe vorbereiteten späteren Texts.
- Root-Nachweise: fokussiert `108 passed, 9 subtests passed`, Vollsuite
  `507 passed, 13 skipped`, Range-Diff-Check PASS, genau ein AP-Commit.
- Freigegebener Server-SHA:
  `8535ee79bb2d898d9897e91b57d6a735c479edf0`.
- AP-SRV-030 ist READY; AP-CLI-010 bleibt bis AP-SRV-040 blockiert.

## 2026-08-27 – NACHTRAG (rekonstruiert): AP-SRV-030 und AP-SRV-040

```text
Nachtrag am 2026-08-27 erstellt.
Historische Zeitpunkte aus Git-Metadaten rekonstruiert.
Append-only-Reihenfolge wurde nicht umgeschrieben.
```

Die detaillierte Chronik dieser Datei endete bisher bei `AP-SRV-020`
(2026-08-25 05:38:46 +02:00). `AP-SRV-030` und `AP-SRV-040` wurden beim
vorherigen kanonischen Abschluss nicht nachgetragen. Diese Lücke wird hier
transparent geschlossen; frühere Einträge wurden dafür weder umsortiert noch
rückwirkend ergänzt.

**Zeitbasis.** Alle unten genannten Zeitpunkte stammen aus
`git show -s --format=%aI/%cI` im Serverrepository
(`voice-stt-server/workspaces/einheitliche-triggerarchitektur`), umgerechnet
auf Europe/Berlin. Eine Git-Commitzeit belegt den Commit- beziehungsweise
Closezeitpunkt, **nicht** den Startzeitpunkt des jeweiligen Agentenlaufs. Die
Startzeitpunkte der AP-SRV-030- und AP-SRV-040-Läufe sind weder aus Git noch
aus den archivierten Prompts/Reports belastbar ableitbar und werden deshalb
bewusst nicht angegeben.

### AP-SRV-030 – Commands und Timer (rekonstruiert)

- **2026-08-27 03:02:19 +02:00** – Execution-/Root-PASS-Source
  `325e55c186713069b25208871da4fef16470f85a`
  (Tree `ec5b6e0849bb7a0949ae5da05d168b8c19a4456e`, Parent
  `8535ee79bb2d898d9897e91b57d6a735c479edf0`),
  Commitbetreff `feat(trigger): implement AP-SRV-030 commands and timers`.
  Inhalt: semantische Commands und der eingefrorene, nicht kumulative
  Timervertrag; damit ist `FIND-010` (kumulative Extend-Semantik) geschlossen.
  Der Stand durchlief eine Root-Korrekturrunde und eine CI-Validierung auf
  Windows/Python 3.12 (Branch `review/AP-SRV-030/run-01`, CI-Provenienz
  `ci/AP-SRV-030-c3-validation`).
- **2026-08-27 06:52:23 +02:00** – kanonischer Archive-Complete-Close
  `b220dd03a594d2b9f8cad65fd279046be36864cc`
  (Tree `61c65f59b1778085affada90b66411e27ec1c004`, Parent
  `8535ee79bb2d898d9897e91b57d6a735c479edf0`),
  Commitbetreff `feat(trigger): canonicalize AP-SRV-030 commands and timers`.
  Produkt-, Test- und Dokustand identisch zur Execution-Source; zusätzlich
  ausschließlich Vervollständigung der Paketakte. `AP-SRV-040` freigegeben.

### AP-SRV-040 – Protokoll v2 (rekonstruiert)

- **2026-08-27 05:59:00 +02:00** – Root-geprüfter C3-Kandidat
  `6f73a4e347be51d02005e81a0c6be546f036deef`
  (Tree `6d36c2639a199c5bdd10a2c8dc1899d8261caee6`),
  Commitbetreff `fix(protocol): serialize AP-SRV-040 event dispatch`.
  Der Lauf umfasste drei Commits auf `review/AP-SRV-040/run-01`: C1
  Implementierung von Protokoll v2 (Handshake, Events, Snapshot), C2
  `stateVersion`-Härtung und C3 die gemeinsame Linearisierung von Projection,
  `eventSeq`-Mint und Sink-Übergabe.
- **2026-08-27 07:01:26 +02:00** – kanonischer Close
  `c0806e5bc5d503580070f2dacc88831d51447938`
  (Tree `e9a1a93aecf433941db91827393bc51afef4ebff`, Parent
  `b220dd03a594d2b9f8cad65fd279046be36864cc`; Autorzeit 07:00:16 +02:00),
  Commitbetreff `feat(protocol): canonicalize AP-SRV-040 protocol v2`.
  Außerhalb der Paketakten identisch zu C3. Nachweise: Vollsuite
  `779 passed, 14 skipped, 448 subtests`, C3-Event-Ordering `20/20`,
  `git diff --check` PASS. `AP-SRV-050` freigegeben.

**Reihenfolgehinweis.** Die Zeitstempel zeigen, dass der AP-SRV-040-Review
(C3, 05:59) auf der bereits abgenommenen AP-SRV-030-Execution-Source lief,
während der kanonische AP-SRV-030-Commit erst danach (06:52) erzeugt wurde.
Die kanonische Kette selbst ist davon unberührt linear:
`8535ee7…` → `b220dd0…` → `c0806e5…`.

## 2026-08-27 20:07:43 +02:00 – CANONICAL CLOSE AP-SRV-050

Zeitbasis: Git-Metadaten. C1/C2/C3 aus dem lokalen Reviewworktree
`workspaces/ap-srv-050` (`review/AP-SRV-050/run-01`), der kanonische Commit
aus dem Serverworkspace nach dem Push.

```text
C1  489ac23a192b2a64abbcdb6779ed132f159e4518  2026-08-27 10:58:11 +02:00
    Tree 17eeb88254809c535404c84872111241470f1010
C2  536ff67cda872b1449f88c5d99e8d8c3017139f4  2026-08-27 16:45:11 +02:00
    Tree 9ff02381fef0b6c8dd6e01482d4633e21ef56be4
C3  18b65216433329456946afd3c41d8df6bbd07d44  2026-08-27 18:33:02 +02:00
    Tree b0dec32ddde90052956165c249b313478c267773   (Root-PASS Source)

Canonical  c901cda3f2c19eeb78c468524161728498b6e27e  2026-08-27 20:07:43 +02:00
Tree       f81144a26f93fb3bc553ab5110d07197a473aa46
Parent     c0806e5bc5d503580070f2dacc88831d51447938
```

- **C1 Implementation.** Settings-Control-Plane: Registry mit
  key/scope/auth/type/constraints, Apply-Policies, sechs Activation-Timings,
  Wake-Sensitivity, Session-Wake-Auswahl und admin-geschützte
  Servereinstellungen.
- **C2 Root Findings F1–F6.** Härtung der Domainautorität, der getrennten
  Session-/Serverrevisionen, der `next_activation`-Latches, der
  `requested`/`effective`-Resyncbarkeit, der Persistenzvalidierung und des
  REST-/Auth-/Secret-Schutzes.
- **C3 Wire-Atomicity.** Settings-Patch, Wire-Mirror und `settings.changed`
  sind gemeinsam linearisiert; der Snapshot liegt auf derselben
  AP-SRV-040-Dispatchgrenze. Damit ist das in C2 nachgewiesene Wire-Race
  strukturell geschlossen.
- **ROOT PASS.** `F1`–`F6` PASS. Settings `120 passed`; Protocol v2
  `205 passed / 1 skipped / 281 subtests`; Activation/Timer
  `218 passed / 82 subtests`; Vollsuite `899 passed / 14 skipped / 448
  subtests`; C3-Races `20/20` (Snapshot/Patch) und `20/20`
  (settings.changed/Domain-Ordering). Zwei NON-BLOCKING Root-Notes: die
  byteidentisch archivierte C3-Promptdatei behält ihre
  Markdown-Hardbreak-Trailing-Spaces, und die committeten Red-Tests belegen
  den C2-Fehler, ohne als Scheduler-Beweis mathematisch vollständig zu sein.
- **Canonical Close.** Genau ein Commit auf `c0806e5…`; Produkt-, Test- und
  dauerhafte Dokumentation identisch zum Root-geprüften C3, zusätzlich nur die
  drei Root-Close-Dokumente der AP050-Akte. `git diff --check` meldet
  ausschließlich die bekannte archivierte Promptdatei; ohne sie ist der Lauf
  sauber.
- **SET-13a/SET-13b Ownership-Korrektur.** `SET-13` ist aufgeteilt in
  `SET-13a` (Settings-REST, AP-SRV-050) und `SET-13b`
  (`GET /api/v2/wake-words`, AP-SRV-060); die Anforderungszahl steigt von 129
  auf 130. `WW-09`, `WW-15`, `WW-18` und `WW-19` führen `SRV-050` nicht mehr.
- **Prep-Provenienz.** Die textuelle Server-Vorbereitung vom 2026-08-25 ist
  byteidentisch gesichert unter
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-25_TRIGGERARCHITEKTUR_SERVER_PREP/`
  (19 Dateien, `SHA256SUMS.txt`, 0 Abweichungen). Ausdrücklich **nicht
  normative** Prep-Provenienz; das Original unter `_PREP\SERVER` bleibt
  bestehen.
- **AP-SRV-060 NEXT** auf `c901cda…`; `AP-CLI-010` bleibt bewusst deferred.

## 2026-08-29 09:09:02 +02:00 – CANONICAL CLOSE AP-SRV-060

Zeitbasis: Git-Metadaten. C1/C2/C3/Asset-Finalisierung/Final Repair aus dem
lokalen Reviewworktree `workspaces/ap-srv-060` (`work/AP-SRV-060/C3`), der
kanonische Commit aus dem Serverworkspace nach dem Push.

```text
C1             548057e96a8a722c84d9a43451577a4415bcd7b1  2026-08-28 01:47:40 +02:00
               Tree 8751ef47ab17a6c5a1359d75f08fcd18358c5003
C2             5e429d6227d6a4660b79c432aa934318e293ecfd  2026-08-28 07:03:33 +02:00
               Tree ac278c4649e64793bdf938a0a41e484209d882ff
C3             d681afa4580bc8d769777b4fe45a36e3cfc6987a  2026-08-28 17:40:57 +02:00
               Tree 7610f208fefdd890556e0f9a557b377095c5ad4c
Asset-Final    abf8e6207d0019018f55ce4dcf57f81328c4cb5a  2026-08-28 20:50:02 +02:00
               Tree 0276f5752ac918b3e28e15e14d7f11c91182f248
Final Repair   2b08e379a36590c99e48e59c81a39418395d9742  2026-08-28 21:53:54 +02:00
               Tree de6fe364545b508a47a87ead67a01c5732477e71   (Root-PASS Source)

Canonical      c82923fc6ce889b4dfbbde1f9877b8b76481a1e8  2026-08-29 09:09:02 +02:00
Tree           de6fe364545b508a47a87ead67a01c5732477e71
Parent         c901cda3f2c19eeb78c468524161728498b6e27e
```

- **C1 Implementation.** Wake-Word-Katalog, `models.json`, Initialisierung,
  Detection-Adapter, `GET /api/v2/wake-words`, `POST /api/v2/wake-words/refresh`,
  Session-Admission, `wakeWord.cooldownMs`/`preRollMs`. Von Root mit Findings
  F1–F10 abgelehnt (`ROOT FAIL`).
- **C2 Root Findings F1–F10.** Wire-Kanonizität, Runtime-Binding für
  `next_activation`, Admission-Ladbarkeitsprobe, Refresh-Atomizität,
  Revisionstracking, Latch/Window-Trennung. Von Root mit Findings F11–F15
  abgelehnt (`ROOT FAIL`).
- **C3 Root Correction F11–F15.** `WakeHitTracker` mit Score-Schwelle,
  `minConsecutivePredictionFrames`, First-finalized-wins, Trailing-Edge-
  Finalisierung, operationaler Nullpunkt, Single-Backend-je-Engine-Policy,
  Exactly-once Eventing (`wakeword.detected`), per-Backend Loadability-Probe.
- **Asset-Finalisierung & Final Root Repair.** Dual-Backend-Artefakte
  (TFLite neben ONNX) im Buildkatalog gebündelt, Manifestgenerator gehärtet,
  F3-Admission-Regressionstest ergänzt.
- **ROOT PASS.** Full Suite: `1180 passed, 14 skipped, 762 subtests, 0 failed`.
  Empirische Kalibrierung (`WW-18`, `WW-19`) bleibt ehrlich als
  `EVIDENCE_BLOCKED / calibration pending` ausgewiesen (lokal kein reales
  Positivmaterial). Das blockiert AP-SRV-060 ROOT PASS nicht.
- **Canonical Close.** Genau ein Aggregate-Commit auf `feat/einheitliche-triggerarchitektur`
  mit Parent `c901cda…` und Tree `de6fe364545b508a47a87ead67a01c5732477e71`
  (identisch zum Root-Source-Stand `2b08e37…`).
- **AP-SRV-070 NEXT** auf `c82923f…`; `AP-CLI-010` bleibt bewusst deferred.

## 2026-10-11 – CLIENT-V2-START-001: gemeinsame Planungs-/Umsetzungslinie

- Auftrag: eigener Branch für vollständige Planung und Umsetzung, erster Commit nur Unterlagen, danach genau ein Code-/Unterlagencommit je AP; Bearbeitungen auf untergeordneten Branches.
- Basis/Ziel: `feat/client-v2` von `8bab1b3f4aa070d0756c305908def4d9ebc52582`; derselbe Baum wie Distributed a80a6b1. Vorhandene Vorarbeit und alte Branches bleiben erhalten.
- Unterlagen: vollständige eigenständige Planrevision 6 im aktiven Clientarbeitsblock, aktualisierte Rollen-Skills/Checklisten, Branch-/Planpflege, Matrix/Requirements und aktuelle Steuerungseinstiege. Herkunft über Importmanifest, Originalpräzisierung über BRANCHSTART belegt.
- Abgrenzung: kein Produktcode, keine CV2-000-Integration/-Abnahme, kein Server-/Mainmerge, kein Push. Serverada13b0 bleibt vorläufiges Finale auf Distributed, Restaggregation später gesondert.
- Prüfung: Dokument-/Quellen-/Vektoren-/Matrix-/Skillkonsistenz und Git-Diff/Scope gemäß Planungsprüfergebnis. Start-SHA aus dem ersten neuen Commit nach der angegebenen Basis ableiten; kein zusätzlicher SHA-Dokumentcommit.

## 2026-10-11 – CLIENT-V2-ROLLEN-001: klare Rollen und Paket-PR-Übergaben

- Auftrag: konkrete Lese-/Arbeitsanweisungen je Auftraggeber, Umsetzer und Reviewer aktualisieren.
- Vorbereitung auf work/client-v2/rollenworkflow vom Planungsstart b0525e6; feat/client-v2 unverändert.
- Inhalt: eigene Rollen-Einstiege, Checklisten, tatsächliche Gitrechte in Promptvorlagen, unabhängiger Reviewreport auf Paketbranch, Head-/PASS-Abgleich, serieller Vorgängercheck und menschlich freigegebener Einzel-Squash.
- Abgrenzung: keine Produkt-/Serveränderung, keine AP-Umsetzung/-Abnahme und kein Commit/Push/PR/Merge.
- Dokumentprüfung: siehe PLANUNG/EVIDENCE/ROLLENWORKFLOW_REV7.md und zugehöriges Prüfergebnis.

## 2026-10-11 – CLIENT-V2-ZUSTAENDE-001: nächster Schritt aus dokumentiertem Stand

Gemeinsamen Einstieg und Workflowrevision 8 ergänzt. Neuer Agent ermittelt AP/Rolle/Kandidat aus offenen Paketlinien, Status-/Runakten und kanonischem Gitverlauf. Festgelegte Workflowphasen mit Pflichtpflege in WORKFLOW_STATUS.json; initial nur AP-CV2-000-Planungsbereitschaft, kein Run/PASS/Freigabeprompt erfunden. Ein ausdrückliches Zusatzreview startet frisch, behält alte Berichte und berücksichtigt alle offenen Pflichtfindings. Menschliche Übernahmefreigabe bleibt getrennt. Unterlagen auf work/client-v2/rollenworkflow vorbereitet, feat/client-v2 unverändert; keine Produktimplementierung oder Git-Veröffentlichung.

## PLAN-CLIENT-V2-009 – 2026-10-11 – vollständiger Unterlagenstart zur Veröffentlichung

Auf ausdrücklichen Auftrag aktuellen vollständigen Unterlagensatz als Revision 9 im noch unveröffentlichten Startcommit von feat/client-v2 konsolidiert und dessen erstmaligen Push vorbereitet. Aktive Vorbereitungsbranch-/Importhinweise ersetzt, historische Prüfstände gekennzeichnet, erste Auftragsvorlage innerhalb des Plans ergänzt und initiale Selbst-SHA durch Gitauflösung ersetzt. Keine Produktänderung und keine AP-Abnahme. Alle Client-/Integrationspakete bleiben offen; Serverada13b0 bleibt gepinnte Distributedreferenz. Prüfdetails: PLANUNG/EVIDENCE/PRUEFBERICHT.md im aktiven Client-V2-Arbeitsblock. Tatsächliche Commit-/Remoteidentität wird nach Transport aus Git ermittelt.

## PLAN-CLIENT-V2-010 – 2026-10-11 – externe Prüffunde bewertet und korrigiert

Sechs Funde geprüft: konkrete Recovery-/Serverrouting-/Auswahlregeln ergänzt, reale Plattformbelege mit unabhängiger Validierung geregelt, vorhandene Ausnahme für spätere Korrekturen konkretisiert, COMPLETED samt Nachmerge-Beleg beschrieben. Versionsmetadaten und Basisschätzung präzisiert. Originalprüfbericht erhalten; dessen ungenaue Commitformulierung berichtigt. Reine Dokumentkorrektur auf work/client-v2/planung-rev10 ab bfade9d, keine Produktumsetzung/AP-Abnahme und kein Commit/Push/PR/Merge aus diesem Auftrag. Prüfdetails in PLANUNG/EVIDENCE/PRUEFBERICHT.md des aktiven Blocks.

## PLAN-CLIENT-V2-011 – 2026-10-11 – Revision 10 zur Veröffentlichung freigegeben

Auf Originalprompt „Go: Revision 10 als einen Dokumentkorrekturcommit auf `feat/client-v2` übernehmen und pushen.“ die vollständige Revision 10 und aktuelle Status-/Agenteneinstiege für genau einen zusätzlichen Dokumentcommit finalisiert. Erhaltener Parent bfade9d, Vorbereitung auf work/client-v2/planung-rev10, Übernahme nur fast-forward und normaler Push mit tatsächlicher Git-/Remoteprüfung. Benannte einmalige Dokumentausnahme vor AP-CV2-000; danach unverändert ein Aggregat je angenommenem AP. Kein Produktcode, keine AP-Abnahme und keine zukünftige Umsetzungsfreigabe. Originalauftrag und abschließende Dokumentprüfung liegen unter PLANUNG/EVIDENCE im aktiven Client-V2-Block. Endgültige Commit-/Transportidentität wird nach Ausführung außerhalb des Commitinhalts gesichert.

## AP-CV2-000-R01 – 2026-10-11 – integrierte Feature-/Releasebasis REVIEW_READY

Auf tatsächlichen nächsten-Schritt-Auftrag Revision-10-Spitze 050e776cf316eb332177294db0c0a2719c2b4415 und fehlende offene Paketlinien geprüft; Rolle Umsetzer. Featurelinie erhalten und kompatible Release-f625904-Änderungen in voice_stt_client portiert. Kandidat ausschließlich auf work/client-v2/ap-cv2-000; ursprüngliche Arbeitsfreigabe in Runakte/workAuthorization gesichert. Baselines Feature1192/Release1147 (Release-pytest-Sammlungsfehler separat), integrierte pytest-/Unittestregression je1221 grün; Wheel-/sdist-Installation außerhalb Checkout qualifiziert. Kein V2-Lifecycle, Eigenreview, Servereingriff oder kanonischer Merge. Nächste Aktion frische unabhängige Abnahme; danach PASS, menschlicher Prompt und Einzelaggregat vor CV2-010. Paketakte: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md`. Endgültige Kandidaten-/PR-Identität aus Git nach Sicherung sämtlicher Akten, kein Selbst-SHA.

## AP-CV2-000-R02 – 2026-10-11 – unabhängige Abnahme: CHANGES_REQUIRED

Paket-PR #2, Reviewerrolle in frischer Session, Kandidat `8b1c4c157b6b431dac6af69e2e264d0c37579bef`, Tree `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e`, Parent `050e776cf316eb332177294db0c0a2719c2b4415`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Git-/Branchprovenienz abgeglichen; GitHub-Actions-Job 114487166298 in Run 38145266161: 1221 Unittests und Packaging-Smokes PASS (externe CI, keine eigenen Tests). Statischer Kontrollflussbefund **CV2-R02-F01**: `voice_stt_client/ui/application.py` speichert Ersatzhotkey vor dem Erfolg von `bridge.start()`; persistente Benutzerpräferenz kann sich trotz Startfehler ändern. Unabhängige vollständige Windows-/Qt-Regression auf exaktem SHA **NOT_RUN**; daher kein ROOT_PASS. Reviewakte: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R02-ABNAHME/01_REPORT.md`. Nächste Aktion Korrekturlauf im selben PR, danach neue unabhängige Abnahme. Keine Produkt-/Testdateien verändert, keine kanonische Übernahme.


## WF-CLIENT-V2-ABLAGE-001 – 2026-10-11 – lokale Belegübergabe für den offenen Paket-PR

Auf Nutzerkorrektur die zwölf ergänzenden Workflow-Auditdateien in den Client-V2-Workspace übernommen; zusätzlich den früheren vollständigen Themenbestand mit 6.355 Dateien als hashgeprüftes, auf drei Git-taugliche Teile verteiltes Provenienzarchiv erhalten. Originalquellen nicht gelöscht oder geändert. Aktuellen Korrekturprompt, Ablagehinweise und Dateimanifest auf repositoryinterne Übergabe umgestellt. Der externe Workflow-Tools-Ordner ist keine operative Quelle mehr. Einstieg: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/KORREKTURPROMPT_AP_CV2_000.md` sowie `README.md` im selben Ordner. Alles lokal vorbereitet, kein Commit, Push oder separater PR. Der beauftragte Korrekturagent übernimmt den vollständigen Satz zusammen mit seinen Korrekturen in den bestehenden AP-CV2-000-PR #2 und weist anschließend die Onlinevollständigkeit nach. Feature050e776 und Paket-/Reviewurteil unverändert; keine Produktkorrektur oder Abnahme aus dieser Ablagevorbereitung.


## AP-CV2-000-R03 – 2026-10-11 – Korrektur und erneute Einreichung

R02-Spitze2dc251d sicher übernommen; F01 mit realem isoliertem Profil reproduziert und Start-Persistierung gezielt korrigiert. Drei R02-Links und aktiver Manifeststatus berichtigt; unabhängiger Testweg und strukturelle Übergaben präzisiert, gemeinsamer V2-Aktenprüfer qualifiziert. Vollständiger vorbereiteter Belegsatz mit drei Archivteilen/6355 Quellen in demselben Paket-PR aufgenommen. [R03-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md) führt Selbsttests/Builds und tatsächliche Remotebereitstellung. REVIEW_READY, frischer unabhängiger Vollreview und F01-Recheck offen; Schreibrecht nach Übergabe pausiert. Featureparent050e776 unverändert, keine Übernahme oder Folgepaketfreigabe.

## AP-CV2-000-R04 – 2026-10-11 – unabhängige Folgesichtung / BLOCKED

Reviewer prüfte PR #2 `cd872d4bfa8eccd0167337cbab16a572ca70bfd4` Tree `6aff2fa629b0c01fde502c345e7e31035cee0926` gegen Parent `050e776cf316eb332177294db0c0a2719c2b4415`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. R02-F01 im korrigierten `ui/application.py` fachlich geschlossen: provisorischer Hotkey erst nach erfolgreichem Corestart persistiert, Fehlerrollenback und neue Negativtests vorhanden. Externe GitHub-Windows-CI 38163179818 mit 1233 Unittests, compileall, EXE/Qt und Packaging/Install-Smokes PASS auf kandidatenidentischem Testmerge 5bb8fed. Eigene volle Windows-Clientregression **NOT_RUN** wegen fehlendem passenden Prüfhost; `ROOT_PASS` ausgesetzt, Blocker R04-T01. Änderungen an Workflow-/Arbeitsunterlagen auf ausdrückliche Nutzeranweisung nicht bewertet. Akte `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R04-ABNAHME/01_REPORT.md`. Kein Produktfix, kein Merge, kein Folgepaket.

## WF-CLIENT-V2-R05-WINDOWS – 2026-10-11 – Testblocker geschlossen und Abschluss beauftragt

R04 gelesen; einziger Blocker R04-T01. Sauberer Detached-Checkout7c4bb2f, codegleich zu R04cd872d4: vollständige Windows-Suite1233 PASS, Startup-Persistenz5 PASS, compileall/Diffprüfung PASS, keine Produktänderung. Nutzerauftrag zu Kandidatenpush/anschließender Einzelübernahme und neuer Testverantwortung in R05 gesichert. Windows-Vollsuite künftig Umsetzungspflicht, ChatGPT-Reviewer prüft Code und gültige Belege ohne Pflichtwiederholung; Rollenregeln Version7 bei Planrevision10. R01–R04 erhalten. ROOT_PASS; finale CI und tatsächliche Einzel-Squash-Provenienz vor CANONICALIZED noch ausstehend. Belege: CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md.


## AP-CV2-010-R01 – 2026-10-11 – Codecqualifikation und REVIEW_READY

Aus tatsächlicher kanonischer AP000-Basis1cf076b: immutable V2-Wirecodec, bytegleiche Originalvektoren, vollständige Fixtures und echter gepinnter Servercheckpoint. Windows1263 Tests, Codec30 Tests, Server188 Checks PASS; individuelle WIRE-01..17-Belege, APIs und Akte aktualisiert. [R01-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), PR #3 gegen feat/client-v2. Unabhängiger Review als nächste Aktion, Paketbranch ab Übergabe pausiert. Keine eigene Abnahme/Promotion und kein Folgepaketstart.

## AP-CV2-010-R02 – 2026-10-11 – unabhängige technische Abnahme ROOT_PASS

Unabhängiger commitgebundener Vollreview des PR #3: `7124e5629e24817dd711b2e2b697b9c07aa11dd7`, Tree `37b61ff4cab90c18abf8e5bfae920f2e265ad3ab`, Parent `1cf076bd2ed56929b1a3780bc140da51348a8295`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Produkt-/Testdiff, WIRE-01..17, 30 Codec-Tests, 1263 Windowsvollsuite, 188 gepinnte Serverchecks, Originalvektoren und finale GitHub-CI unabhängig validiert; keine Pflichtfindings. Windows/HW durch Reviewer selbst NOT_RUN (gültige Fremdevidenz). [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/RUNS/R02-ABNAHME/01_REPORT.md). Paketstatus ROOT_PASS, Workflow WAITING_FOR_APPROVAL; keine Übernahmefreigabe und kein Merge, AP020 nicht gestartet.

## 2026-10-12 – AP-CV2-020 R01 / REVIEW_READY

V2-Transport/Hello/Commandkorrelation auf Paketbranch vom AP010-Aggregat91065f5.
Windows1290, targeted57, echter Servercheckpoint21/46 bytegeprüfte Quellen,
compileall PASS auf `7546298f26e00b83ad4c9510a9b8c1e7e6726fc3`. PR #4 nach feat/client-v2; Originalauftrag,
Report/Traceability/Belege vollständig. Frische unabhängige Abnahme folgt;
Schreibhoheit pausiert, keine Paketpromotion oder Folgepaketimplementierung.
[Runreport](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md).

## AP-CV2-020-R02 – 2026-10-12 – unabhängiger Review: CHANGES_REQUIRED

Unabhängiger SHA-gebundener Review von PR #4 auf `2b79a9a23a6be554a2a2a05ff3256a63ccf022d4`, Tree `647a0b4070d666e37b475841d094d4e37cc43e40`, Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Server ada13b0. Umsetzerbelege (1290 Windows, 57 targeted, 21 echter Servercheckpoint) validiert: PASS; Reviewer-Windowsvollsuite NOT_RUN gemäß Reviewregel. Pflichtbefunde CV2-020-R02-F01 (HTTP-Upgrade-Fehler verlässt den Reconnectloop) und F02 (4408-Zähler wird bei READY nicht zurückgesetzt). [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-020/RUNS/R02-ABNAHME/01_REPORT.md). Kein ROOT_PASS, keine Übernahme; Korrektur im bestehenden PR, danach neue Qualifikation/Review.


## 2026-10-12 – AP-CV2-020 / R03-KORREKTUR – REVIEW_READY

F01/F02 dynamisch bestätigt und gezielt korrigiert (HTTP-Upgrade-Recovery, 4408-Episodenreset erst nach READY). Kandidatenqualifikation `98ab3c0fc5c935019d81d6d6acb1423185cb4793` / `c394dbe3d75086132234cb987469ee6639647af6`:1294 Windowsgesamt-,61 gezielte Tests,21 Serverfälle/46 bytegeprüfte Quellen und compileall PASS. [Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-020/RUNS/R03-KORREKTUR/01_REPORT.md). R02-Findings bleiben bis unabhängiger Abnahme offen; PR #4, keine Übernahme/kein Folgepaket.

## AP-CV2-020-R04 – 2026-10-12 – unabhängige Abnahme ROOT_PASS

Review auf `6d74c1ae06643e026834bc9164028bec908e26df` (Tree `f8a57f79c6bf61d7b079a41a53662adeac34c546`), Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Server ada13b0. R02-Pflichtfindings CV2-020-R02-F01 und -F02 im korrigierten Code plus 4 neuen Regressionstests sowie Vorher-Repros unabhängig geschlossen. Windows1294, targeted61, echter gepinnter Server21/46 Quellblobs, compileall und SHA256 aller Pflichtlogs als vollständige Fremdevidenz unabhängig validiert; GitHub-CI 38183803142 auf exakt submitted Head erfolgreich. Alle28 Paket-Requirements und kumulativer Code-/Testdiff geprüft, kein neuer Pflichtbefund. [R04-Bericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-020/RUNS/R04-ABNAHME/01_REPORT.md). Status ROOT_PASS / WAITING_FOR_APPROVAL; keine menschliche Freigabe und kein Merge/Folgepaket.

## AP-CV2-030-R01 – 2026-10-12 – Mirror und Resync / REVIEW_READY

Von AP020-Aggregat8fa0f82 nach belegtem unabhängigen PASS, menschlicher Freigabe und Baumgleichheit: reiner Mirror, sichere Segment-/Terminal-/Settingsprojektionen und tatsächliche V2-Transport-/Snapshotanbindung. Alle35 Requirements einzeln verknüpft.1339 Windowsgesamttests,106 gezielte Tests,35 echte Serverchecks/46 Quellblobs und compileall PASS; exakte Basis/Produktdiff/Gitblobs und vollständige Logs gesichert. [R01-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-030/RUNS/R01-UMSETZUNG/01_REPORT.md). Keine eigene Abnahme, Promotion oder Folgepaketimplementierung; Schreiben ab Übergabe pausiert.

## AP-CV2-050-R01 – 2026-10-12 – Controls/Runpausen/Win32 / REVIEW_READY

Nach tatsächlicher AP040-Übernahme (PR6, PASS/Freigabe/Singleparent/Baumgleichheit belegt) von 4eb1161 umgesetzt: quellenneutraler Controlservice, ursprüngliche IDbindung, vollständige getrennte Runpausen und atomare Win32rollenregistrierung.1397 Windowsgesamttests,297 gezielte Tests,79 echte Serverchecks/46 Quellblobs,16 native Windowschecks, compileall/diffcheck PASS. Alle14 Requirements einzeln belegt. [Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/01_REPORT.md). Unabhängige Abnahme offen; Schreiben ab Übergabe pausiert, keine kanonische Übernahme oder Folgepaketimplementierung.


## AP-CV2-060-R01 – 2026-10-12 – Final-Pipeline/Historymigration / REVIEW_READY

Von AP050-Aggregat ce95c66 nach belegtem PASS/Freigabe/Singleparent/Baumgleichheit umgesetzt: UUID-Herkunft, unabhängiger Prozessdedup, transaktionale V1-Migration/Backup/Rollback und reservierte automatische/manuelle Ausgabe mit Crashstatus unknown. 1426 Windowsgesamttests, 323 gezielte Tests, 19 echte Serverchecks/46 Quellblobs, compileall/diffcheck PASS. Alle13 RESULT-Requirements einzeln belegt. CI-Pfadaliasfehler in neuer Backupfixture vor endgültiger Übergabe reproduziert/korrigiert und sämtliche Qualifikationschecks mit neuem Testblob wiederholt. [Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/01_REPORT.md). Unabhängige Abnahme offen; Schreiben ab Übergabe pausiert, keine kanonische Übernahme oder Folgepaketimplementierung.


## AP-CV2-060-R02 – 2026-10-12 – unabhängige Abnahme CHANGES_REQUIRED

PR #8 Kandidat `33fef1d892917030100c0583566367f49fff14eb`, Tree `b725d2e467a479de8ce778646eebbe71a4ec67b5`, Parent ce95c66 und Server ada13b0 geprüft. 1426 Windows-Tests, 323 gezielte Tests, 19 echte Serverchecks und finale CI38268881303 als gültige extern durchgeführte Belege bestätigt. Ein Pflichtfinding `CV2-060-R02-F01`: API-Dokumentation nennt `ClientController.attach_v2_results`, tatsächlich implementiert ist `STTController.attach_v2_results`. [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R02-ABNAHME/01_REPORT.md). Keine Produktänderung oder Merge; Docfix und unabhängiger Recheck erforderlich.


## AP-CV2-060-R03 – 2026-10-12 – API-Dokumentnamen / REVIEW_READY

Reviewunterlagen ad10869 übernommen. Berechtigtes F01 reproduziert und ausschließlich ClientController → STTController in öffentlicher API korrigiert. Alle195 Produkt-/Test-/Configblobs und Pflichtloghashes unverändert, Docdiff/Kriterien-/Aktenprüfung PASS. Neue lokale Vollsuite NOT_RUN gemäß ausdrücklicher R02-Regel. [R03-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R03-KORREKTUR/01_REPORT.md). Erneute unabhängige Nachprüfung, kein Eigen-PASS/Merge/AP070; Schreiben ab Übergabe pausiert.


## AP-CV2-060-R04 – 2026-10-12 – unabhängige Nachabnahme ROOT_PASS

PR #8 am Kandidaten `1d81bb0230cfc5a099b7870488f6b42cd4735d5a` (Tree `f3342625d63ec0c296d62d03decb54ea93fd983b`, Parent ce95c66, Server ada13b0) geprüft. R02-Pflichtfinding `CV2-060-R02-F01` zur öffentlichen Controllerklasse durch R03-Einzeilen-Dokumentkorrektur unabhängig geschlossen. Von R02 bis R03 ausschließlich Dokument-/administrative Änderungen, keine Produkt-/Test-/Config-/Vertragsänderungen. R01-Windows 1426 / targeted 323 / gepinnter Servercheckpoint19 sowie alle 195 qualifizierten Produktblobs als gültige externe Belege unabhängig geprüft; eigene Windows-Wiederholung NOT_RUN (regelkonform). GitHub CI38274673106 am exakten Kandidaten mit kompletter Suite, EXE, Wheel und Smokes SUCCESS. Alle13 RESULT-Requirements ROOT_PASS; keine offenen Pflichtfindings. [R04-Bericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R04-ABNAHME/01_REPORT.md). Workflow WAITING_FOR_APPROVAL; kein Merge oder AP070 ohne menschlichen Prompt.


## AP-CV2-060-R05 – 2026-10-12 – ausdrückliche konditionierte Mergefreigabe

Menschlicher Originalauftrag sichergestellt: „Nach erfolgreicher CI wird die Freigabe zun Merge von PR #8, Arbeitspaket AP-CV2-060 erteilt. Bitte führe den Merge durch.“ [R05-Original](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R05-UEBERNAHME/00_PROMPT_ORIGINAL.md), [R05-Vorprüfung](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R05-UEBERNAHME/01_REPORT.md). Technischer R04-ROOT_PASS, Base ce95c66 und CI38276463113 SUCCESS auf `8eb26bae17b46651014d28183f5a9135f36b72af`. Workflow READY_FOR_CANONICALIZATION. Vor Durchführung des genau einen GitHub-Squash erneute CI/Head/Base-/Admin-Diff-Gates prüfen. Kein bereits erfolgter Merge, kein AP070.


## AP-CV2-070-R01 – 2026-10-12 – Settings/Profilmigration / REVIEW_READY

Von tatsächlichem AP060-Aggregat473a75d nach geprüftem PASS/Prompt/Singleparent/Treegleichheit umgesetzt: versioniertes Profil/Backup/Reparatur, dynamischer Katalog, getrennte Revisionsräume und bestätigter NA-Bootstrap vor Audio. 1460 Windowsgesamttests,243 gezielte Tests,38 echte HTTP/WS/Media/PCM-Checks,55 gepinnte Settings/Wake-Supplementtests ohne Skips, compileall/diffcheck PASS. 34 neue Tests;29 Anforderungen einzeln belegt. [R01-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/01_REPORT.md). Keine eigene Abnahme/Promotion/AP080; Schreiben ab Übergabe pausiert.


## AP-CV2-080-R01 – 2026-10-12 – Settings-UI/Admin/Vault/Apply / REVIEW_READY

Vom tatsächlich übernommenen AP070-Aggregat0c8d52d nach PASS/Freigabe/PR-/Parent-/Treeprüfung umgesetzt. Trigger-/Session-/Serveroberfläche, echte No-change-Adminprüfung, originbezogener Windowsvault, explizite Activation-/Drainentscheidungen, epoch-/generationgebundene Requests und bestätigte Profilmigration. 1513 vollständige Windows-Tests, 296 gezielte Regressionen, 53 neue Tests, echte UI27/native29/Settings38 sowie gepinnte Supplement55 ohne Skips; compileall/diffcheck PASS. [R01-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/01_REPORT.md). Zehn UI-Anforderungen einzeln belegt. Eigenprüfung SELF_CHECK_PASS, unabhängige Abnahme offen; kein Merge/AP090. Appkomposition AP100, reale ASR/Hardware AP-IV2-020, Server-Distributed offen. Nach Übergabe Schreiben pausiert.

## 2026-10-13 – AP-CV2-080: unabhängige technische Abnahme R02

PR #10, geprüfter Kandidat `eafd918f456551af694ede4af472ed4515b9fdd6`, Tree `960270c3f786433967aee7b16333be70f41427fe`, kanonischer Parent `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`: **ROOT_PASS** für UI-01 bis UI-10 ohne offene Pflichtfindings. Code-/Parentdiff und neun gepinnte Blobidentitäten unabhängig geprüft; vollständige 1513 Windows-Tests, 296 gezielte, reale Settings38/UI27/native29 und 55 gepinnte Serverchecks ohne Skips als Fremdbelege verifiziert, eigene Windows-Wiederholung NOT_RUN. GitHub-CI auf geprüftem Head grün. [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R02-ABNAHME/01_REPORT.md). Workflow WAITING_FOR_APPROVAL; menschliche Übernahme offen, kein Merge/AP090.

## 2026-10-13 – AP-CV2-080: menschliche Squash-Freigabe gesichert (R03)

Nach unabhängigem [R02-ROOT_PASS](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R02-ABNAHME/01_REPORT.md) hat der Auftraggeber [PR #10](https://github.com/marcosudau-vps/voice-stt-client/pull/10) ausdrücklich zum Merge freigegeben. [Originalprompt](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md), [R03-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R03-UEBERNAHME/01_REPORT.md). Freigegebener Head `777c8e23f531e24532e78312365798bc83f2234c`, Parent `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`, CI #38321633045 PASS. Workflow READY_FOR_CANONICALIZATION, noch kein Merge im vorgezogenen Report. Squash benötigt neue CI sowie Head-/Parent-/Treeprüfung; kein AP090-Autostart.

## 2026-10-13 – AP-CV2-090 / R01-UMSETZUNG

Quellenneutraler V2-Feedbackpfad auf Paketbranch aus AP080-Aggregat 1bc5be8; 1552 Windows-/377 gezielte Tests und 18 reale gepinnte Domain-/Log-/Qtchecks PASS. [Runreport](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/01_REPORT.md). REVIEW_READY, unabhängige Abnahme und menschliche Übernahme offen; kein AP100-/Serverabschluss.


## AP-CV2-100-R01 – 2026-10-13 – Desktopkomposition / REVIEW_READY

Vom kanonischen AP090-Parent dad89bb nach belegtem unabhängigen PASS, menschlichem
Prompt und Single-Parent-/Baumgleichheit. Gemeinsamer V2-Desktop-/Core-/Media-/Settings-/
Result-/Feedbackfluss, Workerpersistenz und kontrollierter Rollback/Shutdown.
1573 Windows-/ 190 gezielte Tests, 17 echte komponierte Serverchecks,
compileall/diffcheck PASS. Unabhängige Abnahme offen, Umsetzungsschreiben ab Abgabe
pausiert; keine kanonische Übernahme oder AP110-Implementierung.

[Runreport](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/01_REPORT.md).

## 2026-10-13 – AP-CV2-100 / R02-KORREKTUR: CI-01

CI-Replaytimeout bei 281-ms-Runnerverzögerung reproduziert; Testfristen für
durable Cursor-IO korrigiert, 280-ms-Regressionsfall ergänzt, fachliche Assertions
erhalten und erweitert. Windows1574/gezielte203/Servercheckpoint17/compileall
PASS, kandidatgebundene vollständige Logs. [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md).
REVIEW_READY im Selbstcheck; tatsächliche Übergabe erst nach grüner finaler PR-CI.
Keine Eigenabnahme, kanonische Übernahme oder AP110.

## 2026-10-13 – AP-CV2-100 / R03-ABNAHME

Unabhängiger Review von PR #12 (Kandidat `4a35a2d7eba5fa55e79528744320419b8ec0a1b3`): Windows-Vollsuite 1574, gezielte 203, Servercheckpoint 17 und finale CI 38347923728 als fremde PASS-Nachweise geprüft; sechs qualifizierte Gitblobs individuell gegen GitHub abgeglichen. **CHANGES_REQUIRED** wegen `CV2-100-R03-F01`: bestehende Settings-OBS-Audit-/Korrelationsereignisse werden im tatsächlichen V2-Desktop/Core-Apply nicht erzeugt. [R03-Abnahmebericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md). Reviewer keine eigene Windows-Suite, keine Produktcodeänderungen. Korrektur und erneute unabhängige Abnahme auf demselben PR; kein Merge/AP110.

## 2026-10-13 – AP-CV2-100 / R04-KORREKTUR: F01

R03-Reviewakte fetch/ff-only übernommen. Fehlende korrelierte Settingsaudits
im tatsächlichen V2-Desktop/Bridge/Core reproduziert und minimal ergänzt; sieben
Positiv-/Negativ-/Rollback-/Busy-/Shutdown-/Ingressfälle hinzugefügt.
Windows1581/gezielte210/Servercheckpoint17/compileall/diffcheck PASS; neue
Kandidaten-/Log-/Gitblobbindung. [R04-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md).
REVIEW_READY im Selbstcheck, tatsächliche Übergabe nach finaler grüner CI.
R03-CHANGES_REQUIRED historisch erhalten; frischer Gesamt-Review offen, kein Merge/AP110.

## 2026-10-13 – AP-CV2-100 / R05-ABNAHME: unabhängiger ROOT_PASS

PR #12 nach R04-Korrektur vollständig gegen Parent dad89bb5d und Kandidat `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` überprüft. F01 (korrelierte V2-Settings-Audits) nach realer Qt/Core/Bridge-Faultinjection und Red/Green-Tests unabhängig geschlossen, keine neuen Pflichtfindings; FINAL-01/02 und RUNTIME-01..04 technisch PASS. Externe Windows-Belege 1581/210 und gepinnte Servercheckpointfälle 17 sowie CI 38394758805 erfolgreich und unabhängig validiert. [R05-Bericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md). **WAITING_FOR_APPROVAL**, keine menschliche Mergefreigabe, kein AP110-Start.

## 2026-10-13 – AP-CV2-100 / R06-UEBERNAHME: menschliche Squash-Freigabe dokumentiert

Wörtlicher Auftrag „Hiermit wird die Freigabe zun Merge von PR #12, Arbeitspaket AP-CV2-100 erteilt. Bitte führe den Merge durch.“ als [Originalprompt](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R06-UEBERNAHME/00_PROMPT_ORIGINAL.md) gesichert. R05-PASS auf 0d45f8e9d3b484631da80be28f31c86ea85ab002; freigegebener Head 4c7be6945ae3f2c52748667963d00a1d5cd30d9f, kanonischer Parent dad89bb5d08e6d34abc5cfab57fc76010c5131dc. Finale PR-CI nach rein administrativem R06-Nachtrag nochmals erforderlich; ACCEPTED erst nach echtem Squash, Git-Parent- und Treeabgleich. Kein AP110-Vorgriff.

## 2026-10-14 – AP-IV2-010 R01 – REVIEW_READY

Paar Client0f0687c/Serverada13b0, Produkt unverändert ab43759d3. Windows1354, Server1964/14, Prozess11, Grenz17, Smokes7/7, compileall/diffcheck PASS. PR14; unabhängiger Review und spätere menschliche Übernahme ausstehend. Report: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md`. Kein Eigenreview/Merge/Folgepaket.

2026-10-15 AP-IV2-020/R01 Phase C: echte Manualbaseline und Followup3000/5000ms verglichen; Auftraggeber wählt5000ms. Sourceprodukt41ca761 unverändert, isolierte Profile gesichert. M01-Overlap und weitere M-Fälle offen. UX01 append_space ohne Wirkung außerhalb Recoveryfreigabe dokumentiert. Nach realem PowerShell-OOM nur0,95GB Hostcommitreserve; eigener Testclient sauber beendet, menschliches Freigeben unbenötigten Appspeichers angefragt, dann Wakeblock. Kein REVIEW_READY.

2026-10-15 AP-IV2-020/R01 Phase C: Hostspeicher nach menschlicher Aktion wieder frei, erster echter Wakeversuch ausgewertet. Sechs bewusst aufgenommene WAVs auf ausdrücklichen Nutzerwunsch004 bytegleich mit Manifest/Hashes und Messskripten versioniert. Erste Jarvis-Pauseaufnahme laut Mensch ohne Wakeanteil, Negativkontrolle. Echte ONNX-Frames und V2/Kroko-Replays0/160/320/480ms:320ms erhält beide direkten Nutzsätze, Livebestätigung offen. Produkt41ca761 unverändert, kein vollständiger M-PASS/REVIEW_READY.

2026-10-19 AP-IV2-020/R01: 11 menschliche Aufgaben/15 Versuche ausgewertet;14Activations, keine pauschalen M-PASS. USB-Stillstand R11 nachgewiesen und im ausdrücklich freigegebenen Recovery-Scope korrigiert: Produkt0f6c85e,48 gezielte/1400 volle Windows-Tests, neue Artefakte und native Source-/Wheel-Recovery am vorhandenen Pro-V2 PASS. Physische USB-/Feedbackwiederholung und weitere Realgates offen; W01 bleibt separat. Sieben privat hashgesicherte externe Ordner nicht entfernt: automatische Freigabeprüfung „blocked by policy“. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher PR15, kein REVIEW_READY/Merge/Servereingriff.

2026-10-19 AP-IV2-020/R01: R11 physische USB-Recovery am Produkt0f6c85e bestätigt und geschlossen; bewusster neuer F8/F9-Pfad, ein Final/eine native Einfügung. Feedbacktimings menschlich akzeptiert, neue gewünschte weiße Idle-Untergrenze30%/Peak100% als vorhandene Testkonfiguration gespeichert; Vergleich offen, Farbprofile ausdrücklich später.29Helfer-/1400Windows-Tests/0Skips, Qt/compileall PASS. Neun beendete privat hashgesicherte externe Ordner: automatische Freigabeprüfung verweigert Bereinigung „blocked by policy“. Gleiche R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS; übrige Real-/Frozen-/W01-Gates offen, kein REVIEW_READY.

2026-10-19 AP-IV2-020/R01: Idle-Rückmeldung akzeptiert, aber ohne Aktivierung/Zielübergang keine30/100%-Kalibrierung bewiesen. Direkte LED-only-Vorschau mit eigenem Start/20s/Übernehmen/Wiederholen, ohne Client/Mikrofon/Hotkey/Server,31Helfertests/Qt PASS. Produkt0f6c85e und R11 CLOSED unverändert; neuer Sichtvergleich offen. Zehn gesicherte externe Ordner: automatische Löschablehnung „blocked by policy“. Gleiche R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

2026-10-19 AP-IV2-020/R01: Direkter realer20sIdle-Puls weiß/min30%/Peak100% menschlich bestätigt, Testwerte reproduzierbar gespeichert. Zusätzlich LED-only-Nativtransportstörung im echten Source-Desktop/Pro-V2 autonom isoliert: LED wiederhergestellt,59→210Audioframes, Session/Generation unverändert, keine Activation/AudioAvailability-Mutation. Erster ProbeFAIL wegen falscher Erwartung eines fortbestehenden Ausfalls beibehalten; Beobachter/Testrahmen korrigiert,33Helfertests PASS. Produkt0f6c85e/R11CLOSED unverändert, übrige Pflichtgates offen.13gesicherte beendete externe Ordner automatisch gegen Löschen blockiert; gleicher R01/PR15, kein REVIEW_READY.

2026-10-19 AP-IV2-020/R01: Windows-Vault-Lebenszyklus mit frischen Prozessen/Origintrennung und Löschung PASS_SCOPED; reale idle-Runpausen über zwei manuelle Reconnects/eigenen TCP-Abbruch/Software-Mute sowie frische Runtime PASS_SCOPED. Wakeengine aus, keine Aktivierung/Paste,5000ms erhalten;1400Windows/0Skips und36Helfertests PASS. Produkt0f6c85e unverändert. Offene Kombinationen, Frozen/Admin/W01 und Gesamtgates bleiben;15private gesicherte Laufordner automatisch gegen Löschen gesperrt. Gleicher kumulativer PR15, kein REVIEW_READY/Servereingriff.

2026-10-20 AP-IV2-020/R01: Neuer Pro-V2-Server67f3ce45/Tree74f37cad/Version2.0.0 über öffentliche Info, passenden Gitbaum/-datum und echten Hello bestätigt; Wakefix-Mergee761b973 direkter Parent.13reale Modellreplays/18Activations ohne Zusatzwake in geprüfter digitaler Stille PASS_SCOPED, native Source/ReSpeaker133Pakete und neue1400Windows/0Skips/43Helfertests PASS. W01-Live-Mikrofon-/Schweige-/Soundvergleich vorbereitet, keine vollständige M-/Frozen-/30min100-Abnahme; Clientprodukt0f6c85e unverändert.17beendete private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, kein REVIEW_READY/Servereingriff.

2026-10-20 AP-IV2-020/R01: Aktuelle reale Alexa-/Hey-Jarvis-Proben mit Sound je genau1Activation/Timeout,20,625s bzw6,954s weitere belegte Audiobeobachtung ohne Folgetrigger, menschlich Wie erwartet: PASS_SCOPED. Sound-aus-Kontrolle endet vorzeitig: nur1,875s Audio nach Timeout, NOT_PROVEN statt angenommener5s. Nur diesen Fall wiederholen; Testoberfläche wartet eine bereits laufende Ruhephase nach explizitem Beendenwunsch ab, Fensterclose bleibt Abbrechen.48Helfer/Qt und neue1400Windows/0Skips PASS. Produkt0f6c85e/Server67f3ce45 unverändert;18private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher PR15, kein REVIEW_READY/Servereingriff.

2026-10-20 AP-IV2-020/R01: W01-Kontrolle Alexa ohne Sound PASS_SCOPED: genau1Wake/Activation/Timeout,29,765s weitere echte Audio-Nachbeobachtung ohne Folgetrigger,1543Pakete, keine Sprache/Final/Paste, menschlich Wie erwartet, Exit0. Damit alle3vorgesehenen Livekontrollen und13Modellfälle erfolgreich; konkretes W01 CLOSED_VERIFIED_SCOPED. Vollständige M-/Frozen-/Both-/Nutzsprachgrenzen-/30min100-Gates bleiben offen. Produkt0f6c85e/Server67f3ce45 unverändert;19private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher PR15, kein REVIEW_READY/Servereingriff.

2026-10-20 AP-IV2-020/R01: Denkpause mit2Segmenten/F9/2exakten nativen Einfügungen, Cancel mit82,969s weiterer Audioübertragung ohne Ausgabe und menschlich ausdrücklich bestätigte Server-/Tab-/Logansicht PASS_SCOPED; T01 geschlossen. Native Refreshprobe enthielt kein Refresh und bleibt NOT_PROVEN, lieferte aber korrekt gebundenen Altfinal-nach-Neustart-Beleg203ms. Zwei autonome reale ASR-/Controls-/Deadline-Refreshfälle PASS_SCOPED. T04-Testhäkchenfehler mit Regression/Qt korrigiert; nur native Refreshprobe entspannt erneut vorbereiten, übrige vollständige Gates offen. Keine Produkt-/Serveränderung, gleicher PR15.

2026-10-20 AP-IV2-020/R01: Menschlicher nativer F8-Refresh während segment_active, F9/Finish und2exakte native Einfügungen derselben Activation PASS_SCOPED; menschlicher15sNachsprechfall bleibt phasenbedingt NOT_PROVEN. Ohne weitere menschliche Wiederholung:2reale native Windows→WM_HOTKEY→Qt→Controls→ASR-Nachsprechfälle bei5000ms/6Callbacks PASS_SCOPED, Fristverlängerung/nichtadditives Wiederholen/Timeout bestätigt. T04 unterscheidet Phasen;56Helfer/Qt PASS, bytegleiches Produkt0f6c85e behält1400Windows/0Skips.21hashgesicherte Aufräumreste automatisch gesperrt. Keine Produkt-/Serveränderung, gleicher PR15.

2026-10-20 AP-IV2-020/R01: Hardware-Mute27,297s/zehn blockierte F8 und bewusste Wiederfreigabe/1exakte Einfügung sowie Reinsert1Final/2passende automatische+manuelle Ausgaben PASS_SCOPED. Zwei aktive Wake-Modell-/Pausen-/Reconnectfälle PASS_SCOPED. Erweiterte Pause→Recovery→manuelle Aufnahme mit Wakefixture→Cancel erzeugt zweimal Zusatzwake bei Stille: IV2-020-W02 offen, Ursache noch einzugrenzen; kein Serverfix vorgenommen.59Helfer/Qt PASS, Produkt0f6c85e unverändert/1400Windowsbeleg erhalten.22gesicherte Aufräumreste automatisch gesperrt. Keine Produkt-/Serveränderung, gleicher PR15.

2026-10-20 AP-IV2-020/R01: Drei übernommene BOTH-Aufgaben PASS_SCOPED: natives Manual-F8/F9 und beide direkten Wake-Nutzsätze genau einmal ohne Rufwort;18,782/23,313s echte Ruhe ohne Zusatzwake. Erster Alexa-Versuch bewusst wiederholt, bleibt NOT_PROVEN. Realer Watchdog55,062sWarnung/60,015sAblauf und3gebundene ASRfinals aus demselben Rohdurchlauf nach phasengenauer Nachauswertung PASS_SCOPED; falsche Einsegmentannahme als Hilfstest-FAIL erhalten.61Helfer/Qt PASS, Produkt0f6c85e/1400Windowsbeleg unverändert. Keine identischen Sprechwiederholungen; technische/EXE-/Dauerreste gebündelt, W02 offen.23Aufräumreste automatisch gesperrt. Gleicher PR15, keine Produkt-/Serveränderung.

2026-10-21 AP-IV2-020/R01: Automatischer zusammenhängender1800.015s/100Activations-Lauf mit echten Modellen PASS_SCOPED;100Finals/100Historyeinträge/100kontrollierte Injektionsversuche, drei eigene Recoveryaktionen. Physische/Frozen-M12-Anteile offen. W02 unverändert0/2reproduziert, historische2FAIL bleiben offen;0,90/2Frames erhält beide Positivfixtures,3/5Frames verfehlen Jarvis. Keine Defaultübernahme. Alle26eigenen externen Laufzeitordner hashgesichert entfernt.70Helfer/Qt und neue1400Windows/0Skips PASS; Produkt0f6c85e unverändert. Zwei Fehlversuche separat erhalten. Gleicher PR15, keine Produkt-/Serveränderung.

2026-10-21 AP-IV2-020/R01: W02 auf ausdrückliche menschliche Entscheidung als aktuell nicht mehr reproduzierbar geschlossen; kein eigener Freigabeblocker. Historische2FAIL erhalten, keine identifizierte Codekorrektur behauptet. Rest: technische Kombinationen, finaler EXE-/Admin-/Clipboard-/physischer Abschluss und Akten/ unabhängige Abnahme. Keine Wiederholung bestandener Standarddiktate, USB-Grundprobe oder des identischen30min100-Replaylaufs. Gesamtstatus BLOCKED, kein REVIEW_READY.
