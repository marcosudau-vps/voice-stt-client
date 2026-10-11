# R03 – Evidenzindex

Status REVIEW_READY. Qualifiziert `98ab3c0fc5c935019d81d6d6acb1423185cb4793`, Tree `c394dbe3d75086132234cb987469ee6639647af6`; Parent
`91065f5f7715aa6653ec5335d9e757b6ef97a067`, Server ada13b0 unverändert.

- [Startprovenienz](start-provenance.json): übernommene Reviewdocs-Spitze71f757b,
  geprüfter R02-Kandidat, initial sauberer Workingtree, betroffene Dateihashes.
- [Vorher-Baseline57](baseline-targeted.txt), [Befehl/Runtime/Exit/Hash](baseline-validation.json).
- [Finding-Repro vor Fix](findings-before-fix.txt), [vollständige originale Ausgabe/Befehl/Hash](findings-before-fix.json):
  EXPECTED_FAIL (7 Failures/9 Errors). TXT entfernt zwei nachgestellte Leerzeichen;
  Originalausgabe vollständig im JSON, separater Raw-SHA256.
- [Qualifikationsmanifest](windows-validation.json): Runtime, exakte Befehle,
  Kandidat/Tree, Zeiten, Exitcodes und SHA256 der vollständigen Pflichtlogs.
- [Codec-/Transport61](targeted-transport-codec-unittest.txt): -W error/-v, PASS.
- [Servercheckpoint21](server-transport-checkpoint.json): echte gepinnte Serverapp
  via TCP/WS,46 Pythonquellen byteverifiziert; Modell-/Hardwaregrenzen offengelegt.
- [compileall](compileall.txt): leerer Log, Exit0 im Manifest.
- [Windowsvollsuite1294](windows-full-unittest.txt): vollständiger Log, Exit0.
- [Administrative Abgabeprüfung](administrative-validation.json): strukturierte
  Status-/Link-/Requirement-/Loghash-/Diffkontrolle und rein administrative Nachträge.

Erzeugende Befehle stehen jeweils in den verlinkten JSONs; finale Logs UTF-8 LF,
keine Verkürzung. Finaler SHA/Tree und Remote-CI im PR-Übergabekommentar.
Kein eigener unabhängiger PASS, keine reale Hardware-/ASR-/Gesamtproduktabnahme.
