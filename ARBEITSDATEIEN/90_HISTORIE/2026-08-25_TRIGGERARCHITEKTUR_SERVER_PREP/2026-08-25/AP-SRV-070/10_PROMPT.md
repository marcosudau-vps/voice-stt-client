# SPEKULATIVE VORIMPLEMENTIERUNG – AP-SRV-070

## 1. WICHTIGE STARTSPERRE

Dieses Paket ist vollständig vorbereitet, aber **nicht sofort auf C1 ausführen**.

`AP-SRV-070` ist ein Subtraktions-/Cut-Paket. Es darf erst gestartet werden,
wenn die Koordination einen temporären Prep-Integrationsstand mit den brauchbaren
040/050/060-Änderungen festgelegt hat.

Erwarteter späterer Worktree:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\prep-srv-070
```

Branch:

```text
prep/AP-SRV-070/legacy-cut
```

Die Koordination liefert vor Start einen konkreten:

```text
PREP_STACK_SHA=<sha>
PREP_STACK_TREE=<tree>
```

Ohne diese Werte:
`BLOCKED` und nichts ändern.

## 2. Rolle

Nach Freigabe implementierst du spekulativ
`AP-SRV-070 – Server-Legacyabbau und Protokollgrenze`.

Das Ziel ist **kein großer Refactor**, sondern der kontrollierte Abbau aller
Runtime-Autoritäten, Adapter und Tests, die nach 040/050/060 nicht mehr zum v2-Zielbild gehören.

## 3. Normative Quellen

Clientrepo NUR LESEN:

- `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`
- `PLANUNG/ZIELBILD.md`
- `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md`
- `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`
- `PLANUNG/IMPLEMENTIERUNGSPLAN.md`
- `ANALYSEN/LEGACY_AND_DEAD_CODE_MAP.md` bzw. tatsächlich vorhandene Legacy-/Dead-Code-Analyse
- `NACHVERFOLGUNG/TRACEABILITY.md`
- `NACHVERFOLGUNG/FUNDE.md`

Server:
- `AGENTS.md`
- `docs/.archiv/README.md`
- `docs/einheitliche-triggerarchitektur.md`
- `docs/module-map.md`
- Produktcode des Prep-Stacks.

## 4. Frozen Ziel

Nach SRV-070 bleibt serverseitig nur der neue Runtimepfad aktiv.

Entfernt/abgelöst:
- serverseitige `session.mode`-Runtimeautorität,
- Source-Merge,
- alte Wake-Follow-up-Autorität,
- v1-Triggeradapter,
- alte additive Extension-/`extend`-Kompatibilität,
- Legacy-Activationpfade, die v2 umgehen,
- widersprechende Alt-Solltests.

Inkompatible Clients scheitern **vor Sessionadmission**.

Browserclient ist nicht Teil dieses Arbeitsblocks.

## 5. Preflight

Nach Bereitstellung des Prep-Stack-SHA:

```powershell
git branch --show-current
git rev-parse HEAD
git rev-parse HEAD^{tree}
git status --short
```

Exakt mit der von der Koordination gelieferten Identität vergleichen.
Bei Abweichung `BLOCKED`.

Kein Push, kein Rebase, keine neue venv.

## 6. Zuerst tatsächliche Runtime-Erreichbarkeit prüfen

Bevor etwas gelöscht wird:
- Callgraph/grep/Tests gegen den **Prep-Stack**, nicht gegen alte C1-Notizen;
- jede Löschung einer Kategorie zuordnen:
  - replaced by v2,
  - compatibility only,
  - dead,
  - still required.

Nichts löschen, das noch vom neuen Runtimepfad verwendet wird.

Die alte Legacy-Map ist Hinweis/Evidence, nicht Ersatz für die Prüfung des aktuellen Prep-Stacks.

## 7. Bekannte Kandidaten

Mindestens prüfen:

### Server
- `RealtimeSession` / alter Inline-Lifecycle,
- `VoiceActivityDetector`, falls nur Legacy-Nutzer,
- `ActivationController.finalized()` / alte finalizing-Reste,
- `finalizing` als Runtimephase,
- `activation_config.mode == "legacy"`,
- Legacy-Wake-Follow-up:
  - `_start_wakeword_followup_window`
  - `_finish_wakeword_followup`
  - `_clear_recorder_followup_gate_locked`
  soweit nicht mehr v2-relevant,
- `merged` / `already_active` Legacysemantik,
- v1 `trigger` / `trigger_ack` Transportadapter,
- `extend` Alias,
- alte `extensionSeconds`-Dokumentation/Tests,
- serverseitige `session.mode`-Semantik,
- alte Settingsnamen, die Diktat-/Mode-Autorität statt Activation-Lifecycle ausdrücken.

Nicht mechanisch alles aus dieser Liste löschen.
Erst nachweisen, dass der Prep-Stack Ersatz besitzt.

## 8. Protokollgrenze

Nach SRV-070:
- Desktop-v2 ist der unterstützte neue Runtimepfad;
- v1 öffnet keine teilweise Session;
- Handshake meldet Serverversion, Servercommit und unterstützte Versionen;
- inkompatible Version scheitert über den frozen v2-Handshakepfad;
- kein stiller Fallback auf Legacy.

Keinen Browserclient migrieren.

## 9. Settingsnamen

Serverseitige Settingsnamen, die fachlich noch `mode`, Dictation-Window oder alte
Triggerautoritität ausdrücken, auf das Activation-Lifecycle-Modell migrieren,
soweit SRV-050 bereits entsprechende Registrykeys/Provider besitzt.

Keine neue Settingsarchitektur in SRV-070.

Migration:
- Konfigurationsleser darf ggf. einmalige klar begrenzte Legacy-Key-Migration besitzen,
  wenn Bestandsconfig das erfordert;
- Runtime danach nur kanonische neue Semantik;
- keine dauerhafte doppelte Autorität.

## 10. Tests zuerst als Cut-Guard

Erzeuge/ergänze Negativ-/AST-/Texttests, die sicherstellen:

- kein `session.mode` als Runtimeautorität;
- kein v1 Triggeradapter im aktiven Desktop-Sessionpfad;
- kein `extend`/additives Zeitguthaben im aktiven Pfad;
- kein Source-Merge;
- kein Legacy-Wake-Follow-up als zweite Autorität;
- `finalizing` nicht als Foregroundphase;
- inkompatibler Client erzeugt keine Session;
- v2-Funktion vollständig grün.

Die AST/Textprüfung soll gezielt sein und nicht harmlose historische Dokumentation,
Migrationstabellen oder Kommentare als Produktfehler markieren.

## 11. Löschstrategie

Bevorzugt:

```text
neuer Pfad vollständig vorhanden
→ Tests beweisen Ersatz
→ Legacy Callsite entfernen
→ Legacy Implementierung entfernen
→ Alt-Solltest ersetzen
→ Dokumentation bereinigen
```

Nicht:
```text
erst alles löschen
→ dann schauen, was bricht
```

## 12. Dead Code

Tatsächlich tote Serverklassen/-methoden dürfen entfernt werden, wenn:
- keine Produktcallsite,
- kein bewusst öffentlicher Bibliotheksexport, der außerhalb dieses AP geschützt ist,
- Ersatz/Scope geklärt.

Öffentliche Bibliotheks-APIs nicht allein deshalb entfernen, weil FastAPI sie nicht nutzt.
SRV-070 betrifft Server-Runtime, nicht ungefragt die gesamte Bibliotheks-API.

## 13. Kompatibilitätsdokumentation

Aktualisieren:
- unterstützter Protokollbereich,
- v2-only Desktop-Runtime,
- keine v1 Partial Session,
- Browserclient ausdrücklich außerhalb Scope,
- Serverversion/Commit-Handshake.

`docs/compatibility.md` nur entsprechend der vorhandenen Ownershipregeln;
keine erfundenen bereits abgenommenen Client-/Server-Paare eintragen.
Finale getestete Commitpaarung gehört später INT-010.

## 14. Pflicht-Tests

- v1 first message / old triggerpath → keine teilweise Session;
- v2 hello → normal;
- kompletter v2 Activationcommandpfad;
- Wake v2 path;
- Settings v2 path;
- Snapshot v2;
- Event v2;
- Search/AST guards für entfernte Runtimeautoritäten;
- vollständige Server-Suite.

Zusätzlich prüfen:
- kein stilles Legacyfallback bei ungültigem v2;
- keine Legacy-Sessionobjekte erzeugt;
- kein zweiter Wake-Follow-up-Timer;
- `extend` wird nicht mehr als Runtimecommand angenommen.

## 15. Nicht in diesem Paket

- Client-Legacyabbau,
- Browserclient,
- neue Protokollfeatures,
- neue Settingsdomains,
- Wake-Word-Neudesign,
- neue Hardware.

## 16. Dokumentation

Serverdocs auf tatsächlichen v2-only-Runtimezustand bringen.

Historische AP-Akten nicht rückwirkend umschreiben.

Keine `ABNAHME.md`.

## 17. Validierung

- Negativ-/Compatibility-/Migrationstests,
- v2 Contracttests,
- vollständige Serversuite,
- `git diff --check`,
- gezielte Server-Dead-Code-/AST-Prüfung.

## 18. Commit

Ein lokaler Prep-Commit:

```text
prep(server): implement speculative AP-SRV-070 legacy cut
```

Kein Push.

## 19. Abschlussbericht

```text
STATUS
Branch
PREP_STACK_SHA
Prep-SHA
Prep-Tree
Working Tree clean

Entfernte Runtimepfade
Beibehaltene Compatibility/Migrationspfade + Begründung
Protocol cut
Settings migration
Dead-code evidence
AST/Text guards

Tests / counts
Geänderte Dateien
git diff --check
Push: nein

Rest bis kanonischem SRV-070
```

Dann stoppen.
