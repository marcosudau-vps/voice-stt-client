# Gemeinsamer Test- und Kalibrierungsablauf

Stand 2026-10-15, R01 bleibt derselbe Umsetzungsauftrag. **In Durchführung: erster Manual-/Follow-up-Block aktiv.**
Verbindliche Kriterien: [M-01 bis M-12](../../../../PLANUNG/REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md).
Die maschinenlesbare [Fallakte](EVIDENCE/real-cases.json) ist das Ergebnisregister.
Vorchecks ergeben keinen M-PASS. Der Agent liest die Diagnosen selbst und ergänzt
je Versuch Zeit, Build/Server/Config, tatsächliche Aktion, Wirkung und Herkunft.

## Isolierte Testumgebung

- Korrigiertes Produkt `41ca7612db526532509ecab65ff9d7d182da565c`; Frozen-EXE
  SHA256 `137a8fc259e05f3a90f23c2babbf4325419bc9cc4195d123b4db6159cae85226`,
  `dist-feedback-rc-iv2-020-recovery/voice-stt-client.exe`; [neue Qualifikation](EVIDENCE/recovery-audit/qualification-summary.json).
- Lokaler Server `127.0.0.1:18020`, exakt ada13b0, Community-DE-64-L, eigene Datenvolume.
- Clientprofile, History, LEFX-Zustand, Cursor, Logs und Samples ausschließlich unter
  `%LOCALAPPDATA%/VoiceSTT-Qualification/AP-IV2-020/`.
- `scripts/qualify_v2_session.py prepare` erstellt Manual/Wake/Both, ohne vorhandene
  Testprofile zu überschreiben. Source-Sitzung: `run --mode manual|wake|both`.
- Hotkeys: **Strg+Umschalt+F8** Primary, **F9** Secondary/Finish, **F10** Wakepause,
  **F11** Wiedereinfügen, **F12** Overlay, jeweils dieselben Modifier.
- Source-Messsitzung instrumentiert die tatsächlichen korrigierten Desktop/Core-/Win32-/Audio-/USB-Komponenten.
  Frozen-Bedienung wird gesondert geprüft; Sourcebelege werden nicht als Frozen ausgegeben.
- Rohaufnahmen und private Transkripte bleiben lokal außerhalb Git. Ins öffentliche
  Protokoll kommen nur geeignete Zustands-/Score-/Timingwerte und ausdrücklich gewählte
  kurze Testtexte. Keine allgemeine Hintergrundaufnahme speichern.
  Ausnahme auf ausdrücklichen [Nutzerwunsch](ZUSATZPROMPTS/004_TESTAUFNAHMEN_REPO.md):
  sechs bewusste Sprach-Testfixtures mit Metadaten/Hashes unter
  [samples/](EVIDENCE/human/samples/README.md) wiederverwendbar versioniert.

## Block 1: leeres Textziel, manuelle Aufnahme und Windowsfunktionen

Einmal ein leeres Editorfenster bereitstellen. Agent startet erst dann den Testclient.

1. M-01: F8; „Dies ist der erste Testsatz.“ Kurze Pause, „Dies ist der zweite Testsatz.“
   Mit F9 beenden. Danach F8 schon vor dem letzten Final. Prüfen: beide Finals jeweils
   einmal, kein Zwischentext im Editor, aktuelle Aufnahme bleibt beim alten Final bestehen.
2. M-04: Primary/Secondary in waiting/recording/followup; Agent variiert die vorhandenen
   Aktionen refresh/finish/cancel/none über Testprofile. Ein realer Fremdprozess hält
   einen Hotkey, Konflikt und Rollback werden nochmals beobachtet. Refresh ist laut
   Controlvertrag in waiting_first_speech wirkungslos, kein Clienttimer wird erfunden.
3. M-09: Admin falsch/richtig, Anlegen/Ersetzen/Löschen über UI; Agent liefert den
   isolierten Testguard ohne Clipboardtransfer und kontrolliert No-change-PATCH,
   Restart-/Originbindung und redigierten Export. Keine produktiven Keys verwenden.
4. M-11: Agent startet das separate leere Clipboardtestfenster. Ein Klick darauf ist
   nötig, falls Windows den automatischen Fokus verweigert. Danach prüft der Helfer
   native Unicodeinjektion, automatische Deduplizierung, explizite Reinsertion und
   echte Clipboard-Sperre eines fremden Prozesses. Eigene Nutzereingaben während dieses
   kurzen Tests vermeiden; bestehende Clipboardformate werden im RAM erhalten.
5. Zusätzlich normales Windows-Editorziel und elevated Ziel testen. Elevatedstart
   benötigt gegebenenfalls den echten UAC-Klick des Auftraggebers. Verhalten bei UIPI,
   Clipboardänderung und Prozessabbruch nahe Paste exakt erfassen; unbekannte Versuche
   dürfen nicht automatisch erneut eingefügt werden.

## Block 2: Wakepositive, negative Sprache, unmittelbarer Nutzsprachbeginn

M-02/M-03/M-12 und REAL-02. Agent startet Wake/Both mit hey_jarvis und alexa.

1. Je Phrase drei Wiederholungen in normaler Lautstärke, zunächst mit einer kurzen
   Pause, danach direkt anschließend „Der blaue Becher steht auf dem Tisch.“
   Separate bewusst gesprochene Samples mit `record --name ... --seconds 12` aufnehmen.
2. Mindestens eine nicht ausgewählte Phrase und natürliche Sprache ohne Wakephrase
   sprechen. Bestehendes negatives Referenzmaterial ergänzen, nicht ersetzen.
3. Hotkey und Wake eng benachbart, Wake während recording, wiederholtes Wake nach
   input_close. Gewinner-ID, genau eine Activation und Latch/Cooldowntrace prüfen.
4. Die Nutzsprachgrenze gemeinsam abhören/annotieren: tatsächliches Wakeende und
   erster Nutzsprachlaut gegen Predictionframes, trailing-edge-Zero und Pre-Roll.
   Weder positiver Treffer allein noch ein synthetisches Sample schließt die Grenze.
5. Varianten nach [Kalibrierungsplan](03_KALIBRIERUNG.md) einzeln vergleichen. Agent
   übernimmt Scoreauswertung, dokumentiert Varianten und wiederholt betroffene Tests.

## Block 3: Geräte-, Pause-, Netzwerk- und Settings-Recovery

M-05..M-08. Einmal denselben ReSpeaker verwenden; Agent kündigt jeden Trennpunkt an.

1. Wakepause und Manualpause getrennt und gemeinsam; Netzreconnect, Mute und Neustart.
   Pausen gelten für Run/Session und werden beim Programmneustart nicht persistiert.
2. Hardware-Mute drücken/lösen. Während foreground und älterem Drain USB abziehen,
   warten und wieder einstecken. Nur echter Audioverlust cancelt foreground; ältere
   Finals und Session bleiben bei Geräteverlust erhalten, keine Autoactivation.
3. LED-only-Ausfall bei weiter verfügbarem Mikrofon getrennt erzeugen. Agent nutzt
   hierfür ausschließlich den isolierten Ausgabepfad. Wenn die Hardware keine
   unabhängige physische Trennung bietet, die genaue Fault-Grenze benennen und keine
   Softwarebenachrichtigung als echten USBverlust deklarieren.
4. Agent erzeugt den Server-/Netzausfall ausschließlich an der Testinstanz, je während
   Preview und ausstehendem Final. Logstoreausfall separat. Neue Session, unterbrochene
   alte Ergebnisse und fortbestehende STT-Bedienbarkeit am tatsächlichen Trace prüfen.
5. Settings bei Aufnahme ändern: cancel/finish/vormerken; bei Drain warten oder
   explizit Verlust wählen. requested/effective auf alter und neuer Activation sowie
   neue Session gegenüberstellen. NS-Noise/VAD nur in isolierten Serverdefaults ändern.

## Block 4: Frozenfeedback und Bediengefühl

M-10 sowie kalibrierte Teile M-01..M-04. Sourceclient zuerst kontrolliert beenden.
EXE mit explizitem Testprofil und `VOICESTT_CLIENT_HOME` auf Testroot starten.
Keine gleichzeitige V1-/V2-LEDsteuerung.

Manual/Wake-Paarvergleich: Waiting, Recording, Follow-up, Finalizing, Erfolg, Abbruch,
Warnung und Recovery. A-Final während B-Aufnahme: LED/Tray/Overlay bleiben bei B.
Vorhandene LED-/Sound-/Overlaywerte in gezielten Varianten vergleichen und bewerten:
„zu früh/spät“, „zu kurz/lang“, „zu hell/dunkel“, „zu laut/leise“, „passt“.
Agent protokolliert die Zuordnung technischer Ereigniszeit zu beobachtetem Feedback.

## Block 5: finaler Stabilitätslauf und Abschluss

Nach bestätigter Konfiguration mindestens **30 Minuten und 100 abgeschlossene
Activations**, wiederholte USB-/Netzreconnects und mindestens einen echten legal
verkürzten Watchdoglauf warning → expiry → Audioverarbeitung. Dauersprache darf die
Watchdogfrist nicht verlängern. Dafür explizite Testsamples, keine privaten Mitschnitte.

Agent erfasst warmen Start, Verlauf und Ende: RSS/Private Bytes, aktive Tasks,
Pendingcommands, Audio-/Injektionsqueues, Activations/Segmente und Terminals sowie
Preview-/Final-/Acklatenzen. Er erklärt Speicheranstieg nach Warmup und überprüft
Retention statt bloß zwei Endpunkte zu vergleichen. Wiederverwendete reale Samples
werden als Replay gekennzeichnet und nicht als 100 menschliche Neusprechvorgänge.

Nach relevanter Kalibrieränderung betroffene Nachweise neu erstellen. Abschließend
vollständige Windowsregression, compileall, Diff-/Aktenprüfung und Traceability.
Pflichtlücken bleiben NOT_RUN/NOT_PROVEN, Fehler FAIL. Erst vollständige Abgabe
REVIEW_READY; unabhängiger Review und menschliche kanonische Übernahme folgen separat.

## Technischer Abschluss vor Beginn der gemeinsamen Blöcke

Die Reconnectfindings F01 bis F10 sind technisch korrigiert und requalifiziert;
[Findingregister](EVIDENCE/recovery-audit/findings.json). Der Paketstatus ist weiter
IN_PROGRESS, die fünf Blöcke wurden noch nicht als menschlich durchgeführt erfasst.
Es ist keine weitere allgemeine Fortsetzungsfreigabe erforderlich. Nächste nötige
menschliche Aktion: einen leeren Testeditor fokussieren und die zwei vereinbarten
Testsätze mit den vorbereiteten Hotkeys sprechen. Der Agent startet/überwacht,
liest Metriken selbst und leitet anschließend gebündelt weiter.

Watchdogmechanismus autonom ergänzt: echte Referenzsprache (4s), danach kontrollierter
PCM-Stillstand bei bestehendem WS; reale Warnung und Ablauf nach legaler 60s-Frist,
anschließend echte Finalverarbeitung. Keine Erhöhung der 30s-Segmentgrenze. Dieser
gezielte Medienfehler ist kein 60s-Dauersprach- oder menschlicher Feedbackbeleg.

Der vorbereitete separate `EVIDENCE/recovery-audit/human_test_editor.py` stellt
auf Wunsch des Testablaufs ein echtes Windows-Textziel bereit. Sein Zustand
(inklusive ausschließlich vereinbartem Testtext) bleibt unter dem isolierten
AppData-Testroot; der Agent liest ihn selbst. Es ist nur ein menschlicher Klick
zum Fokussieren nötig. Der Helfer injiziert nichts und verändert kein Clipboard.
Sein eigener Offscreen-Vorcheck ist kein realer Pastebeleg.
