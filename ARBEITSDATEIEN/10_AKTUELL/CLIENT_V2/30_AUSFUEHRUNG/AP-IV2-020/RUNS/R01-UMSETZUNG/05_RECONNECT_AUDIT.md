# Reconnect-/Recovery-Audit – Fortsetzung R01

Status: technischer Audit abgeschlossen; AP-IV2-020 bleibt IN_PROGRESS.
Alle zehn Findings sind CLOSED_TECHNICAL am korrigierten Produkt; eigenständige
Abnahme und reale Paketpflichtfälle bleiben offen. Kein ROOT_PASS, keine Realabnahme und noch kein REVIEW_READY.

## Auftrag und Baseline

Die [Scope-Freigabe](ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md) erlaubt die
folgenden engen Clientkorrekturen im selben Paketbranch und Draft-PR #15.
Kanonischer Parent bleibt b80ed8b81ad92bd02ac32553883443d2b7673bcd;
Fortsetzung beginnt auf 1783c939f4441bd388c07b11d7cf894825b6deb9.
Server bleibt unverändert ada13b011e1d3829f78e7f389e3b927795a2b3be,
ausschließlich im isolierten lokalen Qualifikationscontainer.

Die bestehende relevante Baseline bestand vor Produktänderungen:
[vollständiger Log](EVIDENCE/recovery-audit/baseline-recovery.txt.gz),
[Runtime-/Quellidentität](EVIDENCE/recovery-audit/baseline-recovery.json).
Historische AP020-/AP010-Nachweise werden nicht als Erfolg des neuen Produkts
übertragen. Das ursprüngliche F01-Repro und der ursprüngliche Vorschlag bleiben
erhalten; der frühere Freigabevorbehalt ist durch den Zusatzauftrag aufgehoben.

## Systematische Prüfung der Kette

| Bereich | Funktionierende Schutzmechanismen | Ergebnis / weitere Prüfung |
|---|---|---|
| Settings-HTTP / Preflight | Same-origin, TLS-Prüfung, keine Redirects, Größenlimit, ein behaltener nativer Worker; Profil-/Schema-/Katalogvalidierung vor Hello | F01, F04, F08; keine HTTP-PATCH-Wiederholung eingeführt |
| WebSocket / Hello / Admission | Eigener Hello mit beiden Suppressionbits; Connect-/Admissionfristen; HTTP-Upgrades 408/429/5xx mit Backoff; 429/1013 Kapazitätsminimum; 4400/4406/4409 und inkompatibles Protokoll blockieren | Bestehende Regression grün; wiederholte echte Serverneustarts neu prüfen |
| Settings-Bootstrap | Snapshot vor und nach NA-PATCH, Revision und effektive Werte bestätigt; höchstens eine Konfliktneuberechnung; keine PCM-/Benutzerbefehlsfreigabe während CONFIGURING | F02; permanente Rejection-/Profilkontrollen erhalten |
| Command/Ack | Begrenzte Caller, domänenweise Serialisierung, maximal ein byteidentischer Retry desselben commandId; unklarer Benutzercommand recycelt Socket | F03 betrifft verspätete Fehler nach erfolgreicher Ersatzverbindung; alte Befehle nie auf neue Session übertragen |
| ActivationMirror / Resync | Session-/Generationsguards, monotone Versionen, Event-Deduplikation, begrenzter Gap-Puffer, begrenzte Snapshotversuche, danach Sessionwechsel | Bestehende Mirrorregression grün; kein nachgewiesener Reducerdefekt. Task-Cancellation-Übergänge werden in Kombination mit Reconnect geprüft |
| Audio / Media / Gerät | PCM nach READY, Queue nach Dauer/Alter/Bytes begrenzt, Callback-Epochenguard; Mute/Geräteverlust meldet false vor nativem Stop; LED unabhängig | F03, F05, F06; zusätzliche echte ReSpeaker-Aufnahme nach Neustarts, physische Trenn-/Mutehandlungen weiterhin offen |
| Logs / Ausgabe | Logzugriff generationsgebunden und ohne Domänenautorität; Ergebnisse vor Injektion reserviert; keine Übernahme alter Finals in neue Session | Bestehende Integrations-/Deduplikationstests; kein nachgewiesener zusätzlicher Fehler, echte Clipboardfälle bleiben M-11 |
| Runtime / Backoff / Shutdown | Run-Pausen separat von Bootstrapmaske; Settingswünsche bleiben Profil; Cleanup pro Komponente; Backoff begrenzt, stop unterbricht Connect/Bootstrap/Backoff | F07; Shutdown während echter HTTP-Wiederherstellung neu prüfen |

## Nachgewiesene Findings und eng begrenzte Korrekturen

Die Findings wurden erst nach der folgenden vollständigen technischen
Requalifikation als CLOSED_TECHNICAL geschlossen.
Rote Tests sind Fehlernachweise, kein Paket-PASS.

| Finding | Reproduzierte Ursache | Korrektur / dauerhafte Regression |
|---|---|---|
| IV2-020-F01 | SettingsError erbt ValueError: temporäre GET-Fehler sowie Preflightdeadline werden dauerhaft blockiert; HTML/leer bei 408/429/5xx vor Statusklassifikation als ungültiges JSON behandelt | Nur idempotente Preflight-GET-Transportfehler werden retrybar; Fehlerstatus vor Erfolgspayload; Preparedeadline durch vorhandenen Backoff. `test_temporary_metadata_failures...`, `test_prepare_deadline...`, `test_non_json_error_status...` |
| IV2-020-F02 | Bootstrapdeadline, verlorener Session-PATCH-Ack und fehlender Bestätigungssnapshot werden dauerhaft als Konfiguration geblockt | Unklare alte Session schließen, neue Session vollständig bootstrappen; fehlender Settingssnapshot als Timeout behandeln. Keine alte Mutation auf neuer Session wiederholen. `test_bootstrap_deadline...`, `test_missing_bootstrap_snapshot_or_patch_ack...` |
| IV2-020-F03 | Alte Command-/Audiosendung scheitert erst nach neuem READY; Fehlerhandler verwendet dann den aktuellen Tracker/Socket und zerstört Ersatzverbindung | Fehlerfolgen nur bei weiterhin aktuellem Binding. `test_late_old_generation_send_failure...` für Command und Audio |
| IV2-020-F04 | Abgerissener HTTP-Erfolgsbody wirft IncompleteRead außerhalb der bisherigen Transportklassifikation; Workerfehler kann ungefangen entweichen | Explizit IncompleteRead als GET-Transportverlust bzw. unklaren PATCH-Ausgang klassifizieren. `test_truncated_success_body...` |
| IV2-020-F05 | Nach Ownercancellation bleibt fehlgeschlagene native Probe als Task erhalten; jeder Folgezugriff wirft denselben Fehler, Gerät kann nie wiederkommen | Fertige alte native Operation nach Beobachtung freigeben; laufende Operation bleibt Barrier. `test_cancelled_native_probe_failure...` |
| IV2-020-F06 | Mehrere wartende native Aufrufer können nach derselben vorherigen Operation gleichzeitig starten; zwei native Gerätoperationen überlappen | Async-Lock serialisiert vollständigen Join-/Startabschnitt, Cancellation behält nativen Task. `test_bootstrap_device_and_settings_native_calls_never_overlap` |
| IV2-020-F07 | reconnect_server nach begonnenem/beendetem Shutdown startet neuen Transport trotz abgeschlossener Komponenten | Runtime-Schließbarriere vor manueller Wiederverbindung. `test_shutdown_rejects_manual_reconnect...` |
| IV2-020-F08 | Zertifikatsverifikation im WS-Pfad fällt unter OSError und würde endlos retryen; HTTP-Fehler muss bei nun retrybaren GETs explizit permanent bleiben | Expliziter sicherer TLS-Verifikationsblocker ohne Abschalten der Prüfung. `test_certificate_verification_failure...` |

| IV2-020-F09 | Gültiger `internal_error`-Ack während Settings-/Snapshot-/Audio-/Suppressionbootstrap wird wie permanente Konfiguration blockiert | Expliziter Transportverlust mit Sessionwechsel; dauerhafte Ablehnungen bleiben blockierend. `test_internal_server_error_during_bootstrap...` |
| IV2-020-F10 | Eigener Shutdown während Preflight cancelt Transport; `run()` awaitet dessen erwartete Cancellation und lässt sie aus dem Runtime-/Qt-Thread entweichen | Bei gesetztem Stop gehört die Runnerbeendigung dem Cleanup, keine weitere Propagation. `test_owned_shutdown_during_preflight...` |

[Roter F09-/F10-Nachweis](EVIDENCE/recovery-audit/red-internal-error-owned-shutdown.txt.gz).
F10 wurde zusätzlich im echten Recoverylauf nach drei erfolgreichen Neustarts
reproduziert (`real-recovery-faults-restarts-2`); dessen Trace wurde vor erneutem
Lauf als `real-recovery-trace-attempt-2.json` gesichert. Der erste reale
Hilfsmittelstart prüfte irrtümlich den Commit im Healthpayload statt im
Settingsschema; das ist ein korrigierter Harnessfehler, kein Produktbefund.

Erste rote Serie: [Log](EVIDENCE/recovery-audit/red-findings-before-fix.txt.gz)
und [Identität](EVIDENCE/recovery-audit/red-findings-before-fix.json).
Zusätzliche I/O-/Geräte-/Shutdownfehler: [Log](EVIDENCE/recovery-audit/red-additional-io-device-shutdown.txt.gz),
separater [WS-TLS-Kontrollfall](EVIDENCE/recovery-audit/red-tls-websocket-control.txt.gz).
F06: [gültiger Repro](EVIDENCE/recovery-audit/red-overlapping-native-owners-valid-repro.txt.gz)
mit maximal zwei gleichzeitigen nativen Operationen vor Lock. Dazu wurde nur der
neue Lock vorübergehend entfernt und anschließend wiederhergestellt; genaue
Vorher-/Nachherquellhashes im zugehörigen JSON.

Die ersten Hilfsmittelversuche bleiben nachvollziehbar: zu enge künstliche
Testdeadlines wurden nach Windows-Timervariabilität vergrößert, ohne
Produktfristen zu ändern. Eine fehlerhaft platzierte neue Testmethode erzeugte
zunächst SyntaxError (`red-overlapping-native-owners` und
`targeted-recovery-after-fixes`); diese Logs sind ausdrücklich **keine**
Defektnachweise. Erst der gültige F06-Repro weist den Produktfehler nach.

## Reale technische Requalifikation

`scripts/check_v2_recovery.py` nutzt das reale V2Runtime, ReSpeaker-Audio und den
realen gepinnten lokalen Server. Ein isolierter HTTP-Testproxy liefert definierte
408/429/5xx-HTMLantworten und einen Timeout; ein Socketadapter verwirft nur den
echten Ack eines tatsächlich angewandten Session-PATCHes einschließlich dessen
erlaubtem identischem Retry. Danach folgen drei kontrollierte lokale Neustarts,
überlagerte manuelle Reconnects, erneute Audio-/Settings-/Pausenbestätigung und
Shutdown während HTTP-Wiederherstellung. Keine Serverproduktcodeänderung und
keine Adminmutation. Trigger bleiben gesperrt, keine Aktivierung oder Einfügung.

Die realen Pflichtfälle M-01 bis M-12, menschliche Wahrnehmung/Kalibrierung und
30 Minuten/100 abgeschlossene Aktivierungen bleiben separat verpflichtend.
Dieser Recoverylauf ersetzt sie nicht. Neue Build-/Paar-/Vollsuitennachweise
werden nach endgültiger Produktkorrektur ergänzt.

## Konsolidiertes technisches Ergebnis (2026-10-15)

Produktcommit `41ca7612db526532509ecab65ff9d7d182da565c`, Tree
`e698089f7975ff6464300ab103e718f0992eb0d5`, Server unverändert ada13b0.
[Maschinenlesbare Qualifikation](EVIDENCE/recovery-audit/qualification-summary.json),
[Findingregister](EVIDENCE/recovery-audit/findings.json).

- Vollständige Windows-Clientsuite am endgültigen Stand: **1373 PASS, keine Skips**,
  [vollständiger Log](EVIDENCE/recovery-audit/client-full-final-environment.txt.gz).
- [Paarqualifikation](EVIDENCE/recovery-audit/pair/validation.json): 11 getrennte
  Prozessfälle, 17 ergänzende Szenariobindungen, sieben Server-Smokes PASS;
  1964 Server-Unit-Tests PASS, 14 optionale Skips einzeln im vollständigen Log und
  Qualifikationssummary ausgewiesen. Vektorbytegleichheit explizit geprüft;
  echte ausgewählte Modelle separat nachgewiesen, keine Skip-Umdeutung.
- [Echter Recoverylauf](EVIDENCE/recovery-audit/real-recovery.json): GET408/429/5xx
  mit HTML, HTTPtimeout und tatsächlich angewandter Session-PATCH mit zweimal
  verworfenem identischem Ack; neue Session statt Übertragung alter Mutation.
  Drei Neustarts samt überlagerten Reconnects: 14,703 / 15,750 / 15,859 Sekunden
  einschließlich Wiederaufnahme von PCM. Beide Run-Pausen und 4000ms Sessionwunsch
  jeweils bestätigt. Tasks an den vier Messpunkten konstant8, Pending0, Queue0,
  keine Overflows; Shutdown während Preflight0,250s. RSS etwa64,3→67,2MB,
  Private Bytes410,9→414,7MB; dieser kurze Aufbauverlauf ist kein30min-Leaknachweis.
- [Nativer Desktoprestart](EVIDENCE/recovery-audit/native/desktop-trace.jsonl)
  mit tatsächlichem ReSpeaker/Qt/Core/Logstream PASS; keine Aktivierung/Injektion.
- Reale ASR-Pipeline PASS, Final0,406s nach Referenzaudioende (ein Smoke,
  keine SLA oder deutsche Qualitätsabnahme); Golden-EN erwarteter Wortlaut exakt,
  RTF0,122. Manual/Wake/Both mit echten Modellen neu admitted.
- Native Win32hotkeys und native Settings-Qt/Vaultkontrollen erneut PASS.
- [Neue Artefakte](EVIDENCE/recovery-audit/build/artifacts.json): EXE, Wheel, sdist
  auf sauberen Produktcommit41ca761 gebunden; Paketguard und Twine PASS,
  [native Frozen-GUI am realen Server](EVIDENCE/recovery-audit/build/frozen-native-runtime.json) PASS.
- Buildorchestrierungsfehler offengelegt: gleichzeitiger `test_build_script`
  überschrieb `build/build_identity.json` mit Testidentität `a*40`. Erster Build
  deshalb verworfen; [Beleg](EVIDENCE/recovery-audit/build/contaminated-build.json).
  Neuer Build nach Clientsuite seriell erfolgreich, keine Produktkorrektur daran.
  Fehlende reine Buildabhängigkeit wheel0.45.1 ausschließlich in Projektvenv ergänzt;
  anschließend abschließende vollständige Windowsregression erneut grün.

Der echte Vorcommit-Recoverylauf ist über alle protokollierten Quellhashes an den
Produktcommit gebunden (nur Git-EOL-Normalisierung), nicht anhand einer
vermuteten Gleichheit. Nachfolgende Akten-/Belegnachträge verändern das Produkt
nicht. V1, VPS und produktive Serverzustände blieben unangetastet.

Nächste Aktion ist die bereits vorbereitete gemeinsame Testphase. Alle vollständigen
M-Fälle, echte Wakepositive/Nutzsprachgrenze, Wahrnehmung/Kalibrierung und finaler
30min-/100Activations-Lauf bleiben NOT_RUN/NOT_PROVEN. Kein REVIEW_READY.
