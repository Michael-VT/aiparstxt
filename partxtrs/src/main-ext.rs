use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;
use std::time::Instant;

// =========================================================
// ENHANCED ALLOWED CHARACTERS
// =========================================================

const ALLOWED_CHARS: &str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\
АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя\
[]{}()-=_+!@#$%&*;'/.,<>\"`~ \\t\\n\\r";

const CANONICAL_ALLOWED: &str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ[]{}():()-=_+!@#$%&*;'/.,<>\"`~—«» \t\n\r";

fn is_allowed(ch: char) -> bool {
    CANONICAL_ALLOWED.contains(ch)
}

// =========================================================
// ENHANCED AI WATERMARK CHARACTERS
// =========================================================

fn is_watermark(ch: char) -> bool {
    let cp = ch as u32;
    
    // Core zero-width characters
    if matches!(cp,
        0x200B | // Zero Width Space (ZWSP)
        0x200C | // Zero Width Non-Joiner (ZWNJ)
        0x200D | // Zero Width Joiner (ZWJ)
        0xFEFF | // Zero Width No-Break Space (ZWNBSP, BOM)
        0x00AD | // Soft Hyphen (SHY)
        0x2060 | // Word Joiner
        0x2061 | // Function Application
        0x2062 | // Invisible Times
        0x2063 | // Invisible Separator
        0x2064 | // Invisible Plus
        0x202A | // Left-to-Right Embedding
        0x202B | // Right-to-Left Embedding
        0x202C | // Pop Directional Formatting
        0x202D | // Left-to-Right Override
        0x202E | // Right-to-Left Override
        0x2028 | // Line Separator
        0x2029 | // Paragraph Separator
        0xE0001 | // Language Tag
        0x180E | // Mongolian Separator
        (0xFE00..=0xFE0F) | // Variation Selectors
        (0xE0020..=0xE007F) // Tag characters
    ) {
        return true;
    }
    
    // Private Use Area - commonly abused for watermarking
    if cp >= 0xE000 && cp <= 0xE07F {
        return true;
    }
    
    // Additional suspicious characters
    if matches!(cp,
        0xFFF9 | 0xFFFA | 0xFFFB | 0xFFFC | 0xFFFD | // Interlinear annotation
        0x2010 | 0x2011 | // Hyphen variants
        0x2012 | 0x2013 | 0x2014 | // Em-dash variants
        0x2018 | 0x2019 | 0x201B | // Smart quotes
        0x201C | 0x201D | 0x201E | 0x201F | // Smart double quotes
        0x2026 | // Ellipsis
        0x202F | // Narrow no-break space
        0x205F | // Medium mathematical space
        0x00A0 | // Non-breaking space
        0x2000 | 0x2001 | 0x2002 | 0x2003 | 0x2004 | 0x2005 |
        0x2006 | 0x2007 | 0x2008 | 0x2009 | 0x200A // Space variants
    ) {
        return true;
    }
    
    false
}

// =========================================================
// TEXT PROCESSING STRUCTS
// =========================================================

#[derive(Debug)]
struct ProcessResult {
    cleaned: String,
    replaced: HashMap<char, usize>,
    watermark_removed: HashMap<char, usize>,
}

fn process(text: &str, remove_watermark: bool) -> ProcessResult {
    let mut replaced = HashMap::new();
    let mut watermark_removed = HashMap::new();
    let mut out = String::with_capacity(text.len());
    
    for ch in text.chars() {
        if remove_watermark && is_watermark(ch) {
            *watermark_removed.entry(ch).or_insert(0) += 1;
            continue;
        }
        
        if is_allowed(ch) {
            out.push(ch);
        } else {
            out.push('?');
            *replaced.entry(ch).or_insert(0) += 1;
        }
    }
    
    ProcessResult {
        cleaned: out,
        replaced,
        watermark_removed,
    }
}

// =========================================================
// FORENSIC ANALYSIS STRUCTS
// =========================================================

#[derive(Debug)]
struct AIMetrics {
    word_count: usize,
    sentence_count: usize,
    lexical_diversity: f64,
    repetition_score: f64,
    entropy: f64,
    burstiness: f64,
    pattern_repetition: f64,
    punctuation_density: f64,
    ai_phrase_hits: usize,
    unicode_symbols: usize,
    avg_word_length: f64,
    word_length_variance: f64,
}

#[derive(Debug)]
struct AIResult {
    probability: f64,
    confidence: String,
    scores: HashMap<String, usize>,
}

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

fn word_frequency(text: &str) -> HashMap<String, usize> {
    let mut freq = HashMap::new();
    let mut current_word = String::new();
    
    // Russian and English stopwords
    let stopwords: HashSet<&'static str> = [
        // English
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
        "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
        "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him",
        "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than",
        // Russian
        "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "всё", "она", "так", "быть",
        "его", "к", "но", "они", "мы", "ее", "бы", "было", "всего", "себе", "еще", "нет", "может", "это", "тебя",
        "тем", "ими", "ее", "ему", "если", "уже", "или", "ему", "где", "зачем", "когда", "куда", "от", "почему",
        "чем", "чтобы", "чье", "чей", "кто", "чём", "кому"
    ].iter().cloned().collect();
    
    for ch in text.chars() {
        if ch.is_alphabetic() || ch == '\'' {
            current_word.push(ch.to_ascii_lowercase());
        } else {
            if !current_word.is_empty() {
                if current_word.len() > 2 && !stopwords.contains(current_word.as_str()) {
                    *freq.entry(current_word.clone()).or_insert(0) += 1;
                }
                current_word.clear();
            }
        }
    }
    
    // Handle last word
    if !current_word.is_empty() && current_word.len() > 2 && !stopwords.contains(current_word.as_str()) {
        *freq.entry(current_word).or_insert(0) += 1;
    }
    
    freq
}

fn split_sentences(text: &str) -> Vec<String> {
    let mut sentences = Vec::new();
    let mut current = String::new();
    let mut sentence_end = false;
    
    for ch in text.chars() {
        if matches!(ch, '.' | '!' | '?') {
            sentence_end = true;
            current.push(ch);
        } else if sentence_end && ch.is_whitespace() {
            sentence_end = false;
            if !current.trim().is_empty() && current.len() > 3 {
                sentences.push(current.trim().to_string());
            }
            current.clear();
        } else {
            current.push(ch);
        }
    }
    
    // Handle last sentence
    if !current.trim().is_empty() && current.len() > 3 {
        sentences.push(current.trim().to_string());
    }
    
    sentences
}

fn calculate_ai_forensic_metrics(text: &str, word_freq: &HashMap<String, usize>) -> Option<AIMetrics> {
    if text.is_empty() {
        return None;
    }
    
    let words: Vec<&str> = text.split_whitespace()
        .map(|w| w.trim_matches(|c: char| !c.is_alphabetic()))
        .filter(|w| !w.is_empty())
        .collect();
    
    let sentences = split_sentences(text);
    
    if words.is_empty() || sentences.is_empty() {
        return None;
    }
    
    // Core metrics
    let word_count = words.len();
    let sentence_count = sentences.len();
    let unique_words = words.iter().map(|w| w.to_lowercase()).collect::<HashSet<_>>().len();
    
    // Lexical diversity
    let lexical_div = unique_words as f64 / word_count as f64;
    
    // Repetition score
    let repeated = word_freq.values().filter(|&&count| count > 1).count();
    let rep_score = repeated as f64 / word_freq.len().max(1) as f64;
    
    // Entropy calculation
    let total: usize = word_freq.values().sum();
    let mut entropy = 0.0;
    for &count in word_freq.values() {
        if total > 0 {
            let p = count as f64 / total as f64;
            entropy -= p * p.log2();
        }
    }
    
    // Sentence length analysis (burstiness)
    let sent_lengths: Vec<usize> = sentences.iter()
        .map(|s| s.split_whitespace().count())
        .collect();
    
    let avg_sent_len = sent_lengths.iter().sum::<usize>() as f64 / sent_lengths.len() as f64;
    let variance = sent_lengths.iter()
        .map(|&len| (len as f64 - avg_sent_len).powi(2))
        .sum::<f64>() / sent_lengths.len() as f64;
    let burstiness = if avg_sent_len > 0.0 {
        variance.sqrt() / avg_sent_len
    } else {
        0.0
    };
    
    // Pattern repetition
    fn categorize_length(length: usize) -> char {
        if length < 10 { 'S' } 
        else if length < 20 { 'M' } 
        else { 'L' }
    }
    
    let patterns: Vec<char> = sent_lengths.iter().map(|&len| categorize_length(len)).collect();
    let mut pattern_counts: HashMap<char, usize> = HashMap::new();
    for &pattern in &patterns {
        *pattern_counts.entry(pattern).or_insert(0) += 1;
    }
    let repeated_patterns = pattern_counts.values().filter(|&&count| count > 1).count();
    let pattern_rep = repeated_patterns as f64 / patterns.len().max(1) as f64;
    
    // Punctuation density
    let punct_count = text.chars()
        .filter(|&c| matches!(c, ',' | '.' | '!' | '?' | ';' | ':' | '(' | ')' | '-' | '—' | '–'))
        .count();
    let punct_density = punct_count as f64 / text.chars().count().max(1) as f64;
    
    // AI phrase detection (simplified)
    let ai_phrases = [
        "in conclusion", "in summary", "it is worth noting", "it is important to note",
        "basically", "essentially", "furthermore", "moreover", "additionally", "in addition",
        "it could be argued", "one might argue", "it appears that", "seems that",
        "on the other hand", "however", "nevertheless", "nonetheless",
        "as an ai", "as a language model", "i cannot", "i'm not able to",
        "в заключение", "в целом", "важно отметить", "более того", "кроме того",
        "можно утверждать", "можно сказать", "с одной стороны", "с другой стороны",
        "как искусственный интеллект", "как языковая модель", "во-первых", "во-вторых",
    ];
    
    let text_lower = text.to_lowercase();
    let ai_hits = ai_phrases.iter()
        .filter(|&&phrase| text_lower.contains(phrase))
        .count();
    
    // Unicode suspicious characters
    let unicode_count = text.chars()
        .filter(|&c| {
            let cp = c as u32;
            matches!(cp,
                0x2010 | 0x2011 | 0x2012 | 0x2013 | 0x2014 |
                0x2018 | 0x2019 | 0x201B |
                0x201C | 0x201D | 0x201E | 0x201F |
                0x2026 | 0x202F | 0x205F | 0x00A0 |
                0x2000 | 0x2001 | 0x2002 | 0x2003 | 0x2004 | 0x2005 |
                0x2006 | 0x2007 | 0x2008 | 0x2009 | 0x200A
            )
        })
        .count();
    
    // Word length statistics
    let word_lengths: Vec<usize> = words.iter().map(|w| w.len()).collect();
    let avg_word_len = word_lengths.iter().sum::<usize>() as f64 / word_lengths.len().max(1) as f64;
    let word_len_variance = if word_lengths.len() > 1 {
        let mean = avg_word_len;
        let variance = word_lengths.iter()
            .map(|&len| (len as f64 - mean).powi(2))
            .sum::<f64>() / word_lengths.len() as f64;
        variance.sqrt()
    } else {
        0.0
    };
    
    Some(AIMetrics {
        word_count,
        sentence_count,
        lexical_diversity: lexical_div,
        repetition_score: rep_score,
        entropy,
        burstiness,
        pattern_repetition: pattern_rep,
        punctuation_density: punct_density,
        ai_phrase_hits: ai_hits,
        unicode_symbols: unicode_count,
        avg_word_length: avg_word_len,
        word_length_variance: word_len_variance,
    })
}

fn calculate_ai_probability(metrics: &AIMetrics) -> AIResult {
    let mut scores = HashMap::new();
    let mut total = 0;
    
    // Core metrics with enhanced weighting
    if metrics.lexical_diversity < 0.45 {
        scores.insert("lexical_diversity".to_string(), 25);
        total += 25;
    } else if metrics.lexical_diversity < 0.55 {
        scores.insert("lexical_diversity".to_string(), 15);
        total += 15;
    }
    
    if metrics.entropy < 5.0 {
        scores.insert("entropy".to_string(), 25);
        total += 25;
    } else if metrics.entropy < 5.8 {
        scores.insert("entropy".to_string(), 15);
        total += 15;
    }
    
    if metrics.burstiness < 0.35 {
        scores.insert("burstiness".to_string(), 20);
        total += 20;
    } else if metrics.burstiness < 0.45 {
        scores.insert("burstiness".to_string(), 10);
        total += 10;
    }
    
    if metrics.pattern_repetition > 0.35 {
        scores.insert("pattern_repetition".to_string(), 20);
        total += 20;
    } else if metrics.pattern_repetition > 0.25 {
        scores.insert("pattern_repetition".to_string(), 10);
        total += 10;
    }
    
    if metrics.ai_phrase_hits >= 3 {
        scores.insert("ai_phrases".to_string(), 20);
        total += 20;
    } else if metrics.ai_phrase_hits >= 1 {
        scores.insert("ai_phrases".to_string(), 10);
        total += 10;
    }
    
    if metrics.repetition_score > 0.5 {
        scores.insert("repetition".to_string(), 15);
        total += 15;
    }
    
    if metrics.punctuation_density > 0.04 {
        scores.insert("punctuation".to_string(), 5);
        total += 5;
    }
    
    if metrics.unicode_symbols > 0 {
        scores.insert("unicode".to_string(), 5);
        total += 5;
    }
    
    // Extended metrics
    if metrics.avg_word_length < 4.0 {
        scores.insert("word_length".to_string(), 10);
        total += 10;
    } else if metrics.avg_word_length < 4.5 {
        scores.insert("word_length".to_string(), 5);
        total += 5;
    }
    
    if metrics.word_length_variance < 1.5 {
        scores.insert("word_variance".to_string(), 8);
        total += 8;
    }
    
    // Length-based confidence adjustment
    let (confidence_factor, confidence) = if metrics.word_count < 300 {
        (0.8, "LOW".to_string())
    } else if metrics.word_count < 1000 {
        (0.9, "MEDIUM".to_string())
    } else {
        (1.0, "HIGH".to_string())
    };
    
    let adjusted_total = total as f64 * confidence_factor;
    let probability = (adjusted_total as f64).min(100.0);
    
    AIResult {
        probability,
        confidence,
        scores,
    }
}

fn get_interpretation(metrics: &AIMetrics, ai_probability: f64) -> (String, Vec<String>) {
    let mut interpretations = Vec::new();
    
    let verdict = if ai_probability > 60.0 {
        format!("High probability of AI-generated content ({:.1}%)", ai_probability)
    } else if ai_probability > 30.0 {
        format!("Moderate probability of AI involvement ({:.1}%)", ai_probability)
    } else if ai_probability > 10.0 {
        format!("Low probability of AI-generated content ({:.1}%)", ai_probability)
    } else {
        format!("Text appears predominantly human-written ({:.1}%)", ai_probability)
    };
    
    if metrics.lexical_diversity < 0.45 {
        interpretations.push("⚠️ Low lexical diversity - limited vocabulary variation".to_string());
    } else if metrics.lexical_diversity > 0.65 {
        interpretations.push("✓ High lexical diversity - rich vocabulary variation".to_string());
    }
    
    if metrics.entropy < 5.0 {
        interpretations.push("⚠️ Low entropy - unnaturally uniform word distribution".to_string());
    } else if metrics.entropy > 6.0 {
        interpretations.push("✓ Good entropy - natural word distribution".to_string());
    }
    
    if metrics.burstiness < 0.35 {
        interpretations.push("⚠️ Low burstiness - overly uniform sentence structure".to_string());
    } else if metrics.burstiness > 0.7 {
        interpretations.push("✓ Good burstiness - natural sentence variation".to_string());
    }
    
    if metrics.ai_phrase_hits > 0 {
        interpretations.push(format!("⚠️ Found {} AI-typical phrases", metrics.ai_phrase_hits));
    }
    
    if metrics.pattern_repetition > 0.35 {
        interpretations.push("⚠️ High pattern repetition - template-like structure".to_string());
    }
    
    if metrics.unicode_symbols > 0 {
        interpretations.push(format!("⚠️ Found {} suspicious Unicode characters", metrics.unicode_symbols));
    }
    
    (verdict, interpretations)
}

// =========================================================
// REPORTING FUNCTIONS
// =========================================================

fn build_report(
    input_file: &str,
    output_file: &str,
    replaced: &HashMap<char, usize>,
    watermark_removed: &HashMap<char, usize>,
    word_freq: &HashMap<String, usize>,
    elapsed: std::time::Duration,
    ai_metrics: &Option<AIMetrics>,
    ai_result: &Option<AIResult>,
    remove_watermark: bool,
    lang: &str,
) -> String {
    let mut lines = Vec::new();
    
    // Header
    lines.push("=".repeat(70));
    lines.push(format!("aiparstxt-ext — Enhanced AI Forensic Analyzer Report"));
    lines.push(format!("Language: {}", lang));
    lines.push("=".repeat(70));
    lines.push(String::new());
    
    // Basic info
    lines.push(format!("Input file:  {}", input_file));
    lines.push(format!("Output file: {}", output_file));
    lines.push(format!("Mode: replace with '?'{}", if remove_watermark { " + watermark removal" } else { "" }));
    lines.push(format!("Execution time: {:.6}s", elapsed.as_secs_f64()));
    lines.push(String::new());
    
    // Watermark analysis
    lines.push("--- AI Watermark Analysis ---".to_string());
    let total_watermark: usize = watermark_removed.values().sum();
    lines.push(format!("Watermark characters removed: {}", total_watermark));
    
    if total_watermark > 0 {
        lines.push("Removed watermark character types:".to_string());
        let mut sorted: Vec<_> = watermark_removed.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));
        for (ch, count) in sorted.iter().take(20) {
            let codepoint = format!("U+{:04X}", **ch as u32);
            lines.push(format!("  {}: {}", codepoint, count));
        }
        if sorted.len() > 20 {
            lines.push(format!("  ... and {} more types", sorted.len() - 20));
        }
    } else {
        lines.push("No AI watermark characters detected".to_string());
    }
    lines.push(String::new());
    
    // Replaced characters
    lines.push("--- Replaced Characters ---".to_string());
    let total_replaced: usize = replaced.values().sum();
    lines.push(format!("Characters replaced: {}", total_replaced));
    
    if total_replaced > 0 {
        lines.push("Replaced character types:".to_string());
        let mut sorted: Vec<_> = replaced.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));
        for (ch, count) in sorted.iter().take(10) {
            let codepoint = format!("U+{:04X}", **ch as u32);
            lines.push(format!("  {}: {}", codepoint, count));
        }
        if sorted.len() > 10 {
            lines.push(format!("  ... and {} more types", sorted.len() - 10));
        }
    } else {
        lines.push("No characters replaced".to_string());
    }
    lines.push(String::new());
    
    // AI Forensic Analysis
    if let (Some(metrics), Some(ai_result)) = (ai_metrics, ai_result) {
        lines.push("=".repeat(70));
        lines.push("AI FORENSIC ANALYSIS".to_string());
        lines.push("=".repeat(70));
        lines.push(String::new());
        
        let (verdict, interpretations) = get_interpretation(metrics, ai_result.probability);
        
        lines.push(format!("Overall Verdict: {}", verdict));
        lines.push(format!("Confidence Level: {}", ai_result.confidence));
        lines.push(String::new());
        
        lines.push("Detailed Metrics:".to_string());
        lines.push(format!("  Word count:            {}", metrics.word_count));
        lines.push(format!("  Sentence count:        {}", metrics.sentence_count));
        lines.push(format!("  Lexical diversity:     {:.3}", metrics.lexical_diversity));
        lines.push(format!("  Repetition score:      {:.3}", metrics.repetition_score));
        lines.push(format!("  Entropy:               {:.3}", metrics.entropy));
        lines.push(format!("  Burstiness:            {:.3}", metrics.burstiness));
        lines.push(format!("  Pattern repetition:    {:.3}", metrics.pattern_repetition));
        lines.push(format!("  Punctuation density:   {:.3}", metrics.punctuation_density));
        lines.push(format!("  AI phrase hits:        {}", metrics.ai_phrase_hits));
        lines.push(format!("  Unicode suspicious:    {}", metrics.unicode_symbols));
        lines.push(format!("  Avg word length:       {:.2}", metrics.avg_word_length));
        lines.push(format!("  Word length variance:  {:.2}", metrics.word_length_variance));
        lines.push(String::new());
        
        if !interpretations.is_empty() {
            lines.push("Signal Analysis:".to_string());
            for interp in interpretations {
                lines.push(format!("  {}", interp));
            }
            lines.push(String::new());
        }
        
        lines.push("=".repeat(70));
        lines.push(String::new());
    }
    
    // Word frequency
    lines.push("--- Top Word Frequencies (Filtered) ---".to_string());
    if !word_freq.is_empty() {
        let mut sorted: Vec<_> = word_freq.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));
        for (word, count) in sorted.iter().take(20) {
            lines.push(format!("  {}: {}", word, count));
        }
    } else {
        lines.push("(skipped)".to_string());
    }
    
    lines.join("\n") + "\n"
}

fn chrono_local_now() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let duration = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    let secs = duration.as_secs();
    // Simple format - not using chrono to avoid dependency
    format!("{}", secs)
}

// =========================================================
// MAIN FUNCTION
// =========================================================

fn main() {
    let args: Vec<String> = std::env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: {} <input_file> [options]", args[0]);
        eprintln!("Options:");
        eprintln!("  -o, --output <file>       Output file (default: <input>.ed.txt)");
        eprintln!("  -r, --report <file>       Report file (default: report_rs-ext.txt)");
        eprintln!("  --no-edit                 Do not create .ed.txt file");
        eprintln!("  --no-report               Do not create report file");
        eprintln!("  --no-words                Exclude word frequency from report");
        eprintln!("  --remove-watermark        Remove AI watermark characters");
        eprintln!("  -h, --help                Show help");
        std::process::exit(1);
    }
    
    let input_file = &args[1];
    let mut output_file = String::new();
    let mut report_file = String::from("report_rs-ext.txt");
    let mut no_edit = false;
    let mut no_report = false;
    let mut no_words = false;
    let mut remove_watermark = false;
    
    let mut i = 2;
    while i < args.len() {
        match args[i].as_str() {
            "-o" | "--output" => {
                if i + 1 < args.len() {
                    output_file = args[i + 1].clone();
                    i += 2;
                } else {
                    i += 1;
                }
            }
            "-r" | "--report" => {
                if i + 1 < args.len() {
                    report_file = args[i + 1].clone();
                    i += 2;
                } else {
                    i += 1;
                }
            }
            "--no-edit" => {
                no_edit = true;
                i += 1;
            }
            "--no-report" => {
                no_report = true;
                i += 1;
            }
            "--no-words" => {
                no_words = true;
                i += 1;
            }
            "--remove-watermark" => {
                remove_watermark = true;
                i += 1;
            }
            "-h" | "--help" => {
                println!("Usage: {} <input_file> [options]", args[0]);
                println!("Options:");
                println!("  -o, --output <file>       Output file (default: <input>.ed.txt)");
                println!("  -r, --report <file>       Report file (default: report_rs-ext.txt)");
                println!("  --no-edit                 Do not create .ed.txt file");
                println!("  --no-report               Do not create report file");
                println!("  --no-words                Exclude word frequency from report");
                println!("  --remove-watermark        Remove AI watermark characters");
                println!("  -h, --help                Show help");
                return;
            }
            _ => {
                i += 1;
            }
        }
    }
    
    // Set default output file if not specified
    if output_file.is_empty() {
        let input_path = Path::new(input_file);
        let stem = input_path.file_stem().and_then(|s| s.to_str()).unwrap_or("output");
        output_file = format!("{}.ed.txt", stem);
    }
    
    // Read input file
    let text = match fs::read_to_string(input_file) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("Error reading {}: {}", input_file, e);
            std::process::exit(1);
        }
    };
    
    // Process text
    let start = Instant::now();
    let process_result = process(&text, remove_watermark);
    let elapsed = start.elapsed();
    
    // Calculate forensic metrics
    let word_freq = if no_words { HashMap::new() } else { word_frequency(&process_result.cleaned) };
    let ai_metrics = calculate_ai_forensic_metrics(&process_result.cleaned, &word_freq);
    let ai_result = ai_metrics.as_ref().map(calculate_ai_probability);
    
    // Write output file
    if !no_edit {
        if let Err(e) = fs::write(&output_file, &process_result.cleaned) {
            eprintln!("Error writing {}: {}", output_file, e);
        }
    }
    
    // Generate and write report
    if !no_report {
        let report_content = build_report(
            input_file,
            &output_file,
            &process_result.replaced,
            &process_result.watermark_removed,
            &word_freq,
            elapsed,
            &ai_metrics,
            &ai_result,
            remove_watermark,
            "Rust-Ext",
        );
        
        if let Err(e) = fs::write(&report_file, report_content) {
            eprintln!("Error writing {}: {}", report_file, e);
        }
    }
    
    // Print summary
    let total_replaced: usize = process_result.replaced.values().sum();
    let total_watermark: usize = process_result.watermark_removed.values().sum();
    
    println!("Processed in {:.6}s", elapsed.as_secs_f64());
    println!("Replacements: {}", total_replaced);
    println!("Watermarks removed: {}", total_watermark);
    if let Some(result) = ai_result {
        println!("AI Probability: {:.1}% (confidence: {})", result.probability, result.confidence);
    }
    println!("Output: {}", if no_edit { "(skipped)" } else { &output_file });
    println!("Report: {}", if no_report { "(skipped)" } else { &report_file });
}
