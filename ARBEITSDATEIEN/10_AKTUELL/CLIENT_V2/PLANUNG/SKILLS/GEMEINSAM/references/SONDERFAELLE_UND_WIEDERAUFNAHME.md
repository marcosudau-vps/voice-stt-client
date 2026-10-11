# Wiederaufnahme, Auswahl, Serverfix und Abschluss

Stand 2026-10-11, Revision 10. Diese Referenz nur beim betreffenden Sonderfall lesen. [Zustandsregeln](ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) steuern weiterhin den normalen Paketablauf. Keine zusätzlichen Pflichtpakete, Rollen oder Reviews.

## 1. Unterbrochene Session übernehmen

Ein erreichbarer aktiver `writeOwner` hat Vorrang vor einem neuen Rollenstart, auch während eines Reviews. Alter, fehlende neue Commits oder ein nicht erreichbarer Rechner beweisen keinen Abbruch. Bei fehlendem Zugriff zuerst den konkret fehlenden Arbeitsstand/Owner nennen. Keine fremde Session stoppen und keine lokale WIP überschreiben.

Eine Wiederaufnahme ist zulässig, wenn eine dokumentierte Schreibübergabe vorliegt oder der Mensch ausdrücklich die Übernahme der unterbrochenen Linie beauftragt. Ein passender Prompt lautet beispielsweise: „Die bisherige Session ist beendet. Übernimm die unterbrochene ausgewählte Paketlinie und führe den nächsten Schritt fort.“ Dieser Prompt erlaubt keine neuen Gitrechte außerhalb einer vorhandenen Arbeitsfreigabe und keine kanonische Übernahme. Ist der Owner unbekannt oder sein Ende nicht belegbar, die notwendige menschliche Übergabe anfordern; „Mach den nächsten Schritt“ allein verdrängt ihn nicht.

Der neue Agent:

1. Prüft Paketbranch/PR, zuletzt bereitgestellten Commit/Tree, Akten, offene Findings sowie erreichbare uncommittierte und ignorierte Arbeit. Nicht erreichbare Arbeit als Lücke dokumentieren; der Mensch muss gegebenenfalls ausdrücklich die Fortsetzung ausschließlich vom bereitgestellten Stand wählen.
2. Sichert die verfügbare WIP und den früheren Aktenstand, bevor er Änderungen übernimmt. Geschlossene Berichte bleiben unverändert. Kein Reset, Force-Push oder stiller Rebase; bei Divergenz den Konflikt klären. Die gewählte Kandidatenlinie bleibt erhalten, sofern kein eigener Kandidatenwechsel beauftragt ist.
3. Legt in der vorhandenen Paketakte einen neuen tatsächlichen Umsetzungs-, Korrektur- oder Abnahmerun an. Originalübergabe, früheren Owner/Run, Ausgangs-SHA bzw. gesicherten Diff und neuen Owner im Report festhalten. `recovery` verweist auf diese Akte und den Übergabeauftrag; erst dann `writeOwner` wechseln. Eine Fortsetzung derselben noch offenen Session braucht keinen neuen Run.
4. Prüft die letzte Abgabe gegen den Iststand. Unvollständige oder nachträglich fachlich geänderte Arbeit behält keinen alten PASS. Begonnene Reviews werden in frischer unabhängiger Session für den ganzen Kandidaten neu geprüft; eigene vorausgegangene Umsetzung schließt die Reviewerrolle aus.

Danach gilt wieder der normale Rollenablauf. Es ist kein eigenständiger Recovery-Abnahmezyklus vorgeschrieben.

## 2. Genau eine ausgewählte Kandidatenlinie

Beim ersten Paketstart ohne offene Konkurrenz wird der vom tatsächlichen Auftrag gebildete Branch ausgewählt: `selectedCandidate=true`; `candidateSelection` hält eine paketweit eindeutige `candidateId`, den tatsächlichen Auftrag/Entscheidungsbeleg als `source`, `reason` und gegebenenfalls den Vorgängerbranch fest. Bei Wiederaufnahme, Review und Korrektur bleibt diese Auswahl unverändert. Ein boolesches Feld allein ist kein Auswahlbeleg.

Der normale Name `work/client-v2/ap-cv2-030` bleibt erlaubt. Weitere Versuche heißen beispielsweise `work/client-v2/ap-cv2-030-attempt-02`, `...-attempt-03`. Suffixe vermeiden auch Git-Ref-Kollisionen mit dem bestehenden Namen. Kandidaten derselben AP-ID haben eigene Branch-/PR- und Runidentitäten; keine Reports gegenseitig überschreiben.

Ein neuer Alternativversuch ersetzt den bisherigen Kandidaten nicht automatisch. Er startet mit `selectedCandidate=false`. Ein ausdrücklicher menschlicher Auswahlauftrag oder dessen eindeutig belegte Auswahl im ursprünglichen Auftrag bestimmt, welcher Versuch weitergeführt wird. Ohne eindeutige Auswahl bei konkurrierenden aktiven Linien ist `BLOCKED` korrekt.

Beim Wechsel den alten Schreiber zuerst geordnet stoppen/übergeben. Die Entscheidung nennt AP, alte/neue Branches und vorhandene SHAs, tatsächlichen kanonischen Parent sowie Originalauftrag. Die neue Akte verlinkt die gesicherte alte Linie und deren Findings. Im erlaubten Git-Scope die alte Linie `SUPERSEDED`/false und die neue true mit gegenseitiger Entscheidungsreferenz bereitstellen. Ein alter PR darf dafür im ausdrücklich erlaubten Scope als ersetzt markiert/geschlossen werden; keine Daten/Branches löschen. Wenn nur eine Seite aktualisierbar ist, ist ein erreichbarer expliziter Entscheidungsbeleg auf der neuen Linie maßgeblich; fehlende alte Pflege sichtbar melden. Ohne diesen Beleg zwei widersprüchliche true-Felder nicht nach Zeitstempel auflösen.

| Situation | Dokumentierter Stand | Nächste Aktion |
| --- | --- | --- |
| Erster Versuch A | A=true mit Originalstartauftrag; kein anderer aktiver Versuch | A bearbeiten |
| Zusätzlich B beauftragt, kein Ablöseauftrag | A=true, B=false; B als Alternativversuch gekennzeichnet | Ausdrücklichen B-Auftrag auf B ausführen; generischer Folgeauftrag bleibt bei A |
| Mensch wählt B statt A | Ablösebeleg verlinkt beide; A=SUPERSEDED/false, B=true | B bearbeiten bzw. prüfen, tatsächliche Phase beachten |
| A und B true, kein eindeutiger Ablösebeleg | Auswahl widersprüchlich | Auswahl klären, keinen frei gewählten Merge |

Ein neuer Kandidat erbt keinen PASS und keine Übernahmefreigabe der alten Linie. Relevante offene Findings werden übernommen oder mit konkretem Nichtbetroffenheitsnachweis geschlossen. Ein gegenüber `feat/client-v2` überholter Parent braucht Neubewertung und passende Freigabe; die Auswahlentscheidung ersetzt diesen Check nicht.

## 3. Blockierender Serverdefekt und Rückkehr zum Client

Ein reproduzierbarer Serverdefekt erzeugt auf dem ausgewählten Clientbranch `packageStatus=BLOCKED`, `workflowPhase=SERVER_FIX_REQUIRED`. Die Clientakte enthält Repro, Finding-ID, betroffene Requirements, bisherige Server-SHA und den gehaltenen Clientkandidaten/Parent. `relatedServerFix` verweist auf ID, Repository, Branch und tatsächlich erreichbaren Akten-/Statuspfad der FIX-Instanz sowie die Rückkehridentität des Clientpakets. Vor Instanziierung bleiben unbekannte Werte ausdrücklich offen. Dieser Zustand darf kein Client-PASS erzeugen.

Serverarbeit verlangt einen tatsächlichen Serverauftrag oder eine gesicherte Arbeitsfreigabe, die genau diesen Repository-/Fixscope umfasst. Die erste Client-Kandidatenfreigabe umfasst dies nicht. Ohne passenden Auftrag/Rechte meldet der gemeinsame Einstieg die benötigte Freigabe; er beginnt keine eigenmächtige Serveränderung. Ein ausdrücklich beauftragter Fix erhält `AP-SV2-FIX-nnn` nach [Serverfix-Spezifikation](../../../ARBEITSPAKETE/AP-SV2-FIX.md).

Die FIX-Instanz führt ihre maßgeblichen Originalprompts, Runs, Reviews und einen eigenen Workflowstatus im Serverrepository. Eine mögliche Ablage ist `docs/client-v2-fixes/<FIX-ID>/`; den im konkreten Serverauftrag und nach Server-AGENTS tatsächlich gewählten Pfad im Client verlinken, keine vorhandene Ablage voraussetzen. Nur der Repro und die Rückkehrverweise gehören in die Clientakte, keine zweite Kopie des Server-Findingregisters.

Der gemeinsame Einstieg folgt der verlinkten FIX-Linie und prüft zuerst den tatsächlichen Serverstand sowie dortige offene Branches/gegebenenfalls PRs. Serverkandidat beispielsweise `work/server-v2/ap-sv2-fix-001`, Ausgangspunkt ist der festgehaltene Server-Distributed-SHA; Ziel bleibt `feat/einheitliche-triggerarchitektur-distributed`. PR, falls beauftragt, hat diese Server-Base. Client-PR-/feat/client-v2-Prüfregeln gelten hier nicht. Der gewählte Rollen-Skill wird mit **Repository=Server, Paket=FIX, Ziel=Server-Distributed** ausgeführt:

- READY_FOR_IMPLEMENTATION oder CHANGES_REQUIRED: beauftragte Serverumsetzung bzw. Korrektur; vollständige schnelle Serversuite, Repro und tatsächlich betroffene Clientintegration.
- REVIEW_READY: frischer unabhängiger Review des gesamten Server-Fixkandidaten; Reviewakte im erlaubten Scope auf dessen pausiertem Serverarbeitsbranch. Repro im Client an der benannten Client-SHA/Tree prüfen; keine beiläufigen Clientänderungen während des Serverreviews.
- ROOT_PASS/WAITING_FOR_APPROVAL: auf menschliche Sicherungsfreigabe für Server-Distributed warten. Dies ist keine Freigabe der endgültigen Serverfeature-/Mainpromotion.
- READY_FOR_DISTRIBUTED_PROMOTION: nach passendem menschlichem Prompt unveränderten Serverparent, finalen Kandidaten, administrative Nachträge und erforderliche Checks prüfen; freigegebenen Fix kumulativ auf Server-Distributed sichern. Transport nur im konkret freigegebenen Verfahren, ohne Force-Push oder erzwungene Übernahme bei geänderter Base. Der finale Serverfeature-Aggregatcommit bleibt aufgeschoben.
- FIX_ACCEPTED: tatsächliche neue Distributed-SHA, Freigabe, Review und erfolgreichen Transport nachweisen. Erst danach ist der nächste generische Schritt die **Rückkehr zum gehaltenen Clientpaket**, kein neues serielles Client-AP.

Im Rückkehrlauf Client-Parent/Branch erneut prüfen; `relatedServerFix` als erledigten Herkunftsverweis erhalten. Neue Server-SHA und betroffene Kontrakte, Vektoren, Quellenbindungen/Matrix und Übergaben gemeinsam pflegen. Falls die Änderung keinen Vertrag ändert, dies konkret belegen, keine unnötigen Neufassungen erzeugen. Repro, betroffene Clienttests, volle vorgeschriebene Regression und bereits erreichte Servercheckpoints am neuen Paar wiederholen; spätere noch nicht umgesetzte Pakete nicht vorziehen. Frühere PASS-Belege qualifizieren dieses geänderte Paar nicht. Korrektur bzw. unterbrochene Umsetzung fortsetzen, danach REVIEW_READY und neuer unabhängiger Clientreview. Nur bei nachweislich unverändertem Client-/Vertragsscope ist eine engere Wiederprüfung begründbar; Paket-/Paarfreigabe niemals still übertragen.

Sind mehrere Serverfixes tatsächlich blockierend, alle in der Clientakte verlinken; `relatedServerFix` bezeichnet die eine aktuell ausgewählte FIX-Linie. Nach deren Abschluss den nächsten belegten Blocker auswählen. Keine vorab erzeugte Fixserie.

## 4. Nachträgliche Korrektur eines angenommenen Pakets

Passt eine kleine notwendige Anschlusskorrektur sachlich in das derzeit offene Paket, führt dessen Gesamtprüfung sie mit und dokumentiert die betroffenen früheren Requirements/Nachweise. Frühere PASS-Berichte und angenommene Commits bleiben erhalten; ein betroffener alter Beleg ist für das neue Paar gegebenenfalls nicht mehr ausreichend.

Ist kein geeignetes Folgepaket offen, kann der Mensch eine konkrete Zusatzkorrektur `AP-CV2-FIX-nnn` ausdrücklich beauftragen. Repro, alte Paket-/Requirement-IDs, begrenzter Scope, aktueller `feat/client-v2`-Parent, Tests und DoD stehen in ihrer Paketakte; sie nutzt dieselben Rollen-/Runvorlagen. Neue Instanz im Manifest/Index eintragen: `correctsPackage` benennt das alte Paket, `affectedRequirements` dessen betroffene bestehende IDs. Das Feld `requirements` führt weiterhin ausschließlich eigene neue Requirements; bestehende IDs nicht duplizieren oder ihre ursprüngliche Ownership still ändern. Neue Korrektur-/Nachweisverweise in deren Matrixzeilen ergänzen. Ein Umsetzungs- und unabhängiger Reviewablauf, anschließend menschlicher Übernahmeprompt, genau ein neuer Korrekturaggregatcommit mit Code und Unterlagen. Kein Amend/Squash bereits angenommener Geschichte und keine künstliche Wiederöffnung des alten AP-Commits.

Für reine Dokumentkorrekturen ohne passenden offenen Paketbezug ist eine ausdrücklich freigegebene dokumentarische Ausnahme möglich; Anlass und Commitumfang sichtbar benennen. Der aktuelle Revisions-10-Auftrag bereitet Unterlagenkorrekturen vor und erteilt keine eigenständige kanonische Commit-/Pushfreigabe. Erst ein entsprechender Folgeauftrag entscheidet über die gemeinsame Aufnahme in AP-CV2-000 oder eine separate Dokumentausnahme.

## 5. Ende ohne weiteres reguläres Paket

Nach der Übernahme von AP-IV2-020 wird `COMPLETED` aus den tatsächlich angenommenen regulären Paketen, gültigen Review-/Freigabeakten und Git-/PR-Nachweisen abgeleitet. Zusätzlich dürfen keine offenen notwendigen Zusatzkorrekturen, Serverfixes oder Pflichtfindings bestehen. Die im letzten Featurecommit enthaltene Vormergephase READY_FOR_CANONICALIZATION ist erwartbar und verhindert den belegten Endzustand nicht. Bei fehlendem Merge-/Transport-/Pflichtbeleg bleibt der Abschluss offen.

Der Abschlussagent schreibt den **erst nach dem Merge erzeugbaren** Nachweis in der letzten Paketakte unter `NACH_ABSCHLUSS/ABSCHLUSS.json` oder einer gleichwertig indexierten Textdatei: AP-ID, Aggregate-SHA/Tree/Parent, finalen geprüften Head, PR/Gittransport, Review- und menschliche Freigabequelle, erforderliche Checks, abgeleiteten Zustand COMPLETED und verbliebene Produktgrenzen. Existierende abgeschlossene Run-/PASS-Berichte nicht umschreiben. Der Auftraggeber erhält denselben Nachweis mit erreichbarem Ablagepfad; ihn vor einem später beauftragten Worktreecleanup dauerhaft sichern.

Dieser Nachweis verlangt keinen weiteren Commit auf `feat/client-v2`. Bei vorhandener ausdrücklicher Akten-Gitfreigabe darf er ausschließlich als administrativer Nachtrag auf dem letzten Paketarbeitsbranch gesichert werden; keinen neuen Produkt-PR und keinen zweiten kanonischen Paketcommit erzeugen. Ohne diese Rechte ist die dauerhafte lokale Akte zulässig. Ein anderer Agent kann den Endzustand auch direkt aus den bereits versionierten Review-/Freigabeakten und tatsächlichem Git-/PR-Abschluss rekonstruieren; der Nachweis ist eine überprüfbare Zusammenstellung.

Bei einem später ausdrücklich beauftragten Zusatzfix wird der neue laufende Zustand daraus geführt und nach dessen belegter Übernahme erneut COMPLETED ermittelt. COMPLETED erlaubt keine automatische Serverfeature-/Mainpromotion, Tags, Releases oder Bereinigung.
