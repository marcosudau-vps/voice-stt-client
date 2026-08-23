# Arbeitspakete

Arbeitspakete sind die agentengerechten Umsetzungseinheiten dieses Arbeitsblocks.

Die verbindlichen Grundregeln für Aufbau, prüfbare Ziele, Akzeptanzkriterien, Validierung und Commit-Verhalten stehen in `../PLANUNG/README.md`.

## Empfohlene Struktur

```text
AP-.../
├── README.md
├── PLAN.md
└── runs/
    └── 01_IMPLEMENTATION/
        ├── PROMPT.md
        ├── REPORT.md
        └── evidence/
```

`runs/` wird erst mit dem ersten tatsächlichen Run angelegt. Weitere Runs können danach ohne Strukturwechsel ergänzt werden.

Abgeschlossene Arbeitspakete bleiben an ihrem Platz und werden über ihren Status als abgeschlossen gekennzeichnet.
