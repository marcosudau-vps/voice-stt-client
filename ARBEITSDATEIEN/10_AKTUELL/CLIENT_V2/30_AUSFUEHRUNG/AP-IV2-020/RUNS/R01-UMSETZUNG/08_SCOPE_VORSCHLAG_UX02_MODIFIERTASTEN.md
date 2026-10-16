# IV2-020-UX02 – zusätzliche Produktausnahme erforderlich

Status: **OPEN_SCOPE_APPROVAL_REQUIRED**. Derselbe AP-IV2-020/R01, Paketbranch und Draft-PR15. Produktcode unverändert; noch keine Korrektur angewandt.

## Reproduzierter Fehler

[Realer Manualdurchlauf](EVIDENCE/ux01/repeatable-manual-20261016-01/assessment.json): F8 Activate und F9 Finish tatsächlich accepted/applied, derselben Activation zugeordnet, input_closed=finished, ein Final34Zeichen und ein command_sent-Versuch. Im eigenen Qt-Ziel wurde **Ctrl+Shift+V** beobachtet (`shiftHeld=true`), kein MIME-Paste und null Zeichen. Der Benutzer hatte die F9-Hotkeymodifikatoren noch gehalten, als der schnelle Finaltext eintraf. Die Queue meldet korrekt nur command_sent; das ist keine bestätigte Zieleinfügung.

[Gezielter roter komponierter Nachweis](EVIDENCE/ux01/modifier-finding/held-shift-red.json) verwendet den tatsächlichen Finalconsumer, SQLite und Queueworker; ausschließlich die OS-Tastaturgrenze wird mit gehaltenem Shift modelliert. Ein Test scheitert gezielt am ausbleibenden Paste. Kein zusätzlicher echter Tastendruck und keine fremde Zwischenablage dabei.

## Ursache und kleinster Korrekturweg

`voice_stt_client/core/text_injector.py`, `WindowsInjectionBackend`/`CtypesWindowsInjectionBackend` und `TextInjectionQueue._process_job`: derzeit vier SendInput-Ereignisse Ctrl↓ V↓ V↑ Ctrl↑ nach50ms. Bereits gehaltene Shift/Alt/Win-Modifikatoren werden nicht berücksichtigt.

Vorschlag: tatsächlichen Modifiertastenstatus über die native Backendgrenze abfragen und im vorhandenen seriellen Worker **begrenzt** auf Freigabe warten. Erst dann Clipboard-/Ziel-/Pastevorgang ausführen. Nach Ablauf klarer fehlgeschlagener/übersprungener Versuch, kein SendInput und keine automatische Nachinjektion. Fokus/Clipboardsequenz am tatsächlich ausgeführten Paste weiter prüfen. Keine pauschal längere feste Pasteverzögerung und keine künstliche Key-up-Injektion gegen physisch gehaltene Tasten. Grenzwert/Abbruchverhalten mit Regressionen konkretisieren (Ausgangsvorschlag höchstens1500ms).

Finaltext/History/IDs/Deduplizierung, Runpausen, Serverprotokoll und bestehende Bedienfristen bleiben erhalten. Betroffen sind automatische Einfügung und bewusster Reinsert über denselben Worker.

## Erforderliche Nachweise nach Freigabe

Dauerhafte Regressionen zuerst rot: gehaltenes Shift/Ctrl/Alt/Win, Freigabe und unveränderte Standardausgabe, begrenzter Timeout ohne Eingabe, Fokus-/Clipboardkonflikt, Reinsert, Shutdown ohne hängenden Worker. Anschließend gezielte Integration, volle Windows-Suite, neuer Clientbuild mit Identität/Serverpaarprüfung und tatsächlicher nativer Halte-/Freigabetest. Vorherige Build-/Realbelege nicht pauschal auf korrigiertes Produkt übertragen.

## Warum eine zusätzliche Entscheidung nötig ist

Die menschliche Produktausnahme002 ist ausdrücklich auf Reconnect/Recovery begrenzt; Zusatzfreigabe006 betrifft UX01/Leerzeichen. UX02 ist eine zusätzliche native Ausgabekorrektur. Die eben beauftragten Testoberflächen-/Timinghilfen sind davon unabhängig bereits umgesetzt. Keine Produktkorrektur ohne ausdrückliche Erweiterung dieses engen Scopes. Kein Servercode, Protokollumbau, Release, Tag oder Übernahme erforderlich.
