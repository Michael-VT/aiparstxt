# AI Text Forensic Analytics — Porting Guide

This document describes the statistical analytics engine implemented in `parscgptv2.py` and provides guidance for porting it to other languages (Rust, Go, C++, Node.js, Bun).

## Overview

The analytics engine performs heuristic forensic analysis of text to estimate the likelihood of AI-generated content. It computes a set of statistical metrics, combines them via a weighted scoring model, and produces an interpreted report with confidence levels.

**Reference implementation**: `parscgptv2.py` (Python, ~490 lines)

---

## Architecture

### Pipeline

```
Input text → Tokenization → Metric computation → Heuristic scoring → Interpretation → Report
```

### Modules

1. **Text helpers** — sentence splitting, tokenization, stopword filtering
2. **Core metrics** — lexical diversity, repetition, entropy, burstiness, punctuation density
3. **AI pattern detection** — phrase matching, n-gram analysis, sentence pattern analysis, Unicode suspicious characters
4. **Interpretation** — metric-level verdicts, overall profile, suspicious pattern warnings
5. **Heuristic scoring** — weighted combination → AI probability estimate

---

## Metrics Reference

### Lexical Diversity

```
lexical_diversity = unique_words / total_words
```

Computed on stopword-filtered words (length > 2). Range: [0, 1]. Higher = more diverse vocabulary. AI text tends to cluster below 0.45.

### Repetition Score

```
repetition_score = repeated_word_count / total_words
```

Count of words appearing more than once, divided by total. Range: [0, 1]. AI text often exceeds 0.5.

### Shannon Entropy

```
entropy = -Σ (count_i / total) * log2(count_i / total)
```

Information-theoretic measure of vocabulary unpredictability. Range: [0, log2(N)]. AI text tends to fall below 5.0.

### Burstiness

```
burstiness = stddev(sentence_lengths) / mean(sentence_lengths)
```

Coefficient of variation of sentence word counts. Human writing varies more — AI text often below 0.35.

### Pattern Repetition Score

Each sentence is encoded as a pattern of Short (≤3 chars), Medium (4-6), Long (7+) word lengths for the first 10 words. Example: `"S-M-L-L-M-S-L-M-L-L"`. The score is the fraction of patterns that appear more than once. AI text often exceeds 0.35.

### Punctuation Density

```
punctuation_density = punctuation_count / total_characters
```

Counts: `,;:()—–`. AI text often exceeds 0.04.

### AI Phrase Hits

Dictionary of matches against a curated list of 21 AI-typical transition phrases: "however", "moreover", "in conclusion", "it is important to note", "furthermore", "therefore", etc.

### Unicode Suspicious Characters

Counts of typographic characters common in AI output: em-dash (`—`), en-dash (`–`), thin space, smart quotes (`""`), bullet (`•`).

### Top N-grams

Most common bigrams and trigrams from stopword-filtered text. Useful for detecting repetitive AI phrasing patterns.

---

## Scoring Model

The AI probability score sums weighted contributions, capped at 100%:

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

Final: `min(score, 100)`

## Confidence Levels

Based on total word count:

| Words | Confidence |
|-------|------------|
| < 300 | low |
| 300-999 | medium |
| ≥ 1000 | high |

---

## Interpretation Rules

Each metric has threshold-based interpretations:

**Lexical diversity**: <0.45 → "Low, repetitive vocabulary, common in LLM text", <0.6 → "Moderate", ≥0.6 → "High, richer and more human-like"

**Entropy**: <5.0 → "Low, statistically predictable", <7.0 → "Moderate", ≥7.0 → "High, varied and less predictable"

**Burstiness**: <0.35 → "Low, unnaturally uniform", <0.7 → "Moderate", ≥0.7 → "High, natural variation"

**Pattern repetition**: <0.2 → "Low", <0.4 → "Moderate", ≥0.4 → "High, repeated templates detected"

---

## Overall Profile

```
if AI score > 70 → "Strong AI-like statistical profile"
if AI score > 45 → "Mixed: both human-like and AI-like signals"
else              → "Text statistically appears more human-like"
```

Positive signals collected: high diversity (>0.6), high entropy (>7), high burstiness (>0.8).

---

## Porting Guide by Language

### Rust

**Recommended crates** (zero external dependencies possible):
- `std::collections::HashMap` for counters
- Split on `[.!?]+` via `regex` crate or manual iteration
- `std::collections::HashSet` for stopwords
- Manual mean/stddev computation (trivial)

**Key considerations**:
- UTF-8 handling is native
- Pattern encoding: use `String` with S/M/L chars
- Performance will be excellent — no special optimization needed

### Go

**Standard library only**:
- `strings.Split` + regex for sentences
- `map[string]int` for counters
- `map[string]bool` for stopwords/phrase sets
- `math` package for log2

**Key considerations**:
- `unicode/utf8` for rune-level iteration
- `sort.Slice` for sorted output
- No generics needed — simple maps suffice

### C++

**Standard library only** (C++20):
- `std::unordered_map<std::string, int>` for counters
- `<regex>` or manual splitting
- `<cmath>` for log2
- `<numeric>` for mean/stddev

**Key considerations**:
- UTF-8 iteration requires care — use a library like `utf8cpp` or iterate byte-by-byte with codecvt
- `std::string_view` for zero-copy token handling
- Pattern encoding with `std::string`

### Node.js / Bun

**No dependencies needed**:
- `String.split()` with regex for sentences
- `Map<string, number>` for counters
- `Set<string>` for stopwords
- `Math.log2` for entropy

**Key considerations**:
- JavaScript handles Unicode well with spread operator `[...str]` for code points
- Use `String.fromCodePoint()` (not `fromCharCode`) for code points > 0xFFFF
- `Intl.Segmenter` (Node 16+) for word segmentation if needed

---

## Configuration

### Stopwords

```python
STOPWORDS = {
    "the", "a", "an", "and", "or", "if", "to", "of",
    "in", "on", "for", "is", "are", "was", "were",
    "be", "been", "with", "that", "this", "it",
    "as", "at", "by", "from", "but", "not",
}
```

### AI Phrases

```python
AI_PHRASES = [
    "however", "moreover", "overall", "in conclusion",
    "it is important to note", "additionally", "that said",
    "on the other hand", "in general", "furthermore",
    "therefore", "as a result", "for example", "for instance",
    "ultimately", "in summary", "notably", "meanwhile",
    "consequently", "in contrast",
]
```

### Suspicious Trigrams

```python
SUSPICIOUS_TRIGRAMS = {
    "it is important",
    "in conclusion",
    "overall the analysis",
}
```

---

## Output Format

```json
{
  "word_count": 198,
  "sentence_count": 11,
  "avg_sentence_length": 18.0,
  "sentence_length_stddev": 9.36,
  "lexical_diversity": 0.832,
  "repetition_score": 0.29,
  "entropy": 6.655,
  "burstiness": 0.52,
  "pattern_repetition_score": 0.0,
  "punctuation_density": 0.0129,
  "ai_phrase_hits": {},
  "unicode_symbols": {"–": 1},
  "top_bigrams": [("data centers", 2), ...],
  "top_trigrams": [("data centers being", 1), ...],
  "estimated_ai_probability": "0%",
  "confidence": "low",
  "interpretation": {
    "lexical_diversity": "High lexical diversity → richer and more human-like vocabulary.",
    "entropy": "Moderate entropy.",
    "burstiness": "Moderate burstiness.",
    "syntax_patterns": "Low syntax repetition."
  },
  "overall_profile": {
    "verdict": "Text statistically appears more human-like.",
    "signals": ["high lexical diversity"]
  },
  "suspicious_patterns": []
}
```

---

## Testing

When porting, validate against these inputs:

1. **Known AI text** — should score >45% (e.g., ChatGPT-generated article)
2. **Known human text** — should score <30% (e.g., manually written prose)
3. **Short text** (<300 words) — confidence should be "low"
4. **Mixed text** — should detect both AI and human signals

Run `parscgptv2.py <file>` and compare your output metric-by-metric against the Python reference.
