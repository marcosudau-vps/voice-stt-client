# AP-CV2-000 / R01-UMSETZUNG

Datum 2026-10-11. Rolle Umsetzer; kein unabhängiger Review.

## Ausgang und Auftrag

READY_FOR_IMPLEMENTATION auf Revision 10; keine offenen Paket-PRs oder aktiven Paketlinien. Sauberer Checkout; neuer Branch `work/client-v2/ap-cv2-000` auf `050e776cf316eb332177294db0c0a2719c2b4415`. Dies ist der kanonische Parent. [Originalauftrag](00_PROMPT_ORIGINAL.md) erteilt workflowweite Kandidatenrechte, keine Übernahmefreigabe.

Featurequellen `8bab1b3f4aa070d0756c305908def4d9ebc52582` und `a80a6b17b40751740f9c9d2aef9cad32b0470c0c` besitzen beide Tree `471197bc6473b8fb10e908c3313093edd96b2253`. Releasequelle `f625904795880ce71acec216e43678f9ec1656d0`; gemeinsame Gitbasis `1b432c97e0be2985fc23e9e9a36b51cfeba7631b`. Serverreferenz unverändert `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

## Baseline und Umsetzungsskizze vor Produktänderungen

Projektvenv: lokaler `venv`-Junction auf die bestehende Client-Projektumgebung in `main/venv`; Python 3.12.10. Alle Pythonaufrufe benutzen diese Umgebung. Releasebaseline separat aus dem Gitarchiv, ohne Eingriff in den vorhandenen Releasecheckout mit untracked `assets/`.

- Feature: `python -m pytest -q`, offscreen: 1192 passed, 98.03 s.
- Release: derselbe pytest-Aufruf scheitert bei Sammlung an ungepräfixtem `test_event_protocol`; unverändertes `unittest discover` besteht mit 1147 Tests, 94.012 s. Featurekorrektur des Imports bleibt erhalten.
- Belege: [EVIDENCE](EVIDENCE/INDEX.md), getrennte Baselinelogs und Gitidentitäten.

Umsetzung: Featurecode samt sämtlichen Tests nach `voice_stt_client` verschieben; kompatible Releaseänderungen dateiweise über die gemeinsame Basis portieren. Namespaceänderungen mechanisch, Loggingkomponentennamen und Wireverhalten erhalten. Konflikte: Feature-Warnungs-Wait in AP06 statt zeitabhängigem Release-Sleep; sämtliche Trigger-Logging-Hooks mit neuen Quellpfaden erhalten. Ressourcen, Pfade/CLI, native Hotkeyerfassung, Version und Buildguards portieren. Vollständige kombinierte Suite plus isolierte Wheel-/sdist-Installation qualifizieren; CI-Pfad für Feature-PRs herstellen. Kein V2-Lifecycleumbau.

## Ergebnis und Interfaces

REVIEW_READY: technische Selbstchecks des AP-CV2-000 vollständig, kein unabhängiger PASS. Der finale Kandidat ist der nach sämtlicher Aktenpflege eingereichte PR-Head von `work/client-v2/ap-cv2-000`; dessen SHA/Tree werden aus Git und in der PR-Übergabe bestimmt. Erwarteter kanonischer Parent: `050e776cf316eb332177294db0c0a2719c2b4415`. Vollständiger Diff: `git diff <Parent>...<Kandidaten-SHA>`. Produktbytes des qualifizierten Arbeitsstands sind durch beide Installationsmanifeste und `source-preservation.txt` gebunden. Finale Git-/PR-Identität folgt als rein administrativer Nachtrag; kein Selbst-SHA im Commit.

`voice_stt_client` ist der einzige Produktnamespace; Ressourcen liegen im Paket. Start über `python -m voice_stt_client` oder installierten Console-Entrypoint `voice-stt-client`; `app.main(argv)` erhält `--config`, `--headless`, `--version` und den nebenwirkungsfreien `--verify-gui-runtime`-Importsmoke. `AppConfig.load(override_path=..., user_path=...)` schichtet explizite Profile auf Paketdefaults und speichert sie mit `save_user()` an die gewählte Datei zurück. CLI hat Vorrang vor Env; eine fehlende explizite Env-Datei scheitert statt auf Legacy zurückzufallen. Ohne explizite Auswahl wird Legacy-Konfiguration nur gelesen, spätere Speicherung erfolgt im neuen Benutzerroot. History nutzt eine bestehende Legacy-DB in situ; kein Copy/Delete/Schemawechsel. Eventcursor bleibt am bisherigen Pfad. Details: [Kompatibilität](../../../../../../../docs/compatibility.md).

Native `QKeySequenceEdit` erfasst Hotkeys (Meta→Win). Alternativen werden erst nach echter Backendregistrierung wirksam; konflikthafte Apply-Vorgänge rollen zurück. Deaktivierte Hotkeys und Wake-only-Sessions bleiben deaktiviert und starten; Legacy-Triggerflags werden im Editor mit ihren effektiven Werten angezeigt. Kein globaler Hotkey in Wake-only. All-null-Legacy-Sounds erben gebündelte Defaults; `sounds_enabled=false`, Custompfade und einzelne Nullwerte bleiben erhalten. Die 1.0.0-Version ist die portierte V1-Ressourcenidentität, kein V2-Release.

Controller/STTSession behalten vollständig den Featurecode abgesehen von Imports: Serverereignisse treiben weiterhin fachliche Zustände und Feedback; Pending-/Ackkorrelation, Generation-/Sessionguards, Callbackreihenfolge und Audiostreamregeln sind nicht neu entworfen. Kein lokaler zweiter Lifecycle. Die zweite Activation sendet nach Finish weiterhin erneut start; der produktionsnahe Charakterisierungstest bleibt erhalten. Wire-/Transportumbau CV2-010/020, Audiopfad CV2-040, Integration CV2-100.

## Integrationsentscheidungen und Fehlerbehebung

- Dreiweg-Inhaltsport über gemeinsame Basis; kein Historymerge/Rebase. Dateiweise Regeln und Provenienz stehen in [Übernahmematrix](EVIDENCE/UEBERNAHMEMATRIX.md).
- Zwei Konflikte: Feature-Event-Wait statt Release-Sleep im AP06-Test; sämtliche Feature-Trigger-Logging-Hooks zusätzlich zum neuen Quellpfad erhalten.
- Erster kombinierter Lauf: 1211 pass/3 fail (zwei verschobene Ressourcenpfade und Nullable-Flag-Roundtrip). Pfade mechanisch aktualisiert; Test vergleicht effektive Legacyflags. Kein Funktionsfall entfernt.
- Drei gezielte Repros zeigten Release-Inkompatibilität: Startup erzwang deaktivierte Hotkeys, Editor-Sync verlor effektive Legacyflags, CI-Push fehlte Featurebase. Kleinste Fixes im Application-/Editor-/Workflowanschluss; anschließend 184 gezielte Tests grün. Zusätzlicher Env-Profil-Negativtest schützt fehlendes explizites Profil vor Legacy-Rückfall.
- `test_history` isoliert nun auch `Path.home` und `VOICESTT_CLIENT_HOME`, damit neue Benutzerpfade keine reale Anwenderhistory als Testfixture benutzen. Keine Anwenderdaten im Diff.
- Die Release-pytest-Sammlungsstörung bleibt als Baseline-FAIL sichtbar; Release-Unittest vollständig grün, bestehender Feature-Importfix im integrierten Stand erhalten.
- V1-Build-/Releaseguards portiert. CI läuft für Feature-PRs und Feature-Pushes. Tag-first-Publishing im lokalen Release-Skript deaktiviert; Releaseworkflow bleibt separat menschlich ausgelöst und auf main begrenzt. Kein Workflowdispatch/Tag/Release ausgeführt.

## Validierung

Windows, Projektvenv Python 3.12.10, Qt offscreen, PYTHONUTF8=1. Jeder folgende Pythonbefehl benutzt `.\venv\Scripts\python.exe`. Keine Skips in den vollständigen integrierten Suites.

| Prüfung | Ergebnis | Beleg |
| --- | --- | --- |
| Feature `-m pytest -q` vor Änderungen | PASS: 1192 / 98.03 s | [Baseline](EVIDENCE/baseline-feature.txt) |
| Release `-m pytest -q` vor Änderungen | FAIL: Sammlung test_event_protocol | [Baseline](EVIDENCE/baseline-release.txt) |
| Release `-m unittest discover -s tests -v` | PASS: 1147 / 94.012 s | [Baseline](EVIDENCE/baseline-release-unittest.txt) |
| Gezielte Integration/Prefs/Trigger/Buildfälle | PASS: 184 / 8.16 s | [Fokus](EVIDENCE/focused-tests.txt) |
| Gesamter Client `-m pytest -q` | PASS: 1221 / 95.19 s | [pytest](EVIDENCE/tests-pytest.txt) |
| Gesamter Client `-m unittest discover -s tests -v` | PASS: 1221 / 95.823 s | [unittest](EVIDENCE/tests-unittest.txt) |
| `-m compileall -q voice_stt_client scripts tests`; `git diff --check` | PASS | [Checks](EVIDENCE/final-checks.txt) |
| `-m build --sdist --wheel`; `-m twine check dist/*.whl dist/*.tar.gz` | PASS | [Build](EVIDENCE/packaging-build.txt), [Twine](EVIDENCE/packaging-check.txt) |
| Wheel und sdist `pip install --no-deps --target <getrennte Tempziele>`; Smoke aus Temp-CWD | PASS: kein Sourceimport; Namespace, Config, acht WAVs, Attribution, Entrypoint, Version, GUIimports | [Wheel](EVIDENCE/wheel-smoke.txt), [sdist](EVIDENCE/sdist-smoke.txt), [Skript](EVIDENCE/installed_smoke.py) |
| Quellen-/Artefaktvergleich | PASS: controller/stt_session nur Imports; Triggerassertions erhalten; Assets bytegleich; beide Paketmanifeste gleich Source | [Vergleich](EVIDENCE/source-preservation.txt), [Skript](EVIDENCE/qualify_sources.py) |

Zusätzlicher lokaler Frozen-Build/Qt-Smoke wird im Evidenzindex mit tatsächlichem Ergebnis geführt. Er ersetzt kein finales V2-Frozen-Gate. Wheel-/sdist-Hashes: [SHA256](EVIDENCE/artifact-hashes.txt). Die automatisierte Regression ersetzt keine physische Mikrofon-, Win32-Hotkey-, Clipboard-, LED-/Soundwahrnehmung oder Live-ASR-Prüfung. Diese Gesamtnachweise sind hier NOT_RUN und bleiben CV2-110/IV2-020 zugeordnet. Der verpflichtende CV2-000-Zwischencheckpoint (integrierte Basis, erhaltene Trigger/Logging/Feedback, Gesamtsuite und Import-/Wheel-Smoke) besteht in technischen Selbstchecks. Serverreferenz ada13b0 ist unverändert; kein Client-/Server-V2-Socket-Smoke behauptet oder für AP000 vorgeschrieben.

Zusätzliche Dokumentprüfung: allgemeines `Test-Arbeitsstruktur.ps1` PASS (0 Fehler/0 Warnungen). `Test-Arbeitsblock.ps1` passt zum älteren Blockschema: bereits am unveränderten Revision-10-Parent sechs Fehler; mit der ausdrücklich vorgeschriebenen `30_AUSFUEHRUNG`-Runablage sieben. Die aktuellen V2-Regeln schreiben genau diese Ablage vor und ersetzen die widersprechenden historischen Metadaten-/Pflichtordnerregeln. Dieser alte Blockvalidator wird daher **SKIPPED_EXPECTED / nicht auf V2 anwendbar** eingeordnet; tatsächlicher FAIL und Baseline sind erhalten, kein Fake-PASS. Kein Umbau des allgemeinen Skills oder der verbindlichen Runstruktur. `check_records.py` prüft stattdessen die aktuelle V2-Struktur, alle zwölf Requirementbelege, Originalfreigabe, relativen Aktenlinks, offene Abnahme/Freigabe und genau einen R01-Meilenstein.

## Requirementbelege

Alle BASE-IDs bleiben `CLIENT OPEN` bis zur unabhängigen Abnahme. Die folgenden Implementierungsnachweise gelten für den eingereichten Paketkandidaten; Matrix/Requirements verweisen separat hierher.

| ID | Tatsächliche Prüfung | Beleg |
| --- | --- | --- |
| BASE-01 | Gitfall: source-identities.txt und Start-/Endrefabgleich | [Runbeleg](EVIDENCE/source-identities.txt) |
| BASE-02 | tests.test_trigger_lifecycle (sämtliche Methoden); tests.test_trigger_feedback_contract (sämtliche Methoden); StreamRestartsAfterFinishWithAFaithfulDouble.test_a_second_activation_resends_start_despite_the_finish_comment; qualify_sources.py: namespace-only controller/stt_session/Featuretests | [Runbeleg](EVIDENCE/source-preservation.txt) |
| BASE-03 | tests.test_history, test_text_injector, test_feedback_mapping, test_feedback_reducer, test_obs010_* bis test_obs060_* (sämtliche Methoden); IntegratedPreferences.test_explicit_profile_keeps_feature_flags_and_preferences_on_roundtrip | [Runbeleg](EVIDENCE/tests-unittest.txt) |
| BASE-04 | Baseline Feature: pytest 1192; Release: unittest 1147; kombiniert: pytest und unittest je 1221 | [Runbeleg](EVIDENCE/tests-pytest.txt) |
| BASE-05 | IntegratedPreferences.test_existing_legacy_history_is_read_in_place_without_loss; IntegratedPreferences.test_environment_profile_never_silently_falls_back_to_legacy; Gitfall: sauberer Start, fremde Worktrees nur inventarisiert | [Runbeleg](EVIDENCE/start-status.txt) |
| BASE-06 | Gitfall: unveränderte Remote-Refs, keine Serveraktionen; workAuthorization verbietet Promotion | [Runbeleg](EVIDENCE/start-remote.txt) |
| BASE-07 | Gitfall: source-identities.txt; UEBERNAHMEMATRIX.md; namespace-normalisierter Vergleich qualify_sources.py | [Runbeleg](EVIDENCE/UEBERNAHMEMATRIX.md) |
| BASE-08 | IntegratedPreferences (alle sieben Methoden); TestConfigValidation.test_explicit_profile_layers_packaged_feedback_and_saves_back_to_profile; TestGlobalHotkeyManager.test_disabled_manager_never_touches_backend; BuildScriptTests.test_release_build_requires_qualified_python_patch; tests.test_client_release_guard, test_client_release_workflow | [Runbeleg](EVIDENCE/tests-unittest.txt) |
| BASE-09 | installed_smoke.py: Wheel UND sdist außerhalb Source; compileall; twine check; vollständige Regression | [Runbeleg](EVIDENCE/wheel-smoke.txt) |
| BASE-10 | Gitfall: Paketbranch Parent 050e776cf316eb332177294db0c0a2719c2b4415; Featurebranch unverändert; PR Base feat/client-v2 | [Runbeleg](EVIDENCE/start-status.txt) |
| BASE-11 | Administrativer Fall: REVIEW_READY, reviewedCommit/humanApproval null; Schreibrecht abgegeben; kein Folgepaketstart | [Runbeleg](EVIDENCE/INDEX.md) |
| BASE-12 | assertion-inventory.json; UEBERNAHMEMATRIX.md mit allen fünf Assertionnachfolgern; getrennte Baselines und vollständige Regression | [Runbeleg](EVIDENCE/assertion-inventory.json) |

## Abgabecheckliste und nächste Aktion

Fachliche Liefergegenstände, zugeordnete Methoden, Baselines/Repros/Gesamtregression, frühe Packaginginstallationen, Produktdokumentation und originale Arbeitsfreigabe sind belegt. Keine neuen Credentials/Schemaentscheidungen; keine Serveränderung. Vorgängerprüfung ist beim ersten Paket nicht anwendbar; Parent ist die tatsächliche Revision-10-Spitze. Paketindex, Workflowstatus, Matrix/Requirements und genau ein Steuerungsmeilenstein für R01 werden gemeinsam auf dem Paketbranch gesichert. Git-/PR-Provenienz und erforderliche CI beziehen sich auf den finalen eingereichten Head/Base-Stand, nicht auf den Versionswert 1.0.0.

Nächste Aktion: frische unabhängige Abnahme von AP-CV2-000 am eingereichten PR-Head gegen den vollständigen Parentdiff. Keine Eigenabnahme. Ab REVIEW_READY sind Paketbranchänderungen und Pushes des Umsetzers pausiert; `writeOwner=null`. Unabhängiger PASS, menschlicher Übernahmeprompt und tatsächlicher kanonischer Einzelaggregatcommit sind vor CV2-010 zwingend. Keine fachlichen Pflichtfindings als erledigt erfunden, kein PASS vorweggenommen. Server-Distributed bleibt offen.
