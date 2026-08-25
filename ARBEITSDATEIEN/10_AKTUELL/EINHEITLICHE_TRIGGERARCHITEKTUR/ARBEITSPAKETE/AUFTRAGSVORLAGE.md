# Vorlage – Ausführungsauftrag für ein Implementierungs-AP

Diese Vorlage wird unmittelbar vor dem Start eines Arbeitspakets konkret
ausgefüllt. Platzhalter oder unbestätigte Annahmen dürfen nicht an einen
Implementierungsagenten übergeben werden.

## 1. Laufmetadaten

```text
AP-ID:
Run-ID:
Agent/Lane:
Modell:
Repository (absolut):
Branch:
Start-SHA:
Freigegebene Dependency-SHAs:
Eigentumsbereich:
Verbotene Repositories/Pfade:
Commit nach PASS im Agentenlauf: ja
Push durch Agent: nein
Zielbranch: feat/einheitliche-triggerarchitektur
```

Der Agent ist nicht allein im Gesamtprojekt. Er darf fremde Änderungen nicht
zurücksetzen und muss ausschließlich im genannten Eigentumsbereich arbeiten.
Er beginnt kein Folge-AP.

## 2. Verbindliche Quellen

Vollständig zu lesen:

1. repositoryeigenes `AGENTS.md` und gegebenenfalls `CLAUDE.md`;
2. der konkrete Auftrag;
3. die ausdrücklich genannten Abschnitte aus Zielbild, Contract-Freeze,
   Wire-Schema und Implementierungsplan;
4. die genannten aktuellen Produktmodule, direkten Abhängigkeiten und Tests.

Nicht verwenden:

- `IDEEN/` und insbesondere Namespace-Unterlagen;
- historische Planungen als aktuelle Sollquelle;
- Chatannahmen, die dem eingefrorenen Contract widersprechen.

## 3. Zielzustand

```text
[Ein eindeutiger, beobachtbarer Endzustand in wenigen Sätzen.]
```

## 4. Wiederzuverwendender Ist-Stand

```text
[Konkrete vorhandene Klassen, Module, Tests und Mechanismen, die erhalten oder
gezielt umgebaut werden sollen. Keine pauschale Neuimplementierung.]
```

## 5. Scope und Dateiownership

Zu ändern/anzulegen:

```text
[Module und fachliche Verantwortungsbereiche]
```

Nicht-Ziele:

```text
[Explizite Grenzen, spätere APs, verbotene Refactors]
```

## 6. Umsetzungsauftrag

```text
[Kleine nummerierte Liste der geforderten Änderungen.]
```

Bei einer echten, bisher nicht entschiedenen Nutzerwirkung stoppt der Agent
und meldet `BLOCKED`. Eine technische Detailentscheidung innerhalb des
Contracts wird klein, testbar und dokumentiert getroffen.

## 7. Schnittstellenvertrag

```text
[Exakte Commands, Events, Payloadfelder, Enums, IDs, Fehlercodes und
Contract-Vektoren, die dieses AP produziert oder konsumiert.]
```

Keine Umbenennung oder additive Semantik ohne ausdrückliche Freigabe. Bei
einem Widerspruch zwischen Zielcode und Vertrag wird nicht stillschweigend
eine Seite angepasst, sondern der Befund gemeldet.

## 8. Tests und Akzeptanzkriterien

```text
[PASS/FAIL-fähige Kriterien]
[Fokussierte Testbefehle]
[Vollständige Repositorysuite]
[Build/Typecheck/Lint, soweit vorhanden]
[Race-/Replay-/Fault-/Clock-Tests, soweit einschlägig]
```

Der Agent debuggt iterativ, bis fokussierte und vollständige Tests grün sind.
Bekannte Flakes werden mit Reproduktion und Wiederholungszahl dokumentiert,
nicht verschwiegen.

## 9. Dokumentationsauftrag

Dokumentation gehört zum Scope dieses APs. Der Agent muss:

- die im Auftrag genannten kanonischen Produktdokumente im eigenen Repository
  an den tatsächlich implementierten Stand anpassen;
- neue öffentliche Konfiguration, Wire-Felder, Zustände, Recoveryregeln und
  Migrationsgrenzen unmittelbar dokumentieren;
- repositoryeigene Fortschritts-/Übergabedokumente und vorgeschriebene
  Aktionsarchive aktualisieren;
- keine normative zentrale Planungsentscheidung eigenmächtig ändern;
- im Report jede Dokumentänderung mit Zweck nennen.

Erwartete Dokumentziele:

```text
[Konkrete Dateien/Abschnitte für dieses AP]
```

## 10. Abschluss und Commit

Vor dem Commit:

1. `git diff --check`;
2. fokussierte Tests und vollständige Suite;
3. `git status --short` prüfen;
4. nur AP-eigene Dateien explizit stagen, niemals blind `git add -A`;
5. dedizierten Commit mit AP-ID erstellen.

Der Commit bleibt lokal. Der Agent pusht nicht. Bei einem späteren
Abnahmebefund wird derselbe Commit nach der Korrektur amended, bis genau ein
finaler AP-Commit vorliegt.

Wenn fremde Änderungen nicht sicher trennbar sind, nicht committen und
`BLOCKED` melden.

## 11. Verbindliches Rückgabeformat

```text
Status: PASS | FAIL | BLOCKED
AP / Run:
Start-SHA:
End-/Commit-SHA:

Implementiert:
- ...

Geänderte Produktdokumentation:
- Datei: Zweck

Tests:
- Befehl: Ergebnis

Contract-/Akzeptanznachweis:
- Kriterium: Nachweis

Abweichungen, Flakes, Risiken:
- keine | ...

Working-Tree-Status:
- ...

Hinweise für die Endabnahme:
- ...
```

Der Agent stoppt danach und wartet auf PASS oder eine konkrete
Korrekturrückgabe der Koordination.
