# AP-IV2-010 / R01 – Evidenzindex

Status IN_PROGRESS. Produktpaar Client `43759d345b2b88354e4f3b383a4833731621d1e3`
/ Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

Prozess-JSONs entstehen durch `tests.test_v2_cross_repository` mit
`IV2_PROCESS_GATE=1`, `IV2_SERVER_ROOT`, `IV2_SERVER_REPOSITORY`, `IV2_EVIDENCE`.
Serverpid verschieden vom Clientpid; empfangene Domain-/Logframes redigiert,
synthetisches PCM nur als Bytezahl. Quellen vor/nach Prozess bytegeprüft.
Fehlversuche und der finale Teststand werden vor Abgabe kandidatengebunden
mit vollständigen komprimierten Logs und Befehl/Exitcode/Runtime gesichert.

Reproduzierbarer Gesamtrunner: `venv/Scripts/python.exe scripts/qualify_v2_pair.py
--server-root <exakter Export> --server-repository <Gitrepo>
--evidence <dieser Ordner>`.

Reale Modell-/Mikrofon-/USB-/Paste-/Feedbackwahrnehmung: NOT_RUN / AP-IV2-020.
