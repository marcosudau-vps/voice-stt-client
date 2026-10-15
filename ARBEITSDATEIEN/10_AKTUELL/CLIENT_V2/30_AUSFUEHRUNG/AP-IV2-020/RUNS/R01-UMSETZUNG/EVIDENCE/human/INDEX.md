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

[Zweite Live320probe](live-wake-320.json), [echter nativer Einfügeprobe-PASS](native-editor-probe.json),
[geführter Lauf mit tatsächlicher erster Einfügung und späterem Fokusverlust](guided-wake-320.json).
Keine pauschale native Einfügestörung behauptet. [Roter UX01-Beleg](append-space-red.json),
[isolierte unapplizierte Vorschau](append-space-preview.json),
[konkreter noch nicht angewandter Scopevorschlag](../../06_SCOPE_VORSCHLAG_UX01.md).

## Ergänzung: UX01-Freigabe und letzte menschliche Rückmeldung

- [Ausdrückliche Freigabe](../../ZUSATZPROMPTS/006_UX01_FREIGABE.md): gleiche R01, Produktkorrektur und Tests/Requalifikation autorisiert.
- [Menschliche Rückmeldung](guided-wake-320-human-feedback.json): beide Sätze vollständig; technische Fokus-/Zielevidenz im [geführten Lauf](guided-wake-320.json) bleibt abweichend nur partiell. Keine nachträgliche Umwertung zu vollständigem PASS.
- [Dauerhafte rote Regression, korrigierte Fixtureannahme](ux01-permanent-red-corrected.json), [gezielte 100 Tests grün](ux01-targeted-green-final.json). Erster roter Testlauf enthielt zusätzlich eine falsche Erwartung an den Rückgabewert für Deduplizierung; erster Greenversuch zusätzlich eine falsche Erwartung an die rohe Queue-API. Die tatsächliche Deduplizierungsautorität liegt im Finalconsumer und bleibt vollständig geprüft.
- Neuer Produkt-/Buildstand und volle Qualifikation folgen unter [UX01-Evidenz](../ux01/). Vorherige Produkt41-Belege werden nicht als Beleg des neuen Produkts ausgegeben.
