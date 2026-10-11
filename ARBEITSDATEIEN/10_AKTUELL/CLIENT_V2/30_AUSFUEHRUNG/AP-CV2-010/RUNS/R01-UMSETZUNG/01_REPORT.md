# AP-CV2-010 / R01 – Umsetzung

Status **REVIEW_READY**, Datum 2026-10-11, Europe/Berlin. [Originalauftrag](00_PROMPT_ORIGINAL.md), [PR #3](https://github.com/marcosudau-vps/voice-stt-client/pull/3), [Evidenzindex](EVIDENCE/INDEX.md).

Parent `1cf076bd2ed56929b1a3780bc140da51348a8295`, Branch `work/client-v2/ap-cv2-010`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Vollständig getesteter Kandidat `9838558173b6bd88d4620b20d4e2e9d832e814c7`, Tree `c3a0b826e5d9614ad6dfb80b51815af77f8090bf`, sauberer Workingtree vor den Prüfungen. Nachfolgende Änderungen betreffen nur Akten, Status, Traceability und Testnachweise; vor Abgabe Diff gegen diesen Commit nachweisen. Exakte eingereichte SHA/Tree nach allen Unterlagen in Git-/PR-Übergabe nennen; keine Selbst-SHA in einem noch zu erzeugenden Commit.

## Start und Umsetzung

Vorgänger-PASS R04/R05, tatsächliche menschliche Freigabe, gemergter PR #2 und kanonischer Single-Parent-Commit wurden vor Paketstart geprüft. Lokale und entfernte feat/client-v2-Spitzen waren identisch, keine offenen Paketlinien oder fremden Workingtreeänderungen. [Nachmergebeleg](EVIDENCE/predecessor-canonicalization.json). Der tatsächliche Auftrag und die gültige workflowweite Kandidaten-Gitfreigabe sind im Originalprompt verlinkt. Kein Gittransport auf Main oder Server, keine Paketpromotion.

Die Vorher-Baseline lief vor der ersten Produktänderung: vollständige Windows-Clientsuite1233 Tests, 95.998s, unittest OK. Der vollständige ursprüngliche Log bleibt erhalten; dessen Shell-Exitcode wurde damals nicht separat gespeichert. Die verpflichtende Kandidatenqualifikation unten erfasst alle Exitcodes ausdrücklich.

Umsetzungsskizze vor Änderung: immutable Wiremodelle mit exakten Feldnamen; strikte Pflichtfeldvalidierung, additive Extras erhalten; getrennte Settingsoberflächen; disjunkte Commandbuilder; begrenzter PCM-Encoder im bestehenden Byteformat. Originalvektoren bytegleich und ergänzende vollständige Fixtures getrennt. Keine bestehende Core-Komponente umgebaut.

Neu implementiert in `voice_stt_client/core/protocol_v2.py`: fünf Commands, vier Activationaktionen,15 Ackresultcodes, fünf Inputphasen und18 Events; Hello/HelloAccepted/Reject, UUIDprüfung/-erzeugung, bekannte Eventpayloads und sequenzierbare UnknownEvents, vollständige standalone/embedded Snapshots und16 Sessionkeys. Settingsschema, Serverread und Patchantwort bleiben unterschiedliche Formen mit ausdrücklichem Revisionsscope. LogAccess hält Token im dedizierten, repr-redigierten Speicher und prüft Session-/Originbindung. Audio verwendet exakt den bestehenden uint32LE/JSON/PCM16LE-Encoder; Sampling-/Kanal-/Metadaten-/PCM-/Framesgrenzen werden geprüft.

[Öffentliche Funktionen und Datentypen, Decodervertrag und Folgepaketübergabe](../../../../../../../docs/protocol-v2-codec.md). Parser/Builder erzeugen detached immutable Modelle; `to_mapping()` ist ein expliziter frischer Wireexport und darf Token enthalten, daher nicht loggen. Enumwerte und Feldnamen bleiben Wirestrings. Unknown extras werden erhalten. Schemaconstraints/Crossfields/Applypolicy bleiben Serverautorität.

Keine Callbacks, Threads, Domainzustandsänderungen, Netzverbindung, Audioaufnahme, Profil-/SQLite-/Credentialmigration oder UIänderung. Empfangsreihenfolge, Generation-/Sessionguards und Commandkorrelation werden im späteren Transport umgesetzt; UnknownEvent trägt dort nur Sequenzfortschritt. Ack kann älter als ein bereits empfangenes Event sein. Bestehende Laufzeitanwendung bleibt auf ihrem bisherigen Pfad. Kein V1-Test entfernt oder geschwächt; die30 Codec-Methoden ergänzen die1233 vorhandenen Tests.

## Quellenentscheidungen und iteratives Debugging

Originalvektoren aus serverada13b0 bleiben bytegleich (SHA256694971cea437ca57c207620fac7f169d0397987d7fe1ee02fd276eb8b941de34). Ein Windows-Export hatte zunächst CRLF; tatsächliche Gitblobbytes wurden exportiert und per Hash/bytegleich geprüft. Die originale idle_snapshot-Skizze ist unvollständig, wird nachvollziehbar abgewiesen und durch separate vollständige Fixtures sowie echte Serverprojektion ergänzt. command_id_conflict ist syntaktisch gültig, aber am echten Replaycache konfliktbehaftet; keine pauschale Client-Syntaxablehnung aller invalidMessages.

K-01 präzisiert vorhandene frames als positiv statt nichtnegativ: der gepinnte Server prüft require_positive_int. Leeres PCM ohne frames bleibt zulässig. Dies ist Quellenklärung derselben Serverbaseline. Grenztest für Metadaten65536 wurde wegen einer um zwei Bytes falschen Testrechnung korrigiert. Im ersten Harnesslauf tatsächliches ReplayLookup.state statt vermutetem status verwendet; unabhängige Eventprojektionen erhalten je eigenen frischen Wirezustand statt künstlich widersprüchlicher Terminalmemos. Snapshot-Registrytuples werden wie auf echtem Wire über JSON serialisiert. Alle Korrekturen liegen vor dem vollständig qualifizierten Commit.

## Tatsächliche Qualifikation

Windows11 Build26300, Python3.12.10/AMD64 aus Projektvenv, `QT_QPA_PLATFORM=offscreen`, UTF8. Vollständige Befehle, Runtime, Beginn/Ende, Exitcodes und SHA256 der kompletten Logs: [windows-validation.json](EVIDENCE/windows-validation.json).

| Prüfung | Ergebnis | Beleg |
| --- | --- | --- |
| Vorher: gesamte unittest-Suite |1233 Tests OK,95.998s | [Baseline](EVIDENCE/baseline-full-unittest.txt) |
| Codec: `-m unittest tests.test_v2_protocol -v` |30 Tests PASS, Exit0 | [Vollständiger Log](EVIDENCE/targeted-protocol-unittest.txt) |
| Tatsächlicher Clientcodec gegen serverada13b0 |188 Checks PASS, Exit0;17 Serverquellen byteverifiziert | [Checkpoint](EVIDENCE/server-contract-checkpoint.json) |
| `-m compileall -q voice_stt_client scripts tests` |PASS, Exit0; erwartungsgemäß leere stdout/stderr | [Log](EVIDENCE/compileall.txt), [Exitbeleg](EVIDENCE/windows-validation.json) |
| Nachher: `-m unittest discover -s tests -p 'test_*.py'` |1263 Tests PASS,93.640s, Exit0 | [Vollständiger Log](EVIDENCE/windows-full-unittest.txt) |
| `git diff --check` und gemeinsamer Aktenprüfer einschließlich weiterer Markdownlinks/aktueller PRbody |PASS vor endgültiger Abgabe | [Abgabeprüfungen](EVIDENCE/administrative-validation.json) |

Keine Pflichtskips oder unerklärten Testfehler. Erwartete Exception-/Warnlogs vorhandener Negativtests werden im vollständigen Suitebeleg erhalten, nicht als zusätzliche Fehler umgedeutet. GitHub-CI des getesteten Erstkandidaten38174130404 einschließlich Windows-Build PASS; finalen administrativen Headcheck zusätzlich vor Übergabe aus PR prüfen. Kein neuer produktrelevanter Unterschied nach Windowsqualifikation.

Der checkpoint `scripts/check_v2_server_contract.py` benutzt echte Commands/Handshake, Registry, Replaycache, Controller/Ledger und Snapshot-/Event-/Ackprojektionen der17 byteverifizierten Originalquellen. Zwei unveränderte Audioproduktionsfunktionen werden aus dem originalen AST kompiliert, damit kein ASR-Appimport nötig ist. Kontrollierter Adapter nur für Wakekatalog/Capabilities; NumPy und tatsächliche Resamplingpfade. Alle fünf Commands,15 Ackresultcodes × fünf Phasen,18 Events,16/48kHz ×1/2/8 Kanäle, Patch-Revisions-/Crossfieldfälle und negative Envelopefälle werden durch den echten Clientcodec geschickt. Sourcehashes und188 Fallresultate sind einzeln im Checkpoint enthalten.

Beweisgrenzen: kein WebSocket-/Mikrofon-/ASR-/Hardware-/vollständiger Bootstrapnachweis. Diese Fälle sind für das reine Codecpaket kein vorgeschriebenes Plattformgate und bleiben den geplanten Folgepaketen zugeordnet. Kein Serverprodukt verändert, Server-Distributed bleibt offen. Späterer Transport muss sämtliche Guards und Audio-/Commandfreigabe implementieren; diese Paketabgabe behauptet keinen lauffähigen V2-Gesamtclient.

## Individuelle Requirementbelege

Alle IDs weiter CLIENT OPEN bis unabhängiger Abnahme. Die folgenden tatsächlich ausgeführten Methoden und die188 benannten Checkpointfälle sind an getesteten SHA/Tree gebunden; [Requirements-JSON](../../../../PLANUNG/REFERENZ/TRACEABILITY/requirements.json) und [Matrix](../../../../PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) enthalten gleiche Zuordnung.

| ID | Tatsächliche Methode / Fall | Selbstcheck |
| --- | --- | --- |
| WIRE-01 | `tests.test_v2_protocol.VocabularyAndVectors.test_vocabulary_and_endpoint_match_pinned_manifest` | PASS |
| WIRE-02 | `tests.test_v2_protocol.ClientMessages.test_hello_builder_and_uuid_generation`; `tests.test_v2_protocol.ClientMessages.test_hello_missing_required_fields_and_bool_integer` | PASS |
| WIRE-03 | `tests.test_v2_protocol.ClientMessages.test_hello_trigger_selection_and_suppression_matrix` | PASS |
| WIRE-04 | `tests.test_v2_protocol.ClientMessages.test_hello_trigger_selection_and_suppression_matrix` | PASS |
| WIRE-05 | `tests.test_v2_protocol.ClientMessages.test_uuid_canonical_not_version_restricted`; `tests.test_v2_protocol.ClientMessages.test_hello_builder_and_uuid_generation` | PASS |
| WIRE-06 | `tests.test_v2_protocol.ClientMessages.test_all_commands_and_controls_encode_without_rewriting`; `tests.test_v2_protocol.ClientMessages.test_command_envelope_and_payload_negatives` | PASS |
| WIRE-07 | `tests.test_v2_protocol.ClientMessages.test_forbidden_activation_field_combinations` | PASS |
| WIRE-08 | `tests.test_v2_protocol.ClientMessages.test_forbidden_activation_field_combinations`; `tests.test_v2_protocol.ClientMessages.test_all_commands_and_controls_encode_without_rewriting` | PASS |
| WIRE-09 | `tests.test_v2_protocol.ClientMessages.test_command_envelope_and_payload_negatives`; `tests.test_v2_protocol.ServerMessages.test_all_ack_results_and_phases`; `server checkpoint: envelope_rejection/*` | PASS |
| WIRE-10 | `tests.test_v2_protocol.VocabularyAndVectors.test_vocabulary_and_endpoint_match_pinned_manifest`; `tests.test_v2_protocol.ClientMessages.test_uuid_canonical_not_version_restricted`; `server checkpoint: ignored/* and envelope_ack_identity/*` | PASS |
| WIRE-11 | `tests.test_v2_protocol.ServerMessages.test_all_18_events_and_required_field_omissions`; `tests.test_v2_protocol.ServerMessages.test_minimal_and_rich_interim_defensive_optional_fields`; `tests.test_v2_protocol.ServerMessages.test_unknown_valid_event_preserves_sequence_without_domain_effect` | PASS |
| WIRE-12 | `tests.test_v2_protocol.ServerMessages.test_event_bool_int_uuid_null_negatives`; `tests.test_v2_protocol.SnapshotsAndSettings.test_snapshot_revisions_bool_and_input_null_omission`; `tests.test_v2_protocol.ClientMessages.test_command_envelope_and_payload_negatives` | PASS |
| WIRE-13 | `tests.test_v2_protocol.VocabularyAndVectors.test_every_original_vector_is_directionally_classified`; `tests.test_v2_protocol.VocabularyAndVectors.test_vendored_vectors_are_byte_identical_and_hashed`; `tests.test_v2_protocol.VocabularyAndVectors.test_vocabulary_and_endpoint_match_pinned_manifest` | PASS |
| WIRE-14 | `tests.test_v2_protocol.AudioCodec.test_audio_exact_existing_bytes_16_48khz_mono_stereo_eight_channels`; `tests.test_v2_protocol.AudioCodec.test_audio_optional_metadata_defaults_and_byte_example` | PASS |
| WIRE-15 | `tests.test_v2_protocol.AudioCodec.test_audio_sample_channel_frames_limits_and_bool_rejected`; `tests.test_v2_protocol.AudioCodec.test_audio_exact_existing_bytes_16_48khz_mono_stereo_eight_channels` | PASS |
| WIRE-16 | `tests.test_v2_protocol.AudioCodec.test_audio_metadata_boundary_and_invalid_binary_frames`; `tests.test_v2_protocol.AudioCodec.test_audio_sample_channel_frames_limits_and_bool_rejected` | PASS |
| WIRE-17 | `tests.test_v2_protocol.SnapshotsAndSettings.test_schema_read_patch_have_distinct_forms_and_revision_scopes`; `tests.test_v2_protocol.SnapshotsAndSettings.test_snapshot_has_full_separate_maps_and_embedded_shape`; `tests.test_v2_protocol.SnapshotsAndSettings.test_settings_numbers_and_maps_not_coerced`; `tests.test_v2_protocol.SnapshotsAndSettings.test_hello_accepted_log_token_repr_and_unavailable`; `tests.test_v2_protocol.SnapshotsAndSettings.test_log_access_shape_paths_identity_expiry_and_no_secret_errors` | PASS |

## Dokumentation und Übergabe

Produkt-APIvertrag, Paketvertrag/Checkboxen, Manifest, Requirements/Matrix, aktive Steuerung, task.md, ÜBERGABE.md und Übersicht aktualisiert. AP000-Nachmergeprovenienz auf diesem Paketbranch nachgeführt, historische Reports unverändert. Originalauftrag, Startvertragshashes und vollständige reproduzierbare Qualifikationsbelege enthalten. Administrative Änderungen nach getestetem Commit werden separat im Abgabebeleg aufgelistet.

Nächste Aktion: frische unabhängige Session prüft gesamten PR #3 vom Parent bis eingereichtem Head einschließlich Code, Kontrakten und gültigen Windows-/Servernachweisen. Offene Selbstfindings: keine. Unabhängiges Urteil und menschliche spätere Übernahmefreigabe noch offen. Status REVIEW_READY; `writeOwner=null` nach Abgabe, Paketbranch bis Review pausiert. Kein eigener ROOT_PASS, Merge, Cleanup oder Folgepaketstart.
