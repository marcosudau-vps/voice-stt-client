# Bewertung der externen Prüffunde und Korrektur Revision 10

Stand 2026-10-11. Auftrag: die Funde selbst bewerten und bei Bedarf korrigieren. Grundlage ist der [originale externe Prüfbericht](HISTORIE/EXTERNER_PRUEFBERICHT_REV9.md), bytegleich aus dem Anhang übernommen. Geprüfter veröffentlichter Planstand: `bfade9d0ffe1262ca25b05c9334dcacfcd3d3452` auf `feat/client-v2`.

Die sechs Punkte beschreiben reale praktische Lücken oder Präzisierungsbedarf. Sie begründen keine neue Produktarchitektur und keine zusätzliche reguläre Paketserie. Die Bewertung 8,5/10 übernehme ich nicht als formales Prüfsiegel. Diese Revision ist eine gezielte Unterlagenkorrektur, keine unabhängige Abnahme ihrer eigenen Umsetzung und keine V2-Produktqualifikation.

| Befund | Eigene Bewertung | Korrektur / maßgebliche Stelle |
| --- | --- | --- |
| B-01 Wiederaufnahme | Berechtigt: der Schutz fremder Arbeit war vorhanden, aber die Voraussetzung für eine geordnete Übernahme blieb ungenau. | [Sonderfallreferenz](../SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md): echte Übergabe oder menschlicher Recoveryauftrag, erreichbare WIP/Commit-/Aktenprüfung, neuer tatsächlicher Run, belegter Ownerwechsel. Keine Altersheuristik, kein Reset/Force-Push. REVIEW_IN_PROGRESS macht auch aktive Reviewarbeit erkennbar. |
| B-02 Serverfix-Routing | Berechtigt: die Rollen-Skills enthielten überwiegend Client-PR-/Zielprüfungen. Ein Serverfix darf nicht an diesen Kriterien hängenbleiben. | SERVER_FIX_REQUIRED plus verlinkter eigener Serverstatus; Rollen-Scope vor Auswahl auf Server/FIX/Distributed auflösen. Eigener Serverauftrag, dortiger Review/Sicherungsnachweis, anschließend Rückkehr zum gehaltenen Clientpaket mit neuer SHA und Paarprüfungen. [FIX-Spezifikation](../ARBEITSPAKETE/AP-SV2-FIX.md). |
| B-03 Kandidatenwahl | Berechtigt: Auswahlereignis und konsistente Ablösung waren nicht konkret genug. | `candidateSelection` mit tatsächlicher Quelle; erster normaler Start ausgewählt, Alternativen zunächst ungewählt. Eindeutige `-attempt-nn`-Branches, Ablösebeleg mit beiden Linien/SHAs, alte Linie SUPERSEDED. Unauflösbarer Konflikt bleibt BLOCKED; kein geerbter PASS. [Zustandsreferenz](../SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md). |
| B-04 Plattform-/Hardwarebelege | Berechtigt: Pflichtfälle waren definiert, aber Eigen- und Fremddurchführung nicht ausreichend unterschieden. | [Windows-/Hardware-Nachweisregeln](../REFERENZ/QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md): realer benannter Bediener darf ausführen, Reviewer prüft Herkunft/Build/SHA-Paar/Wirkung und veranlasst nötige Nachtests. Keine Pflicht zur doppelten gesamten Hardwarekampagne; kein Fake-/Aussage-PASS. |
| B-05 Änderungen nach Annahme | Teilweise bereits geregelt: Branchführung erlaubte ausdrückliche Ausnahmen. Für einen Produktfix nach dem letzten regulären Paket fehlte eine klare Instanz-/Ownershipregel. | Bestehende Ausnahme präzisiert: konkretes ausdrücklich beauftragtes AP-CV2-FIX-nnn mit aktuellem Parent, Repro/DoD, eigenem Review und einem neuen freigegebenen Aggregat. Alte Commits/PASS-Akten erhalten, bestehende Requirements über affectedRequirements verlinken. [Branchreferenz](../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md). |
| B-06 Letzter Abschluss | Präzisierungsbedarf: COMPLETED und Ableitung aus Git existierten, aber der endgültige post-merge Nachweis ohne Folgepaket hatte keinen klaren Ablageort. | Letzte Paketakte `NACH_ABSCHLUSS/ABSCHLUSS.json`; tatsächliche Aggregate-/Review-/Freigabe-/Transportidentität. COMPLETED auch direkt aus Git ableitbar, kein zusätzlicher Featurecommit. [IV2-020](../ARBEITSPAKETE/AP-IV2-020.md). |
| M-01 Revisionsmetadaten | Berechtigt: package-manifest revision=6/roleSkillVersion=2 waren veraltet. | Baseline und Manifest gemeinsam revision=10/roleSkillVersion=5; Schema-/Aktenformatversionen getrennt erklärt. Paketliste/Ownership unverändert. |
| M-02 Aufwand | Redaktionelle Präzisierung sinnvoll; die bisherigen Zahlen schlossen Korrekturen bereits aus. | [Umfangsmodell](../REFERENZ/PLANUNG/UMFANG_UND_AGENTENLAEUFE.md) ausdrücklich als 28–30 Basissessions, keine Gesamtprognose einschließlich Zusatz-/Korrektur-/Recoveryläufen. Keine neue Pflichtsession. |
| M-03 Wiederholter Standardtext | Wartbarkeitshinweis, kein konkreter Fehler. | Gezielte gemeinsame Sonderfall-/Hardware-Referenzen mit bedingtem Lesen. Kein breiter Umbau der bestehenden fachlichen AP-Spezifikationen in diesem Auftrag. |

## Präzisierung einer Aussage des externen Berichts

Die Formulierung, bfade9d liege „einen Commit hinter dem beschriebenen Planungsstart“, ist ungenau. Dieser Commit ist **selbst der Planungsstart**: genau ein neuer Single-Parent-Commit nach `8bab1b3f4aa070d0756c305908def4d9ebc52582`. HEAD, Parent, Commitanzahl und Remote wurden aus Git geprüft. Die Aussage, dass noch keine AP-CV2-000-Implementierung vorliegt, stimmt.

## Nachprüfung der Sonderfälle anhand der Regeln

Diese Situationen wurden durch Lesen der vollständigen jeweils verlinkten Anweisungen bewertet; keine tatsächlich ausgeführten Produkt-/Hardwaretests und keine simulierten unabhängigen Agentensessions:

| Prüfsituation | Erwarteter Weg der Revision 10 |
| --- | --- |
| Alten aktiven Owner nur wegen Alters als verlassen ansehen | Keine Übernahme; tatsächliche Übergabe/Ende klären. |
| Mensch beendet alten Run und erlaubt Fortsetzung vom bereitgestellten Stand | WIP-/Aktenstand sichern, Originalauftrag belegen, neuen Run/Owner setzen, fehlende lokale Arbeit ausdrücklich einordnen. |
| Review läuft, zweiter generischer Auftrag erscheint | Schreibhoheit/Reviewfreeze beachten; kein paralleler Review desselben Kandidaten. |
| Serverdefekt belegt, nur Client-Gitrechte vorhanden | Client bleibt SERVER_FIX_REQUIRED; benötigten Serverauftrag konkret melden. |
| Server-FIX im eigenen Repo REVIEW_READY | Serverrolle/Distributed-Base prüfen, unabhängige Serverabnahme, keine feat/client-v2-PR-Prüfung. |
| Serverfix tatsächlich auf Distributed gesichert | Rückkehr zum gehaltenen Clientpaket, neue Server-SHA/Vertragswirkung und Regression/Paarprüfungen, kein neues AP starten. |
| Zwei Versuche, A ausgewählt und B ungewählte Alternative | Generischer Folgeauftrag bleibt bei A; ausdrücklicher B-Auftrag darf B bearbeiten. |
| Zwei true-Felder ohne Ablösebeleg | Auswahlkonflikt melden, keine Zeitstempelwahl. |
| Mensch wechselt von A zu B | Entscheidung/alte Findings sichern, A ersetzt, B ausgewählt, kein übertragener PASS. |
| Bediener liefert vollständige reale Windowsbelege | Reviewer prüft Identität/Fallabdeckung/Wirkung, eigene Prüfungen und validierte Fremddurchführung getrennt ausweisen. |
| Linuxsuite grün, echte Windows-Pflichtfälle fehlen | Kein Paket-PASS; Plattformnachweise fehlen weiterhin. |
| Defekt nach letztem angenommenem AP | Konkreten Zusatzfix beauftragen; eigene Instanz, Review/Freigabe und neuer Aggregatcommit, alte Geschichte erhalten. |
| Letzter AP gemergt, Index zeigt Vormerge-PASS | Git-/Review-/Freigabe prüfen, COMPLETED ableiten und post-merge Beleg in letzter Paketakte sichern. |

## Umfang und Bereitstellung

Kontrakte, Wire-/Settingsvektoren, die 216 Requirements und deren fachliche Paketownership bleiben unverändert. Zwölf Clientpakete, zwei Integrationspakete, bedingte FIX-Vorlage; kein Paket begonnen oder als bestanden markiert.

Die Korrektur wurde auf `work/client-v2/planung-rev10` ab dem veröffentlichten Revision-9-Start vorbereitet und dauerhaft gesichert. Anschließend hat der Auftraggeber die Übernahme von Revision 10 als **einen Dokumentkorrekturcommit auf `feat/client-v2` einschließlich normalem Push** ausdrücklich beauftragt; [Originalfreigabe und Umfang](VEROEFFENTLICHUNGSAUFTRAG_REV10.md). Dieser Commit enthält ausschließlich Unterlagen und Veröffentlichungseinstiege. Der veröffentlichte Startcommit wird erhalten; AP-CV2-000 startet danach vom aktuellen Feature-HEAD. Keine Produkt-/Paketabnahme und keine zukünftige Umsetzungsfreigabe.

Formale Nachprüfung des vorbereiteten Korrekturstands: [revision10-validation.json](revision10-validation.json). Veröffentlichungssatz mit aktualisierten Statusangaben: [revision10-publication-validation.json](revision10-publication-validation.json). Gesamtbericht: [PRUEFBERICHT.md](PRUEFBERICHT.md).
