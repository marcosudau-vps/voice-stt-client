# AP-IV2-010 / R01-UMSETZUNG

Status **IN_PROGRESS**, Workflow **IMPLEMENTATION_IN_PROGRESS**.
[Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenz](EVIDENCE/INDEX.md).

Clientprodukt und Parent `43759d345b2b88354e4f3b383a4833731621d1e3`,
Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. AP110-PASS, menschlicher
R03-Prompt und PR13-Squash sind vorhanden; keine offene frühere Paketlinie.
Arbeitsfreigabe aus AP000/R01 gilt workflowweit; keine AP-IV2-010-Übernahmefreigabe.

Umsetzungsskizze: vorhandene Smokes wiederverwenden, exakten Git-Blobexport
prüfen, getrennten Produktionsserver mit kontrollierten Recorder-/Schedulerports
starten und V2Runtime über echte HTTP-/WebSockets bis zu temporärer SQLite und
kontrolliertem Clipboard prüfen. Seltene Reihenfolgen und native Fehlergrenzen
mit vorhandenen konkreten Methoden ergänzen. Alle 28 automatisierten Szenarien
binden; SC29/30 bleiben IV2-020. Keine Produktcodeänderungen.

Baseline: vollständige Windows-Clientsuite 1353 PASS / 170.483s; initialer
unbegrenzter Lauf wurde nach Hängen beendet, verbose Wiederholung grün.
Serverumgebung iterativ ergänzt (httpx, soundfile, dotenv, scipy, torch,
webrtcvad, onnxruntime, python-multipart). Noch keine vollständige
Serverqualifikation behauptet. Vollständige Nachweise folgen in diesem Run.

Getrennte Servervenv verwendet kompatible installierte Abhängigkeiten über
einen expliziten lokalen Pfad; FastAPI/Starlette sind dort separat gepinnt.
Diese lokalen Testabhängigkeiten werden nicht in Clientrequirements übernommen.
Serverexport direkt aus Git-Blobs, weil Git-Archive EOL-Attribute anwendet.
Recordergrenze übernimmt AP040s immutable Jobherkunft; der upstream
Testrecorder besitzt einen ungeeigneten gemeinsamen FIFO für überlappende Jobs.

Nächste Aktion: Qualifikation des gesicherten Harnesskandidaten.
