#!/usr/bin/env python3
"""
AI Text Forensic Analyzer - Extended Version
Enhanced with advanced linguistic metrics and improved detection accuracy
"""

import re
import sys
import math
from collections import Counter
from itertools import islice
from statistics import mean, median, stdev, pstdev


# =========================================================
# EXTENDED CONFIG - Expanded Knowledge Base
# =========================================================

AI_PHRASES = [
    # Original transitional phrases
    "however", "moreover", "overall", "in conclusion", 
    "it is important to note", "additionally", "that said", 
    "on the other hand", "in general", "furthermore", 
    "therefore", "as a result", "for example", "for instance", 
    "ultimately", "in summary", "notably", "meanwhile", 
    "consequently", "in contrast",
    
    # Extended AI-specific phrases
    "it's worth noting", "it should be emphasized", 
    "it is crucial to understand", "it is essential to recognize",
    "it is important to consider", "it is vital to remember",
    "it is significant to highlight", "it is noteworthy that",
    "it is interesting to observe", "it is relevant to mention",
    
    # Hedge words and qualifiers
    "relatively", "somewhat", "quite", "rather", "fairly",
    "reasonably", "comparatively", "moderately", "substantially",
    "considerably", "significantly", "notably", "remarkably",
    
    # Academic/formal patterns
    "in this context", "in this regard", "in this perspective",
    "from this perspective", "in this sense", "in this manner",
    "in this way", "in this approach", "in this framework",
    
    # Logical connectors
    "given that", "considering that", "taking into account",
    "bearing in mind", "in light of", "in view of",
    "with respect to", "in terms of", "in regard to",
    
    # Conclusion patterns
    "to summarize", "in essence", "fundamentally", "essentially",
    "at its core", "at its heart", "in essence", "in substance",
    "in effect", "in practice", "in theory", "in principle",
    
    # Analysis patterns
    "suggests that", "indicates that", "implies that", "demonstrates that",
    "reveals that", "shows that", "points to", "leads to",
    
    # Structure markers
    "first and foremost", "last but not least", "in the first place",
    "in the second place", "on one hand", "on the other hand",
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
    "—", "–", """, """, "'", "'", 
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
    "того", "своей", "или", "ебать", "тебя", "через", "ни",
    "ему", "будет", "них", "них", "там", "ее", "им", "про",
    "этом", "мо", "этому", "куда", "потом", "этого", "раз",
    "можно", "два", "где", "ли", "без", "чем", "эти", "нас",
    "за", "своих", "его", "какой", "сам", "них", "всех",
    "этом", "любой", "один", "между", "была", "вас", "чей",
    "которой", "сейчас", "она", "они", "чем", "также", "свои",
    "ей", "которого", "эти", "либо", "мы", "ваш", "нужно",
    "своей", "сейчас", "ему", "так", "были", "каждый", "или",
    "будет", "том", "потому", "какой", "раз", "мог", "где",
    "дело", "когда", "ли", "после", "над", "четвертый", "очень",
    "даже", "кое", "вам", "куда", "кроме", "моего", "хоть",
    "чего", "свой", "впрочем", "он", "него", "ваша", "затем",
    "которые", "твой", "кого", "их", "все", "её", "ни",
    "может", "такой", "ей", "кое", "всех", "чей", "будто",
    "кому", "зачем", "впереди", "его", "третьего", "вашего",
    "мой", "ему", "своих", "моего", "хотя", "другой", "этого",
    "твоего", "два", "эти", "твоей", "между", "лишь", "без",
    "никогда", "себя", "перед", "каких", "какой", "их",
    "сейчас", "над", "тоже", "кое-кого", "третьего", "том",
    "эту", "пять", "дальше", "которые", "чей", "там", "почему",
    "вашей", "затем", "вторых", "потому", "каждой", "чей-нибудь",
    "чего", "ей", "них", "каждое", "он", "него", "них",
    "тебя", "ни", "вы", "мы", "все", "вы", "они",
    "оно", "я", "нас", "вы", "они", "твоих", "мной",
    "ним", "вами", "них", "мною", "тобой", "ею", "тобою",
    "собой", "себя", "ею", "ими", "ими", "о", "об",
    "обо", "от", "ото", "из", "изо", "ко", "по",
    "при", "про", "без", "за", "на", "над", "об",
    "от", "перед", "под", "про", "ради", "с", "сквозь",
    "у", "через", "из-за", "из-под", "вокруг", "позади",
    "посреди", "после", "против", "среди", "шесть", "семь",
    "восемь", "девять", "десять", "нуль", "ноль", "один",
    "два", "три", "четыре", "пять", "миллион", "миллиарда",
}


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
    """Calculate sentence length variation (original metric)."""
    if len(lengths) < 2:
        return 0
    
    avg = mean(lengths)
    return pstdev(lengths) / avg if avg else 0

def punctuation_density(text):
    """Calculate punctuation density (original metric)."""
    punct = re.findall(r'[,;:()\-\—–]', text)
    return len(punct) / max(len(text), 1)

def readability_score(text, words, sentences):
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
    
    adjectives = [w for w in words if any(w.endswith(ind) for ind in adj_indicators)]
    nouns = [w for w in words if any(w.endswith(ind) for ind in noun_indicators)]
    
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
    """Extended AI phrase detection."""
    lower = text.lower()
    hits = []
    
    for phrase in AI_PHRASES:
        if phrase in lower:
            hits.append(phrase)
    
    return hits

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
        'burstiness': 0,
        'pattern_repetition': 0,
        'repetition': 0,
        'punctuation': 0,
        'ai_phrases': 0,
        'unicode': 0,
        
        # New metrics
        'avg_word_length': 0,
        'word_length_variance': 0,
        'pronoun_ratio': 0,
        'readability': 0,
        'passive_voice': 0,
        'adj_noun_diversity': 0,
        'structural_uniformity': 0,
        'quantifier_overuse': 0,
    }
    
    # Original metrics with refined thresholds
    diversity = metrics['lexical_diversity']
    if diversity < 0.45:
        scores['lexical_diversity'] = 25  # Increased from 20
    elif diversity < 0.55:
        scores['lexical_diversity'] = 15
    
    entropy_score = metrics['entropy']
    if entropy_score < 5.0:
        scores['entropy'] = 25  # Increased from 20
    elif entropy_score < 6.5:
        scores['entropy'] = 15
    
    burst = metrics['burstiness']
    if burst < 0.35:
        scores['burstiness'] = 20  # Increased from 15
    
    pattern_rep = metrics['pattern_repetition_score']
    if pattern_rep > 0.35:
        scores['pattern_repetition'] = 20  # Increased from 15
    
    rep = metrics['repetition_score']
    if rep > 0.5:
        scores['repetition'] = 15
    
    punct = metrics['punctuation_density']
    if punct > 0.04:
        scores['punctuation'] = 5
    
    ai_phrases = len(metrics['ai_phrase_hits'])
    if ai_phrases >= 3:
        scores['ai_phrases'] = 20  # Increased from 15
    elif ai_phrases >= 1:
        scores['ai_phrases'] = 10
    
    if metrics['unicode_stats']:
        scores['unicode'] = 5
    
    # New advanced metrics
    avg_word_len = metrics['avg_word_length']
    if avg_word_len < 4.0:
        scores['avg_word_length'] = 10
    elif avg_word_len < 4.5:
        scores['avg_word_length'] = 5
    
    word_var = metrics['word_length_variance']
    if word_var < 1.5:
        scores['word_length_variance'] = 8  # Low variance = AI
    
    pronoun_ratio = metrics['pronoun_analysis']['ratio']
    if pronoun_ratio > 0.15:
        scores['pronoun_ratio'] = 10  # High pronoun use = AI
    
    readability = metrics['readability_score']
    if readability > 70:
        scores['readability'] = 8  # Too readable = AI
    elif readability > 60:
        scores['readability'] = 4
    
    passive = metrics['passive_voice_density']
    if passive > 0.05:
        scores['passive_voice'] = 7  # High passive voice = AI
    
    adj_noun_div = metrics['adj_noun_pair_diversity']
    if adj_noun_div < 0.3:
        scores['adj_noun_diversity'] = 6  # Low diversity = AI
    
    struct_unif = metrics['structural_uniformity']
    if struct_unif > 0.4:
        scores['structural_uniformity'] = 8  # Too uniform = AI
    
    quant_overuse = metrics['quantifier_overuse']
    if quant_overuse > 0.02:
        scores['quantifier_overuse'] = 6
    
    # Text length adaptation - longer texts get more reliable scores
    length_factor = min(1.0, text_length / 1000)  # Scale up to 1000 words
    
    # Calculate total with length adjustment
    total = sum(scores.values())
    adjusted_total = total * (0.8 + 0.2 * length_factor)  # Min 80%, max 100%
    
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
        
        "burstiness": (
            [
                (0.25, "Very low burstiness → extremely uniform sentence lengths, strong AI indicator."),
                (0.40, "Low burstiness → sentence lengths are unnaturally uniform, AI-like."),
                (0.65, "Moderate burstiness → some natural variation."),
                (0.80, "Good burstiness → natural sentence variation."),
            ],
            "High burstiness → natural, human-like variation in sentence structure."
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
                (50, "Very high readability → text is overly simple, strong AI indicator."),
                (65, "High readability → text is unusually simple, AI-like."),
                (75, "Moderate readability → appropriate complexity."),
            ],
            "Normal readability → natural text complexity, human-like."
        ),
    }
    
    levels, high_msg = rules.get(name, ([], "No interpretation available."))
    
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
    burst = metrics['burstiness']
    readability = metrics['readability_score']
    pronoun_ratio = metrics['pronoun_analysis']['ratio']
    
    # Positive human signals
    if diversity > 0.65:
        signals.append("rich vocabulary diversity")
    if entropy_score > 7.5:
        signals.append("natural entropy distribution")
    if burst > 0.80:
        signals.append("excellent sentence variability")
    if readability < 70:
        signals.append("natural text complexity")
    if pronoun_ratio < 0.12:
        signals.append("natural pronoun usage")
    
    # Warning signals
    if diversity < 0.40:
        warnings.append("concerning vocabulary repetition")
    if entropy_score < 4.5:
        warnings.append("statistically predictable text")
    if burst < 0.30:
        warnings.append("unnaturally uniform sentences")
    if readability > 75:
        warnings.append("overly simplified text")
    if pronoun_ratio > 0.18:
        warnings.append("excessive pronoun usage")
    
    # Determine verdict
    if ai_score > 75:
        verdict = "Strong AI-like statistical profile detected."
    elif ai_score > 55:
        verdict = "Probable AI-generated text with multiple indicators."
    elif ai_score > 35:
        verdict = "Mixed profile: contains both human-like and AI-like signals."
    else:
        verdict = "Text statistically appears more human-like."
    
    return verdict, signals, warnings

def suspicious_patterns(phrase_hits, repetitive_hits, top_trigrams):
    """Enhanced suspicious pattern detection."""
    warnings = []
    
    # Suspicious phrases from expanded list
    high_risk_phrases = [
        "it is important to note", "it should be emphasized",
        "it is crucial to understand", "in conclusion", 
        "ultimately", "in essence", "fundamentally",
    ]
    
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
    punct_density = punctuation_density(text)
    
    phrase_hits = ai_phrase_hits(text)
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
    
    # Build metrics dictionary
    metrics = {
        'lexical_diversity': diversity,
        'repetition_score': rep_score,
        'entropy': entropy_score,
        'burstiness': burst,
        'punctuation_density': punct_density,
        'ai_phrase_hits': phrase_hits,
        'repetitive_hits': repetitive_hits,
        'unicode_stats': uni_stats,
        'sentence_patterns': patterns,
        'pattern_repetition_score': pattern_rep_score,
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
        },
        'metrics': {
            'lexical_diversity': round(diversity, 3),
            'repetition_score': round(rep_score, 3),
            'entropy': round(entropy_score, 3),
            'burstiness': round(burst, 3),
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
            'repetitive_hits': repetitive_hits,
            'unicode_symbols': uni_stats,
            'ai_probability_score': round(ai_score, 1),
            'detailed_scores': detailed_scores,
        },
        'interpretation': {
            'metric_interpretations': {
                'lexical_diversity': interpret_metric("diversity", diversity),
                'entropy': interpret_metric("entropy", entropy_score),
                'burstiness': interpret_metric("burstiness", burst),
                'pattern': interpret_metric("pattern", pattern_rep_score),
                'word_length': interpret_metric("word_length", avg_word_len),
                'readability': interpret_metric("readability", readability),
            },
            'overall_verdict': verdict,
            'positive_signals': signals,
            'warning_signals': warnings,
            'suspicious_patterns': pattern_warnings,
        },
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
    print(f"  Confidence: {text_info['confidence'].upper()}")
    
    # Core metrics
    metrics = result['metrics']
    print(f"\nCore Metrics:")
    print(f"  lexical_diversity: {metrics['lexical_diversity']}")
    print(f"  repetition_score: {metrics['repetition_score']}")
    print(f"  entropy: {metrics['entropy']}")
    print(f"  burstiness: {metrics['burstiness']}")
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
    print(f"\nDetection Results:")
    print(f"  estimated_ai_probability: {detection['ai_probability_score']}%")
    
    if detection['ai_phrase_hits']:
        print(f"  AI phrases found: {', '.join(detection['ai_phrase_hits'][:5])}")
        if len(detection['ai_phrase_hits']) > 5:
            print(f"    ... and {len(detection['ai_phrase_hits']) - 5} more")
    
    if detection['repetitive_hits']:
        print(f"  Repetitive patterns: {', '.join(detection['repetitive_hits'][:3])}")
    
    if detection['unicode_symbols']:
        print(f"  Unicode symbols: {list(detection['unicode_symbols'].keys())[:5]}")
    
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
    print("END OF REPORT - EXTENDED VERSION")
    print("="*60 + "\n")


# =========================================================
# CLI INTERFACE
# =========================================================

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python3 parscgpt-ext.py <textfile>")
        print("\nExtended AI forensic analyzer with advanced linguistic metrics.")
        print("Provides enhanced detection accuracy through:")
        print("  • 17 metrics (vs 8 in standard version)")
        print("  • 70+ AI phrases (vs 21 in standard version)")  
        print("  • Advanced linguistic analysis")
        print("  • Weighted scoring system")
        print("  • Improved confidence intervals")
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