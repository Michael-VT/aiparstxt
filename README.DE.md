# aiparstxt — Mehrsprachiger Text-Bereiniger & AI-Forensik-Analysator

Eine Sammlung von Kommandozeilen-Tools zur Textbereinigung durch Ersetzung unzulässiger Zeichen durch '?'. In 6 Sprachen implementiert für Leistungsvergleiche. Enthält AI-Wasserzeichen-Entfernung und **statistische Forensik-Analyse** zur Erkennung KI-generierter Texte.

**🌍 Online ausprobieren (keine Installation, läuft im Browser):** <https://michael-vt.github.io/aiparstxt/> — Text einfügen, Bewertung und die genauen KI-typischen Stellen erhalten (Oberfläche DE-frei: EN/RU/UA/PT).

**Verfügbar in:** [English](README.md) | [Русский](README.RU.md) | [Українська](README.UA.md) | [Português](README.PT.md) | [Français](README.FR.md) | [Deutsch](README.DE.md)


## Funktionen

- **Textbereinigung** — Ersetzung unzulässiger Zeichen durch '?' in 6 Sprachimplementierungen
- **AI-Wasserzeichen-Entfernung** — Entfernung unsichtbarer Unicode-Zeichen, die von KI-Systemen eingefügt werden
- **AI-Forensik-Analytik** — Heuristische statistische Analyse zur Einschätzung der KI-Autorenschaft (Python)
- **Erweiterte Erkennungsversionen** — verbesserte forensische Analyse verfügbar für alle 6 Sprachen ⭐

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

## CLI — Textbereiniger (alle 6 Sprachen)

```bash
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
# Standardversionen
python3 partxtpy/partxt.py testdata/sample.txt
python3 partxtpy/partxt.py testdata/sample.txt --remove-watermark

# Erweiterte Versionen mit AI-Forensik-Analyse ⭐
python3 partxtpy/partxt-ext.py testdata/sample.txt
python3 partxtpy/partxt-ext.py testdata/sample.txt --remove-watermark

cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext -- testdata/sample.txt -- --remove-watermark

cd partxtgo && go run . testdata/sample.txt
cd partxtgo && go run main-ext.go testdata/sample.txt --remove-watermark

cd partxtcpp && make && ./partxt testdata/sample.txt
cd partxtcpp && make && ./partxt-ext testdata/sample.txt --remove-watermark

node partxtnode/partxt.js testdata/sample.txt
node partxtnode/partxt-ext.js testdata/sample.txt --remove-watermark

bun run partxtjs/partxt.js testdata/sample.txt
bun run partxtjs/partxt-ext.js testdata/sample.txt --remove-watermark
```

### Alle auf einmal

```bash
# Nur Standardversionen
./run_all.sh testdata/sample.txt

# Erweiterte Versionen mit KI-Erkennung
./run_all_extended.sh testdata/sample.txt
```

---

## CLI — AI-Forensik-Analytik (nur Python)

### Standard Python-Analysatoren

```bash
python3 parscgptv2.py <textdatei>
```

Drei Varianten analytischer Skripte stehen im Projektverzeichnis zur Verfügung:

| Skript | Metriken | KI-Phrasen | Funktionen | Empfohlene Verwendung |
|--------|----------|-----------|-------------|----------------------|
| `parscgpt.py` | 8 Basis | 21 | Nur Basismetriken | Legacy/Testen |
| `parscgptv1.py` | 8 Basis + Interpretation | 21 | + Stoppwörter, Konfidenz | Basis-Erkennung |
| `parscgptv2.py` | 8 Basis + verfeinerte Interpretation | 21 | + Saubere Ausgabe | **Standard-Erkennung** ✅ |
| `parscgpt-ext.py` | **17 erweiterte Metriken** | **70+** | + Linguistische Analyse, gewichtete Bewertung | **Erweiterte Erkennung** ⭐ |

### Integrierte Erweiterte Analysatoren (Alle 6 Sprachen) ⭐

Erweiterte Versionen der grundlegenden Textbereiniger (`partxt-ext`) sind nun für **alle 6 Sprachimplementierungen** mit verbesserter AI-Forensik-Analyse verfügbar:

| Sprache | Erweitertes Binary | Berichtsdatei | Funktionen |
|----------|-------------------|---------------|-----------|
| Python | `partxtpy/partxt-ext.py` | report_py-ext.txt | 11 Kernmetriken + KI-Wahrscheinlichkeitsbewertung |
| Rust | `partxtrs/target/partxt-ext` | report_rs-ext.txt | Gleiche Metriken wie Python, kompilierte Leistung |
| Go | `partxtgo/main-ext.go` | report_go-ext.txt | Gleiche Metriken, kompilierte Leistung |
| C++ | `partxtcpp/partxt-ext` | report_cpp-ext.txt | Gleiche Metriken, kompilierte Leistung |
| Node.js | `partxtnode/partxt-ext.js` | report_node-ext.txt | Gleiche Metriken, JavaScript-Laufzeit |
| Bun | `partxtjs/partxt-ext.js` | report_bun-ext.txt | Gleiche Metriken, optimiertes JavaScript |

**Verbesserte Funktionen in Erweiterten Versionen:**
- 11 Kern-AI-Forensik-Metriken (lexikalische Vielfalt, Entropie, Burstiness, Musterwiederholung usw.)
- KI-Phrase-Erkennung mit 70+ verdächtigen Phrasen
- Unicode-verdächtige Zeichenerkennung
- Statistische KI-Wahrscheinlichkeitsbewertung (0-100%)
- Konfidenzniveaus (NIEDRIG/MITTEL/HOCH) basierend auf Textlänge
- Detaillierte Signalanalyse mit visuellen Indikatoren
- Interpretation jeder Metrik mit umsetzbaren Erkenntnissen

---

## Standardmetriken (Alle Erweiterten Versionen)

| Metrik | Beschreibung | KI-Erkennungswert |
|--------|-------------|-------------------|
| `lexical_diversity` | Einzigartige Wörter / Gesamtzahl der Wörter (nach Stoppwort-Entfernung) | KI hat geringere Vielfalt |
| `repetition_score` | Anteil der mehrfach vorkommenden Wörter | KI wiederholt mehr |
| `entropy` | Shannon-Entropie der Worthäufigkeitsverteilung | KI hat unnatürlich gleichmäßige Verteilung |
| `burstiness` | Variationskoeffizient der Satzlängen | KI hat übermäßig einheitliche Satzstruktur (Hauptsignal) |
| `paragraph_length_cv` | Variationskoeffizient der Absatzlängen (Wortanzahl) | KI-Absätze sind unnatürlich gleich lang (Hauptsignal) |
| `joint_uniformity` | Sowohl Satz- als auch Absatz-CV niedrig | Stärkstes strukturelles KI-Signal |
| `connective_density` | Diskurs-Konnektive pro Satz (mehrsprachig) | KI verwendet übermäßig Konnektive |
| `pattern_repetition` | Anteil wiederholter Satzlängenmuster | KI verwendet Vorlagenmuster |
| `punctuation_density` | Anzahl Satzzeichen / Gesamtzeichen | KI verwendet möglicherweise übermäßig Satzzeichen |
| `ai_phrase_hits` | ~150 kuratierte KI-typische Phrasen in 3 Stufen (EN/RU/UK/PT) | Direkte KI-Signatur |
| `unicode_symbols` | Anzahl verdächtiger Unicode-Zeichen | Technische KI-Marker |
| `avg_word_length` | Durchschnittliche Wortlänge | KI verwendet einfacheren Wortschatz |
| `word_length_variance` | Varianz der Wortlängen | KI-Texte einheitlicher |
| `confidence` | Basierend auf Wortanzahl (NIEDRIG <300, MITTEL 300-999, HOCH ≥1000) | Zuverlässigkeitsindikator |

### Fundstellen im Text — AI EVIDENCE (v0.4.0+)

Jeder ausgelöste Indikator wird mit seiner genauen Fundstelle im Text gemeldet:
Zeilennummer, ein Ausschnitt mit hervorgehobenem Auslöser als `>>>Phrase<<<`
sowie Sequenzen der Satz-/Absatzlängen bei Gleichförmigkeits-Signalen. Die
Sektion `AI EVIDENCE` erscheint in den Berichten der erweiterten Bereiniger
und in der Ausgabe von `parscgpt-ext.py`.

### Ehrliche Enthaltung (v0.4.1–v0.4.3)

- Kurze Texte (< 150 Wörter oder < 5 Sätze): Struktursignale werden nach
  statistischer Zuverlässigkeit skaliert, statt still abgeschaltet zu werden;
  das Verdikt erhält den Vermerk „Verdikt unzuverlässig" — keine selbstbewussten
  „menschlich"-Verdikte mehr bei Texten, die für eine Analyse zu klein sind.
- Wiederholung von Vorlagen-Überschriften (v0.4.2): wörtlich wiederholte kurze
  Kopfzeilen („Что верно" ×7, „Итог" ×7) — ein starkes Merkmal strukturierter
  LLM-Antworten; null Fehlalarme im Human-Korpus.
- Werbe-/Social-Media-Register (v0.4.3): Texte mit vielen Emojis und
  Ausrufezeichen erhalten einen Genre-Hinweis statt eines „menschlich"-Verdikts —
  dieses Register liefern sowohl KI als auch menschliche SMM-Texter, daher
  werden keine KI-Punkte vergeben, das Verdikt wird einfach zurückgehalten.

### Online-Demo (GitHub Pages)

Die Browser-Version liegt in [`docs/`](docs/): Text einfügen — Bewertung, Verdikt und Fundstellen; alles läuft lokal im Browser. Veröffentlichung: Settings → Pages → main / `/docs`.

### Analyse einer Datei mit allen Detektoren

```bash
./analyze_all.sh input.txt
```

Kompiliert fehlende Binaries, führt alle Analysatoren des Projekts aus
(technisch, Legacy ×2, Standard, erweitert, markerbasiert sowie alle sechs
`partxt-ext`), prüft die Parität der Implementierungen und druckt einen
zusammenfassenden Bericht: Konsens, Worst-Case (strengster Analysator),
Risikobereich und die Liste der Stellen, die vor der Veröffentlichung
bearbeitet werden sollten.

### Validierung (v0.4.0+)

Kalibriert und validiert an 34 bestätigten KI-Antworten (8 Dienste × 4 Sprachen)
und 20 quellenbasierten Human-Texten — siehe `validation/AI_CORPUS_REPORT.md`
und `AI_SIGNALS_SPEC.md`. Bei Klassifikationsschwelle 50: Recall 93,9%,
Fehlalarmrate 0%. Die Scores sind heuristisch und kein Autorschaftsnachweis.

### KI-Wahrscheinlichkeitsbewertung (Erweiterte Versionen)

| Bedingung | Punkte | Verbesserung |
|-----------|--------|-------------|
| Lexikalische Vielfalt < 0.45 | **+25** | ↑ +5 vs Standard |
| Entropie < 5.0 | **+25** | ↑ +5 vs Standard |
| Burstiness < 0.35 | **+20** | ↑ +5 vs Standard |
| Musterwiederholung > 0.35 | **+20** | ↑ +5 vs Standard |
| KI-Phrasen-Treffer ≥ 3 | **+20** | ↑ +5 vs Standard |
| Wiederholungsscore > 0.5 | +15 | Gleich |
| Satzzeichendichte > 0.04 | +5 | Gleich |
| Verdächtige Unicode-Zeichen vorhanden | +5 | Gleich |
| Durchschnittliche Wortlänge < 4.0 | **+10** | 🆕 Neue Metrik |
| Wortlängenvarianz < 1.5 | **+8** | 🆕 Neue Metrik |

**Gesamt** auf 100% begrenzt mit Konfidenzfaktor-Anpassung (80%-100% basierend auf Textlänge).

### Ausgabeformat (Erweiterte Versionen)

```
======================================================================
aiparstxt-ext — Verbesserter AI-Forensik-Analysator-Bericht
======================================================================

Eingabedatei:  sample.txt
Ausgabedatei: sample.ed.txt
Ausführungszeit: 0.000560s

--- AI Watermark Analysis ---
Entfernte Wasserzeichenzeichen: 17
Entfernte Wasserzeichenzeichentypen:
  U+200B: 5
  U+200C: 3
  ...

--- Ersetzte Zeichen ---
Ersetzte Zeichen: 197

======================================================================
AI FORENSIC ANALYSIS
======================================================================

Gesamturteil: Mittlere Wahrscheinlichkeit der KI-Beteiligung (35.2%)
Konfidenzniveau: MITTEL

Detaillierte Metriken:
  Wortanzahl:            198
  Satzzahl:        11
  Lexikalische Vielfalt:     0.832
  Wiederholungsscore:      0.202
  Entropie:               6.655
  Burstiness:            1.590
  Musterwiederholung:    0.000
  Satzzeichendichte:   0.037
  KI-Phrasen-Treffer:        2
  Verdächtig Unicode:    0
  Durchschnittliche Wortlänge:       4.52
  Wortlängenvarianz:  2.18

Signalanalyse:
  ✓ Hohe lexikalische Vielfalt - reiche Wortschatzvariation
  ✓ Gute Entropie - natürliche Wortverteilung
  ✓ Gute Burstiness - natürliche Satzvariation
  ⚠️ 2 KI-typische Phrasen gefunden
```

---

## Erweiterte Metriken (nur parscgpt-ext.py) ⭐

Für die umfassendste Analyse bietet der eigenständige `parscgpt-ext.py` 17 erweiterte Metriken:

| Metrik | Beschreibung | KI-Erkennungswert |
|--------|-------------|-------------------|
| `avg_word_length` | Durchschnittliche Wortlänge | KI verwendet einfacheren Wortschatz |
| `word_length_variance` | Varianz der Wortlängen | KI-Texte einheitlicher |
| `pronoun_ratio` | Verhältnis von Pronomen zur Gesamtzahl der Wörter | KI verwendet übermäßig Pronomen |
| `readability_score` | Flesch-Lesbarkeits-Score | KI-Texte "zu lesbar" |
| `passive_voice_density` | Häufigkeit von Passivkonstruktionen | KI bevorzugt Passiv |
| `adj_noun_pair_diversity` | Einzigartige Adjektiv-Substantiv-Kombinationen | KI hat begrenzte Kombinationen |
| `structural_uniformity` | Wiederholung von Satzanfangsmustern | KI verwendet Vorlagen |
| `quantifier_overuse` | Häufigkeit von Qualifizierer-Wörtern | KI verwendet übermäßig Qualifizierer |

Verwenden Sie `parscgpt-ext.py`, wenn Sie die tiefste linguistische Analyse über die integrierten Bereiniger hinaus benötigen.

**Hauptunterschiede: Erweiterte vs Standard-Versionen**
- Bietet **9 zusätzliche Metriken** für tiefere Analyse
- Zeigt **detaillierte Bewertung** anstelle einer einzelnen Wahrscheinlichkeit
- Enthält **spezifische Interpretation** für jede Metrik
- Bietet **verbesserte Zuverlässigkeit** mit Anpassung an Textlänge
- Erkennt **mehr KI-Muster** — 70+ Phrasen vs 21 in Standard-Version

---

## Portierung der Analytik in andere Sprachen

Die verbesserte Analyse-Engine ist nun in **allen 6 Sprachimplementierungen** über die `-ext`-Versionen verfügbar. Der eigenständige Python `parscgpt-ext.py` bietet die umfassendste 17-Metrik-Analyse als Referenz.

Siehe **`ANALYTICS_RECOMMENDATIONS.md`** für einen vollständigen Portierungsleitfaden mit:
- Metrik-Berechnungsformeln
- Gewichte und Schwellenwerte des Bewertungsmodells
- Interpretationsregeln
- Sprachspezifische Anleitung

---

## Implementierungen

| Sprache   | Verzeichnis  | Build-Befehl                     | Berichtsdatei    | Erweiterter Bericht  |
|-----------|-------------|----------------------------------|------------------|---------------------|
| Python    | partxtpy/   | (kein Build nötig)               | report_py.txt    | report_py-ext.txt   |
| Rust      | partxtrs/   | cargo build --release            | report_rs.txt    | report_rs-ext.txt   |
| Go        | partxtgo/   | cd partxtgo && go build          | report_go.txt    | report_go-ext.txt   |
| C++       | partxtcpp/  | make                             | report_cpp.txt   | report_cpp-ext.txt  |
| Node.js   | partxtnode/ | (kein Build nötig)                | report_node.txt  | report_node-ext.txt |
| Bun       | partxtjs/   | (kein Build nötig)                | report_bun.txt   | report_bun-ext.txt  |

---

## Berichtsformat (Bereiniger)

Jeder Bericht enthält:
- Ausführungszeit
- Modus (Ersetzen/Entfernen + Wasserzeichen-Entfernungsstatus)
- Entfernte Wasserzeichen (mit Unicode-Codepunkten)
- Ersetzte Zeichen (mit Häufigkeit)
- Worthäufigkeitswörterbuch (aufsteigend sortiert)

**Erweiterte Versionen** enthalten zusätzlich:
- AI-Forensik-Metrik-Sektion
- KI-Wahrscheinlichkeitsbewertung mit Konfidenzniveau
- Signalanalyse mit visuellen Indikatoren
- Metrik-spezifische Interpretationen

---

## Beispielergebnisse (testdata/sample.txt, 197 Ersetzungen)

| Sprache | Ausführungszeit | Erweiterte Zeit |
|---------|----------------|-----------------|
| Go      | ~0.00004 s     | ~0.00006 s      |
| Rust    | ~0.00008 s     | ~0.00010 s      |
| C++     | ~0.00040 s     | ~0.00050 s      |
| Node.js | ~0.00046 s     | ~0.00060 s      |
| Python  | ~0.00056 s     | ~0.00070 s      |
| Bun     | ~0.00220 s     | ~0.00280 s      |

---

## Aktuelle Korrekturen (v0.3.0)

### Neue Erweiterte Versionen ⭐

**Verbesserte AI-Forensik-Analyse nun in allen 6 Sprachen verfügbar:**

1. **Python Extended** (`partxtpy/partxt-ext.py`)
   - Vollständige AI-Forensik-Metrik-Integration
   - Wahrscheinlichkeitsbasierte Bewertung
   - Signalanalyse mit Interpretationen

2. **JavaScript Extended** (Bun + Node.js)
   - `partxtjs/partxt-ext.js` für Bun
   - `partxtnode/partxt-ext.js` für Node.js
   - Gleiche Metriken wie Python-Version

3. **Rust Extended** (`partxtrs/src/main-ext.rs`)
   - Kompillierte Leistung
   - Effiziente Speicherverarbeitung
   - Vollständiger Metrik-Satz

4. **Go Extended** (`partxtgo/main-ext.go`)
   - Typsichere Implementierung
   - Nur Standardbibliothek
   - Umfassende Metriken

5. **C++ Extended** (`partxtcpp/partxt-ext.cpp`)
   - Hohe Leistung
   - Modernes C++20
   - Vollständige Funktionalität

6. **Node.js Extended** (`partxtnode/partxt-ext.js`)
   - Node.js-Kompatibilität
   - Gleiche Metriken und Funktionen

---

## Versionsverwaltung

- Patch (0.0.x): Fehlerbehebungen
- Minor (0.x.0): Voll funktional, entspricht Anforderungen
- Major (x.0.0): Erhebliche neue Funktionen

Aktuelle Version: 0.4.3

## Lizenz

MIT