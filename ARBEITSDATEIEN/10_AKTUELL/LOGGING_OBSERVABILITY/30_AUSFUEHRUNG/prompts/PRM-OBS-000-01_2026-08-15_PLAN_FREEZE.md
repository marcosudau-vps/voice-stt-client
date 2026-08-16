# PRM-OBS-000-01 – Logging Plan Freeze & Baseline

## Run-Metadaten

```text
Workstream: OBS
Work Package: OBS-000
Run: RUN-OBS-000-01_2026-08-15_CLAUDE
```

Workspace:

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude
```

Arbeitsbereich:

```text
ARBEITSDATEIEN\AP_THEMA_LOGGING
```

Run-Ordner:

```text
ARBEITSDATEIEN\AP_THEMA_LOGGING\
30_AUSFUEHRUNG\runs\
RUN-OBS-000-01_2026-08-15_CLAUDE
```

---

## 1. Auftrag

Führe **OBS-000 – Plan Freeze & Baseline** vollständig durch.

Ziel ist:

> Die vorhandenen Logging-/Observability-Entwürfe, deine bereits abgeschlossenen Code-Audits und das adversariale Review zu einer einzigen widerspruchsfreien, implementation-ready Sollgrundlage zusammenzuführen.

Danach soll `OBS-010` ohne neue grundlegende Architekturentscheidung implementierbar sein.

**Noch keine Produktimplementierung.**

---

## 2. Zuerst Arbeitsregeln und Gesamtplan lesen

Lies vollständig:

```text
ARBEITSDATEIEN\AP_THEMA_LOGGING\START_HIER.md
ARBEITSDATEIEN\AP_THEMA_LOGGING\AGENTS.md
```

Danach:

```text
ARBEITSDATEIEN\AP_THEMA_LOGGING\
20_PLANUNG\LOGGING_GESAMTPLAN\
00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md

ARBEITSDATEIEN\AP_THEMA_LOGGING\
20_PLANUNG\LOGGING_GESAMTPLAN\
01_WORKPACKAGE_INDEX.md

ARBEITSDATEIEN\AP_THEMA_LOGGING\
20_PLANUNG\LOGGING_GESAMTPLAN\
02_OBS000_FREEZE_CHECKLIST.md

ARBEITSDATEIEN\AP_THEMA_LOGGING\
20_PLANUNG\LOGGING_GESAMTPLAN\
03_TRACEABILITY_MATRIX.md
```

und das Work Package:

```text
20_PLANUNG\LOGGING_GESAMTPLAN\workpackages\
WP-OBS-010_CANONICAL_MODEL_CONTRACTS.md
```

Falls der konkrete Dateiname geringfügig abweicht, verwende die vorhandene `OBS-010`-Work-Package-Datei.

---

## 3. Grundlagen lesen

Lies:

```text
00_GRUNDLAGEN\
LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md

00_GRUNDLAGEN\
LOGGING_V1_ABGRENZUNG_ENTWURF.md

00_GRUNDLAGEN\
LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md
```

Der folgende Entwurf ist **nur historische/unverbindliche Ideenquelle**:

```text
05_DRAFTS_UNGEPRUEFT\
ErsterEntwurf_Logging.md
```

Er darf keine neueren Analysen oder Entscheidungen überschreiben.

---

## 4. Deine bereits erzeugten Logging-Analysen einsammeln

Folgende Dateien wurden bereits in vorherigen Claude-Runs erzeugt:

```text
LOGGING_CODE_INTEGRATION_AUDIT.md
LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md
LOGGING_CONCURRENCY_FAILURE_MODEL.md
LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md
LOGGING_V1_IMPLEMENTATION_PLAN.md
LOGGING_OPEN_DECISIONS.md
LOGGING_TEST_MATRIX.md              ## falls erzeugt
LOGGING_ADVERSARIAL_REVIEW.md
```

Suche sie **rekursiv im bestehenden Workspace**, bevorzugt unter `ARBEITSDATEIEN`.

Zielablage:

```text
ARBEITSDATEIEN\AP_THEMA_LOGGING\
10_ANALYSE\CLAUDE_VORARBEIT\
```

Wenn eine Datei dort noch nicht liegt:

1. kopiere sie dorthin;
2. lösche das Original NICHT;
3. dokumentiere ursprünglichen Pfad und SHA-256 in:

```text
10_ANALYSE\CLAUDE_VORARBEIT\SOURCE_MANIFEST.md
```

Wenn mehrere Varianten desselben Dateinamens existieren:

- nicht stillschweigend überschreiben;
- Inhalt/Modified Time/Hash vergleichen;
- im Manifest dokumentieren;
- die tatsächlich neueste bzw. zum letzten Auftrag gehörende Variante eindeutig auswählen.

Falls eine erwartete Pflichtdatei tatsächlich nicht auffindbar ist:

- nicht raten;
- im Run Report als fehlend markieren;
- nur dann `OBS-000 BLOCKED`, wenn ihr Inhalt für eine Freeze-Entscheidung wirklich unverzichtbar ist.

---

## 5. Quellenhierarchie

Für diesen Run gilt:

### Sollrichtung

Die Logging-Zielbild-/V1-Dateien formulieren die bisher gemeinsam entworfene Sollrichtung, sind aber noch Entwürfe.

### Ist-Evidence

Deine Code-Audits und der reale Produktcode entscheiden über Aussagen zum heutigen System.

### Red-Team

`LOGGING_ADVERSARIAL_REVIEW.md` ist ausdrücklich dazu da, Schwächen, YAGNI, falsche Annahmen und notwendige Korrekturen sichtbar zu machen.

### Keine stille Harmonisierung

Bei Widerspruch:

1. Widerspruch explizit benennen;
2. Quellen nennen;
3. Codefakt feststellen;
4. Zielauswirkung erläutern;
5. begründete Entscheidung/Empfehlung treffen;
6. Änderung sichtbar in Plan/Decision-Artefakten dokumentieren.

---

## 6. OBS-000 vollständig abarbeiten

Schließe mindestens alle Punkte der vorhandenen:

```text
02_OBS000_FREEZE_CHECKLIST.md
```

Dazu gehören insbesondere:

- CanonicalRecord finalisieren;
- Feldtypen / Pflichtfelder / optionale Felder;
- Record-/Schema-Versionierung;
- Producer-/Source-Modell;
- Channel-Modell;
- Level-/Type-Semantik;
- Replay-/Dedupe-Modell;
- stabiler Server-Live-Identity-Key;
- passiver `/ws/logs`-Fan-out-Hook;
- klare Trennung `/ws/logs` Observability vs `/ws/transcribe` Runtime-Control;
- Queue-/Backpressure-Modell;
- Worker-Lifecycle;
- Drop-/Health-Semantik;
- SQLite-Schema;
- Indizes;
- Schema-Migration;
- Retention;
- Cleanup;
- Shutdown-/Flush-Regeln;
- Redaction;
- Privacy;
- Raw-Payload-Policy;
- Transkriptinhalt-Policy;
- V1 File-Sink-Scope;
- QueryProvider-/QueryService-Contracts;
- Provider Status;
- UI-/Settings-Grenzen;
- V1 Observation-Hooks;
- Hot-Path-Regeln;
- Zukunftsgrenzen für Server History/Admin/LED.

Keine neue breite Analyse beginnen.

Gezielte Codeprüfung ist erlaubt, wenn eine konkrete Freeze-Entscheidung sonst nicht belastbar getroffen werden kann.

---

## 7. Endzustand UND V1 gemeinsam konsistent machen

Wir wollen nicht nur V1 planen.

Der Gesamtplan muss zwei klar getrennte Ausbauteile behalten:

### TEIL A – vor Triggerarchitektur-Migration

```text
OBS-010
OBS-020
OBS-030
OBS-040
OBS-050
OBS-060
```

### TEIL B – danach

```text
OBS-100
OBS-110
OBS-120
OBS-130
OBS-140
OBS-150
OBS-160
OBS-170
OBS-180
```

V1 darf spätere Funktionen nicht implementieren müssen, aber ihre Schnittstellen nicht verbauen.

Insbesondere berücksichtigen:

- Admin Authentication / Capability State;
- ServerControlConnection;
- historische/globale Serverlogs;
- serverweite Konfiguration;
- LED-Controller als späterer Producer;
- zusätzliche Sinks/Storage Backends;
- Multi-Provider Query;
- Cross-Source Forensics.

---

## 8. Planungsdateien aktualisieren

Du darfst im Rahmen dieses Runs die Logging-Arbeits-/Planungsdateien ändern.

Primär:

```text
20_PLANUNG\LOGGING_GESAMTPLAN\
```

Aktualisiere dort mindestens, soweit erforderlich:

```text
00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md
01_WORKPACKAGE_INDEX.md
02_OBS000_FREEZE_CHECKLIST.md
03_TRACEABILITY_MATRIX.md
workpackages\...
```

Besonders `OBS-010` und `OBS-020` müssen nach dem Freeze implementation-ready sein.

Wenn deine jüngsten Audits ergeben, dass Work-Package-Grenzen des Gesamtplans fachlich korrigiert werden müssen:

- ändern;
- Änderung begründen;
- keine unnötige Paketvermehrung.

---

## 9. Normative Freeze-Artefakte

Nur wenn OBS-000 tatsächlich `PASS` erreicht:

Lege in:

```text
00_NORMATIV\
```

mindestens eine klare, zusammenhängende Freeze-Grundlage an.

Empfohlen:

```text
LOGGING_ARCHITEKTUR_FREEZE_V1.md
LOGGING_CONTRACTS_FREEZE_V1.md
LOGGING_DECISIONS_FREEZE_V1.md
```

Alternativ darfst du eine gleichwertige, besser begründete Aufteilung verwenden.

Diese Dateien müssen eindeutig markieren:

```text
status: FROZEN
authority: normative
workstream: OBS
freeze_gate: OBS-000
```

Wichtig:

- Die vollständige Endarchitektur bleibt enthalten.
- Teil A/V1 ist als erste Implementierungsstufe abgegrenzt.
- Keine offene Architekturentscheidung darf als scheinbar final versteckt werden.

Falls OBS-000 BLOCKED:

- KEINE Datei als `FROZEN` markieren.

---

## 10. Run-Dokumentation

Pflege während des Runs:

```text
30_AUSFUEHRUNG\runs\
RUN-OBS-000-01_2026-08-15_CLAUDE\
RUN_REPORT.md
```

und:

```text
OUTPUT_INDEX.md
```

`RUN_REPORT.md` muss am Ende mindestens enthalten:

- Run-ID;
- Work Package;
- Ausgangszustand;
- gefundene Quellen;
- durchgeführte Arbeiten;
- erzeugte/geänderte Dateien;
- geschlossene Entscheidungen;
- verbliebene Entscheidungen;
- Widersprüche und deren Auflösung;
- gezielte Codeprüfungen;
- Tests/Evidence;
- Blocker;
- Gate-Empfehlung;
- nächster Schritt.

---

## 11. Evidence

Gezielte nachprüfbare Freeze-Evidence nach:

```text
40_EVIDENCE\OBS-000\
```

Beispiele:

- `SOURCE_MANIFEST.md`;
- SHA-256;
- gezielte Grep-/Codepfad-Prüfungen;
- Konsistenzcheck der Planungsdateien;
- relevante Git-Status-Ausgabe.

Keine ausufernde Evidence ohne Zweck.

---

## 12. Harte Verbote

Für diesen Run:

- KEINE Produktcodeänderungen;
- KEINE Produkt-Testcodeänderungen;
- KEINE aktive Produktconfig ändern;
- KEINE Triggerarchitektur reparieren;
- KEINE Logging-Implementierung beginnen;
- KEIN Commit;
- KEIN Push;
- KEIN Merge;
- KEIN Rebase;
- KEIN Tag;
- KEIN PR.

Keine Änderung in:

```text
voice-stt-client
voice-stt-server
led_controller_respeaker-v3
```

außer rein lesende Untersuchung.

---

## 13. Abschlussentscheidung

Am Ende exakt eine Hauptklassifikation:

```text
OBS-000 PASS
```

oder:

```text
OBS-000 BLOCKED
```

Bei PASS zusätzlich eindeutig:

```text
OBS-010 READY FOR IMPLEMENTATION
```

Falls OBS-010 noch nicht READY ist, kann OBS-000 nicht als vollständig bestanden gelten, sofern der Grund eine noch offene grundlegende Logging-Architekturentscheidung ist.

---

## 14. Falls noch Claude-Kapazität übrig ist

Nur nach `OBS-000 PASS`:

Führe einen adversarialen **Implementation-Readiness-Review von OBS-010** durch.

Prüfe:

- Scope eindeutig?
- keine verborgene Architekturentscheidung?
- Dateien/Komponenten konkret genug?
- positive Tests?
- negative Tests?
- Mutation-/False-Positive-Proofs bei kritischen Contracts?
- keine spätere Admin-/History-/LED-Erweiterung verbaut?

Ergebnis im Run Report:

```text
OBS-010 READINESS REVIEW: PASS/FAIL
```

OBS-010 selbst **noch nicht implementieren**.

## 15. LOG_VERLAUF.md weiterführen

Führe bitte auch den bestehenden ARBEITSDATEIEN\LOG_VERLAUF.md weiter. Ergänze am Ende des Runs genau einen neuen Meilenstein-Eintrag für RUN-OBS-000-01_2026-08-15_CLAUDE mit Datum, Workstream, Work Package, Ergebnis/Gate-Status und Verweisen auf die wichtigsten erzeugten Artefakte. Bestehende, insbesondere rekonstruierte historische Einträge nicht verändern. Der Verlaufslog soll nur Meilensteine dokumentieren, keine einzelnen Befehle oder Detailarbeiten.

Danach stoppen.
