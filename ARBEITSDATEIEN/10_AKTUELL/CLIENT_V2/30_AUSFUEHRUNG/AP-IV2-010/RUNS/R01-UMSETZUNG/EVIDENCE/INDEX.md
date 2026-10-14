# AP-IV2-010 / R01 – vollständige Evidenz

Automatisierter Selbstcheck PASS / REVIEW_READY. Kein unabhängiger ROOT_PASS.

- [validation.json](validation.json): endgültige Commands, SHA/Tree/Runtime, 555 Serverblobs, Crossrepo-Hash, 28 Szenarien; initiale fehlgeschlagene Commands superseded.
- [client-repeat-validation.json](client-repeat-validation.json), [Windowsvollsuite](client-full-repeat.txt.gz):1354, exit0, stabiles0f0687c.
- [server-repeat-validation.json](server-repeat-validation.json), [Servervollsuite](server-full-repeat.txt.gz): gesamter pytest-unit-Lauf; [einzeln eingeordnete Skips](server-skips.json).
- [Processmanifest](process-manifest.json): getrennte PIDs/Interpreter, Client0f0687c/Serverada13b0. Einzelne `test_*.json`: redigierte tatsächliche Domain-/Logframes, HTTP-Routen, vor/nach Prozess geprüfte Quellen.
- [Prozesslog](cross-process.txt.gz):11 PASS; [Grenzfalllog](scenario-boundaries.txt.gz):17 PASS mit konkreten Methoden.
- [Sourcekonsistenz](source-consistency.json):555 unveränderte Serverblobs, keine Produkt-/Test-/Dependencyänderung nach Harness6c969a9; Produkt unverändert ab Parent43759d3.
- [Startprovenienz](start-provenance.json): AP110-R02-PASS, menschlicher R03-Prompt, tatsächlicher PR13-Merge, genau ein neuer Single-Parent-Commit, Baumgleichheit.
- [initial-validation.json](initial-validation.json), `initial-*.txt.gz`, `client-full.txt.gz`, `server-full.txt.gz`, `intermediate-client-full.txt.gz`: vollständige frühe Umgebungs-/Harness-/HEAD-Wechsel-Fehlversuche und ausdrücklich abgebrochene Versuche. Kein Erfolgsbeleg daraus.
- Kumulative Socketlogs: [transport](server-transport.txt.gz), [audio/logs](server-audio.txt.gz), [controls](server-controls.txt.gz), [results](server-results.txt.gz), [settings](server-settings.txt.gz), [feedback](server-feedback.txt.gz), [runtime](server-runtime.txt.gz). Je exit0, konkrete Checks/Quellen/Runtime/Grenzen.
- [compileall](compileall.txt.gz), [diffcheck](diff-check.txt.gz), [Clientumgebung](client-environment.txt.gz), [Serverumgebung](server-environment.txt.gz).

Commandlogs besitzen unkomprimierten/komprimierten SHA256 im Manifest;
zusätzliche frühe Logs im [Vollhashmanifest](full-log-manifest.json).
[CI des qualifizierten Kandidaten](ci-qualified-candidate.json). Synthetischer Testtext, redigierte
Logtokens und PCM-Bytezahlen; keine Nutzeraudiodaten.
Reale ASR-/Mic-/USB-/Paste-/Wahrnehmung, SC29/30: NOT_RUN/AP-IV2-020.
[Reproduktion](../../../../../../../../docs/protocol-v2-integration.md).
