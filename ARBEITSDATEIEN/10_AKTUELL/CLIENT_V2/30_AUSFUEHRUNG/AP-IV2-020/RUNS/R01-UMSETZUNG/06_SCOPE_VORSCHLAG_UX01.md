# Produktkorrektur UX01 – ausdrücklich freigegeben

Gleicher AP-IV2-020/R01. **Am 2026-10-15 ausdrücklich freigegeben**, siehe [wörtliche Freigabe](ZUSATZPROMPTS/006_UX01_FREIGABE.md). Umsetzung und technische Requalifikation laufen. Die folgenden Vorschlagspassagen dokumentieren den vor der Freigabe vorgelegten Stand. Historische rote Belege bleiben unverändert. Die erteilte Produktausnahme
[Reconnect/Recovery](ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md) deckt den
fachlich unabhängigen Einfügeparameter nicht ab. Entscheidung gebündelt mit
dem laufenden Kalibrierungsstand; keine weitere Freigabe für Recoverykorrekturen
erforderlich. Kein Serverprodukt-/Protokolleingriff vorgeschlagen.

## Konkreter Fehler und Ursache

`text_injection.append_space=true` ist bestehende Konfiguration und sichtbare
Einstellung, wird aber im aktiven Einfügepfad nicht gelesen. Zwei richtige Finals
werden daher ohne Trennzeichen aneinandergefügt. Native Manualbaseline und
[gezielter roter Nachweis](EVIDENCE/human/append-space-red.json) bestätigen das.
Eine gefüllte Zwischenablage allein beweist keine erfolgreiche Zieleinfügung;
dieser Befund ist vom später separat untersuchten Fokusproblem getrennt.

## Kleiner, konkret prüfbarer Änderungsvorschlag

[Unangewandter Patch](EVIDENCE/human/append-space-proposed.patch.gz) ausschließlich
in `voice_stt_client/core/text_injector.py`:

- Nach der Leertextprüfung lokalen `payload_text` bilden.
- Bei aktivierter Einstellung ein Leerzeichen ergänzen, falls das Ende noch
  kein Whitespace ist.
- Diesen Ausgabetext in die Zwischenablage schreiben.
- Originales Final, History, IDs, Reservierung, Deduplizierung und unveränderlicher
  Queuejob bleiben unverändert. Der vorhandene gemeinsame Pfad gilt auch für
  manuell angeforderte Wiedereinfügung.

Der Patch ist mit `git apply --check` gegen den unveränderten Produktstand
prüfbar. Er wurde nicht auf Produktdateien angewandt. Eine isoliert nur im
Speicher ausgeführte Vorschau desselben Codes besteht
[vier gezielte Fälle](EVIDENCE/human/append-space-preview.json): True ergänzt,
False lässt unverändert, vorhandenes Leerzeichen beziehungsweise Newline
bleibt erhalten. Das ist kein Green-PASS des noch unveränderten Produkts.

## Umfang einer eventuellen Freigabe

Diese Produktkorrektur, dauerhafte Regressionen für automatische und explizite
Wiedereinfügung sowie notwendige Präzisierung vorhandener Testfixtures, die
bisher rohen unveränderten Text voraussetzen. Keine vorsorglichen Refactors.
Danach Windows-Vollsuite, betroffene Integration, neue Builds/Identitäten und
Paarprüfungen; reale Pflichtnachweise an den endgültigen Stand binden.

Die bereits menschlich gewählten5000ms Follow-up und der gemessene320ms
Pre-Roll-Kandidat sind vorhandene Session-/Profileinstellungen und bleiben
innerhalb der erlaubten Testkonfiguration. Ihre Persistenz wird über das
bestehende Konfigurationssystem nachgewiesen. Eine Änderung globaler
Serverdefaults oder sonstiger Produktdefaults ist mit diesem Patch nicht nötig.

Bis zum erfolgreichen Abschluss der erforderlichen Nachweise bleibt UX01 offen. Weitere bloße Risiken oder Fehler der
Testdurchführung werden nicht still als Produktänderungsgrund hinzugefügt.
