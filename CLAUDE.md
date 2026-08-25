# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aiparstxt** — Multi-language text sanitizer with AI forensic analytics. Six implementations (Python, Rust, Go, C++, Node.js, Bun) that sanitize text files by replacing disallowed characters with '?'. Designed for cross-language performance comparison. Includes enhanced AI forensic analysis for detecting AI-generated text.

## Project Tools

### 1. Text Sanitizer (all 6 languages)
CLI tools in `partxtpy/`, `partxtrs/`, `partxtgo/`, `partxtcpp/`, `partxtnode/`, `partxtjs/` — sanitize text, remove watermarks, generate replacement reports.

### 2. Extended AI Forensic Analytics (All 6 languages) ⭐
Enhanced sanitizers with integrated AI detection:
- `partxt-ext` for each language (Python, Rust, Go, C++, Node.js, Bun)
- **18 forensic metrics** incl. sentence/paragraph-length uniformity (CV)
- **~150 AI phrases** in 3 tiers across EN/RU/UK/PT
- **AI EVIDENCE**: line numbers + highlighted excerpts for every indicator
- Unicode suspicious character detection
- Statistical AI probability scoring (0-100%)
- Confidence levels based on text length

### 3. Advanced AI Analysis (Python only)
Comprehensive analysis scripts:
- `parscgpt.py` — basic metrics and AI score (legacy)
- `parscgptv1.py` — adds stopword filtering, confidence, interpretation (legacy)
- `parscgptv2.py` — **standard detection** (conservative: core metrics + multilingual phrase tiers)
- `parscgpt-ext.py` — **extended detection** (18 metrics, ~150 tiered phrases EN/RU/UK/PT, evidence locations)

## Build & Run Commands

### Build all
```bash
make -C partxtcpp
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext
(cd partxtgo && go build -o partxtgo main.go)
(cd partxtgo && go build -o partxt-ext main-ext.go)
# Python, Node.js, Bun — no build needed
```

### Run sanitizer (standard versions)
```bash
python3 partxtpy/partxt.py testdata/sample.txt
./partxtrs/target/release/partxt testdata/sample.txt
./partxtgo/partxtgo testdata/sample.txt
./partxtcpp/partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt
```

### Run extended sanitizers with AI detection ⭐
```bash
python3 partxtpy/partxt-ext.py testdata/sample.txt
./partxtrs/target/release/partxt-ext testdata/sample.txt
./partxtgo/partxt-ext testdata/sample.txt
./partxtcpp/partxt-ext testdata/sample.txt
node partxtnode/partxt-ext.js testdata/sample.txt
bun run partxtjs/partxt-ext.js testdata/sample.txt
```

### Run AI analytics
```bash
# Standard version (conservative, multilingual phrases)
python3 parscgptv2.py testdata/sample.txt

# Extended version (18 metrics, tiered multilingual phrases, evidence locations)
python3 parscgpt-ext.py testdata/sample.txt
```

### Run all + timing comparison
```bash
./run_all.sh testdata/sample.txt
./run_all_extended.sh testdata/sample.txt
```

### Analyze one file with ALL detectors and compare results
```bash
./analyze_all.sh input.txt   # parscgpt-ext/v2 + partxt-ext x6, parity check
```

## CLI Interface — Sanitizer (consistent across all implementations)

```
partxt <input_file> [-o output] [-r report] [--no-edit] [--no-report] [-w] [--remove-watermark]
```

- `-o` / `--output`: output file (default: `<input>.ed.txt`)
- `-r` / `--report`: report file (default: `report_<lang>.txt`)
- `--no-edit`: skip writing .ed.txt
- `--no-report`: skip writing report
- `-w` / `--no-words`: exclude word frequency from report
- `--remove-watermark`: remove AI watermark characters

## CLI Interface — AI Analytics

```bash
python3 parscgptv2.py <textfile>          # Standard version
python3 parscgpt-ext.py <textfile>        # Extended version
```

No options. Reads file, prints forensic report to stdout.

## Allowed Characters (Sanitizer)

Digits `0-9`, Latin `A-Za-z`, Russian `А-Яа-я` (incl. Ёё), Ukrainian `ҐґЄєІіЇї`, Portuguese `àáâãéêíóôõúç` (+ uppercase), punctuation `[]{}()-=_+!@#$%&*;'/.,<>:'"\`~—«»`, whitespace. Everything else → `?`. Canonical contract: `CHARACTER_SET.md`. Python additionally supports `-l/--language` modes that narrow the set (auto-detected when no `-l` given); cross-language comparisons use `-l universal`.

## Analytics Metrics

### Extended Version (parscgpt-ext.py) — 18 metrics ⭐
**Advanced comprehensive analysis (spec: `AI_SIGNALS_SPEC.md`):**
- Structural (primary): sentence_length_cv, paragraph_length_cv, joint_uniformity, connective_density
- Core: lexical_diversity, repetition_score, entropy, pattern_repetition_score, punctuation_density, ai_phrase_hits (3 tiers, ~150 phrases EN/RU/UK/PT), unicode_symbols
- Extended: avg_word_length, word_length_variance, pronoun_ratio, readability_score, passive_voice_density, adj_noun_pair_diversity, structural_uniformity, quantifier_overuse
- Linguistic: top_bigrams, top_trigrams
- **Evidence**: located indicators (line numbers + excerpts with `>>>phrase<<<` highlighting)

### Standard Version (parscgptv2.py) — conservative
- Core metrics: lexical_diversity, repetition_score, entropy, burstiness (CV tiers), paragraph_uniformity, pattern_repetition_score, punctuation_density, ai_phrase_hits (HIGH+MEDIUM tiers), unicode_symbols
- Evidence: located phrase hits (line numbers)
- Linguistic: top_bigrams, top_trigrams

### Scoring System (v0.4.0, corpus-validated)
- **Extended**: weighted sum dominated by structural uniformity (sentence/paragraph CV tiers + joint bonus), tiered phrases and connective density; length adaptation `total * (0.9 + 0.1*min(1, words/1000))`, clamped 0-100
- **Validation** (34 AI files vs 20 human, threshold 50): recall 93.9%, FP 0%; at threshold 70: recall 60.6%, FP 0% — see `validation/AI_CORPUS_REPORT.md`
- **Recommended thresholds**: 50-55 "probable AI", 70 conservative "strong AI"
- **Standard**: conservative subset scoring (0-100%)
- **Confidence**: low/medium/high based on word count

## Architecture

### Sanitizer (each implementation)
1. **Parse CLI args** → input file, output path, report path, flags
2. **Read input** as UTF-8
3. **Process**: iterate characters, check against allowed set, replace disallowed with '?', count replacements per character
4. **Word frequency**: split processed text on non-alphanumeric boundaries (keeping `'` and `-`), count occurrences
5. **AI Analysis** (extended versions only): compute metrics, calculate probability, generate interpretation
6. **Write output** (.ed.txt) and **report** (replacements table + word frequency + AI analysis)

### Analytics (parscgpt-ext.py)
1. **Tokenize** → sentences, words, filtered words (stopwords removed)
2. **Compute metrics** → diversity, repetition, entropy, burstiness, patterns, punctuation, linguistic analysis
3. **Score** → weighted heuristic with confidence adjustment → AI probability
4. **Interpret** → per-metric verdicts + signal analysis + overall profile
5. **Output** → structured text report with visual indicators

Report filenames include language prefix: `report_py.txt`, `report_py-ext.txt`, `report_rs.txt`, `report_rs-ext.txt`, etc.

## Versioning

Semantic: patch (0.0.x) = bug fixes, minor (0.x.0) = meets requirements, major (x.0.0) = significant new features. **Current: 0.4.3**.

### Version History
- **v0.4.3**: genre abstention for promotional/social register; readability
  interpretation fix (was inverted); Rust dead-code cleanup
- **v0.4.2**: template header repetition signal (structured LLM answers);
  `analyze_all.sh` — one-file analysis with all detectors + summarized report
- **v0.4.1**: smooth reliability scaling replaces hard CV guards; honest
  abstention NOTE on short texts (all 6 languages)
- **v0.4.0**: Corpus-validated rescoring: sentence/paragraph CV signals, multilingual phrase tiers (EN/RU/UK/PT), connective density, AI EVIDENCE locations; recall 93.9% at FP 0% (threshold 50); all 6 implementations at exact parity
- **v0.3.0**: Extended AI forensic analytics in all 6 languages, 11/17 metrics, 70+ phrases, weighted scoring
- **v0.2.0**: Watermark detection bug fixes, cross-language support
- **v0.1.0**: Initial multi-language implementation

## Key Files

### Core Analysis
- `parscgpt-ext.py` — **Extended AI forensic analytics** (18 metrics, evidence locations, most comprehensive) ⭐
- `AI_SIGNALS_SPEC.md` — **Canonical spec**: phrase tiers, weights, formula, evidence format, abstention rules
- `analyze_all.sh` — **Run every analyzer on one file** + summarized report (builds missing binaries)
- `docs/index.html` + `docs/analyzer.js` — **browser demo** for GitHub Pages (parity-tested)
- `parscgptv2.py` — **Standard AI forensic analytics** (conservative multilingual version)
- `partxtpy/partxt-ext.py` — Python extended sanitizer with integrated AI detection
- `ANALYTICS_RECOMMENDATIONS.md` — Porting guide for analytics to other languages

### Documentation
- `EXTENDED_VERSIONS.md` — Comprehensive extended versions documentation ⭐
- `README.md` — Main documentation (English)
- `CLAUDE.md` — This file (project guidance for Claude Code)

### Build & Test
- `testdata/sample.txt` — Test file with diverse Unicode characters
- `run_all.sh` — Builds and runs all standard implementations
- `run_all_extended.sh` — Builds and runs all extended versions with timing comparison

### Language Implementations
- `partxtcpp/Makefile` — C++ build (g++, C++20, -O2)
- `partxtrs/Cargo.toml` — Rust project (no external deps)
- `partxtgo/go.mod` — Go module
- `ai-chart.txt` — AI watermark character reference
- `ai-chart-extended.txt` — Comprehensive watermarking reference

### Historical
- `WATERMARK_FIXES_SUMMARY.md` — v0.2.0 watermark detection bug fixes
- `WATERMARKING_UPDATE_SUMMARY.md` — Original watermark implementation details

## Watermark Detection (v0.2.0 → v0.3.0)

All 6 implementations correctly detect **259 watermark characters**:
- Core watermarks: 17 characters (ZWSP, ZWNJ, ZWJ, ZWNBSP, invisible operators, bidirectional overrides, etc.)
- Variation selectors (FE00-FE0F): 16 chars
- Tag characters (E0020-E007F): 96 chars
- Private Use Area (E000-E07F): 128 chars
- Language tag (E0001): 1 char
- Mongolian separator (180E): 1 char

**Critical fixes in v0.2.0:**
- Fixed PUA range bug (was E000-E007F, corrected to E000-E07F)
- Fixed Node.js code point handling (fromCharCode → fromCodePoint)
- Documented Go flag position requirement (flags before filename)

**Enhanced in v0.3.0:**
- Extended watermark detection in all 6 language implementations
- Integrated AI forensic analysis with extended sanitizers
- Improved detection accuracy with 70+ phrase database

All implementations pass comprehensive watermark test (259/259 detected).

## Performance Characteristics

### Language Performance (sample.txt, 136 replacements)
| Language | Standard Time | Extended Time |
|----------|---------------|---------------|
| Go       | ~0.00004 s    | ~0.00006 s    |
| Rust     | ~0.00008 s    | ~0.00010 s    |
| C++      | ~0.00040 s    | ~0.00050 s    |
| Node.js  | ~0.00046 s    | ~0.00060 s    |
| Python   | ~0.00056 s    | ~0.00070 s    |
| Bun      | ~0.00220 s    | ~0.00280 s    |

## Recommended Usage

### For quick text sanitization
Use standard versions for fastest performance:
```bash
python3 partxtpy/partxt.py input.txt
```

### For exploratory forensic metrics with evidence locations
Use the Python analyzers for exploratory metrics:
```bash
python3 parscgpt-ext.py input.txt   # shows AI EVIDENCE: line numbers + excerpts
python3 parscgptv2.py input.txt     # conservative standard version
```

### For extended exploratory analysis
Extended versions provide additional metrics, but are not reliable authorship detectors:
```bash
python3 partxtpy/partxt-ext.py input.txt
# or for deepest analysis
python3 parscgpt-ext.py input.txt
```

### For cross-language performance comparison
Use batch scripts:
```bash
./run_all.sh input.txt
./run_all_extended.sh input.txt
```

### For reproducible verification
```bash
./tests/test_cross_language.sh
./tests/test_web_parity.sh        # browser demo vs console analyzer
```
