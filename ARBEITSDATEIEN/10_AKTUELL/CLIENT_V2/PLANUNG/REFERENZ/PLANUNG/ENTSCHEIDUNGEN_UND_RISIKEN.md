# Entscheidungen, Grenzen und verbleibende Nachweise

## Verbindliche Entscheidungen dieser Planung

| ID | Entscheidung | Wirkung / Owner |
| --- | --- | --- |
| D-01 | Serverada13b0 ist Referenz, weiterhin ungemergt | alle Kontrakte und Integration darauf pinnen |
| D-02 | Feature-Linie a80a6b1/8bab1b3 fortsetzen; V1-f625904 gezielt früh integrieren | CV2-000 qualifiziert den neu entstehenden integrierten Start-SHA und voice_stt_client-Namespace |
| D-03 | Neuer Desktop ausschließlich V2, Server-V1 bleibt separater Pfad | CV2-020/110, kein Fallback/Serverabbau |
| D-04 | ein Mirror und IDgebundene Vorder-/Hintergrundmodelle | CV2-030, keine Qt-/Logparallelsteuerung |
| D-05 | vor Audiofreigabe Hello mit temporärer beidseitiger Suppression, NAsettings, availability, desiredPause | CV2-020/040/070/100, keine Defaultactivation im Bootstrap |
| D-06 | Primaryactive default refresh, Secondaryactive finish; Secondary/Wakepauseslot initial ungebunden | CV2-050/080, vorhandene explizite Belegungen sichtbar migrieren |
| D-07 | Secondaryidle keine Aktion, Primaryidle manualactivate, Controls in Wake-only erhalten | CV2-050 |
| D-08 | Duplicate physische Hotkeys als Applyfehler, Registrierungswechsel atomar mit Rollback | CV2-050/080 |
| D-09 | NSNoise/VADkeine individuelle Sessionpräferenz anbieten; tatsächlicher Admindefaultweg | CV2-070/080, kein stiller Serverfeatureausbau |
| D-10 | Adminprüfung über No-change-PATCH eines vorhandenen Defaults | CV2-080, kein erfundener Authendpoint |
| D-11 | nur Finalcompleted-Nutztext automatisch injizieren, Prozessdedup unabhängig von Historie | CV2-060 |
| D-12 | nach Crash unklarer Pasteversuch nicht automatisch erneut injizieren | CV2-060, Status unbekannt und bewusstes Reinsert |
| D-13 | Snapshotresync erhält Texte und markiert tatsächlichen Verlust als incomplete | CV2-030, keine Logreplayreparatur |
| D-14 | Settingsreconnect nennt auch Backgrounddrainverlust | CV2-080/100, ausdrückliche Benutzerwahl |
| D-15 | lokale Transport-/Puffergrenzen begrenzen Speicher und Wiederholungen | Werte in K-01/K-02/K-04 sind begründbar anpassbare technische Startwerte, keine Server-SLA |
| D-16 | vollständige Regression, qualifizierter Build, Prozessgate und reales Gate getrennt | CV2-110 / IV2-010 / IV2-020 |
| D-17 | Streng seriell, unabhängige Paketabnahme; Distributed-Kandidat vor Root-PASS, kanonisch ein Aggregat nach PASS und Auftraggeberprompt | Agentenregelwerk; Main-/Publishfreigabe getrennt |
| D-18 | 14 vollständige Umsetzungsläufe plus 14 unabhängige Abnahme-/Abschlussläufe; regulär 28, höchstens 30 ohne Korrekturen | Umfangsmodell und AP-Teilaufträge |

Interne Modul-/Testnamen und Datenrepräsentationen sind Vorschläge gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Die [Paketablage mit Vorlagen](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) legt eine schlanke einheitliche Struktur fest.

## Risiken und Auflösung

| ID | Konkretes Risiko / Grenze | Behandlung | Auflösung / Abnahme |
| --- | --- | --- | --- |
| R-01 | Featurevorarbeiten und veröffentlichter Paketnamespace divergieren | frühe Releaseportierung in die Featurelinie; Triggerassertions einzeln erhalten/überführen | CV2-000 Baselineinventar |
| R-02 | alte Acks/Closeevents setzen neuere Aufnahme zurück | Generation/Session/Activationguards; Event-vor-Acktests | CV2-030/IV2-010 |
| R-03 | Seqgap verliert einen Finaltext unwiederbringlich | incomplete anzeigen, Pufferpayload erhalten, keine Auto-Log-Paste | CV2-030/IV2-010 |
| R-04 | Wake-Engine-NSpatch sieht erfolgreich aus ohne Wirkung | requested/effective zeigen, Sessionpräferenz sperren | CV2-070/080 |
| R-05 | Aliaspatch speichert Rohwert | ausschließlich kanonische IDclientinputs | CV2-070; Serverfix optional bei tatsächlichem Bedarf |
| R-06 | reale Wakephrase/Nutzsprachgrenze nicht vollständig kalibriert | echte positive/negative Audio-/Grenztraces, pendingkennzeichnung | IV2-020; bis Beleg NOT_PROVEN |
| R-07 | Hardware/Coretests grün, echte Registrierung/USB/Clipboard scheitern | separates realWindowsgate und frozen Client | IV2-020 |
| R-08 | SQLiteidentitymigration verliert V1zeilen oder Attempts | Backup, Transaktion, idempotente schemaVersion, FKchecks | CV2-060 |
| R-09 | externe Injektion nach Crash doppelt | vorherige Attemptreservierung, unklarer Status ohne Auto-Retry | CV2-060/IV2-020 |
| R-10 | Settingsreconnect verliert alte Backgroundresultate | Zahl pendingActivations zeigen, warten/Verlust explizit | CV2-080/100 |
| R-11 | Secrets in Debug-/Config-/Bootstrapdarstellung | redigierte Credentialtypen, Memorytoken, CredManager, Exporttests | CV2-040/080/090 |
| R-12 | Logreplay produziert doppelte Feedback-/Finalnebenwirkungen | Domainmirror einzige Autorität, Logdiagnosepassiv | CV2-040/090 |
| R-13 | Audio nach Reconnect mit Settingsdefaults oder ungepaustem Wake | Bootstrapbarrier und temporäre Suppression | CV2-070/100 |
| R-14 | echte Serverbereitstellung unbekannt obwohl Branchfinal | Process-/Image-/SHAnachweis im Integrationsmanifest | IV2-010/020 |
| R-15 | Audiopfad ohne Anwendungs-Auth | bestehende Netzwerk/Proxykonfiguration separat beschreiben | Deploymentvorbereitung IV2; kein Client-Token erfinden |
| R-16 | voller Audio-/Resyncpuffer oder Task-/Tombstonewachstum | explizite Queue-/Puffer-/Retentionsgrenzen und Dauerprüfung | CV2-030/040/100, IV2-020 |

## Noch benötigte Eingaben / Nachweise

Für die Planung ist kein ungeklärter fachlicher Serververtrag als Voraussetzung versteckt. Vor Wireimplementierung muss CV2-000 die Feature-/Releaseintegration einschließlich Namespace und Gesamttests tatsächlich qualifizieren. Der noch nicht erzeugte integrierte Start-SHA darf nicht erfunden werden. Vor realer Abnahme werden passende Serverbereitstellung, Windows/ReSpeaker und bewusst gewählte Sprachsamples benötigt. Dies verhindert nicht die headless Clientpakete.

Ein Wunsch nach individuellen Noise/VADstartoptionen oder Domaintextreplay wäre eine neue Produktentscheidung und löst eine konkrete Erweiterungsspezifikation aus. Diese Planung implementiert die vorhandenen Grenzen konsistent und verlangt keine solche Änderung als Vorbedingung.

## D-19 / Revision 6: gemeinsamer Branch und ein Paketcommit

`feat/client-v2` beginnt bei der kanonischen Featurebasis 8bab1b3; deren Baum entspricht der bisherigen Ausführungsreferenz a80a6b1. Erster Commit nur vollständige Planung und Agenteneinstiege, danach pro AP ein Aggregat aus Code und aktualisierten Unterlagen. Bearbeitung und Korrekturen auf untergeordneten Paketbranches. Die [Branchreferenz](../GOVERNANCE/BRANCH_UND_PLANPFLEGE.md) ist für neue Zielrefs und Ablagen maßgeblich. D-02 bleibt fachlich erhalten, D-17 wird durch die paketbezogene Distributedrolle konkretisiert. Kein vorzeitiger Serverfeature-/Mainmerge; finales Serverrestaggregat erst nach gemeinsamer Qualifikation und eigener Freigabe.

## D-20 / Revision 9: vollständiger veröffentlichter Unterlagenstart

Alle Rollen-, Zustands-, Review- und Auftragsvorlagen gehören bereits in den ersten Unterlagencommit auf feat/client-v2. Frühere Arbeitsstände werden nicht mehr als zusätzliche Importvoraussetzung für AP-CV2-000 behandelt. Initiale Selbst-SHAs werden aus dem Gitverlauf aufgelöst; jeder tatsächlich begonnene Paketbranch dokumentiert seinen vollen kanonischen Parent. Unabhängiger PASS und menschliche Übernahmefreigabe bleiben getrennt. Der nächste Schritt wird aus belegten Zuständen erkannt; weitere unabhängige Reviews sind auf ausdrücklichen Auftrag möglich.

## D-21 / Revision 10: Ausnahmefälle ohne zusätzliche Pflichtkampagne

Tatsächliche Wiederaufnahmefreigabe, belegte Kandidatenwahl, servereigene FIX-Linie mit Rückkehr zum Client, unabhängig validierte echte Fremd-Hardwarebelege, ausdrücklich beauftragbare Anschlussfixes und abgeleiteter Endabschluss ergänzen die normale Serie. Paketfolge, Requirements, Kontrakte und Basisschätzung bleiben fachlich erhalten. Aktuelle Metadaten revision/roleSkillVersion gemeinsam pflegen; Schema-/Akten-/Aufwandsmodellversionen beschreiben eigenständige Formate.
