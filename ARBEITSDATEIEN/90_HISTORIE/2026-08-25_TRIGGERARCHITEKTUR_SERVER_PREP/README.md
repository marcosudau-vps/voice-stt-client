# Server-Prep-Provenienz 2026-08-25 (historisch)

```text
HISTORISCHE PREP-PROVENIENZ
NICHT NORMATIV
KEINE AP-ABNAHME
KEIN KANONISCHER PRODUKTSTAND

Bei Widerspruch gelten:
Entscheidungen / Frozen Contract / kanonische AP-Akten / Produktcode.
```

## Zweck

Dieser Ordner ist die dauerhaft versionierte, byteidentische Kopie der
textuellen Voranalyse- und Planungsstände, mit denen am 2026-08-25 die
Serverpakete `AP-SRV-040` bis `AP-SRV-070` vorbereitet wurden. Er wurde beim
kanonischen Abschluss von `AP-SRV-050` (2026-08-27) angelegt, damit diese
Provenienz nicht nur unversioniert im Arbeitsverzeichnis liegt.

Der Snapshot ersetzt **keine** Quelle. Er belegt ausschließlich, welche
Vorüberlegungen es zu welchem Zeitpunkt gab. Verbindlich sind allein:

- `10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`;
- `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md` und `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`;
- die kanonischen AP-Akten unter
  `docs/.archiv/einheitliche_triggerarchitektur/` im Serverrepository;
- der kanonische Produktcode.

Nicht aus diesem Ordner implementieren.

## Quelle

```text
P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur\_PREP\SERVER
```

Das Original bleibt unverändert bestehen; es wurde nicht gelöscht, verschoben
oder bereinigt. Die relative Struktur unterhalb von `_PREP\SERVER` ist hier
erhalten.

## Donor-Provenienz der Serverbranches

```text
AP-SRV-050 server prep branch:
prep/AP-SRV-050/settings-control
SHA  52a32daed8ffa44a36032cd7cef73ba231f25a52
Tree e852babe76663ac77a2454fc869f1292716a9d00

AP-SRV-060 server prep branch:
prep/AP-SRV-060/wakeword
SHA  1579b68d2e885ff3e3634318192ec03656e3b7ee
Tree 08ba91d702d4d920f4fbeb9c0f159bb1f94b9a9b
```

Der AP060-Prep-Verweis liegt in
`2026-08-25/AP-SRV-060/30_REVSION_IMPLEMENTATIONPLAN.md`.

## Umfang

19 Dateien übernommen (18 × `.md`, 1 × `.ps1`), byteidentisch geprüft:
Quelle und Ziel wurden nach der Kopie erneut gehasht, 0 Abweichungen. Die
Prüfsummen stehen in `SHA256SUMS.txt`, sortiert nach relativem Pfad.

Damit die Bytegleichheit auch nach Checkout erhalten bleibt, schaltet die
lokale `.gitattributes` (`* -text`) jede EOL-/Textnormalisierung für diesen
Ordner ab. Die Quelldateien verwenden CRLF; die repositoryweite Regel
`*.md text eol=lf` würde sie sonst umschreiben.

Keine Prep-Datei wurde inhaltlich geändert, korrigiert oder modernisiert.

`git diff --check` meldet für diesen Ordner Markdown-Hardbreak-Trailing-Spaces
und CRLF-Zeilenenden. Das ist beabsichtigt und wird bewusst hingenommen: Die
Byteidentität der archivierten Provenienz hat Vorrang vor kosmetischer
Whitespace-Bereinigung. Außerhalb dieses Ordners ist der Lauf sauber, geprüft
mit `git diff --cached --check -- . ":(exclude)<dieser Ordner>/**"`
(exit 0, keine Ausgabe). Die Bytegleichheit wurde zusätzlich gegen die
gestagten Git-Blobs verifiziert: 19/19 identisch.

## Bewusst nicht übernommen

```text
2026-08-25/AP-SRV-070_CLAUDE_PACKAGE.zip
2026-08-25/SERVER_PREP_PACKAGES_2026-08-25.zip
2026-08-25/SERVER_PREP_PACKAGES_2026-08-25_SHORTPATH.zip
```

Begründung: binäre Archive; übernommen wird ausschließlich textuelle
Provenienz. Ein Abgleich der Archivinhalte gegen die losen Dateien ergab:

- `AP-SRV-070_CLAUDE_PACKAGE.zip` – 3/3 Mitglieder byteidentisch zu den
  übernommenen Dateien;
- `SERVER_PREP_PACKAGES_2026-08-25.zip` – 12/15 byteidentisch; abweichend
  sind `00_README_START_HERE.md`, `00_SETUP_WORKTREES.ps1` und
  `99_MANIFEST.md`;
- `SERVER_PREP_PACKAGES_2026-08-25_SHORTPATH.zip` – 14/15 byteidentisch;
  abweichend ist `00_SETUP_WORKTREES.ps1`.

Diese vier abweichenden Archivvarianten sind bewusst **nicht** Teil des
Snapshots und nur im unveränderten Original unter `_PREP\SERVER` vorhanden.

Secrets, `venv`, Caches, Builds, Pytest-Temp, Modellgewichte, große
Binärdateien oder Logs waren im Quellordner nicht vorhanden. Eine Suche nach
Token-, Key- und Passwortmustern über alle übernommenen Dateien ergab nur
Treffer in Regeltexten („keine Secrets“, „Secret-Redaction“), keine echten
Geheimnisse.

## Inhalt

```text
2026-08-25/00_README_START_HERE.md
2026-08-25/00_SETUP_WORKTREES.ps1
2026-08-25/99_MANIFEST.md
2026-08-25/AP-SRV-040/   (Begleitnachricht, Prompt, Session-Start)
2026-08-25/AP-SRV-050/   (Begleitnachricht, Prompt, Session-Start)
2026-08-25/AP-SRV-060/   (Begleitnachricht, Prompt, Session-Start,
                          30_REVSION_IMPLEMENTATIONPLAN.md)
2026-08-25/AP-SRV-070/   (Begleitnachricht, Prompt, Session-Start)
2026-08-25/AP-SRV-070_CLAUDE_PACKAGE/ (Begleitnachricht, Session-Start,
                          Execution-Prompt)
```

Der Dateiname `30_REVSION_IMPLEMENTATIONPLAN.md` enthält einen Tippfehler der
Quelle und wurde bewusst nicht korrigiert.
