# Fortsetzungsauftrag AP-IV2-020 – Reconnect-Audit einschließlich vollständiger Fehlerbehebung

Bitte setze den laufenden Umsetzungsauftrag **AP-IV2-020 / R01-UMSETZUNG** im bestehenden Arbeitskontext und auf demselben Paketbranch `work/client-v2/ap-iv2-020` fort.

Grundlage ist der dokumentierte Blocker `IV2-020-F01` einschließlich des vorhandenen Korrekturvorschlags und aller bereits erstellten Nachweise.

**Hiermit erteile ich ausdrücklich die Freigabe für die notwendigen, eng auf Reconnect/Recovery begrenzten Produktcode- und Teständerungen im bestehenden AP-IV2-020.**

Diese Freigabe umfasst sowohl die Behebung des bereits reproduzierten Fehlers `IV2-020-F01` als auch die unmittelbare Korrektur weiterer beim nachfolgenden Audit nachgewiesener, fachlich zusammenhängender Fehler.

### 1. Systematischer Reconnect-/Recovery-Audit

Prüfe vor den Änderungen die gesamte relevante Wiederverbindungskette:

- Settings-HTTP und Preflight
- WebSocket-Verbindungsaufbau und Wiederverbindung
- Hello, Admission und Settings-Bootstrap
- Commands, Acknowledgements und unklare Mutationsergebnisse
- ActivationMirror und Snapshot-Resynchronisation
- Audio-/Media-Lifecycle und Hardware-Recovery
- Runtime, manuelle Wiederverbindung, Backoff und Shutdown
- Zusammenspiel mehrerer gleichzeitiger oder aufeinanderfolgender Fehler

Unterscheide dabei zwischen vorhandenen funktionierenden Schutzmechanismen, bloßen Testlücken, plausiblen Risiken und tatsächlich nachgewiesenen Fehlern.

Untersuche insbesondere die Ursachenklasse des bestehenden Findings: temporäre Transport- und Serverfehler dürfen nicht unbegründet als permanente Konfigurationsfehler behandelt werden.

Berücksichtige auch HTTP-Fehlerantworten ohne gültigen JSON-Body, HTTP 408/429/5xx, Timeouts während des Bootstraps sowie wiederholte Serverneustarts.

### 2. Gefundene Fehler unmittelbar beheben

**Der Auftrag endet ausdrücklich nicht bei einer Analyse oder einem Korrekturvorschlag.**

Behebe den ursprünglichen Fehler `IV2-020-F01` und alle zusätzlich nachgewiesenen, innerhalb des beschriebenen Reconnect-/Recovery-Scopes liegenden Defekte direkt im selben Umsetzungslauf.

Dafür ist keine weitere Einzelgenehmigung erforderlich.

Arbeite ursachenorientiert und vermeide symptomatische Workarounds, pauschale Exception-Catches oder künstliche Erfolgszustände.

Erhalte insbesondere folgende Invarianten:

- Kein Audio und keine Triggerfreigabe vor erfolgreichem Bootstrap.
- Keine doppelte Ausführung unklarer mutierender Operationen.
- Keine ungeprüfte Wiederholung von Settings-PATCHes.
- Keine Vermischung verschiedener Sessions, Generationen oder Activation-IDs.
- Keine doppelte Textinjektion.
- Kein Verlust bestätigter Benutzerpräferenzen oder Run-Pausen.
- Kein unkontrolliertes Wachstum von Tasks, Buffern oder HTTP-Workern.
- Dauerhaft ungültige Konfigurationen und Protokollfehler bleiben korrekt blockierend.

Bereits funktionierende Mechanismen sollen nicht unnötig neu implementiert werden.

### 3. Testgetriebene Härtung

Erstelle für jeden behobenen Fehler zunächst einen gezielten, möglichst reproduzierbaren Fehlernachweis und anschließend eine dauerhafte Regression.

Prüfe nicht ausschließlich einzelne Methoden, sondern auch das reale Zusammenspiel der beteiligten Komponenten.

Führe insbesondere die relevanten Szenarien mit temporären HTTP-Ausfällen, Bootstrapabbrüchen, überlagerten Reconnects, wiederholten Serverneustarts, ausstehenden Commands und Shutdown während der Wiederherstellung durch.

Verwende für reale Integrationstests den bereits eingerichteten isolierten lokalen Server mit dem vorgeschriebenen gepinnten Serverstand.

Nach den Korrekturen sind die betroffenen Integrationstests, die vollständige Windows-Regression sowie alle erforderlichen Build-, Identitäts- und Produkt-/Server-Paarprüfungen am neuen endgültigen Produktstand zu wiederholen.

### 4. Grenzen der erteilten Freigabe

Diese Freigabe ist bewusst auf **Client-Reconnect, Recovery und unmittelbar notwendige Tests** begrenzt.

Nicht freigegeben sind:

- Ein grundlegender Architekturumbau oder umfassender Refactor.
- Fachlich unabhängige Produktänderungen.
- Serverproduktcodeänderungen oder Serverpromotion.
- Änderungen an Wire-Protokollen oder Sicherheitsinvarianten.
- Release, Tagging oder kanonische Übernahme.

Falls tatsächlich eine dieser Maßnahmen unvermeidlich sein sollte, dokumentiere den konkreten Grund und hole dafür eine gesonderte Entscheidung ein.

Alle anderen nachgewiesenen Fehler innerhalb des freigegebenen Bereichs sind ohne erneute Rückfrage zu beheben.

Dokumentiere die ausdrücklich erteilte Scope-Ausnahme gegenüber der ursprünglichen Qualifikationsplanung nachvollziehbar in der Paketakte.

### 5. Anschließend AP-IV2-020 vollständig fortsetzen

Nach erfolgreichem Audit, Korrektur und technischer Requalifikation sollst du **nicht erneut auf einen allgemeinen Fortsetzungsauftrag warten**.

Führe alle weiteren autonomen Arbeiten des ursprünglichen AP-IV2-020-Auftrags fort.

Danach folgen die bereits vorbereiteten gebündelten gemeinsamen Windows-/ReSpeaker-Realtests und die interaktive Kalibrierung von Wake-Word, Nachsprechzeit, Triggerverhalten, LED-/Soundfeedback, Overlay und sonstigen relevanten Timing- und Default-Werten.

Die bisherigen Vorprüfungen und Nachweise bleiben erhalten, werden aber nicht ungeprüft als Qualifikation des korrigierten Builds übernommen.

### 6. Workflow und Abschluss

Nutze weiterhin denselben R01-Umsetzungslauf, denselben Paketbranch und denselben kumulativen Draft-PR #15.

Dokumentiere den Audit, sämtliche Findings, Ursachen, Korrekturen, Regressionen und neuen Qualifikationsnachweise vollständig.

Kennzeichne behobene Findings erst dann als geschlossen, wenn ihre erforderlichen Nachweise erfolgreich sind.

Ein `REVIEW_READY` darf erst nach Erfüllung aller Pflichtkriterien von AP-IV2-020 gemeldet werden.

Kein Eigenreview, kein automatischer Merge und keine Änderung der vorgesehenen unabhängigen Abnahme.

**Ziel: Ein konsolidierter Audit mit unmittelbarer Behebung sämtlicher nachgewiesener, zusammenhängender Reconnect-/Recoveryfehler und anschließender vollständiger Realqualifikation – ohne unnötige weitere Freigabeschleifen.**

Beginne eigenständig mit dem Audit und gehe anschließend direkt in die Umsetzung der erforderlichen Korrekturen über.
