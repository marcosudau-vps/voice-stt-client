# UX01 – Produktkorrektur und erneute Qualifikation

Die [ausdrückliche Freigabe006](../../ZUSATZPROMPTS/006_UX01_FREIGABE.md)
erlaubt diese begrenzte Ausnahmekorrektur im selben AP020/R01.
Status: **IN_PROGRESS**, kein vollständiges Realgate-PASS.

- [Vorherige relevante Baseline](../human/ux01-current-product-baseline.json):
  67 bestehende Injection-/Reinsertiontests PASS am alten Produkt.
- [V2-Ergebnisbaseline](../human/ux01-v2-results-baseline.json): PASS.
- [Gezielter ursprünglicher Fehlernachweis](../human/append-space-red.json).
- [Dauerhafte Regression vor Produktfix](../human/ux01-permanent-red-corrected.json):
  fünf Tests, drei tatsächliche Leerzeichenfehler.
- [Gezielte Regression nach Fix](../human/ux01-targeted-green-final.json):
  100 Tests PASS, einschließlich fünf neuer komponierter Regressionen.
- [Vollständige Windows-Suite vor Kandidatencommit](windows-full-precommit.json).

Die Protokolle liegen jeweils vollständig als `.txt.gz` neben den JSON-Belegen;
JSON enthält Befehl, Runtime, Quellhashes vorher/nachher und Exitcode.
Neue Commit-/Build-/Paaridentitäten werden nach erfolgreicher Prüfung ergänzt.
Frühere Produkt41-Belege bleiben unverändert historisch. Keine Übertragung
offener menschlicher Pflichtfälle auf den neuen Build.

Windows-Vollsuite vor Commit: **1378 PASS, keine Skips**, 210.906s. Native Probe ohne menschlichen Fokus: **NOT_RUN**, Zwischenablage blieb unverändert. Kein Produktfehler abgeleitet; Fokusaktion wird mit dem nächsten menschlichen Block gebündelt.
