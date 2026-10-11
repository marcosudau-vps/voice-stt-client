# Unabhängige Abnahme – AP-CV2-010 / R02

**Verdict: ROOT_PASS** – 2026-10-11, Europe/Berlin. Es bestehen keine offenen Pflichtfindings (Finding-IDs: keine). Dies ist eine technische Paketabnahme, **keine menschliche Freigabe, kein Merge und kein ACCEPTED**.

[Originalauftrag](00_PROMPT_ORIGINAL.md) · [Evidenzindex](EVIDENCE/INDEX.md) · [Umsetzung R01](../R01-UMSETZUNG/01_REPORT.md) · [PR #3](https://github.com/marcosudau-vps/voice-stt-client/pull/3)

## Unveränderliche Kandidatenidentität

- Repository: `marcosudau-vps/voice-stt-client`; PR #3, Headbranch `work/client-v2/ap-cv2-010`, Base `feat/client-v2`.
- **reviewed_sha:** `7124e5629e24817dd711b2e2b697b9c07aa11dd7`
- **reviewed_tree:** `37b61ff4cab90c18abf8e5bfae920f2e265ad3ab`
- **canonical_parent / tatsächlicher Feature-Base-Head:** `1cf076bd2ed56929b1a3780bc140da51348a8295` (AP-CV2-000-Übernahme, PR #2).
- **server_sha:** `ada13b011e1d3829f78e7f389e3b927795a2b3be` (Distributed-Referenz, keine Serverpromotion).
- **produktiv und mit Windows qualifiziert:** `9838558173b6bd88d4620b20d4e2e9d832e814c7`, Tree `c3a0b826e5d9614ad6dfb80b51815af77f8090bf`. Per GitHub-Commitvergleich sind dessen zwei Nachfolgecommits bis zum geprüften Head ausschließlich administrativ (Dokumente, Status, Traceability, Testbelege), ohne Produkt-, Test- und testrelevante Konfigurationsänderungen.
- **Beurteilungsweg:** frische ChatGPT-Session, commitgebundene GitHub-Dateien, vollständiger PR-Diff gegen den kanonischen Parent (42 Dateien, rund 404 kB Diff), tatsächlicher Vergleich qualifizierter SHA → reviewte SHA. Kein lokaler Reviewer-Checkout. Die Reviewakten werden erst **nach** diesem geprüften SHA als Docs-Commit auf dem Paketbranch abgelegt und sind nicht nachträglich als Produktprüfung des neuen Heads zu verstehen.

## Quellen und unabhängige Prüfungen

Verbindlichen gemeinsamen Einstieg, Abnahmeskill, Start-/Status-/PR-/Ablageregeln, Checkliste, Umsetzungsspielraum, AP-CV2-010 und K-01 bis K-03 gelesen. Alle 790 Zeilen `voice_stt_client/core/protocol_v2.py`, alle 502 Zeilen `tests/test_v2_protocol.py`, den 297-zeiligen echten Servercontract-Harness `scripts/check_v2_server_contract.py`, API-/Folgepaketdokumentation, Originalvektorprovenienz und relevante Änderungen vom Parent geprüft. Der im Harness verwendete Server-Commit und seine 17 Gitbyte-verifizierten Quellmodule stimmen mit dem gepinnten Vertrag überein. Der Checkpoint nutzt echte Parser, Registry, Replaycache, Controller, Ledger, Snapshot-/Event-/Ackprojektoren und unveränderte AST-Audiofunktionen; kontrollierte Wakekatalog-Adapter und fehlende Socket-/ASRintegration sind ausdrücklich abgegrenzt.

Codekontrolle: Wirevokabulare fünf Commands / vier Aktionen / 15 Ackcodes / fünf Phasen / 18 Events; kanonische UUIDs; bool/int-Trennung; Pflicht-, nullable- und additive Felder; disjunkte Activate-/Control-Formen; Events inklusive Sequenzhülle unbekannter Typen; Snapshot mit zwei vollständigen 16-Key-Maps und geordneten pendingActivations; getrennte Settingsschema-/Read-/Patchantwort und Revisionscopes; Tokenredaktion in LogAccess; bytegleiches Audioformat mit positiven frames, Grenzen und 16/48 kHz. Keine neuen Nebenwirkungen, Transport-, UI- oder Datenmigration im Codecpaket. Unbekannte normale Nachricht wird nicht als Domainwirkung interpretiert.

## Requirement-Matrix – eigenständige Zuordnung

Die folgenden Methoden stehen unter `tests.test_v2_protocol.<Klasse>.<Methode>` (gekürzt dargestellt); konkrete Resultate sind im vollständigen 30-Test-Log und serverseitig ergänzend im 188-Check-Index nachprüfbar.

| ID | abgeglichene fachliche Wirkung | konkrete Methoden / weitere Quelle | Urteil |
| --- | --- | --- | --- |
| WIRE-01 | V2-Vokabular / Endpunkt, keine V1-Domainnachrichten | VocabularyAndVectors.test_vocabulary_and_endpoint_match_pinned_manifest | PASS |
| WIRE-02 | Hello-Hülle, Versionen und Client-Run-ID | ClientMessages.test_hello_builder_and_uuid_generation; ClientMessages.test_hello_missing_required_fields_and_bool_integer | PASS |
| WIRE-03 | Trigger/Selection-Matrix | ClientMessages.test_hello_trigger_selection_and_suppression_matrix | PASS |
| WIRE-04 | Suppression trotz aktiver Wake-Auswahl | ClientMessages.test_hello_trigger_selection_and_suppression_matrix | PASS |
| WIRE-05 | kanonische UUIDs und UUIDv4-Erzeugung | ClientMessages.test_uuid_canonical_not_version_restricted | PASS |
| WIRE-06 | fünf Commands und disjunkte Activation-Aktionen | ClientMessages.test_all_commands_and_controls_encode_without_rewriting | PASS |
| WIRE-07 | verbotene Activate-Kombinationen | ClientMessages.test_forbidden_activation_field_combinations | PASS |
| WIRE-08 | Control-Aktion ohne source und ohne extend | ClientMessages.test_forbidden_activation_field_combinations | PASS |
| WIRE-09 | Envelope-/Payloadfehler und Ack-Reaktionen | ClientMessages.test_command_envelope_and_payload_negatives; ServerMessages.test_all_ack_results_and_phases; Servercheckpoint envelope_rejection/* | PASS |
| WIRE-10 | Ignorierte unbekannte Nachrichten, Correlation/Replay | VocabularyAndVectors.test_vocabulary_and_endpoint_match_pinned_manifest; ClientMessages.test_uuid_canonical_not_version_restricted; Servercheckpoint ignored/* | PASS |
| WIRE-11 | 18 Events, Interim/UnknownEvent | ServerMessages.test_all_18_events_and_required_field_omissions; ServerMessages.test_minimal_and_rich_interim_defensive_optional_fields; ServerMessages.test_unknown_valid_event_preserves_sequence_without_domain_effect | PASS |
| WIRE-12 | Eventtypen, bool/int, nullable/omitted | ServerMessages.test_event_bool_int_uuid_null_negatives; SnapshotsAndSettings.test_snapshot_revisions_bool_and_input_null_omission | PASS |
| WIRE-13 | originale Servervektoren bytegleich, Richtungen/Negativfälle | VocabularyAndVectors.test_vendored_vectors_are_byte_identical_and_hashed; VocabularyAndVectors.test_every_original_vector_is_directionally_classified | PASS |
| WIRE-14 | PCM-Framing bytegleich mit bestehendem Encoder | AudioCodec.test_audio_exact_existing_bytes_16_48khz_mono_stereo_eight_channels | PASS |
| WIRE-15 | Sample-/Channel-/Framegrenzen | AudioCodec.test_audio_sample_channel_frames_limits_and_bool_rejected | PASS |
| WIRE-16 | Metadatenlimit und ungültige Audioframes | AudioCodec.test_audio_metadata_boundary_and_invalid_binary_frames | PASS |
| WIRE-17 | Snapshot, getrennte Settingsrevisionen, LogAccess-Redaktion | SnapshotsAndSettings.test_schema_read_patch_have_distinct_forms_and_revision_scopes; SnapshotsAndSettings.test_hello_accepted_log_token_repr_and_unavailable; SnapshotsAndSettings.test_log_access_shape_paths_identity_expiry_and_no_secret_errors | PASS |

Requirements-JSON und Traceability-Matrix führen dieselben 17 IDs für AP-CV2-010 und verweisen auf die tatsächlichen R01-Implementierungstests. Der Reviewer ergänzt seinen unabhängigen R02-Beleg ohne die fachlichen Kriterien umzuschreiben.

## Unabhängig geprüfte Fremdnachweise

| Pflichtnachweis | Durchführung / reviewed evidence | Entscheidung |
| --- | --- | --- |
| Windowsvollsuite | Windows 11 Build 26300, Python 3.12.10/AMD64, `QT_QPA_PLATFORM=offscreen`, Test-SHA `9838558173b6bd88d4620b20d4e2e9d832e814c7`; vollständiger Aufruf `python -m unittest discover -s tests -p 'test_*.py'`; Exit 0, `Ran 1263 tests in 93.640s`, `OK`; kompletter erreichbarer Log und SHA256 im Windows-Record | **PASS, extern durchgeführt und unabhängig geprüft** |
| Zieltests | `python -m unittest tests.test_v2_protocol -v`; 30 Tests, Exit 0, Log/Hash vorhanden | **PASS, extern durchgeführt und unabhängig geprüft** |
| Realer Servercheckpoint | `python scripts/check_v2_server_contract.py --server-root <gepinnter Export> --server-repository <Server-Gitrepository>`; 188 benannte Checks, Exit 0, 17 bytegeprüfte Servermodule und Server-SHA | **PASS, extern durchgeführt und unabhängig geprüft** |
| Compileall / Diff | `python -m compileall -q voice_stt_client scripts tests` Exit 0; `git diff --check` Exit 0 | **PASS, externe Ausführung und Belege geprüft** |
| Final-Head-CI | GitHub Actions Run [38174781782](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38174781782), complete/success, Windows-Unittests, Compileall, EXE-Smoketest, wheel/sdist und Installations-Smoke erfolgreich | **PASS, unabhängig anhand GitHub-Job/Steps/Log geprüft** |
| Vorher-Baseline | R01-Lauf: 1233 Unittests, 95.998 s, `OK`; historische Shell-Exitcode-Erfassung fehlte, nachfolgende qualifizierte Kandidatensuite enthält echten Exit 0 | **PASS der Baseline-Logaussage; Exitcode dort nicht separat belegt, für Kandidatenqualifikation kein Blocker** |

Die 32 sichtbaren Tracebacks der alten Negativtests wurden mit dem Baseline-Log abgeglichen: beides sind erwartete, absichtlich simulierte Fehler; die Gesamtsuite endet jeweils `OK`, ohne ausgewiesene Skips. Keine entfernten oder abgeschwächten bestehenden Tests im Paketdiff.

**Eigene Windows-/Hardwareausführung:** NOT_RUN; der unabhängige Reviewer hat keine Windows-Vollsuite selbst ausgeführt. Der verbindliche Prüfschritt besteht darin, deren vollständige tatsächliche R01-Evidenz und Kandidatenidentität unabhängig zu verifizieren. Kein reales Mikrofon, ASR, WebSocket, Qt-Integration oder Credential-Manager behauptet. Solche Nachweise sind laut Paket-/Checkpointplan späteren Paketen zugeordnet, nicht AP-CV2-010.

## Akten-, Sicherheit- und Statusprüfung

R01-Originalprompt, Paketbericht, kompletter Windows-Log, gezielter Testlog, Checkpoint, SHA256-Identitäten, Quelle und Provenienz sowie Package-/Status-/Requirementverweise sind im Kandidaten veröffentlicht und wurden anhand commitgebundener Dateien gelesen. Ursprünglicher strukturprüferischer Abgabebeleg: PASS, 26 referenzierte Dateien, 21 Markdown-Dateien, 669 relative Links, null Fehler; zusätzlich neue R02-Verweise vor der Rückgabe separat auf gültige Zielpfade und Statuskonsistenz abgleichen. GitHub-/SHA-Vergleich bestätigt, dass nach der Windowsqualifikation keine funktionalen Änderungen vorliegen. Keine neuen Produktdaten, Nutzeraudiodateien, produktiven Credentials oder Runtime-Datenbanken im untersuchten PR-Diff. LogAccess-Token befindet sich nur im dedizierten repr-redigierten Modell; dessen expliziter `to_mapping()`-Export ist bewusst nicht log-sicher und so dokumentiert.

**Findings:** keine. Fällige Folgepflichten – erst AP-CV2-020 tatsächlicher WebSocket-Transport, dann Mirror/Audio/UI/Realtests nach Plan – sind keine AP-CV2-010-Defekte.

## Verdict und Übergabe

**ROOT_PASS auf exakt reviewed_sha `7124e5629e24817dd711b2e2b697b9c07aa11dd7` / reviewed_tree `37b61ff4cab90c18abf8e5bfae920f2e265ad3ab`.** Der später erzeugte R02-Reviewunterlagencommit ändert ausschließlich die neue Reviewakte, administrative Zustände/Spiegel, Matrix-/Requirements-Reviewverweise und den Steuerungsmeilenstein. Die neue PR-Spitze muss vor kanonischer Übernahme separat zum PASS-SHA auf rein administrative Änderungen verglichen werden. Der Commit-SHA der eigenen Reviewunterlagen wird erst nach Gitobjekterzeugung in PR-Übergabe/Chat genannt, nicht als Selbst-SHA in diesem noch zu committenden Report.

Status: `packageStatus=ROOT_PASS`, `workflowPhase=WAITING_FOR_APPROVAL`, `humanApproval=null`, `writeOwner=null`. **Nächste Aktion:** ausdrückliche menschliche Übernahmefreigabe für PR #3 unter Nennung aktueller Docs-Spitze, Parent und R02-PASS-Report. Kein automatischer Merge, Folgepaketstart, Main-/Serverpush oder Release.
