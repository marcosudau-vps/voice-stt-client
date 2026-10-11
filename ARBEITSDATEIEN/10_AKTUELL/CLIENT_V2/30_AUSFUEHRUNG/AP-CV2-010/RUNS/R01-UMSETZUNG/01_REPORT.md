# AP-CV2-010 / R01 – Umsetzung

Status **IN_PROGRESS**, Datum 2026-10-11, Europe/Berlin.

[Originalauftrag](00_PROMPT_ORIGINAL.md). Parent `1cf076bd2ed56929b1a3780bc140da51348a8295`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`, Kandidat `work/client-v2/ap-cv2-010`.

Umsetzungsskizze: unabhängige immutable Wiremodelle mit exakten Feldnamen; strikte Pflichtfeldvalidierung, additive Extras erhalten; getrennte Settingsoberflächen; disjunkte Commandbuilder; begrenzter PCM-Encoder im bestehenden Byteformat. Bytegleiche Servervektoren separat von ergänzten vollständigen Fixtures führen. Baseline vor Produktänderung, gezielte Negativ-/Grenztests, gepinnter Serverparser-/Registrycheckpoint und gesamte Windowsregression vor Abgabe.

Vorgängerprüfung: lokale/entfernte feat/client-v2-Spitze identisch, sauberer Start, keine offenen Paket-PRs. AP000-Aggregat genau ein Single-Parent-Commit nach 050e776, Tree gleich finaler PR-#2-Spitze. R04 unabhängige Produktprüfung und R05 tatsächliche Windowsvollsuite sowie Originalfreigabe gelesen.

[Evidenzindex](EVIDENCE/INDEX.md). Ergebnisse werden vor Abgabe ergänzt.
