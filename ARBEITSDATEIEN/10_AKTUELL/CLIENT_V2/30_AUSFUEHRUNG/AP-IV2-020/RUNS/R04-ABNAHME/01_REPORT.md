# AP-IV2-020 – R04-ABNAHME / ROOT_PASS

Datum: 22.10.2026. Unabhängige neue ChatGPT-Nachabnahme nach R03-KORREKTUR. Gegenstand: kompletter ausgewählter kumulativer Paketkandidat PR #15 und die konkret geänderten R03-Teile; keine eigene Windows-/Hardwareausführung.

## Prüfkandidat und Provenienz

- Repository `marcosudau-vps/voice-stt-client`, PR https://github.com/marcosudau-vps/voice-stt-client/pull/15, Base `feat/client-v2`, Paketbranch `work/client-v2/ap-iv2-020`, Draft zum Prüfzeitpunkt.
- **reviewed_sha:** `ca56b5ab58c47bd97bae36335e9d9314b2d35294`; **reviewed_tree:** `631276f5ba11d49425c052e0fec5ec29636b55a9`.
- **canonical_parent / Base:** `b80ed8b81ad92bd02ac32553883443d2b7673bcd` (unverändert, Vorgänger AP-IV2-010 übernommen).
- **finaler qualifizierter Code-/Testcommit:** `09b16c0f79e3251d3854112a38129527c79029c1`, Tree `21d5efbba4e1c7d06f36eabb6ae919416d6b6e58`. Diff von dort zu reviewed_sha: ausschließlich Run-/Status-/Log-/Evidenzdokumentation, keine weiteren Produkt-, Test- oder CI-Änderungen.
- **gebundener Server:** `67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, Tree `74f37cad84c5be9e74d880a4b10c3d9623de7da3`, Pro-V2 /ws/v2; historische Vertragsherkunft `ada13b0`. Keine Servermutation.
- Paketumfang über alle **1598 PR-Dateinamen**, R01/R02-Reviewkontext und die drei R03-Korrekturcommits abgegrenzt: im neuen Korrekturdiff nur `activation_mirror.py`, `final_results.py`, `tests/test_v2_mirror.py`, `tests/test_v2_results.py`, `tests/test_event_stream.py` plus notwendige Dokument-/Belegakten. Kein unerlaubter Produktnebenumbau erkennbar.

## Unabhängige Sachprüfung der beiden Korrekturen

### R02-F02 – **CLOSED_VERIFIED_R04**

- `ActivationMirror`: begrenztes `_seen` (max_records plus explizit gepinnte Buffer-Fingerprints), `_retain` verdichtet nur zusammenhängende nachweislich abgeschlossene Activation-/Segmentpräfixe; neue monotone retire-Watermarks schützen alte Wiresequenzen. Maximal 64 reguläre Detailactivations; 1024 offene/unklare Register als konservatives Ressourcenbudget (plus auslösender Record), bei Überschreitung `session_retention_overflow`, `RECONNECT_REQUIRED` und `incomplete` statt stiller Löschung. Alle Buffer bereits separat begrenzt.
- Retentionsguards berücksichtigen ausstehende/fehlende Finals, Terminal-/Acceptedcounts, Input-Close, Foreground, historische Snapshot-/Gap-Salvage und unklare Outcomes. Kein TTL-basiertes Löschen. `_snapshot` validiert retire-Schwellen; Retentionsereignisse werden nicht als neue Domainereignisse publiziert.
- `V2ResultService`: behält `_terminals` nur für die aktuelle Mirror-Segmentprojektion und blockiert Wiederpublikation historischer Reduction-Finals durch monotonen `_last_final_event_seq`; konkrete Bindungs-/Identitäts-/History-/Queuechecks bleiben bestehen. Ursprüngliche Duplicate-Callbacksemantik wurde nach einem zielgerichtet aufgedeckten Suitefehler wiederhergestellt.
- Reale Code-/Regressionprüfung: `test_600_activations_one_session_bound_registers_and_effects` mit 600 aufeinanderfolgenden Activations ohne Reconnect, 600 Historyeinträgen und 600 kontrollierten Injektionen; Register jeweils höchstens 64, `_seen` höchstens 1024. Ergänzende Tests für spätes Final (200 weitere Activations), Gap-Snapshot-Salvage, Cancel/Failed/Empty, Replay nach Retention, Unknown-outcome und sichtbaren Budgetüberlauf. Keine doppelten Sideeffects im geprüften Testumfang.
- Bewertete Grenze: Permanentes ungeklärtes Ergebnis verhindert absichtlich Compaction und führt im Ressourcenlimit zu kontrollierter Recovery; das ist eine explizite, sichere Grenze und kein verbleibendes unbegrenztes Wachstum. Kein eigener erneut verlangter 30-min-/Hardwarelauf.

### GitHub-Issue #16 – **TECHNISCH VERIFIZIERT (Issue bleibt bis separater Pflege offen)**

- Der instabile Happy-Path-Semantiktest verwendet nun testlokale logische Protokollzeit und einen In-Memory-Cursor mit Bindungs-/Commitprüfungen; die echte Disk-I/O und Replay-/Speicherfehler bleiben in getrennten Store-/Transporttests geprüft.
- Originalassertions zu Subscribe/Token nur im ersten Frame, Replay/Live, Cursor 3→24, Bindung, Generation und Stop bestehen fort. 280-ms-Commitverzögerung als gezielte Regression; unerwarteter Reconnect wird vor erneutem Verbrauch desselben Script-Sockets mit Originalfehler sichtbar abgebrochen. Der reale äußere Sicherheitswatchdog bleibt.
- `event_stream.py`, `event_protocol.py`, `event_cursor_store.py` und CI-Workflow im R03-Korrekturdiff **nicht** verändert. Kein pauschaler Retry oder bloße willkürliche Timeouterhöhung.

## Pflichtqualifikation und Quellenstatus

- **Eigene Reviewprüfung:** commitgebundene Quellen/Code, komplette R03-Dateiliste und fachliche Diffgrenzen, bestehende R02-Feststellungen, Testlogik, Requirement-/Paketmatrix, CI-Head und tatsächliche CI-Jobschritte. Keine eigenen Windows-, ReSpeaker- oder Modellversuche (NOT_RUN durch Reviewer; nicht abnahmeblockierend nach Qualifikationsregeln).
- **Fremdbeleg R03 lokal Windows:** 1407 bestandene Tests/79 Module/0 Skips, Python 3.12.10 auf Windows 11; vollständiges Logarchiv `R03-KORREKTUR/EVIDENCE/windows-suite.zip`, dokumentierter ZIP-SHA256 `06bc370a8c1656c76415f8cee78d5aa49b63c2d12c41008693ac54480362abc6`, Befehl und lokale Commitbindung im R03-Index. Anfangs roter Anschlussfall und dessen konkrete anschließende Reparatur offen berichtet, danach vollständige finale Suite grün. Kein eigener Hashabgleich des Binär-ZIPs behauptet.
- **Unabhängig aus GitHub geprüfter CI-Beleg:** [GitHub Actions Run 39734511679](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/39734511679), Trigger pull_request, Head `ca56b5ab58c47bd97bae36335e9d9314b2d35294`, Status completed/**success**. Windowsjob 119676963735: `Ran 1407 tests in 224.774s / OK`, danach compileall, vollständiger EXE-/GUI-Smoke, Wheel/sdist, installierter Wheel-Smoke, Artefaktupload alle success. PR-Testmerge `9cdaf1d4bca522449968ea20a782062979d68f27`, unveränderte Base.
- **R01-Realnachweise unverändert komplementär anerkannt:** M-01 bis M-12 auf tatsächlicher Windows-/ReSpeaker-/ASR-/Wake-/Clipboard-/Frozen-/Serveridentität in [R01 Abschluss40](../R01-UMSETZUNG/40_REVIEW_READY_UND_KONSOLIDIERTE_QUALIFIKATION.md) und seiner Matrix. R03 änderte Retention/Tests, nicht die native Audio-/UI-/Server-/Clipboardimplementierung; keine pauschale Neudurchführung ohne fachliche Lücke. Historische gescheiterte Versuche, Grenzen zur erhöhten UAC-Zielanwendung, W02-Menschendisposition und fehlende Zuordnung einzelner früherer Nutzermeldungen bleiben getrennt dokumentiert.
- **R02-F01:** bereits vor R03 als `WITHDRAWN_BY_REVIEWER` zurückgenommen; komplementäre Dauer- und physische USB-Nachweise zulässig. Nicht fälschlich als R03-Fix oder als neue 30min/USB-Qualifikation verbuchen.
- Administrative R03-Statusdateien kennzeichnen verbliebene historische `OPEN_INVESTIGATION`-/`PARTIALLY_PROVEN`-Beobachtungen ausdrücklich mit `scope=HISTORICAL_RUN_OBSERVATION`; sie sind nicht automatisch neue aktuelle Pflichtfindings.

### Requirement-Bewertung

| ID | R04-Urteil | Grundlage |
| --- | --- | --- |
| REAL-01 | PASS | M-01..M-04 und echte native Bedienpfade aus R01, unverändert |
| REAL-02 | PASS | ReSpeaker/Mute/Recovery/Live-Wake- und Modellbelege aus R01, unverändert |
| REAL-03 | PASS | M-12-Dauer und komplementäre Hardware-/Wakebelege; R02-F01 zurückgenommen |
| REAL-04 | PASS | Credential-/Clipboard-/Admin-/Frozen- und negative Fälle aus R01, mit dokumentierten Grenzen |
| REAL-05 | PASS | M-12-Ressourcen + R03 sichere Retention/Overflow und Regression mit 600 Activations |
| REAL-06 | PASS | Vollständige Pflichtmatrix, unabhängige Prüfung, R03-CI und vorgenannte methodische Begrenzungen |

## Verdict und Folgeschritt

**ROOT_PASS – 6/6 REAL-Requirements unabhängig fachlich angenommen; 0 offene Pflichtfindings.** R02-F02 nach R03 nachweislich geschlossen; R02-F01 ausdrücklich zurückgenommen. Issue #16 technisch behoben und unabhängig anhand der Teständerung plus erfolgreicher finaler Windows-CI bestätigt. Keine neuen blockierenden Abnahmebefunde.

**Workflow: WAITING_FOR_APPROVAL.** Kein Merge/Release/Serverpromotion und kein Folgepaketbeginn durch dieses Urteil. Für die kanonische Übernahme von PR #15 auf `feat/client-v2` ist eine **separate ausdrückliche menschliche Freigabe** einschließlich finaler CI-/Head-/Base-/Docs-Diffprüfung erforderlich. Das gegenständliche PASS bezieht sich ausschließlich auf `reviewed_sha/tree` oben; der anschließend nur administrativ ergänzte PR-Head ist nicht derselbe SHA.

Siehe [EVIDENCE/INDEX.md](EVIDENCE/INDEX.md) für direkte Quellen.
