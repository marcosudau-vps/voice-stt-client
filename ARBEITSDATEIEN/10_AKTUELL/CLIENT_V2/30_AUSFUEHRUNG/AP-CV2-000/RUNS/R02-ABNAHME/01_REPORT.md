# AP-CV2-000 / R02-ABNAHME – unabhängiger Review

**Datum:** 2026-10-11. **Verdict: CHANGES_REQUIRED.** Technische statische Prüfung mit einem konkreten Produktfinding; zwingende eigene Windows-Regression **NOT_RUN**. Keine Produkt- oder Testdateien geändert. Keine kanonische Übernahme.

## 1. Auftrag, Scope und Identität

- Originalauftrag: [00_PROMPT_ORIGINAL.md](00_PROMPT_ORIGINAL.md)
- Repo: `marcosudau-vps/voice-stt-client`; PR: [#2](https://github.com/marcosudau-vps/voice-stt-client/pull/2)
- Base: `feat/client-v2`; Kandidat: `work/client-v2/ap-cv2-000`
- **reviewed_sha:** `8b1c4c157b6b431dac6af69e2e264d0c37579bef`
- **reviewed_tree:** `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e`
- **canonical_parent:** `050e776cf316eb332177294db0c0a2719c2b4415` (unveränderter Ziel-HEAD)
- **server_sha:** `ada13b011e1d3829f78e7f389e3b927795a2b3be` (unveränderte, weiterhin offene Server-Distributed-Linie)
- Planstand: Revision 10, AP-CV2-000; vorgeschriebener Zwischencheckpoint ist kombinierte Clientsuite, Trigger-/Logging-/Feedbackerhalt und Import-/Wheel-Smoke. Ein V2-WebSocket- oder Hardware-Endgate gehört ausdrücklich **nicht** zu diesem Paket.
- Prüfumfang: Git-/PR-Provenienz, 226 geänderte Pfade klassifiziert, Umsetzung/CI/Übernahmematrix als vorhandene Fremdbelege gesichtet; gezielte statische Inspektion von Config-/Legacy-/History-/Hotkey-/UI-/Startup-, Build- und CI-Änderungen. **Kein vollständiger Dateifür-Datei-Checkout-Diff in isoliertem Worktree** und keine eigene Gesamtsuite. Diese methodische Grenze verhindert ROOT_PASS unabhängig vom Finding.

## 2. Ergebnis der tatsächlich nachgewiesenen Prüfungen

| Gegenstand | Befund | Bewertung |
| --- | --- | --- |
| Base/Head/Tree | Base `050e776cf316eb332177294db0c0a2719c2b4415`, Head `8b1c4c157b6b431dac6af69e2e264d0c37579bef`, Tree `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e` über GitHub-Gitobjekte und Branchrefs abgeglichen | PASS |
| Paket/Scope | Feature-/Releaseintegration, `voice_stt_client`-Namespace, V1-Transport belassen; kein behauptetes V2-Paar | Plausibel, ohne eigenen vollständigen Lauf NOT_PROVEN |
| Vorhandene CI | [Run 38145266161](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38145266161): Windows-Job success, 1221 Tests/OK, compileall, EXE, Wheel/sdist/Twine und installierter Wheel-Smoke | PASS **externer CI-Beleg** |
| Implementierungs-Selbstchecks | [R01-Bericht](../R01-UMSETZUNG/01_REPORT.md): lokale pytest/unittest je 1221, Baselines 1192/1147, Packaging und Quellvergleich dokumentiert | Übernommene Fremdbelege, keine unabhängige Verifikation aller Fälle |
| Kritischer Negativfall Hotkeyfallback bei fehlgeschlagenem Corestart | Kontrollfluss geprüft; eigener Windows-/Qt-Test nicht ausgeführt | Statisches Finding **F01**, dynamischer Nachweis NOT_RUN |
| Eigene vollständige Clientregression | Projektvenv/Windows-Checkout nicht verfügbar | **NOT_RUN / Pflichtgate offen** |
| Reale Win32-/Mikrofon-/ASR-Hardware | Nach Paketvertrag erst spätere CV2-/IV2-Gates | SKIPPED_EXPECTED für AP-CV2-000 |

## 3. Requirement- und DoD-Zuordnung

| Requirement | Unabhängige Bewertung |
| --- | --- |
| BASE-01 | Git-Identitäten/Parent remote PASS; lokale WIP-Isolierung aus R01 nicht eigenständig messbar |
| BASE-02 | Trigger-Controller/Session importbasiert migriert; R01-Testnamen vorhanden, eigenes vollständiges Regressionsergebnis NOT_PROVEN |
| BASE-03 | History/Feedback/Observability im Scope gesichtet; vollständiger Erhalt NOT_PROVEN |
| BASE-04 | Beide Baselines und kombinierte 1221-Regressionssuite in R01/CI belegt; eigene Tests NOT_RUN |
| BASE-05 | Legacy-History-/Config-Erhalt statisch gesichtet; F01 kann Benutzerpräferenz trotz fehlgeschlagenem Start verändern |
| BASE-06 | Kein Server-/Main-Merge, keine Tags oder Releases in diesem Review; Remote-Branchidentität PASS |
| BASE-07 | Feature-/Releasequellen, Report und Übernahmematrix dokumentiert; kompletter mechanischer Quellvergleich nur R01-Eigenbeleg |
| **BASE-08** | **CV2-R02-F01: automatische persistente Hotkeyänderung vor erfolgreichem Corestart; CHANGES_REQUIRED** |
| BASE-09 | Externe Windows-CI PASS, frühes Packaging belegt; eigene vollständige Regression NOT_RUN |
| BASE-10 | PR/Parent korrekt, kanonische Featurelinie nicht angefasst; späterer Merge/Freigabe offen wie vorgeschrieben |
| BASE-11 | Unabhängige Reviewerrolle durchgeführt, aber kein ROOT_PASS; Korrektur und erneuter unabhängiger Vollreview nötig |
| BASE-12 | Assertioninventar und Übernahmematrix vorhanden; alle Nachfolger eigenständig noch nicht vollständig geprüft |

Matrix-/Requirements-Vertragsinhalte werden durch diesen Review nicht geändert; die IDs bleiben offen, bis die tatsächlichen Pflichtnachweise vorliegen.

## 4. Offene Findings

### CV2-R02-F01 – Persistente Änderung der Benutzer-Hotkeys trotz fehlgeschlagenem Anwendungsstart

- **Schwere/Wirkung:** mittel; dauerhafte, vom Benutzer nicht bestätigte Änderung funktionierender Benutzerpräferenzen. Besonders relevant für Wiederanlauf nach vorübergehendem Hotkeykonflikt oder Core-Initialisierungsfehler.
- **Requirement:** BASE-05 (Nutzerdatenpräferenzen erhalten), BASE-08 (V1-Hotkey-/Konfigurationsintegration).
- **Fundstelle:** `voice_stt_client/ui/application.py`, `start()` und `_register_startup_hotkeys()`.
- **Statisch reproduzierbarer Ablauf:** 1) Die ursprünglich konfigurierte Tastenkombination ist anderweitig registriert; `self.hotkeys.register()` schlägt fehl. 2) Ein Ersatz aus `fallback_hotkeys()` wird erfolgreich registriert. 3) Noch während `_register_startup_hotkeys()` ruft der Client **`self.config.save_user()`** auf. 4) Erst danach wird in `start()` `self.bridge.start()` versucht. 5) Liefert die Bridge `False`, wird die Anwendung nicht gestartet, die Profil-YAML enthält aber bereits den zufällig ausgewählten Ersatzhotkey.
- **Expected:** Bei fehlgeschlagenem Start bleibt die bisher persistierte Benutzerbelegung unverändert; ein Ersatz wird erst bei bestätigtem Start bzw. nach nachvollziehbarer Zustimmung persistiert.
- **Actual laut Quellkontrollfluss:** Speichern vor dem Core-Erfolg; keine Rollback-Persistenz im `bridge.start() == False`-Zweig.
- **Reprostatus:** **statisch nachgewiesen, dynamischer Windows-/Qt-Repro NOT_RUN**. Keine behauptete Hardwarebeobachtung.
- **Owner:** Umsetzer AP-CV2-000.
- **Geforderte Korrektur/Nachweis:** Hotkey-Fallback und aktive temporäre Registrierung erhalten, aber persistente Änderung erst nach erfolgreichem Appstart absichern oder bei Startfehler Originalprofil atomar wiederherstellen. Deterministischen Regressionstest mit simuliertem 1409-Konflikt, anschließend `FakeBridge.start()==False`, und Prüfung von Dateibytes/geladenem alten Hotkey ergänzen. Gegenfall erfolgreicher Start, explizit deaktivierte Hotkeys und Wake-only weiterhin prüfen. Danach komplette Regression und Installations-/Smokecheck wiederholen.

### Nachweislücke (kein separater Produktfinding)

Die verbindliche unabhängige Windows-Gesamtsuite, eigene kritische Repros und ein isolierter Checkout auf dem reviewed_sha konnten in dieser Reviewumgebung nicht ausgeführt werden. Die vorhandene grüne CI ersetzt den explizit geforderten eigenen Reviewlauf nicht automatisch. Teststatus `NOT_RUN`; vor einem späteren `ROOT_PASS` ist ein frischer unabhängiger Prüflauf auf realem Windows-Host erforderlich.

## 5. Technisches Verdict und Übergabe

**CHANGES_REQUIRED**, offene Finding-ID `CV2-R02-F01`. Paket-PR bleibt offen und auf `feat/client-v2` gerichtet; Reviewer verändert ausschließlich seine Akte und administrative Status-/Einstiegsverweise. Geprüfter Produktkandidat bleibt `8b1c4c157b6b431dac6af69e2e264d0c37579bef`; ein späterer Review-Dokumentcommit ist **nicht** technisch als neuer Produkt-SHA getestet. PR-Head nach Docs-Push muss gesondert ermittelt werden.

Nächste erlaubte Aktion: Umsetzer übernimmt die neuen Reviewunterlagen, korrigiert F01 im selben Paket-PR und liefert `REVIEW_READY` mit frischen Produkt-/Regressionstests. Danach neue unabhängige Abnahme mit tatsächlich eigenständig ausgeführter gesamter Windows-Clientsuite. Ohne PASS keine menschliche Übernahme; ohne ausdrücklichen Übernahmeprompt weder Squash noch CV2-010.

Evidenzindex: [EVIDENCE/INDEX.md](EVIDENCE/INDEX.md). Review-Meilenstein im `ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md`.
