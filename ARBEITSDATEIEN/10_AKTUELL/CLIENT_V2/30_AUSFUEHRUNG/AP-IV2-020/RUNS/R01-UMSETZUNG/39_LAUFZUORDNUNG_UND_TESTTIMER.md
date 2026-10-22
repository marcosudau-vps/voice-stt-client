# AP-IV2-020/R01 – Laufzuordnung und Wartezeitkorrektur

Status **BLOCKED** / IMPLEMENTATION_IN_PROGRESS,22.10.2026.
Ausgangskandidat344f8693a83b0f0cc6dbd8afd8d5a60e6d7a00e4,
Baum604062ea3de62375dcee257308eb2b1d0497f32d. Produkt0f6c85e unverändert,
gleiche normale EXE/SHA und Pro-V2-Server67f3ce45/Instanz14e6ff8d wie
[Bericht38](38_ADMIN_UAC_EXE_UND_MINIMALER_ABSCHLUSS.md).
Gleicher R01, Paketbranch und Draft-PR15; kein Eigenreview/Übernahme.

## Menschliche Rückmeldung nicht ungeprüft als Real-PASS übertragen

[Die Rückmeldung](ZUSATZPROMPTS/038_RUECKMELDUNG_OHNE_LAUFZUORDNUNG.md)
bestätigt sichtbaren Text und Fensterschluss. Die tatsächlich gespeicherte
[Vorbereitung](EVIDENCE/probe-followup-20261022/frozen-live-minimal-ready.json)
zeigt jedoch TIMEOUT ohne Clientstart: bootloaderPid=null, Produkt-PID=null,
keine Ereignisse/History/Editorzeichen, keine Clientdatenbank. Beginn02:25:40,
Ende02:55:41 Europe/Berlin. Keine weitere eigene aktuelle Probe auffindbar,
die diese menschliche Beobachtung eindeutig zuordnet. Satz auf Nachfrage
nicht mehr bekannt. Ergebnis **HUMAN_REPORTED_SUCCESS_UNBOUND**, technischer
Live-Nachweis weiterhin NOT_PROVEN. Keine Ursache der Diskrepanz behauptet.

## Nachgewiesener Hilfsfehler und Korrektur

Die Testhilfe rechnete ihre1800s auch während der Vorbereitung vor dem
Startklick. Dadurch konnte sie sich ohne Clientstart selbst schließen.
Fehlversuch erhalten, kein Produktfehler daraus abgeleitet. Korrektur:
vor Start zeitlich unbegrenzt, begrenztes Testbudget erst ab tatsächlichem
Clientstart. Wiederholen verlängert dieses laufende Budget nicht beliebig.
Startklick/Bootloaderbindung werden unmittelbar gespeichert. Zwei dauerhafte
Regressionen decken beliebig langes Vorabwarten und echte Laufzeitgrenzen ab.

Ein tatsächlicher eigener GUI-Startklick mit normaler EXE, Ready und
achtsekündigem Vorbereitungsweg wurde über Windows/Stereomix geprüft.
Autonome Fixturewiedergabe ist als solche markiert. Dieser
[Kontrollversuch](EVIDENCE/probe-followup-20261022/frozen-operator-flow-selfcheck.json)
endet **NOT_PROVEN**: ein Wake und eine zusätzliche protokollierte
Primary-Hotkey-Aktivierung, keine erkannte Nutzsprache/History/Einfügung.
Herkunft der zusätzlichen Taste nicht gesichert, kein sauberer neuer
Wake-/ASRvergleich und kein menschlicher Hardware-PASS. Nur der beobachtete
Start/Ready/Countdown ist ein technischer Teilbeleg. Automatische Kontrollen
tragen künftig einen eigenen deutlichen Fenstertitel und Bedienhinweis,
damit sie nicht wie eine neue menschliche Sprechaufgabe erscheinen.

## Validierung, Bereinigung und verbleibende Grenze

82Helfertests/0Skips PASS, compileall PASS. Produkt-/Buildquellen unverändert;
1400Windows/0Skips am identischen Produkt bleiben gültig. Kein Neuaufbau,
Server-/Default-/Credential-/V1-Eingriff. Öffentliche Daten redigiert und
gehasht, private Laufzeitbytes im ignorierten Archiv.

Die zuvor ungestartete Vorbereitung und der eigene Kontrollversuch sind
beendet, vollständig privat hasharchiviert und mit dem verifizierenden
PowerShell-Skript entfernt. Auch Helfer-TEMP entfernt. Genehmigter externer
Qualifikationsnamensraum wieder leer. Kein Testclient und keine weitere
menschliche Sprechaufgabe laufen. Keine erneute subjektive Feedbackbefragung.

Die [Restmatrix](EVIDENCE/probe-followup-20261022/qualification-matrix.json)
übernimmt die konkreten technischen Grenzen aus Bericht38. Admin und
UAC-Teilnachweise bleiben gültig, subjektive Bewertung menschlich beendet,
W02 bleibt geschlossen. Nicht eindeutig gebundener ReSpeaker-EXE-Retestsieg
schließt weder die erste fehlende automatische Einfügung noch die fehlenden
Hardware-/Pendingfinal-, Frozen-Überlappungs- und physischen Dauergrenzen.
Weiterhin kein REVIEW_READY oder ROOT_PASS. Nächste Aktion ist ein eindeutig
identifizierter technischer Restlauf nach Verfügbarkeit menschlicher
Hardwarebedienung; keine erneute allgemeine Arbeits-/Gitfreigabe erforderlich.
