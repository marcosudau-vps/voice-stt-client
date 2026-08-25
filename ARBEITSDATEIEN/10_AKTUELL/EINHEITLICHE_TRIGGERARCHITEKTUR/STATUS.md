# Status – Einheitliche Triggerarchitektur

<!-- ARBEITSBLOCK-META
schema: 1
name: EINHEITLICHE_TRIGGERARCHITEKTUR
title: Einheitliche Triggerarchitektur
state: AKTIV
phase: PLANUNG
created_at: 2026-08-24 01:08:47 +02:00
updated_at: 2026-08-25 02:51:08 +02:00
branch: feat/einheitliche-triggerarchitektur
baseline_head: dd0af5ed22e7401895f08c8c13e4e37c7e78ddb7
-->

**Status:** AKTIV

**Phase:** PLANUNG ABGESCHLOSSEN / READY FOR IMPLEMENTATION

**Branch:** `feat/einheitliche-triggerarchitektur`

## Aktueller Stand

Der Planungsbereich wurde auf zwei klare Einstiege reduziert:

- `PLANUNG/` für Zielbild, technischen Contract, finalen Implementierungsplan,
  Entscheidungen und Analysen;
- `NACHVERFOLGUNG/` für Status, Funde und Traceability.

Die fachlichen Entscheidungen sind in `PLANUNG/ZIELBILD.md` konsolidiert.
`PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md` schreibt Phasen, Hintergrundledger,
Timer, IDs, Wire, Snapshot, Settings und Recovery fest.
`PLANUNG/IMPLEMENTIERUNGSPLAN.md` ist der verbindliche, testbare Plan.

Zusätzlich bestätigt sind jetzt das heutige Mehrsegment-Verhalten innerhalb
einer Activation, nicht kumulatives `refresh`, ein dritter optional belegbarer
Wake-Pause-Hotkey, die fachliche Finish-/Cancel-Semantik samt verpflichtendem
Lifecycle-Ereignis sowie das Laden nur der je Session ausgewählten
Wake-Word-Modelle. `refresh` setzt in `followup_wait` den Inaktivitätstimer und
in `segment_active` ausschließlich den Daueraufnahme-Sicherheitswatchdog neu.

Die Finish-/Cancel-Phasenmatrix und Retry-Semantik sind nun ebenfalls
fachlich eingefroren. Cancel verwirft nur noch nicht veröffentlichte
Resultate; bereits ausgegebener oder eingefügter Text bleibt bestehen. Eine
ungültige Wake-Word-Sessionauswahl wird vollständig statt teilweise oder per
Fallback abgelehnt.

Server-/Geräteverlust, triggerlose Laufzeit, Pre-Roll-Ziel und
Daueraufnahme-Schutz sind fachlich weiter präzisiert. Außerdem ist die
Settings-Control-Plane als Bestandteil dieses Umbaus vorgesehen: gemeinsamer
Serververtrag, Trigger-/Wake-Word-/Timing-Einstellungen und eine
admin-geschützte Servereinstellungsseite; fachfremde Vollmigration später.

Die zweite Härtungsrunde ist abgeschlossen: Der Daueraufnahme-Watchdog
verarbeitet das bereits erfasste Audio regulär. Manual und Wake Word sind
getrennt laufzeitweit suppressierbar; eine zusätzliche Pause-all-Funktion gibt
es nicht. Physische Hotkeys, Geräte- und sämtliche Feedbackkonfiguration
bleiben Clientverantwortung; der Server verarbeitet nur semantische Commands,
einen generischen Audioverfügbarkeitsstatus und erzeugt fachliche Ereignisse.
Eine Activation behält unveränderlich ihre Starteinstellungen. Der Admin-Key
liegt bei dauerhafter Speicherung im Windows Credential Manager und kann in
der UI wieder gelöscht werden. Desktop-Client und Server erhalten einen klaren
Protokoll-Cut samt Versions-/Commit-Kompatibilitätsmatrix.

Neu bestätigt ist die Freigabe des Trigger-Locks nach sicherem Ende des
Follow-up-/Eingabefensters. Final-Transkriptionen älterer Activations dürfen im
Hintergrund weiterlaufen und werden über unveränderliche IDs sowie eine
Segmentreihenfolge nachgereicht. `finalizing` blockiert den Vordergrund nicht.
Der Segment-Watchdog startet mit zehn Minuten; ein Refresh sichert drei
Minuten ab Interaktion, ohne eine längere Restzeit zu verkürzen oder Zeit zu
kumulieren.

Die Arbeitspakete sind strikt getrennt: `AP-SRV-*` besitzt nur Servercode,
`AP-CLI-*` nur Clientcode. `AP-INT-*` validiert koordinierte Commits, ändert
aber keinen Produktcode.

Der Ausführungsrahmen ist vorbereitet. Ein GPT-5.6-Sol-Agent und ein
separater Claude-Code-CLI-Lauf dürfen nur bei erfüllten Dependencies und
getrenntem Ownership parallel implementieren. Nach den parallelen Baselines
ist bis AP-SRV-040 zunächst eine serielle Servervorleistung nötig; danach
öffnen sich drei definierte Server-/Client-Parallelfenster. Opus ist
kapazitätsbewusst primär für AP-CLI-010 und den unabhängigen INT-010-Audit
reserviert, Sonnet für die übrige Clientreihe.

Das v2-Wire-Schema ist auf konkrete Pflichtfelder, Acks, Result-Codes,
Close-Codes und maschinenlesbare Vertragsvektoren gehärtet. Der Desktop-Client
darf keinen Wake-Word-Trigger behaupten: Er sendet `activate` nur mit
`source=manual`; Wake-Word-Admission entsteht serverintern und wird danach in
Events und Snapshot sichtbar.

Produktdokumentation wird in jedem AP durch den Implementierungsagenten im
eigenen Repository mitgezogen. Die Endabnahme schützt normative Planung,
Gate-Status, Traceability und freigegebene Commitpaare vor parallelen
Schreibkonflikten.

Der Traceability-Vollständigkeitsaudit hat die zuvor stark gebündelte Matrix
auf 129 eindeutige Summary- und Einzelanforderungen erweitert. Phasen,
Pipeline, Ledger, Reihenfolge, Timer, Commands, Suppression, Wire, Wake Words,
Settings, Geräte-/Feedbackgrenzen, Recovery, Kompatibilität sowie
Ausführungsgovernance sind jetzt jeweils separat abnehmbar. Vier erkannte
Wire-Unklarheiten wurden geschlossen: Wake-Auswahl bei deaktivierter Quelle,
Activation-ID/Sequence für manuelle und serverinterne Admission,
`causedByCommandId` und Snapshot-Sortierung. Hotkey-Kollisionen sowie konkrete
Cooldown-/Pre-Roll-Kalibrierwerte bleiben sichtbar offen und blockieren die
Baselinepakete nicht.

Der Server-Worktree befindet sich bereits auf
`feat/einheitliche-triggerarchitektur`; alle vorhandenen lokalen Änderungen
liegen dort unverändert als geerbter Baseline-Diff. Die GitHub-Remote wurde
ergänzt. AP-SRV-000 übernimmt und inventarisiert diesen Stand kontrolliert,
bevor der erste Server-Push erfolgt.

Für jedes AP gilt nun: repositorylokaler Ordner mit Originalprompt,
Agentenbericht, Endabnahme und Evidence; Agent erstellt genau einen lokalen
Commit, Befunde werden vor Push per Amend korrigiert, und die Koordination
pusht erst nach PASS auf den jeweiligen GitHub-Feature-Branch.

## Aktive Arbeit

Noch kein Implementierungs-Arbeitspaket. `AP-TRG-000_GATE_0` enthält
vorbereitende historische Gate-0-Prompts, steuert aber die aktuelle
Dialogrunde nicht.

## Bekannte neue Abweichungen

- Der neue serverseitige `ActivationController` kumuliert aktuell
  Extension-Zeit. Gewünscht ist ein nicht kumulatives Zurücksetzen des
  Inaktivitätstimers (`FIND-010`).
- Mehrere Wake-Word-Detection-Signale pro gesprochener Äußerung sind gemeldet.
  Einzel-Score-Adapterpfad und fehlender Detection-Guard nach dem ersten
  Treffer bestätigen einen technischen Mehrfachsignalpfad. Ein fachlicher
  Latch bis zum Unlock ist festgelegt; nur eine möglicherweise zusätzliche
  Fehlalarm-Bestätigungsregel wird noch mit Audio- und Score-Traces bestimmt
  (`FIND-011`).

## Verbleibende Kalibrierung

Keine breite fachliche Entscheidung blockiert den Start. Wake-Word-
Bestätigungsregel und Audiofreigabegrenze werden in AP-SRV-060 anhand realer
Score-/Audiodaten innerhalb des eingefrorenen Contracts kalibriert.

## Nächster Schritt

Den vollständig auditierten Planungsstand committen und auf den
Client-Feature-Branch pushen. Danach die repositorylokalen Akten und
Originalprompts für AP-SRV-000 und AP-CLI-000 mit aktuellen SHAs erzeugen und
Welle 1 starten.

## Abgrenzung

Dieser Dokumentationslauf verändert keinen Produktcode, führt kein
Implementierungs-Arbeitspaket aus und erstellt ohne ausdrückliche Freigabe
keinen Commit.
