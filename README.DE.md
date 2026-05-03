# aiparstxt — Mehrsprachiger Text-Bereiniger

Eine Sammlung von Kommandozeilen-Tools zur Textbereinigung durch Ersetzung unzulässiger Zeichen durch '?'. In 6 Sprachen implementiert für Leistungsvergleiche.

## Erlaubte Zeichen
- Ziffern: 0-9
- Lateinische Buchstaben: A-Z, a-z
- Russische Buchstaben: А-Я, а-я (einschließlich Ё/ё)
- Satzzeichen und Symbole: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Leerzeichen: Leerzeichen, Tabulator, Zeilenumbruch

Alle anderen Zeichen werden durch '?' ersetzt.

## CLI-Verwendung (gleich für alle Sprachen)

partxt <eingabedatei> [optionen]

Optionen:
  -o, --output <datei>   Ausgabedatei (Standard: <eingabe>.ed.txt)
  -r, --report <datei>   Berichtsdatei (Standard: report_<sprache>.txt)
  --no-edit             Keine .ed.txt-Datei erstellen
  --no-report           Keinen Bericht erstellen
  -w, --no-words        Worthäufigkeit nicht in Bericht aufnehmen
  -h, --help            Hilfe anzeigen

## Berichtsformat
Jeder Bericht enthält:
- Ausführungszeit
- Tabelle der ersetzten Zeichen mit Häufigkeit
- Worthäufigkeitswörterbuch (aufsteigend sortiert)

## Implementierungen

| Sprache   | Verzeichnis  | Build-Befehl                     | Berichtsdatei    |
|-----------|-------------|----------------------------------|------------------|
| Python    | partxtpy/   | (kein Build nötig)               | report_py.txt    |
| Rust      | partxtrs/   | cargo build --release            | report_rs.txt    |
| Go        | partxtgo/   | cd partxtgo && go build          | report_go.txt    |
| C++       | partxtcpp/  | make                             | report_cpp.txt   |
| Node.js   | partxtnode/ | (kein Build nötig)               | report_node.txt  |
| Bun       | partxtjs/   | (kein Build nötig)               | report_bun.txt   |

## Ausführung

### Einzeln
python3 partxtpy/partxt.py testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cd partxtgo && go run . testdata/sample.txt
cd partxtcpp && make && ./partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt

### Alle auf einmal
./run_all.sh testdata/sample.txt

## Beispielergebnisse (testdata/sample.txt, 197 Ersetzungen)

| Sprache | Ausführungszeit |
|---------|----------------|
| Go      | ~0.0001 s      |
| Rust    | ~0.0003 s      |
| C++     | ~0.0004 s      |
| Python  | ~0.0014 s      |
| Node.js | ~0.0013 s      |
| Bun     | ~0.0022 s      |

## Versionsverwaltung
- Patch (0.0.x): Fehlerbehebungen
- Minor (0.x.0): Voll funktional, entspricht Anforderungen
- Major (x.0.0): Erhebliche neue Funktionen

Aktuelle Version: 0.0.0

## Lizenz
MIT
