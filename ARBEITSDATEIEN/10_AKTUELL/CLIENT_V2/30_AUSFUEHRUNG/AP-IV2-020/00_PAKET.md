# AP-IV2-020 – reale Windows-, Modell- und Hardwarequalifikation

Status **BLOCKED**, Workflow **SERVER_FIX_REQUIRED**, 2026-10-18.
Rolle: ein Umsetzer, R01-UMSETZUNG. Schreibhoheit: Codex in dieser Session.
Branch `work/client-v2/ap-iv2-020`, Base `feat/client-v2`, tatsächlicher Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
Serverbasis `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Clientprodukt erhält ausdrücklich freigegebene enge Recoverykorrekturen; neue Qualifikation erforderlich.

[Vertrag](../../PLANUNG/ARBEITSPAKETE/AP-IV2-020.md), Planung Revision 10,
Rollenregelversion 7. Keine Produktcodeänderung ohne gesonderte Freigabe.
Keine kanonische Übernahme, Releases, Tags oder Serverpromotion beauftragt.

- [Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md)
- [Laufender Report](RUNS/R01-UMSETZUNG/01_REPORT.md)
- [Evidenzindex](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md)

AP-IV2-010 nach unabhängigem R02-ROOT_PASS und menschlichem R03-Prompt
tatsächlich per PR14-Squash übernommen. Nachmergebeleg in dieser Akte.
Reale Pflichtfälle bleiben bis zur Durchführung NOT_RUN/NOT_PROVEN.

Zehn technische Reconnect-/Recoveryfindings behoben; [Audit und neue Qualifikation](RUNS/R01-UMSETZUNG/05_RECONNECT_AUDIT.md).
Keine fachliche Abgabe. R01-Schreibhoheit bleibt für autorisierte Fortsetzung erhalten.

Kumulativer [Draft-PR #15](https://github.com/marcosudau-vps/voice-stt-client/pull/15), Base feat/client-v2.
IN_PROGRESS, kein REVIEW_READY; R01 behält Schreibhoheit für die genehmigte Fortsetzung.

## Scope-Ausnahme bei Fortsetzung R01 (2026-10-15)

Der [menschliche Fortsetzungsauftrag](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md) erlaubt eng auf Client-Reconnect/Recovery begrenzte Produktcode- und Testkorrekturen einschließlich weiterer nachgewiesener zusammenhängender Fehler. Dies ersetzt die ursprüngliche Produktcode-Sperre ausschließlich in diesem Scope. Derselbe R01, Paketbranch und Draft-PR #15 bleiben aktiv. Neue Produktidentität erfordert neue Windows-, Build- und Paarqualifikation; bisherige Nachweise bleiben historische Evidenz. Keine Servercodeänderung, Protokoll-/Sicherheitsänderung, Promotion, Release, Tags oder kanonische Übernahme freigegeben. Keine unabhängige Abnahme vorweggenommen.

## Zusätzliche Produktausnahme UX01, gleicher R01

[Ausdrücklich freigegeben](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/006_UX01_FREIGABE.md): bestehende Einstellung Leerzeichen anhängen wirksam machen, rohe Finals/History/Deduplizierung erhalten, dauerhafte Regressionen und neue Produkt-/Buildqualifikation. Produkt17261e6, neue [Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/ux01/INDEX.md). Keine sonstige Erweiterung der ursprünglichen Qualifikationsausnahme. Reale Pflichtfälle bleiben bis zur vollständigen Durchführung offen.

## Zusätzliche Produktausnahmen UX02 und UX03, gleicher R01

UX02 ist [ausdrücklich freigegeben](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/012_UX02_FREIGABE.md)
und am Produktd95043e technisch sowie physisch belegt: begrenztes Warten auf
freigegebene Modifiertasten vor nativer Einfügung, keine künstlichen Key-Ups.

UX03 ist durch den [direkten Fixauftrag vom18.10.2026](RUNS/R01-UMSETZUNG/09_UX03_CLOSE_SOUND.md)
freigegeben: fehlenden Beendigungston an serverbestätigtem Eingabeschluss
korrigieren, einschließlich Regression und neuer Kandidaten-/Buildqualifikation.
Produkt7bb5646, [Belege](RUNS/R01-UMSETZUNG/EVIDENCE/ux03-close-sound/assessment.json).
Kein Server-/Wirewechsel. Die ergänzte [Sound-/LED-/Triggerübersicht](RUNS/R01-UMSETZUNG/10_FEEDBACK_UEBERSICHT.md)
unterscheidet wirkliche V2-Ausgaben von lediglich deklarierten Regeln.

## Serverblocker IV2-020-W01

[Livebefund, echter Modellrepro und konkreter Korrekturweg](RUNS/R01-UMSETZUNG/12_WAKE_REAKTIVIERUNG_W01.md). Serverfix noch nicht beauftragt/instanziiert; Clientprodukt/Parent unverändert. Kein REVIEW_READY.
