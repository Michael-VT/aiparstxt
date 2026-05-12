import re
import math
from collections import Counter
from statistics import mean, pstdev
from itertools import islice

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

def generate_ngrams(words, n=2):
    return zip(*(islice(words, i, None) for i in range(n)))


def top_ngrams(words, n=2, top_k=10):
    ngrams = generate_ngrams(words, n)

    counter = Counter(ngrams)

    return counter.most_common(top_k)

def burstiness(lengths):
    if len(lengths) < 2:
        return 0

    avg = mean(lengths)

    if avg == 0:
        return 0

    return pstdev(lengths) / avg
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

def split_sentences(text):
    return re.split(r'[.!?]+', text)


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def sentence_lengths(sentences):
    lengths = []

    for s in sentences:
        words = tokenize(s)

        if words:
            lengths.append(len(words))

    return lengths


def lexical_diversity(words):
    if not words:
        return 0

    return len(set(words)) / len(words)


def repetition_score(words):
    counter = Counter(words)

    repeated = sum(v for v in counter.values() if v > 1)

    return repeated / len(words) if words else 0


def entropy(words):
    counter = Counter(words)
    total = len(words)

    if total == 0:
        return 0

    entropy_value = 0

    for count in counter.values():
        p = count / total
        entropy_value -= p * math.log2(p)

    return entropy_value


def ai_phrase_hits(text):
    lower = text.lower()

    hits = {}

    for phrase in AI_PHRASES:
        count = lower.count(phrase)

        if count:
            hits[phrase] = count

    return hits


def unicode_stats(text):
    result = {}

    for symbol in UNICODE_SUSPICIOUS:
        count = text.count(symbol)

        if count:
            result[symbol] = count

    return result


def punctuation_density(text):
    punct = re.findall(r'[,;:()\-\—–]', text)

    return len(punct) / max(len(text), 1)


def analyze(text):
    sentences = split_sentences(text)
    words = tokenize(text)
    lengths = sentence_lengths(sentences)
    
    burstiness_score = burstiness(lengths)
    
    pattern_score = pattern_repetition_score(sentences)
    
    top_bigrams = top_ngrams(words, n=2)
    
    top_trigrams = top_ngrams(words, n=3)

    avg_sentence = mean(lengths) if lengths else 0
    std_sentence = pstdev(lengths) if len(lengths) > 1 else 0

    diversity = lexical_diversity(words)
    repetition = repetition_score(words)
    entropy_score = entropy(words)

    phrase_hits = ai_phrase_hits(text)
    unicode_hits = unicode_stats(text)

    punct_density = punctuation_density(text)

    ai_score = 0

    if std_sentence < 5:
        ai_score += 15

    if diversity < 0.45:
        ai_score += 20

    if repetition > 0.45:
        ai_score += 15

    if entropy_score < 4.5:
        ai_score += 20

    if len(phrase_hits) >= 3:
        ai_score += 15

    if punct_density > 0.04:
        ai_score += 5

    if unicode_hits:
        ai_score += 5
    
    if burstiness_score < 0.35:
        ai_score += 15

    if pattern_score > 0.3:
        ai_score += 15

    ai_score = min(ai_score, 100)

    return {
        "word_count": len(words),
        "sentence_count": len(lengths),
        "avg_sentence_length": round(avg_sentence, 2),
        "sentence_length_stddev": round(std_sentence, 2),
        "lexical_diversity": round(diversity, 3),
        "repetition_score": round(repetition, 3),
        "entropy": round(entropy_score, 3),
        "punctuation_density": round(punct_density, 4),
        "ai_phrase_hits": phrase_hits,
        "unicode_symbols": unicode_hits,
        "burstiness": round(burstiness_score, 3),
        "pattern_repetition_score": round(pattern_score, 3),
        "top_bigrams": [
            (" ".join(k), v) for k, v in top_bigrams
        ],
        "top_trigrams": [
            (" ".join(k), v) for k, v in top_trigrams
        ],
        "estimated_ai_probability": f"{ai_score}%"
    }


if __name__ == "__main__":

    with open("parsaitext.txt", "r", encoding="utf-8") as f:
        sample_text = f.read()

    result = analyze(sample_text)

    print("\n=== AI Text Heuristic Analysis ===\n")

    for k, v in result.items():
        print(f"{k}: {v}")

