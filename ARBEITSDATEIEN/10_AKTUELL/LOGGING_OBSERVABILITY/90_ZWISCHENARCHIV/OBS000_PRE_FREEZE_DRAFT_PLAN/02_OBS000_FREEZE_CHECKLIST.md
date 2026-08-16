# OBS-000 – Entscheidungen und Freeze Gate

## Zweck

Dieses Dokument ist die Checkliste, die vor dem ersten Produktcode-Work-Package geschlossen werden muss.

## Einzuarbeitende Claude-Ergebnisse

- [ ] LOGGING_CODE_INTEGRATION_AUDIT.md
- [ ] LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md
- [ ] LOGGING_CONCURRENCY_FAILURE_MODEL.md
- [ ] LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md
- [ ] LOGGING_V1_IMPLEMENTATION_PLAN.md
- [ ] LOGGING_OPEN_DECISIONS.md
- [ ] LOGGING_TEST_MATRIX.md, falls erzeugt
- [ ] LOGGING_ADVERSARIAL_REVIEW.md

## Entscheidungen

- [ ] CanonicalRecord exakt festgelegt.
- [ ] Record-/Schema-Versionierung festgelegt.
- [ ] Producer-Identität festgelegt.
- [ ] Channelmodell festgelegt.
- [ ] Event-/Record-Dedupe festgelegt.
- [ ] Replay-Semantik festgelegt.
- [ ] Ingress-/Fan-out-Hook festgelegt.
- [ ] Queue-Typ/Default/Dropstrategie festgelegt.
- [ ] Worker-Lifecycle festgelegt.
- [ ] SQLite-Pfad festgelegt.
- [ ] SQLite Schema/Migration festgelegt.
- [ ] Retention Defaults festgelegt.
- [ ] Raw-Payload Default festgelegt.
- [ ] Transcription-Content Default festgelegt.
- [ ] Secret-Redaction-Liste festgelegt.
- [ ] V1 File-Sinks festgelegt.
- [ ] Query-Provider-Interface festgelegt.
- [ ] UI-Position festgelegt.
- [ ] Settings-Scope festgelegt.
- [ ] V1 Observation-Hooks festgelegt.
- [ ] Hot-Path Sampling/Aggregation festgelegt.
- [ ] Shutdown-/Flush-Semantik festgelegt.

## Freeze-Kriterium

`PASS`, wenn keine dieser Fragen mehr von einem Coding-Agenten entschieden werden muss.
