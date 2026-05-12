import re
import math
import sys

from collections import Counter
from statistics import mean, pstdev
from itertools import islice


# =========================================================
# CONFIG
# =========================================================

AI_PHRASES = [
    "however",
    "moreover",
    "overall",
    "in conclusion",
    "it is important to note",
    "additionally",
    "that said",
    "on the other hand",
    "in general",
    "furthermore",
    "therefore",
    "as a result",
    "for example",
    "for instance",
    "ultimately",
    "in summary",
    "notably",
    "meanwhile",
    "consequently",
    "in contrast",
]

UNICODE_SUSPICIOUS = [
    "—",
    "–",
    " ",
    "“",
    "”",
    "•",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "if", "to", "of",
    "in", "on", "for", "is", "are", "was", "were",
    "be", "been", "with", "that", "this", "it",
    "as", "at", "by", "from", "but", "not",
}


# =========================================================
# TEXT HELPERS
# =========================================================

def split_sentences(text):
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def filtered_words(words):
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


# =========================================================
# CORE METRICS
# =========================================================

def lexical_diversity(words):
    return len(set(words)) / len(words) if words else 0


def repetition_score(words):
    counter = Counter(words)

    repeated = sum(v for v in counter.values() if v > 1)

    return repeated / len(words) if words else 0


def entropy(words):
    counter = Counter(words)
    total = len(words)

    if not total:
        return 0

    return -sum(
        (c / total) * math.log2(c / total)
        for c in counter.values()
    )


def burstiness(lengths):
    if len(lengths) < 2:
        return 0

    avg = mean(lengths)

    return pstdev(lengths) / avg if avg else 0


def punctuation_density(text):
    punct = re.findall(r'[,;:()\-\—–]', text)

    return len(punct) / max(len(text), 1)


# =========================================================
# AI PATTERNS
# =========================================================

def ai_phrase_hits(text):
    lower = text.lower()

    return {
        p: lower.count(p)
        for p in AI_PHRASES
        if lower.count(p)
    }


def unicode_stats(text):
    return {
        s: text.count(s)
        for s in UNICODE_SUSPICIOUS
        if text.count(s)
    }


def generate_ngrams(words, n=2):
    return zip(*(islice(words, i, None) for i in range(n)))


def top_ngrams(words, n=2, top_k=10):
    counter = Counter(generate_ngrams(words, n))

    return counter.most_common(top_k)


def sentence_patterns(sentences):
    patterns = []

    for s in sentences:

        words = tokenize(s)

        if not words:
            continue

        pattern = []

        for w in words[:10]:

            if len(w) <= 3:
                pattern.append("S")

            elif len(w) <= 6:
                pattern.append("M")

            else:
                pattern.append("L")

        patterns.append("-".join(pattern))

    return patterns


def pattern_repetition_score(sentences):
    patterns = sentence_patterns(sentences)

    if not patterns:
        return 0

    counter = Counter(patterns)

    repeated = sum(v for v in counter.values() if v > 1)

    return repeated / len(patterns)


# =========================================================
# INTERPRETATION
# =========================================================

def interpret_metric(name, value):

    rules = {

        "diversity": (
            [
                (0.45, "Low lexical diversity → repetitive vocabulary, common in LLM text."),
                (0.6, "Moderate lexical diversity."),
            ],
            "High lexical diversity → richer and more human-like vocabulary."
        ),

        "entropy": (
            [
                (5, "Low entropy → text is statistically predictable."),
                (7, "Moderate entropy."),
            ],
            "High entropy → varied and less predictable writing."
        ),

        "burstiness": (
            [
                (0.35, "Low burstiness → sentence lengths are unnaturally uniform."),
                (0.7, "Moderate burstiness."),
            ],
            "High burstiness → natural variation in sentence structure."
        ),

        "pattern": (
            [
                (0.2, "Low syntax repetition."),
                (0.4, "Moderate syntax repetition."),
            ],
            "High syntax repetition → repeated sentence templates detected."
        ),
    }

    levels, high_msg = rules[name]

    for threshold, msg in levels:
        if value < threshold:
            return msg

    return high_msg


def overall_profile(ai_score, diversity, entropy_score, burst):

    signals = []

    if diversity > 0.6:
        signals.append("high lexical diversity")

    if entropy_score > 7:
        signals.append("high entropy")

    if burst > 0.8:
        signals.append("natural sentence variability")

    if ai_score > 70:
        verdict = "Strong AI-like statistical profile detected."

    elif ai_score > 45:
        verdict = "Mixed profile: contains both human-like and AI-like signals."

    else:
        verdict = "Text statistically appears more human-like."

    return verdict, signals


def suspicious_patterns(phrase_hits, top_trigrams):

    warnings = []

    suspicious = {
        "it is important",
        "in conclusion",
        "overall the analysis",
    }

    for phrase in phrase_hits:
        warnings.append(f"AI-like transition phrase detected: '{phrase}'")

    for phrase, count in top_trigrams:

        if phrase in suspicious:
            warnings.append(
                f"Repeated AI-like trigram: '{phrase}'"
            )

    return warnings


# =========================================================
# MAIN ANALYSIS
# =========================================================

def analyze(text):

    sentences = split_sentences(text)

    words = tokenize(text)

    clean_words = filtered_words(words)

    lengths = [len(tokenize(s)) for s in sentences]

    diversity = lexical_diversity(clean_words)

    repetition = repetition_score(clean_words)

    entropy_score = entropy(clean_words)

    burst = burstiness(lengths)

    punct_density = punctuation_density(text)

    phrase_hits = ai_phrase_hits(text)

    unicode_hits = unicode_stats(text)

    pattern_score = pattern_repetition_score(sentences)

    top_bigrams = top_ngrams(clean_words, 2)

    top_trigrams = top_ngrams(clean_words, 3)

    ai_score = 0

    # =====================================================
    # HEURISTICS
    # =====================================================

    if diversity < 0.45:
        ai_score += 20

    if entropy_score < 5:
        ai_score += 20

    if burst < 0.35:
        ai_score += 15

    if pattern_score > 0.35:
        ai_score += 15

    if repetition > 0.5:
        ai_score += 10

    if len(phrase_hits) >= 3:
        ai_score += 15

    if punct_density > 0.04:
        ai_score += 5

    if unicode_hits:
        ai_score += 5

    ai_score = min(ai_score, 100)

    # =====================================================
    # INTERPRETATION
    # =====================================================

    verdict, signals = overall_profile(
        ai_score,
        diversity,
        entropy_score,
        burst
    )

    warnings = suspicious_patterns(
        phrase_hits,
        [(" ".join(k), v) for k, v in top_trigrams]
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    return {

        "word_count": len(words),

        "sentence_count": len(sentences),

        "avg_sentence_length":
            round(mean(lengths), 2) if lengths else 0,

        "sentence_length_stddev":
            round(pstdev(lengths), 2) if len(lengths) > 1 else 0,

        "lexical_diversity":
            round(diversity, 3),

        "repetition_score":
            round(repetition, 3),

        "entropy":
            round(entropy_score, 3),

        "burstiness":
            round(burst, 3),

        "pattern_repetition_score":
            round(pattern_score, 3),

        "punctuation_density":
            round(punct_density, 4),

        "ai_phrase_hits":
            phrase_hits,

        "unicode_symbols":
            unicode_hits,

        "top_bigrams":
            [(" ".join(k), v) for k, v in top_bigrams],

        "top_trigrams":
            [(" ".join(k), v) for k, v in top_trigrams],

        "estimated_ai_probability":
            f"{ai_score}%",

        "confidence":
            (
                "low" if len(words) < 300
                else "medium" if len(words) < 1000
                else "high"
            ),

        "interpretation": {

            "lexical_diversity":
                interpret_metric("diversity", diversity),

            "entropy":
                interpret_metric("entropy", entropy_score),

            "burstiness":
                interpret_metric("burstiness", burst),

            "syntax_patterns":
                interpret_metric("pattern", pattern_score),
        },

        "overall_profile": {
            "verdict": verdict,
            "signals": signals,
        },

        "suspicious_patterns":
            warnings,
    }


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python3 parscgpt.py <textfile>")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    result = analyze(text)

    print("\n=== AI TEXT FORENSIC ANALYSIS ===\n")

    for k, v in result.items():

        if isinstance(v, dict):

            print(f"{k}:")

            for kk, vv in v.items():
                print(f"  {kk}: {vv}")

        elif isinstance(v, list):

            print(f"{k}:")

            for item in v:
                print(f"  {item}")

        else:
            print(f"{k}: {v}")

    print("\n=== END OF REPORT ===\n")

