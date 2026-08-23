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
--replacement <char>       Replacement character (default: '?')
--remove                  Remove disallowed chars instead of replacing
```

## Key Features

### 11 Core AI Forensic Metrics

1. **Lexical Diversity** — Unique words / total words (after stopword removal)
2. **Repetition Score** — Fraction of words appearing more than once
3. **Entropy** — Shannon entropy of word frequency distribution
4. **Burstiness** — Coefficient of variation of sentence lengths
5. **Pattern Repetition** — Fraction of repeated sentence-length patterns
6. **Punctuation Density** — Punctuation count / total characters
7. **AI Phrase Hits** — Matches against 70+ curated AI-typical phrases
8. **Unicode Symbols** — Count of suspicious Unicode characters
9. **Average Word Length** — Mean length of words in text
10. **Word Length Variance** — Variance in word lengths
11. **Confidence Level** — LOW/MEDIUM/HIGH based on text length

### AI Probability Scoring

The extended versions calculate a comprehensive AI probability score (0-100%) based on weighted analysis of all metrics:

| Metric | Condition | Points |
|--------|-----------|--------|
| Lexical diversity | < 0.45 | +25 |
| Entropy | < 5.0 | +25 |
| Burstiness | < 0.35 | +20 |
| Pattern repetition | > 0.35 | +20 |
| AI phrase hits | ≥ 3 | +20 |
| Repetition score | > 0.5 | +15 |
| Punctuation density | > 0.04 | +5 |
| Unicode symbols | Present | +5 |
| Average word length | < 4.0 | +10 |
| Word length variance | < 1.5 | +8 |

**Total is capped at 100%** with confidence factor adjustment:
- LOW confidence (< 300 words): 80% factor
- MEDIUM confidence (300-999 words): 90% factor  
- HIGH confidence (≥ 1000 words): 100% factor

## Interpretation Guide

### Verdict Categories

| AI Probability | Verdict | Action |
|---------------|---------|--------|
| 60-100% | High probability of AI-generated content | Investigate further, verify source |
| 30-60% | Moderate probability of AI involvement | Review for patterns, check context |
| 10-30% | Low probability of AI-generated content | Likely human, minor AI influence |
| 0-10% | Text appears predominantly human-written | Natural human writing detected |

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

*Times on 197-character test file with 197 replacements*

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
| Core metrics | 11 | 8 | 17 |
| AI phrases | 70+ | 21 | 70+ |
| Probability scoring | ✅ Yes | ✅ Yes | ✅ Yes |
| Confidence levels | ✅ Yes | ✅ Yes | ✅ Yes |
| Signal analysis | ✅ Yes | ✅ Yes | ✅ Yes |
| Advanced metrics | ❌ No | ❌ No | ✅ Yes (6 extra) |

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

- Current version: 0.3.0
- Release date: 2025
- Changelog: See main README.md for version history
