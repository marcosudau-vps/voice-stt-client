# AP-IV2-020 – R02-ABNAHME / CHANGES_REQUIRED

Datum: 22.10.2026. Frische unabhängige ChatGPT-Prüfung über commitgebundene GitHub-Dateien.

## Geprüfte Identität

- Repository: marcosudau-vps/voice-stt-client; PR: https://github.com/marcosudau-vps/voice-stt-client/pull/15
- Base feat/client-v2; canonical_parent: b80ed8b81ad92bd02ac32553883443d2b7673bcd (unverändert).
- reviewed_sha: 29fb0e159c69051bedba6d097f69a5974fc09528
- reviewed_tree: 2b0ffe601582560770af47d727617ff726d8bf90
- Fachlicher Produktcommit: 0f6c85e0ecf971e596aae1b7d265dad7132754e2.
- Qualifizierte EXE SHA256: e20059f6dff1279cb23fb01576d447fb285aa94cb270d71968b8430a063a15fc.
- Ausgewählter Server-SHA: 67f3ce45f6ea1ff659382e40c194c70bd33d58ff, Tree 74f37cad84c5be9e74d880a4b10c3d9623de7da3, Pro 2.0.0. Historischer Kontraktpin ada13b0.
- Reviewgrundlagen: verbindlicher nächster-Schritt- und Abnahme-Skill, ABNAHMECHECKLISTE, AP-IV2-020, TEST_UND_ABNAHMEPLAN, WINDOWS_UND_HARDWARENACHWEISE, PR-/Reviewübergabe und AGENTS.md.

## Positiv unabhängig geprüfte Umsetzung und Fremdbelege

- GitHub-CI #39712620060 SUCCESS auf exakt reviewed_sha.
- Windowsfremdbeleg: 1400/1400 entdeckte Test-IDs, 79 isoliert ausgeführte Module, 0 Skips, Modulprotokolle in review-ready-20261022/windows und Hashangaben im Assessment; 83 Helfertests ohne Skips und compileall PASS. Die native Qt-Monolithproblematik/Fehlversuche sind dokumentiert, nicht verschwiegen. Keine eigene Windows-Wiederholung durch den Reviewer.
- Neun geänderte Produktmodule mit den Kernpatches für Settings-GET/Bootstrap/Transport, nativen Audio-Stillstand, Textinjektion/Modifier und Close-Feedback auf Scope und Fehlerbehandlung geprüft. Entsprechende Regressionen und Realgrenzen eingesehen; keine eigenmächtige Server- oder Protokollcodeänderung im Client-PR festgestellt.
- Echte Windows-, ReSpeaker-USB-/Mute-, ASR-/Wake-, Admin-/Vault-, UAC-, LED-/Feedback-, Stereomix-Frozen- und ausstehende-Final-Nachweise vorhanden. Separate Nachweisgrenzen (Replay statt akustisches Mikrofon, kontrolliertes Clipboard, API-Annahme statt sichtbares Elevated-Paste) wurden transparent protokolliert.
- Das kombinierte 30-Minuten-/100-Activation-Ergebnis ist für seine tatsächliche Testgrenze gültig: 1800,015 s, 100 Finals/Historyeinträge, drei Session-/Netz-Recoveryaktionen; die automatische Auswertung behauptet ausdrücklich keine vollständige physische M-12-Erfüllung.

## Pflichtfindings

### IV2-020-R02-F01 – M-12 / REAL-03 und REAL-05: kombinierter Dauer-/Geräte-Recoverynachweis fehlt (BLOCKING)

**Vorgabe:** TEST_UND_ABNAHMEPLAN §5 M-12 und AP-IV2-020 Arbeitsschritt 6 verlangen 30 Minuten und mindestens 100 abgeschlossene Activations mit wiederholten Netzwerk-/USBwechseln sowie Ressourcen-/Recoverykontrolle. Die Hardware-Nachweisregel erlaubt gesonderte komplementäre Checks, aber keinen unbewiesenen Abschluss einer ausdrücklich geforderten Kombination.
**Ist:** Der 1800,015-s-Dauerlauf nutzt einen ReplayStream an der PortAudio-Grenze, kontrollierte Clipboardausgabe und nach 25/50/75 gezielte Session-/TCP-Recovery. Sein Helper selbst schreibt hardwareUsbRecovery=NOT_RUN, frozenNativeUiClipboard=NOT_RUN und fullM12=NOT_PROVEN; confirmed-assessment.json nennt fullPhysicalM12=NOT_PROVEN. Physischer USBverlust/Neuöffnen wurde separat, aber nicht innerhalb dieses Dauerlaufs belegt. Die spätere qualification-matrix.json hebt M-12 ohne einen solchen neuen kombinierten Lauf zu PASS_SCOPED_COMPOSITE an.
**Wirkung:** Aussage über langlaufendes Wiederanlaufen nach tatsächlichem Hardwareverlust unter Last bleibt unbelegt; deshalb kein vollständiger Real-PASS.
**Geforderte Korrektur (Umsetzer):** Einen eindeutig kandidaten- und servergebundenen mindestens 30-min-/100-Activation-Realmodelllauf mit kontrolliert ausgeführten und protokollierten mehrfachen Geräte-/USB- und Netzunterbrechungen bzw. gleichwertige innerhalb desselben Laufes tatsächlich validierte native Geräteaktionen erbringen. Nicht 100 neue menschliche Sprechhandlungen verlangen: begründete Audiofixtures dürfen eingesetzt werden; echte physische Hardwarehandlungen dürfen nicht durch reine Softwarekennzeichen ersetzt werden. Während/ nach Ausfall Audio-ACK, alte Finals, neue Session oder unveränderte Session nach Gerätverlust, Recovery, Aufgaben/Queues/Memory und Endzustand prüfen. Bestehende reale Teilbelege erhalten. Erst dann M12/REAL05 und REAL06 fachlich schließen.

### IV2-020-R02-F02 – REAL-05 / REAL-06: unbegrenztes aktives Sessionledger und unzureichender Ressourcenbeleg (BLOCKING)

**Vorgabe:** TEST_UND_ABNAHMEPLAN §6 verlangt keine stetig wachsenden abgeschlossenen Tombstones/Runtimeledger ohne begründetes Retentionkonzept; REAL-05 fordert Queue-/Task-/Memorykontrolle.
**Ist/Quellnachweis:** voice_stt_client/core/activation_mirror.py – _reset erzeugt unbeschränkte dicts activations, segments, _seen, _sequences; normale Eventreduktion ergänzt Einträge bis Sessionende. Nur der Gap-Puffer hat max_events/max_bytes. Mirror.view kopiert die vollständigen Maps pro Projektion. voice_stt_client/core/final_results.py – V2ResultService._terminals erweitert sich für jedes finale Segment und wird erst bei Generationswechsel/Close geleert. Die 100er Messung forcierte drei Reconnects, so dass maximal 25 Aktivierungen derselben Session gehalten wurden. Das beweist keine Begrenzung bei einer dauerhaft verbundenen Sitzung.
**Wirkung:** Über Stunden/Tage verbundene Sessions können Linearwachstum an Identitäten/Tombstones und zunehmend teure View-Projektionen erzeugen; für den langfristigen Hintergrundbetrieb fehlt die geforderte Begrenzung.
**Geforderte Korrektur (Umsetzer):** Sichere Retention-/Pruningstrategie mit klaren Lifecycle-, Replay-/Gap-, Exactly-once-/Unknown-outcome- und Snapshot-Guards sowie angemessener Grenze für alle betroffenen sessiongebundenen Register. Keine einfache Löschung, die alte Finals nochmals ausgibt. Zusätzlich deterministischer und/oder realer Mehrhundert-Activation-Dauertest ohne erzwungenen Reconnect über eine Session: Registergrößen, Task-/Queue-Stabilität, Memorytrend und Deduplizierung vor/nach Pruning belegen. Produktcodeänderungen benötigen die eng gebundene Scope-/Freigabeentscheidung nach gültigen Regeln, sofern außerhalb bereits autorisierter Recoveryhärtung.

## Zusätzliche Aktenkonsistenz (administrativer Korrekturhinweis)

WORKFLOW_STATUS.json enthält historische observations mit OPEN_INVESTIGATION/PARTIALLY_PROVEN bzw. VISUAL_CONFIRMATION_PENDING (O01, O02, T03), während aktuelle Abschlussmatrix sämtlichen M-Fällen remaining=null zuweist. Diese Einträge müssen als historische Beobachtungen oder tatsächliche aktuelle offene Risiken eindeutig unterschieden und mit dem Reviewstand synchronisiert werden. Historische Fehlläufe, W02-Dispositionsentscheidung und ungelöster ursprünglicher ReSpeaker-Autopasteversuch dürfen nicht stillschweigend umgedeutet werden.

## Verdict, Grenzen und nächste Aktion

**CHANGES_REQUIRED: Kein ROOT_PASS, kein Merge, keine Release-/Serverpromotion.** Zwei Pflichtfindings verhindern die vollständige technische Paketabnahme. REAL-01/02/04 und weitere Teile besitzen teils belastbare komplementäre Evidenz, aber ein Gesamturteil über REAL-03/05/06 kann vor Schließung der Befunde nicht PASS sein.
Reviewverfahren: unabhängige statische Prüfung der commitgebundenen Produktionspatches, ausgewählter Test-/Hilfsquellen, Paket-/Requirement-/Evidenzakten und der eingereichten Windows-/Realreports sowie GitHub-CI; keine eigene Hardwaredurchführung und keine erneute Windowsvollsuite. Externe Windows-/Hardwareergebnisse als Fremdbelege geprüft, nicht als selbst ausgeführt ausgegeben.
Umsetzer: im selben Paketbranch nach Übernahme dieser R02-Akte die beiden Findings reproduzierbar schließen, erforderlichenfalls gesonderte Produktfreigabe innerhalb des gültigen Scopes abgrenzen, endgültigen Produkt-/Teststand neu qualifizieren und kumulativen PR15 wieder als REVIEW_READY übergeben. Danach unabhängige Gesamt-Nachabnahme. Menschliche kanonische Übernahme erst nach unabhängigem ROOT_PASS und separater Freigabe.

Siehe EVIDENCE/INDEX.md für genaue Prüflinks und Beleggrenzen.
