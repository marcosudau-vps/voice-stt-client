# IV2-020-F01 – vorübergehender Settings-HTTP-Ausfall blockiert Recovery dauerhaft

**Offener Produktbefund / FAIL. Produktcode unverändert. Freigabe erforderlich.**
Betroffen: REAL-03, M-07; Reconnect auch bei Start während Serverwarmup betroffen.

## Tatsächlicher Repro und Ursache

Zwei lokale native Desktopsessions mit echtem ReSpeaker und unverändertem V2Runtime,
an source-qualified ada13b0. Kontrollierter Neustart ausschließlich des AP020-
Testcontainers. Beide Male: ready → backoff/network_lost → generation2/connecting →
**blocked/settings_preflight_failed**. Server war danach wieder ready; Client
blieb über den Beobachtungszeitraum geblockt und sendete kein Audio mehr.
[Trace](EVIDENCE/restart-repro-trace.jsonl), [Messung](EVIDENCE/restart-repro-smoke.json).

`SettingsService.prepare()` lädt öffentliche Metadaten mit GET. Ein vorübergehender
HTTPausfall erzeugt `SettingsError('http_unavailable')`. SettingsError erbt von
ValueError. `V2STTSession._connection()` klassifiziert jeden ValueError und jeden
Prepare-Timeout als permanente Konfigurationsstörung. Die Backoffschleife endet.

[Gezielter unveränderter Repro](EVIDENCE/repro_transient_preflight.py): zwei rote
Recoveryfälle, ein grüner Kontrollfall für unverändert permanente invalid_schema.
[Vollständiger Log](EVIDENCE/repro-transient-preflight.txt.gz).
Das ist ein neuer Realbefund trotz grüner bisheriger Regression; kein Eigenreview.

## Konkreter, noch nicht angewandter Änderungsvorschlag

[Reviewbarer Patch](EVIDENCE/proposed-client-recovery-fix.patch), ausschließlich:

1. `voice_stt_client/core/settings_service.py`, `SettingsService.prepare()`:
   vorübergehende GET-Fehler http_unavailable/http_timeout/http_worker_busy sowie
   HTTP408/429/5xx als retrybaren Transportfehler weiterreichen. Ungültige Schemas,
   Profile, Auswahl und permanente HTTPfehler bleiben blockierend. Keine Mutation
   und insbesondere kein automatischer Retry unklarer PATCHes.
2. `voice_stt_client/core/v2_transport.py`, `_connection()`:
   Prepare-Timeout in die vorhandene begrenzte Backoffbehandlung laufen lassen;
   ValueError bleibt Konfigurationsblocker. Audio und Trigger bleiben während
   erneuter Preflight-/Hello-/Settingsbestätigung gesperrt.
3. Passende Regressionen in `tests/test_v2_settings_service.py` und
   `tests/test_v2_transport.py`: Transienttypen/Statuscodes, Timeoutretry,
   permanente Fehler, keine vorzeitige Socket-/Audiofreigabe, kein PATCHretry,
   Shutdown/Generationguards. Vorhandene Reprofälle in reguläre Regression übernehmen.

Keine Serveränderung, kein Wire-/Sicherheitslimitwechsel, keine Defaultkalibrierung.
Zulässiger Weg: ausdrücklich freigegebene enge Clientkorrektur im selben kumulativen
AP020-Branch/PR und R01; anschließend frische vollständige Qualifikation des neuen
Produkts. Alternativ separate ausdrücklich beauftragte Client-FIX-Instanz.

## Erforderlicher Nachweis nach Freigabe

Gezielte Regression, komplette Windowsclientsuite/compileall/diffcheck, echter
Serverrestart einschließlich temporär nicht verfügbarem HTTP und erfolgreicher
neuer Session/Audioaufnahme; invalid_schema/-profile bleibt BLOCKED. Neue EXE aus
dem korrigierten Produktcommit bauen und mit SHA256 binden, betroffene Paar-/Build-
und reale Pflichtfälle am endgültigen Stand erneut prüfen. AP010-Buildnachweise
werden dann nur Herkunft, nicht ungeprüft Erfolg des neuen Produkts.

Vor diesem Fix ist eine vollständige reale Abnahme ausgeschlossen. Die übrigen
vorbereiteten Sprach-/USB-/Wahrnehmungsblöcke bleiben im selben Auftrag verfügbar.
