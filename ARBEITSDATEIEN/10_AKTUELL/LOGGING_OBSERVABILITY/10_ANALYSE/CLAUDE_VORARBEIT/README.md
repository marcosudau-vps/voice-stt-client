# CLAUDE_VORARBEIT

Hier werden die bereits erzeugten Logging-Codeanalysen und Reviews gesammelt.

Für OBS-000 erwartet:

```text
LOGGING_CODE_INTEGRATION_AUDIT.md
LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md
LOGGING_CONCURRENCY_FAILURE_MODEL.md
LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md
LOGGING_V1_IMPLEMENTATION_PLAN.md
LOGGING_OPEN_DECISIONS.md
LOGGING_TEST_MATRIX.md             # falls vorhanden
LOGGING_ADVERSARIAL_REVIEW.md
```

Claude soll diese Dateien beim Start im bestehenden Workspace rekursiv suchen.

Falls sie an anderer Stelle liegen:

- in diesen Ordner kopieren;
- Originale nicht löschen;
- Quelle und SHA-256 in `SOURCE_MANIFEST.md` dokumentieren;
- bei mehreren Varianten nicht stillschweigend überschreiben.
