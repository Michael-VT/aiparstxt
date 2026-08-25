#!/usr/bin/env python3
"""aiparstxt-ext — Enhanced Text Sanitizer with AI Forensic Analysis

Enhanced version with:
- Extended AI watermark character detection
- Statistical AI pattern analysis  
- Probability-based AI detection scoring
- Advanced forensic reporting
"""

import argparse
import sys
from collections import Counter
from pathlib import Path
import re
from statistics import mean, stdev, pstdev
import time

# =========================================================
# EXTENDED ALLOWED CHARACTERS
# =========================================================

ALLOWED = set(
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяҐґЄєІіЇї"
    "àáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ"
    "[]{}():()-=_+!@#$%&*;'/.,<>\"'`~—«» \t\n\r"
)
# =========================================================
# ENHANCED AI WATERMARK CHARACTERS
# =========================================================

WATERMARK_CHARS = set([
    # Core zero-width characters
    '\u200B',  # Zero Width Space (ZWSP) - самый частый маркер
    '\u200C',  # Zero Width Non-Joiner (ZWNJ)
    '\u200D',  # Zero Width Joiner (ZWJ)
    '\uFEFF',  # Zero Width No-Break Space (ZWNBSP, BOM)
    
    # Invisible formatting characters
    '\u00AD',  # Soft Hyphen (SHY)
    '\u2060',  # Word Joiner
    '\u2061',  # Function Application
    '\u2062',  # Invisible Times
    '\u2063',  # Invisible Separator
    '\u2064',  # Invisible Plus
    
    # Bidirectional control characters (используются для скрытного форматирования)
    '\u202A',  # Left-to-Right Embedding
    '\u202B',  # Right-to-Left Embedding
    '\u202C',  # Pop Directional Formatting
    '\u202D',  # Left-to-Right Override
    '\u202E',  # Right-to-Left Override
    
    # Separators
    '\u2028',  # Line Separator
    '\u2029',  # Paragraph Separator
    
    # Variation Selectors (могут использоваться для watermarking)
    '\uFE00', '\uFE01', '\uFE02', '\uFE03', '\uFE04', '\uFE05', '\uFE06', '\uFE07',
    '\uFE08', '\uFE09', '\uFE0A', '\uFE0B', '\uFE0C', '\uFE0D', '\uFE0E', '\uFE0F',
    
    # Language and script tags
    '\uE0001',  # Language Tag
    '\u180E',   # Mongolian Separator (often abused as watermark)
    
    # Additional Unicode planes suspicious for AI watermarking
    '\uFFF9', '\uFFFA', '\uFFFB', '\uFFFC', '\uFFFD',  # Interlinear annotation anchors
    
    # Musical symbols and other unusual Unicode (используются для стеганографии)
    '\u1D000',  # Musical Symbol start range
    '\u1D1FF',  # Musical Symbol end range
])

# Tag characters (E0020-E007F) - расширенный диапазон
for cp in range(0xE0020, 0xE0080):
    WATERMARK_CHARS.add(chr(cp))

# Private Use Area - commonly abused for watermarking (расширенный диапазон)
for cp in range(0xE000, 0xE080):
    WATERMARK_CHARS.add(chr(cp))

# Additional Private Use Areas (Plane 15 and 16)
for cp in range(0xF0000, 0xF00FF):  # Supplementary Private Use Area-A
    try:
        WATERMARK_CHARS.add(chr(cp))
    except ValueError:
        pass  # Some Unicode points may not be valid in Python

for cp in range(0x100000, 0x1000FF):  # Supplementary Private Use Area-B
    try:
        WATERMARK_CHARS.add(chr(cp))
    except ValueError:
        pass

# =========================================================
# AI FORENSIC PATTERNS
# =========================================================

# Suspicious Unicode characters - aligned with the parscgpt-ext.py reference
UNICODE_SUSPICIOUS = [
    "\u2014", "\u2013", "\u201C", "\u201D", "\u2018", "\u2019",
    "\u2026", "\u2022", "\u2192", "\u2190", "\u2191", "\u2193",
    "\u00A9", "\u00AE", "\u2122", "\u00B0", "\u00B1", "\u00D7", "\u00F7",
]

# AI-typical phrases: tiered multilingual database (v0.4.0).
# Canonical source: parscgpt-ext.py / AI_SIGNALS_SPEC.md.
# HIGH   - distinctive LLM template phrases, zero hits in human validation corpus
# MEDIUM - typical AI connective/register markers, rare in human corpus
# WEAK   - markers that also occur in human prose; evidence-only, tiny weight
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

# Scoring weights (v0.4.0) - canonical values, see AI_SIGNALS_SPEC.md
SENT_CV_TIERS = [(0.30, 32), (0.35, 26), (0.40, 19), (0.45, 11), (0.50, 5)]
PARA_CV_TIERS = [(0.15, 28), (0.25, 22), (0.35, 16), (0.45, 7)]
JOINT_CV_TIERS = [(0.40, 14), (0.45, 10)]
HIGH_PHRASE_SCORES = (24, 15)   # (>=2 hits, ==1 hit)
MEDIUM_PHRASE_SCORES = (10, 5)  # (>=3 hits, >=1 hit)
WEAK_PHRASE_SCORE = 4           # >=4 hits
CONNECTIVE_TIERS = [(0.12, 13), (0.08, 7)]
# Template header repetition: verbatim-repeated short non-punctuated lines
# ("Что верно" x7 etc.) - structured LLM answers reuse section templates.
# Zero hits in the human validation corpus.
TEMPLATE_HEADER_MIN_REPEATS = 3
TEMPLATE_HEADER_SCORES = (14, 8)  # (>=2 distinct templates or >=10 repeats, >=3 repeats)
# Guards: CV signals are unreliable on tiny texts. Instead of a hard cutoff
# (which silently made short AI texts score as "human"), tier points are
# scaled by statistical reliability: min(1, n/SENT_CV_FULL_SENTENCES) etc.
SENT_CV_MIN_SENTENCES = 5    # below this, sentence CV is pure noise -> 0
SENT_CV_FULL_SENTENCES = 15  # full weight from this many sentences on
PARA_CV_MIN_PARAGRAPHS = 3   # below this, paragraph CV is not computed
PARA_CV_FULL_PARAGRAPHS = 4
MIN_WORDS_FOR_CV = 40
FULL_WORDS_FOR_CV = 150

# Passive voice patterns (reference basis for passive_voice_density)
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
# TEXT PROCESSING FUNCTIONS
# =========================================================

def process(text, replacement="?", remove=False, remove_watermark=False):
    """Process text with enhanced AI watermark detection."""
    replaced = Counter()
    watermark_removed = Counter()
    out = []
    
    for ch in text:
        if remove_watermark and ch in WATERMARK_CHARS:
            watermark_removed[ch] += 1
            continue  # Remove watermark characters
            
        if ch in ALLOWED:
            out.append(ch)
        else:
            if remove:
                continue  # Skip character
            out.append(replacement)
            replaced[ch] += 1
    
    return "".join(out), replaced, watermark_removed


# =========================================================
# FORENSIC ANALYSIS FUNCTIONS
# =========================================================

def word_frequency(text):
    """Calculate word frequency with filtering."""
    words = []
    current_word = []
    
    for ch in text.lower():
        if ch.isalpha() or ch == "'":
            current_word.append(ch)
        else:
            if current_word:
                word = "".join(current_word)
                if len(word) > 2 and word not in STOPWORDS:
                    words.append(word)
                current_word = []
    
    # Handle last word
    if current_word:
        word = "".join(current_word)
        if len(word) > 2 and word not in STOPWORDS:
            words.append(word)
    
    return Counter(words)


def split_sentences(text):
    """Split text into sentences (aligned with parscgpt-ext.py reference)."""
    text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\.', r'\1<DOT>', text)
    sentences = [s.strip().replace('<DOT>', '.') for s in re.split(r'[.!?]+', text)]
    return [s for s in sentences if s.strip() and len(s) > 3]


def calculate_ai_forensic_metrics(text, word_freq=None):
    """Calculate comprehensive AI forensic metrics.

    Basis aligned with the parscgpt-ext.py reference (AI_SIGNALS_SPEC.md):
    diversity/entropy/repetition are computed on filtered words (stopwords
    and words <= 2 chars removed); unicode symbols are counted in the
    original (pre-sanitization) text."""
    if not text:
        return {}

    import math

    words = re.findall(r'\b\w+\b', text.lower())
    sentences = split_sentences(text)

    if not words or not sentences:
        return {}

    # Filtered words (reference basis for diversity/entropy/repetition)
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    filtered_counter = Counter(filtered)

    # Core metrics
    word_count = len(words)
    sentence_count = len(sentences)

    # Lexical diversity (on filtered words, as in reference)
    lexical_div = len(filtered_counter) / len(filtered) if filtered else 0

    # Repetition score (distinct repeated filtered words / filtered words)
    repeated = sum(1 for count in filtered_counter.values() if count > 1)
    rep_score = repeated / len(filtered) if filtered else 0

    # Entropy calculation (on filtered words, as in reference)
    total = len(filtered)
    entropy = -sum((count/total) * math.log2(count/total) for count in filtered_counter.values()) if total > 0 else 0
    
    # Sentence length analysis (burstiness = CV of sentence word counts);
    # word count per sentence uses whitespace split, as in the reference
    sent_lengths = [len(s.split()) for s in sentences]
    avg_sent_len = mean(sent_lengths) if sent_lengths else 0
    burstiness = pstdev(sent_lengths) / avg_sent_len if avg_sent_len > 0 and len(sent_lengths) > 1 else 0

    # Paragraph length uniformity (CV of paragraph word counts)
    paragraphs = [p for p in re.split(r'\n\s*\n', text) if len(p.split()) > 15]
    para_lengths = [len(p.split()) for p in paragraphs]
    if len(para_lengths) >= PARA_CV_MIN_PARAGRAPHS:
        para_avg = mean(para_lengths)
        para_cv = pstdev(para_lengths) / para_avg if para_avg > 0 else 0
        para_count = len(para_lengths)
    else:
        para_cv = None
        para_count = 0
    
    # Pattern repetition
    def categorize_length(length):
        if length <= 10: return 'S'
        elif length <= 20: return 'M'
        else: return 'L'
    
    patterns = [categorize_length(length) for length in sent_lengths]
    pattern_counts = Counter(patterns)
    repeated_patterns = sum(1 for count in pattern_counts.values() if count > 1)
    pattern_rep = repeated_patterns / len(patterns) if patterns else 0
    
    # Punctuation density (reference regex)
    punct_chars = re.findall(r'[,;:()\-\—–]', text)
    punct_density = len(punct_chars) / len(text) if text else 0
    
    # AI phrase detection (tiered, with occurrences for evidence)
    text_lower = text.lower()
    ai_hits = 0
    phrase_tiers = {'high': 0, 'medium': 0, 'weak': 0}
    phrase_occurrences = []
    for tier in ('high', 'medium', 'weak'):
        for phrase in AI_PHRASES[tier]:
            found = text_lower.count(phrase)
            if found:
                ai_hits += 1
                phrase_tiers[tier] += found
                idx = text_lower.find(phrase)
                for _ in range(min(found, 3)):
                    phrase_occurrences.append((tier, phrase, idx))
                    idx = text_lower.find(phrase, idx + len(phrase))

    # Connective density (connectives per sentence)
    conn_total = 0
    for s in sentences:
        s_lower = s.lower()
        conn_total += sum(1 for c in CONNECTIVES if c in s_lower)
    connective_density = conn_total / len(sentences) if sentences else 0

    # Promotional/social-media register (genre abstention, NOT an AI score:
    # both AI hype posts and human SMM copy trigger this)
    promo_emoji = sum(1 for c in text if ord(c) >= 0x2600)
    promo_excl = text.count('!') / word_count if word_count else 0
    promo = promo_emoji >= 5 and promo_excl >= 0.02

    # Template header repetition (structured-answer genre)
    line_counter = Counter()
    first_line_no = {}
    for i, raw in enumerate(text.split('\n'), 1):
        line = raw.strip()
        if (4 <= len(line) <= 60 and 1 <= len(line.split()) <= 8
                and line[-1] not in '.!?:;,…"»„'
                and not line[0].isdigit()):
            line_counter[line] += 1
            first_line_no.setdefault(line, i)
    tmpl_occurrences = []
    tmpl_total = 0
    tmpl_distinct = 0
    for line, count in line_counter.items():
        if count >= TEMPLATE_HEADER_MIN_REPEATS:
            tmpl_total += count
            tmpl_distinct += 1
            tmpl_occurrences.append((line, count, first_line_no[line]))
    tmpl_occurrences.sort(key=lambda o: -o[1])
    
    # Unicode suspicious characters
    # Unicode suspicious chars - count in the ORIGINAL (pre-sanitization)
    # text, matching the reference analyzer
    unicode_count = sum(1 for char in UNICODE_SUSPICIOUS if char in text)
    
    # Word length statistics
    word_lengths = [len(word) for word in words]
    avg_word_len = mean(word_lengths) if word_lengths else 0
    word_len_var = stdev(word_lengths) if len(word_lengths) > 1 else 0

    # --- Supporting metrics (mirror parscgpt-ext.py reference) ---
    # Pronoun ratio
    pronoun_lists = [
        ['i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves'],
        ['you', 'your', 'yours', 'yourself', 'yourselves'],
        ['he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
         'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'],
        ['this', 'that', 'these', 'those'],
        ['anyone', 'anything', 'everyone', 'everything', 'someone', 'something',
         'noone', 'nothing', 'each', 'every', 'either', 'neither', 'both', 'few',
         'many', 'several'],
    ]
    all_pronouns = set(p for lst in pronoun_lists for p in lst)
    pronoun_ratio = sum(1 for w in words if w in all_pronouns) / word_count if word_count else 0

    # Readability (Flesch, simplified syllables)
    syllable_count = sum(max(1, sum(1 for ch in w if ch in 'aeiouy')) for w in words)
    avg_sentence_length = word_count / len(sentences) if sentences else 0
    avg_syllables_per_word = syllable_count / word_count if word_count else 0
    flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    readability = max(0, min(100, flesch))

    # Passive voice density
    passive_count = sum(text_lower.count(p) for p in AI_PASSIVE_PATTERNS)
    passive_density = passive_count / max(len(text.split()), 1)

    # Adjective-noun pair diversity
    adj_indicators = ['al', 'ble', 'cal', 'ful', 'ic', 'ive', 'less', 'ous']
    noun_indicators = ['er', 'ism', 'ment', 'ness', 'tion', 'ship', 'cy', 'dom']
    adjectives = set(w for w in words if any(w.endswith(ind) for ind in adj_indicators))
    nouns = set(w for w in words if any(w.endswith(ind) for ind in noun_indicators))
    pairs = set()
    for i in range(len(words) - 1):
        if words[i] in adjectives and words[i + 1] in nouns:
            pairs.add(f"{words[i]} {words[i + 1]}")
    total_possible = len(adjectives) * len(nouns) if adjectives and nouns else 1
    adj_noun_div = len(pairs) / total_possible

    # Structural uniformity (repeated 2-word sentence starts)
    starts = [' '.join(s.split()[:2]).lower() for s in sentences if s.split()]
    repeated_starts = sum(1 for count in Counter(starts).values() if count > 1)
    struct_unif = repeated_starts / len(sentences) if sentences else 0

    # Quantifier overuse
    quantifiers = ['relatively', 'somewhat', 'quite', 'rather', 'fairly',
                   'reasonably', 'comparatively', 'moderately', 'substantially',
                   'considerably', 'significantly', 'notably', 'remarkably']
    quant_count = sum(text_lower.count(q) for q in quantifiers)
    quant_overuse = quant_count / max(len(text.split()), 1)
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'lexical_diversity': lexical_div,
        'repetition_score': rep_score,
        'entropy': entropy,
        'burstiness': burstiness,
        'paragraph_uniformity_cv': para_cv,
        'paragraph_count': para_count,
        'pattern_repetition': pattern_rep,
        'punctuation_density': punct_density,
        'ai_phrase_hits': ai_hits,
        'ai_phrase_tiers': phrase_tiers,
        'ai_phrase_occurrences': phrase_occurrences,
        'connective_density': connective_density,
        'template_header_repetition': {'total': tmpl_total, 'distinct': tmpl_distinct},
        'promotional_register': promo,
        'template_header_occurrences': tmpl_occurrences,
        'sentences': sentences,
        'unicode_symbols': unicode_count,
        'avg_word_length': avg_word_len,
        'word_length_variance': word_len_var,
        'pronoun_ratio': pronoun_ratio,
        'readability_score': readability,
        'passive_voice_density': passive_density,
        'adj_noun_pair_diversity': adj_noun_div,
        'structural_uniformity': struct_unif,
        'quantifier_overuse': quant_overuse,
    }


def calculate_ai_probability(metrics):
    """Calculate AI probability based on forensic metrics.

    v0.4.0 scoring - canonical weights, see AI_SIGNALS_SPEC.md."""
    if not metrics:
        return 0, {}, None

    scores = {}
    total = 0

    def add(name, points):
        nonlocal total
        if points > 0:
            scores[name] = points
            total += points

    # --- Primary structural signals ---
    # Tier points are scaled by statistical reliability of the sample
    # (short texts get partial credit instead of a silent zero).
    sent_cv = metrics['burstiness']
    sent_scale = (min(1.0, metrics['sentence_count'] / SENT_CV_FULL_SENTENCES)
                  * min(1.0, metrics['word_count'] / FULL_WORDS_FOR_CV))
    sent_cv_points = 0
    if metrics['sentence_count'] >= SENT_CV_MIN_SENTENCES and metrics['word_count'] >= MIN_WORDS_FOR_CV:
        for threshold, points in SENT_CV_TIERS:
            if sent_cv < threshold:
                sent_cv_points = int(round(points * sent_scale))
                break
    add('sentence_cv', sent_cv_points)

    para_cv = metrics.get('paragraph_uniformity_cv')
    para_points = 0
    para_scale = 0.0
    if para_cv is not None:
        para_scale = min(1.0, metrics.get('paragraph_count', PARA_CV_FULL_PARAGRAPHS)
                         / PARA_CV_FULL_PARAGRAPHS)
        for threshold, points in PARA_CV_TIERS:
            if para_cv < threshold:
                para_points = int(round(points * para_scale))
                break
    add('paragraph_cv', para_points)

    if para_cv is not None and sent_cv_points > 0:
        for threshold, points in JOINT_CV_TIERS:
            if sent_cv < threshold and para_cv < threshold:
                add('joint_uniformity', int(round(points * min(sent_scale, para_scale))))
                break

    # --- Tiered phrase scores ---
    tiers = metrics['ai_phrase_tiers']
    if tiers['high'] >= 2:
        add('ai_phrases', HIGH_PHRASE_SCORES[0])
    elif tiers['high'] == 1:
        add('ai_phrases', HIGH_PHRASE_SCORES[1])
    elif tiers['medium'] >= 3:
        add('ai_phrases', MEDIUM_PHRASE_SCORES[0])
    elif tiers['medium'] >= 1:
        add('ai_phrases', MEDIUM_PHRASE_SCORES[1])
    elif tiers['weak'] >= 4:
        add('ai_phrases', WEAK_PHRASE_SCORE)

    # --- Connective density ---
    for threshold, points in CONNECTIVE_TIERS:
        if metrics['connective_density'] >= threshold:
            add('connectives', points)
            break

    # --- Template header repetition (structured-answer genre) ---
    tmpl = metrics.get('template_header_repetition', {'total': 0, 'distinct': 0})
    if tmpl['distinct'] >= 2 or tmpl['total'] >= 10:
        add('template_headers', TEMPLATE_HEADER_SCORES[0])
    elif tmpl['total'] >= TEMPLATE_HEADER_MIN_REPEATS:
        add('template_headers', TEMPLATE_HEADER_SCORES[1])

    # --- Supporting statistical metrics ---
    if metrics['lexical_diversity'] < 0.45:
        add('lexical_diversity', 15)
    elif metrics['lexical_diversity'] < 0.55:
        add('lexical_diversity', 8)

    if metrics['entropy'] < 5.0:
        add('entropy', 15)
    elif metrics['entropy'] < 6.5:
        add('entropy', 8)

    if metrics['pattern_repetition'] > 0.35:
        add('pattern_repetition', 10)

    if metrics['repetition_score'] > 0.5:
        add('repetition', 8)

    if metrics['punctuation_density'] > 0.04:
        add('punctuation', 4)

    if metrics['unicode_symbols'] > 0:
        add('unicode', 4)

    if metrics['avg_word_length'] < 4.0:
        add('avg_word_length', 5)
    elif metrics['avg_word_length'] < 4.5:
        add('avg_word_length', 3)

    if metrics['word_length_variance'] < 1.5:
        add('word_length_variance', 4)

    if metrics['pronoun_ratio'] > 0.15:
        add('pronoun_ratio', 4)

    if metrics['readability_score'] > 70:
        add('readability', 5)
    elif metrics['readability_score'] > 60:
        add('readability', 3)

    if metrics['passive_voice_density'] > 0.05:
        add('passive_voice', 4)

    if metrics['adj_noun_pair_diversity'] < 0.3:
        add('adj_noun_diversity', 3)

    if metrics['structural_uniformity'] > 0.4:
        add('structural_uniformity', 4)

    if metrics['quantifier_overuse'] > 0.02:
        add('quantifier_overuse', 3)

    # Length-based confidence adjustment
    word_count = metrics['word_count']
    if word_count < 300:
        confidence = "LOW"
    elif word_count < 1000:
        confidence = "MEDIUM"
    else:
        confidence = "HIGH"

    length_factor = min(1.0, word_count / 1000)
    adjusted_total = total * (0.9 + 0.1 * length_factor)
    probability = min(100, adjusted_total)

    return probability, scores, confidence


def get_interpretation(metrics, ai_probability, confidence):
    """Generate human-readable interpretation of results."""
    interpretations = []

    if ai_probability > 70:
        verdict = f"Strong AI-like statistical profile ({ai_probability:.1f}%)"
    elif ai_probability > 55:
        verdict = f"Probable AI-generated text with multiple indicators ({ai_probability:.1f}%)"
    elif ai_probability > 35:
        verdict = f"Mixed profile: human-like and AI-like signals ({ai_probability:.1f}%)"
    else:
        verdict = f"Text statistically appears more human-like ({ai_probability:.1f}%)"

    # Honest abstention: below the structural-signal horizon the "human-like"
    # verdict would be an artifact of missing data, not evidence.
    if metrics.get('word_count', 0) < 150 or metrics.get('sentence_count', 0) < 5:
        verdict += (" NOTE: text is too short for reliable structural analysis — "
                    "this verdict is unreliable, not evidence of human authorship.")

    # Genre abstention: promotional/social register - verdict withdrawn, no AI points
    if metrics.get('promotional_register'):
        verdict += (" NOTE: promotional/social-media register (emoji- and "
                    "exclamation-heavy) is outside the calibration corpus — "
                    "this verdict is unreliable for this genre.")

    if metrics['burstiness'] < 0.35:
        interpretations.append("⚠️ Uniform sentence lengths (low burstiness) - strong AI signal")
    elif metrics['burstiness'] < 0.45:
        interpretations.append("⚠️ Somewhat uniform sentence lengths - AI-like")

    para_cv = metrics.get('paragraph_uniformity_cv')
    if para_cv is not None and para_cv < 0.35:
        interpretations.append("⚠️ Uniform paragraph lengths - AI-like")

    if metrics['lexical_diversity'] < 0.45:
        interpretations.append("⚠️ Low lexical diversity - limited vocabulary variation")
    elif metrics['lexical_diversity'] > 0.65:
        interpretations.append("✓ High lexical diversity - rich vocabulary variation")

    if metrics['entropy'] < 5.0:
        interpretations.append("⚠️ Low entropy - unnaturally uniform word distribution")
    elif metrics['entropy'] > 6.0:
        interpretations.append("✓ Good entropy - natural word distribution")

    tiers = metrics.get('ai_phrase_tiers')
    if tiers and (tiers['high'] or tiers['medium']):
        interpretations.append(
            f"⚠️ AI phrases: high={tiers['high']}, medium={tiers['medium']}")

    if metrics['connective_density'] >= 0.12:
        interpretations.append("⚠️ High discourse-connective density")

    if metrics['pattern_repetition'] > 0.35:
        interpretations.append("⚠️ High pattern repetition - template-like structure")

    if metrics['unicode_symbols'] > 0:
        interpretations.append(f"⚠️ Found {metrics['unicode_symbols']} suspicious Unicode characters")

    return verdict, interpretations


def truncate_middle(s, width=110):
    """Truncate a long string in the middle, keeping both ends."""
    if len(s) <= width:
        return s
    half = width // 2 - 5
    return s[:half] + ' ... ' + s[-half:]


def build_evidence(text, metrics):
    """Collect located AI indicators: line numbers + highlighted excerpts.

    v0.4.0 - see AI_SIGNALS_SPEC.md section 6."""
    evidence = []
    sentences = metrics.get('sentences') or []
    occurrences = metrics.get('ai_phrase_occurrences') or []

    def excerpt_for(idx, phrase):
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
    for tier, phrase, idx in sorted(occurrences, key=lambda o: ('high', 'medium', 'weak').index(o[0])):
        if shown >= 10:
            break
        label = {'high': 'HIGH-risk', 'medium': 'typical', 'weak': 'weak'}[tier]
        evidence.append({
            'type': 'phrase',
            'detail': f"{label} AI phrase '{phrase}'",
            'line': text.count('\n', 0, idx) + 1,
            'excerpt': excerpt_for(idx, phrase),
        })
        shown += 1

    # 1b. Repeated template headers (structured-answer genre)
    for line, count, line_no in (metrics.get('template_header_occurrences') or [])[:4]:
        evidence.append({
            'type': 'template',
            'detail': f"repeated template header '{line}' ×{count}",
            'line': line_no,
            'excerpt': None,
        })

    # 2. Sentence-length uniformity
    sent_cv = metrics['burstiness']
    if sent_cv < 0.50 and metrics['word_count'] >= MIN_WORDS_FOR_CV:
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
    para_cv = metrics.get('paragraph_uniformity_cv')
    if para_cv is not None and para_cv < 0.45:
        para_lengths = [len(p.split()) for p in re.split(r'\n\s*\n', text) if len(p.split()) > 15]
        evidence.append({
            'type': 'uniformity',
            'detail': (f"paragraph lengths are uniform: CV={para_cv:.2f} across "
                       f"{len(para_lengths)} paragraphs (human prose is typically > 0.50); "
                       "lengths: " + ' '.join(str(l) for l in para_lengths[:20])),
            'line': None,
            'excerpt': None,
        })

    # 4. Connective overuse with example sentences
    if metrics['connective_density'] >= 0.10:
        ranked = []
        for sent in sentences:
            lower_sent = sent.lower()
            n = sum(1 for c in CONNECTIVES if c in lower_sent)
            if n >= 2:
                ranked.append((n, sent))
        ranked.sort(key=lambda x: -x[0])
        for n, sent in ranked[:2]:
            evidence.append({
                'type': 'connective',
                'detail': f"sentence carries {n} discourse connectives",
                'line': None,
                'excerpt': truncate_middle(sent.strip(), 130),
            })

    # 5. Most suspicious sentences
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
    text_lower = text.lower()
    for markers, sent in sentence_scores[:3]:
        if markers >= 2:
            idx = text_lower.find(sent[:40].lower())
            evidence.append({
                'type': 'sentence',
                'detail': f"sentence with {markers} AI markers",
                'line': text.count('\n', 0, idx) + 1 if idx != -1 else None,
                'excerpt': truncate_middle(sent.strip(), 130),
            })

    return evidence


# =========================================================
# REPORTING FUNCTIONS
# =========================================================

def build_report(input_file, output_file, replaced, watermark_removed, word_freq, elapsed,
                 ai_metrics=None, ai_probability=None, ai_confidence=None,
                 lang="Python-Ext", replacement="?", remove=False, remove_watermark=False,
                 ai_evidence=None):
    """Build enhanced report with AI forensic analysis."""
    lines = []
    
    # Header
    lines.append("=" * 70)
    lines.append("aiparstxt-ext — Enhanced AI Forensic Analyzer Report")
    lines.append(f"Language: {lang}")
    lines.append("=" * 70)
    lines.append("")
    
    # Basic info
    lines.append(f"Input file:  {input_file}")
    lines.append(f"Output file: {output_file}")
    lines.append(f"Execution time: {elapsed:.6f}s")
    lines.append("")
    
    # Watermark analysis
    lines.append("--- AI Watermark Analysis ---")
    total_watermark = sum(watermark_removed.values()) if watermark_removed else 0
    lines.append(f"Watermark characters removed: {total_watermark}")
    if watermark_removed and total_watermark > 0:
        lines.append("Removed watermark character types:")
        for char, count in sorted(watermark_removed.items(), key=lambda x: -x[1]):
            char_repr = repr(char)[1:-1]  # Remove quotes
            codepoint = f"U+{ord(char):04X}"
            lines.append(f"  {codepoint} ({char_repr}): {count}")
    else:
        lines.append("No AI watermark characters detected")
    lines.append("")
    
    # Replaced characters
    lines.append("--- Replaced Characters ---")
    total_replaced = sum(replaced.values()) if replaced else 0
    lines.append(f"Characters replaced: {total_replaced}")
    if replaced and total_replaced > 0:
        lines.append("Replaced character types:")
        for char, count in sorted(replaced.items(), key=lambda x: -x[1])[:10]:
            char_repr = repr(char)[1:-1]
            codepoint = f"U+{ord(char):04X}"
            lines.append(f"  {codepoint} ({char_repr}): {count}")
        if len(replaced) > 10:
            lines.append(f"  ... and {len(replaced) - 10} more types")
    else:
        lines.append("No characters replaced")
    lines.append("")
    
    # AI Forensic Analysis
    if ai_metrics and ai_probability is not None:
        lines.append("=" * 70)
        lines.append("AI FORENSIC ANALYSIS")
        lines.append("=" * 70)
        lines.append("")
        
        verdict, interpretations = get_interpretation(ai_metrics, ai_probability, ai_confidence)
        
        lines.append(f"Overall Verdict: {verdict}")
        lines.append(f"Confidence Level: {ai_confidence}")
        lines.append("")
        
        if ai_metrics:
            lines.append("Detailed Metrics:")
            lines.append(f"  Word count:            {ai_metrics['word_count']}")
            lines.append(f"  Sentence count:        {ai_metrics['sentence_count']}")
            lines.append(f"  Sentence length CV:    {ai_metrics['burstiness']:.3f}")
            para_cv = ai_metrics.get('paragraph_uniformity_cv')
            lines.append(f"  Paragraph length CV:   {para_cv:.3f}" if para_cv is not None
                         else "  Paragraph length CV:   n/a (<4 paragraphs)")
            lines.append(f"  Lexical diversity:     {ai_metrics['lexical_diversity']:.3f}")
            lines.append(f"  Repetition score:      {ai_metrics['repetition_score']:.3f}")
            lines.append(f"  Entropy:               {ai_metrics['entropy']:.3f}")
            lines.append(f"  Connective density:    {ai_metrics['connective_density']:.3f}")
            tmpl = ai_metrics.get('template_header_repetition', {})
            lines.append(f"  Template headers:      {tmpl.get('total', 0)} repeats "
                         f"({tmpl.get('distinct', 0)} distinct)")
            lines.append(f"  Pattern repetition:    {ai_metrics['pattern_repetition']:.3f}")
            lines.append(f"  Punctuation density:   {ai_metrics['punctuation_density']:.3f}")
            tiers = ai_metrics.get('ai_phrase_tiers', {})
            if tiers:
                lines.append(f"  AI phrases (tiers):    high={tiers['high']}, "
                             f"medium={tiers['medium']}, weak={tiers['weak']}")
            lines.append(f"  AI phrase hits:        {ai_metrics['ai_phrase_hits']}")
            lines.append(f"  Unicode suspicious:    {ai_metrics['unicode_symbols']}")
            lines.append(f"  Avg word length:       {ai_metrics['avg_word_length']:.2f}")
            lines.append(f"  Word length variance:  {ai_metrics['word_length_variance']:.2f}")
            lines.append("")

        if ai_evidence:
            lines.append("AI EVIDENCE (locations in the text):")
            for i, ev in enumerate(ai_evidence[:15], 1):
                loc = f"line {ev['line']}" if ev.get('line') else "text-wide"
                lines.append(f"  [{i}] {loc}: {ev['detail']}")
                if ev.get('excerpt'):
                    lines.append(f"      \"{ev['excerpt']}\"")
            lines.append("")
        
        if interpretations:
            lines.append("Signal Analysis:")
            for interp in interpretations:
                lines.append(f"  {interp}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("")
    
    # Word frequency
    lines.append("--- Top Word Frequencies (Filtered) ---")
    if word_freq:
        for word, count in word_freq.most_common(20):
            lines.append(f"  {word}: {count}")
    else:
        lines.append("(skipped)")
    
    return "\n".join(lines) + "\n"


# =========================================================
# MAIN FUNCTION
# =========================================================

def main():
    parser = argparse.ArgumentParser(
        description="aiparstxt-ext — Enhanced text sanitizer with AI forensic analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.txt                    # Basic analysis
  %(prog)s input.txt --remove-watermark # Remove AI watermarks
  %(prog)s input.txt -o output.txt      # Custom output file
        """
    )
    
    parser.add_argument("input_file", help="Input text file to analyze")
    parser.add_argument("-o", "--output", help="Output file (default: <input>.ed.txt)")
    parser.add_argument("-r", "--report", help="Report file (default: report_<lang>-ext.txt)")
    parser.add_argument("--no-edit", action="store_true", help="Do not create .ed.txt file")
    parser.add_argument("--no-report", action="store_true", help="Do not create report file")
    parser.add_argument("--no-words", action="store_true", help="Exclude word frequency from report")
    parser.add_argument("--remove-watermark", action="store_true", help="Remove AI watermark characters")
    parser.add_argument("--replacement", default="?", help="Replacement character (default: '?')")
    parser.add_argument("--remove", action="store_true", help="Remove disallowed characters instead of replacing")
    
    args = parser.parse_args()
    
    # Set default paths
    input_path = Path(args.input_file)
    default_output = input_path.parent / f"{input_path.stem}.ed.txt"
    default_report = Path("report_py-ext.txt")
    
    output_file = args.output or str(default_output)
    report_file = args.report or str(default_report)
    
    # Read input file
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process text
    start = time.time()
    processed_text, replaced, watermark_removed = process(
        text, 
        replacement=args.replacement, 
        remove=args.remove, 
        remove_watermark=args.remove_watermark
    )
    
    # Calculate forensic metrics
    ai_metrics = None
    ai_probability = None
    ai_confidence = None
    ai_evidence = None

    if processed_text:
        word_freq = word_frequency(processed_text) if not args.no_words else None
        # AI forensic analysis runs on the ORIGINAL text: sanitization
        # replaces disallowed characters with '?', which would corrupt
        # sentence splitting and phrase positions.
        ai_metrics = calculate_ai_forensic_metrics(text, word_freq or Counter())
        if ai_metrics:
            ai_probability, scores, ai_confidence = calculate_ai_probability(ai_metrics)
            ai_evidence = build_evidence(text, ai_metrics)
    else:
        word_freq = None
    
    elapsed = time.time() - start
    
    # Write output file
    if not args.no_edit:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(processed_text)
        except Exception as e:
            print(f"Error writing {output_file}: {e}", file=sys.stderr)
    
    # Generate and write report
    if not args.no_report:
        report_content = build_report(
            args.input_file, output_file, replaced, watermark_removed,
            word_freq, elapsed, ai_metrics, ai_probability, ai_confidence,
            "Python-Ext", args.replacement, args.remove, args.remove_watermark,
            ai_evidence
        )
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)
        except Exception as e:
            print(f"Error writing {report_file}: {e}", file=sys.stderr)
    
    # Print summary
    print(f"Processed in {elapsed:.6f}s")
    print(f"Replacements: {sum(replaced.values()) if replaced else 0}")
    print(f"Watermarks removed: {sum(watermark_removed.values()) if watermark_removed else 0}")
    if ai_probability is not None:
        print(f"AI Probability: {ai_probability:.1f}% (confidence: {ai_confidence})")
        if ai_evidence:
            print(f"AI Evidence (top {min(3, len(ai_evidence))} of {len(ai_evidence)}):")
            for ev in ai_evidence[:3]:
                loc = f"line {ev['line']}" if ev.get('line') else "text-wide"
                print(f"  {loc}: {ev['detail']}")
    print(f"Output: {output_file if not args.no_edit else '(skipped)'}")
    print(f"Report: {report_file if not args.no_report else '(skipped)'}")


if __name__ == "__main__":
    main()
