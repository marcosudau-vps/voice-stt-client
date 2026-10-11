# AP-CV2-000 / R05 – ergänzender Windows-Nachweis und Abschluss

Datum: 2026-10-11 (Europe/Berlin). **Verdict: ROOT_PASS**, gemeinsam getragen durch den unabhängigen fachlichen R04-Review und den hier tatsächlich ausgeführten fehlenden Windows-Nachweis. Dieser Run implementiert keine Produktkorrektur. R04 bleibt unverändert mit seinem damaligen BLOCKED-Urteil erhalten.

## Auftrag und Identität

[Tatsächliche Nutzeraufträge und bedingte Übernahmefreigabe](00_PROMPT_ORIGINAL.md).

- reviewed/tested SHA: `7c4bb2f7d3f3a79d0b2f0beae5bdbae27795d0fe`; Tree `aeb7d5fa686d0e3bf0bfa114d55366bada688e54` in [Windows-Nachweis](EVIDENCE/windows-validation.json).
- R04-Produktreview: `cd872d4bfa8eccd0167337cbab16a572ca70bfd4`, Tree `6aff2fa629b0c01fde502c345e7e31035cee0926`; [R04-Bericht](../R04-ABNAHME/01_REPORT.md).
- canonical_parent: `050e776cf316eb332177294db0c0a2719c2b4415`; PR [#2](https://github.com/marcosudau-vps/voice-stt-client/pull/2), Paketbranch `work/client-v2/ap-cv2-000`, Ziel `feat/client-v2`.
- server_sha: `ada13b011e1d3829f78e7f389e3b927795a2b3be`, unverändert.

Vom R04-Prüfkandidaten bis zum aktuellen Test-SHA wurden ausschließlich zehn Arbeitsunterlagen geändert. Produkt-, Test-, Build-/CI- und Abhängigkeitsstand sind identisch. Der eigene Windows-Lauf erfolgte im neu angelegten sauberen Detached-Worktree auf exakt diesem SHA; Quellimport stammt nachweislich aus diesem Checkout. Python 3.12.10 aus der vorhandenen Projektvenv, Windows, Qt offscreen; der vollständige Runtime-/Befehlsnachweis liegt im JSON. Die Tests hinterließen keinen getrackten oder ungetrackten Produktdiff.

## Ergebnisse und Pflichtblocker

| Prüfung | Ergebnis | Nachweis |
| --- | --- | --- |
| Gesamte Windows-Clientsuite, unittest discover, alle `test_*.py` | **1.233 PASS, 0 Fehler, 0 Skips** | [Vollständiger Log](EVIDENCE/windows-full-unittest.txt), Exitcode 0, 99,219 s |
| Fünf StartupPersistence-Repros/Gegenfälle | **5 PASS** | [Gezielter Log](EVIDENCE/startup-persistence.txt) |
| compileall, Produkt/Skripte/Tests | PASS | [Log](EVIDENCE/compileall.txt) |
| Diffprüfung und sauberer Testcheckout | PASS | [Log](EVIDENCE/diff-check.txt), [Runtime/Status](EVIDENCE/windows-validation.json) |

`R04-T01` ist durch eine tatsächlich unabhängige ergänzende Windows-Ausführung geschlossen, nicht allein durch eine geänderte Regel oder ein grünes CI-Symbol. `CV2-R02-F01` war in R04 fachlich geschlossen; die fünf konkreten Regressionstests wurden hier zusätzlich selbst ausgeführt. Keine offenen Produktfindings oder Testblocker. R04s NOT_PROVEN-Abgrenzung für die unabhängige vollständige Regression ist damit ergänzt. BASE-01 bis BASE-12 sind technisch ROOT_PASS; Methoden-/Requirementzuordnung aus R01/R03 bleibt erhalten und erhält diese zusätzliche Abnahmequelle.

Build-/Installationsnachweise aus R03 und CI sind dem identischen Produkt-/Teststand zugeordnet. Die finale PR-CI muss vor Übernahme auf der tatsächlichen neuen PR-Spitze bzw. ihrem Head/Base-Testmerge SUCCESS liefern. Ihre abgeschlossene Identität und das tatsächliche Squash-Ergebnis werden erst aus GitHub/Git ermittelt, nicht hier vorweggenommen.

## Beauftragte Regelpflege für kommende Runs

Windows-Vollsuite verpflichtend im Umsetzungslauf mit vollständigen Logs und Kandidatenbezug; unabhängiger Reviewer prüft Code und Nachweis, keine routinemäßige zweite Windows-Vollsuite. ChatGPT darf commitgebundene GitHub-Dateien mit vollständigem Parentdiff nutzen. Bei geänderten testrelevanten Ständen, konkreten Fehlerverdachten oder unzureichenden Belegen verlangt der Reviewer Ergänzung bzw. erneute Qualifikation. Tatsächlich fehlende Pflichtnachweise und die zugeordneten realen Hardwarefälle bleiben blockierend.

Die ausdrückliche Regeländerung stammt vom Auftraggeber, nicht aus allgemeinem Reviewer-Schreibrecht. Rollen-Skills, Checklisten, Vorlage, Governance und Testplan werden gemeinsam angeglichen, Rollenregelversion 7 bei unveränderter Planrevision 10 und unveränderten Wirekontrakten. R04 hatte Workflow-/Arbeitsunterlagen auf Nutzerwunsch nicht inhaltlich bewertet; dieser Run beansprucht keinen rückwirkenden R04-PASS für sie. Konsistenz und Links der tatsächlich geänderten Unterlagen werden hier geprüft. Historische Auditempfehlungen und Originalaufträge sind keine aktuellen Testpflichten.

Die Aktenprüfung fand drei erneut falsch relativierte R04-Links im Paketindex; deren Zielpfade werden auf `RUNS/R04-ABNAHME/...` korrigiert. R04-Reports/Originalprompts bleiben unverändert. ChatGPT-Reviewer ohne lokalen Checkout können die gleiche Strukturprüfung commitgebunden über GitHub durchführen, ohne Windows-Venv. Das historische CP1252-Vollsuitenlog bleibt byteidentisch erhalten; die UTF-8-Lesefassung ist nachweislich textgleich.

## Grenzen und Übergabe

Kein neuer vollständiger Quellcodeaudit und keine physische Hotkey-/Clipboard-/ReSpeaker-/ASR- oder V2-Gesamtqualifikation behauptet. Die fachliche Reviewgrundlage bleibt R04 im vom Nutzer festgelegten Scope; dieser Run schließt dessen einzigen Testblocker und prüft die beauftragte Dokumentpflege. AP000 behält seinen vorhandenen V1-Transport. V2-Transport und reale Paketgates folgen gemäß Plan.

ROOT_PASS ist die technische Entscheidung. Der aktuelle Nutzerauftrag erlaubt anschließend die Einzel-Squash-Übernahme genau dieses Pakets nach grüner finaler CI und unveränderter Base. Neuere Produkt-/Teständerungen würden diese Qualifikation ungültig machen. Bis zum tatsächlichen Merge bleiben Unterlagen ROOT_PASS / READY_FOR_CANONICALIZATION; erst Git-/PR-Provenienz beweist CANONICALIZED. Keine automatische Umsetzung von AP-CV2-010. [Evidenzindex](EVIDENCE/INDEX.md).
