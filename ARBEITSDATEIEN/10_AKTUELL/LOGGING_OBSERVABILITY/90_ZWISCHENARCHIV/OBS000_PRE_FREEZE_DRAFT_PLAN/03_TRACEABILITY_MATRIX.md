# Traceability Matrix – Logging / Observability

| ID | Invariante/Feature | Primär-WP | Automatischer Nachweis | Manueller Nachweis |
|---|---|---|---|---|
| O-01 | Observability only | OBS-020/040 | failure/isolation tests | Runtime smoke |
| O-02 | Fan-out | OBS-040 | dispatch tests | event flow review |
| O-03 | Non-blocking | OBS-030/060 | overload/perf tests | runtime behavior |
| O-04 | Bounded memory | OBS-030 | queue saturation | – |
| O-05 | Failure isolation | OBS-060 | injected failures | manual smoke |
| O-06 | Structured data | OBS-010/040 | schema tests | LogView inspection |
| O-07 | Source preservation | OBS-010 | normalization tests | filter check |
| O-08 | Replay safety | OBS-030/040 | replay tests | reconnect smoke |
| O-09 | Security | OBS-020/060/110 | redaction tests | secret audit |
| O-10 | Query independence | OBS-050 | architecture tests | code review |
| O-11 | Extensibility | OBS-010/050/140 | interface tests | integration review |
| O-12 | Admin separation | OBS-110/120 | dependency tests | code review |
| O-13 | Control plane separation | OBS-040/100 | architecture tests | lifecycle smoke |
| F-01 | Python logging | OBS-020 | handler integration | – |
| F-02 | SQLite history | OBS-030 | store/query tests | UI history |
| F-03 | Live server logs | OBS-040 | adapter integration | live run |
| F-04 | Client observations | OBS-040/100 | hook tests | timeline |
| F-05 | Minimal UI | OBS-050 | model tests | visual smoke |
| F-06 | Remote history | OBS-120 | provider integration | admin run |
| F-07 | Admin server config | OBS-130 | admin service tests | admin UI |
| F-08 | LED producer | OBS-140 | adapter tests | hardware smoke |
| F-09 | Additional sinks | OBS-150 | sink tests | configured smoke |
| F-10 | Forensic comparison | OBS-170 | correlation tests | incident walkthrough |
