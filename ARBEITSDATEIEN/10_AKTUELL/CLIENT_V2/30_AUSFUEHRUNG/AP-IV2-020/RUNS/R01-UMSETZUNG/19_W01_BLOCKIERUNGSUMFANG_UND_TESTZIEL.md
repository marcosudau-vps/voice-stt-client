# W01: gezielter Aufschub der Serverkorrektur, Fortsetzung der Clientprüfungen

19.10.2026 · AP-IV2-020 / derselbe R01, Branch und kumulative Draft-PR15.
Grundlage: menschlicher Wunsch, unabhängige Clientprüfungen vor dem Server-FIX
fortzuführen, korrigierte V2-Testadressen und benannte VPS-Provenienzunterlagen.

**Ja: W01 verhindert nicht die weitere Bearbeitung des gesamten Clientpakets.**
Wir können unabhängige Prüfungen zuerst abschließen und die Korrektur in den
späteren Server-FIX-Schritt legen. W01 bleibt offen; seine betroffenen Nachweise
werden erst danach am korrigierten Paar wiederholt. Ein vollständiges AP020-PASS
vor diesen Pflichtbelegen wird damit nicht erteilt.

## Was Issue7 tatsächlich blockiert

W01 betrifft die serverseitige Wiederfreigabe der Wake-Erkennung nach einer
Wake-Activation: alte Modellhistorie kann trotz anschließender Stille einen neuen
Hit auslösen. Der Client verarbeitet dabei zwei verschiedene autoritative
Activations. Das ist weder ein allgemeiner Client-/HTTP-/Clipboardausfall noch
ein Beweis, dass beliebige ASR-Finals durch denselben Fehler ausbleiben.

| Pflichtfall | Unabhängig weiter prüfbar | Durch W01 zurückzustellender Anteil |
| --- | --- | --- |
| M-01 Manual-only | Mehrere Segmente, Follow-up, Finish, neues Diktat vor altem Final, genau einmalige Ausgabe; Wake schon in Hello deaktiviert | Kein direkter W01-Anteil. Ausbleibende Finals wären separat zu untersuchen. |
| M-02 Wake-only | Modellwahl, erstmaliger Treffer je kontrollierter frischer Session, Controls trotz deaktiviertem Manual | Vollständige wiederholte Wakefolge ohne unerwünschte neue Activation. Frische Sessions ersetzen diesen Nachweis nicht. |
| M-03 Both | Client-/Protokollguards und einzelne eng benachbarte Trigger beobachtbar | Reale Wiederfreigabe und wiederholte Wakephrase nach Close; vollständiger First-wins-/Repeated-hit-Gesamtlauf. |
| M-04 Controls | Phasenmatrix Refresh/Finish/Cancel/None und Kollisionen im Manual-only-Aufbau | Wakevarianten mit anschließender Wiederfreigabe; ungestörter Rückkehrzustand. |
| M-05 Run-Pausen | Flags, kein Trigger bei Unterdrückung, Erhaltung über Reconnect/Neustart gezielt prüfen | Neue Wake-Auswertung nach vorausgegangener Wake-Activation/Freigabe bleibt mitbetroffen. |
| M-06 Geräte | Audio-/LED-Verlust trennen, Hardwaremute, Wiedereinstecken und Cancel/Drain im Manual-Aufbau | Wake-Neuarmung und belastbarer Ausschluss einer Autoactivation danach. |
| M-07 Netz/Log | Verbindungsverlust mit Preview/Pending, neue Session, alte Finals nicht einfügen, Logstore-Unabhängigkeit und Log-Recovery im Manual-Aufbau | Ein zusätzlich beobachteter Wakefolgeablauf erhält einen eigenen begrenzten Status; Kern-Recovery wird nicht pauschal blockiert. |
| M-08 Settings | Explizites Cancel/Finish/Aufschieben, Drain/Reconnect und wirksame Werte im Manual-Aufbau | Wakebezogene Wechsel mit anschließender modellzustandsabhängiger Erkennung. |
| M-09 Credentials | Speichern/Ersetzen/Löschen, falscher/richtiger Key, Geheimnisschutz und Storefehler | Kein direkter W01-Anteil. Keine ungefragte Änderung produktiver Serverdefaults. |
| M-10 Feedback/Frozen | Manuelle Zustände, echte Sound-/LED-Ausgabe, Muster-/Lautstärke-/Overlaybewertung und alte Finals während neuer Aufnahme | Vollständiger Manual-/Wake-Paarvergleich und störungsfreier Wake-Abschluss/Idle. Zusätzliche W01-Starts dürfen nicht clientseitig versteckt werden. |
| M-11 Ausgabe | Clipboard, normale/erhöhte Anwendung, Konflikte, Reinsert und unklarer Pasteausgang im Manual-Aufbau | Kein direkter W01-Anteil. |
| M-12 Dauerlauf | Separater Manual-only-Ressourcen-/Recoverylauf als Teilbeleg möglich | Vollständige gemischte30min/100-Qualifikation mit Wakepositiv/-negativ, wiederholter Freigabe und Ende-zu-Ende-Kalibrierung. Ein Manuallauf allein schließt M12 nicht. |

REAL-01/02/04/05 bleiben damit teilweise betroffen; auch Wake-Neuarmungsanteile
von REAL-03. REAL-06 verhindert weiterhin, dass Teilnachweise als vollständige
Realgate-Abnahme ausgegeben werden. Bestehende Teilbelege werden angerechnet,
keine Pflichtfälle pauschal auf PASS gesetzt.

Der [TV-/Finishfall](18_AUTONOME_KLAERUNG_UND_RESTPUNKTE.md) bleibt **separat**:
W01 kann eine unerwünschte Activation erklären, beweist aber nicht die Ursache
des fehlenden Finals/Terminals danach. Diese Diagnose muss nicht auf W01 warten.

## Einordnung des späteren Serverpakets

Der aktuell versionierte [Paketindex](../../../../PLANUNG/ARBEITSPAKETE/README.md)
endet regulär bei AP-IV2-020. Zusätzlich ist
[AP-SV2-FIX](../../../../PLANUNG/ARBEITSPAKETE/AP-SV2-FIX.md) eine **bedingte
Vorlage**, kein bereits instanziiertes festes AP-IV2-030. Die spätere finale
Serverfeature-Übernahme ist eine eigene Promotion, keine automatische
Serverproduktkorrektur.

Für den gewünschten Ablauf ist kein sofortiger W01-FIX erforderlich:

1. Unabhängige Client-/Windowsprüfungen und geeignete Kalibrierteile jetzt.
2. Nachgewiesenen W01 im gesondert beauftragten Server-FIX bearbeiten und
   unabhängig abnehmen; hier wird noch kein Serverproduktcode geändert.
3. Neues Server-/Clientpaar prüfen, zurückgestellte Wake-/Feedback-/Dauerfälle
   abschließen; erst dann vollständige AP020-Abnahme.

Die Reihenfolge der **Bearbeitung** ist damit konkretisiert. Requirements werden
nicht stillschweigend aus AP020 entfernt oder an eine nicht vorhandene Paket-ID
verschoben. Falls AP020 bereits vor Schritt2 formal angenommen werden soll,
wäre dafür eine gesonderte ausdrückliche Änderung seiner Liefer-/Abnahmekriterien
und eines konkreten Folgepakets nötig; das ist nicht Voraussetzung für die
Fortsetzung der unabhängigen Arbeiten.

## Vom Menschen gewähltes vorhandenes Testziel

- Pro: `wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`.
- Alternative Normal: `wss://v2.voice-stt-server.marcosudau.com/ws/v2`.
- Zugehörige HTTP-Origins: jeweils HTTPS desselben Hosts.
- Die anfänglich genannte V1-Adresse ist durch die menschliche Korrektur
  ersetzt; deren404-V2-Vorcheck ist kein aktueller V2-Blocker.

Beide V2-Origins liefern Health, Settingsschema, Servereinstellungen und
Wakekatalog mit HTTP200. Pro `/ws/v2` hat einen diagnostischen V2-Hello angenommen;
keine Audioframes, keine Aktivierung, keine Settings-PATCHes, kein Desktopclient.
Beide konfigurierten Trigger waren während dieser Probe laufzeitunterdrückt.
Schema/Settings und Hello melden `serverCommit=unknown`. K-01 erlaubt dies,
verlangt dann aber den tatsächlichen Checkout-/Imagedigest-Nachweis.

Die benannten Unterlagen unter
`/home/marco/.codex_projekte/voice-stt-server_umstrukturierung/` enthalten
Buildmanifeste fürada13b0 mit `gitDirty=false`. Aktuell gelesene Containerimages
entsprechen genau deren festgehaltenen IDs:

| Ziel | Image-ID | Hostport |
| --- | --- | --- |
| Pro V2 | `sha256:57a7907b36389e09ce978efe0ceb18997f34eb729a0b29143bade01e96eb0078` | Loopback8021 |
| Normal V2 | `sha256:6dcc498e9c9154d24ad654108742d1630efed04b9a45af768401c750bfc81956` | Loopback8020 |

[Neu gesicherter lesender Laufzeit-/Build-/Quellnachweis](EVIDENCE/target-and-deferral-20261019/selected-server-identity.json):
Beide tatsächlichen Git-HEADs stimmen mit dem Pin überein, keine Änderungen an
getrackten Dateien, beide Wheel-SHA256 identisch zum jeweiligen Buildmanifest.
Die vier W01-relevanten `.py`-Dateien sind pro Container zusätzlich aus dem
installierten Paket nur in den Speicher gelesen und gegen die Quellen verglichen:
alle acht Vergleiche identisch. Keine Codemount-Overrides. Damit ist die gesonderte
Serverpinbindung trotz Wirewert `unknown` für diese beobachteten Images belegt.
Es handelt sich nicht um eine vollständige Paket-/Abhängigkeitsqualifikation.
Ein optionaler vollständiger Docker-Writable-Layer-Diff lief zuvor in45s-Timeout
und bleibt ausdrücklich NOT_PROVEN; er wurde nicht als bestanden umgedeutet.

Das sind neue Buildidentitäten und im Pro-Fall ein anderes Kroko-Modell
(Pro16 statt des bisherigen lokalen Community64). Bisherige Tests qualifizieren
dieses neue Paar nicht automatisch. Die Umstrukturierungsakte prüfte überwiegend
`/ws/transcribe`/OpenAI, nicht den vollständigen Desktop-V2-Ablauf; sie ist
Provenienz, kein Ersatz für AP020. Der neue `/ws/v2`-Hello ist separat belegt.

Für weitere diagnostische Open-/Serverantwort-/Modellstartprüfungen gelten
**180s Timeout**. Hello wird trotzdem unmittelbar nach Open gesendet;
festgeschriebene Serverprotokollfristen und Produktdefaults werden nicht verändert.
Die Umstrukturierungsakte dokumentiert einen kalten OWW-Start von etwa44s.

## Belege und Grenzen

- [V2-HTTP-Vorcheck beider Origins](EVIDENCE/target-and-deferral-20261019/v2-http-preflight.json).
- [Tatsächlicher Pro-V2-Hello mit180s-Prüfgrenzen](EVIDENCE/target-and-deferral-20261019/v2-hello-preflight.json).
- [Lesender Provenienzhelfer](EVIDENCE/human/capture_selected_server_identity.py).
- [Konsistenzprüfung und Grenzen](EVIDENCE/target-and-deferral-20261019/validation.json).
- Frühere V1-Prüfung bleibt als überholte Diagnose erhalten; keine V1- oder
  nachträgliche pauschale Serverqualifikation daraus.

Keine Deployment-, Image-, Konfigurations-, Servercode- oder Prozessänderung auf
dem VPS; keine neue lokale Serverinstanz. Status für **vollständige Abnahme**
bleibt **BLOCKED**. Der ausführbare Workflow wird auf **IMPLEMENTATION_IN_PROGRESS**
für denselben R01 zurückgeführt; W01 bleibt offen und zeitlich zurückgestellt.
Damit führt ein generischer Folgeschritt zu den unabhängigen Clientprüfungen
statt ungefragt eine Server-FIX-Umsetzung anzufordern. Kein Finding geschlossen.
