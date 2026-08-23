# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aiparstxt** — Multi-language text sanitizer with AI forensic analytics. Six implementations (Python, Rust, Go, C++, Node.js, Bun) that sanitize text files by replacing disallowed characters with '?'. Designed for cross-language performance comparison. Includes Python-only statistical analysis for detecting AI-generated text.

## Two Distinct Tools

### 1. Text Sanitizer (all 6 languages)
CLI tools in `partxtpy/`, `partxtrs/`, `partxtgo/`, `partxtcpp/`, `partxtnode/`, `partxtjs/` — sanitize text, remove watermarks, generate replacement reports.

### 2. AI Forensic Analytics (Python only)
Three scripts in the project root for heuristic AI text detection:
- `parscgpt.py` — basic metrics and AI score
- `parscgptv1.py` — adds stopword filtering, confidence, interpretation
- `parscgptv2.py` — **recommended** — refined scoring, clean output

NOT ported to other languages. See `ANALYTICS_RECOMMENDATIONS.md` for porting guidance.

## Build & Run Commands

### Build all
```bash
make -C partxtcpp
cargo build --release --manifest-path partxtrs/Cargo.toml
(cd partxtgo && go build -o partxtgo .)
# Python, Node.js, Bun — no build needed
```

### Run sanitizer
```bash
python3 partxtpy/partxt.py testdata/sample.txt
./partxtrs/target/release/partxt testdata/sample.txt
./partxtgo/partxtgo testdata/sample.txt
./partxtcpp/partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt
```

### Run AI analytics
```bash
python3 parscgptv2.py testdata/sample.txt
```

### Run all + timing comparison
```bash
./run_all.sh testdata/sample.txt
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

```
python3 parscgptv2.py <textfile>
```

No options. Reads file, prints forensic report to stdout.

## Allowed Characters (Sanitizer)

Digits `0-9`, Latin `A-Za-z`, Russian `А-Яа-я` (incl. Ёё), punctuation `[]{}()-=_+!@#$%&*;'/.,<>'"\`~`, whitespace. Everything else → `?`.

## Analytics Metrics (parscgptv2.py)

Key metrics: lexical_diversity, repetition_score, entropy, burstiness, pattern_repetition_score, punctuation_density, ai_phrase_hits, unicode_symbols, top_bigrams, top_trigrams.

Scoring: weighted sum of threshold conditions → `estimated_ai_probability` (0-100%).
Confidence: low/medium/high based on word count.

## Architecture

### Sanitizer (each implementation)

1. **Parse CLI args** → input file, output path, report path, flags
2. **Read input** as UTF-8
3. **Process**: iterate characters, check against allowed set, replace disallowed with '?', count replacements per character
4. **Word frequency**: split processed text on non-alphanumeric boundaries (keeping `'` and `-`), count occurrences
5. **Write output** (.ed.txt) and **report** (replacements table + word frequency sorted ascending + execution time)

### Analytics (parscgptv2.py)

1. **Tokenize** → sentences, words, filtered words (stopwords removed)
2. **Compute metrics** → diversity, repetition, entropy, burstiness, patterns, punctuation, n-grams
3. **Score** → weighted heuristic → AI probability
4. **Interpret** → per-metric verdicts + overall profile
5. **Output** → structured text report

Report filenames include language prefix: `report_py.txt`, `report_rs.txt`, `report_go.txt`, `report_cpp.txt`, `report_node.txt`, `report_bun.txt`.

## Versioning

Semantic: patch (0.0.x) = bug fixes, minor (0.x.0) = meets requirements, major (x.0.0) = significant new features. Current: 0.2.0.

## Key Files

- `parscgptv2.py` — AI forensic analytics (recommended version)
- `parscgpt.py`, `parscgptv1.py` — earlier analytics variants
- `ANALYTICS_RECOMMENDATIONS.md` — porting guide for analytics to other languages
- `testdata/sample.txt` — test file with diverse Unicode characters
- `run_all.sh` — builds and runs all implementations, shows timing comparison
- `partxtcpp/Makefile` — C++ build (g++, C++20, -O2)
- `partxtrs/Cargo.toml` — Rust project (no external deps)
- `partxtgo/go.mod` — Go module
- `ai-chart.txt` — AI watermark character reference
- `ai-chart-extended.txt` — Comprehensive watermarking reference
- `WATERMARK_FIXES_SUMMARY.md` — v0.2.0 watermark detection bug fixes
- `WATERMARKING_UPDATE_SUMMARY.md` — Original watermark implementation details

## Watermark Removal (v0.2.0)

All 4 implementations (Python, Go, Node.js, Rust) correctly detect **259 watermark characters**:
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

All implementations now pass comprehensive watermark test (17/17 detected).


