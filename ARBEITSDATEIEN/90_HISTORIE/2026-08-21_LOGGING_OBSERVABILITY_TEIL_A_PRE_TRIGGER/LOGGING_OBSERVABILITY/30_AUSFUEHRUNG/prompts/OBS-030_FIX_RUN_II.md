Führe jetzt einen eng begrenzten Cleanup des OBS-030-Korrekturlaufs durch.

Dies ist KEIN neuer Implementierungslauf und KEINE erneute Architekturarbeit.

Ziel ist ausschließlich, zwei inzwischen von dir selbst als nicht eindeutig autorisiert bzw. als echte Contract-Erweiterung identifizierte Änderungen zurückzunehmen, bevor der Stand erneut unabhängig geprüft wird.

Arbeitsbereich:

P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur

## Vor Beginn

Bevor du irgendetwas änderst, lies jetzt die im vorherigen Korrekturlauf ausgelassene verbindliche Pflichtlektüre:

- ARBEITSDATEIEN\README.md
- ARBEITSDATEIEN\AGENTS.md
- ARBEITSDATEIEN\00_STEUERUNG\MASTERPLAN.md
- ARBEITSDATEIEN\00_STEUERUNG\ARBEITSPROZESS.md
- ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\AGENTS.md

Prüfe anschließend nochmals die für die beiden Punkte unmittelbar maßgeblichen Stellen in:

- LOGGING_ARCHITEKTUR_FREEZE_V1.md
- LOGGING_CONTRACTS_FREEZE_V1.md
- LOGGING_DECISIONS_FREEZE_V1.md
- WP-OBS-030
- RUN-OBS-030-02
- GATE-REVIEW-01

Die bestehende Stellungnahme zu den drei Prüfproblemen ist ebenfalls verbindlicher Kontext für diesen Cleanup.

## Harte Scope-Grenze

Ändere ausschließlich, was für die beiden nachfolgenden Rücknahmen und die dadurch zwingend notwendigen Test-/Evidence-Konsistenzanpassungen erforderlich ist.

Insbesondere:

- die bereits umgesetzten fachlichen B-1-, B-3- und W-1/W-2/W-4/W-5/W-7-Korrekturen NICHT zurücknehmen,
- Worker-Failure-Isolation nicht verschlechtern,
- P-8 nicht zurücknehmen,
- Store-/Sink-Isolation nicht zurücknehmen,
- Retention-Pressure-Verhalten nicht zurücknehmen,
- keine neuen Architekturentscheidungen treffen,
- keine Implementierung von OBS-040 oder späteren Paketen beginnen,
- historische Gate-FAIL-Evidence nicht löschen oder umschreiben.

---

# Korrektur 1 – `dropped_failed` vollständig zurücknehmen

Du hast selbst festgestellt, dass `dropped_failed` eine echte, nicht autorisierte Erweiterung von:

- ARCH §7.3 „Zähler – eingefroren“
- CONTRACTS §11.2 `LoggingHealthSnapshot`

darstellt.

Entferne deshalb `dropped_failed` vollständig wieder aus dem Produktstand.

Das umfasst insbesondere, soweit tatsächlich vorhanden:

- `LoggingHealthSnapshot`
- `LoggingInternalHealth`
- Ingress-/Worker-/Manager-Code
- Exports
- Tests
- Assertions
- Evidence-/Coverage-Aussagen
- sonstige Referenzen im aktiven OBS-030-Korrekturstand

Wichtig:

Die fachliche B-1-Korrektur bleibt bestehen.

Nach endgültigem Worker-Ausfall muss weiterhin mindestens gelten:

- Health → `FAILED_WORKER`
- `worker_errors` korrekt erhöht
- keine still beendete Worker-Schleife
- kein ungefilterter `threading`-Traceback
- `submit()` liefert nach endgültigem Worker-Ausfall nicht scheinbar erfolgreich `True`
- bereits in der Queue verbliebene Records werden beim vorgesehenen Shutdown-/Resteverfahren entsprechend dem bestehenden eingefrorenen Modell behandelt

Erfinde KEINEN Ersatzcounter.

Mappe die fehlgeschlagenen neuen Submits auch NICHT eigenmächtig auf `dropped_watermark`, `dropped_queue_full` oder einen anderen vorhandenen Counter, sofern die normativen Unterlagen dies nicht ausdrücklich verlangen.

Die verbleibende Auslegungsfrage zu ARCH §8.3 „nur verwerfen und zählen“ ist als offener Entscheidungsbedarf zu dokumentieren:

- Bedeutet dies zwingend einen eigenen Zähler für nach `FAILED_WORKER` abgewiesene neue Submits?
- Oder ist die bestehende eingefrorene Zählersemantik einschließlich der Behandlung bereits eingereihter Queue-Reste ausreichend?

Diese Frage jetzt NICHT selbst entscheiden.

---

# Korrektur 2 – `DR-OBS-030-01` aus der normativen Freeze-Datei zurücknehmen

Du hast selbst festgestellt, dass der Implementierungslauf:

- den vorgeschriebenen Schritt `anhalten` übersprungen hat,
- einen neuen offenen Status und einen neuen Abschnitt in einem FROZEN-Dokument eingeführt hat,
- damit selbst die normative Grundlage verändert hat, gegen die später geprüft werden soll.

Entferne daher ausschließlich den durch diesen Korrekturlauf eingeführten `DR-OBS-030-01`-Nachtrag bzw. Abschnitt wieder aus:

`LOGGING_DECISIONS_FREEZE_V1.md`

Stelle den Zustand dieser normativen Datei bezüglich dieses Eingriffs wieder so her, wie er vor RUN-OBS-030-02 war.

Keine anderen bestehenden Entscheidungen oder Inhalte dieser Freeze-Datei verändern.

Der Entscheidungsbedarf darf NICHT verschwinden.

Er muss weiterhin eindeutig und vollständig in der RUN-02-/Evidence-Dokumentation stehen, insbesondere mit:

- Ausgangsproblem,
- relevanter Formulierung aus ARCH §8.3,
- Konflikt mit dem eingefrorenen Zählersatz aus ARCH §7.3 / CONTRACTS §11.2,
- Hinweis, dass `dropped_failed` bewusst NICHT Bestandteil des finalen Implementierungsstands ist,
- Status: Entscheidung durch unabhängige Prüf-/Entscheidungsinstanz ausstehend.

Der Cleanup selbst darf diese Entscheidung nicht treffen.

---

# RUN-01-Evidence

Die nachträglich angehängten Korrekturvermerke in RUN-01-Evidence jetzt NICHT weiter verändern.

Sie sollen Gegenstand des unabhängigen Gate-Reviews bleiben.

Keine weitere Bereinigung, Entfernung oder Umformulierung dieser historischen Dateien durchführen.

---

# Tests

Passe ausschließlich die Tests an, die durch die Entfernung von `dropped_failed` zwingend betroffen sind.

Ergänze oder erhalte Tests, die weiterhin beweisen:

1. unerwartete Worker-Ausnahmen werden isoliert,
2. `worker_errors` steigt korrekt,
3. Health erreicht bei endgültigem Ausfall `FAILED_WORKER`,
4. nach endgültigem Ausfall liefert `submit()` `False`,
5. keine Records werden scheinbar erfolgreich angenommen und anschließend dauerhaft gestrandet,
6. kein ungefilterter Thread-Traceback entsteht,
7. Queue-Reste beim Shutdown werden gemäß bestehendem eingefrorenem Modell behandelt,
8. keine Regression der sonstigen OBS-030-Korrekturen.

Führe anschließend mindestens aus:

- komplette `-k obs030`-Suite,
- OBS-010 + OBS-020 + OBS-030,
- vollständige Client-Suite,
- die relevante Worker-Fault-Injection,
- `git diff --check`,
- `git status --short`,
- `git diff --stat`.

Bekannte vorbestehende Testfehler dürfen weiterhin nur dann als solche ausgewiesen werden, wenn sie erneut nachvollziehbar außerhalb des aktuellen Diffs liegen.

---

# Dokumentation

Aktualisiere ausschließlich die RUN-02-/aktiven Evidence- und Steuerungsunterlagen, soweit dies zur wahrheitsgemäßen Darstellung des finalen Cleanup-Zustands notwendig ist.

Dokumentiere ausdrücklich:

- `dropped_failed` wurde zurückgenommen, weil es eine nicht autorisierte Contract-Erweiterung war;
- `DR-OBS-030-01` wurde aus der normativen Freeze-Datei entfernt;
- die zugrunde liegende Auslegungsfrage bleibt offen und ist im Gate zu entscheiden;
- die eigentliche Worker-Failure-Korrektur B-1 bleibt vollständig bestehen.

`LOG_VERLAUF.md` bleibt append-only.

Historische Gate-FAIL-Dokumente nicht verändern.

OBS-030 Gate weiterhin NICHT selbst abhaken.

---

# Git

Kein Commit.
Kein Push.
Kein Merge.
Kein Rebase.
Kein Tag.
Kein PR.

---

# Abschluss

Liefere am Ende ausschließlich einen kompakten Cleanup-Bericht mit:

1. entfernten `dropped_failed`-Stellen,
2. Rücknahme von `DR-OBS-030-01`,
3. Nachweis, dass B-1 weiterhin vollständig funktioniert,
4. verbleibender offener Entscheidungsfrage zu „verwerfen und zählen“,
5. Teststand,
6. tatsächlich geänderten Dateien,
7. `git status --short`.

Abschlussstatus:

OBS-030 CLEANUP COMPLETED – READY FOR INDEPENDENT RE-REVIEW

Beginne nicht mit OBS-040.