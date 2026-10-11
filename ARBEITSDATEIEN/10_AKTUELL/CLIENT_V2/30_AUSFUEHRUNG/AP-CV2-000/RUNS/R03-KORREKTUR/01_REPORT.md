# AP-CV2-000 – R03-KORREKTUR

2026-10-11. **Status:** REVIEW_READY (Selbstqualifikation; kein unabhängiges Urteil).

[Tatsächlicher Originalauftrag](00_PROMPT_ORIGINAL.md), [referenzierter Korrekturauftrag](../../../../PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/KORREKTURPROMPT_AP_CV2_000.md), [Bewertung und kompletter Belegsatz](../../../../PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/README.md), [Evidenz](EVIDENCE/INDEX.md).

## Ausgangsbasis und Scope

Lokaler Einstieg `8b1c4c157b6b431dac6af69e2e264d0c37579bef`; veröffentlichte R02-Reviewspitze `2dc251df959f97e2a0bb37b10a1a77486ae6eb5a` vor Änderungen per scoped fetch/fast-forward übernommen. Einzige Vorarbeit: der ungetrackte vorbereitete Belegsatz; er blieb erhalten. [Ausgangszustand und historische Hashes](EVIDENCE/start-state.json). Kanonischer Parent und weiterhin veröffentlichte Featurebasis `050e776cf316eb332177294db0c0a2719c2b4415`; Server unverändert `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

Rolle Korrekturagent auf `work/client-v2/ap-cv2-000`, derselbe [PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2), Base `feat/client-v2`. Original/workAuthorization erlaubt normale Paketbranch-Commits, Push und PR-Übergabe. Kein Merge, Eigenreview, Folgepaketstart oder Zugriff auf externe Workflow Tools. Die finale SHA und Tree werden nach allen Unterlagen tatsächlich aus Git/PR ermittelt und im Übergabekommentar genannt; keine unmögliche Selbst-SHA im Commitinhalt.

Vor erster Produktänderung: relevante Baseline 73 PASS. Skizze: Registrierung vorläufig halten, Ersatz erst nach erfolgreichem Corestart persistieren; bei Fehlern ursprüngliche Hotkeys wiederherstellen. Aktenprüfung und bestehende Übergaberegeln gezielt ergänzen.

## Befunde und Korrekturen

| Befund / Auftrag | Vorher-Nachweis | Korrektur und neuer Nachweis |
| --- | --- | --- |
| CV2-R02-F01 | [Repro vorher](EVIDENCE/repro-before.txt): echte temporäre AppConfig-Profilbytes bereits vor fehlgeschlagenem Corestart überschrieben; 4/5 neue Methoden schlagen fehl, deaktivierte/Wake-only Gegenfälle bestehen. | `DesktopApplication.start` persistiert registrierten Fallback nach Corestart. Bei Corefehler Registrierungen lösen, ursprünglichen Manager und Konfiguration herstellen. Bei Speicherfehler gestarteten Core stoppen und Registrierung/Config zurücknehmen. Erfolgsmeldung nach Speicherung. [33 gezielte Tests](EVIDENCE/focused-after.txt), [12 finale Repro-/Aktenmethoden](EVIDENCE/targeted-final.txt) PASS. |
| Drei R02-Verweise und veralteter Manifeststatus | [Gemeinsamer Prüfer vor Linkfix](EVIDENCE/records-before.txt); [genaues Gitarchiv der R02-Spitze](EVIDENCE/records-baseline-replay.json): 3 gebrochene Links + Statuswiderspruch. | Links vom Paketindex relativ mit `RUNS/R02-ABNAHME/…`. Aktive Zustände während Korrektur IN_PROGRESS/CORRECTION_IN_PROGRESS, bei Abgabe einheitlich REVIEW_READY. PR-Kurzfassung synchronisiert; historische Reports behalten ihr Urteil. [Finale Aktenprüfung](EVIDENCE/records-final.json). |
| Workflow-Nachschärfung | Korrekturauftrag Abschnitte 3a–c. | Reviewerstart prüft isolierten Kandidaten und eigenen geeigneten Testweg; bestehende grüne CI bleibt Fremdbeleg. Rollenwahl gleicht Remote-/PR-/lokalen Stand und aktive Statusquellen ab. Beide Rollen prüfen Links, referenzierte Akten, PR-Kurzfassung und eigenen Docs-Commit vor jeder Übergabe. Generischer read-only-Aktenprüfer, 7 qualifizierende Methoden für verschiedene APs/Zustände und tatsächliche Negativfälle. |
| Vollständige Belegbereitstellung | [Unveränderte Vorbereitungsmetadaten](EVIDENCE/bundle-preparation.json), lokaler Importprüfer PASS vor/nach fast-forward. | Gesamter Satz: 22 Dateien, drei bytegenau erhaltene Archivteile, 6355 archivierte Quelldateien. Vorbereiteter Logeintrag übernommen. Aktualisierte Bereitstellungsmetadaten/Dateimanifest und Remoteprüfung am tatsächlichen Commit, siehe Übergabe und [Remoteprüfer](EVIDENCE/verifiziere_remote.py). |

Der Speicherreihenfolgefehler ist aus dem V1-Release `f625904795880ce71acec216e43678f9ec1656d0` übernommen, wie die erhaltene Bewertung/probe belegt. Kleinste Startkorrektur; keine Hotkey-/Feedback-Neugestaltung und kein V2-Lifecycle. Coremodule unverändert. Echte Profildateien und persistierender AppConfig-Code werden im Test verwendet; nur Core-/Win32-/LED-Adapter sind Fakes. Die fehlerhafte erste historische Auditfixture ist kein Produktrepro. Historische Audit-/Finalisierungsskripte wurden nicht ausgeführt.

## Qualifikation und Traceability

Runtime Windows, Projektvenv Python 3.12.10, Qt offscreen, isolierte synthetische Profile und Installationsziele. Relevante Module vollständig gelesen; Serverwire unverändert, historischer Serverindex nur zur Einordnung. Alle Befehle und Logs im [Evidenzindex](EVIDENCE/INDEX.md).

- Baseline: 73 PASS; F01 vor Änderung reproduziert, nach Änderung alle Gegenfälle PASS.
- Vollständige Clientregression: unittest 1233 PASS / 110.043s; pytest 1233 PASS / 104.09s, keine Skips. Nach Präzisierung zusätzlicher Backend-Assertions erneut vollständiger unittest-Lauf: 1233 PASS / 92.752s, [finales Log](EVIDENCE/tests-unittest-final.txt).
- Wheel/sdist gebaut, Twine PASS; jeweils separat installiert und aus Temp-CWD ohne Sourceimport qualifiziert. Installierte korrigierte application.py entspricht LF-normalisiert dem getesteten Source.
- Windows-EXE gebaut, Versions-/GUIruntime-Smokes PASS; Version 1.0.0, 75.423.632 Bytes, SHA256 `6cdf75b2df2f66341034acee582c3b0b197611f43ebda64bfc48a6d051eca5fd`. Binaries verbleiben lokal in ignorierten Buildverzeichnissen; [Artefakthashes](EVIDENCE/artifact-hashes.json).
- compileall, Diff-/Akten-/neue relative Linkprüfung, unveränderte R01/R02-Hashes und vollständiger Importmanifest-/Archiveinhaltscheck: [Abschlusschecks](EVIDENCE/final-checks.txt), [Aktencheck](EVIDENCE/records-final.json), [Importcheck](EVIDENCE/bundle-check.txt).

BASE-01 bis BASE-12 bleiben CLIENT OPEN. Bestehende R01-Methoden/Assertions bleiben in Gesamtsuite enthalten; R03-`correctionEvidence` in requirements.json und Matrix ergänzt, kein Requirement neu oder selbst angenommen. BASE-05/BASE-08: alle fünf `StartupPersistence`-Methoden (Profil/Corefehler, Erfolg mit Persistierungsreihenfolge/Präferenzen, deaktiviert/Wake-only, Speicherfehler, erneuter Start). BASE-09 zusätzlich aktualisierte Builds/Smokes. Rollemetadaten in Baseline/Manifest gemeinsam Version 6, fachliche Planrevision weiter 10. Gemeinsamer V2-Prüfer ersetzt für laufende Akten den alten nur R01-bezogenen Prüfpfad; R01-check_records.py unverändert, alter allgemeiner Blockvalidator erzwingt keine andere Struktur.

## Bereitstellung und nächste Aktion

Die beiden Paketbranch-Nachträge dienen demselben kumulativen Korrekturkandidaten: zuerst Code/Unterlagen/gesamter Belegsatz, anschließend tatsächlicher Erstpublikationsbeleg und aktualisierte Bereitstellungsmetadaten. Keine zusätzliche Runnummer oder eigenständige Dokumentveröffentlichung. Nach finalem Push alle erforderlichen Dateien erneut am finalen Remotecommit per LF-normalisiertem SHA256, Archive bytegenau, prüfen. Tatsächliche CI des finalen Heads samt Base/Testmerge wird im PR-Übergabekommentar belegt; kein vorhergesagter CI-PASS. Frühere R01/R02-Logs und Reports unverändert.

REVIEW_READY, writeOwner null: neue unabhängige Abnahme des gesamten kumulativen PR-Kandidaten. F01 ist selbst korrigiert, **unabhängiger Recheck offen**; openFindingIds behält F01 bis Reviewer-Schließung. R02-eigene Windows-Gesamtregression bleibt historisch NOT_RUN; der folgende Reviewer muss eigene geeignete vollständige Windows-Nachweise erbringen. Lokale Selbsttests und CI ersetzen dies nicht. Reale V2-/ASR-/Hardware-/Clipboard-/Win32-Bedienabnahme nicht durchgeführt und nicht als PASS behauptet; spätere Pakete bleiben PLANNED. Kein ROOT_PASS oder menschlicher Übernahmeprompt vorhanden. Nach Übergabe Änderungen/Pushes pausieren und stoppen.
