# R05 – tatsächliche Nutzeraufträge

Datum: 2026-10-11, Europe/Berlin. Ergänzender Windows-Prüflauf und ausdrücklich beauftragte Anpassung der Testverantwortung; keine eigene Produktimplementierung.

## Regelanpassung

> Was zum Teufel ist denn los? Ich möchte die Reviews von einer ChatGPT Session durchführen lassen, beziehungsweise habe ich die letzten auch schon. Dort kann nur die Windows Full Suite nicht durchgeführt werden. Können wir das so machen, dass diese in den Umsetzungslauf nachgewiesen werden muss, sodass diese nicht nochmal durch den Reviewer geprüft werden muss. Das würde einiges vereinfachen.

## Windows-Nachweis und bedingte Übernahmefreigabe

> Der Reviewer hat alles auf Pass gesetzt, außer eben besagte Tests. Kannst du die für den aktuellen Pull Request selber durchführen? Dann kannst du diesen eigentlich, die Änderungen für den nächsten Lauf pushen und dann eigentlich auch annehmen.

Aufgelöster Scope: Client-PR #2, Paket AP-CV2-000, Base `feat/client-v2` am Parent `050e776cf316eb332177294db0c0a2719c2b4415`, Head bei Auftrag/Prüfstart `7c4bb2f7d3f3a79d0b2f0beae5bdbae27795d0fe`. R04 prüfte den codegleichen Stand `cd872d4bfa8eccd0167337cbab16a572ca70bfd4` und schloss F01. Windows-Prüfung, Regelpflege und Belegpush im selben Paket-PR sind beauftragt; Einzel-Squash-Übernahme erst nach tatsächlichem positivem Test-/Abnahmeabschluss und grüner finaler CI. Die Testverantwortung wird für kommende Runs angepasst; R04 wird nicht rückwirkend umgeschrieben. Andere Repositories, Main, Tags und Releases sind nicht Gegenstand dieses Auftrags.
