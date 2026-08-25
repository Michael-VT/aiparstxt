# aiparstxt — Multi-language Text Sanitizer & AI Forensic Analyzer

A set of command-line utilities that sanitize text files by replacing disallowed characters with '?'. Implemented in 6 languages for performance comparison. Includes AI watermark removal and **statistical forensic analysis** for detecting AI-generated text.

**⚠️ IMPORTANT UPDATE (August 2026):** After extensive testing with DEFINITELY HUMAN and DEFINITELY AI samples, we've created **honest_ai_detector.py** — the only detector with transparent limitations. See [AI Detection Limitations](#ai-detection-limitations) below.

**Available in:** [English](README.md) | [Русский](README.RU.md) | [Українська](README.UA.md) | [Português](README.PT.md) | [Français](README.FR.md) | [Deutsch](README.DE.md)


## Features

- **Text sanitization** — replace disallowed characters with '?' across 6 language implementations
- **AI watermark removal** — strip invisible Unicode watermarks inserted by AI systems
- **AI forensic analytics** — heuristic statistical analysis to estimate AI authorship probability
- **Extended detection versions** — enhanced forensic analysis available for all 6 languages ⭐
- **Honest AI detection** — transparent AI detector with known limitations ✅

---

## Allowed Characters

- Digits: 0-9
- Latin letters: A-Z, a-z
- Russian letters: А-Я, а-я (including Ё/ё)
- Ukrainian letters: ҐґЄєІіЇї
- Portuguese letters: àáâãéêíóôõúç and uppercase equivalents
- Punctuation and symbols: []{}()-=_+!@#$%&*;'/.,<>'"`~:—«»
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

### ✅ HONEST AI Detector (RECOMMENDED)

```bash
python3 honest_ai_detector.py <textfile>
```

**The only detector with transparent limitations:**

✅ **Correctly detects human texts** (5% for real 2014 article)  
✅ **Honestly admits limitations** (10% + warnings for AI text)  
✅ **No false guarantees** (explicitly warns about false negatives)

**Principles:**
- Better to NOT detect AI than falsely accuse a human
- Checks ONLY technically detectable features
- Honestly states its limitations

**Methodology:**
- ✅ Checks AI watermarks (zero-width characters)
- ✅ Checks formatting anomalies
- ❌ Does NOT use lexical markers (false positives on professional style)
- ❌ Does NOT use statistics (too variable)
- ❌ Does NOT use stylometry (unreliable)

**What it CAN detect:**
- Low-quality AI (with watermarks, formatting anomalies)
- Human texts with high precision

**What it CANNOT detect:**
- High-quality AI (without technical indicators)
- Technical documentation (may be false negative)
- Human-edited AI texts

### ❌ Legacy Analyzers (NOT RECOMMENDED for AI Detection)

**The following analyzers have been tested and found unreliable for AI detection:**

| Script | Status | Issue |
|--------|--------|-------|
| `parscgpt.py` | ❌ Not Recommended | Testing showed 15-35% for DEFINITELY AI text |
| `parscgptv1.py` | ❌ Not Recommended | Testing showed 15-35% for DEFINITELY AI text |
| `parscgptv2.py` | ❌ Not Recommended | Testing showed 15-35% for DEFINITELY AI text |
| `parscgpt-ext.py` | ❌ Not Recommended | Testing showed 15-35% for DEFINITELY AI text |

**Testing Results:**

| Detector | Human Text (Habr 2014) | AI Text (Sample README) | Verdict |
|----------|-----------------------|---------------------|---------|
| **honest_ai_detector** ✅ | **5%** ✅ | **10% + ⚠️** ✅ | **HONEST** |
| `parscgptv2.py` | 1% ✅ | 15% ❌ | DOES NOT WORK |
| `parscgpt-ext.py` | 1% ✅ | 15% ❌ | DOES NOT WORK |

**Critical Problem:** **NONE of the existing analyzers can correctly detect AI-generated text!**

All analyzers show 15-35% for text that was DEFINITELY written by AI, instead of the expected 70-95%.

### Integrated Extended Analyzers (All 6 Languages) ⚠️

⚠️ **WARNING:** Extended analyzers are included for text sanitization features, but their AI detection should NOT be relied upon due to known limitations.

| Language | Extended Binary | Report file | AI Detection Status |
|----------|----------------|-------------|-------------------|
| Python | `partxtpy/partxt-ext.py` | report_py-ext.txt | ⚠️ Limited reliability |
| Rust | `partxtrs/target/partxt-ext` | report_rs-ext.txt | ⚠️ Limited reliability |
| Go | `partxtgo/main-ext.go` | report_go-ext.txt | ⚠️ Limited reliability |
| C++ | `partxtcpp/partxt-ext` | report_cpp-ext.txt | ⚠️ Limited reliability |
| Node.js | `partxtnode/partxt-ext.js` | report_node-ext.txt | ⚠️ Limited reliability |
| Bun | `partxtjs/partxt-ext.js` | report_bun-ext.txt | ⚠️ Limited reliability |

---

## AI Detection Limitations ⚠️

### The Reality

✅ **HONEST detector** — the only correct approach to AI detection

❌ **All other detectors** — give false guarantees and do not work properly

### Why Detectors DON'T WORK for AI Texts

1. **README files are a special case**
   - Technical documentation is structured by definition
   - Uses formal style
   - Has standard phrases ("installation", "usage", "examples")
   - Lacks personal experience

2. **AI generation has become too high-quality**
   - Modern AIs write naturally
   - Do not use zero-width watermarks
   - Do not make formatting errors
   - Imitate human style

3. **No reliable technical indicators exist**
   - Watermarks: not used in high-quality AI
   - Formatting anomalies: absent in high-quality AI
   - Statistical indicators: too variable

### What Actually Works

**For Human Texts:**
```bash
python3 honest_ai_detector.py human_text.txt
```
**Expected result:** 5% + "NO AI INDICATORS FOUND" ✅

**For AI Texts (if technical indicators exist):**
```bash
python3 honest_ai_detector.py ai_text.txt
```
**Expected result:** High probability + indicators found ✅

**For High-Quality AI (README, tech docs):**
```bash
python3 honest_ai_detector.py readme.md
```
**Expected result:** 10-35% + HONEST warnings ⚠️

---

## Standard Metrics (Extended Versions)

⚠️ **NOTE:** These metrics are provided for text analysis features, but their AI detection reliability is limited.

| Metric | Description | AI Detection Value |
|--------|-------------|---------------------|
| `lexical_diversity` | Unique words / total words (after stopword removal) | AI has lower diversity |
| `repetition_score` | Fraction of words appearing more than once | AI repeats more |
| `entropy` | Shannon entropy of word frequency distribution | AI has unnaturally uniform distribution |
| `burstiness` | Coefficient of variation of sentence lengths | AI has overly uniform sentence structure (primary signal) |
| `paragraph_length_cv` | CV of paragraph word counts | AI paragraphs are unnaturally equal (primary signal) |
| `joint_uniformity` | Both sentence and paragraph CV low | Strongest structural AI signal |
| `connective_density` | Discourse connectives per sentence (multilingual) | AI overuses connectives |
| `pattern_repetition` | Fraction of repeated sentence-length patterns | AI uses template patterns |
| `punctuation_density` | Punctuation count / total characters | AI may overuse punctuation |
| `ai_phrase_hits` | ~150 curated AI-typical phrases in 3 tiers (EN/RU/UK/PT) | Direct AI signature |
| `unicode_symbols` | Count of suspicious Unicode characters | Technical AI markers |
| `avg_word_length` | Average word length | AI uses simpler vocabulary |
| `word_length_variance` | Variance in word lengths | AI texts more uniform |
| `confidence` | Based on word count (LOW <300, MEDIUM 300-999, HIGH ≥1000) | Reliability indicator |

### AI Evidence Locations (v0.4.0+)

Every triggered indicator is reported with its exact location in the text:
line number, an excerpt with the trigger highlighted as `>>>phrase<<<`,
and sentence/paragraph length sequences for uniformity signals. The `AI EVIDENCE`
section appears in the extended sanitizer reports and in `parscgpt-ext.py` output.

### Honest abstention (v0.4.1–v0.4.3)

- Short texts (< 150 words or < 5 sentences): structural signals are scaled by
  statistical reliability instead of being silently switched off, and the
  verdict is annotated as unreliable — no more confident "human" verdicts
  on texts too small to analyze.
- Template header repetition (v0.4.2): verbatim-repeated short header lines
  ("Что верно" ×7, "Итог" ×7) — a strong marker of structured LLM answers;
  zero false positives on the human corpus.
- Promotional/social-media register (v0.4.3): emoji- and exclamation-heavy
  texts get a genre note instead of a "human" verdict — the register is
  produced by both AI and human SMM writers, so no AI points are awarded,
  the verdict is simply withheld.

### Online demo (GitHub Pages)

A browser-based version lives in [`docs/`](docs/) (`index.html` + `analyzer.js`):
paste a text, get the score, verdict and the located evidence — everything runs
locally in the browser, the text never leaves the device. The web analyzer is
byte-compatible with the console implementations (`tests/test_web_parity.sh`).

To publish on GitHub: repo **Settings → Pages → Source: Deploy from a branch →
main / `/docs`** — the demo appears at `https://<user>.github.io/aiparstxt/`.

### One-file analysis with all detectors

```bash
./analyze_all.sh input.txt
```

Builds missing binaries, runs every analyzer in the project (technical,
legacy ×2, standard, extended, marker-based, and all six `partxt-ext`),
verifies cross-implementation parity, and prints a summarized report:
consensus, worst-case (strictest analyzer), risk band, and the list of
spots to review/edit before publishing.

### Validation (v0.4.0+)

Calibrated and validated against 34 confirmed AI answers (8 services × 4
languages) and 20 source-based human texts — see `validation/AI_CORPUS_REPORT.md`
and `AI_SIGNALS_SPEC.md`. At classification threshold 50: recall 93.9%,
false-positive rate 0%. Scores are heuristic, not proof of authorship.

### Output Format (Honest AI Detector)

```
======================================================================
HONEST AI DETECTOR — Transparent Limitations
======================================================================

📁 File: example.txt
⏰ Analysis: 2026-08-24T21:33:48
🔤 Language: RU
----------------------------------------------------------------------

🎯 VERDICT: ✅ NO AI INDICATORS FOUND
📈 AI Probability: 5%
🔍 Confidence: HIGH

💭 REASONING:
  • No technical AI indicators found

📋 DOCUMENT TYPE: Technical Article
  ⚠️  WARNING: Technical documentation may produce false-negative results!

----------------------------------------------------------------------

⚠️  DETECTOR LIMITATIONS:
  MAY PRODUCE FALSE-NEGATIVE RESULTS FOR:
    • README files and technical documentation
    • Texts written by professional technical writers
    • AI texts edited by humans

✅ DETECTOR HONESTLY STATES:
  • CANNOT detect all AI texts
  • CANNOT distinguish AI from professional technical writer
  • Better to NOT detect AI than falsely accuse a human

----------------------------------------------------------------------

🧠 METHODOLOGY:
  • Checks ONLY technically detectable features:
    - AI watermarks (zero-width characters)
    - Formatting anomalies (repetitions, uniform spacing)
  • Does NOT use unreliable methods:
    - Lexical markers (false positives)
    - Statistics (variable)
    - Stylometry (unreliable)
======================================================================
```

---

## Implementations

| Language   | Directory    | Build command                    | Report file      | Extended Report      | Honest AI Detector |
|------------|-------------|----------------------------------|------------------|---------------------|-------------------|
| Python     | partxtpy/   | (no build needed)                | report_py.txt    | report_py-ext.txt   | ✅ Available       |
| Rust       | partxtrs/   | cargo build --release            | report_rs.txt    | report_rs-ext.txt   | ✅ Available       |
| Go         | partxtgo/   | cd partxtgo && go build -o partxtgo main.go | report_go.txt    | report_go-ext.txt   | ✅ Available       |
| C++        | partxtcpp/  | make                             | report_cpp.txt   | report_cpp-ext.txt  | ✅ Available       |
| Node.js    | partxtnode/ | (no build needed)                | report_node.txt  | report_node-ext.txt | ✅ Available       |
| Bun        | partxtjs/   | (no build needed)                | report_bun.txt   | report_bun-ext.txt  | ✅ Available       |

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

## Sample Results (testdata/sample.txt, 136 replacements)

| Language | Execution Time | Extended Time |
|----------|---------------|---------------|
| Go       | ~0.00004 s    | ~0.00006 s    |
| Rust     | ~0.00008 s    | ~0.00010 s    |
| C++      | ~0.00040 s    | ~0.00050 s    |
| Node.js  | ~0.00046 s    | ~0.00060 s    |
| Python   | ~0.00056 s    | ~0.00070 s    |
| Bun      | ~0.00220 s    | ~0.00280 s    |

---

## Project Status (August 2026)

✅ **Text Sanitization:** VERIFIED — all 6 implementations produce identical standard output
✅ **AI Watermark Removal:** VERIFIED — all 6 implementations pass the shared watermark test
⚠️ **AI Detection:** LIMITED RELIABILITY — Only `honest_ai_detector.py` with transparent limitations  

### What Works

✅ **Text sanitization** — replaces disallowed characters with '?'  
✅ **AI watermark removal** — strips invisible Unicode characters  
✅ **Honest AI detection** — transparent about limitations  

### What Has Limitations

⚠️ **Statistical AI detection** — limited reliability for technical documentation  
⚠️ **Extended analyzers** — do NOT reliably detect high-quality AI texts  

### Recommendation

**Use `honest_ai_detector.py` for AI detection** — it's the only detector with transparent limitations and correct methodology.

---

## Testing

**Testing:**

Comprehensive testing was conducted using:
- **DEFINITELY HUMAN sample:** Real 2014 Habr article (pre-ChatGPT era)
- **DEFINITELY AI sample:** AI-generated README file
- **MULTILINGUAL TEST:** ChatGPT-generated Ukrainian text (bas-dcxv-try-orig.txt)

**Results:**

| Detector | Human Text (Habr 2014) | AI Text (Sample README) | Ukrainian AI Text | Status |
|----------|-----------------------|---------------------|------------------|--------|
| **honest_ai_detector** ✅ | **5%** ✅ | **10% + ⚠️** ✅ | **5%** ❌ | **HONEST (language limitation)** |
| `parscgptv2.py` | 1% ✅ | 15% ❌ | 5% ❌ | DOES NOT WORK |
| `parscgpt-ext.py` | 1% ✅ | 15% ❌ | 5% ❌ | DOES NOT WORK |

**Ukrainian Text Testing (August 2026):**
All existing detectors failed to correctly identify ChatGPT-generated Ukrainian text (1-30% AI probability instead of 100%). This revealed critical language detection limitations:
- 6 out of 7 detectors incorrectly identified language as Russian instead of Ukrainian
- No Ukrainian-specific AI patterns in detector databases
- Perplexity/burstiness metrics insufficient for non-English languages

**See:** `tmp/FINAL_REPORT.md` for complete multilingual testing analysis and recommendations.

**See `TESTING.md` for the reproducible cross-language verification.**

---

## Documentation

- [EXTENDED_VERSIONS.md](EXTENDED_VERSIONS.md) — Details on extended analyzers
- [ANALYZER_COMPARISON.md](ANALYZER_COMPARISON.md) — Comparison of analyzers
- [ANALYTICS_RECOMMENDATIONS.md](ANALYTICS_RECOMMENDATIONS.md) — Analytics porting guide
- [CHARACTER_SET.md](CHARACTER_SET.md) — Canonical character contract
- [TESTING.md](TESTING.md) — Reproducible test procedure

---

## License

MIT

## Contributing

Contributions welcome! The project is especially interested in:
- Improving AI detection reliability
- Adding more language implementations
- Enhancing text sanitization features
- Documentation improvements

**Please note:** AI detection is an active research area with known limitations. The `honest_ai_detector.py` represents our current best effort with transparent limitations.
