# AP-CV2-070 / R01-UMSETZUNG – REVIEW_READY

Stand 2026-10-12. Vollständiger Umsetzungsselbstcheck **SELF_CHECK_PASS / REVIEW_READY**; unabhängige Abnahme offen. Keine offenen Umsetzungsfindings. Paketbranch ab Übergabe für Umsetzungsänderungen pausiert, kein eigener ROOT_PASS, Merge oder AP080-Start.

## Auftrag und Provenienz

[Originalauftrag](00_PROMPT_ORIGINAL.md), [Paketvertrag](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-070.md), [Einstiegsskill](../../../../PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md), [Umsetzungsskill](../../../../PLANUNG/SKILLS/voice-stt-client-v2-umsetzen/SKILL.md). Verwendete Eingangsvertragsblobs sind mit SHA256 am kanonischen Parent in [input-provenance.json](EVIDENCE/input-provenance.json) gesichert. Fortsetzungssteuerung separat in ZUSATZPROMPTS.

Startparent/aktuelle feat/client-v2-Basis `473a75d02fb6d00e5664af4328dadaa44da5191a`; Paketbranch `work/client-v2/ap-cv2-070`; Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. [AP060-Startprüfung](EVIDENCE/predecessor-canonicalization.json) belegt unabhängigen R04-PASS, tatsächlichen R05-Freigabeprompt, PR8 MERGED, Single-Parent ce95c66 und Baumgleichheit des Aggregats zum finalen AP060-Head 1da7b71. Arbeitsbaum vor Start sauber; Branch vom gefetchten origin/feat/client-v2 erstellt. Keine fremden WIP übernommen.

Normale Paketbranch-Commits/Pushes, PR gegen feat/client-v2 und sachlicher Handoff sind durch den [workflowweiten Originalauftrag AP000](../../../AP-CV2-000/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md) autorisiert. Kanonische Promotion bleibt an unabhängigen PASS und einen neuen ausdrücklichen menschlichen Übernahmeprompt gebunden.

Der getestete Kandidat ist reproduzierbar über Parent, genauen staged Produktdiff und 199 qualifizierte Produkt-/Test-/CI-/Konfigurationsblobs im [Windowsmanifest](EVIDENCE/windows-validation.json) identifiziert. Finale Commit-ID/Tree werden außerhalb des erzeugenden Commits in der PR-Beschreibung und Übergabe genannt. Nach Qualifikation ausschließlich Dokument-/Akten-/administrative Änderungen; endgültige Blobgleichheit gesondert verifiziert.

## Ergebnis und Umsetzungsskizze

Die vor Implementierung ausgeführte Baseline umfasst 172 einschlägige Tests. Umsetzung: (1) reine V1-Profilmigration und explizite atomare Persistenz, (2) begrenzter HTTP-Service und unveränderliche Katalog-/Schema-/Reporttypen, (3) Pre-Hello-Metadatenprüfung und bestätigter NA-Bootstrap im vorhandenen Transport-/Medienpfad, (4) Konflikt-/Revision-/Recoveryfälle und echter gepinnter Servercheckpoint, (5) gesamte Windowsregression und Abgabeunterlagen.

`core/v2_profile.py` implementiert Schema2, explizite Triggerflags, exakte Sekunden→ms-Konversion, Sichtbarkeit widersprüchlicher/ungelöster Werte, Controlmigration, Katalogauflösung, Backup und atomaren Dateireplace. Alte Mode-/extension-/warning-Felder steuern den V2-Pfad nicht. V1 und lokale Präferenzen bleiben erhalten. Ein vorhandenes Schema2-Profil wird niemals aus alten Feldern abgeleitet. Offline/unavailable/ungültige Auswahl bleibt sichtbar blockiert und reparierbar.

`core/settings_service.py` stellt HTTP, Schema, dynamischen Wake-Katalog und Settingsservice auf dem asyncio-Core bereit. 18/16/15-Feldmengen, getrennte Session-/Serverrevisionen, echte Typen/Grenzen/Crossfieldprüfung, NA-only-Sessionwrites, read-before-patch, einmalige Revisionskonflikt-Neuberechnung mit neuer Command-ID, Snapshotbestätigung, requested/effective/pending/unsupported und begrenzte generationgebundene Hintergrundreads sind umgesetzt. NS-Noise/VAD wird nicht als individuell anwendbar ausgegeben. Wake-Auswahl wird ausschließlich für einen neuen Hello gespeichert; die ganze Auswahl benötigt ein gesundes gemeinsames Backend. Kalibrierungsmetadaten bleiben pending.

`core/v2_transport.py` benötigt einen kleinen Pre-Hello-Hook, damit Profile/Katalog vor Admission feststehen. Die bootstrapinterne Patchablehnung ist gezielt für eine Konflikt-Neuberechnung zugelassen; der Settingsservice muss anschließend bestätigen. Bestehende übrige Bootstrapfehler bleiben blockierend. `core/config.py` und `config.yaml` transportieren das optionale Schema2-Profil ohne automatische V1-Appmigration. Keine Änderung am funktionierenden V1-Core, an QT-/Credential-/Appkomposition oder am Serverprodukt.

Vollständige Anschlussbeschreibung mit tatsächlichen APIs, Callbackreihenfolge, Shutdown, Generation-/Sessionguards und Reparaturpfad: [protocol-v2-settings.md](../../../../../../../docs/protocol-v2-settings.md). SET-01…19 und WAKE-01…10 sind [einzeln mit Methoden/Fällen belegt](EVIDENCE/requirement-coverage.md), Matrix und Requirements-JSON konsistent; deren unabhängiger Status bleibt CLIENT OPEN.

## Entscheidungen und Grenzen

Standardbibliothek-HTTP über `asyncio.to_thread` vermeidet eine neue Produktdependency. TLS wird verifiziert, Origin/Festpfade/Redirects/Responsegröße begrenzt; nach Timeout/Cancellation wird ein laufender Worker gehalten. Unklarer Adminpatch wird gelesen und als unklar gemeldet, niemals automatisch wiederholt; Keys werden nicht gespeichert oder in Fehlern ausgegeben. Die 5-s-Defaults sind begründete Timeouts, keine empirisch optimalen Kalibrierungswerte.

Die bisherigen vorgeschlagenen getrennten Metadaten-/Serviceorte sind im kleinen gemeinsamen `settings_service.py` realisiert; vorhandener Codec und Transport werden weiterverwendet. Interne Entscheidung, keine Verschiebung von Requirementownern. Katalogrevision ist entsprechend gepinntem Ist-Server eine Ganzzahl. Migration arbeitet vor Defaultlayering, damit widersprüchliche reale Nutzpräferenzen nicht durch künstlich hinzugefügte Defaultfelder entstehen.

AppConfig hält V1-Felder absichtlich unverändert; ungültige V1-Felder können dessen bisherigen Load weiterhin sperren. Rohmapping/V2Profile liefern den expliziten Reparaturpfad; Appkomposition und UI-Persistenzintegration folgen AP100/AP080. Servicewrites sind Intentänderungen im Speicher, keine heimliche Configpersistenz. Offene Input-/Drain-/bewusste Reconnectentscheidungen werden nicht aus Testdoubles in die UI vorweggenommen.

Der Servercheckpoint läuft über TCP auf Produktions-FastAPI-Routen mit tatsächlichem SettingsHTTP/SettingsService, V2STTSession, V2MirrorConnection, V2MediaConnection und AudioCapture. Kontrolliert sind PortAudio, Model-/Artifactengine-Probe, GateAwareRecorder/AutoScheduler und synthetische WakeHit-Ausgaben; Sharedcontroller, HTTP-/WS-Verträge und PCM-Ingest sind real. Kein Kontakt zum Produktivserver, keine Serverproduktänderung. SHA-verifizierte 46 importierte Serverblobs, im Supplementlauf 48. Empirische Nutzsprachgrenze, reale ASR/Hardware und optimale Wakekalibrierung **NOT_RUN**, gehören AP-IV2-020. Kontrollierte trailing-edge/Historyclamp/Gainfälle sind bestanden. Server-Distributed bleibt offen.

## Validierung und Selbstkorrekturen

Runtime Windows11 10.0.26300, Python3.12.10 aus Projektvenv, PySide6 6.11.1, websockets17.0.1, offscreenQt. Komplette Befehle, Zeit, Exitcode, Loghashes und Runtimeidentität im [Manifest](EVIDENCE/windows-validation.json), Logs im [Evidenzindex](EVIDENCE/INDEX.md).

| Prüfung | Ergebnis |
| --- | --- |
| Baseline vor Codeänderung | 172 Tests PASS |
| Neue Migrations-/Service-/HTTP-/Katalogfälle | 34 Tests, enthalten in gezielter/Gesamtsuite PASS |
| Gezielt einschließlich bestehender Config/Transport/Mirror/Media/Controls/Settings | 243 Tests PASS, `-W error` |
| Tatsächlicher Settings-/Reconnect-/Wake-Checkpoint | 38 Checks PASS |
| Gepinnte Settings-/Wake-/Gain-Supplementtests | 55 Tests PASS, 0 Skips |
| Gesamter Clientcode | 1460 Tests PASS |
| compileall und git diff/cached --check | PASS |
| Akten-/Relative-Link-/Kandidatenblobprüfung | PASS, gesonderte Abgabeevidenz |

Während Entwicklung korrigiert: synthetische ServerVersion-/Revisionfixtures dem gepinnten Vertrag angepasst; Ackfristen im FakeWS auf 0,2 s statt flakender 0,025 s unter Windows angehoben. Produktdefaults unverändert. Ursprünglich ausgewählte optionale Server-TestClient-/Recording-Testmodule benötigten httpx/soundfile und waren deshalb kein Pflicht-PASS. An derselben fachlichen Grenze nachgewiesen: echte TCP-HTTP/WS-Routen plus verfügbare gepinnte modelunabhängige Wakeboundary-/Gain-Tests; kein ursprünglicher Clienttest entfernt, kein Pflichtfall geskippt. Ganzer qualifizierter Stand nach Ergänzung der vier Detector-Gain-Tests erneut getestet. Die finale Qualifikation ersetzt Zwischenlogs; diese werden nicht als erfolgreiche Abgabebelege verwendet.

## Übergabe und Stop

Unabhängiges Review gegen den endgültig veröffentlichten PR-Head; sämtliche Produkt-/Test-/Konfigurationsblobs müssen zum Windowsmanifest passen. Reviewer kann commitgebunden die vollständigen Windowsnachweise prüfen; erneute lokale Windowsvollsuite ist keine Pflicht. Pflichtbefunde als CHANGES_REQUIRED zurückgeben. Kein eigener PASS, kein Merge, kein Folgepaketstart. Vollständige technische Abgabecheckliste im Report erfüllt; endgültiger PR-/CI-/Aktenabgleich gehört zur Veröffentlichungsevidenz. Nach Übergabe Umsetzungsbranch-Schreiben pausiert.


## PR-Bereitstellung

[PR #9](https://github.com/marcosudau-vps/voice-stt-client/pull/9) gegen feat/client-v2, qualifizierter erster Umsetzungscommit `8b68b4840c7955cd06a2be14736678d83ee729dc` / Tree `cd46b9047762829e89dd8f5fd95e5f66d0a9032e`. Anschließende PR-/Verifikationsverweise sind rein administrativ. Finale SHA/Tree und CI-Ergebnis extern in aktueller PR-Beschreibung/Handoff; keine Selbsteinbettung eines noch zu erzeugenden Commits. Der PR ist der Codex-Aufgabe angehängt.
