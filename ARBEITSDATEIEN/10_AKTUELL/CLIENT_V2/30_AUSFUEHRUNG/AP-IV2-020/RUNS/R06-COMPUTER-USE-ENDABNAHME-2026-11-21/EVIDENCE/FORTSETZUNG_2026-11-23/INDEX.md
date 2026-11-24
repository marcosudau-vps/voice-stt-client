# Nachweisindex: Fortsetzung durch ChatGPT, 23.11.2026

Lokaler Nachweisordner: `C:/Users/marco/OneDrive/Desktop/Voice-STT-Client-V2-Finalabnahme/Nachweise/korrektur-2026-11-23`. Enthält die ausgeführten Hilfsskripte, Rohlogs und isolierten Profile; keine privaten Aufnahmen. Repo enthält Ergebniszusammenfassungen. Produktdiff und Dateifingerabdrücke: continuation-provenance.json.

| Datei | SHA-256 |
|---|---|
| live-correction-retest.json | 7fb76a4eed31cfe745866ad20f818ac803b085a274491f9f6fe94bc9dde18d87 |
| native-desktop-retest.json | 59e6593d110ff82b3dd22ad4fbd7258ffbb67457d13a61a68dadd35c386cbde3 |
| native-desktop-settings-retest.json | 8db2df319a8c4a72097a33dea9fe1938e93f899af5214083d61a94e89e439606 |
| native-desktop-settings-retest-repeat.json | 41971ec021c2481d27043517a5aa639fd5bd9b1c3bd817dc8d94d8f840d4e32d |
| native-desktop-settings-retest-final.json | cdc0d20411a88298ca9140bab5094ac3df0b4a611797ccc14e02aeef4b411305 |
| native-frozen-local.json | 62c87ba2d1b41bc56a35c8cc8c5c8fa0aa4f338a81eb426ab38812e75ae92bfc |
| native-frozen-onedrive.json | 0e20ee581ad1d05eeebd6d3961525c2678255d984a338f758334a9e8a0d06e16 |
| continuation-provenance.json | 47ef22967932e46e58d1a9d3403d5c98d300e56910da9f69ee75229ed1c29b49 |

Sechs Windows-QPA-Einzeltests (Rohlog im lokalen Nachweisordner, je Exit 0 / OK):
- native-test_decision_cancel_default_and_all_three_choices.log: 4acb3b809eea4183aac4097e18fcd2231120863b4c6166241477a1429e729d91
- native-test_duplicate_hotkey_names_both_fields_without_saving.log: ed71bcd3fe6cf20dbe8d8a79a3bc752a864d0a1526ba199c571388accdc2e630
- native-test_offline_displays_unconfirmed_triggers_and_desired_pause.log: 464cae303b701d32072592fb3b55c915df6b4b0bf56cf2d85167153b43630ced
- native-test_rejected_triggerless_ui_does_not_persist.log: 7f6bf34dff5379fcc505423fc3091d97c83b8c7b412bece43682eacdcd63ec6b
- native-test_successful_reload_preserves_drafts_and_updates_unedited_defaults.log: 1d7f7e64f52d5e79d67d9a3641e328423f18e6818d5eb71345c587ebc74f362a
- native-test_unavailable_and_unknown_saved_ids_remain_visible.log: a6287c0c187ba7e2d367950ec22549ec624d4ae9574b8bf378a19249b8b92a54

Native Frozen-Smokes: Windows-QPA, Exit 0, kein _MEI-Rest, sowohl lokaler als auch OneDrive-TEMP. Die zwei vorgelagerten Desktop-Ergebnisse mit falsch bewertetem Doppelbelegungs-Check bleiben erhalten; der tatsächliche deutsche Status und Profilhash im Wiederholungsergebnis sind korrekt. Finaler Test mit korrigiertem Vergleich: 20/20 PASS_SCOPED.
