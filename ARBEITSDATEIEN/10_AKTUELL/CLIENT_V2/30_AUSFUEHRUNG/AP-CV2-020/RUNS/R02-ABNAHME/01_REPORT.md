# AP-CV2-020 – R02 / unabhängige technische Abnahme

**Verdict: CHANGES_REQUIRED.** Offene Pflichtfindings: `CV2-020-R02-F01`, `CV2-020-R02-F02`. 2026-10-12, neue unabhängige ChatGPT-Session.

[Originalauftrag](00_PROMPT_ORIGINAL.md) · [Belegindex](EVIDENCE/INDEX.md) · [PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4)

## Geprüfte Identitäten und Reviewmethode

- Repository `marcosudau-vps/voice-stt-client`, Base `feat/client-v2`, Paketbranch `work/client-v2/ap-cv2-020`, PR offen.
- **reviewed_sha `2b79a9a23a6be554a2a2a05ff3256a63ccf022d4`; reviewed_tree `647a0b4070d666e37b475841d094d4e37cc43e40`.** Dies ist die Kandidatenspitze **vor** dem administrativen Reviewcommit.
- **canonical_parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`**, server_sha `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
- Windowsqualifizierter Produktcommit `7546298f26e00b83ad4c9510a9b8c1e7e6726fc3`, Tree `7bd496ef70a192781ff999b31695b3ef3fd72210`; geprüfter Compare bis Kandidatenhead enthält ausschließlich nachträgliche administrative Dokument-/Beleg-/Traceability-Dateien, keinen neuen Produkt-/Testcode.
- Vorgänger AP010: tatsächliche R02-Abnahme, menschliche Freigabe, PR #3 und kanonischer Einzelaggregatecommit `91065f5f7715aa6653ec5335d9e757b6ef97a067` anhand [Provenienz](../R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json) kontrolliert.
- Review über commitgebundene GitHub-Dateien; vollständig betroffene Transport-/Tracker-/Testdateien, Paketauftrag, K-01/K-04, 28 Requirements und konkrete Belege gelesen. **Keine** eigene Windows-Vollsuite, kein lokaler Windows-Checkout. Keine Produkt-/Test-/Serveränderung vorgenommen.

## Positiv geprüfter Umfang

- Hello wird beim Socketopen zuerst gesendet; bis Admission und explizitem Bootstrap sind Audio und Nutzercommands gesperrt. Suppression erfolgt nach notwendiger Bootstrapkonfiguration; ausgelieferte Bootstrap- und Mirroranschlüsse sind als Grenze für Folgepakete dokumentiert.
- `CommandTracker` speichert Command/Generation/Future/JSONbytes, begrenzt Kapazität, serialisiert gleiche Commandtypen, ermöglicht höchstens einen bytegleichen Retry, behandelt 15 Ackresulttypen und versorgt den späteren Mirror mit Versions-Watermark und Advice. Alte Session-/Generationcallbacks verworfen, Shutdown bereinigt Pendingfutures.
- Echter Clienttransport am gepinnten Server über Loopback-TCP/WebSocket und Produktions-FastAPI-Route, 46 geprüfte Server-Pythonquellen. Recorder/Scheduler und noch offene Settings-/Audioclientgrenzen sind transparent ersetzt; echter Hardware-/ASR-/Qt-Gesamttest folgt in späteren Paketen.
- Umsetzungstestnachweise **als Fremdbeleg unabhängig gelesen**: Windows 11 / Python 3.12.10, volle Suite **1290 PASS**, Codec/Transport **57 PASS** (`-W error`), gepinnte Serverapp **21 Checkpointfälle PASS**, compileall Exit 0. Runtime, Befehle, Exitcodes, vollständige Logs und SHA256 in [Windowsvalidation](https://github.com/marcosudau-vps/voice-stt-client/blob/2b79a9a23a6be554a2a2a05ff3256a63ccf022d4/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/windows-validation.json). Beide Unittestlogs enden mit OK; simulierte UI-Fehlertraces im Volltestlog stammen aus Negativtests. Finale GitHub-CI [38179921718](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38179921718): completed/success.
- ACK-01..21 sind im aktuellen Code/Tests und Traceability durch tatsächliche Methoden belegt. Für RECONNECT-02/03/06 bestehen folgende konkrete Lücken; der vorhandene Testgrünstatus beweist deren korrekte Behandlung nicht.

## Pflichtfinding CV2-020-R02-F01 – HTTP-Upgrade-Ausnahmen verlassen Reconnectschleife

**Schwere HOCH**, Owner AP-CV2-020-Umsetzer. Anforderungen **RECONNECT-03/06**, K-01/K-04.
**Fundstelle:** [v2_transport.py:183–210](https://github.com/marcosudau-vps/voice-stt-client/blob/2b79a9a23a6be554a2a2a05ff3256a63ccf022d4/voice_stt_client/core/v2_transport.py#L183-L210) und [237–240](https://github.com/marcosudau-vps/voice-stt-client/blob/2b79a9a23a6be554a2a2a05ff3256a63ccf022d4/voice_stt_client/core/v2_transport.py#L237-L240).

**Repro / actual:** Injizierten `connector` beim WebSocket-HTTP-Upgrade eine `websockets.exceptions.InvalidStatus` (HTTP 503 eines vorgeschalteten Reverse Proxy) werfen lassen. `run()` behandelt zwar ConnectionClosed, OSError, TimeoutError u.a., nicht aber InvalidStatus aus dem Upgrade. Deshalb entkommt die Exception aus dem Run; nur äußeres Cleanup und Status CLOSED erfolgen. Es gibt **keinen BACKOFF und keinen späteren Wiederverbindungsversuch**.

**Expected:** Temporäre 502/503-/Upgradefehler verursachen begrenzten Backoff mit erneuter Verbindungsaufnahme; dauerhafte Konfigurations-/Autorisierungsablehnungen sind sichtbar und ohne Endlosschleife blockiert. **Wirkung:** Ein zeitweise gestörter Proxy kann den Client auch nach dessen Erholung dauerhaft offline halten. **Verlangter Nachweis:** connector-mock HTTP 503→Reconnect→READY, unrecoverable 403/Handshake-Konfigfall mit klarer Einordnung, keine Hotloop/Pendingleaks, anschließend Kandidatenregression.

## Pflichtfinding CV2-020-R02-F02 – 4408-Fehlerzähler wird nach READY nicht zurückgesetzt

**Schwere MITTEL**, Owner AP-CV2-020-Umsetzer. Anforderungen **RECONNECT-02**, K-01 Close-Matrix.
**Fundstelle:** [v2_transport.py:149,197–200](https://github.com/marcosudau-vps/voice-stt-client/blob/2b79a9a23a6be554a2a2a05ff3256a63ccf022d4/voice_stt_client/core/v2_transport.py#L197-L200), READY-[272–273](https://github.com/marcosudau-vps/voice-stt-client/blob/2b79a9a23a6be554a2a2a05ff3256a63ccf022d4/voice_stt_client/core/v2_transport.py#L272-L273), [vorhandener 4408-Test](https://github.com/marcosudau-vps/voice-stt-client/blob/2b79a9a23a6be554a2a2a05ff3256a63ccf022d4/tests/test_v2_transport.py#L327-L341).

**Repro / actual:** 4408 beim ersten Connect setzt `_silent_failures=1`; der Retry gelingt vollständig (Admission, Bootstrap, READY). Danach bricht eine andere Verbindung ab; ihr erster neuer 4408 zählt als `_silent_failures=2` und blockiert dauerhaft als `repeated_hello_timeout`, weil bei Erfolg allein `_attempt`, nicht der 4408-Zähler, zurückgesetzt wird.

**Expected:** Ein erfolgreicher Bootstrap trennt die Timeout-Episoden. Die neue erste 4408-Stille erlaubt wieder einen einzelnen Retry; nur 4408→4408 ohne erfolgreichen Zwischenconnect blockiert. **Wirkung:** Ein einzelner späterer transienter Fehler kann den Client permanent blockieren. **Verlangter Nachweis:** Tests für 4408→4408 BLOCKED und 4408→READY→4408→READY plus definierter Zählerreset.

## Reviewentscheidung und Übergabe

| Gate | Ergebnis |
| --- | --- |
| PR-Parent, Head/Tree, Vorgängerprovenienz, Server-Baseline | PASS |
| Vollständige betroffene Produkt-/Testcode-Sichtung | PASS als Reviewmethode; zwei fachliche Pflichtfindings |
| Externe Windowsvollsuite 1290, targeted 57, Servercheckpoint 21 | PASS als validierter **Umsetzer-Fremdbeleg** |
| Eigene Windows-Vollsuite/Hardware/ASR | NOT_RUN, gemäß Reviewvertrag für AP020 nicht nötig |
| HTTP-Upgrade-Recovery und 4408-Reset | FAIL (statische Reproduktion); gezielte dynamische Regression noch NOT_RUN |
| Root-PASS / kanonische Übernahme / AP030 | **NICHT ERTEILT**, nicht beauftragt |

**F01/F02 sind Pflichtfindings**, keine optionalen Optimierungen. Nächste Aktion: explizit beauftragter Korrekturlauf in **demselben PR #4**, gezielte Tests und anschließend erneut vollständige kandidatengebundene Windowsregression samt betroffenem gepinnten Servercheckpoint. Anschließend frischer unabhängiger Review des neuen kumulativen Kandidaten; keine automatische Übernahme und kein AP030. Die hier erstellte Reviewdokument-SHA ist **nicht** die reviewed_sha.
