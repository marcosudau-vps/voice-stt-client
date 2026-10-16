## Livebestätigung mit getrennten Startknöpfen, 16.10.2026

[Bewerteter Durchgang](stepped-20261016-01/assessment.json), [unveränderter Prozessbericht](stepped-20261016-01/stepped-trial.json), vollständige minimierte Event-/Ack-/Metrik- und Quellidentitätsprotokolle daneben als `.json.gz`. Beide direkten Nutzsätze vollständig und sichtbar mit Leerzeichen, Nutzerbestätigung stimmt mit Editorhash überein. Zwei separate Sitzungen; F9 mangels Activationack und wegen timed_out unbewiesen. Quelle exakt Produkt17261e6, M02 insgesamt offen. [Neue passive Hotkeydiagnose vorgeprüft](hotkey-task-precheck/summary.json).

## Aktualisierung: UX01 geschlossen, Sprache wird getrennt gestartet

[Native Bestätigung](repeat-01/native-editor-spaced.json) und [exakte Produktbindung](repeat-01/native-product-binding.json) PASS. Der automatisch gestartete Sprachversuch hatte null Activations/Finals, menschlicher Übergang verpasst, daher [NOT_RUN_HUMAN_SPEECH](repeat-01/voice-attempt-assessment.json). Native Probe nicht erneut nötig; nur zwei Wake-Sätze nach explizitem Sprachstart offen.

# UX01 – Produktkorrektur und erneute Qualifikation

Die [ausdrückliche Freigabe006](../../ZUSATZPROMPTS/006_UX01_FREIGABE.md)
erlaubt diese begrenzte Ausnahmekorrektur im selben AP020/R01.
Status: **technische Qualifikation einschließlich nativer Ausgabebestätigung PASS**, kein vollständiges Realgate-PASS.

- [Vorherige relevante Baseline](../human/ux01-current-product-baseline.json):
  67 bestehende Injection-/Reinsertiontests PASS am alten Produkt.
- [V2-Ergebnisbaseline](../human/ux01-v2-results-baseline.json): PASS.
- [Gezielter ursprünglicher Fehlernachweis](../human/append-space-red.json).
- [Dauerhafte Regression vor Produktfix](../human/ux01-permanent-red-corrected.json):
  fünf Tests, drei tatsächliche Leerzeichenfehler.
- [Gezielte Regression nach Fix](../human/ux01-targeted-green-final.json):
  100 Tests PASS, einschließlich fünf neuer komponierter Regressionen.
- [Vollständige Windows-Suite vor Kandidatencommit](windows-full-precommit.json).

Die Protokolle liegen jeweils vollständig als `.txt.gz` neben den JSON-Belegen;
JSON enthält Befehl, Runtime, Quellhashes vorher/nachher und Exitcode.
[Finale technische Identitäten und Nachweise](qualification-summary.json): Produkt17261e6, neue EXE56fe943b… und Wheel/sdist, voller Paarlauf erfolgreich.
Frühere Produkt41-Belege bleiben unverändert historisch. Keine Übertragung
offener menschlicher Pflichtfälle auf den neuen Build.

Windows-Vollsuite vor Commit: **1378 PASS, keine Skips**, 210.906s. Native Probe ohne menschlichen Fokus: **NOT_RUN**, Zwischenablage blieb unverändert. Kein Produktfehler abgeleitet; Fokusaktion wird mit dem nächsten menschlichen Block gebündelt.

## Weitere ausgeführte Nachweise am Produkt17261e6

- [Saubere neue Builds und Hashes](build/artifacts.json), [Releaseguard](build/release-guard.json), [Twine](twine.json). Keine Veröffentlichung.
- [Neue Frozen-GUI an echtem lokalen Server](frozen-native-real-server.json), [frisch installiertes Wheel](wheel-runtime.json), [native Desktop-/ReSpeaker-Recovery](native-desktop-restart.json), [realer kompletter Reconnectlauf](real-recovery.json).
- [Native Hotkeys](windows-hotkeys.json), [native Settings/Credential-UI](windows-settings.json).
- [Konfiguration Save/Load](config-roundtrip.json): alle drei isolierten Profile speichern5000ms Follow-up,320ms Pre-Roll und bestehendes append_space=True unverändert. Kein globaler Default geändert.
- [Sechs echte Wake-Replays](real-wake-replay320.json): direkte Jarvis-/Alexa-Nutzsätze exakt, drei Negativfälle ohne Aktivierung. Alexa-Pausentext weicht vom geplanten Satz ab (**FAIL** für exakte Zielphrase). [Vergleich ohne Wakeabtrennung](alexa-pause-differential.json) zeigt denselben Nutztext; Wakegrenze vollständig, tatsächlich gesprochener Wortlaut noch zu annotieren. Keine neue Clientursache nachgewiesen.
- [Echter SQLite-Ausfall](logstore-diskfull.json), [reproduzierbarer Helfer](../logstore_diskfull.py): separate kurzlebige Instanz, nur deren64MiB tmpfs bis ENOSPC gefüllt,30 tatsächliche SQLite-Fehler, Ack16ms und nichtleeres reales ASR-Final bei unveränderter STT-Session und Generation. Instanz kontrolliert gestoppt. Logtransport am Ende BACKOFF, vollständige Logerholung **NOT_PROVEN**. M07 insgesamt bleibt offen.
- [Kandidatengebundener Paarlauf](pair/validation.json) abgeschlossen: Windows1378 PASS/0skips, Server1964 PASS/14 begründete optionale Skips, elf Prozessfälle,17 Grenztests und7/7 Smokes PASS.
