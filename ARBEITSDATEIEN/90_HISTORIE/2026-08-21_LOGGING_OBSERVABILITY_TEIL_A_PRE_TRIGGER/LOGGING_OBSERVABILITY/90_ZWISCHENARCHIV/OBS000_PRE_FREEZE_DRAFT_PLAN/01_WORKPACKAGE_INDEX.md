# Work-Package Index – Logging / Observability

| ID | Titel | Phase | Status | Abhängigkeit |
|---|---|---|---|---|
| OBS-000 | Plan Freeze & Baseline | 0 | DRAFT | neueste Audits/Review |
| OBS-010 | Canonical Model & Contracts | A | DRAFT | OBS-000 |
| OBS-020 | Ingress, Health & Redaction | A | DRAFT | OBS-010 |
| OBS-030 | Queue, Worker, SQLite & Retention | A | DRAFT | OBS-020 |
| OBS-040 | Live Adapter & Client Hooks | A | DRAFT | OBS-020, OBS-030 |
| OBS-050 | Local Query, Minimal UI & Settings | A | DRAFT | OBS-030 |
| OBS-060 | V1 Hardening & Baseline | A | DRAFT | OBS-040, OBS-050 |
| OBS-100 | Post-Trigger Instrumentation | B | DRAFT | Trigger-Migration |
| OBS-110 | Server Control/Auth/Capabilities | C | DRAFT | OBS-060 |
| OBS-120 | Remote Server History/Global Logs | C | DRAFT | OBS-110 |
| OBS-130 | Server Admin Settings | C | DRAFT | OBS-110 |
| OBS-140 | LED Logging Integration | D | DRAFT | OBS-060 |
| OBS-150 | Extended Sinks/Storage | D | DRAFT | OBS-060 |
| OBS-160 | Advanced Query/UX | E | DRAFT | OBS-120 |
| OBS-170 | Cross-Source Correlation | E | DRAFT | OBS-100, OBS-120, OBS-140 |
| OBS-180 | Final Hardening/Docs/Acceptance | Final | DRAFT | alle relevanten |
