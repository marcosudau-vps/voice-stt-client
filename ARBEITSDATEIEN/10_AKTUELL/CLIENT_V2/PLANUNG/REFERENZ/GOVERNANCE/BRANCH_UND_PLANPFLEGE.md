# Branchführung und gemeinsame Planpflege

Stand 2026-10-11, Revision 9. Diese vom Auftraggeber festgelegte Struktur gilt für die neue Cliententwicklung und ersetzt die frühere Client-Zielbranchzuordnung in historischen Analysen. Fachlicher Serververtrag und Paketumfang bleiben bestehen.

## Einstieg und Herkunft

Der gemeinsame Planungs- und Umsetzungsbranch heißt `feat/client-v2` im Repository `marcosudau-vps/voice-stt-client`. Er beginnt bei `8bab1b3f4aa070d0756c305908def4d9ebc52582`, dem bisherigen kanonischen Featurestand. Dessen vollständiger Baum `471197bc6473b8fb10e908c3313093edd96b2253` stimmt mit Distributed `a80a6b17b40751740f9c9d2aef9cad32b0470c0c` überein. Die Wahl bewahrt die vorhandene Implementierung und den bisherigen kanonischen Aggregateverlauf; die alte Distributedhistorie bleibt als Provenienz erhalten. Es findet kein Merge der Kandidatenhistorie statt.

`main`/V1 `f625904795880ce71acec216e43678f9ec1656d0` bleibt Quelle gezielt zu integrierender Releaseverbesserungen. Der erste neue Commit ändert ausschließlich Planung, Rollenregeln und Dokumenteinstiege. Er ist kein abgeschlossener AP-CV2-000 und kein qualifizierter integrierter Produktstand. `integratedClientCommit` bleibt bis zur geprüften CV2-000-Übernahme offen.

```text
feat/einheitliche-triggerarchitektur @ 8bab1b3
└── feat/client-v2                       # neue gemeinsame Abschlusslinie
    ├── START: vollständige Planung      # erster neuer Commit, keine Codeänderung
    ├── AP-CV2-000: Code + Unterlagen     # genau ein freigegebener Paketcommit
    ├── AP-CV2-010: Code + Unterlagen     # genau ein freigegebener Paketcommit
    └── weitere APs in geplanter Folge

Je Paket ab dem zuletzt übernommenen Stand:
feat/client-v2 @ aktueller Paketparent
└── work/client-v2/ap-cv2-000             # Beispiel; kumulative C1/C2/Korrekturen
    └── review/ci/prep-Unterbranches     # nur wenn tatsächlich benötigt
```

Ein Gitbranch ist technisch ein Ref, keine Ordnerhierarchie. „Untergeordnet“ bedeutet hier: Paketbranch vom festgehaltenen letzten Abschlusscommit abzweigen und nur dessen geprüftes Gesamtergebnis aggregieren. Der nächste Paketbranch entsteht frisch vom nächsten übernommenen Paketstand; alte Kandidaten werden nicht hineingemergt. Ein dauerhaft quer zur Abschlusslinie wachsender Client-Distributedbranch ist nicht nötig. Die **Distributedrolle** übernehmen die jeweiligen Paketbranches. Bestehende alte Branches bleiben unverändert.

## Ein Commit je Paket durch Isolation und Aggregation

1. Paket-ID, aktuellen feat/client-v2-Parent, Server-SHA und Gitrechte festhalten; Vorgängerprüfung gemäß [Startreferenz](../../SKILLS/GEMEINSAM/references/START_UND_GRENZEN.md). Umsetzung/Planpflege ausschließlich auf Paketbranch.
2. Code, betroffene Planung, Matrix/Requirements und Runbelege gemeinsam entwickeln. Bei erlaubtem Remoteauftrag ein kumulativer Paket-PR mit Base feat/client-v2.
3. Frischer unabhängiger Review auf exakt eingereichtem SHA. Umsetzer pausiert. Reviewer prüft vollständigen Diff samt Tests/Unterlagen und committet/pusht im erlaubten Scope nur seine Reviewakte/administrativen Verweise auf den Paketbranch. Umsetzer übernimmt diese Spitze vor beauftragter Korrektur; gleicher PR, neue unabhängige Reviewakte.
4. Nach technischem ROOT_PASS auf ausdrücklichen menschlichen Übernahmeprompt warten. reviewed_sha/tree ist der geprüfte Kandidat, spätere Reviewunterlagen erzeugen einen zusätzlichen Head; ausschließlich erlaubte administrative Differenzen vor Merge prüfen.
5. Nach Freigabe finale Head/Base und erforderliche CI prüfen; genau diesen PR per **Squash and merge** übernehmen. Kein normaler Historymerge, Rebase-Merge oder Kandidaten-Cherry-pick-Verlauf auf feat/client-v2. Bei GitHub-Squash vorab PR-Head bzw. CI-Testmerge mit exakter Base prüfen; seine erst beim Merge erzeugte Aggregate-SHA existiert vorher nicht.
6. Unmittelbar danach genau einen neuen Single-Parent-Commit auf canonical_parent und Ergebnisbaum gleich finalem PR-Head nachweisen. Git-/CI-/Transportfehler nicht ACCEPTED nennen. Ein geänderter Zielparent verlangt neue Bewertung/Prüfung und passende Freigabe, keinen erzwungenen Merge.
7. Lokale Einzelaggregation bleibt bei ausdrücklich gewähltem Auftrag möglich: genau ein Single-Parent-Aggregat auf exaktem Parent, Baumprüfung, CI dieses vorhandenen SHA und Ziel nur fast-forward/push im erlaubten Scope. Nicht zusätzlich denselben PR squash-mergen.

Verbindliche Details zu Schreibhoheit, Review-Push, PASS-SHA, finalem PR-Head, Freigabebeleg und CI: [PR und Reviewübergabe](../../SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md).

Damit enthält die neue Abschlusslinie einen Startcommit plus genau einen Commit je angenommenem AP. Ein reines Qualifikationspaket liefert seinen einen Commit mit Plan-/Abnahmebelegen, ohne erfundene Codeänderung. Auch nachträgliche Dokumentkorrekturen werden auf einem Arbeitsbranch vorbereitet und in den nächsten sachlich zuständigen Paketcommit aufgenommen; eine dringliche eigenständige Änderung außerhalb dieser Kette verlangt einen ausdrücklichen Auftrag und sichtbar benannten Ausnahmeumfang.

Die Selbstreferenz eines Commits wird vermieden: Ein Paketcommit kann seinen eigenen endgültigen SHA nicht bereits enthalten. Paket-ID, Parent, reviewed_sha/tree und Freigabe stehen in seinen Unterlagen; der Aggregate-SHA ist über den eindeutigen AP-Commit im Gitverlauf ermittelbar. Vor Merge bleiben Unterlagen beim technischen ROOT_PASS; erfolgreicher gemergter PR und überprüfter Aggregatecommit belegen ACCEPTED. Der Abschlussreport nennt danach den tatsächlichen SHA und wird mit dem nächsten Paket gesichert. Kein zusätzlicher „Abschluss-SHA-Aufräumcommit“ für dasselbe AP.

## Eine gepflegte Ablage

Die maßgebliche Planung liegt **in jedem Checkout dieses Branches** unter `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/`. Von [README](../../README.md) und den Rollen-Skills aus sind alle benötigten Referenzen erreichbar. Keine absolute Worktreeadresse als allgemeine Laufvoraussetzung; bei jedem Auftrag Repository, Checkout, Branch und HEAD verifizieren.

Paketakten werden daneben unter `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/<AP-ID>/` geführt, nach [Aktenstruktur](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md). Kleine redigierte Textbelege/Original-Prompts mitführen; große Artefakte und vertrauliche Daten nur über sichere Identitäts-/Hashnachweise referenzieren. Steuerungsstatus und Log liegen unter `ARBEITSDATEIEN/00_STEUERUNG/` desselben Clientcheckouts.

Die zuvor außerhalb von Git abgelegten Unterlagen bleiben als unveränderte historische Planungsfassung erhalten. Sie werden nicht parallel fortgeschrieben und sind keine Pflichtquelle der neuen Agentenläufe. Das Importmanifest belegt ihre Herkunft; die neue Planung ist eigenständig vollständig. Erforderliche Servernachweise bleiben ihrem Serverrepository zugeordnet; Clientplan und Commitpaar referenzieren sie.

## Server bleibt bis zum gemeinsamen Abschluss auf Distributed

Serverreferenz ist `feat/einheitliche-triggerarchitektur-distributed` bei `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Der ältere kanonische Serverfeaturestand `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8` enthält das noch offene finale Delta nicht. Dieses wird bewusst erst nach Cliententwicklung und gemeinsamer Qualifikation als **ein sauberer finaler Aggregatecommit** auf den Serverfeaturebranch übernommen, nach eigener ausdrücklicher Freigabe. Ein Mainmerge bleibt eine weitere separate Entscheidung.

Nötige AP-SV2-FIX-nnn-Korrekturen entstehen isoliert auf Serverarbeitsbranches und werden nach Prüfung und passender Freigabe kumulativ auf Server-Distributed geführt. Sie erzwingen keine sofortige Einzelpromotion auf den kanonischen Serverfeaturebranch. Im Client werden neue Server-SHAs und betroffene Kontrakte/Vektoren/Requirements gemeinsam mit dem zugehörigen Clientpaket übernommen und das neue Paar geprüft. Servercode gehört in das Serverrepository; dieses Startcommit ändert dort nichts.

## Konsolidierter Unterlagenstart Revision 9

Vor dem ersten Remote-Push werden alle aktuellen Rollen-/Zustandsunterlagen im noch unveröffentlichten ersten Unterlagencommit zusammengeführt. Das ersetzt dessen vorläufige lokale Fassung; die alten Client-Feature-/Distributed-Refs und ihre Historien bleiben unverändert. Es entsteht genau ein Startcommit nach 8bab1b3 und kein vorgezogener CV2-000-Commit. Frühere Prüfergebnisse mit damaligen Vorbereitungsbranch-/Importhinweisen sind in EVIDENCE ausdrücklich historisch gekennzeichnet.

Die SHA des Startcommits lässt sich aus dem Gitverlauf ermitteln: `git rev-list --reverse 8bab1b3f4aa070d0756c305908def4d9ebc52582..feat/client-v2`; erster Eintrag. Im initialen Workflowstatus steht wegen der Selbstreferenz nur canonicalParentRef. Beim ersten Paketstart wird der tatsächliche aktuelle kanonische HEAD auf dem Paketbranch als voller canonicalParent festgehalten. Spätere Pakete starten immer von der zuletzt übernommenen Feature-Spitze.
