#!/usr/bin/env python3
"""
AI Text Forensic Analyzer - Extended Version
Enhanced with advanced linguistic metrics and improved detection accuracy.

v0.4.0:
  - Multilingual AI phrase database (EN/RU/UK/PT) with HIGH/MEDIUM/WEAK tiers
  - Sentence-length and paragraph-length uniformity (CV) as primary signals
  - Connective density metric
  - AI EVIDENCE section: exact locations (line numbers + excerpts) of every
    detected indicator in the text
  - Recalibrated scoring validated on the 34-file AI corpus + 22 human texts
    (see validation/AI_CORPUS_REPORT.md)
"""

import re
import sys
import math
from collections import Counter
from itertools import islice
from statistics import mean, stdev, pstdev


# =========================================================
# EXTENDED CONFIG - Expanded Knowledge Base
# =========================================================

# Tiered multilingual AI phrase database.
# HIGH   - distinctive LLM template phrases, zero hits in the source-based
#          human validation corpus (validation/manifest.json).
# MEDIUM - typical AI connective/register markers, rare in human corpus.
# WEAK   - markers that also occur in human prose; evidence-only, tiny weight.
# Tiers were assigned empirically against the validation corpus; phrases from
# all languages are matched against every text (scripts do not overlap).
AI_PHRASES = {
    "high": [
        # English
        "it is important to note", "it's worth noting", "it is worth noting",
        "it should be emphasized", "it is crucial to understand",
        "it is essential to recognize", "it is noteworthy",
        "plays a crucial role", "plays an important role",
        "plays a significant role", "a testament to",
        "a wide range of", "a variety of",
        "first and foremost", "last but not least",
        "in conclusion", "to summarize", "in summary",
        # Russian
        "стоит отметить", "следует отметить", "необходимо отметить",
        "важно отметить", "важно понимать", "играет важную роль",
        "играет ключевую роль", "играет значительную роль",
        "играет существенную роль", "является одним из",
        "одним из важнейших", "одним из основных", "одной из ключевых",
        "ключевую роль", "существенную роль", "в значительной степени",
        "в заключение", "подводя итог", "широкий спектр",
        "по праву считается", "многочисленные исследования",
        # Ukrainian
        "варто зазначити", "слід зазначити", "необхідно зазначити",
        "важливо зазначити", "відіграє важливу роль",
        "відіграє ключову роль", "є одним із",
        "однією з найважливіших", "одним із основних",
        "значною мірою", "у висновку", "підсумовуючи",
        "широкий спектр", "ключову роль", "істотну роль",
        # Portuguese
        "vale ressaltar", "vale destacar", "é importante destacar",
        "é importante notar", "desempenha um papel",
        "desempenham um papel", "de grande importância",
        "em conclusão", "para concluir", "ampla gama",
        "ampla variedade", "ao longo dos anos",
        "nos dias de hoje", "cada vez mais",
    ],
    "medium": [
        # English
        "moreover", "furthermore", "additionally", "consequently",
        "subsequently", "notably", "ultimately", "in essence",
        "fundamentally", "essentially", "on the other hand",
        "for instance", "as a result", "therefore", "overall",
        # Russian
        "более того", "с одной стороны", "с другой стороны",
        "во-первых", "во-вторых", "также как и", "наконец",
        # Ukrainian
        "крім того", "більше того", "з одного боку", "з іншого боку",
        "по-перше", "по-друге", "нарешті",
        # Portuguese
        "além disso", "dessa forma", "deste modo", "por um lado",
        "em primeiro lugar", "em segundo lugar", "de modo geral",
        "em termos gerais", "não obstante",
        "um dos mais", "uma das mais",
    ],
    "weak": [
        # English
        "however", "various", "relatively", "somewhat", "quite", "rather",
        "fairly", "significantly", "considerably", "generally", "in general",
        "for example",
        # Russian
        "кроме того", "при этом", "однако", "следовательно",
        "соответственно", "многочисленные", "разнообразные",
        "сравнительно", "достаточно", "например", "таким образом",
        "в частности",
        # Ukrainian
        "при цьому", "однак", "отже", "численні", "різноманітні",
        "порівняно", "наприклад", "таким чином", "зокрема",
        # Portuguese
        "no entanto", "diversas", "diversos", "relativamente",
        "bastante", "por exemplo", "em resumo", "por outro lado",
        "portanto",
    ],
}

# Discourse connectives (all languages merged); used for connective_density.
CONNECTIVES = [
    # English
    "however", "moreover", "furthermore", "additionally", "therefore",
    "thus", "consequently", "for example", "for instance", "in addition",
    "similarly", "meanwhile", "overall", "as a result", "on the other hand",
    # Russian
    "однако", "при этом", "кроме того", "более того", "также",
    "таким образом", "следовательно", "поэтому", "в частности", "например",
    "во-первых", "во-вторых", "наконец", "в итоге", "в результате",
    "с одной стороны",
    # Ukrainian
    "однак", "при цьому", "крім того", "більше того", "також", "отже",
    "тому", "зокрема", "наприклад", "по-перше", "по-друге", "нарешті",
    "у результаті", "з одного боку", "таким чином",
    # Portuguese
    "no entanto", "além disso", "portanto", "assim", "por exemplo",
    "dessa forma", "em primeiro lugar", "em segundo lugar",
    "por conseguinte", "por outro lado", "deste modo",
]

AI_PASSIVE_PATTERNS = [
    "is considered to be", "are considered to be",
    "is often said to be", "are often said to be",
    "is generally regarded as", "are generally regarded as",
    "is typically characterized by", "are typically characterized by",
    "is commonly associated with", "are commonly associated with",
    "is widely recognized as", "are widely recognized as",
    "is frequently observed to", "are frequently observed to",
    "is usually understood to", "are usually understood to",
]

AI_REPETITIVE_PATTERNS = [
    "in order to", "for the purpose of", "with the aim of",
    "in the context of", "in the case of", "in the event of",
    "on the basis of", "in light of", "in view of",
    "in terms of", "with respect to", "in regard to",
]

UNICODE_SUSPICIOUS = [
    "—", "–", "“", "”", "‘", "’",
    "…", "•", "→", "←", "↑", "↓",
    "©", "®", "™", "°", "±", "×", "÷",
]

STOPWORDS = {
    # English stopwords
    "the", "a", "an", "and", "or", "but", "if", "then",
    "else", "when", "at", "from", "by", "on", "off", "for",
    "in", "out", "over", "to", "into", "with", "about", "against",
    "between", "through", "during", "before", "after", "above",
    "below", "up", "down", "of", "off", "again", "further",
    "then", "once", "here", "there", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "should", "now",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves", "he", "him",
    "his", "himself", "she", "her", "hers", "herself", "it", "its",
    "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "having", "do", "does", "did", "doing",

    # Russian stopwords
    "и", "в", "во", "не", "на", "я", "с", "что", "а", "как",
    "его", "она", "оно", "к", "но", "они", "мы", "вы", "бы",
    "был", "было", "быть", "если", "это", "того", "потом",
    "себя", "чтобы", "от", "так", "для", "тем", "под", "это",
    "когда", "же", "ну", "пока", "еще", "были", "который",
    "того", "своей", "или", "тебя", "через", "ни",
    "ему", "будет", "них", "там", "ее", "им", "про",
    "этом", "этому", "куда", "этого", "раз",
    "можно", "два", "где", "ли", "без", "чем", "эти", "нас",
    "за", "своих", "какой", "сам", "всех",
    "любой", "один", "между", "была", "вас", "чей",
    "которой", "сейчас", "также", "свои",
    "ей", "которого", "либо", "ваш", "нужно",
    "каждый", "будет", "том", "потому",
    "дело", "после", "над", "очень",
    "даже", "вам", "кроме", "моего", "хоть",
    "чего", "свой", "впрочем", "он", "него", "ваша", "затем",
    "которые", "твой", "кого", "их", "все", "её",
    "может", "такой", "кому", "зачем", "впереди",
    "мой", "хотя", "другой",
    "твоего", "твоей", "лишь",
    "никогда", "перед", "каких",
    "тоже", "кое-кого",
    "эту", "пять", "дальше", "почему",
    "вашей", "вторых", "каждой",
    "каждое", "твоих", "мной",
    "ним", "вами", "мною", "тобой", "ею", "тобою",
    "собой", "ими", "о", "об",
    "обо", "ото", "из", "изо", "ко", "по",
    "при", "ради", "сквозь",
    "у", "из-за", "из-под", "вокруг", "позади",
    "посреди", "против", "среди", "шесть", "семь",
    "восемь", "девять", "десять", "нуль", "ноль",
    "три", "четыре", "миллион", "миллиарда",
}

# =========================================================
# SCORING WEIGHTS (v0.4.0) - canonical values, see AI_SIGNALS_SPEC.md
# =========================================================

# Primary structural signals (corpus-validated):
#   sentence-length CV: AI corpus 0.27-0.44, human corpus 0.42-1.5
#   paragraph-length CV: AI corpus 0.06-0.40, human corpus 0.45-0.98
SENT_CV_TIERS = [(0.30, 32), (0.35, 26), (0.40, 19), (0.45, 11), (0.50, 5)]
PARA_CV_TIERS = [(0.15, 28), (0.25, 22), (0.35, 16), (0.45, 7)]
# Joint uniformity bonus: BOTH sentence and paragraph CV low - 33/34 AI files
# in the corpus have both < 0.45, 0/10 human files (where computable).
JOINT_CV_TIERS = [(0.40, 14), (0.45, 10)]
HIGH_PHRASE_SCORES = (24, 15)   # (>=2 hits, ==1 hit)
MEDIUM_PHRASE_SCORES = (10, 5)  # (>=3 hits, >=1 hit)
WEAK_PHRASE_SCORE = 4           # >=4 hits
CONNECTIVE_TIERS = [(0.12, 13), (0.08, 7)]  # connectives per sentence
# Template header repetition: verbatim-repeated short non-punctuated lines
# (e.g. "Что верно" x7, "Итог" x7 in structured LLM answers). Zero hits in
# the human validation corpus; the same template-reuse principle as
# pattern_repetition, applied to lines instead of sentences.
TEMPLATE_HEADER_MIN_REPEATS = 3
TEMPLATE_HEADER_SCORES = (14, 8)  # (>=2 distinct templates or >=10 repeats, >=3 repeats)
# Guards: CV signals are unreliable on tiny texts. Instead of a hard cutoff
# (which silently made short AI texts score as "human"), tier points are
# scaled by statistical reliability: min(1, n/SENTENCE_TARGET) etc.
SENT_CV_MIN_SENTENCES = 5    # below this, sentence CV is pure noise -> 0
SENT_CV_FULL_SENTENCES = 15  # full weight from this many sentences on
PARA_CV_MIN_PARAGRAPHS = 3   # below this, paragraph CV is not computed
PARA_CV_FULL_PARAGRAPHS = 4
MIN_WORDS_FOR_CV = 40
FULL_WORDS_FOR_CV = 150


# =========================================================
# ADVANCED TEXT HELPERS
# =========================================================

def split_sentences(text):
    """Split text into sentences with improved handling."""
    # Handle common abbreviations
    text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\.', r'\1<DOT>', text)
    sentences = [s.strip().replace('<DOT>', '.') for s in re.split(r'[.!?]+', text)]
    return [s for s in sentences if s.strip() and len(s) > 3]

def tokenize(text):
    """Tokenize text into words."""
    return re.findall(r"\b\w+\b", text.lower())

def filtered_words(words):
    """Filter out stopwords and short words."""
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def calculate_word_lengths(words):
    """Calculate individual word lengths."""
    return [len(word) for word in words if word]

def analyze_pronouns(words):
    """Analyze pronoun usage patterns."""
    pronouns = {
        'first_person': ['i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves'],
        'second_person': ['you', 'your', 'yours', 'yourself', 'yourselves'],
        'third_person': ['he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                        'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'],
        'demonstrative': ['this', 'that', 'these', 'those'],
        'indefinite': ['anyone', 'anything', 'everyone', 'everything', 'someone', 'something',
                      'noone', 'nothing', 'each', 'every', 'either', 'neither', 'both', 'few', 'many', 'several'],
    }

    total_pronouns = 0
    category_counts = {cat: 0 for cat in pronouns.keys()}

    for word in words:
        lower_word = word.lower()
        for category, pronoun_list in pronouns.items():
            if lower_word in pronoun_list:
                category_counts[category] += 1
                total_pronouns += 1
                break

    return {
        'total': total_pronouns,
        'ratio': total_pronouns / len(words) if words else 0,
        'categories': category_counts
    }

def detect_language(text):
    """Rough language detection for en/ru/uk/pt (used for reporting only)."""
    lower = text.lower()
    cyrillic = sum(1 for c in lower if 'а' <= c <= 'я' or 'ђ' <= c <= 'ї')
    latin = sum(1 for c in lower if 'a' <= c <= 'z')
    if cyrillic > latin:
        uk_markers = lower.count('і') + lower.count('ї') + lower.count('є') + lower.count('ґ')
        words = len(lower.split())
        if words and uk_markers / words > 0.01:
            return 'uk'
        return 'ru'
    pt_markers = sum(lower.count(c) for c in 'ãçêõáâóô')
    return 'pt' if pt_markers > 3 else 'en'

def line_of_offset(text, offset):
    """1-based line number of a character offset."""
    return text.count('\n', 0, offset) + 1

def truncate_middle(s, width=110):
    """Truncate a long string in the middle, keeping both ends."""
    if len(s) <= width:
        return s
    half = width // 2 - 5
    return s[:half] + ' ... ' + s[-half:]


# =========================================================
# EXTENDED CORE METRICS
# =========================================================

def lexical_diversity(words):
    """Calculate vocabulary diversity (original metric)."""
    return len(set(words)) / len(words) if words else 0

def avg_word_length(words):
    """Calculate average word length - AI tends to use simpler words."""
    lengths = calculate_word_lengths(words)
    return mean(lengths) if lengths else 0

def word_length_variance(words):
    """Calculate variance in word lengths - AI texts are more uniform."""
    lengths = calculate_word_lengths(words)
    return stdev(lengths) if len(lengths) > 1 else 0

def repetition_score(words):
    """Calculate word repetition (original metric)."""
    counter = Counter(words)
    repeated = sum(1 for count in counter.values() if count > 1)
    return repeated / len(words) if words else 0

def entropy(words):
    """Calculate Shannon entropy (original metric)."""
    counter = Counter(words)
    total = len(words)
    if total == 0:
        return 0

    entropy_value = -sum(
        (count / total) * math.log2(count / total)
        for count in counter.values()
    )
    return entropy_value

def burstiness(lengths):
    """Calculate sentence length variation (original metric).

    This is the coefficient of variation (pstdev/mean) of sentence word
    counts: uniformly-sized sentences (low CV) are a strong AI signal."""
    if len(lengths) < 2:
        return 0

    avg = mean(lengths)
    return pstdev(lengths) / avg if avg else 0

def paragraph_lengths(text):
    """Word counts of substantive paragraphs (>15 words)."""
    paragraphs = [p for p in re.split(r'\n\s*\n', text) if len(p.split()) > 15]
    return [len(p.split()) for p in paragraphs]

def paragraph_uniformity(text):
    """CV of paragraph word counts - AI paragraphs are unnaturally equal.

    Returns (cv, n_paragraphs); cv is None below PARA_CV_MIN_PARAGRAPHS."""
    lengths = paragraph_lengths(text)
    if len(lengths) < PARA_CV_MIN_PARAGRAPHS:
        return None
    return burstiness(lengths)

def connective_density(sentences):
    """Discourse connectives per sentence (all languages merged)."""
    if not sentences:
        return 0
    total = 0
    for sent in sentences:
        lower = sent.lower()
        total += sum(1 for c in CONNECTIVES if c in lower)
    return total / len(sentences)

def template_header_repetition(text):
    """Verbatim-repeated short header-like lines - structured LLM answers
    reuse section templates ("Что верно" x7, "Итог" x7).

    Returns (total_repeats, distinct_templates, occurrences) where
    occurrences is [(line, count, first_line_no)]."""
    counter = Counter()
    first_line = {}
    for i, raw in enumerate(text.split('\n'), 1):
        line = raw.strip()
        if (4 <= len(line) <= 60 and 1 <= len(line.split()) <= 8
                and line[-1] not in '.!?:;,…"»„'
                and not line[0].isdigit()):
            counter[line] += 1
            first_line.setdefault(line, i)
    occurrences = []
    total = 0
    distinct = 0
    for line, count in counter.items():
        if count >= TEMPLATE_HEADER_MIN_REPEATS:
            total += count
            distinct += 1
            occurrences.append((line, count, first_line[line]))
    occurrences.sort(key=lambda o: -o[1])
    return total, distinct, occurrences

def promotional_register(text):
    """Emoji- and exclamation-heavy promotional/social register detection.

    Not an AI score signal: both AI hype posts and human SMM copy look like
    this. Used ONLY to abstain honestly - the statistical signals are
    calibrated on plain prose and do not transfer to this genre."""
    words = len(text.split())
    emoji = sum(1 for c in text if ord(c) >= 0x2600)
    excl_density = text.count('!') / words if words else 0
    is_promo = emoji >= 5 and excl_density >= 0.02
    return emoji, excl_density, is_promo

def punctuation_density(text):
    """Calculate punctuation density (original metric)."""
    punct = re.findall(r'[,;:()\-\—–]', text)
    return len(punct) / max(len(text), 1)

def readability_score(_text, words, sentences):
    """Calculate Flesch Reading Ease score - AI texts are often 'too readable'."""
    if not words or not sentences:
        return 0

    # Count syllables (simplified estimation)
    syllable_count = 0
    for word in words:
        syllable_count += max(1, sum(1 for char in word.lower() if char in 'aeiouy'))

    # Flesch Reading Ease formula
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables_per_word = syllable_count / len(words)

    flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    return max(0, min(100, flesch))

def passive_voice_density(text):
    """Detect passive voice constructions - AI uses more passive voice."""
    passive_count = 0
    text_lower = text.lower()

    for pattern in AI_PASSIVE_PATTERNS:
        passive_count += text_lower.count(pattern)

    return passive_count / max(len(text.split()), 1)

def adj_noun_pair_diversity(words):
    """Calculate diversity of adjective-noun pairs - AI has limited combinations."""
    # Simplified POS tagging based on common suffixes
    adj_indicators = ['al', 'ble', 'cal', 'ful', 'ic', 'ive', 'less', 'ous']
    noun_indicators = ['er', 'ism', 'ment', 'ness', 'tion', 'ship', 'cy', 'dom']

    adjectives = set(w for w in words if any(w.endswith(ind) for ind in adj_indicators))
    nouns = set(w for w in words if any(w.endswith(ind) for ind in noun_indicators))

    # Count unique adj-noun pairs
    pairs = set()
    for i in range(len(words) - 1):
        if words[i] in adjectives and words[i+1] in nouns:
            pairs.add(f"{words[i]} {words[i+1]}")

    total_possible = len(adjectives) * len(nouns) if adjectives and nouns else 1
    return len(pairs) / total_possible if total_possible > 0 else 0

def structural_uniformity(sentences):
    """Measure how uniform sentence structures are - AI prefers templates."""
    if len(sentences) < 3:
        return 0

    # Analyze sentence starts
    starts = []
    for sent in sentences:
        words = sent.split()
        if words:
            # Extract first two words as structural pattern
            pattern = ' '.join(words[:2]).lower()
            starts.append(pattern)

    start_counter = Counter(starts)
    # Calculate how repetitive sentence starts are
    repeated_starts = sum(1 for count in start_counter.values() if count > 1)

    return repeated_starts / len(sentences) if sentences else 0

def quantifier_overuse(text):
    """Detect overuse of quantifiers and qualifiers - AI hedge words."""
    quantifiers = [
        'relatively', 'somewhat', 'quite', 'rather', 'fairly',
        'reasonably', 'comparatively', 'moderately', 'substantially',
        'considerably', 'significantly', 'notably', 'remarkably',
    ]

    text_lower = text.lower()
    quant_count = sum(text_lower.count(q) for q in quantifiers)
    word_count = len(text.split())

    return quant_count / max(word_count, 1)


# =========================================================
# ENHANCED AI PATTERNS
# =========================================================

def ai_phrase_hits(text):
    """Extended AI phrase detection across tiers.

    Returns (flat_hits, tier_counts, occurrences) where occurrences is a list
    of (tier, phrase, offset) used for evidence reporting."""
    lower = text.lower()
    hits = []
    tier_counts = {'high': 0, 'medium': 0, 'weak': 0}
    occurrences = []

    for tier in ('high', 'medium', 'weak'):
        for phrase in AI_PHRASES[tier]:
            start = 0
            found = 0
            while True:
                idx = lower.find(phrase, start)
                if idx == -1:
                    break
                found += 1
                if found <= 3:  # cap stored occurrences per phrase
                    occurrences.append((tier, phrase, idx))
                start = idx + len(phrase)
            if found:
                hits.append(phrase)
                tier_counts[tier] += found

    return hits, tier_counts, occurrences

def repetitive_pattern_hits(text):
    """Detect repetitive AI patterns."""
    lower = text.lower()
    hits = []

    for pattern in AI_REPETITIVE_PATTERNS:
        if pattern in lower:
            hits.append(pattern)

    return hits

def unicode_stats(text):
    """Unicode suspicious characters (original metric)."""
    result = {}
    for char in UNICODE_SUSPICIOUS:
        count = text.count(char)
        if count > 0:
            result[char] = count
    return result

def generate_ngrams(words, n=2):
    """Generate n-grams (original metric)."""
    return zip(*(islice(words, i, None) for i in range(n)))

def top_ngrams(words, n=2, top_k=10):
    """Get top n-grams with proper string formatting."""
    ngram_list = list(generate_ngrams(words, n))
    counter = Counter([' '.join(ngram) for ngram in ngram_list])
    return counter.most_common(top_k)



def sentence_patterns(sentences):
    """Analyze sentence length patterns (original metric)."""
    patterns = []
    for sent in sentences:
        words = sent.split()
        length = len(words)

        if length <= 10:
            patterns.append('S')
        elif length <= 20:
            patterns.append('M')
        else:
            patterns.append('L')

    return patterns

def pattern_repetition_score(sentences):
    """Calculate pattern repetition (original metric)."""
    patterns = sentence_patterns(sentences)
    if not patterns:
        return 0

    pattern_counter = Counter(patterns)
    repeated = sum(1 for count in pattern_counter.values() if count > 1)

    return repeated / len(patterns) if patterns else 0


# =========================================================
# EVIDENCE COLLECTION (v0.4.0) - where in the text the signals are
# =========================================================

def build_evidence(text, sentences, phrase_occurrences, sent_cv, para_cv, conn_density,
                   template_occurrences=None):
    """Collect located indicators: line numbers + highlighted excerpts.

    Every entry: {'type', 'detail', 'line', 'excerpt'}. Sorted by severity."""
    evidence = []
    words_total = len(text.split())

    # Sentence spans with line numbers (char offsets are into original text)
    lower = text.lower()

    def excerpt_for(idx, phrase):
        """Sentence containing offset idx, with the phrase highlighted."""
        sent_start = max(text.rfind('. ', 0, idx), text.rfind('! ', 0, idx),
                         text.rfind('? ', 0, idx), text.rfind('\n', 0, idx)) + 1
        sent_end = min([p for p in (text.find('. ', idx), text.find('! ', idx),
                                    text.find('? ', idx), text.find('\n', idx)) if p != -1]
                       + [len(text)])
        fragment = text[sent_start:sent_end].strip()
        f_lower = fragment.lower()
        pos = f_lower.find(phrase)
        if pos == -1:
            return truncate_middle(fragment)
        if len(fragment) > 110:
            # keep a window centered on the phrase, not on the sentence
            w_left, w_right = 45, 60
            start = max(0, pos - w_left)
            end = min(len(fragment), pos + len(phrase) + w_right)
            prefix = '... ' if start > 0 else ''
            suffix = ' ...' if end < len(fragment) else ''
            fragment = prefix + fragment[start:end] + suffix
            pos = pos - start + len(prefix)
        return (fragment[:pos] + '>>>' + fragment[pos:pos + len(phrase)]
                + '<<<' + fragment[pos + len(phrase):])

    # 1. Phrase hits with locations (high tier first)
    shown = 0
    for tier, phrase, idx in sorted(phrase_occurrences, key=lambda o: ('high', 'medium', 'weak').index(o[0])):
        if shown >= 10:
            break
        label = {'high': 'HIGH-risk', 'medium': 'typical', 'weak': 'weak'}[tier]
        evidence.append({
            'type': 'phrase',
            'detail': f"{label} AI phrase '{phrase}'",
            'line': line_of_offset(text, idx),
            'excerpt': excerpt_for(idx, phrase),
        })
        shown += 1

    # 1b. Repeated template headers (structured-answer genre)
    for line, count, line_no in (template_occurrences or [])[:4]:
        evidence.append({
            'type': 'template',
            'detail': f"repeated template header '{line}' ×{count}",
            'line': line_no,
            'excerpt': None,
        })

    # 2. Sentence-length uniformity
    if sent_cv is not None and sent_cv < 0.50 and words_total >= MIN_WORDS_FOR_CV:
        lengths = [len(s.split()) for s in sentences if s.split()]
        evidence.append({
            'type': 'uniformity',
            'detail': (f"sentence lengths are uniform: CV={sent_cv:.2f} "
                       f"(human prose is typically > 0.50); first lengths: "
                       + ' '.join(str(l) for l in lengths[:25])),
            'line': None,
            'excerpt': None,
        })

    # 3. Paragraph-length uniformity
    if para_cv is not None and para_cv < 0.45:
        lengths = paragraph_lengths(text)
        evidence.append({
            'type': 'uniformity',
            'detail': (f"paragraph lengths are uniform: CV={para_cv:.2f} across "
                       f"{len(lengths)} paragraphs (human prose is typically > 0.50); "
                       "lengths: " + ' '.join(str(l) for l in lengths[:20])),
            'line': None,
            'excerpt': None,
        })

    # 4. Connective overuse with example sentences
    if conn_density >= 0.10 and sentences:
        ranked = []
        for i, sent in enumerate(sentences):
            lower_sent = sent.lower()
            n = sum(1 for c in CONNECTIVES if c in lower_sent)
            if n >= 2:
                ranked.append((n, i, sent))
        ranked.sort(reverse=True)
        for n, i, sent in ranked[:2]:
            evidence.append({
                'type': 'connective',
                'detail': f"sentence carries {n} discourse connectives",
                'line': None,
                'excerpt': truncate_middle(sent.strip(), 130),
            })

    # 5. Most suspicious sentences (phrase + connective markers per sentence)
    sentence_scores = []
    for sent in sentences:
        lower_sent = sent.lower()
        markers = 0
        for tier in ('high', 'medium', 'weak'):
            weight = {'high': 3, 'medium': 2, 'weak': 1}[tier]
            markers += weight * sum(1 for p in AI_PHRASES[tier] if p in lower_sent)
        markers += sum(1 for c in CONNECTIVES if c in lower_sent)
        sentence_scores.append((markers, sent))
    sentence_scores.sort(key=lambda x: -x[0])
    for markers, sent in sentence_scores[:3]:
        if markers >= 2:
            idx = lower.find(sent[:40].lower())
            evidence.append({
                'type': 'sentence',
                'detail': f"sentence with {markers} AI markers",
                'line': line_of_offset(text, idx) if idx != -1 else None,
                'excerpt': truncate_middle(sent.strip(), 130),
            })

    return evidence


# =========================================================
# ENHANCED SCORING SYSTEM
# =========================================================

def calculate_ai_score(metrics, text_length):
    """
    Advanced weighted scoring system with text length adaptation.
    Returns score 0-100 with confidence intervals.
    """

    # Base scoring with improved weights
    scores = {
        'lexical_diversity': 0,
        'entropy': 0,
        'sentence_cv': 0,
        'paragraph_cv': 0,
        'joint_uniformity': 0,
        'pattern_repetition': 0,
        'repetition': 0,
        'punctuation': 0,
        'ai_phrases': 0,
        'connectives': 0,
        'template_headers': 0,
        'unicode': 0,

        # Supporting metrics
        'avg_word_length': 0,
        'word_length_variance': 0,
        'pronoun_ratio': 0,
        'readability': 0,
        'passive_voice': 0,
        'adj_noun_diversity': 0,
        'structural_uniformity': 0,
        'quantifier_overuse': 0,
    }

    # --- Primary structural signals (v0.4.0) ---
    # Tier points are scaled by statistical reliability of the sample
    # (short texts get partial credit instead of a silent zero).
    sent_cv = metrics['burstiness']
    n_sents = metrics['sentence_count']
    sent_scale = (min(1.0, n_sents / SENT_CV_FULL_SENTENCES)
                  * min(1.0, text_length / FULL_WORDS_FOR_CV))
    if n_sents >= SENT_CV_MIN_SENTENCES and text_length >= MIN_WORDS_FOR_CV:
        for threshold, points in SENT_CV_TIERS:
            if sent_cv < threshold:
                scores['sentence_cv'] = int(round(points * sent_scale))
                break

    para_cv = metrics.get('paragraph_uniformity_cv')
    para_scale = 0.0
    if para_cv is not None:
        n_paras = metrics.get('paragraph_count', PARA_CV_FULL_PARAGRAPHS)
        para_scale = min(1.0, n_paras / PARA_CV_FULL_PARAGRAPHS)
        for threshold, points in PARA_CV_TIERS:
            if para_cv < threshold:
                scores['paragraph_cv'] = int(round(points * para_scale))
                break

    # Joint uniformity: both sentence and paragraph sizes unusually equal
    if (para_cv is not None and scores['sentence_cv'] > 0):
        for threshold, points in JOINT_CV_TIERS:
            if sent_cv < threshold and para_cv < threshold:
                scores['joint_uniformity'] = int(round(points * min(sent_scale, para_scale)))
                break

    # --- Tiered phrase scores ---
    tiers = metrics['ai_phrase_tiers']
    if tiers['high'] >= 2:
        scores['ai_phrases'] = HIGH_PHRASE_SCORES[0]
    elif tiers['high'] == 1:
        scores['ai_phrases'] = HIGH_PHRASE_SCORES[1]
    elif tiers['medium'] >= 3:
        scores['ai_phrases'] = MEDIUM_PHRASE_SCORES[0]
    elif tiers['medium'] >= 1:
        scores['ai_phrases'] = MEDIUM_PHRASE_SCORES[1]
    elif tiers['weak'] >= 4:
        scores['ai_phrases'] = WEAK_PHRASE_SCORE

    # --- Connective density ---
    conn = metrics['connective_density']
    for threshold, points in CONNECTIVE_TIERS:
        if conn >= threshold:
            scores['connectives'] = points
            break

    # --- Template header repetition (structured-answer genre) ---
    tmpl = metrics.get('template_header_repetition', {'total': 0, 'distinct': 0})
    if tmpl['distinct'] >= 2 or tmpl['total'] >= 10:
        scores['template_headers'] = TEMPLATE_HEADER_SCORES[0]
    elif tmpl['total'] >= TEMPLATE_HEADER_MIN_REPEATS:
        scores['template_headers'] = TEMPLATE_HEADER_SCORES[1]

    # --- Original statistical metrics (supporting weight) ---
    diversity = metrics['lexical_diversity']
    if diversity < 0.45:
        scores['lexical_diversity'] = 15
    elif diversity < 0.55:
        scores['lexical_diversity'] = 8

    entropy_score = metrics['entropy']
    if entropy_score < 5.0:
        scores['entropy'] = 15
    elif entropy_score < 6.5:
        scores['entropy'] = 8

    pattern_rep = metrics['pattern_repetition_score']
    if pattern_rep > 0.35:
        scores['pattern_repetition'] = 10

    rep = metrics['repetition_score']
    if rep > 0.5:
        scores['repetition'] = 8

    punct = metrics['punctuation_density']
    if punct > 0.04:
        scores['punctuation'] = 4

    if metrics['unicode_stats']:
        scores['unicode'] = 4

    # --- Advanced linguistic metrics (supporting weight) ---
    avg_word_len = metrics['avg_word_length']
    if avg_word_len < 4.0:
        scores['avg_word_length'] = 5
    elif avg_word_len < 4.5:
        scores['avg_word_length'] = 3

    word_var = metrics['word_length_variance']
    if word_var < 1.5:
        scores['word_length_variance'] = 4

    pronoun_ratio = metrics['pronoun_analysis']['ratio']
    if pronoun_ratio > 0.15:
        scores['pronoun_ratio'] = 4

    readability = metrics['readability_score']
    if readability > 70:
        scores['readability'] = 5
    elif readability > 60:
        scores['readability'] = 3

    passive = metrics['passive_voice_density']
    if passive > 0.05:
        scores['passive_voice'] = 4

    adj_noun_div = metrics['adj_noun_pair_diversity']
    if adj_noun_div < 0.3:
        scores['adj_noun_diversity'] = 3

    struct_unif = metrics['structural_uniformity']
    if struct_unif > 0.4:
        scores['structural_uniformity'] = 4

    quant_overuse = metrics['quantifier_overuse']
    if quant_overuse > 0.02:
        scores['quantifier_overuse'] = 3

    # Text length adaptation - longer texts get more reliable scores
    length_factor = min(1.0, text_length / 1000)

    # Calculate total with length adjustment
    total = sum(scores.values())
    adjusted_total = total * (0.9 + 0.1 * length_factor)

    return min(100, adjusted_total), scores


# =========================================================
# ENHANCED INTERPRETATION
# =========================================================

def interpret_metric(name, value):
    """Enhanced metric interpretation with more granular feedback."""

    rules = {
        "diversity": (
            [
                (0.35, "Very low lexical diversity → highly repetitive vocabulary, strong AI indicator."),
                (0.45, "Low lexical diversity → repetitive vocabulary, common in LLM text."),
                (0.55, "Moderate lexical diversity → some repetition present."),
                (0.65, "Good lexical diversity → reasonable vocabulary range."),
            ],
            "High lexical diversity → rich and varied vocabulary, human-like."
        ),

        "entropy": (
            [
                (4.0, "Very low entropy → highly predictable text, strong AI indicator."),
                (5.5, "Low entropy → text is statistically predictable, AI-like."),
                (6.5, "Moderate entropy → acceptable variation."),
                (7.5, "Good entropy → natural word distribution."),
            ],
            "High entropy → varied and less predictable writing, human-like."
        ),

        "sentence_cv": (
            [
                (0.30, "Very uniform sentence lengths (CV < 0.30) → strong AI indicator."),
                (0.35, "Uniform sentence lengths (CV < 0.35) → AI-like."),
                (0.45, "Somewhat uniform sentence lengths → weak AI signal."),
                (0.55, "Natural sentence-length variation."),
            ],
            "High variation in sentence lengths → human-like."
        ),

        "paragraph_cv": (
            [
                (0.20, "Very uniform paragraph sizes → strong AI indicator."),
                (0.35, "Uniform paragraph sizes → AI-like."),
                (0.50, "Somewhat uniform paragraph sizes → weak AI signal."),
            ],
            "Varied paragraph sizes → human-like."
        ),

        "pattern": (
            [
                (0.15, "Low syntax repetition → diverse sentence structures."),
                (0.30, "Moderate syntax repetition → some patterns present."),
                (0.50, "High syntax repetition → repeated sentence templates, AI-like."),
            ],
            "Very high syntax repetition → strong template usage detected, AI indicator."
        ),

        "word_length": (
            [
                (3.5, "Very short average word length → simplified vocabulary, AI indicator."),
                (4.2, "Short average word length → somewhat simplified vocabulary."),
                (4.8, "Normal average word length → appropriate vocabulary complexity."),
            ],
            "Long average word length → sophisticated vocabulary, human-like."
        ),

        "readability": (
            [
                # NOTE: Flesch Reading Ease is HIGHER for simpler text, so the
                # comparison direction is reversed here (handled below).
                (50, "Very high readability → text is overly simple, strong AI indicator."),
                (65, "High readability → text is unusually simple, AI-like."),
                (75, "Moderate readability → appropriate complexity."),
            ],
            "Normal readability → natural text complexity, human-like."
        ),
    }

    levels, high_msg = rules.get(name, ([], "No interpretation available."))

    # readability (Flesch) runs the other way: a HIGH score means SIMPLE text
    if name == "readability":
        if value >= 90:
            return "Very high readability → text is overly simple, strong AI indicator."
        if value >= 70:
            return "High readability → text is unusually simple, AI-like."
        if value >= 50:
            return "Moderate readability → appropriate complexity."
        return "Low readability (complex text) → natural complexity, human-like."

    for threshold, msg in levels:
        if value < threshold:
            return msg

    return high_msg

def overall_profile(ai_score, metrics):
    """Enhanced overall profile with more detailed signals."""

    signals = []
    warnings = []

    diversity = metrics['lexical_diversity']
    entropy_score = metrics['entropy']
    sent_cv = metrics['burstiness']
    readability = metrics['readability_score']
    pronoun_ratio = metrics['pronoun_analysis']['ratio']
    para_cv = metrics.get('paragraph_uniformity_cv')

    # Positive human signals
    if diversity > 0.65:
        signals.append("rich vocabulary diversity")
    if entropy_score > 7.5:
        signals.append("natural entropy distribution")
    if sent_cv > 0.55:
        signals.append("excellent sentence-length variability")
    if para_cv is not None and para_cv > 0.50:
        signals.append("varied paragraph sizes")
    if readability < 70:
        signals.append("natural text complexity")
    if pronoun_ratio < 0.12:
        signals.append("natural pronoun usage")

    # Warning signals
    if sent_cv < 0.30:
        warnings.append("unnaturally uniform sentences")
    if sent_cv < 0.45 and sent_cv >= 0.30:
        warnings.append("uniform sentence lengths")
    if para_cv is not None and para_cv < 0.35:
        warnings.append("uniform paragraph lengths")
    if diversity < 0.40:
        warnings.append("concerning vocabulary repetition")
    if entropy_score < 4.5:
        warnings.append("statistically predictable text")
    if readability > 75:
        warnings.append("overly simplified text")
    if pronoun_ratio > 0.18:
        warnings.append("excessive pronoun usage")

    # Determine verdict
    if ai_score > 70:
        verdict = "Strong AI-like statistical profile detected."
    elif ai_score > 55:
        verdict = "Probable AI-generated text with multiple indicators."
    elif ai_score > 35:
        verdict = "Mixed profile: contains both human-like and AI-like signals."
    else:
        verdict = "Text statistically appears more human-like."

    # Honest abstention: below the structural-signal horizon the "human-like"
    # verdict would be an artifact of missing data, not evidence.
    if metrics.get('word_count', 0) < 150 or metrics['sentence_count'] < 5:
        verdict += (" NOTE: text is too short for reliable structural analysis — "
                    "this verdict is unreliable, not evidence of human authorship.")

    # Genre abstention: promotional/social-media register. Both AI hype posts
    # and human SMM copy trigger this - it does NOT score toward AI, it only
    # withdraws the "human-like" claim for a genre outside the calibration.
    if metrics.get('promotional_register'):
        verdict += (" NOTE: promotional/social-media register (emoji- and "
                    "exclamation-heavy) is outside the calibration corpus — "
                    "this verdict is unreliable for this genre.")

    return verdict, signals, warnings

def suspicious_patterns(phrase_hits, repetitive_hits, top_trigrams):
    """Enhanced suspicious pattern detection."""
    warnings = []

    high_risk_phrases = set(AI_PHRASES['high'])

    for phrase in phrase_hits:
        if phrase in high_risk_phrases:
            warnings.append(f"⚠️ High-risk AI phrase: '{phrase}'")
        else:
            warnings.append(f"AI-like phrase: '{phrase}'")

    # Repetitive patterns
    for pattern in repetitive_hits:
        warnings.append(f"Repetitive AI pattern: '{pattern}'")

    # Suspicious trigrams
    suspicious_trigrams = {
        "it is important", "it is crucial", "it is essential",
        "in this context", "in this regard", "in this perspective",
        "on the other hand", "first and foremost", "last but not least",
    }

    for phrase, count in top_trigrams:
        if phrase in suspicious_trigrams and count > 1:
            warnings.append(f"⚠️ Repeated suspicious trigram: '{phrase}' ({count} times)")

    return warnings


# =========================================================
# MAIN ANALYSIS FUNCTION
# =========================================================

def analyze(text):
    """Enhanced main analysis function with new metrics."""

    sentences = split_sentences(text)
    words = tokenize(text)
    filtered = filtered_words(words)

    if not words:
        return {"error": "No words found in text"}

    # Original metrics
    diversity = lexical_diversity(filtered)
    rep_score = repetition_score(filtered)
    entropy_score = entropy(filtered)

    sent_lengths = [len(s.split()) for s in sentences if s.split()]
    burst = burstiness(sent_lengths) if sent_lengths else 0
    para_cv = paragraph_uniformity(text)
    punct_density = punctuation_density(text)

    phrase_hits, phrase_tiers, phrase_occurrences = ai_phrase_hits(text)
    conn_density = connective_density(sentences)
    tmpl_total, tmpl_distinct, tmpl_occurrences = template_header_repetition(text)
    repetitive_hits = repetitive_pattern_hits(text)
    uni_stats = unicode_stats(text)

    patterns = sentence_patterns(sentences)
    pattern_rep_score = pattern_repetition_score(sentences)

    top_bigrams = top_ngrams(filtered, 2, 10)
    top_trigrams = top_ngrams(filtered, 3, 10)

    # New advanced metrics
    avg_word_len = avg_word_length(words)
    word_var = word_length_variance(words)
    pronoun_analysis = analyze_pronouns(words)
    readability = readability_score(text, words, sentences)
    passive_density = passive_voice_density(text)
    adj_noun_div = adj_noun_pair_diversity(words)
    struct_unif = structural_uniformity(sentences)
    quant_over = quantifier_overuse(text)

    # Evidence: located indicators (v0.4.0)
    evidence = build_evidence(text, sentences, phrase_occurrences, burst,
                              para_cv, conn_density, tmpl_occurrences)
    promo_emoji, promo_excl, promo = promotional_register(text)
    if promo:
        evidence.append({
            'type': 'genre',
            'detail': (f"promotional/social-media register: {promo_emoji} emoji, "
                       f"{promo_excl:.3f} exclamations/word - statistical signals "
                       "are not calibrated for this genre; verdict withheld"),
            'line': None,
            'excerpt': None,
        })

    # Build metrics dictionary
    metrics = {
        'word_count': len(words),
        'promotional_register': promo,
        'lexical_diversity': diversity,
        'repetition_score': rep_score,
        'entropy': entropy_score,
        'burstiness': burst,
        'paragraph_uniformity_cv': para_cv,
        'paragraph_count': len(paragraph_lengths(text)) if para_cv is not None else 0,
        'punctuation_density': punct_density,
        'ai_phrase_hits': phrase_hits,
        'ai_phrase_tiers': phrase_tiers,
        'connective_density': conn_density,
        'template_header_repetition': {'total': tmpl_total, 'distinct': tmpl_distinct},
        'repetitive_hits': repetitive_hits,
        'unicode_stats': uni_stats,
        'sentence_patterns': patterns,
        'pattern_repetition_score': pattern_rep_score,
        'sentence_count': len(sentences),
        'top_bigrams': top_bigrams,
        'top_trigrams': top_trigrams,

        # New metrics
        'avg_word_length': avg_word_len,
        'word_length_variance': word_var,
        'pronoun_analysis': pronoun_analysis,
        'readability_score': readability,
        'passive_voice_density': passive_density,
        'adj_noun_pair_diversity': adj_noun_div,
        'structural_uniformity': struct_unif,
        'quantifier_overuse': quant_over,
    }

    # Calculate scores
    ai_score, detailed_scores = calculate_ai_score(metrics, len(words))

    # Generate interpretations
    verdict, signals, warnings = overall_profile(ai_score, metrics)
    pattern_warnings = suspicious_patterns(phrase_hits, repetitive_hits, top_trigrams)

    # Determine confidence based on text length
    word_count = len(words)
    if word_count < 300:
        confidence = "low"
    elif word_count < 1000:
        confidence = "medium"
    else:
        confidence = "high"

    # Build result
    result = {
        'text_analysis': {
            'word_count': word_count,
            'sentence_count': len(sentences),
            'confidence': confidence,
            'language': detect_language(text),
        },
        'metrics': {
            'lexical_diversity': round(diversity, 3),
            'repetition_score': round(rep_score, 3),
            'entropy': round(entropy_score, 3),
            'sentence_length_cv': round(burst, 3),
            'paragraph_length_cv': round(para_cv, 3) if para_cv is not None else None,
            'connective_density': round(conn_density, 3),
            'template_header_repeats': tmpl_total,
            'punctuation_density': round(punct_density, 3),
            'pattern_repetition_score': round(pattern_rep_score, 3),

            # New metrics
            'avg_word_length': round(avg_word_len, 2),
            'word_length_variance': round(word_var, 2),
            'pronoun_ratio': round(pronoun_analysis['ratio'], 3),
            'readability_score': round(readability, 1),
            'passive_voice_density': round(passive_density, 4),
            'adj_noun_pair_diversity': round(adj_noun_div, 3),
            'structural_uniformity': round(struct_unif, 3),
            'quantifier_overuse': round(quant_over, 4),
        },
        'detection_results': {
            'ai_phrase_hits': phrase_hits,
            'ai_phrase_tiers': phrase_tiers,
            'repetitive_hits': repetitive_hits,
            'unicode_symbols': uni_stats,
            'ai_probability_score': round(ai_score, 1),
            'detailed_scores': detailed_scores,
        },
        'interpretation': {
            'metric_interpretations': {
                'lexical_diversity': interpret_metric("diversity", diversity),
                'entropy': interpret_metric("entropy", entropy_score),
                'sentence_cv': interpret_metric("sentence_cv", burst),
                'paragraph_cv': (interpret_metric("paragraph_cv", para_cv)
                                 if para_cv is not None else "Not enough paragraphs."),
                'pattern': interpret_metric("pattern", pattern_rep_score),
                'word_length': interpret_metric("word_length", avg_word_len),
                'readability': interpret_metric("readability", readability),
            },
            'overall_verdict': verdict,
            'positive_signals': signals,
            'warning_signals': warnings,
            'suspicious_patterns': pattern_warnings,
        },
        'evidence': evidence,
        'ngram_analysis': {
            'top_bigrams': top_bigrams[:5],
            'top_trigrams': top_trigrams[:5],
        }
    }

    return result


# =========================================================
# FORMATTED OUTPUT
# =========================================================

def print_report(result):
    """Print comprehensive analysis report."""

    print("\n" + "="*60)
    print("AI TEXT FORENSIC ANALYSIS - EXTENDED VERSION")
    print("="*60)

    # Text analysis
    text_info = result['text_analysis']
    print(f"\nText Statistics:")
    print(f"  Words: {text_info['word_count']}")
    print(f"  Sentences: {text_info['sentence_count']}")
    print(f"  Detected language: {text_info.get('language', '?')}")
    print(f"  Confidence: {text_info['confidence'].upper()}")

    # Core metrics
    metrics = result['metrics']
    print(f"\nCore Metrics:")
    print(f"  sentence_length_cv (burstiness): {metrics['sentence_length_cv']}")
    print(f"  paragraph_length_cv: {metrics['paragraph_length_cv']}")
    print(f"  lexical_diversity: {metrics['lexical_diversity']}")
    print(f"  repetition_score: {metrics['repetition_score']}")
    print(f"  entropy: {metrics['entropy']}")
    print(f"  connective_density: {metrics['connective_density']}")
    print(f"  punctuation_density: {metrics['punctuation_density']}")
    print(f"  pattern_repetition_score: {metrics['pattern_repetition_score']}")

    # New advanced metrics
    print(f"\nAdvanced Linguistic Metrics:")
    print(f"  avg_word_length: {metrics['avg_word_length']}")
    print(f"  word_length_variance: {metrics['word_length_variance']}")
    print(f"  pronoun_ratio: {metrics['pronoun_ratio']}")
    print(f"  readability_score: {metrics['readability_score']}")
    print(f"  passive_voice_density: {metrics['passive_voice_density']}")
    print(f"  adj_noun_pair_diversity: {metrics['adj_noun_pair_diversity']}")
    print(f"  structural_uniformity: {metrics['structural_uniformity']}")
    print(f"  quantifier_overuse: {metrics['quantifier_overuse']}")

    # Detection results
    detection = result['detection_results']
    tiers = detection.get('ai_phrase_tiers', {})
    print(f"\nDetection Results:")
    print(f"  estimated_ai_probability: {detection['ai_probability_score']}%")
    if tiers:
        print(f"  AI phrases by tier: high={tiers['high']}, medium={tiers['medium']}, weak={tiers['weak']}")

    if detection['ai_phrase_hits']:
        print(f"  AI phrases found: {', '.join(detection['ai_phrase_hits'][:5])}")
        if len(detection['ai_phrase_hits']) > 5:
            print(f"    ... and {len(detection['ai_phrase_hits']) - 5} more")

    if detection['repetitive_hits']:
        print(f"  Repetitive patterns: {', '.join(detection['repetitive_hits'][:3])}")

    if detection['unicode_symbols']:
        print(f"  Unicode symbols: {list(detection['unicode_symbols'].keys())[:5]}")

    # Evidence: exact locations (v0.4.0)
    evidence = result.get('evidence', [])
    if evidence:
        print(f"\nAI EVIDENCE (locations in the text):")
        for i, ev in enumerate(evidence[:15], 1):
            loc = f"line {ev['line']}" if ev.get('line') else "text-wide"
            print(f"  [{i}] {loc}: {ev['detail']}")
            if ev.get('excerpt'):
                print(f"      \"{ev['excerpt']}\"")

    # Interpretation
    interpretation = result['interpretation']
    print(f"\nMetric Interpretations:")
    for metric, interp in interpretation['metric_interpretations'].items():
        print(f"  {metric}: {interp}")

    print(f"\nOverall Analysis:")
    print(f"  verdict: {interpretation['overall_verdict']}")

    if interpretation['positive_signals']:
        print(f"  positive_signals:")
        for signal in interpretation['positive_signals']:
            print(f"    - {signal}")

    if interpretation['warning_signals']:
        print(f"  warning_signals:")
        for warning in interpretation['warning_signals']:
            print(f"    - {warning}")

    if interpretation['suspicious_patterns']:
        print(f"  suspicious_patterns:")
        for pattern in interpretation['suspicious_patterns']:
            print(f"    - {pattern}")

    # N-grams
    ngrams = result['ngram_analysis']
    if ngrams['top_bigrams']:
        print(f"\nTop Bigrams:")
        for bigram, count in ngrams['top_bigrams']:
            print(f"  '{bigram}': {count}")

    if ngrams['top_trigrams']:
        print(f"\nTop Trigrams:")
        for trigram, count in ngrams['top_trigrams']:
            print(f"  '{trigram}': {count}")

    print("\n" + "="*60)
    print("Note: scores are heuristic, calibrated on an encyclopedic corpus")
    print("(see validation/AI_CORPUS_REPORT.md). Not proof of authorship.")
    print("="*60 + "\n")


# =========================================================
# CLI INTERFACE
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python3 parscgpt-ext.py <textfile>")
        print("\nExtended AI forensic analyzer with advanced linguistic metrics.")
        print("Provides enhanced detection accuracy through:")
        print("  • 18 metrics incl. sentence/paragraph uniformity (CV)")
        print("  • Multilingual AI phrase tiers (EN/RU/UK/PT)")
        print("  • AI EVIDENCE: line numbers + excerpts for each indicator")
        print("  • Weighted scoring system with confidence intervals")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        if not text.strip():
            print("Error: File is empty")
            sys.exit(1)

        result = analyze(text)
        print_report(result)

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
