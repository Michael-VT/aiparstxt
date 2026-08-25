use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;
use std::time::Instant;

// =========================================================
// ENHANCED ALLOWED CHARACTERS
// =========================================================

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
// AI FORENSIC PATTERN DATABASES (v0.4.0)
// Canonical source: partxtpy/partxt-ext.py / AI_SIGNALS_SPEC.md
// =========================================================

// Suspicious Unicode characters - aligned with the parscgpt-ext.py reference
const UNICODE_SUSPICIOUS: [char; 19] = [
    '\u{2014}', '\u{2013}', '\u{201C}', '\u{201D}', '\u{2018}', '\u{2019}',
    '\u{2026}', '\u{2022}', '\u{2192}', '\u{2190}', '\u{2191}', '\u{2193}',
    '\u{00A9}', '\u{00AE}', '\u{2122}', '\u{00B0}', '\u{00B1}', '\u{00D7}', '\u{00F7}',
];

// AI-typical phrases: tiered multilingual database (v0.4.0).
// HIGH   - distinctive LLM template phrases, zero hits in human validation corpus
// MEDIUM - typical AI connective/register markers, rare in human corpus
// WEAK   - markers that also occur in human prose; evidence-only, tiny weight
const AI_PHRASES_HIGH: &[&str] = &[
    // English
    "it is important to note", "it's worth noting", "it is worth noting",
    "it should be emphasized", "it is crucial to understand",
    "it is essential to recognize", "it is noteworthy",
    "plays a crucial role", "plays an important role",
    "plays a significant role", "a testament to",
    "a wide range of", "a variety of",
    "first and foremost", "last but not least",
    "in conclusion", "to summarize", "in summary",
    // Russian
    "стоит отметить", "следует отметить", "необходимо отметить",
    "важно отметить", "важно понимать", "играет важную роль",
    "играет ключевую роль", "играет значительную роль",
    "играет существенную роль", "является одним из",
    "одним из важнейших", "одним из основных", "одной из ключевых",
    "ключевую роль", "существенную роль", "в значительной степени",
    "в заключение", "подводя итог", "широкий спектр",
    "по праву считается", "многочисленные исследования",
    // Ukrainian
    "варто зазначити", "слід зазначити", "необхідно зазначити",
    "важливо зазначити", "відіграє важливу роль",
    "відіграє ключову роль", "є одним із",
    "однією з найважливіших", "одним із основних",
    "значною мірою", "у висновку", "підсумовуючи",
    "широкий спектр", "ключову роль", "істотну роль",
    // Portuguese
    "vale ressaltar", "vale destacar", "é importante destacar",
    "é importante notar", "desempenha um papel",
    "desempenham um papel", "de grande importância",
    "em conclusão", "para concluir", "ampla gama",
    "ampla variedade", "ao longo dos anos",
    "nos dias de hoje", "cada vez mais",
];

const AI_PHRASES_MEDIUM: &[&str] = &[
    // English
    "moreover", "furthermore", "additionally", "consequently",
    "subsequently", "notably", "ultimately", "in essence",
    "fundamentally", "essentially", "on the other hand",
    "for instance", "as a result", "therefore", "overall",
    // Russian
    "более того", "с одной стороны", "с другой стороны",
    "во-первых", "во-вторых", "также как и", "наконец",
    // Ukrainian
    "крім того", "більше того", "з одного боку", "з іншого боку",
    "по-перше", "по-друге", "нарешті",
    // Portuguese
    "além disso", "dessa forma", "deste modo", "por um lado",
    "em primeiro lugar", "em segundo lugar", "de modo geral",
    "em termos gerais", "não obstante",
    "um dos mais", "uma das mais",
];

const AI_PHRASES_WEAK: &[&str] = &[
    // English
    "however", "various", "relatively", "somewhat", "quite", "rather",
    "fairly", "significantly", "considerably", "generally", "in general",
    "for example",
    // Russian
    "кроме того", "при этом", "однако", "следовательно",
    "соответственно", "многочисленные", "разнообразные",
    "сравнительно", "достаточно", "например", "таким образом",
    "в частности",
    // Ukrainian
    "при цьому", "однак", "отже", "численні", "різноманітні",
    "порівняно", "наприклад", "таким чином", "зокрема",
    // Portuguese
    "no entanto", "diversas", "diversos", "relativamente",
    "bastante", "por exemplo", "em resumo", "por outro lado",
    "portanto",
];

// Discourse connectives (all languages merged); used for connective_density.
const CONNECTIVES: &[&str] = &[
    // English
    "however", "moreover", "furthermore", "additionally", "therefore",
    "thus", "consequently", "for example", "for instance", "in addition",
    "similarly", "meanwhile", "overall", "as a result", "on the other hand",
    // Russian
    "однако", "при этом", "кроме того", "более того", "также",
    "таким образом", "следовательно", "поэтому", "в частности", "например",
    "во-первых", "во-вторых", "наконец", "в итоге", "в результате",
    "с одной стороны",
    // Ukrainian
    "однак", "при цьому", "крім того", "більше того", "також", "отже",
    "тому", "зокрема", "наприклад", "по-перше", "по-друге", "нарешті",
    "у результаті", "з одного боку", "таким чином",
    // Portuguese
    "no entanto", "além disso", "portanto", "assim", "por exemplo",
    "dessa forma", "em primeiro lugar", "em segundo lugar",
    "por conseguinte", "por outro lado", "deste modo",
];

// Scoring weights (v0.4.0) - canonical values, see AI_SIGNALS_SPEC.md
const SENT_CV_TIERS: [(f64, usize); 5] = [(0.30, 32), (0.35, 26), (0.40, 19), (0.45, 11), (0.50, 5)];
const PARA_CV_TIERS: [(f64, usize); 4] = [(0.15, 28), (0.25, 22), (0.35, 16), (0.45, 7)];
const JOINT_CV_TIERS: [(f64, usize); 2] = [(0.40, 14), (0.45, 10)];
const HIGH_PHRASE_SCORES: (usize, usize) = (24, 15);   // (>=2 hits, ==1 hit)
const MEDIUM_PHRASE_SCORES: (usize, usize) = (10, 5);  // (>=3 hits, >=1 hit)
const WEAK_PHRASE_SCORE: usize = 4;                    // >=4 hits
const CONNECTIVE_TIERS: [(f64, usize); 2] = [(0.12, 13), (0.08, 7)];
// Template header repetition: verbatim-repeated short non-punctuated lines
// ("Что верно" x7 etc.) - structured LLM answers reuse section templates.
// Zero hits in the human validation corpus.
const TEMPLATE_HEADER_MIN_REPEATS: usize = 3;
const TEMPLATE_HEADER_SCORES: (usize, usize) = (14, 8); // (>=2 distinct templates or >=10 repeats, >=3 repeats)
// Structural-signal reliability scaling (v0.4.0): tier points are scaled by
// sample reliability instead of being silently zeroed on short texts.
const SENT_CV_MIN_SENTENCES: usize = 5;   // below this, sentence CV is pure noise -> 0
const SENT_CV_FULL_SENTENCES: usize = 15; // full weight from this many sentences on
const PARA_CV_MIN_PARAGRAPHS: usize = 3;  // below this, paragraph CV is not computed
const PARA_CV_FULL_PARAGRAPHS: usize = 4;
const MIN_WORDS_FOR_CV: usize = 40;
const FULL_WORDS_FOR_CV: usize = 150;

// Emulate Python's int(round(x)) (banker's rounding) for non-negative values.
fn py_round(x: f64) -> usize {
    let floor = x.floor();
    let diff = x - floor;
    let v = if diff > 0.5 {
        floor + 1.0
    } else if diff < 0.5 {
        floor
    } else if (floor as i64) % 2 == 0 {
        floor
    } else {
        floor + 1.0
    };
    v.max(0.0) as usize
}

// Passive voice patterns (reference basis for passive_voice_density)
const AI_PASSIVE_PATTERNS: &[&str] = &[
    "is considered to be", "are considered to be",
    "is often said to be", "are often said to be",
    "is generally regarded as", "are generally regarded as",
    "is typically characterized by", "are typically characterized by",
    "is commonly associated with", "are commonly associated with",
    "is widely recognized as", "are widely recognized as",
    "is frequently observed to", "are frequently observed to",
    "is usually understood to", "are usually understood to",
];

const STOPWORDS: &[&str] = &[
    // English stopwords
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

    // Russian stopwords
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
];

fn stopwords_set() -> HashSet<&'static str> {
    STOPWORDS.iter().cloned().collect()
}

// =========================================================
// FORENSIC ANALYSIS STRUCTS
// =========================================================

#[derive(Debug, Clone)]
struct PhraseOccurrence {
    tier: usize, // 0=high, 1=medium, 2=weak
    phrase: &'static str,
    idx: usize,  // char offset in the lowercased text (aligned with original)
}

#[derive(Debug)]
struct AIMetrics {
    word_count: usize,
    sentence_count: usize,
    lexical_diversity: f64,
    repetition_score: f64,
    entropy: f64,
    burstiness: f64,
    paragraph_uniformity_cv: Option<f64>,
    paragraph_count: usize, // paragraph count when para CV is computable, else 0
    pattern_repetition: f64,
    punctuation_density: f64,
    ai_phrase_hits: usize,
    ai_phrase_tiers: [usize; 3], // high, medium, weak occurrence counts
    ai_phrase_occurrences: Vec<PhraseOccurrence>,
    connective_density: f64,
    template_header_total: usize,
    template_header_distinct: usize,
    template_header_occurrences: Vec<(String, usize, usize)>, // (line, count, first line no)
    sentences: Vec<String>,
    paragraph_lengths: Vec<usize>,
    unicode_symbols: usize,
    avg_word_length: f64,
    word_length_variance: f64,
    pronoun_ratio: f64,
    readability_score: f64,
    passive_voice_density: f64,
    adj_noun_pair_diversity: f64,
    structural_uniformity: f64,
    quantifier_overuse: f64,
    promotional_register: bool,
}

#[derive(Debug)]
struct AIResult {
    probability: f64,
    confidence: String,
}

#[derive(Debug)]
struct Evidence {
    detail: String,
    line: Option<usize>,
    excerpt: Option<String>,
}

// =========================================================
// LOW-LEVEL TEXT HELPERS
// =========================================================

fn lower_char(c: char) -> char {
    let mut it = c.to_lowercase();
    let first = it.next().unwrap();
    if it.next().is_none() {
        first
    } else {
        c // multi-char lowercase expansion: keep original to stay index-aligned
    }
}

fn lower_vec(s: &str) -> Vec<char> {
    s.chars().map(lower_char).collect()
}

fn find_from(hay: &[char], needle: &[char], from: usize) -> Option<usize> {
    if needle.is_empty() || hay.len() < needle.len() {
        return None;
    }
    let mut i = from;
    while i + needle.len() <= hay.len() {
        if hay[i..i + needle.len()] == *needle {
            return Some(i);
        }
        i += 1;
    }
    None
}

fn rfind_before(hay: &[char], needle: &[char], before: usize) -> Option<usize> {
    if needle.is_empty() {
        return None;
    }
    let mut i = before as isize - needle.len() as isize;
    while i >= 0 {
        let start = i as usize;
        if hay[start..start + needle.len()] == *needle {
            return Some(start);
        }
        i -= 1;
    }
    None
}

fn truncate_middle_chars(s: &[char], width: usize) -> String {
    if s.len() <= width {
        return s.iter().collect();
    }
    let half = width / 2 - 5;
    let left: String = s[..half].iter().collect();
    let right: String = s[s.len() - half..].iter().collect();
    format!("{} ... {}", left, right)
}

// Split on \n\s*\n (runs of whitespace containing >= 2 newlines)
fn split_paragraphs(text: &str) -> Vec<String> {
    let chars: Vec<char> = text.chars().collect();
    let mut parts = Vec::new();
    let mut start = 0usize;
    let mut i = 0usize;
    while i < chars.len() {
        if chars[i] == '\n' {
            let mut j = i + 1;
            while j < chars.len() && chars[j].is_whitespace() {
                j += 1;
            }
            let nl = chars[i..j].iter().filter(|&&c| c == '\n').count();
            if nl >= 2 {
                parts.push(chars[start..i].iter().collect::<String>());
                start = j;
                i = j;
                continue;
            }
        }
        i += 1;
    }
    parts.push(chars[start..].iter().collect::<String>());
    parts
}

// Python's re \w (word char) = Letter/Number categories + '_'.
// Rust's char::is_alphanumeric additionally includes combining vowel
// signs and other Other_Alphabetic marks (Mn/Mc), e.g. Thai "ั" "ี",
// which Python \w does NOT match. Exclude the Unicode Mark blocks so
// tokenization matches re.findall(r'\b\w+\b') on the reference corpus.
fn is_unicode_mark(c: char) -> bool {
    matches!(c as u32,
        0x0300..=0x036F | 0x0483..=0x0489 | 0x0591..=0x05BD | 0x05BF | 0x05C1..=0x05C2 |
        0x05C4..=0x05C5 | 0x05C7 | 0x0610..=0x061A | 0x064B..=0x065F | 0x0670 |
        0x06D6..=0x06DC | 0x06DF..=0x06E4 | 0x06E7..=0x06E8 | 0x06EA..=0x06ED |
        0x0711 | 0x0730..=0x074A | 0x07A6..=0x07B0 | 0x07EB..=0x07F3 |
        0x0816..=0x0819 | 0x081B..=0x0823 | 0x0825..=0x0827 | 0x0829..=0x082D |
        0x0859..=0x085B | 0x08D3..=0x08E1 | 0x08E3..=0x0903 | 0x093A..=0x093C |
        0x093E..=0x094F | 0x0951..=0x0957 | 0x0962..=0x0963 | 0x0981..=0x0983 |
        0x09BC..=0x09CD | 0x09D7 | 0x09E2..=0x09E3 | 0x0A01..=0x0A03 | 0x0A3C..=0x0A51 |
        0x0A70..=0x0A71 | 0x0A75 | 0x0A81..=0x0A83 | 0x0ABC..=0x0ACD | 0x0AE2..=0x0AE3 |
        0x0B01..=0x0B03 | 0x0B3C..=0x0B57 | 0x0B62..=0x0B63 | 0x0B82 |
        0x0BBE..=0x0BCD | 0x0BD7 | 0x0C00..=0x0C04 | 0x0C3E..=0x0C56 | 0x0C62..=0x0C63 |
        0x0C81..=0x0C83 | 0x0CBC..=0x0CD6 | 0x0CE2..=0x0CE3 | 0x0D00..=0x0D03 |
        0x0D3B..=0x0D4D | 0x0D57 | 0x0D62..=0x0D63 | 0x0D82..=0x0D83 |
        0x0DCA..=0x0DDF | 0x0DF2..=0x0DF3 | 0x0E31 | 0x0E34..=0x0E3A | 0x0E47..=0x0E4E |
        0x0EB1 | 0x0EB4..=0x0EBC | 0x0EC8..=0x0ECD | 0x0F18..=0x0F19 | 0x0F35 | 0x0F37 |
        0x0F39 | 0x0F3E..=0x0F3F | 0x0F71..=0x0F84 | 0x0F86..=0x0F87 | 0x0F8D..=0x0FBC |
        0x0FC6 | 0x102D..=0x1030 | 0x1032..=0x1037 | 0x1039..=0x103A | 0x103D..=0x103E |
        0x1058..=0x1059 | 0x105E..=0x1060 | 0x1071..=0x1074 | 0x1082 | 0x1085..=0x1086 |
        0x108D | 0x135D..=0x135F | 0x1712..=0x1714 | 0x1732..=0x1734 |
        0x1752..=0x1753 | 0x1772..=0x1773 | 0x17B4..=0x17D3 | 0x17DD | 0x180B..=0x180D |
        0x1885..=0x1886 | 0x18A9 | 0x1920..=0x193B | 0x1A17..=0x1A1B | 0x1A55..=0x1A5E |
        0x1A60..=0x1A7C | 0x1A7F | 0x1AB0..=0x1AFF | 0x1B00..=0x1B04 | 0x1B34..=0x1B44 |
        0x1B6B..=0x1B73 | 0x1B80..=0x1B82 | 0x1BA1..=0x1BAD | 0x1BE6..=0x1BF3 |
        0x1C24..=0x1C37 | 0x1CD0..=0x1CD2 | 0x1CD4..=0x1CE8 | 0x1CED | 0x1CF4 |
        0x1CF7..=0x1CF9 | 0x1DC0..=0x1DFF | 0x20D0..=0x20F0 | 0x2CEF..=0x2CF1 |
        0x2D7F | 0x2DE0..=0x2DFF | 0x302A..=0x302F | 0x3099..=0x309A | 0xA66F..=0xA672 |
        0xA674..=0xA67D | 0xA69E..=0xA69F | 0xA6F0..=0xA6F1 | 0xA802 | 0xA806 | 0xA80B |
        0xA825..=0xA826 | 0xA8C4..=0xA8C5 | 0xA8E0..=0xA8F1 | 0xA926..=0xA92D |
        0xA947..=0xA951 | 0xA980..=0xA982 | 0xA9B3 | 0xA9B6..=0xA9B9 | 0xA9BC..=0xA9BD |
        0xAA29..=0xAA2E | 0xAA31..=0xAA32 | 0xAA35..=0xAA36 | 0xAA43 | 0xAA4C |
        0xAAB0 | 0xAAB2..=0xAAB4 | 0xAAB7..=0xAAB8 | 0xAABE..=0xAABF | 0xAAC1 |
        0xAAEC..=0xAAED | 0xAAF6 | 0xABE5 | 0xABE8 | 0xABED | 0xFB1E |
        0xFE00..=0xFE0F | 0xFE20..=0xFE2F
    )
}

// Tokenize like Python re.findall(r'\b\w+\b', text.lower())
fn tokenize_words(text: &str) -> Vec<String> {
    let lower = text.to_lowercase();
    let mut words = Vec::new();
    let mut cur = String::new();
    for ch in lower.chars() {
        if (ch.is_alphanumeric() || ch == '_') && !is_unicode_mark(ch) {
            cur.push(ch);
        } else if !cur.is_empty() {
            words.push(std::mem::take(&mut cur));
        }
    }
    if !cur.is_empty() {
        words.push(cur);
    }
    words
}

fn pstdev(vals: &[f64]) -> f64 {
    if vals.is_empty() {
        return 0.0;
    }
    let mean = vals.iter().sum::<f64>() / vals.len() as f64;
    let var = vals.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / vals.len() as f64;
    var.sqrt()
}

fn sample_stdev(vals: &[f64]) -> f64 {
    if vals.len() < 2 {
        return 0.0;
    }
    let mean = vals.iter().sum::<f64>() / vals.len() as f64;
    let var = vals.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / (vals.len() - 1) as f64;
    var.sqrt()
}

fn tier_lists() -> [&'static [&'static str]; 3] {
    [AI_PHRASES_HIGH, AI_PHRASES_MEDIUM, AI_PHRASES_WEAK]
}

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

fn word_frequency(text: &str) -> HashMap<String, usize> {
    let stopwords = stopwords_set();
    let mut freq = HashMap::new();
    let mut current_word = String::new();

    for ch in text.to_lowercase().chars() {
        if ch.is_alphabetic() || ch == '\'' {
            current_word.push(ch);
        } else if !current_word.is_empty() {
            if current_word.chars().count() > 2 && !stopwords.contains(current_word.as_str()) {
                *freq.entry(current_word.clone()).or_insert(0) += 1;
            }
            current_word.clear();
        }
    }

    if !current_word.is_empty()
        && current_word.chars().count() > 2
        && !stopwords.contains(current_word.as_str())
    {
        *freq.entry(current_word).or_insert(0) += 1;
    }

    freq
}

// Split text into sentences (aligned with the Python reference):
// mask Mr|Mrs|Ms|Dr|Prof|Sr|Jr. as <DOT>, split on [.!?]+,
// keep sentences that are non-empty after trimming and longer than 3 chars.
fn split_sentences(text: &str) -> Vec<String> {
    const ABBREV: [&str; 7] = ["Mr", "Mrs", "Ms", "Dr", "Prof", "Sr", "Jr"];
    let chars: Vec<char> = text.chars().collect();
    let is_word = |c: char| c.is_alphanumeric() || c == '_';

    let mut masked = String::with_capacity(text.len());
    let mut i = 0usize;
    while i < chars.len() {
        let boundary_ok = i == 0 || !is_word(chars[i - 1]);
        if boundary_ok {
            let mut matched = false;
            for abbr in ABBREV.iter() {
                let ac: Vec<char> = abbr.chars().collect();
                if chars.len() >= i + ac.len() + 1
                    && chars[i..i + ac.len()] == ac[..]
                    && chars[i + ac.len()] == '.'
                {
                    masked.push_str(abbr);
                    masked.push_str("<DOT>");
                    i += ac.len() + 1;
                    matched = true;
                    break;
                }
            }
            if matched {
                continue;
            }
        }
        masked.push(chars[i]);
        i += 1;
    }

    // split on runs of [.!?]+
    let mut raw: Vec<String> = Vec::new();
    let mut cur = String::new();
    let mut in_sep = false;
    for c in masked.chars() {
        if c == '.' || c == '!' || c == '?' {
            in_sep = true;
        } else {
            if in_sep {
                raw.push(std::mem::take(&mut cur));
                in_sep = false;
            }
            cur.push(c);
        }
    }
    raw.push(cur);

    raw.into_iter()
        .map(|s| s.trim().replace("<DOT>", "."))
        .filter(|s| !s.trim().is_empty() && s.chars().count() > 3)
        .collect()
}

/// Calculate comprehensive AI forensic metrics.
/// Must be called on the ORIGINAL (pre-sanitization) text: sanitization
/// inserts '?' which corrupts sentence splitting and phrase positions.
/// Basis aligned with the Python reference (AI_SIGNALS_SPEC.md).
fn calculate_ai_forensic_metrics(text: &str) -> Option<AIMetrics> {
    if text.is_empty() {
        return None;
    }

    let stopwords = stopwords_set();
    let words = tokenize_words(text);
    let sentences = split_sentences(text);

    if words.is_empty() || sentences.is_empty() {
        return None;
    }

    // Filtered words (reference basis for diversity/entropy/repetition)
    let filtered: Vec<&String> = words
        .iter()
        .filter(|w| !stopwords.contains(w.as_str()) && w.chars().count() > 2)
        .collect();
    let mut filtered_counter: HashMap<&str, usize> = HashMap::new();
    for w in &filtered {
        *filtered_counter.entry(w.as_str()).or_insert(0) += 1;
    }

    // Core metrics
    let word_count = words.len();
    let sentence_count = sentences.len();

    // Lexical diversity (on filtered words, as in reference)
    let lexical_div = if !filtered.is_empty() {
        filtered_counter.len() as f64 / filtered.len() as f64
    } else {
        0.0
    };

    // Repetition score (distinct repeated filtered words / filtered words)
    let repeated = filtered_counter.values().filter(|&&c| c > 1).count();
    let rep_score = if !filtered.is_empty() {
        repeated as f64 / filtered.len() as f64
    } else {
        0.0
    };

    // Entropy (on filtered words, as in reference)
    let total = filtered.len();
    let entropy = if total > 0 {
        -filtered_counter
            .values()
            .map(|&c| {
                let p = c as f64 / total as f64;
                p * p.log2()
            })
            .sum::<f64>()
    } else {
        0.0
    };

    // Sentence length analysis (burstiness = CV of sentence word counts);
    // word count per sentence uses whitespace split, as in the reference
    let sent_lengths: Vec<usize> = sentences.iter().map(|s| s.split_whitespace().count()).collect();
    let sent_lengths_f: Vec<f64> = sent_lengths.iter().map(|&l| l as f64).collect();
    let avg_sent_len = sent_lengths_f.iter().sum::<f64>() / sent_lengths_f.len() as f64;
    let burstiness = if avg_sent_len > 0.0 && sent_lengths_f.len() > 1 {
        pstdev(&sent_lengths_f) / avg_sent_len
    } else {
        0.0
    };

    // Paragraph length uniformity (CV of paragraph word counts)
    let paragraphs: Vec<String> = split_paragraphs(text)
        .into_iter()
        .filter(|p| p.split_whitespace().count() > 15)
        .collect();
    let para_lengths: Vec<usize> = paragraphs.iter().map(|p| p.split_whitespace().count()).collect();
    let (paragraph_uniformity_cv, paragraph_count) = if para_lengths.len() >= PARA_CV_MIN_PARAGRAPHS {
        let para_f: Vec<f64> = para_lengths.iter().map(|&l| l as f64).collect();
        let para_avg = para_f.iter().sum::<f64>() / para_f.len() as f64;
        (
            Some(if para_avg > 0.0 {
                pstdev(&para_f) / para_avg
            } else {
                0.0
            }),
            para_lengths.len(),
        )
    } else {
        (None, 0)
    };

    // Pattern repetition
    let categorize_length = |length: usize| -> char {
        if length <= 10 {
            'S'
        } else if length <= 20 {
            'M'
        } else {
            'L'
        }
    };
    let patterns: Vec<char> = sent_lengths.iter().map(|&l| categorize_length(l)).collect();
    let mut pattern_counts: HashMap<char, usize> = HashMap::new();
    for &p in &patterns {
        *pattern_counts.entry(p).or_insert(0) += 1;
    }
    let repeated_patterns = pattern_counts.values().filter(|&&c| c > 1).count();
    let pattern_rep = if !patterns.is_empty() {
        repeated_patterns as f64 / patterns.len() as f64
    } else {
        0.0
    };

    // Punctuation density (reference char class [,;:()-—–])
    let text_char_count = text.chars().count();
    let punct_count = text
        .chars()
        .filter(|&c| matches!(c, ',' | ';' | ':' | '(' | ')' | '-' | '—' | '–'))
        .count();
    let punct_density = if text_char_count > 0 {
        punct_count as f64 / text_char_count as f64
    } else {
        0.0
    };

    // AI phrase detection (tiered, with occurrences for evidence)
    let text_lower_vec = lower_vec(text);
    let text_lower: String = text_lower_vec.iter().collect();
    let mut ai_hits = 0usize;
    let mut phrase_tiers = [0usize; 3];
    let mut phrase_occurrences: Vec<PhraseOccurrence> = Vec::new();
    let tiers = tier_lists();
    for (tier_idx, list) in tiers.iter().enumerate() {
        for &phrase in list.iter() {
            let pc: Vec<char> = phrase.chars().collect();
            let mut found = 0usize;
            let mut idx_opt = find_from(&text_lower_vec, &pc, 0);
            while let Some(idx) = idx_opt {
                if found < 3 {
                    phrase_occurrences.push(PhraseOccurrence {
                        tier: tier_idx,
                        phrase,
                        idx,
                    });
                }
                found += 1;
                idx_opt = find_from(&text_lower_vec, &pc, idx + pc.len());
            }
            if found > 0 {
                ai_hits += 1;
                phrase_tiers[tier_idx] += found;
            }
        }
    }

    // Connective density (connectives per sentence)
    let mut conn_total = 0usize;
    for s in &sentences {
        let s_lower = s.to_lowercase();
        conn_total += CONNECTIVES.iter().filter(|c| s_lower.contains(*c)).count();
    }
    let connective_density = if sentence_count > 0 {
        conn_total as f64 / sentence_count as f64
    } else {
        0.0
    };

    // Template header repetition (structured-answer genre)
    let mut tmpl_counts: HashMap<&str, usize> = HashMap::new();
    let mut tmpl_order: Vec<&str> = Vec::new(); // first-encounter order, like Counter
    let mut tmpl_first_line: HashMap<&str, usize> = HashMap::new();
    for (i, raw) in text.split('\n').enumerate() {
        let line = raw.trim();
        let line_chars: Vec<char> = line.chars().collect();
        let word_count = line.split_whitespace().count();
        let first_digit = line_chars.first().map_or(false, |c| c.is_numeric());
        if (4 <= line_chars.len() && line_chars.len() <= 60 && word_count >= 1 && word_count <= 8)
            && !line_chars.is_empty()
            && !".!?:;,…\"»„".contains(line_chars[line_chars.len() - 1])
            && !first_digit
        {
            let entry = tmpl_counts.entry(line).or_insert(0);
            if *entry == 0 {
                tmpl_order.push(line);
                tmpl_first_line.insert(line, i + 1);
            }
            *entry += 1;
        }
    }
    let mut tmpl_occurrences: Vec<(String, usize, usize)> = Vec::new();
    let mut tmpl_total = 0usize;
    let mut tmpl_distinct = 0usize;
    for line in &tmpl_order {
        let count = tmpl_counts[line];
        if count >= TEMPLATE_HEADER_MIN_REPEATS {
            tmpl_total += count;
            tmpl_distinct += 1;
            tmpl_occurrences.push((line.to_string(), count, tmpl_first_line[line]));
        }
    }
    tmpl_occurrences.sort_by(|a, b| b.1.cmp(&a.1)); // stable, preserves first-encounter order

    // Unicode suspicious chars - count how many of the suspicious chars
    // appear in the ORIGINAL (pre-sanitization) text, matching the reference
    let unicode_count = UNICODE_SUSPICIOUS.iter().filter(|&&c| text.contains(c)).count();

    // Word length statistics
    let word_lengths: Vec<f64> = words.iter().map(|w| w.chars().count() as f64).collect();
    let avg_word_len = word_lengths.iter().sum::<f64>() / word_lengths.len().max(1) as f64;
    let word_len_var = sample_stdev(&word_lengths);

    // --- Supporting metrics (mirror the Python reference) ---
    // Pronoun ratio
    let pronoun_lists: &[&[&str]] = &[
        &["i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"],
        &["you", "your", "yours", "yourself", "yourselves"],
        &["he", "him", "his", "himself", "she", "her", "hers", "herself",
          "it", "its", "itself", "they", "them", "their", "theirs", "themselves"],
        &["this", "that", "these", "those"],
        &["anyone", "anything", "everyone", "everything", "someone", "something",
          "noone", "nothing", "each", "every", "either", "neither", "both", "few",
          "many", "several"],
    ];
    let all_pronouns: HashSet<&&str> = pronoun_lists.iter().flat_map(|l| l.iter()).collect();
    let pronoun_ratio = if word_count > 0 {
        words.iter().filter(|w| all_pronouns.contains(&w.as_str())).count() as f64
            / word_count as f64
    } else {
        0.0
    };

    // Readability (Flesch, simplified syllables)
    let syllable_count: usize = words
        .iter()
        .map(|w| {
            let v = w.chars().filter(|&ch| matches!(ch, 'a' | 'e' | 'i' | 'o' | 'u' | 'y')).count();
            v.max(1)
        })
        .sum();
    let avg_sentence_length = word_count as f64 / sentence_count.max(1) as f64;
    let avg_syllables_per_word = syllable_count as f64 / word_count.max(1) as f64;
    let flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word);
    let readability = flesch.clamp(0.0, 100.0);

    // Passive voice density
    let passive_count: usize = AI_PASSIVE_PATTERNS
        .iter()
        .map(|p| text_lower.matches(p).count())
        .sum();
    let ws_count = text.split_whitespace().count();
    let passive_density = passive_count as f64 / ws_count.max(1) as f64;

    // Adjective-noun pair diversity
    let adj_indicators = ["al", "ble", "cal", "ful", "ic", "ive", "less", "ous"];
    let noun_indicators = ["er", "ism", "ment", "ness", "tion", "ship", "cy", "dom"];
    let adjectives: HashSet<&String> = words
        .iter()
        .filter(|w| adj_indicators.iter().any(|ind| w.ends_with(ind)))
        .collect();
    let nouns: HashSet<&String> = words
        .iter()
        .filter(|w| noun_indicators.iter().any(|ind| w.ends_with(ind)))
        .collect();
    let mut pairs: HashSet<String> = HashSet::new();
    for i in 0..words.len().saturating_sub(1) {
        if adjectives.contains(&words[i]) && nouns.contains(&words[i + 1]) {
            pairs.insert(format!("{} {}", words[i], words[i + 1]));
        }
    }
    let total_possible = if !adjectives.is_empty() && !nouns.is_empty() {
        adjectives.len() * nouns.len()
    } else {
        1
    };
    let adj_noun_div = pairs.len() as f64 / total_possible as f64;

    // Structural uniformity (repeated 2-word sentence starts)
    let starts: Vec<String> = sentences
        .iter()
        .filter(|s| !s.split_whitespace().collect::<Vec<_>>().is_empty())
        .map(|s| {
            s.split_whitespace()
                .take(2)
                .collect::<Vec<_>>()
                .join(" ")
                .to_lowercase()
        })
        .collect();
    let mut start_counter: HashMap<&str, usize> = HashMap::new();
    for s in &starts {
        *start_counter.entry(s.as_str()).or_insert(0) += 1;
    }
    let repeated_starts = start_counter.values().filter(|&&c| c > 1).count();
    let struct_unif = if !sentences.is_empty() {
        repeated_starts as f64 / sentences.len() as f64
    } else {
        0.0
    };

    // Quantifier overuse
    let quantifiers = ["relatively", "somewhat", "quite", "rather", "fairly",
                       "reasonably", "comparatively", "moderately", "substantially",
                       "considerably", "significantly", "notably", "remarkably"];
    let quant_count: usize = quantifiers.iter().map(|q| text_lower.matches(q).count()).sum();
    let quant_overuse = quant_count as f64 / ws_count.max(1) as f64;

    // Promotional/social-media register (genre abstention, NOT an AI score:
    // both AI hype posts and human SMM copy trigger this)
    let promo_emoji = text.chars().filter(|&c| c as u32 >= 0x2600).count();
    let promo_excl = if word_count > 0 {
        text.matches('!').count() as f64 / word_count as f64
    } else {
        0.0
    };
    let promotional_register = promo_emoji >= 5 && promo_excl >= 0.02;

    Some(AIMetrics {
        word_count,
        sentence_count,
        lexical_diversity: lexical_div,
        repetition_score: rep_score,
        entropy,
        burstiness,
        paragraph_uniformity_cv,
        paragraph_count,
        pattern_repetition: pattern_rep,
        punctuation_density: punct_density,
        ai_phrase_hits: ai_hits,
        ai_phrase_tiers: phrase_tiers,
        ai_phrase_occurrences: phrase_occurrences,
        connective_density,
        template_header_total: tmpl_total,
        template_header_distinct: tmpl_distinct,
        template_header_occurrences: tmpl_occurrences,
        sentences,
        paragraph_lengths: para_lengths,
        unicode_symbols: unicode_count,
        avg_word_length: avg_word_len,
        word_length_variance: word_len_var,
        pronoun_ratio,
        readability_score: readability,
        passive_voice_density: passive_density,
        adj_noun_pair_diversity: adj_noun_div,
        structural_uniformity: struct_unif,
        quantifier_overuse: quant_overuse,
        promotional_register,
    })
}

fn calculate_ai_probability(metrics: &AIMetrics) -> AIResult {
    let mut total: usize = 0;

    macro_rules! add {
        ($name:expr, $points:expr) => {
            // $name documents which metric contributes; only points are summed
            if $points > 0 {
                total += $points;
            }
        };
    }

    // --- Primary structural signals ---
    // Tier points are scaled by statistical reliability of the sample
    // (short texts get partial credit instead of a silent zero).
    let sent_cv = metrics.burstiness;
    let sent_scale = (metrics.sentence_count as f64 / SENT_CV_FULL_SENTENCES as f64).min(1.0)
        * (metrics.word_count as f64 / FULL_WORDS_FOR_CV as f64).min(1.0);
    let mut sent_cv_points = 0usize;
    if metrics.sentence_count >= SENT_CV_MIN_SENTENCES && metrics.word_count >= MIN_WORDS_FOR_CV {
        for &(threshold, points) in SENT_CV_TIERS.iter() {
            if sent_cv < threshold {
                sent_cv_points = py_round(points as f64 * sent_scale);
                break;
            }
        }
    }
    add!("sentence_cv", sent_cv_points);

    let para_cv = metrics.paragraph_uniformity_cv;
    let mut para_points = 0usize;
    let mut para_scale = 0.0f64;
    if let Some(pcv) = para_cv {
        para_scale =
            (metrics.paragraph_count as f64 / PARA_CV_FULL_PARAGRAPHS as f64).min(1.0);
        for &(threshold, points) in PARA_CV_TIERS.iter() {
            if pcv < threshold {
                para_points = py_round(points as f64 * para_scale);
                break;
            }
        }
    }
    add!("paragraph_cv", para_points);

    if let Some(pcv) = para_cv {
        if sent_cv_points > 0 {
            for &(threshold, points) in JOINT_CV_TIERS.iter() {
                if sent_cv < threshold && pcv < threshold {
                    let joint_points = py_round(points as f64 * sent_scale.min(para_scale));
                    add!("joint_uniformity", joint_points);
                    break;
                }
            }
        }
    }

    // --- Tiered phrase scores ---
    let tiers = &metrics.ai_phrase_tiers;
    if tiers[0] >= 2 {
        add!("ai_phrases", HIGH_PHRASE_SCORES.0);
    } else if tiers[0] == 1 {
        add!("ai_phrases", HIGH_PHRASE_SCORES.1);
    } else if tiers[1] >= 3 {
        add!("ai_phrases", MEDIUM_PHRASE_SCORES.0);
    } else if tiers[1] >= 1 {
        add!("ai_phrases", MEDIUM_PHRASE_SCORES.1);
    } else if tiers[2] >= 4 {
        add!("ai_phrases", WEAK_PHRASE_SCORE);
    }

    // --- Connective density ---
    for &(threshold, points) in CONNECTIVE_TIERS.iter() {
        if metrics.connective_density >= threshold {
            add!("connectives", points);
            break;
        }
    }

    // --- Template header repetition (structured-answer genre) ---
    if metrics.template_header_distinct >= 2 || metrics.template_header_total >= 10 {
        add!("template_headers", TEMPLATE_HEADER_SCORES.0);
    } else if metrics.template_header_total >= TEMPLATE_HEADER_MIN_REPEATS {
        add!("template_headers", TEMPLATE_HEADER_SCORES.1);
    }

    // --- Supporting statistical metrics ---
    if metrics.lexical_diversity < 0.45 {
        add!("lexical_diversity", 15);
    } else if metrics.lexical_diversity < 0.55 {
        add!("lexical_diversity", 8);
    }

    if metrics.entropy < 5.0 {
        add!("entropy", 15);
    } else if metrics.entropy < 6.5 {
        add!("entropy", 8);
    }

    if metrics.pattern_repetition > 0.35 {
        add!("pattern_repetition", 10);
    }

    if metrics.repetition_score > 0.5 {
        add!("repetition", 8);
    }

    if metrics.punctuation_density > 0.04 {
        add!("punctuation", 4);
    }

    if metrics.unicode_symbols > 0 {
        add!("unicode", 4);
    }

    if metrics.avg_word_length < 4.0 {
        add!("avg_word_length", 5);
    } else if metrics.avg_word_length < 4.5 {
        add!("avg_word_length", 3);
    }

    if metrics.word_length_variance < 1.5 {
        add!("word_length_variance", 4);
    }

    if metrics.pronoun_ratio > 0.15 {
        add!("pronoun_ratio", 4);
    }

    if metrics.readability_score > 70.0 {
        add!("readability", 5);
    } else if metrics.readability_score > 60.0 {
        add!("readability", 3);
    }

    if metrics.passive_voice_density > 0.05 {
        add!("passive_voice", 4);
    }

    if metrics.adj_noun_pair_diversity < 0.3 {
        add!("adj_noun_diversity", 3);
    }

    if metrics.structural_uniformity > 0.4 {
        add!("structural_uniformity", 4);
    }

    if metrics.quantifier_overuse > 0.02 {
        add!("quantifier_overuse", 3);
    }

    // Length-based confidence adjustment
    let word_count = metrics.word_count;
    let confidence = if word_count < 300 {
        "LOW".to_string()
    } else if word_count < 1000 {
        "MEDIUM".to_string()
    } else {
        "HIGH".to_string()
    };

    let length_factor = (word_count as f64 / 1000.0).min(1.0);
    let adjusted_total = total as f64 * (0.9 + 0.1 * length_factor);
    let probability = adjusted_total.min(100.0);

    AIResult {
        probability,
        confidence,
    }
}

fn get_interpretation(metrics: &AIMetrics, ai_probability: f64) -> (String, Vec<String>) {
    let mut interpretations = Vec::new();

    let mut verdict = if ai_probability > 70.0 {
        format!("Strong AI-like statistical profile ({:.1}%)", ai_probability)
    } else if ai_probability > 55.0 {
        format!("Probable AI-generated text with multiple indicators ({:.1}%)", ai_probability)
    } else if ai_probability > 35.0 {
        format!("Mixed profile: human-like and AI-like signals ({:.1}%)", ai_probability)
    } else {
        format!("Text statistically appears more human-like ({:.1}%)", ai_probability)
    };

    // Honest abstention: below the structural-signal horizon the "human-like"
    // verdict would be an artifact of missing data, not evidence.
    if metrics.word_count < FULL_WORDS_FOR_CV || metrics.sentence_count < SENT_CV_MIN_SENTENCES {
        verdict += " NOTE: text is too short for reliable structural analysis — \
                    this verdict is unreliable, not evidence of human authorship.";
    }

    // Genre abstention: promotional/social register - verdict withdrawn, no AI points
    if metrics.promotional_register {
        verdict += " NOTE: promotional/social-media register (emoji- and \
                    exclamation-heavy) is outside the calibration corpus — \
                    this verdict is unreliable for this genre.";
    }

    if metrics.burstiness < 0.35 {
        interpretations.push("⚠️ Uniform sentence lengths (low burstiness) - strong AI signal".to_string());
    } else if metrics.burstiness < 0.45 {
        interpretations.push("⚠️ Somewhat uniform sentence lengths - AI-like".to_string());
    }

    if let Some(pcv) = metrics.paragraph_uniformity_cv {
        if pcv < 0.35 {
            interpretations.push("⚠️ Uniform paragraph lengths - AI-like".to_string());
        }
    }

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

    let tiers = &metrics.ai_phrase_tiers;
    if tiers[0] > 0 || tiers[1] > 0 {
        interpretations.push(format!(
            "⚠️ AI phrases: high={}, medium={}",
            tiers[0], tiers[1]
        ));
    }

    if metrics.connective_density >= 0.12 {
        interpretations.push("⚠️ High discourse-connective density".to_string());
    }

    if metrics.pattern_repetition > 0.35 {
        interpretations.push("⚠️ High pattern repetition - template-like structure".to_string());
    }

    if metrics.unicode_symbols > 0 {
        interpretations.push(format!(
            "⚠️ Found {} suspicious Unicode characters",
            metrics.unicode_symbols
        ));
    }

    (verdict, interpretations)
}

// =========================================================
// EVIDENCE (v0.4.0) - port of build_evidence from the Python reference
// =========================================================

fn excerpt_for(text: &[char], idx: usize, phrase: &[char]) -> String {
    let dot_sp: Vec<char> = ". ".chars().collect();
    let excl_sp: Vec<char> = "! ".chars().collect();
    let q_sp: Vec<char> = "? ".chars().collect();
    let nl: Vec<char> = "\n".chars().collect();

    let starts = [
        rfind_before(text, &dot_sp, idx),
        rfind_before(text, &excl_sp, idx),
        rfind_before(text, &q_sp, idx),
        rfind_before(text, &nl, idx),
    ];
    let sent_start = starts.iter().flatten().max().map(|&v| v + 1).unwrap_or(0);

    let ends = [
        find_from(text, &dot_sp, idx),
        find_from(text, &excl_sp, idx),
        find_from(text, &q_sp, idx),
        find_from(text, &nl, idx),
    ];
    let sent_end = ends.iter().flatten().min().copied().unwrap_or(text.len());

    let mut fragment: Vec<char> = text[sent_start.min(sent_end)..sent_end].to_vec();
    // strip() - trim whitespace from both ends
    let lead = fragment.iter().take_while(|c| c.is_whitespace()).count();
    let trail = fragment.iter().rev().take_while(|c| c.is_whitespace()).count();
    if lead + trail <= fragment.len() {
        fragment = fragment[lead..fragment.len() - trail].to_vec();
    }

    let f_lower: Vec<char> = fragment.iter().map(|&c| lower_char(c)).collect();
    let pos = find_from(&f_lower, phrase, 0);
    let phrase_len = phrase.len();

    match pos {
        None => truncate_middle_chars(&fragment, 110),
        Some(mut pos) => {
            if fragment.len() > 110 {
                let (w_left, w_right) = (45usize, 60usize);
                let start = pos.saturating_sub(w_left);
                let end = (pos + phrase_len + w_right).min(fragment.len());
                let prefix = if start > 0 { "... " } else { "" };
                let suffix = if end < fragment.len() { " ..." } else { "" };
                let middle: String = fragment[start..end].iter().collect();
                let full = format!("{}{}{}", prefix, middle, suffix);
                pos = pos - start + prefix.chars().count();
                let fc: Vec<char> = full.chars().collect();
                let mut out = String::new();
                out.extend(fc[..pos].iter());
                out.push_str(">>>");
                out.extend(fc[pos..pos + phrase_len].iter());
                out.push_str("<<<");
                out.extend(fc[pos + phrase_len..].iter());
                return out;
            }
            let mut out = String::new();
            out.extend(fragment[..pos].iter());
            out.push_str(">>>");
            out.extend(fragment[pos..pos + phrase_len].iter());
            out.push_str("<<<");
            out.extend(fragment[pos + phrase_len..].iter());
            out
        }
    }
}

fn build_evidence(text: &str, metrics: &AIMetrics) -> Vec<Evidence> {
    let mut evidence: Vec<Evidence> = Vec::new();
    let text_chars: Vec<char> = text.chars().collect();
    let text_lower: Vec<char> = lower_vec(text);
    let sentences = &metrics.sentences;

    let line_of = |idx: usize| -> usize {
        text_chars[..idx.min(text_chars.len())]
            .iter()
            .filter(|&&c| c == '\n')
            .count()
            + 1
    };

    // 1. Phrase hits with locations (high tier first)
    let mut occurrences = metrics.ai_phrase_occurrences.clone();
    occurrences.sort_by_key(|o| o.tier); // stable, preserves insertion order
    let labels = ["HIGH-risk", "typical", "weak"];
    let mut shown = 0usize;
    for occ in &occurrences {
        if shown >= 10 {
            break;
        }
        let phrase_chars: Vec<char> = occ.phrase.chars().collect();
        evidence.push(Evidence {
            detail: format!("{} AI phrase '{}'", labels[occ.tier], occ.phrase),
            line: Some(line_of(occ.idx)),
            excerpt: Some(excerpt_for(&text_chars, occ.idx, &phrase_chars)),
        });
        shown += 1;
    }

    // 1b. Repeated template headers (structured-answer genre)
    for (line, count, line_no) in metrics.template_header_occurrences.iter().take(4) {
        evidence.push(Evidence {
            detail: format!("repeated template header '{}' ×{}", line, count),
            line: Some(*line_no),
            excerpt: None,
        });
    }

    // 2. Sentence-length uniformity
    let sent_cv = metrics.burstiness;
    if sent_cv < 0.50 && metrics.word_count >= MIN_WORDS_FOR_CV {
        let lengths: Vec<usize> = sentences
            .iter()
            .filter(|s| !s.split_whitespace().collect::<Vec<_>>().is_empty())
            .map(|s| s.split_whitespace().count())
            .collect();
        let first: Vec<String> = lengths.iter().take(25).map(|l| l.to_string()).collect();
        evidence.push(Evidence {
            detail: format!(
                "sentence lengths are uniform: CV={:.2} (human prose is typically > 0.50); first lengths: {}",
                sent_cv,
                first.join(" ")
            ),
            line: None,
            excerpt: None,
        });
    }

    // 3. Paragraph-length uniformity
    if let Some(pcv) = metrics.paragraph_uniformity_cv {
        if pcv < 0.45 {
            let first: Vec<String> = metrics
                .paragraph_lengths
                .iter()
                .take(20)
                .map(|l| l.to_string())
                .collect();
            evidence.push(Evidence {
                detail: format!(
                    "paragraph lengths are uniform: CV={:.2} across {} paragraphs (human prose is typically > 0.50); lengths: {}",
                    pcv,
                    metrics.paragraph_lengths.len(),
                    first.join(" ")
                ),
                line: None,
                excerpt: None,
            });
        }
    }

    // 4. Connective overuse with example sentences
    if metrics.connective_density >= 0.10 {
        let mut ranked: Vec<(usize, &String)> = Vec::new();
        for sent in sentences {
            let lower_sent = sent.to_lowercase();
            let n = CONNECTIVES.iter().filter(|c| lower_sent.contains(*c)).count();
            if n >= 2 {
                ranked.push((n, sent));
            }
        }
        ranked.sort_by(|a, b| b.0.cmp(&a.0));
        for &(n, sent) in ranked.iter().take(2) {
            let sc: Vec<char> = sent.trim().chars().collect();
            evidence.push(Evidence {
                detail: format!("sentence carries {} discourse connectives", n),
                line: None,
                excerpt: Some(truncate_middle_chars(&sc, 130)),
            });
        }
    }

    // 5. Most suspicious sentences
    let mut sentence_scores: Vec<(usize, &String)> = Vec::new();
    for sent in sentences {
        let lower_sent = sent.to_lowercase();
        let mut markers = 0usize;
        let weights = [3usize, 2, 1];
        for (tier_idx, list) in tier_lists().iter().enumerate() {
            markers += weights[tier_idx] * list.iter().filter(|p| lower_sent.contains(*p)).count();
        }
        markers += CONNECTIVES.iter().filter(|c| lower_sent.contains(*c)).count();
        sentence_scores.push((markers, sent));
    }
    sentence_scores.sort_by(|a, b| b.0.cmp(&a.0));
    for &(markers, sent) in sentence_scores.iter().take(3) {
        if markers >= 2 {
            let probe: Vec<char> = sent.chars().take(40).map(lower_char).collect();
            let idx = find_from(&text_lower, &probe, 0);
            let sc: Vec<char> = sent.trim().chars().collect();
            evidence.push(Evidence {
                detail: format!("sentence with {} AI markers", markers),
                line: idx.map(line_of),
                excerpt: Some(truncate_middle_chars(&sc, 130)),
            });
        }
    }

    evidence
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
    ai_evidence: &Option<Vec<Evidence>>,
    remove_watermark: bool,
    lang: &str,
) -> String {
    let mut lines = Vec::new();

    // Header
    lines.push("=".repeat(70));
    lines.push("aiparstxt-ext — Enhanced AI Forensic Analyzer Report".to_string());
    lines.push(format!("Language: {}", lang));
    lines.push("=".repeat(70));
    lines.push(String::new());

    // Basic info
    lines.push(format!("Input file:  {}", input_file));
    lines.push(format!("Output file: {}", output_file));
    lines.push(format!(
        "Mode: replace with '?'{}",
        if remove_watermark { " + watermark removal" } else { "" }
    ));
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
    if let (Some(metrics), Some(ai_result), evidence) = (ai_metrics, ai_result, ai_evidence) {
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
        lines.push(format!("  Sentence length CV:    {:.3}", metrics.burstiness));
        match metrics.paragraph_uniformity_cv {
            Some(pcv) => lines.push(format!("  Paragraph length CV:   {:.3}", pcv)),
            None => lines.push("  Paragraph length CV:   n/a (<4 paragraphs)".to_string()),
        }
        lines.push(format!("  Lexical diversity:     {:.3}", metrics.lexical_diversity));
        lines.push(format!("  Repetition score:      {:.3}", metrics.repetition_score));
        lines.push(format!("  Entropy:               {:.3}", metrics.entropy));
        lines.push(format!("  Connective density:    {:.3}", metrics.connective_density));
        lines.push(format!(
            "  Template headers:      {} repeats ({} distinct)",
            metrics.template_header_total, metrics.template_header_distinct
        ));
        lines.push(format!("  Pattern repetition:    {:.3}", metrics.pattern_repetition));
        lines.push(format!("  Punctuation density:   {:.3}", metrics.punctuation_density));
        lines.push(format!(
            "  AI phrases (tiers):    high={}, medium={}, weak={}",
            metrics.ai_phrase_tiers[0], metrics.ai_phrase_tiers[1], metrics.ai_phrase_tiers[2]
        ));
        lines.push(format!("  AI phrase hits:        {}", metrics.ai_phrase_hits));
        lines.push(format!("  Unicode suspicious:    {}", metrics.unicode_symbols));
        lines.push(format!("  Avg word length:       {:.2}", metrics.avg_word_length));
        lines.push(format!("  Word length variance:  {:.2}", metrics.word_length_variance));
        lines.push(String::new());

        if let Some(ev) = evidence {
            if !ev.is_empty() {
                lines.push("AI EVIDENCE (locations in the text):".to_string());
                for (i, e) in ev.iter().take(15).enumerate() {
                    let loc = match e.line {
                        Some(l) => format!("line {}", l),
                        None => "text-wide".to_string(),
                    };
                    lines.push(format!("  [{}] {}: {}", i + 1, loc, e.detail));
                    if let Some(ex) = &e.excerpt {
                        lines.push(format!("      \"{}\"", ex));
                    }
                }
                lines.push(String::new());
            }
        }

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
        eprintln!("  --no-report               Do not write report file");
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
                println!("  --no-report               Do not write report file");
                println!("  --no-words                Exclude word frequency from report");
                println!("  --remove-watermark        Remove AI watermark characters");
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

    // Calculate word frequency (on sanitized text, for the report)
    let word_freq = if no_words { HashMap::new() } else { word_frequency(&process_result.cleaned) };

    // AI forensic analysis runs on the ORIGINAL text: sanitization
    // replaces disallowed characters with '?', which would corrupt
    // sentence splitting and phrase positions.
    let ai_metrics = if !process_result.cleaned.is_empty() {
        calculate_ai_forensic_metrics(&text)
    } else {
        None
    };
    let ai_result = ai_metrics.as_ref().map(calculate_ai_probability);
    let ai_evidence = match (&ai_metrics, &ai_result) {
        (Some(m), Some(_)) => Some(build_evidence(&text, m)),
        _ => None,
    };

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
            &ai_evidence,
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
    if let Some(result) = &ai_result {
        println!("AI Probability: {:.1}% (confidence: {})", result.probability, result.confidence);
        if let Some(evidence) = &ai_evidence {
            if !evidence.is_empty() {
                println!("AI Evidence (top {} of {}):", evidence.len().min(3), evidence.len());
                for ev in evidence.iter().take(3) {
                    let loc = match ev.line {
                        Some(l) => format!("line {}", l),
                        None => "text-wide".to_string(),
                    };
                    println!("  {}: {}", loc, ev.detail);
                }
            }
        }
    }
    println!("Output: {}", if no_edit { "(skipped)" } else { &output_file });
    println!("Report: {}", if no_report { "(skipped)" } else { &report_file });
}
