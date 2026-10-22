# AP-IV2-020 – R02-ABNAHME / CHANGES_REQUIRED (berichtigt am 22.10.2026)

Datum: 22.10.2026. Frische unabhängige ChatGPT-Prüfung über commitgebundene GitHub-Dateien.

**Berichtigung nach Rücksprache mit dem Auftraggeber am 22.10.2026:** Die überstrenge Kombinationsanforderung aus R02-F01 wurde durch den Reviewer zurückgenommen. **Einziges noch blockierendes R02-Finding ist R02-F02.** Die später bekannt gewordene CI-Flakiness wird separat in [Issue #16](https://github.com/marcosudau-vps/voice-stt-client/issues/16) dokumentiert, ohne nachträglich ein neues fachliches Reviewfinding zu erzeugen. Der ursprüngliche fachlich geprüfte SHA bleibt derselbe; Dokumentationscommits sind keine neue Produktqualifikation.

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
- Der 30-Minuten-/100-Activation-Test belegt 1800,015 s, 100 Finals/Historyeinträge und drei Session-/Netz-Recoveries in seinem Replay-Testscope. Getrennte reale USB-/ReSpeaker-/Windows-Recoverybelege werden als **komplementärer Gesamtnachweis** anerkannt. Die lokalen NOT_RUN/NOT_PROVEN-Marker des Replay-Helfers gelten weiterhin nur für dessen eigene physische Testgrenze.

## Pflichtfindings

### IV2-020-R02-F01 – M-12 / REAL-03 und REAL-05: früherer Kombinationsvorbehalt (**WITHDRAWN_BY_REVIEWER – NICHT BLOCKIEREND**)

**Historischer Erstbefund:** Der 1800,015-s-/100-Activation-Dauerlauf verwendet ReplayStream statt physischem USB-Audio und dokumentiert lokal `hardwareUsbRecovery=NOT_RUN`, `fullM12=NOT_PROVEN`; separate reale USB-/ReSpeaker-/Windows-Recoveryfälle existieren. R02 hatte daraus zwingend einen neuen **einzigen** Dauerlauf mit physischen USB-Wechseln gefordert.

**Korrigierte Bewertung:** Dies war zu streng: Der Testplan verlangt den Nachweis von Langzeitbetrieb, Activations und Geräte-/Netz-Recovery, legt aber nicht eindeutig fest, dass alle Einzelnachweise im **selben Lauf** erbracht werden müssen. Die vorhandene methodisch getrennte Langzeit-/Netz-/Modellqualifikation und die realen physischen USB-/Capture-/Altfinal-/Windows-Recoveryprüfungen dürfen zusammen als komplementärer Gesamtnachweis gelten. Lokale NOT_PROVEN-Felder im Langzeit-Testhelper bedeuten **nicht**, dass diese anderen physischen Belege ungültig sind. Für eine konkrete zeitabhängige USB-Abweichung nach 30 Minuten liegt kein reproduzierter Fehler bzw. begründeter Verdacht vor.

**Disposition:** `IV2-020-R02-F01 = WITHDRAWN_BY_REVIEWER`, ausdrücklich **kein** `FIXED_BY_IMPLEMENTER`. Aus F01 folgt **keine** Umsetzungsaufgabe, **kein** weiterer 30min-/100-Activation-Test, **keine** zusätzlichen realen USB-/Hardwareversuche und **keine** neuen menschlichen Sprachproben. Historische Testergebnisse und Scopegrenzen unverändert erhalten. Daraus folgt noch **kein Gesamt-ROOT_PASS**.

### IV2-020-R02-F02 – REAL-05 / REAL-06: unbegrenztes aktives Sessionledger und unzureichender Ressourcenbeleg (**EINZIGES OFFENES PFLICHTFINDING**)

**Vorgabe:** TEST_UND_ABNAHMEPLAN §6 verlangt keine stetig wachsenden abgeschlossenen Tombstones/Runtimeledger ohne begründetes Retentionkonzept; REAL-05 fordert Queue-/Task-/Memorykontrolle.
**Ist/Quellnachweis:** voice_stt_client/core/activation_mirror.py – _reset erzeugt unbeschränkte dicts activations, segments, _seen, _sequences; normale Eventreduktion ergänzt Einträge bis Sessionende. Nur der Gap-Puffer hat max_events/max_bytes. Mirror.view kopiert die vollständigen Maps pro Projektion. voice_stt_client/core/final_results.py – V2ResultService._terminals erweitert sich für jedes finale Segment und wird erst bei Generationswechsel/Close geleert. Die 100er Messung forcierte drei Reconnects, so dass maximal 25 Aktivierungen derselben Session gehalten wurden. Das beweist keine Begrenzung bei einer dauerhaft verbundenen Sitzung.
**Wirkung:** Über Stunden/Tage verbundene Sessions können Linearwachstum an Identitäten/Tombstones und zunehmend teure View-Projektionen erzeugen; für den langfristigen Hintergrundbetrieb fehlt die geforderte Begrenzung.
**Erforderliches Ergebnis (Umsetzer):** Unkontrolliertes Wachstum der gehaltenen Session-/Terminalzustände während einer fortlaufenden, nicht reconnectenden Sitzung wirksam verhindern oder mit überzeugender Code-/Testbegründung entkräften. Jede Retention-Änderung muss ausstehende Finals, Out-of-order-, Replay-/Gap-, Unknown-outcome- und Exactly-once-Garantien wahren: keine pauschale Löschung mit später doppelten History-/Pastewirkungen. **Minimalnachweis:** Wenige gezielte Regressionen, darunter eine deterministische Folge von mehreren hundert Activations in derselben Session mit prüfbaren Grenzen für Register-/Snapshotgröße und Replay-/Duplikatsicherheit. Bestehende Tests wiederverwenden; keine zusätzlichen 30-Minuten-, Realmodell-, Hardware- oder menschlichen Sprachtests wegen F02. Anschließend ohnehin vorgeschriebene vollständige Windows-CI am neuen Kandidaten; weitere Nachweise nur bei konkreter Risikolücke. Kein vorsorglicher Architekturumbau.

## Zusätzliche Aktenkonsistenz (administrativer Korrekturhinweis)

WORKFLOW_STATUS.json enthält historische observations mit OPEN_INVESTIGATION/PARTIALLY_PROVEN bzw. VISUAL_CONFIRMATION_PENDING (O01, O02, T03), während aktuelle Abschlussmatrix sämtlichen M-Fällen remaining=null zuweist. Diese Einträge müssen als historische Beobachtungen oder tatsächliche aktuelle offene Risiken eindeutig unterschieden und mit dem Reviewstand synchronisiert werden. Historische Fehlläufe, W02-Dispositionsentscheidung und ungelöster ursprünglicher ReSpeaker-Autopasteversuch dürfen nicht stillschweigend umgedeutet werden.

## Verdict, Grenzen und nächste Aktion

**CHANGES_REQUIRED: Kein ROOT_PASS, kein Merge, keine Release-/Serverpromotion.** Nach Rücknahme von F01 verbleibt **genau ein** blockierendes fachliches Reviewfinding, `IV2-020-R02-F02`. Komplementäre M-12-/USB-/Dauerlaufbelege werden anerkannt, ohne Gesamt-ROOT_PASS vorwegzunehmen. Nach den ausschließlich dokumentarischen Folgecommits scheiterte die CI auf `840a0e5ffdf9a379c51bc1d367e977f76e02a262` an einer eigenständigen Testflakiness, siehe [Issue #16](https://github.com/marcosudau-vps/voice-stt-client/issues/16); CI auf dem ursprünglichen geprüften Kandidaten war grün.
Reviewverfahren: unabhängige statische Prüfung der commitgebundenen Produktionspatches, ausgewählter Test-/Hilfsquellen, Paket-/Requirement-/Evidenzakten und der eingereichten Windows-/Realreports sowie GitHub-CI; keine eigene Hardwaredurchführung und keine erneute Windowsvollsuite. Externe Windows-/Hardwareergebnisse als Fremdbelege geprüft, nicht als selbst ausgeführt ausgegeben.
Umsetzer: im selben Paketbranch **nur R02-F02 und das separat beauftragte CI-Issue #16** zielgerichtet beheben, vorhandene Nachweise wiederverwenden, gezielte Regressionen plus reguläre Windows-CI durchführen und PR #15 als REVIEW_READY für eine unabhängige Nachabnahme übergeben. F01 ist zurückgenommen und verlangt keine Korrektur. Danach unabhängige Gesamt-Nachabnahme. Menschliche kanonische Übernahme erst nach unabhängigem ROOT_PASS und separater Freigabe.

Siehe EVIDENCE/INDEX.md für genaue Prüflinks und Beleggrenzen.
