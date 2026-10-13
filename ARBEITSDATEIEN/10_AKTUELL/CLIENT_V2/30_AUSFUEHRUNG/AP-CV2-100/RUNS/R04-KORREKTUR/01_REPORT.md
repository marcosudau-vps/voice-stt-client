# AP-CV2-100 / R04-KORREKTUR – CV2-100-R03-F01

**Status:** REVIEW_READY. Vollständige Selbstchecks; keine unabhängige Eigenabnahme.
Tatsächliche Reviewübergabe erst nach grüner finaler PR-CI.

## Auftrag und Identität

[Originalauftrag](00_PROMPT_ORIGINAL.md), [R03-CHANGES_REQUIRED](../R03-ABNAHME/01_REPORT.md).
Branch `work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)
gegen `feat/client-v2`; Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`, Server
`ada13b011e1d3829f78e7f389e3b927795a2b3be`. Starthead nach Fetch/Fast-forward
`c5a510f193908d7493f979365e45be6317cd9dab`, sämtliche R03-Unterlagen enthalten;
R03-Nachtrag gegenüber reviewed4a35a2d rein administrativ, Produkt-/Testdiff leer.
[Start-/Git-/PR-Provenienz](EVIDENCE/start-provenance.json); Parent unverändert,
kein fremder aktiver Schreibowner. Fortgeltende Paket-Gitfreigabe und menschlicher
Korrekturprompt gesichert; keine kanonische Übernahmefreigabe.

## F01: Repro, minimale Korrektur und neue Nachweise

Vorherige relevante Suite: 56 Tests PASS. Neue Prüfungen im tatsächlichen
V2DesktopApplication + V2CoreBridge + V2Runtime mit realem aufzeichnendem
ObservabilityIngress: Overlay/Audio/Logging anwenden und AppConfig.save_user gezielt
scheitern lassen. Vor Fix fehlen alle drei Auditereignisse; zwei Reprofälle FAIL.
Vollständige [Baseline](EVIDENCE/baseline-targeted.txt) und
[Vorher-Repro](EVIDENCE/f01-before-fix.txt); Befehle im Evidenzindex.

Produktfix ausschließlich ui/v2_application.py und core/v2_runtime.py:

- Qt erzeugt `settings:<uuid-prefix>` und `client.settings.apply_started` samt
  Policies erst nach Busyprüfung. Bestehender V2CoreBridge-Korrelationsport reicht
  dieselbe ID über CoreBridge an V2Runtime weiter; keine zweite Applyausführung.
- Core emittiert nach der angenommenen lokalen Transaktion genau ein
  `client.settings.runtime_apply`, im finally nach normalem Abschluss oder Rollback.
  Details: `session_changed=false`, tatsächlicher `audio_changed`-Vergleich,
  `mode_changed=false`, `success`, `status`; Session/Generation am Emissionspunkt.
  Flags folgen dem lokalen Port: Server-/Triggerprofilwechsel sind weiterhin
  abgewiesen und gehören SettingsUISession. Reine Overlay-/Loggingänderung hat
  drei false Flags und keinen Reconnect/Audiorestart.
- Qt verwendet den geerbten idempotenten `_complete_settings_observation` für
  `client.settings.apply_completed` mit derselben ID und Resultstatus. IDverbrauch
  verhindert doppelte Abschlüsse; Core-Abweisung und Shutdown schließen offene
  Versuche ebenfalls ab. Busy überschreibt keine laufende ID.
- Vorhandener ClientEventEmitter schirmt Ingressfehler ab. Nur Policies/Flags und
  Status werden publiziert, keine Konfigwerte/Credentials. Korrelations-ID hat
  keine steuernde Wirkung. Kein Server-/Wire-/Schema-/Technologiewechsel.

Sieben neue Methoden in tests.test_v2_runtime_integration.QtRuntime:
- `test_local_settings_audit_correlates_overlay_audio_and_logging_success`
- `test_local_settings_audit_reports_persist_failure_and_restores_audio`
- `test_local_settings_audit_reports_post_save_rollback`
- `test_local_settings_busy_attempt_preserves_pending_audit_correlation`
- `test_local_settings_unavailable_core_finishes_audit_once`
- `test_local_settings_apply_survives_audit_ingress_failure`
- `test_local_settings_shutdown_completes_pending_audit_once`

Sie prüfen drei Events in Reihenfolge, Auditkanal, identische eindeutige ID, drei
Flags, Erfolgs-/Fehlerstatus, Session/Generation und genau einen UI-Abschluss;
Audio/Persistenzfehler sowie Fehler nach bereits erfolgreichem Speichern sichern
tatsächlichen Memory-/Diskrollback. Zusätzliche Core-Abweisung bewahrt zwei
Started/Completed-Events ohne erfundene Runtimeausführung. Shutdown prüft fertigen
Persistenzschritt, beendeten Core und abgemeldete Keys; Completion darf bereits
`applied` oder wegen UI-Teardown `shutdown` sein, bleibt genau einmal korreliert.

Erster Nachfixlauf: vier Tests FAIL ausschließlich wegen erwarteter Listendarstellung
der Policies; der echte CanonicalLogRecord friert Listen als Tuple ein. Assertion
auf tatsächliches Immutable-Tuple korrigiert, funktionaler Auditvertrag unverändert.
Danach 62 Tests PASS, zusätzlicher Shutdownfall PASS, abschließend alle sieben Fälle
erneut in gezielter Suite und Vollsuite. Sämtliche Iterationslogs erhalten.

## Vollqualifikation und Kandidatenbindung

Windows11/Python3.12.10, Dependencies, vollständige Befehle/Exits/Zahlen/Zeitpunkte,
Loghashes, 213 qualifizierte Gitblobs und lokale Sourcehashes im
[Windowsmanifest](EVIDENCE/windows-validation.json). Basis c5a510f plus
[exakte staged Produkt-/Testdiff](EVIDENCE/tested-product.patch.base64), base64/SHA256.
Finalen Head/Tree nach Unterlagen aus Git in PR/Übergabe ermitteln; administrative
Nachträge verändern keinen qualifizierten Produkt-/Test-/Konfigblob.

- 1581 vollständige Windows-Clienttests PASS, keine Skips.
- 210 gezielte Tests mit -W error PASS (28 Runtime/Qt/Migrationsfälle plus Bestand).
- 17 tatsächliche komponierte Desktop/Core/Qt-/HTTP-/Domain-/Logchecks gegen
  45 bytegeprüfte Serverquellen am gepinnten ada13b0 PASS.
- compileall, staged/unstaged Diffcheck und [Akten-/Blob-/Logprüfung](EVIDENCE/submission-verification.json) PASS.

Vollständige [Belege/Befehle](EVIDENCE/INDEX.md). Nach Push muss finale headgebundene
Windows-CI einschließlich EXE-/sdist-/Wheel-Smokes bestanden sein; tatsächliches
Ergebnis/SHA/Run wird im PR verlinkt, keine vorausgenommene CI-Erfolgsbehauptung.

## Traceability, Dokumentation und Übergabe

FINAL-01/02 und RUNTIME-01 bis RUNTIME-04 bleiben CLIENT OPEN. Die individuellen
[R01-Paketmethoden](../R01-UMSETZUNG/01_REPORT.md) wurden im R04-Kandidaten erneut
bestanden; RUNTIME-02 erhält die sieben tatsächlichen Audit-/Fehlerfälle zusätzlich.
Requirements/Matrix führen R04-Belege, bisherige R01/R02-Belege bleiben in der
Historie. R03-Reviewurteil und komplette Reviewakte unverändert erhalten.
WORKFLOW_STATUS, Manifest, Paket-/Planindex, Steuerung, task.md, ÜBERGABE.md,
Projektübersicht sowie Runtimeinterfaces/OBS-Katalog aktuell; genau ein
R04-Selbstcheckmeilenstein in Block-/Steuerungslog.

Neue öffentliche Signatur entsteht nicht: correlation_id und der Bridgeport
existierten bereits; Runtime nutzt ihn nun tatsächlich. Thread-/Generationguards,
vorhandene Serverautorität, Persistenz-/Rollbackablauf und sonstige Produktports
aus R01 unverändert. Frische unabhängige Abnahme des gesamten kumulativen AP100
mit Fokus F01 erforderlich, Umsetzung nach Übergabe pausiert. F01 im Selbstcheck
behoben, kein eigenes ROOT_PASS. Kein Merge/AP110 ohne unabhängigen PASS und
menschlichen Prompt. Reale Hardware-/ASR-/Crossrepo-/finale V2-Buildgates bleiben
den späteren Paketen zugeordnet; CI-Smokes ersetzen diese nicht.
