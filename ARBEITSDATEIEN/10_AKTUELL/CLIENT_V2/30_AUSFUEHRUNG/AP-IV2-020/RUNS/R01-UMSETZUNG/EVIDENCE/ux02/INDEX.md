# UX02 – freigegebene Modifiertastenkorrektur

[Zusatzfreigabe012](../../ZUSATZPROMPTS/012_UX02_FREIGABE.md), gleicher R01/Branch/PR15. **Produkt d95043e technisch PASS; physische Bestätigung offen.**
[Verifizierte Gesamtauswertung](qualification-summary.json), [reproduzierbarer Evidenzprüfer](aggregate_qualification.py).

- [Baseline100](baseline.json), [dauerhafter Rotbeleg](permanent-red.json), [präzisierte Restore-Faultfixture](targeted-green-attempt1.json), [112 gezielte PASS/zwölf neue Regressionen](targeted-green-final.json), [ursprünglicher komponierter Nachweis grün](original-composed-green.json).
- [Vollsuite und Paar](pair/validation.json):1390 Windows/0 Skips,1964 Server/14 erwartete optionale Skips,11 Prozessfälle,17 Grenztests,7 Socketsmokes;555 Serverblobs geprüft. [Erster vor Tests gestoppter Preflight](pair-preflight-attempt.json) erhalten.
- [Echte Recovery](real-recovery.json), [aus Vollstdout rekonstruierte Zusammenfassung](real-recovery-summary.json), [vollständiger Trace](real-recovery-trace.json). Namenskollision des Detail-JSON offen dokumentiert.
- [Native Desktop-/ReSpeaker-Neustartprobe](native-desktop-restart.json), [40 Ressourcenmessungen](native-desktop-metrics.json), [native Hotkeys](windows-hotkeys.json), [native Settings/Credentials](windows-settings.json).
- [Neue EXE/Wheel/sdist-Hashes](build/artifacts.json), [PyInstaller](build/pyinstaller.json), [Distributionsbuild](build/distributions.json), [Releaseguard](build/release-guard.json), [Twine](twine.json), [EXE-Laufzeit](frozen-native-runtime.json), [isolierte Wheelinstallation](wheel-install.json), [Wheel-Laufzeit](wheel-native-runtime.json).
- [Drei unveränderte Testprofile/temporärer Roundtrip](config-roundtrip.json).
- [Neue echte Modellreplays](real-model-replay-summary.json), [vollständiges Commandlog/Quellbindung](real-model-replay.json): zwei direkte Nutzsätze exakt; Alexa-Pausensatz geplanten Wortlaut verfehlt, tatsächliche Sprachannotation offen; drei bekannte Negative ohne Aktivierung. Kein nativer Hardware-PASS aus Replay.
- [Finale Veredict-/Attemptguardprüfung](native-verdict-final.json), [echte Qt-Anzeigenprüfung](native-labels-final.json), [Compile der Helfer](native-helpers-compile.json). [Physische Probe](../human/native_modifier_trial.py) und [GUIadapter](../human/native_modifier_editor.py) warten auf bewussten eigenen Start. Nur native physische Tasten/Produktqueue/own Qt-Editor; kein Mikrofon/Server. Vollständige M-Fälle weiterhin offen.

Bei Commandbelegen jeweils vollständige Logs .txt.gz plus Befehl, Runtime, Exit und Vorher-/Nachherquellidentität. Historische Rot-/Fehlversuche bleiben erhalten. Release NOT_PUBLISHED, kein REVIEW_READY.
