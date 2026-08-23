# aiparstxt — Multi-language Text Sanitizer & AI Forensic Analyzer

A set of command-line utilities that sanitize text files by replacing disallowed characters with '?'. Implemented in 6 languages for performance comparison. Includes AI watermark removal and **statistical forensic analysis** for detecting AI-generated text.

**Available in:** [English](README.md) | [Русский](README.RU.md) | [Українська](README.UA.md) | [Português](README.PT.md) | [Français](README.FR.md) | [Deutsch](README.DE.md)


## Features

- **Text sanitization** — replace disallowed characters with '?' across 6 language implementations
- **AI watermark removal** — strip invisible Unicode watermarks inserted by AI systems
- **AI forensic analytics** — heuristic statistical analysis to estimate AI authorship probability (Python)

---

## Allowed Characters

- Digits: 0-9
- Latin letters: A-Z, a-z
- Russian letters: А-Я, а-я (including Ё/ё)
- Punctuation and symbols: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Whitespace: space, tab, newline

All other characters are replaced with '?'.

## AI Watermark Removal

The sanitizer supports removal of invisible AI watermark characters used by various AI systems to mark generated text:
- Zero-width characters (ZWSP, ZWNJ, ZWJ, ZWNBSP)
- Invisible formatting characters (Word Joiner, Invisible Times, etc.)
- Variation selectors
- Tag characters
- Bidirectional override characters

See `ai-chart.txt` for complete reference.

---

## CLI Usage — Text Sanitizer (all 6 languages)

```
partxt <input_file> [options]
```

Options:
  -o, --output <file>       Output file (default: <input>.ed.txt)
  -r, --report <file>       Report file (default: report_<lang>.txt)
  --no-edit                 Do not create .ed.txt file
  --no-report               Do not create report file
  -w, --no-words            Exclude word frequency from report
  --remove-watermark        Remove AI watermark characters (hidden/invisible)
  -h, --help                Show help

### Individual

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

### All at once

```bash
./run_all.sh testdata/sample.txt
```

---

## CLI Usage — AI Forensic Analytics (Python only)

```bash
python3 parscgptv2.py <textfile>
```

Three analytical script variants are available in the project root:

| Script | Description |
|--------|-------------|
| `parscgpt.py` | Initial version — basic heuristic metrics and AI score |
| `parscgptv1.py` | Extended — adds stopword filtering, confidence level, interpretation, suspicious pattern detection |
| `parscgptv2.py` | Full version — refined scoring, clean output, recommended for use |

### Metrics Computed

| Metric | Description |
|--------|-------------|
| `lexical_diversity` | Unique words / total words (after stopword removal) |
| `repetition_score` | Fraction of words appearing more than once |
| `entropy` | Shannon entropy of word frequency distribution |
| `burstiness` | Coefficient of variation of sentence lengths |
| `pattern_repetition_score` | Fraction of repeated sentence-length patterns (S/M/L encoding) |
| `punctuation_density` | Punctuation count / total characters |
| `ai_phrase_hits` | Matches against 21 curated AI-typical phrases |
| `unicode_symbols` | Count of suspicious Unicode characters (em-dash, smart quotes, etc.) |
| `top_bigrams` | Top 10 bigrams from filtered text |
| `top_trigrams` | Top 10 trigrams from filtered text |

### AI Probability Scoring

| Condition | Points |
|-----------|--------|
| Lexical diversity < 0.45 | +20 |
| Entropy < 5.0 | +20 |
| Burstiness < 0.35 | +15 |
| Pattern repetition > 0.35 | +15 |
| Repetition score > 0.5 | +10 |
| AI phrase hits ≥ 3 | +15 |
| Punctuation density > 0.04 | +5 |
| Unicode suspicious chars present | +5 |

**Total** capped at 100%. Confidence: low (<300 words), medium (300-999), high (≥1000).

### Output includes

- All raw metrics with rounded values
- `estimated_ai_probability` — heuristic score
- `confidence` — based on text length
- `interpretation` — human-readable verdict for each metric
- `overall_profile` — verdict and positive signals
- `suspicious_patterns` — detected AI-like phrases and trigrams

### Example output

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

## Porting Analytics to Other Languages

The analytics engine is currently Python-only. See **`ANALYTICS_RECOMMENDATIONS.md`** for a complete porting guide with:
- Metric computation formulas
- Scoring model weights and thresholds
- Interpretation rules
- Language-specific guidance for Rust, Go, C++, Node.js, Bun

---

## Implementations

| Language   | Directory    | Build command                    | Report file      |
|------------|-------------|----------------------------------|------------------|
| Python     | partxtpy/   | (no build needed)                | report_py.txt    |
| Rust       | partxtrs/   | cargo build --release            | report_rs.txt    |
| Go         | partxtgo/   | cd partxtgo && go build          | report_go.txt    |
| C++        | partxtcpp/  | make                             | report_cpp.txt   |
| Node.js    | partxtnode/ | (no build needed)                | report_node.txt  |
| Bun        | partxtjs/   | (no build needed)                | report_bun.txt   |

---

## Report Format (Sanitizer)

Each report includes:
- Execution time
- Mode (replace/remove + watermark removal status)
- Watermark characters removed (with Unicode code points)
- Replaced characters (with counts)
- Word frequency (ascending)

---

## Sample Results (testdata/sample.txt, 197 replacements)

| Language | Execution Time |
|----------|---------------|
| Go       | ~0.00004 s    |
| Rust     | ~0.00008 s    |
| C++      | ~0.00040 s    |
| Node.js  | ~0.00046 s    |
| Python   | ~0.00056 s    |
| Bun      | ~0.00220 s    |

---

## Recent Fixes (v0.2.0)

### Watermark Removal Improvements

**Fixed critical bugs in AI watermark detection across all 4 implementations:**

1. **PUA Range Bug** — Corrected Unicode range from `E000-E007F` (573,343 chars) to `E000-E07F` (128 chars)
   - Reduced watermark character set from 860,305 to 259 characters
   - Fixed in: Python, Go, Node.js, Rust

2. **Node.js Code Point Handling** — Changed `String.fromCharCode()` to `String.fromCodePoint()`
   - Previously detected 853 false watermarks (ASCII characters)
   - Now correctly detects 17 watermarks

3. **Go Flag Position** — Documented that Go requires flags BEFORE filename
   ```bash
   # Correct usage for Go:
   cd partxtgo && go run . --remove-watermark input.txt
   ```

### Test Results (testdata/comprehensive_watermark_test.txt)

All implementations now correctly detect **17/17 watermark characters**:

| Language | Time (s) | Watermarks Removed |
|----------|----------|-------------------|
| Python   | 0.000560 | ✅ 17 (all) |
| Go       | 0.000039 | ✅ 17 (all) |
| Node.js  | 0.000455 | ✅ 17 (all) |
| Rust     | 0.000078 | ✅ 17 (all) |

**Total watermark coverage:** ~270+ character codepoints

## Versioning

- Patch (0.0.x): bug fixes
- Minor (0.x.0): fully functional, meets requirements
- Major (x.0.0): significant new features

Current version: 0.2.0

## License



MIT

## License

MIT
