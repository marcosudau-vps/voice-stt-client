# Gemeinsame Realtests und wiederverwendbare Werkzeuge

[Manual3000](manual-followup-3000.json), [menschlich gewählte5000ms](manual-followup-5000.json),
[erster Live-Wakeversuch](wake-first-live.json), [behebbarer Hostspeichermangel](host-memory-constraint.json).

[Sechs ausdrücklich freigegebene Original-WAVs und Reproduktion](samples/README.md),
[Fixturemanifest](samples/manifest.json), [Sampleherkunft](sample-index.json).
[Testhilfenprüfung](tool-validation.md), [reale Scores](wake-scores-summary.json),
[vollständige echte Predictionframes](wake-scores-full.json.gz),
[0/160/320/480ms im echten V2-/ASR-Replay](wake-replay-calibration.json).

320ms ist vorbereiteter Livekandidat, noch keine menschliche Endwahl.
Die fehlende Wakephrase der ersten Aufnahme wurde vom Menschen erklärt; drei
positive/drei negative Samples, kein behauptetes Detector-FAIL für diese Datei.

[UX01](ux-findings.json): wirkungsloses append_space, Produktkorrektur noch
außerhalb der Recoveryfreigabe. Keine komplette M-Abnahme aus diesen Teilbelegen.
