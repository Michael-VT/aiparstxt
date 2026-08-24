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
from statistics import mean, median, stdev, pstdev
import time

# =========================================================
# EXTENDED ALLOWED CHARACTERS
# =========================================================

ALLOWED = set()
ALLOWED.update("0123456789")
ALLOWED.update("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
ALLOWED.update("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяҐґЄєІіЇї")
ALLOWED.update("àâçéèêëîïôùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŸŒÆ")  # Français
ALLOWED.update("äöüßÄÖÜ")  # Deutsch  
ALLOWED.update("àáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ")  # Português
ALLOWED.update("[]{}():()-=_+!@#$%&*;'/.,<>"
               "'"
               '"`~|—«»')
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

# Suspicious Unicode characters commonly found in AI-generated text
UNICODE_SUSPICIOUS = [
    '\u2010', '\u2011',  # Hyphen variants
    '\u2012', '\u2013', '\u2014',  # Em-dash variants
    '\u2018', '\u2019', '\u201B',  # Smart quotes
    '\u201C', '\u201D', '\u201E', '\u201F',  # Smart double quotes
    '\u2026',  # Ellipsis
    '\u202F',  # Narrow no-break space
    '\u205F',  # Medium mathematical space
    '\u00A0',  # Non-breaking space
    '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', 
    '\u2006', '\u2007', '\u2008', '\u2009', '\u200A',  # Space variants
]

# AI-typical phrases (расширенный набор)
AI_PHRASES = [
    # Language model typical phrases
    "в заключение", "в целом", "важно отметить", "值得注意的是", "重要的是",
    "in conclusion", "in summary", "it is worth noting", "it is important to note",
    "т综上所述", "总的来说", "值得注意的是", "总之", "basically", "essentially",
    "в самом деле", "в действительности", "в самом", "на самом деле",
    
    # Overused connectors
    " furthermore", "moreover", "additionally", "in addition", "moreover",
    "более того", "кроме того", "следует отметить", "следует упомянуть",
    
    # Hedging language
    "it could be argued", "one might argue", "it appears that", "seems that",
    "можно утверждать", "можно сказать", "кажется", "по-видимому",
    
    # Generic transitions
    "on the other hand", "however", "nevertheless", "nonetheless",
    "с одной стороны", "с другой стороны", "однако", "тем не менее",
    
    # AI disclaimer patterns
    "as an ai", "as a language model", "i cannot", "i'm not able to",
    "как искусственный интеллект", "как языковая модель",
    
    # Over-structured patterns
    "first and foremost", "last but not least", "firstly", "secondly",
    "во-первых", "во-вторых", "в-третьих", "с одной стороны", "с другой стороны",
]

STOPWORDS = {
    # English
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
    "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him",
    "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than",
    "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most",
    # Russian
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "всё", "она", "так", "быть",
    "его", "к", "но", "они", "мы", "ее", "бы", "было", "всего", "себе", "еще", "нет", "может", "это", "тебя",
    "тем", "ими", "ее", "ему", "если", "уже", "или", "ему", "где", "зачем", "когда", "куда", "от", "почему",
    "чем", "чтобы", "чье", "чей", "кто", "чём", "кому"
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
    """Split text into sentences."""
    sentence_endings = re.compile(r'[.!?]+[\s\n]+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip() and len(s) > 3]


def calculate_ai_forensic_metrics(text, word_freq):
    """Calculate comprehensive AI forensic metrics."""
    if not text:
        return {}
    
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = split_sentences(text)
    
    if not words or not sentences:
        return {}
    
    # Core metrics
    word_count = len(words)
    sentence_count = len(sentences)
    unique_words = len(set(words))
    
    # Lexical diversity
    lexical_div = unique_words / word_count if word_count > 0 else 0
    
    # Repetition score
    repeated = sum(1 for count in word_freq.values() if count > 1)
    rep_score = repeated / len(word_freq) if word_freq else 0
    
    # Entropy calculation
    import math
    total = sum(word_freq.values())
    entropy = -sum((count/total) * math.log2(count/total) for count in word_freq.values()) if total > 0 else 0
    
    # Sentence length analysis (burstiness)
    sent_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    avg_sent_len = mean(sent_lengths)
    burstiness = stdev(sent_lengths) / avg_sent_len if avg_sent_len > 0 and len(sent_lengths) > 1 else 0
    
    # Pattern repetition
    def categorize_length(length):
        if length < 10: return 'S'
        elif length < 20: return 'M'
        else: return 'L'
    
    patterns = [categorize_length(length) for length in sent_lengths]
    pattern_counts = Counter(patterns)
    repeated_patterns = sum(1 for count in pattern_counts.values() if count > 1)
    pattern_rep = repeated_patterns / len(patterns) if patterns else 0
    
    # Punctuation density
    punct_chars = re.findall(r'[,.!?;:()\-\—–]', text)
    punct_density = len(punct_chars) / len(text) if text else 0
    
    # AI phrase detection
    text_lower = text.lower()
    ai_hits = sum(1 for phrase in AI_PHRASES if phrase in text_lower)
    
    # Unicode suspicious characters
    unicode_count = sum(1 for char in UNICODE_SUSPICIOUS if char in text)
    
    # Word length statistics
    word_lengths = [len(word) for word in words]
    avg_word_len = mean(word_lengths) if word_lengths else 0
    word_len_var = stdev(word_lengths) if len(word_lengths) > 1 else 0
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'lexical_diversity': lexical_div,
        'repetition_score': rep_score,
        'entropy': entropy,
        'burstiness': burstiness,
        'pattern_repetition': pattern_rep,
        'punctuation_density': punct_density,
        'ai_phrase_hits': ai_hits,
        'unicode_symbols': unicode_count,
        'avg_word_length': avg_word_len,
        'word_length_variance': word_len_var,
    }


def calculate_ai_probability(metrics):
    """Calculate AI probability based on forensic metrics."""
    if not metrics:
        return 0, {}
    
    scores = {}
    total = 0
    
    # Core metrics with enhanced weighting
    if metrics['lexical_diversity'] < 0.45:
        scores['lexical_diversity'] = 25
        total += 25
    elif metrics['lexical_diversity'] < 0.55:
        scores['lexical_diversity'] = 15
        total += 15
        
    if metrics['entropy'] < 5.0:
        scores['entropy'] = 25
        total += 25
    elif metrics['entropy'] < 5.8:
        scores['entropy'] = 15
        total += 15
        
    if metrics['burstiness'] < 0.35:
        scores['burstiness'] = 20
        total += 20
    elif metrics['burstiness'] < 0.45:
        scores['burstiness'] = 10
        total += 10
        
    if metrics['pattern_repetition'] > 0.35:
        scores['pattern_repetition'] = 20
        total += 20
    elif metrics['pattern_repetition'] > 0.25:
        scores['pattern_repetition'] = 10
        total += 10
        
    if metrics['ai_phrase_hits'] >= 3:
        scores['ai_phrases'] = 20
        total += 20
    elif metrics['ai_phrase_hits'] >= 1:
        scores['ai_phrases'] = 10
        total += 10
        
    if metrics['repetition_score'] > 0.5:
        scores['repetition'] = 15
        total += 15
        
    if metrics['punctuation_density'] > 0.04:
        scores['punctuation'] = 5
        total += 5
        
    if metrics['unicode_symbols'] > 0:
        scores['unicode'] = 5
        total += 5
        
    # Extended metrics
    if metrics['avg_word_length'] < 4.0:
        scores['word_length'] = 10
        total += 10
    elif metrics['avg_word_length'] < 4.5:
        scores['word_length'] = 5
        total += 5
        
    if metrics['word_length_variance'] < 1.5:
        scores['word_variance'] = 8
        total += 8
        
    # Length-based confidence adjustment
    word_count = metrics['word_count']
    if word_count < 300:
        confidence_factor = 0.8
        confidence = "LOW"
    elif word_count < 1000:
        confidence_factor = 0.9
        confidence = "MEDIUM"
    else:
        confidence_factor = 1.0
        confidence = "HIGH"
    
    adjusted_total = total * confidence_factor
    probability = min(100, adjusted_total)
    
    return probability, scores, confidence


def get_interpretation(metrics, ai_probability, confidence):
    """Generate human-readable interpretation of results."""
    interpretations = []
    
    if ai_probability > 60:
        verdict = f"High probability of AI-generated content ({ai_probability:.1f}%)"
    elif ai_probability > 30:
        verdict = f"Moderate probability of AI involvement ({ai_probability:.1f}%)"
    elif ai_probability > 10:
        verdict = f"Low probability of AI-generated content ({ai_probability:.1f}%)"
    else:
        verdict = f"Text appears predominantly human-written ({ai_probability:.1f}%)"
    
    if metrics['lexical_diversity'] < 0.45:
        interpretations.append("⚠️ Low lexical diversity - limited vocabulary variation")
    elif metrics['lexical_diversity'] > 0.65:
        interpretations.append("✓ High lexical diversity - rich vocabulary variation")
        
    if metrics['entropy'] < 5.0:
        interpretations.append("⚠️ Low entropy - unnaturally uniform word distribution")
    elif metrics['entropy'] > 6.0:
        interpretations.append("✓ Good entropy - natural word distribution")
        
    if metrics['burstiness'] < 0.35:
        interpretations.append("⚠️ Low burstiness - overly uniform sentence structure")
    elif metrics['burstiness'] > 0.7:
        interpretations.append("✓ Good burstiness - natural sentence variation")
        
    if metrics['ai_phrase_hits'] > 0:
        interpretations.append(f"⚠️ Found {metrics['ai_phrase_hits']} AI-typical phrases")
        
    if metrics['pattern_repetition'] > 0.35:
        interpretations.append("⚠️ High pattern repetition - template-like structure")
        
    if metrics['unicode_symbols'] > 0:
        interpretations.append(f"⚠️ Found {metrics['unicode_symbols']} suspicious Unicode characters")
        
    return verdict, interpretations


# =========================================================
# REPORTING FUNCTIONS
# =========================================================

def build_report(input_file, output_file, replaced, watermark_removed, word_freq, elapsed, 
                 ai_metrics=None, ai_probability=None, ai_confidence=None, 
                 lang="Python-Ext", replacement="?", remove=False, remove_watermark=False):
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
            lines.append(f"  Lexical diversity:     {ai_metrics['lexical_diversity']:.3f}")
            lines.append(f"  Repetition score:      {ai_metrics['repetition_score']:.3f}")
            lines.append(f"  Entropy:               {ai_metrics['entropy']:.3f}")
            lines.append(f"  Burstiness:            {ai_metrics['burstiness']:.3f}")
            lines.append(f"  Pattern repetition:    {ai_metrics['pattern_repetition']:.3f}")
            lines.append(f"  Punctuation density:   {ai_metrics['punctuation_density']:.3f}")
            lines.append(f"  AI phrase hits:        {ai_metrics['ai_phrase_hits']}")
            lines.append(f"  Unicode suspicious:    {ai_metrics['unicode_symbols']}")
            lines.append(f"  Avg word length:       {ai_metrics['avg_word_length']:.2f}")
            lines.append(f"  Word length variance:  {ai_metrics['word_length_variance']:.2f}")
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
    
    if processed_text:
        word_freq = word_frequency(processed_text) if not args.no_words else None
        ai_metrics = calculate_ai_forensic_metrics(processed_text, word_freq or Counter())
        if ai_metrics:
            ai_probability, ai_confidence = calculate_ai_probability(ai_metrics)
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
            "Python-Ext", args.replacement, args.remove, args.remove_watermark
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
    print(f"Output: {output_file if not args.no_edit else '(skipped)'}")
    print(f"Report: {report_file if not args.no_report else '(skipped)'}")


if __name__ == "__main__":
    main()
