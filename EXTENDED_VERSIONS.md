# Extended Versions — Enhanced AI Forensic Analysis

## Overview

The `-ext` versions provide enhanced AI forensic analysis integrated directly into the text sanitizers, available for all 6 language implementations.

## Quick Start

### Run Extended Analyzers

```bash
# Individual extended versions
python3 partxtpy/partxt-ext.py input.txt
cargo run --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext -- input.txt
cd partxtgo && go run main-ext.go ../input.txt
cd partxtcpp && make && ./partxt-ext ../input.txt
node partxtnode/partxt-ext.js input.txt
bun run partxtjs/partxt-ext.js input.txt

# All extended versions at once
./run_all_extended.sh input.txt
```

### Available Options

All extended versions support the same options as standard versions:

```
-o, --output <file>       Output file (default: <input>.ed.txt)
-r, --report <file>       Report file (default: report_<lang>-ext.txt)
--no-edit                 Do not create .ed.txt file
--no-report               Do not create report file
--no-words                Exclude word frequency from report
--remove-watermark        Remove AI watermark characters
```

The common cross-language options are `-o/--output`, `-r/--report`,
`--no-edit`, `--no-report`, `--no-words` and `--remove-watermark`.

## Key Features

### AI Forensic Metrics (v0.4.0 — 18 metrics, spec: `AI_SIGNALS_SPEC.md`)

**Primary structural signals (corpus-validated):**
1. **Sentence-length CV** — coefficient of variation of sentence word counts (AI corpus: 0.27–0.44; human corpus: 0.42–1.5)
2. **Paragraph-length CV** — CV of paragraph word counts (AI: 0.06–0.40; human: 0.45–0.98)
3. **Joint uniformity** — both CVs low simultaneously (33/34 AI vs 0/10 human)
4. **Connective density** — discourse connectives per sentence (multilingual list)

**Core metrics:**
5. **Lexical Diversity** — unique/total words (after stopword removal)
6. **Repetition Score** — distinct words appearing more than once
7. **Entropy** — Shannon entropy of word frequency distribution
8. **Pattern Repetition** — fraction of repeated sentence-length patterns
9. **Punctuation Density** — punctuation count / total characters
10. **AI Phrase Hits** — ~150 curated phrases in 3 tiers (HIGH/MEDIUM/WEAK) across EN/RU/UK/PT
11. **Unicode Symbols** — suspicious Unicode characters

**Extended metrics:** average word length, word length variance, pronoun ratio,
Flesch readability, passive voice density, adjective-noun pair diversity,
structural uniformity, quantifier overuse, confidence level.

**AI EVIDENCE** — every indicator is reported with its location: line number,
excerpt (~110 chars) with the trigger highlighted as `>>>phrase<<<`,
sentence/paragraph length sequences.

### AI Probability Scoring

The extended versions calculate a comprehensive AI probability score (0-100%) based on weighted analysis of all metrics:

Canonical weights (see `AI_SIGNALS_SPEC.md`); summary of the primary signals:

| Signal | Condition | Points |
|--------|-----------|--------|
| Sentence-length CV | < 0.30 / 0.35 / 0.40 / 0.45 / 0.50 | +32 / 26 / 19 / 11 / 5 |
| Paragraph-length CV | < 0.15 / 0.25 / 0.35 / 0.45 | +28 / 22 / 16 / 7 |
| Joint uniformity | both CV < 0.40 / < 0.45 | +14 / 10 |
| HIGH phrases | ≥ 2 / = 1 | +24 / 15 |
| MEDIUM phrases | ≥ 3 / ≥ 1 | +10 / 5 |
| Connective density | ≥ 0.12 / ≥ 0.08 | +13 / 7 |

Plus supporting weights for the core/extended metrics (≤ 15 each).
Guards: sentence CV requires ≥ 15 sentences and ≥ 150 words; paragraph CV
requires ≥ 4 paragraphs of > 15 words.

**Total**: `min(100, total × (0.9 + 0.1 × min(1, words/1000)))`.

**Validation** (34 confirmed AI answers vs 20 human texts, `validation/AI_CORPUS_REPORT.md`):
threshold 50 → recall 93.9%, false positives 0%; threshold 70 → recall 60.6%, FP 0%.

## Interpretation Guide

### Verdict Categories

| AI Probability | Verdict | Action |
|---------------|---------|--------|
| > 70% | Strong AI-like statistical profile | Investigate further, verify source |
| 55-70% | Probable AI-generated text | Review evidence locations, check context |
| 35-55% | Mixed profile | Review AI EVIDENCE section |
| < 35% | Statistically more human-like | Natural human writing likely |

Recommended classification thresholds: 50-55 "probable AI", 70 "strong AI".

### Signal Analysis

#### Positive Indicators (Human-like)
- ✓ High lexical diversity — rich vocabulary variation
- ✓ Good entropy — natural word distribution
- ✓ Good burstiness — natural sentence variation
- ✓ High average word length — appropriate complexity
- ✓ Good word length variance — natural variety

#### Warning Indicators (AI-like)
- ⚠️ Low lexical diversity — limited vocabulary
- ⚠️ Low entropy — unnaturally uniform distribution
- ⚠️ Low burstiness — overly uniform structure
- ⚠️ High pattern repetition — template-like writing
- ⚠️ AI phrase hits — detected AI-typical phrases
- ⚠️ Suspicious Unicode characters — technical markers
- ⚠️ Low average word length — simplified vocabulary
- ⚠️ Low word length variance — uniform complexity

## Report Format

Extended reports include three main sections:

### 1. Basic Analysis
```
--- AI Watermark Analysis ---
Watermark characters removed: 17
Removed watermark character types:
  U+200B: 5
  U+200C: 3
```

### 2. AI Forensic Analysis
```
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

### 3. Word Frequency
```
--- Top Word Frequencies (Filtered) ---
  example: 15
  analysis: 12
  text: 10
```

## Performance Comparison

| Language | Standard Time | Extended Time | Overhead |
|----------|--------------|---------------|----------|
| Go       | ~0.00004 s   | ~0.00006 s    | +50%     |
| Rust     | ~0.00008 s   | ~0.00010 s    | +25%     |
| C++      | ~0.00040 s   | ~0.00050 s    | +25%     |
| Node.js  | ~0.00046 s   | ~0.00060 s    | +30%     |
| Python   | ~0.00056 s   | ~0.00070 s    | +25%     |
| Bun      | ~0.00220 s   | ~0.00280 s    | +27%     |

*Illustrative times on the small sample file with 136 replacements; run the
cross-language test for current measurements.*

## Use Cases

### Academic Integrity
- Detect AI-generated content in student submissions
- Verify authorship of research papers
- Screen for AI plagiarism in essays

### Content Verification
- Identify AI-generated articles or blog posts
- Verify authenticity of user-generated content
- Filter AI-produced content in content moderation

### Quality Assurance
- Assess human involvement in content creation
- Evaluate AI mixing in collaborative writing
- Monitor AI content generation policies

### Forensic Analysis
- Investigate AI watermark presence in documents
- Analyze text characteristics for AI patterns
- Track AI-generated content across platforms

## Best Practices

1. **Text Length**: For accurate results, use texts with ≥300 words for MEDIUM confidence, ≥1000 words for HIGH confidence
2. **Context**: Consider the context when interpreting results — some legitimate uses may score higher
3. **Multiple Sources**: Cross-reference with other detection methods for confirmation
4. **Threshold Tuning**: Adjust scoring thresholds based on your specific use case
5. **Human Review**: Always combine automated analysis with human judgment

## Comparison with Standalone Python Analyzers

| Feature | Extended Versions | parscgptv2.py | parscgpt-ext.py |
|---------|------------------|---------------|-----------------|
| Integrated with sanitizer | ✅ Yes | ❌ No | ❌ No |
| Languages | 6 (all) | 1 (Python) | 1 (Python) |
| Core metrics | 18 | 9 | 18 |
| AI phrases | ~150 (3 tiers, EN/RU/UK/PT) | HIGH+MEDIUM tiers | ~150 (3 tiers) |
| Probability scoring | ✅ Yes | ✅ Yes (conservative) | ✅ Yes |
| Confidence levels | ✅ Yes | ✅ Yes | ✅ Yes |
| Signal analysis | ✅ Yes | ✅ Yes | ✅ Yes |
| Evidence locations | ✅ Yes | ✅ (phrases) | ✅ Yes |
| Advanced metrics | ✅ Yes | ❌ No | ✅ Yes |

**Recommendation**: Use extended versions for integrated analysis, `parscgpt-ext.py` for the deepest linguistic analysis.

## Troubleshooting

### Build Issues

**Rust extended version not found:**
```bash
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext
```

**C++ extended version not found:**
```bash
cd partxtcpp && make partxt-ext
```

### Runtime Issues

**Missing dependencies:**
- Python: Requires Python 3.7+
- Node.js: Requires Node.js 14+
- Bun: Requires latest Bun version
- Rust: Requires Rust 1.70+ (edition 2021)
- Go: Requires Go 1.18+
- C++: Requires C++20 compliant compiler

## Version Information

- Current version: 0.4.3
- Release date: 2026
- Changelog: See main README.md for version history
