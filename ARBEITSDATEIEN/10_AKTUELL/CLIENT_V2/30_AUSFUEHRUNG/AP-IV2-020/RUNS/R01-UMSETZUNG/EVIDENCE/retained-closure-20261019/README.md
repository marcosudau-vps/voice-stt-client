# Offline-Belegklärung AP-IV2-020

`results.json` enthält die neue25-Modell-Metadatenprüfung und die rein lesende
Auswertung erhaltener Akten. `validation.json` bindet Helfer, Befehle und volle
Logs. `real-case-rests.json` erhält die unveränderten ursprünglichen M-Status.
Kein gestarteter Server/Client, keine neue Live-/Hardwarequalifikation.

Wiederholung ausschließlich mit der Projektumgebung:

```powershell
.\venv\Scripts\python.exe -B ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/resolve_retained_evidence.py --source <erhaltene-source-exact> --server-repository <Server-Git-Checkout> --runtime <erhaltener-AP020-Laufzeitordner> --output <Ergebnisdatei-innerhalb-dieses-Repositorys>
```

Eingaben werden nur gelesen; Quellbytes müssen zum Pinada13b0 passen. Ausgabe
außerhalb des Clientrepositorys wird abgewiesen. Das Werkzeug startet keinen
Server, sendet kein Audio, lädt kein Benutzerprofil und schreibt keine externen
Caches/Logs. `-B` verhindert Python-Bytecodeablage bei den gelesenen Quellen.
ONNX-Runtime muss bereits in der Projektumgebung verfügbar sein; keine automatische
Installation. Nur CPU-Modellladen/Metadaten, kein Score-Inferenzlauf.

Sessionzuordnung bevorzugt gemeinsame Command-IDs. Ältere Observer ohne solche
IDs werden nur bei eindeutigem Beginn innerhalb5s schwächer zeitlich zugeordnet;
widersprechende IDs und mehrdeutige Zuordnungen ergeben keinen Beleg.
