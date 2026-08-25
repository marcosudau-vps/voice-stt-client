# Endabnahme – AP-CLI-000 / Run 01_BASELINE

**Status:** PASS

## Referenzen

- AP-Start-HEAD: `db102fdc6dd70e4de798a363608d1e7412533dd7`
- Agentencommit vor der koordinierenden Endabnahme:
  `974d09024a3ab62ffff3b8bc360c4dfe95ea7e38`
- SHA-256 des unveränderten Originalauftrags:
  `A952E1DE9F27BBD108EDD6D131837196BE588D9236AC1572116B4B1B2B4951F7`

## Prüfung durch die Koordination

- Der AP-Umfang enthält keinen Produktcode-Umbau, sondern reproduzierbare
  Charakterisierung, Testnachweise und die Zuordnung der Ist-Befunde zu den
  Folgepaketen.
- Die Korrekturläufe dokumentieren und beheben zwei Formatierungsbefunde sowie
  die falsche lokale-venv-Angabe und die zunächst zu grobe Source-Merge-
  Zuordnung. Server-Admission, manuelle Client-Kommandos und source-neutrales
  Feedback sind nun `SRV-010`, `CLI-020` und `CLI-040` getrennt zugeordnet.
- Der Originalauftrag des Baseline-Runs blieb unverändert.
- Die Koordination hat ausschließlich diese Abnahme, den AP-Status und eine
  überzählige Leerzeile im eigenen Korrekturauftrag `02_CORRECTION/PROMPT.md`
  ergänzt beziehungsweise korrigiert.

## Unabhängige Validierung

```text
Fokussiert:
24 passed in 0.60s

Vollsuite (QT_QPA_PLATFORM=offscreen):
1192 passed in 79.38s

Commitanzahl seit AP-Start:
1

git diff --check AP-Start..HEAD:
PASS
```

## Abnahmeentscheidung

`AP-CLI-000` ist angenommen. Der charakterisierte Widerspruch beim erneuten
Streaming-Start bleibt bewusst ein Befund des Ist-Zustands und wird erst im
zuständigen Folgepaket `AP-CLI-010` aufgelöst.
