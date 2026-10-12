# Evidenz AP-CV2-060 / R01-UMSETZUNG

[Report](../01_REPORT.md), [Originalauftrag](../00_PROMPT_ORIGINAL.md). Status **REVIEW_READY**, unabhängige Abnahme offen.

| Beleg | Erzeugung/Inhalt |
| --- | --- |
| [Vorgänger](predecessor-canonicalization.json) | Git show/rev-list/rev-parse und gh pr view7: PASS, menschlicher Prompt, gemergter PR, Parent/Treegleichheit |
| [Vertragshashes](start-contract-hashes.json) | SHA256 von git show Parent:path vor Statuspflege |
| [Baseline](baseline.txt) | Projektpython, relevante bestehende Module, 212 PASS vor Änderungen |
| [Windowsmanifest](windows-validation.json) | Vollständige Befehle/Runtime/Zeiten/Exitcodes/Loghashes und qualifizierte Gitblobs |
| [Getesteter staged Produktdiff](tested-product.patch.base64) | git diff --cached --binary --unified=0 HEAD -- voice_stt_client tests scripts |
| [Gezielte Suite](targeted-unittest.txt) | 323 PASS, -W error |
| [Servercheckpoint](server-results-checkpoint.json) / [stderr](server-results-checkpoint.json.stderr.txt) | 19 PASS, 46 gepinnte Quellblobs vor/nach Lauf geprüft |
| [Compileall](compileall.txt) | Exit0, vollständiger leerer Log |
| [Windowsvollsuite](windows-full-unittest.txt) | 1426 PASS, keine Skips |
| [Requirementmethoden](requirement-coverage.md) | RESULT-01 bis RESULT-13 einzeln; zusätzlicher bestehender Clipboard-/Elevated-/Reinsertvertrag in gezielter Suite |
| [Runner](qualify_windows.py) | Reproduzierbare sequentielle Befehle, Sources vor/nach Lauf unverändert |
| [Abgabeverifikation](submission-validation.json) | Produktblobs und Loghashes, unveränderte Fachkriterien, Methoden-/Link-/Status-/Diffchecks |
| [Erster Vollsuiteabbruch](windows-full-unittest.txt.first-timeout.txt) / [Manifest](windows-validation.json.first-timeout.txt) | TIMEOUT300s, superseded durch unveränderten Kandidaten im finalen PASS |

Qualifikation 2026-10-12T14:53:34.706117+00:00 bis 2026-10-12T14:56:04.083520+00:00. Python3.12.10/Windows11/PySide6 und weitere genaue Identitäten im Manifest. Runner: `.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/EVIDENCE/qualify_windows.py`. Sourcehashes sind lokale Bytes; Gitblobs normalisierte veröffentlichte Inhalte. Finale Logs sind UTF-8/LF, auf genau diese Dateien beziehen sich die SHA256.

Serverbaseline `ada13b011e1d3829f78e7f389e3b927795a2b3be`, Clientbasis `ce95c66a7a3b4440faaa33289351871a040ebe19` plus exakter staged Produktdiff. Tatsächliche TCP-/WebSocketserverroutes und Clientworker; Recorder/Inferenz und Clipboard/SendInput mit kontrollierten benannten Adaptern. Kein Nutzeraudio, Nutzerclipboard oder Secret in den Belegen. Crashfälle verwenden temporäre echte SQLite-Dateien und reale Kindprozessabbrüche.

Weitere Dateien baseline/first-regression/results-*/server-results-*/targeted-prequalification sind iterative Diagnosebelege, im Report eingeordnet. Ihr Name und Inhalt gelten nicht als aktuelle Qualifikation. Der veröffentlichte abschließende Produktstand wird gegen qualifiedGitBlobs geprüft; administrative PR-Nachträge erfordern keine neue fachliche Vollsuite.


Der exakte Produktpatch wird verlustfrei als Base64 transportiert, weil enthaltene entfernte Legacyzeilen nachgestellte Leerzeichen besitzen. productDiffSha256 bezieht sich auf decodierte Patchbytes, productDiffArtifactSha256 auf das veröffentlichte Artefakt. Decode: `base64.decodebytes(Path(artifact).read_bytes())`; keine getestete Quelle wurde verändert.


[PR #8](https://github.com/marcosudau-vps/voice-stt-client/pull/8) gegen feat/client-v2. Früherer vor CI-Selbstkorrektur qualifizierter Umsetzungscommit `66b6e39daa86855ae1314025bc06344eb55f7d39`, Tree `fbe3931c3b68efa510bee1e35db4b77ad7a83f27`. Nachfolgende Veröffentlichungsverweise sind rein administrativ; endgültige eingereichte SHA/Tree stehen in aktueller PR-Beschreibung und finaler Übergabe.


CI-Selbstkorrektur: [vollständige CI-Failure](ci-first-failure.txt), [lokaler Vorher-Repro](ci-path-repro-before.txt). Alle Pflichtbefehle danach mit neuem Testblob wiederholt; aktuelles Windowsmanifest 2026-10-12T15:10:56.388352+00:00 bis 2026-10-12T15:13:25.899663+00:00. Basis 66f44e0be1ec9485d90ec0b918bffafdab2d57f0 plus staged Testkorrektur; Paketparent unverändert. Frühere Logs/Manifest/Patch liegen unter *.before-ci-fix.txt und sind als frühere Qualifikation superseded. Der finale Test nutzt ausdrücklich einen Pfadalias und bleibt strenger Negativfall.


Maßgeblich nach CI-Selbstkorrektur: aktuelles Windowsmanifest mit getesteter Basis 66f44e0 plus staged Pfadalias-Testkorrektur, vollständig neu qualifiziertem Testblob und allen 195 qualifizierten Produktblobs. Finale Kandidaten-SHA/Tree stehen in PR und Übergabe.
