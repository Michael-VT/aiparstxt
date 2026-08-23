# aiparstxt — Multi-language Text Sanitizer & AI Forensic Analyzer

A set of command-line utilities that sanitize text files by replacing disallowed characters with '?'. Implemented in 6 languages for performance comparison. Includes AI watermark removal and **statistical forensic analysis** for detecting AI-generated text.

**Available in:** [English](README.md) | [Русский](README.RU.md) | [Українська](README.UA.md) | [Português](README.PT.md) | [Français](README.FR.md) | [Deutsch](README.DE.md)


## Features

- **Text sanitization** — replace disallowed characters with '?' across 6 language implementations
- **AI watermark removal** — strip invisible Unicode watermarks inserted by AI systems
- **AI forensic analytics** — heuristic statistical analysis to estimate AI authorship probability
- **Extended detection versions** — enhanced forensic analysis available for all 6 languages ⭐

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
# Standard versions
python3 partxtpy/partxt.py testdata/sample.txt
python3 partxtpy/partxt.py testdata/sample.txt --remove-watermark

# Extended versions with AI forensic analysis ⭐
python3 partxtpy/partxt-ext.py testdata/sample.txt
python3 partxtpy/partxt-ext.py testdata/sample.txt --remove-watermark

cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext -- testdata/sample.txt --remove-watermark

cd partxtgo && go run . testdata/sample.txt
cd partxtgo && go run main-ext.go testdata/sample.txt --remove-watermark

cd partxtcpp && make && ./partxt testdata/sample.txt
cd partxtcpp && make && ./partxt-ext testdata/sample.txt --remove-watermark

node partxtnode/partxt.js testdata/sample.txt
node partxtnode/partxt-ext.js testdata/sample.txt --remove-watermark

bun run partxtjs/partxt.js testdata/sample.txt
bun run partxtjs/partxt-ext.js testdata/sample.txt --remove-watermark
```

### All at once

```bash
# Standard versions only
./run_all.sh testdata/sample.txt

# Extended versions with AI detection
./run_all_extended.sh testdata/sample.txt
```

---

## CLI Usage — AI Forensic Analytics

### Standalone Python Analyzers

```bash
python3 parscgptv2.py <textfile>
```

Four analytical script variants are available in the project root:

| Script | Metrics | AI Phrases | Features | Recommended Use |
|--------|----------|------------|----------|-----------------|
| `parscgpt.py` | 8 core | 21 | Basic metrics only | Legacy/testing |
| `parscgptv1.py` | 8 core + interpretation | 21 | + Stopwords, confidence | Basic detection |
| `parscgptv2.py` | 8 core + refined interpretation | 21 | + Clean output | **Standard detection** ✅ |
| `parscgpt-ext.py` | **17 advanced metrics** | **70+** | + Linguistic analysis, weighted scoring | **Enhanced detection** ⭐ |

### Integrated Extended Analyzers (All 6 Languages) ⭐

Extended versions of the basic text sanitizers (`partxt-ext`) are now available for **all 6 language implementations** with enhanced AI forensic analysis:

| Language | Extended Binary | Report file | Features |
|----------|----------------|-------------|-----------|
| Python | `partxtpy/partxt-ext.py` | report_py-ext.txt | 11 core metrics + AI probability scoring |
| Rust | `partxtrs/target/partxt-ext` | report_rs-ext.txt | Same metrics as Python, compiled performance |
| Go | `partxtgo/main-ext.go` | report_go-ext.txt | Same metrics, compiled performance |
| C++ | `partxtcpp/partxt-ext` | report_cpp-ext.txt | Same metrics, compiled performance |
| Node.js | `partxtnode/partxt-ext.js` | report_node-ext.txt | Same metrics, JavaScript runtime |
| Bun | `partxtjs/partxt-ext.js` | report_bun-ext.txt | Same metrics, optimized JavaScript |

**Enhanced Features in Extended Versions:**
- 11 core AI forensic metrics (lexical diversity, entropy, burstiness, pattern repetition, etc.)
- AI phrase detection with 70+ suspicious phrases
- Unicode suspicious character detection
- Statistical AI probability scoring (0-100%)
- Confidence levels (LOW/MEDIUM/HIGH) based on text length
- Detailed signal analysis with visual indicators
- Interpretation of each metric with actionable insights

---

## Standard Metrics (All Extended Versions)

| Metric | Description | AI Detection Value |
|--------|-------------|---------------------|
| `lexical_diversity` | Unique words / total words (after stopword removal) | AI has lower diversity |
| `repetition_score` | Fraction of words appearing more than once | AI repeats more |
| `entropy` | Shannon entropy of word frequency distribution | AI has unnaturally uniform distribution |
| `burstiness` | Coefficient of variation of sentence lengths | AI has overly uniform sentence structure |
| `pattern_repetition` | Fraction of repeated sentence-length patterns | AI uses template patterns |
| `punctuation_density` | Punctuation count / total characters | AI may overuse punctuation |
| `ai_phrase_hits` | Matches against curated AI-typical phrases (70+) | Direct AI signature |
| `unicode_symbols` | Count of suspicious Unicode characters | Technical AI markers |
| `avg_word_length` | Average word length | AI uses simpler vocabulary |
| `word_length_variance` | Variance in word lengths | AI texts more uniform |
| `confidence` | Based on word count (LOW <300, MEDIUM 300-999, HIGH ≥1000) | Reliability indicator |

### AI Probability Scoring (Extended Versions)

| Condition | Points | Enhancement |
|-----------|--------|-------------|
| Lexical diversity < 0.45 | **+25** | ↑ +5 vs standard |
| Entropy < 5.0 | **+25** | ↑ +5 vs standard |
| Burstiness < 0.35 | **+20** | ↑ +5 vs standard |
| Pattern repetition > 0.35 | **+20** | ↑ +5 vs standard |
| AI phrase hits ≥ 3 | **+20** | ↑ +5 vs standard |
| Repetition score > 0.5 | +15 | Same |
| Punctuation density > 0.04 | +5 | Same |
| Unicode suspicious chars present | +5 | Same |
| Average word length < 4.0 | **+10** | 🆕 New metric |
| Word length variance < 1.5 | **+8** | 🆕 New metric |

**Total** capped at 100% with confidence factor adjustment (80%-100% based on text length).

### Output Format (Extended Versions)

```
======================================================================
aiparstxt-ext — Enhanced AI Forensic Analyzer Report
======================================================================

Input file:  sample.txt
Output file: sample.ed.txt
Execution time: 0.000560s

--- AI Watermark Analysis ---
Watermark characters removed: 17
Removed watermark character types:
  U+200B: 5
  U+200C: 3
  ...

--- Replaced Characters ---
Characters replaced: 197

======================================================================
AI FORENSIC ANALYSIS
======================================================================

Overall Verdict: Moderate probability of AI involvement (35.2%)
Confidence Level: MEDIUM

Detailed Metrics:
  Word count:            198
  Sentence count:        11
  Lexical diversity:     0.832
  Repetition score:      0.202
  Entropy:               6.655
  Burstiness:            1.590
  Pattern repetition:    0.000
  Punctuation density:   0.037
  AI phrase hits:        2
  Unicode suspicious:    0
  Avg word length:       4.52
  Word length variance:  2.18

Signal Analysis:
  ✓ High lexical diversity - rich vocabulary variation
  ✓ Good entropy - natural word distribution
  ✓ Good burstiness - natural sentence variation
  ⚠️ Found 2 AI-typical phrases
```

---

## Extended Metrics (parscgpt-ext.py only) ⭐

For the most comprehensive analysis, the standalone `parscgpt-ext.py` provides 17 advanced metrics:

| Metric | Description | AI Detection Value |
|--------|-------------|---------------------|
| `avg_word_length` | Average word length | AI uses simpler vocabulary |
| `word_length_variance` | Variance in word lengths | AI texts more uniform |
| `pronoun_ratio` | Ratio of pronouns to total words | AI overuses pronouns |
| `readability_score` | Flesch Reading Ease score | AI texts "too readable" |
| `passive_voice_density` | Passive voice construction frequency | AI prefers passive |
| `adj_noun_pair_diversity` | Unique adj-noun combinations | AI has limited combinations |
| `structural_uniformity` | Sentence start pattern repetition | AI uses templates |
| `quantifier_overuse` | Hedge word frequency | AI overuses qualifiers |

Use `parscgpt-ext.py` when you need the deepest linguistic analysis beyond the integrated sanitizers.
**Key Differences: Extended vs Standard Versions**
- Provides **9 additional metrics** for deeper analysis
- Shows **detailed scoring** instead of single probability
- Includes **specific interpretation** for each metric  
- Offers **improved reliability** with text length adaptation
- Detects **more AI patterns** — 70+ phrases vs 21 in standard version


---

## Porting Analytics to Other Languages

The enhanced analytics engine is now available in **all 6 language implementations** via the `-ext` versions. The standalone Python `parscgpt-ext.py` provides the most comprehensive 17-metric analysis for reference.

See **`ANALYTICS_RECOMMENDATIONS.md`** for a complete porting guide with:
- Metric computation formulas
- Scoring model weights and thresholds
- Interpretation rules
- Language-specific guidance

---

## Implementations

| Language   | Directory    | Build command                    | Report file      | Extended Report      |
|------------|-------------|----------------------------------|------------------|---------------------|
| Python     | partxtpy/   | (no build needed)                | report_py.txt    | report_py-ext.txt   |
| Rust       | partxtrs/   | cargo build --release            | report_rs.txt    | report_rs-ext.txt   |
| Go         | partxtgo/   | cd partxtgo && go build          | report_go.txt    | report_go-ext.txt   |
| C++        | partxtcpp/  | make                             | report_cpp.txt   | report_cpp-ext.txt  |
| Node.js    | partxtnode/ | (no build needed)                | report_node.txt  | report_node-ext.txt |
| Bun        | partxtjs/   | (no build needed)                | report_bun.txt   | report_bun-ext.txt  |

---

## Report Format (Sanitizer)

Each report includes:
- Execution time
- Mode (replace/remove + watermark removal status)
- Watermark characters removed (with Unicode code points)
- Replaced characters (with counts)
- Word frequency (ascending)


**Extended versions** additionally include:
- AI forensic metrics section
- AI probability score with confidence level
- Signal analysis with visual indicators
- Metric-specific interpretations

---

## Sample Results (testdata/sample.txt, 197 replacements)

| Language | Execution Time | Extended Time |
|----------|---------------|---------------|
| Go       | ~0.00004 s    | ~0.00006 s    |
| Rust     | ~0.00008 s    | ~0.00010 s    |
| C++      | ~0.00040 s    | ~0.00050 s    |
| Node.js  | ~0.00046 s    | ~0.00060 s    |
| Python   | ~0.00056 s    | ~0.00070 s    |
| Bun      | ~0.00220 s    | ~0.00280 s    |

---

## Recent Fixes (v0.3.0)

### New Extended Versions ⭐

**Enhanced AI forensic analysis now available in all 6 languages:**

1. **Python Extended** (`partxtpy/partxt-ext.py`)
   - Full AI forensic metrics integration
   - Probability-based scoring
   - Signal analysis with interpretations

2. **JavaScript Extended** (Bun + Node.js)
   - `partxtjs/partxt-ext.js` for Bun
   - `partxtnode/partxt-ext.js` for Node.js
   - Same metrics as Python version

3. **Rust Extended** (`partxtrs/src/main-ext.rs`)
   - Compiled performance
   - Memory-efficient processing
   - Full metric suite

4. **Go Extended** (`partxtgo/main-ext.go`)
   - Type-safe implementation
   - Standard library only
   - Comprehensive metrics

5. **C++ Extended** (`partxtcpp/partxt-ext.cpp`)
   - High-performance C++20
   - Full Unicode support
   - Extended metrics

**All extended versions include:**
- 11 core AI forensic metrics
- AI phrase detection (70+ phrases)
- Unicode suspicious character detection
- Statistical probability scoring (0-100%)
- Confidence levels (LOW/MEDIUM/HIGH)
- Detailed signal analysis
- Enhanced reporting

### Previous Fixes (v0.2.0)

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

---

## Versioning

- Patch (0.0.x): bug fixes
- Minor (0.x.0): fully functional, meets requirements
- Major (x.0.0): significant new features

Current version: 0.3.0

---

## License

MIT
