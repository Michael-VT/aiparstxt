# aiparstxt — Mehrsprachiger Text-Bereiniger & AI-Forensik-Analysator

Eine Sammlung von Kommandozeilen-Tools zur Textbereinigung durch Ersetzung unzulässiger Zeichen durch '?'. In 6 Sprachen implementiert für Leistungsvergleiche. Enthält AI-Wasserzeichen-Entfernung und **statistische Forensik-Analyse** zur Erkennung KI-generierter Texte.

## Funktionen

- **Textbereinigung** — Ersetzung unzulässiger Zeichen durch '?' in 6 Sprachimplementierungen
- **AI-Wasserzeichen-Entfernung** — Entfernung unsichtbarer Unicode-Zeichen, die von KI-Systemen eingefügt werden
- **AI-Forensik-Analytik** — Heuristische statistische Analyse zur Einschätzung der KI-Autorenschaft (Python)

---

## Erlaubte Zeichen

- Ziffern: 0-9
- Lateinische Buchstaben: A-Z, a-z
- Russische Buchstaben: А-Я, а-я (einschließlich Ё/ё)
- Satzzeichen und Symbole: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Leerzeichen: Leerzeichen, Tabulator, Zeilenumbruch

Alle anderen Zeichen werden durch '?' ersetzt.

## AI-Wasserzeichen-Entfernung

Der Bereiniger unterstützt die Entfernung unsichtbarer KI-Wasserzeichen, die von verschiedenen KI-Systemen zur Markierung generierter Texte verwendet werden:
- Zeichen mit Nullbreite (ZWSP, ZWNJ, ZWJ, ZWNBSP)
- Unsichtbare Formatierungszeichen (Word Joiner, Invisible Times usw.)
- Variationsselektoren
- Tag-Zeichen
- Bidirektionale Override-Zeichen

Siehe `ai-chart.txt` für eine vollständige Referenz.

---

## CLI-Verwendung — Textbereiniger (alle 6 Sprachen)

```
partxt <eingabedatei> [optionen]
```

Optionen:
  -o, --output <datei>      Ausgabedatei (Standard: <eingabe>.ed.txt)
  -r, --report <datei>      Berichtsdatei (Standard: report_<sprache>.txt)
  --no-edit                Keine .ed.txt-Datei erstellen
  --no-report              Keinen Bericht erstellen
  -w, --no-words           Worthäufigkeit nicht in Bericht aufnehmen
  --remove-watermark       KI-Wasserzeichen entfernen (versteckte/unsichtbare Zeichen)
  -h, --help               Hilfe anzeigen

### Einzeln

```bash
python3 partxtpy/partxt.py testdata/sample.txt
python3 partxtpy/partxt.py testdata/sample.txt --remove-watermark

cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt -- --remove-watermark

cd partxtgo && go run . testdata/sample.txt
cd partxtgo && go run . --remove-watermark testdata/sample.txt

cd partxtcpp && make && ./partxt testdata/sample.txt
cd partxtcpp && make && ./partxt testdata/sample.txt --remove-watermark

node partxtnode/partxt.js testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt --remove-watermark

bun run partxtjs/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt --remove-watermark
```

### Alle auf einmal

```bash
./run_all.sh testdata/sample.txt
```

---

## CLI-Verwendung — AI-Forensik-Analytik (nur Python)

```bash
python3 parscgptv2.py <textdatei>
```

Drei Varianten analytischer Skripte stehen im Projektverzeichnis zur Verfügung:

| Skript | Beschreibung |
|--------|--------------|
| `parscgpt.py` | Initialversion — grundlegende heuristische Metriken und KI-Score |
| `parscgptv1.py` | Erweitert — Stoppwort-Filterung, Konfidenzniveau, Interpretation, Erkennung verdächtiger Muster |
| `parscgptv2.py` | Vollversion — verfeinertes Scoring, saubere Ausgabe, empfohlen zur Verwendung |

### Berechnete Metriken

| Metrik | Beschreibung |
|--------|--------------|
| `lexical_diversity` | Einzigartige Wörter / Gesamtzahl der Wörter (nach Stoppwort-Entfernung) |
| `repetition_score` | Anteil der mehrfach vorkommenden Wörter |
| `entropy` | Shannon-Entropie der Worthäufigkeitsverteilung |
| `burstiness` | Variationskoeffizient der Satzlängen |
| `pattern_repetition_score` | Anteil wiederholter Satzlängenmuster (S/M/L-Kodierung) |
| `punctuation_density` | Anzahl Satzzeichen / Gesamtzeichen |
| `ai_phrase_hits` | Treffer mit 21 kuratierten KI-typischen Phrasen |
| `unicode_symbols` | Anzahl verdächtiger Unicode-Zeichen (Gedankenstrich, typografische Anführungszeichen usw.) |
| `top_bigrams` | Top-10-Bigramme aus gefiltertem Text |
| `top_trigrams` | Top-10-Trigramme aus gefiltertem Text |

### KI-Wahrscheinlichkeits-Scoring

| Bedingung | Punkte |
|-----------|--------|
| Lexikalische Diversität < 0.45 | +20 |
| Entropie < 5.0 | +20 |
| Burstiness < 0.35 | +15 |
| Musterwiederholung > 0.35 | +15 |
| Wiederholungsscore > 0.5 | +10 |
| KI-Phrasen-Treffer ≥ 3 | +15 |
| Satzzeichendichte > 0.04 | +5 |
| Verdächtige Unicode-Zeichen vorhanden | +5 |

**Gesamt** auf 100% begrenzt. Konfidenz: niedrig (<300 Wörter), mittel (300–999), hoch (≥1000).

### Ausgabe enthält

- Alle Rohmetriken mit gerundeten Werten
- `estimated_ai_probability` — heuristischer Score
- `confidence` — basierend auf Textlänge
- `interpretation` — lesbare Bewertung jeder Metrik
- `overall_profile` — Fazit und positive Signale
- `suspicious_patterns` — erkannte KI-ähnliche Phrasen und Trigramme

### Beispielausgabe

```
=== AI TEXT FORENSIC ANALYSIS ===

word_count: 198
sentence_count: 11
lexical_diversity: 0.832
entropy: 6.655
burstiness: 0.52
estimated_ai_probability: 0%
confidence: low
interpretation:
  lexical_diversity: High lexical diversity → richer and more human-like vocabulary.
  entropy: Moderate entropy.
  burstiness: Moderate burstiness.
overall_profile:
  verdict: Text statistically appears more human-like.
  signals: ['high lexical diversity']

=== END OF REPORT ===
```

---

## Portierung der Analytik in andere Sprachen

Die Analytik-Engine ist derzeit nur in Python verfügbar. Eine vollständige Portierungsanleitung finden Sie in **`ANALYTICS_RECOMMENDATIONS.md`**:
- Formeln zur Metrikberechnung
- Gewichte und Schwellenwerte des Scoring-Modells
- Interpretationsregeln
- Sprachspezifische Hinweise für Rust, Go, C++, Node.js, Bun

---

## Implementierungen

| Sprache   | Verzeichnis  | Build-Befehl                     | Berichtsdatei    |
|-----------|-------------|----------------------------------|------------------|
| Python    | partxtpy/   | (kein Build nötig)               | report_py.txt    |
| Rust      | partxtrs/   | cargo build --release            | report_rs.txt    |
| Go        | partxtgo/   | cd partxtgo && go build          | report_go.txt    |
| C++       | partxtcpp/  | make                             | report_cpp.txt   |
| Node.js   | partxtnode/ | (kein Build nötig)               | report_node.txt  |
| Bun       | partxtjs/   | (kein Build nötig)               | report_bun.txt   |

---

## Berichtsformat (Bereiniger)

Jeder Bericht enthält:
- Ausführungszeit
- Modus (Ersetzen/Entfernen + Wasserzeichen-Entfernungsstatus)
- Entfernte Wasserzeichen (mit Unicode-Codepunkten)
- Ersetzte Zeichen (mit Häufigkeit)
- Worthäufigkeitswörterbuch (aufsteigend sortiert)

---

## Beispielergebnisse (testdata/sample.txt, 197 Ersetzungen)

| Sprache | Ausführungszeit |
|---------|----------------|
| Go      | ~0.00004 s     |
| Rust    | ~0.00008 s     |
| C++     | ~0.00040 s     |
| Node.js | ~0.00046 s     |
| Python  | ~0.00056 s     |
| Bun     | ~0.00220 s     |

---

## Aktuelle Korrekturen (v0.2.0)

### Verbesserungen der Wasserzeichen-Entfernung

**Kritische Bugs bei der KI-Wasserzeichen-Erkennung in allen 4 Implementierungen behoben:**

1. **PUA-Range-Bug** — Unicode-Bereich von `E000-E007F` (573.343 Zeichen) auf `E000-E07F` (128 Zeichen) korrigiert
   - Wasserzeichen-Zeichensatz von 860.305 auf 259 Zeichen reduziert
   - Korrigiert in: Python, Go, Node.js, Rust

2. **Code-Point-Verarbeitung in Node.js** — `String.fromCharCode()` durch `String.fromCodePoint()` ersetzt
   - Erkannte zuvor 853 falsche Wasserzeichen (ASCII-Zeichen)
   - Erkennt nun korrekt 17 Wasserzeichen

3. **Flag-Position in Go** — Dokumentiert, dass Go Flags VOR dem Dateinamen erfordert
   ```bash
   # Korrekte Verwendung für Go:
   cd partxtgo && go run . --remove-watermark input.txt
   ```

### Testergebnisse (testdata/comprehensive_watermark_test.txt)

Alle Implementierungen erkennen nun korrekt **17/17 Wasserzeichen**:

| Sprache | Zeit (s) | Wasserzeichen entfernt |
|---------|----------|----------------------|
| Python  | 0.000560 | ✅ 17 (alle) |
| Go      | 0.000039 | ✅ 17 (alle) |
| Node.js | 0.000455 | ✅ 17 (alle) |
| Rust    | 0.000078 | ✅ 17 (alle) |

**Gesamte Wasserzeichen-Abdeckung:** ~270+ Codepoints

## Versionsverwaltung

- Patch (0.0.x): Fehlerbehebungen
- Minor (0.x.0): Voll funktional, entspricht Anforderungen
- Major (x.0.0): Erhebliche neue Funktionen

Aktuelle Version: 0.2.0

## Lizenz

MIT
