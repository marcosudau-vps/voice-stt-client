# Traceability Matrix – Zielbild → Arbeitspaket → Nachweis

**Zweck:** Kein Spezifikationspunkt darf „zwischen den Dateien“ verloren gehen.

| Zielbild / Invariante | Haupt-AP | Sekundär-AP | Automatischer Nachweis | Manueller Nachweis | Status |
|---|---|---|---|---|---|
| Ein serverseitiger gemeinsamer Lifecycle | 02 | 05 | E2E Lifecycle | M-01/M-02 | [ ] |
| Kein lokales VAD als Manual-Authority | 04/05 | 10 | Architektur-/Integrationstest | M-01 | [ ] |
| First Trigger wins | 02 | 06 | Collision/Race | M-06 | [ ] |
| Wake Word während Activation ohne Wirkung | 02/06 | 10 | Negativtest | M-03/M-05 | [ ] |
| Hotkey Idle = Activate | 06 | 05 | Controller/E2E | M-01 | [ ] |
| Hotkey Active = Finish | 06 | 02 | E2E | M-07 | [ ] |
| separater Wake-Word-Pause-Hotkey | 06 | 08 | UI/Hotkey-Test | M-08 | [ ] |
| Trigger-Lock bis stabil Idle | 02 | 03 | Finalizing/Lock-Test | M-06/M-09 | [ ] |
| Continuous Stream | 04 | 10 | multi-activation E2E | M-14 | [ ] |
| Server alleinige Lifecycle-Authority | 02/03 | 05 | Mirror/State tests | M-01/M-02 | [ ] |
| Kein `mode` zur Runtime | 07 | 10 | Grep/AST + Config tests | M-12 | [ ] |
| Triggerflags 3 gültige Kombinationen | 07/08 | 11 | Config/Admission | M-12 | [ ] |
| Wake-Word-Konfiguration sichtbar | 08 | 03 | Settings test | M-12 | [ ] |
| Source-neutrales UI/Feedback | 09 | 05 | pair comparison | M-13 | [ ] |
| Kein Warnloop | 09/10 | 05 | 10s idle test | M-02/M-12 | [ ] |
| Jeder Zustand hat Exit/Recovery | 02/03/05 | 10 | fault/race tests | M-09/M-11 | [ ] |
| Reconnect resynchronisiert | 03/05 | 10 | reconnect E2E | M-11 | [ ] |
| Browser aktueller Contract | 11 | 03 | browser contract | M-15 | [ ] |
| LED reine Darstellung | 09 | 11 | interface tests | M-16/M-17 | [ ] |
| Vollregression | 12 | alle | komplette Suites | – | [ ] |
| Reale Hardwareabnahme | 13 | 09 | – | M-17 | [ ] |
| Aktive Doku = reale Architektur | 14 | alle | Doc audit | Abschlussreview | [ ] |

## Pflege

- [ ] Bei neuer Zielbildforderung neue Zeile hinzufügen.
- [ ] Bei neuem Defekt betroffene Zeile(n) referenzieren.
- [ ] Kein Gate schließen, solange zugehörige Zeilen nicht nachgewiesen sind.
