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
- **11 core AI forensic metrics** + AI probability scoring
- **70+ AI phrases** detection (vs 21 in standard versions)
- Unicode suspicious character detection
- Statistical AI probability scoring (0-100%)
- Confidence levels based on text length

### 3. Advanced AI Analysis (Python only)
Comprehensive analysis scripts:
- `parscgpt.py` — basic metrics and AI score (legacy)
- `parscgptv1.py` — adds stopword filtering, confidence, interpretation (legacy)
- `parscgptv2.py` — **standard detection** (8 core metrics, 21 phrases)
- `parscgpt-ext.py` — **extended detection** (17 metrics, 70+ phrases, most comprehensive)

## Build & Run Commands

### Build all
```bash
make -C partxtcpp
cargo build --release --manifest-path partxtrs/Cargo.toml
(cd partxtgo && go build -o partxtgo .)
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
./partxtgo/main-ext testdata/sample.txt
./partxtcpp/partxt-ext testdata/sample.txt
node partxtnode/partxt-ext.js testdata/sample.txt
bun run partxtjs/partxt-ext.js testdata/sample.txt
```

### Run AI analytics
```bash
# Standard version (8 metrics, 21 phrases)
python3 parscgptv2.py testdata/sample.txt

# Extended version (17 metrics, 70+ phrases, most comprehensive)
python3 parscgpt-ext.py testdata/sample.txt
```

### Run all + timing comparison
```bash
./run_all.sh testdata/sample.txt
./run_all_extended.sh testdata/sample.txt
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

Digits `0-9`, Latin `A-Za-z`, Russian `А-Яа-я` (incl. Ёё), punctuation `[]{}()-=_+!@#$%&*;'/.,<>'"\`~`, whitespace. Everything else → `?`.

## Analytics Metrics

### Extended Version (parscgpt-ext.py) — 17 metrics ⭐
**Advanced comprehensive analysis:**
- Core 8: lexical_diversity, repetition_score, entropy, burstiness, pattern_repetition_score, punctuation_density, ai_phrase_hits (70+ phrases), unicode_symbols
- Extended 9: avg_word_length, word_length_variance, pronoun_ratio, readability_score, passive_voice_density, adj_noun_pair_diversity, structural_uniformity, quantifier_overuse
- Linguistic: top_bigrams, top_trigrams

### Standard Version (parscgptv2.py) — 8 metrics
**Basic reliable analysis:**
- Core metrics: lexical_diversity, repetition_score, entropy, burstiness, pattern_repetition_score, punctuation_density, ai_phrase_hits (21 phrases), unicode_symbols
- Linguistic: top_bigrams, top_trigrams

### Scoring System
- **Extended**: Weighted sum with text length adaptation (0-100%, confidence-adjusted)
- **Standard**: Threshold-based scoring (0-100%)
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

Semantic: patch (0.0.x) = bug fixes, minor (0.x.0) = meets requirements, major (x.0.0) = significant new features. **Current: 0.3.0**.

### Version History
- **v0.3.0**: Extended AI forensic analytics in all 6 languages, 11/17 metrics, 70+ phrases, weighted scoring
- **v0.2.0**: Watermark detection bug fixes, cross-language support
- **v0.1.0**: Initial multi-language implementation

## Key Files

### Core Analysis
- `parscgpt-ext.py` — **Extended AI forensic analytics** (17 metrics, 70+ phrases, most comprehensive) ⭐
- `parscgptv2.py` — **Standard AI forensic analytics** (8 metrics, 21 phrases, recommended for quick checks)
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

### Language Performance (sample.txt, 197 replacements)
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

### For AI text detection (basic)
Use standard Python analyzer for quick checks:
```bash
python3 parscgptv2.py input.txt
```

### For comprehensive AI analysis (recommended) ⭐
Use extended versions for most accurate detection:
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