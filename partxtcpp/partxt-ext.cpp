#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <iomanip>
#include <sstream>
#include <codecvt>
#include <locale>

// =========================================================
// ENHANCED ALLOWED CHARACTERS
// =========================================================

const std::string ALLOWED_CHARS =
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    "[]{}()-=_+!@#$%&*;'/.,<>\"`~ \t\n\r";

const std::u32string CANONICAL_ALLOWED = U"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    U"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    U"ҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ[]{}():()-=_+!@#$%&*;'/.,<>'\"`~—«» \t\n\r";

bool isAllowed(char32_t ch) {
    return CANONICAL_ALLOWED.find(ch) != std::u32string::npos;
}

// =========================================================
// ENHANCED AI WATERMARK CHARACTERS
// =========================================================

bool isWatermark(char32_t ch) {
    uint32_t cp = static_cast<uint32_t>(ch);

    // Core zero-width characters
    switch (cp) {
        case 0x200B: // Zero Width Space (ZWSP)
        case 0x200C: // Zero Width Non-Joiner (ZWNJ)
        case 0x200D: // Zero Width Joiner (ZWJ)
        case 0xFEFF: // Zero Width No-Break Space (ZWNBSP, BOM)
        case 0x00AD: // Soft Hyphen (SHY)
        case 0x2060: // Word Joiner
        case 0x2061: // Function Application
        case 0x2062: // Invisible Times
        case 0x2063: // Invisible Separator
        case 0x2064: // Invisible Plus
        case 0x202A: // Left-to-Right Embedding
        case 0x202B: // Right-to-Left Embedding
        case 0x202C: // Pop Directional Formatting
        case 0x202D: // Left-to-Right Override
        case 0x202E: // Right-to-Left Override
        case 0x2028: // Line Separator
        case 0x2029: // Paragraph Separator
        case 0xE0001: // Language Tag
        case 0x180E: // Mongolian Separator
            return true;
    }

    // Variation Selectors
    if (cp >= 0xFE00 && cp <= 0xFE0F) {
        return true;
    }

    // Tag characters
    if (cp >= 0xE0020 && cp <= 0xE007F) {
        return true;
    }

    // Private Use Area
    if (cp >= 0xE000 && cp <= 0xE07F) {
        return true;
    }

    // Additional suspicious characters
    switch (cp) {
        case 0xFFF9: case 0xFFFA: case 0xFFFB: case 0xFFFC: case 0xFFFD: // Interlinear annotation
        case 0x2010: case 0x2011: // Hyphen variants
        case 0x2012: case 0x2013: case 0x2014: // Em-dash variants
        case 0x2018: case 0x2019: case 0x201B: // Smart quotes
        case 0x201C: case 0x201D: case 0x201E: case 0x201F: // Smart double quotes
        case 0x2026: // Ellipsis
        case 0x202F: // Narrow no-break space
        case 0x205F: // Medium mathematical space
        case 0x00A0: // Non-breaking space
            return true;
    }

    // Space variants
    if (cp >= 0x2000 && cp <= 0x200A) {
        return true;
    }

    return false;
}

// =========================================================
// TEXT PROCESSING STRUCTS
// =========================================================

struct ProcessResult {
    std::u32string cleaned;
    std::map<char32_t, size_t> replaced;
    std::map<char32_t, size_t> watermarkRemoved;
};

ProcessResult process(const std::u32string& text, bool removeWatermark) {
    ProcessResult result;
    result.cleaned.reserve(text.size());

    for (char32_t ch : text) {
        if (removeWatermark && isWatermark(ch)) {
            result.watermarkRemoved[ch]++;
            continue;
        }

        if (isAllowed(ch)) {
            result.cleaned.push_back(ch);
        } else {
            result.cleaned.push_back('?');
            result.replaced[ch]++;
        }
    }

    return result;
}

// =========================================================
// UTF-32 HELPERS (Unicode-aware lowercase / predicates)
// =========================================================

static std::u32string u32from8(const char* s) {
    static std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.from_bytes(s);
}

static std::string u8from32(const std::u32string& s) {
    static std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.to_bytes(s);
}

// Unicode-aware lowercase covering the script ranges this tool handles
// (Latin-1/Latin Extended, Greek, Cyrillic incl. Ё Є І Ї Ґ).
// ASCII tolower() is NOT enough for RU/UK texts.
static char32_t toLowerW(char32_t ch) {
    if (ch >= U'A' && ch <= U'Z') return ch + 32;
    if (ch >= 0x00C0 && ch <= 0x00DE && ch != 0x00D7) return ch + 0x20; // À-Þ (× excluded)
    if (ch >= 0x0100 && ch <= 0x0137 && ((ch - 0x0100) % 2 == 0)) return ch + 1; // Latin ext-A
    if (ch >= 0x0139 && ch <= 0x0148 && ((ch - 0x0139) % 2 == 0)) return ch + 1;
    if (ch >= 0x014A && ch <= 0x017E && ((ch - 0x014A) % 2 == 0)) return ch + 1;
    if (ch >= 0x0400 && ch <= 0x040F) return ch + 0x50;                 // Ѐ-Џ (Ё Є І Ї)
    if (ch >= 0x0410 && ch <= 0x042F) return ch + 0x20;                 // А-Я
    if (ch >= 0x0460 && ch <= 0x052F && ((ch - 0x0460) % 2 == 0)) return ch + 1; // Ґ etc.
    return ch;
}

static std::u32string lower32(const std::u32string& s) {
    std::u32string out(s);
    for (auto& ch : out) ch = toLowerW(ch);
    return out;
}

static bool isSpace32(char32_t ch) {
    switch (ch) {
        case U' ': case U'\t': case U'\n': case U'\r': case 0x000B: case 0x000C:
        case 0x0085: case 0x00A0: case 0x1680:
        case 0x2000: case 0x2001: case 0x2002: case 0x2003: case 0x2004:
        case 0x2005: case 0x2006: case 0x2007: case 0x2008: case 0x2009:
        case 0x200A: case 0x2028: case 0x2029: case 0x202F: case 0x205F:
        case 0x3000:
            return true;
        default:
            return false;
    }
}

// Equivalent of Python \w (Unicode letters, digits, underscore) approximated
// by script block ranges; covers Latin, Greek, Cyrillic, Hebrew, Arabic,
// Thai, CJK, kana, Hangul, numerals (superscripts, fractions) etc.
static bool isWordChar(char32_t ch) {
    uint32_t c = static_cast<uint32_t>(ch);
    if ((c >= U'a' && c <= U'z') || (c >= U'A' && c <= U'Z') ||
        (c >= U'0' && c <= U'9') || c == U'_') return true;
    switch (c) {
        case 0x00AA: case 0x00B5: case 0x00BA:           // ª µ º (letters)
        case 0x00B2: case 0x00B3: case 0x00B9:           // superscript digits
            return true;
        default:
            break;
    }
    if (c >= 0x00BC && c <= 0x00BE) return true;          // vulgar fractions
    if (c >= 0x00C0 && c <= 0x00FF && c != 0x00D7 && c != 0x00F7) return true;
    // combining marks (Mn) are not \w in Python
    if (c >= 0x0591 && c <= 0x05C7) return false;          // Hebrew points
    if ((c >= 0x064B && c <= 0x065F) || c == 0x0670 ||
        (c >= 0x06D6 && c <= 0x06DC) || (c >= 0x06DF && c <= 0x06E4) ||
        (c >= 0x06E7 && c <= 0x06E8) || (c >= 0x06EA && c <= 0x06ED)) return false; // Arabic marks
    if ((c >= 0x093A && c <= 0x094D) || (c >= 0x0951 && c <= 0x0957) ||
        (c >= 0x0962 && c <= 0x0963)) return false;        // Devanagari matras
    if (c == 0x0E31 || (c >= 0x0E34 && c <= 0x0E3A) ||
        (c >= 0x0E47 && c <= 0x0E4E)) return false;        // Thai marks
    if (c == 0x0EB1 || (c >= 0x0EB4 && c <= 0x0EBC) ||
        (c >= 0x0EC8 && c <= 0x0ECD)) return false;        // Lao marks
    if (c >= 0x0100 && c <= 0x02C1) return true;          // Latin ext / IPA / modifiers
    if (c >= 0x0370 && c <= 0x0481) return true;          // Greek + Cyrillic
    if (c >= 0x048A && c <= 0x052F) return true;          // Cyrillic ext
    if (c >= 0x0531 && c <= 0x058F) return true;          // Armenian
    if (c >= 0x05D0 && c <= 0x05F4) return true;          // Hebrew letters
    if (c >= 0x0600 && c <= 0x06FF) return true;          // Arabic
    if (c >= 0x0700 && c <= 0x074F) return true;          // Syriac
    if (c >= 0x0780 && c <= 0x07B1) return true;          // Thaana
    if (c >= 0x0900 && c <= 0x097F) return true;          // Devanagari
    if (c >= 0x0980 && c <= 0x0DFF) return true;          // other Indic scripts
    if (c >= 0x0E00 && c <= 0x0E7F) return true;          // Thai
    if (c >= 0x0E80 && c <= 0x0EFF) return true;          // Lao
    if (c >= 0x0F00 && c <= 0x0FFF) return true;          // Tibetan
    if (c >= 0x1000 && c <= 0x109F) return true;          // Myanmar
    if (c >= 0x10A0 && c <= 0x10FF) return true;          // Georgian
    if (c >= 0x1100 && c <= 0x11FF) return true;          // Hangul Jamo
    if (c >= 0x1E00 && c <= 0x1FFF) return true;          // Latin ext additional, Greek ext
    if (c >= 0x3041 && c <= 0x30FF) return true;          // Hiragana / Katakana
    if (c >= 0x3100 && c <= 0x318F) return true;          // Bopomofo / Hangul compat
    if (c >= 0x3400 && c <= 0x4DBF) return true;          // CJK ext A
    if (c >= 0x4E00 && c <= 0x9FFF) return true;          // CJK
    if (c >= 0xA000 && c <= 0xA4CF) return true;          // Yi
    if (c >= 0xAC00 && c <= 0xD7A3) return true;          // Hangul syllables
    if (c >= 0xF900 && c <= 0xFAFF) return true;          // CJK compat
    if (c >= 0xFB00 && c <= 0xFB17) return true;          // Latin ligatures
    if (c >= 0xFB1D && c <= 0xFDFF) return true;          // Hebrew/Arabic presentation
    if (c >= 0xFE70 && c <= 0xFEFC) return true;          // Arabic presentation B
    if (c >= 0xFF10 && c <= 0xFF19) return true;          // fullwidth digits
    if (c >= 0xFF21 && c <= 0xFF3A) return true;          // fullwidth upper
    if (c >= 0xFF41 && c <= 0xFF5A) return true;          // fullwidth lower
    if (c >= 0xFF66 && c <= 0xFFDC) return true;          // halfwidth kana/hangul
    if (c >= 0x20000 && c <= 0x2FA1F) return true;        // CJK ext B+
    return false;
}

// Equivalent of Python str.isalpha() for the ranges we care about.
static bool isAlpha32(char32_t ch) {
    if ((ch >= U'a' && ch <= U'z') || (ch >= U'A' && ch <= U'Z')) return true;
    if (ch >= 0x00C0 && ch <= 0x024F && ch != 0x00D7 && ch != 0x00F7) return true;
    if (ch >= 0x0370 && ch <= 0x052F) return true;
    return false;
}

// Equivalent of Python str.isdigit() for the digit ranges we care about
// (ASCII, superscripts, Arabic-Indic, Devanagari, fullwidth).
static bool isDigit32(char32_t ch) {
    uint32_t c = static_cast<uint32_t>(ch);
    if (c >= U'0' && c <= U'9') return true;
    switch (c) {
        case 0x00B2: case 0x00B3: case 0x00B9:  // superscript digits
            return true;
        default:
            break;
    }
    if (c >= 0x0660 && c <= 0x0669) return true;  // Arabic-Indic
    if (c >= 0x06F0 && c <= 0x06F9) return true;  // Eastern Arabic-Indic
    if (c >= 0x0966 && c <= 0x096F) return true;  // Devanagari
    if (c >= 0xFF10 && c <= 0xFF19) return true;  // fullwidth
    return false;
}

static std::u32string trim32(const std::u32string& s) {
    size_t b = 0, e = s.size();
    while (b < e && isSpace32(s[b])) b++;
    while (e > b && isSpace32(s[e - 1])) e--;
    return s.substr(b, e - b);
}

static bool endsWith32(const std::u32string& w, const std::u32string& suf) {
    return w.size() >= suf.size() && w.compare(w.size() - suf.size(), suf.size(), suf) == 0;
}

// Python str.count(): non-overlapping occurrences
static size_t countNonOverlap(const std::u32string& hay, const std::u32string& needle) {
    if (needle.empty()) return 0;
    size_t cnt = 0, pos = 0;
    while ((pos = hay.find(needle, pos)) != std::u32string::npos) {
        cnt++;
        pos += needle.size();
    }
    return cnt;
}

// Python text.rfind(sub, 0, limit): last position fully inside [0, limit)
static size_t rfindBefore(const std::u32string& hay, const std::u32string& nd, size_t limit) {
    if (limit > hay.size()) limit = hay.size();
    if (nd.empty() || limit < nd.size()) return std::u32string::npos;
    for (size_t start = limit - nd.size() + 1; start-- > 0;) {
        if (hay.compare(start, nd.size(), nd) == 0) return start;
    }
    return std::u32string::npos;
}

// Python len(text.split()): whitespace-separated word count
static size_t whitespaceWordCount(const std::u32string& s) {
    size_t cnt = 0;
    bool inWord = false;
    for (char32_t ch : s) {
        if (!isSpace32(ch)) {
            if (!inWord) { cnt++; inWord = true; }
        } else {
            inWord = false;
        }
    }
    return cnt;
}

// =========================================================
// AI FORENSIC DATABASES (v0.4.0)
// Canonical source: parscgpt-ext.py / AI_SIGNALS_SPEC.md
// =========================================================

// Suspicious Unicode characters - aligned with the parscgpt-ext.py reference
static const std::vector<char32_t> UNICODE_SUSPICIOUS = {
    0x2014, 0x2013, 0x201C, 0x201D, 0x2018, 0x2019,
    0x2026, 0x2022, 0x2192, 0x2190, 0x2191, 0x2193,
    0x00A9, 0x00AE, 0x2122, 0x00B0, 0x00B1, 0x00D7, 0x00F7,
};

static std::vector<std::u32string> mkList(std::initializer_list<const char*> items) {
    std::vector<std::u32string> out;
    out.reserve(items.size());
    for (const char* s : items) out.push_back(u32from8(s));
    return out;
}

// AI-typical phrases: tiered multilingual database (v0.4.0).
// HIGH   - distinctive LLM template phrases, zero hits in human validation corpus
// MEDIUM - typical AI connective/register markers, rare in human corpus
// WEAK   - markers that also occur in human prose; evidence-only, tiny weight
static const std::vector<std::u32string> AI_PHRASES_HIGH = mkList({
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
});

static const std::vector<std::u32string> AI_PHRASES_MEDIUM = mkList({
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
});

static const std::vector<std::u32string> AI_PHRASES_WEAK = mkList({
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
});

static const std::vector<std::u32string> AI_PHRASES_BY_TIER[3] = {
    AI_PHRASES_HIGH, AI_PHRASES_MEDIUM, AI_PHRASES_WEAK,
};

// Discourse connectives (all languages merged); used for connective_density.
static const std::vector<std::u32string> CONNECTIVES = mkList({
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
});

// Passive voice patterns (reference basis for passive_voice_density)
static const std::vector<std::u32string> AI_PASSIVE_PATTERNS = mkList({
    "is considered to be", "are considered to be",
    "is often said to be", "are often said to be",
    "is generally regarded as", "are generally regarded as",
    "is typically characterized by", "are typically characterized by",
    "is commonly associated with", "are commonly associated with",
    "is widely recognized as", "are widely recognized as",
    "is frequently observed to", "are frequently observed to",
    "is usually understood to", "are usually understood to",
});

static const std::set<std::u32string> mkSet(std::initializer_list<const char*> items) {
    std::set<std::u32string> out;
    for (const char* s : items) out.insert(u32from8(s));
    return out;
}

static const std::set<std::u32string> STOPWORDS = mkSet({
    // English stopwords
    "the", "a", "an", "and", "or", "but", "if", "then",
    "else", "when", "at", "from", "by", "on", "off", "for",
    "in", "out", "over", "to", "into", "with", "about", "against",
    "between", "through", "during", "before", "after", "above",
    "below", "up", "down", "of", "again",
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
    "себя", "чтобы", "от", "так", "для", "тем", "под",
    "когда", "же", "ну", "пока", "еще", "были", "который",
    "своей", "или", "тебя", "через", "ни",
    "ему", "будет", "них", "там", "ее", "им", "про",
    "этом", "этому", "куда", "этого", "раз",
    "можно", "два", "где", "ли", "без", "чем", "эти", "нас",
    "за", "своих", "какой", "сам", "всех",
    "любой", "один", "между", "была", "вас", "чей",
    "которой", "сейчас", "также", "свои",
    "ей", "которого", "либо", "ваш", "нужно",
    "каждый", "том", "потому",
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
});

// Scoring weights (v0.4.0) - canonical values, see AI_SIGNALS_SPEC.md
struct CVTier { double threshold; int points; };
static const std::vector<CVTier> SENT_CV_TIERS = {
    {0.30, 32}, {0.35, 26}, {0.40, 19}, {0.45, 11}, {0.50, 5},
};
static const std::vector<CVTier> PARA_CV_TIERS = {
    {0.15, 28}, {0.25, 22}, {0.35, 16}, {0.45, 7},
};
static const std::vector<CVTier> JOINT_CV_TIERS = {
    {0.40, 14}, {0.45, 10},
};
static const int HIGH_PHRASE_SCORES[2] = {24, 15};   // (>=2 hits, ==1 hit)
static const int MEDIUM_PHRASE_SCORES[2] = {10, 5};  // (>=3 hits, >=1 hit)
static const int WEAK_PHRASE_SCORE = 4;              // >=4 hits
static const std::vector<CVTier> CONNECTIVE_TIERS = {
    {0.12, 13}, {0.08, 7},
};
// Template header repetition (structured-answer genre):
// (>=2 distinct templates or >=10 repeats, >=3 repeats)
static const size_t TEMPLATE_HEADER_MIN_REPEATS = 3;
static const int TEMPLATE_HEADER_SCORES[2] = {14, 8};
// Structural-signal reliability: tier points are scaled by sample reliability
// (short texts get partial credit instead of a silent zero).
static const size_t SENT_CV_MIN_SENTENCES = 5;    // below this, sentence CV is pure noise -> 0
static const size_t SENT_CV_FULL_SENTENCES = 15;  // full weight from this many sentences on
static const size_t PARA_CV_MIN_PARAGRAPHS = 3;   // below this, paragraph CV is not computed
static const size_t PARA_CV_FULL_PARAGRAPHS = 4;
static const size_t MIN_WORDS_FOR_CV = 40;
static const size_t FULL_WORDS_FOR_CV = 150;

static const std::set<std::u32string> PRONOUNS = mkSet({
    "i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those",
    "anyone", "anything", "everyone", "everything", "someone", "something",
    "noone", "nothing", "each", "every", "either", "neither", "both", "few",
    "many", "several",
});

static const std::vector<std::u32string> QUANTIFIERS = mkList({
    "relatively", "somewhat", "quite", "rather", "fairly",
    "reasonably", "comparatively", "moderately", "substantially",
    "considerably", "significantly", "notably", "remarkably",
});

static const std::vector<std::u32string> ADJ_INDICATORS = mkList({
    "al", "ble", "cal", "ful", "ic", "ive", "less", "ous",
});
static const std::vector<std::u32string> NOUN_INDICATORS = mkList({
    "er", "ism", "ment", "ness", "tion", "ship", "cy", "dom",
});

// =========================================================
// FORENSIC ANALYSIS STRUCTS
// =========================================================

struct PhraseOccurrence {
    int tier;               // 0=high, 1=medium, 2=weak
    std::u32string phrase;
    size_t idx;
};

struct AIMetrics {
    size_t wordCount;
    size_t sentenceCount;
    double lexicalDiversity;
    double repetitionScore;
    double entropy;
    double burstiness;             // sentence length CV
    double paragraphUniformityCv;  // < 0 when not computable (<3 paragraphs)
    size_t paragraphCount;         // 0 when paragraph CV not computable
    std::vector<size_t> paragraphLengths;
    double patternRepetition;
    double punctuationDensity;
    size_t aiPhraseHits;
    size_t phraseTiers[3];         // high / medium / weak occurrence counts
    std::vector<PhraseOccurrence> phraseOccurrences;
    struct TemplateOccurrence {
        std::u32string line;
        size_t count;
        size_t firstLineNo;
    };
    std::vector<TemplateOccurrence> templateOccurrences;
    double connectiveDensity;
    // Template header repetition (structured-answer genre)
    size_t templateTotal;      // sum of counts of lines repeated >= 3 times
    size_t templateDistinct;   // number of such lines
    std::vector<std::u32string> sentences;
    size_t unicodeSymbols;
    double avgWordLength;
    double wordLengthVariance;
    double pronounRatio;
    double readabilityScore;
    double passiveVoiceDensity;
    double adjNounPairDiversity;
    double structuralUniformity;
    double quantifierOveruse;
    // Promotional/social-media register (genre abstention, NOT an AI score:
    // both AI hype posts and human SMM copy trigger this)
    bool promotionalRegister = false;
};

struct AIResult {
    double probability;
    std::string confidence;
    std::map<std::string, size_t> scores;
};

struct EvidenceItem {
    std::string type;
    std::string detail;
    bool hasLine = false;
    size_t line = 0;
    bool hasExcerpt = false;
    std::string excerpt;
};

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

std::map<std::string, size_t> wordFrequency(const std::u32string& text) {
    std::map<std::string, size_t> freq;
    std::u32string textLower = lower32(text);
    std::u32string currentWord;

    for (char32_t ch : textLower) {
        if (isAlpha32(ch) || ch == U'\'') {
            currentWord.push_back(ch);
        } else {
            if (!currentWord.empty()) {
                if (currentWord.size() > 2 && STOPWORDS.find(currentWord) == STOPWORDS.end()) {
                    freq[u8from32(currentWord)]++;
                }
                currentWord.clear();
            }
        }
    }
    if (!currentWord.empty()) {
        if (currentWord.size() > 2 && STOPWORDS.find(currentWord) == STOPWORDS.end()) {
            freq[u8from32(currentWord)]++;
        }
    }
    return freq;
}

// Equivalent of re.findall(r'\b\w+\b', text.lower())
static std::vector<std::u32string> tokenizeWords(const std::u32string& textLower) {
    std::vector<std::u32string> words;
    std::u32string cur;
    for (char32_t ch : textLower) {
        if (isWordChar(ch)) {
            cur.push_back(ch);
        } else {
            if (!cur.empty()) { words.push_back(cur); cur.clear(); }
        }
    }
    if (!cur.empty()) words.push_back(cur);
    return words;
}

// Split on blank lines: equivalent of re.split(r'\n\s*\n', text)
static std::vector<std::u32string> splitParagraphs(const std::u32string& text) {
    std::vector<std::u32string> out;
    size_t segStart = 0;
    size_t i = 0;
    while (i < text.size()) {
        if (text[i] == U'\n') {
            size_t j = i + 1;
            while (j < text.size() && isSpace32(text[j])) j++;
            // whitespace run [i, j): match \n\s*\n if another '\n' exists after i
            size_t last = std::u32string::npos;
            for (size_t k = j; k-- > i + 1;) {
                if (text[k] == U'\n') { last = k; break; }
            }
            if (last != std::u32string::npos) {
                out.push_back(text.substr(segStart, i - segStart));
                i = segStart = last + 1;
                continue;
            }
        }
        i++;
    }
    out.push_back(text.substr(segStart));
    return out;
}

// Sentence splitter aligned with the Python reference:
// mask (Mr|Mrs|Ms|Dr|Prof|Sr|Jr). as <DOT>, split on [.!?]+,
// keep non-empty sentences longer than 3 characters.
std::vector<std::u32string> splitSentences(const std::u32string& text) {
    static const std::vector<std::u32string> abbrevs = mkList({
        "Mrs", "Mr", "Ms", "Prof", "Dr", "Sr", "Jr",
    });
    static const std::u32string dotMask = U"<DOT>";

    std::u32string masked;
    masked.reserve(text.size());
    for (size_t i = 0; i < text.size();) {
        bool matched = false;
        bool wordBoundary = (i == 0) || !isWordChar(text[i - 1]);
        if (wordBoundary) {
            for (const auto& abbr : abbrevs) {
                if (i + abbr.size() < text.size() &&
                    text.compare(i, abbr.size(), abbr) == 0 &&
                    text[i + abbr.size()] == U'.') {
                    masked += abbr;
                    masked += dotMask;
                    i += abbr.size() + 1;
                    matched = true;
                    break;
                }
            }
        }
        if (!matched) {
            masked.push_back(text[i]);
            i++;
        }
    }

    std::vector<std::u32string> sentences;
    auto closeSentence = [&](std::u32string seg) {
        std::u32string s = trim32(seg);
        // restore masked abbreviation dots
        size_t pos;
        while ((pos = s.find(dotMask)) != std::u32string::npos) {
            s.replace(pos, dotMask.size(), U".");
        }
        if (!trim32(s).empty() && s.size() > 3) {
            sentences.push_back(s);
        }
    };

    std::u32string cur;
    for (char32_t ch : masked) {
        if (ch == U'.' || ch == U'!' || ch == U'?') {
            closeSentence(cur);
            cur.clear();
        } else {
            cur.push_back(ch);
        }
    }
    closeSentence(cur);
    return sentences;
}

AIMetrics* calculateAIForensicMetrics(const std::u32string& text) {
    if (text.empty()) {
        return nullptr;
    }

    std::u32string textLower = lower32(text);
    std::vector<std::u32string> words = tokenizeWords(textLower);
    std::vector<std::u32string> sentences = splitSentences(text);

    if (words.empty() || sentences.empty()) {
        return nullptr;
    }

    // Filtered words (reference basis for diversity/entropy/repetition)
    std::map<std::u32string, size_t> filteredCounter;
    size_t filteredTotal = 0;
    for (const auto& w : words) {
        if (w.size() > 2 && STOPWORDS.find(w) == STOPWORDS.end()) {
            filteredCounter[w]++;
            filteredTotal++;
        }
    }

    AIMetrics* m = new AIMetrics();
    m->wordCount = words.size();
    m->sentenceCount = sentences.size();

    // Lexical diversity (on filtered words, as in reference)
    m->lexicalDiversity = filteredTotal > 0
        ? static_cast<double>(filteredCounter.size()) / static_cast<double>(filteredTotal)
        : 0.0;

    // Repetition score (distinct repeated filtered words / filtered words)
    size_t repeatedWords = 0;
    for (const auto& kv : filteredCounter) {
        if (kv.second > 1) repeatedWords++;
    }
    m->repetitionScore = filteredTotal > 0
        ? static_cast<double>(repeatedWords) / static_cast<double>(filteredTotal)
        : 0.0;

    // Entropy (on filtered words, as in reference)
    m->entropy = 0.0;
    if (filteredTotal > 0) {
        for (const auto& kv : filteredCounter) {
            double p = static_cast<double>(kv.second) / static_cast<double>(filteredTotal);
            m->entropy -= p * std::log2(p);
        }
    }

    // Sentence length analysis (burstiness = CV of sentence word counts);
    // word count per sentence uses whitespace split, as in the reference
    std::vector<size_t> sentLengths;
    for (const auto& s : sentences) sentLengths.push_back(whitespaceWordCount(s));
    double avgSentLen = 0.0;
    for (size_t len : sentLengths) avgSentLen += static_cast<double>(len);
    avgSentLen /= static_cast<double>(sentLengths.size());
    double variance = 0.0;
    for (size_t len : sentLengths) {
        double diff = static_cast<double>(len) - avgSentLen;
        variance += diff * diff;
    }
    variance /= static_cast<double>(sentLengths.size());
    m->burstiness = (avgSentLen > 0.0 && sentLengths.size() > 1)
        ? std::sqrt(variance) / avgSentLen : 0.0;

    // Paragraph length uniformity (CV of paragraph word counts)
    m->paragraphUniformityCv = -1.0;  // not computable by default
    m->paragraphCount = 0;
    std::vector<size_t> paraLengths;
    for (const auto& p : splitParagraphs(text)) {
        size_t wc = whitespaceWordCount(p);
        if (wc > 15) paraLengths.push_back(wc);
    }
    if (paraLengths.size() >= PARA_CV_MIN_PARAGRAPHS) {
        double paraAvg = 0.0;
        for (size_t len : paraLengths) paraAvg += static_cast<double>(len);
        paraAvg /= static_cast<double>(paraLengths.size());
        double paraVar = 0.0;
        for (size_t len : paraLengths) {
            double diff = static_cast<double>(len) - paraAvg;
            paraVar += diff * diff;
        }
        paraVar /= static_cast<double>(paraLengths.size());
        m->paragraphUniformityCv = paraAvg > 0.0 ? std::sqrt(paraVar) / paraAvg : 0.0;
        m->paragraphCount = paraLengths.size();
    }
    m->paragraphLengths = std::move(paraLengths);

    // Pattern repetition (<=10 'S', <=20 'M', else 'L')
    auto categorizeLength = [](size_t length) -> char {
        if (length <= 10) return 'S';
        if (length <= 20) return 'M';
        return 'L';
    };
    std::map<char, size_t> patternCounts;
    for (size_t len : sentLengths) patternCounts[categorizeLength(len)]++;
    size_t repeatedPatterns = 0;
    for (const auto& kv : patternCounts) {
        if (kv.second > 1) repeatedPatterns++;
    }
    m->patternRepetition = sentLengths.empty() ? 0.0
        : static_cast<double>(repeatedPatterns) / static_cast<double>(sentLengths.size());

    // Punctuation density (reference regex [,;:()\-—–] / len(text))
    size_t punctCount = 0;
    for (char32_t ch : text) {
        switch (ch) {
            case U',': case U';': case U':': case U'(': case U')': case U'-':
            case 0x2014: case 0x2013:
                punctCount++;
                break;
            default:
                break;
        }
    }
    m->punctuationDensity = static_cast<double>(punctCount) / static_cast<double>(text.size());

    // AI phrase detection (tiered, with occurrences for evidence)
    m->aiPhraseHits = 0;
    m->phraseTiers[0] = m->phraseTiers[1] = m->phraseTiers[2] = 0;
    for (int tier = 0; tier < 3; ++tier) {
        for (const auto& phrase : AI_PHRASES_BY_TIER[tier]) {
            size_t found = countNonOverlap(textLower, phrase);
            if (found > 0) {
                m->aiPhraseHits++;
                m->phraseTiers[tier] += found;
                size_t idx = textLower.find(phrase);
                for (size_t k = 0; k < found && k < 3; ++k) {
                    m->phraseOccurrences.push_back({tier, phrase, idx});
                    idx = textLower.find(phrase, idx + phrase.size());
                }
            }
        }
    }

    // Connective density (connectives per sentence)
    size_t connTotal = 0;
    for (const auto& s : sentences) {
        std::u32string sLower = lower32(s);
        for (const auto& c : CONNECTIVES) {
            if (sLower.find(c) != std::u32string::npos) connTotal++;
        }
    }
    m->connectiveDensity = sentences.empty() ? 0.0
        : static_cast<double>(connTotal) / static_cast<double>(sentences.size());

    // Promotional/social-media register (genre abstention, NOT an AI score)
    size_t promoEmoji = 0;
    size_t promoExclCount = 0;
    for (char32_t ch : text) {
        if (ch >= 0x2600) promoEmoji++;
        if (ch == U'!') promoExclCount++;
    }
    double promoExcl = m->wordCount > 0
        ? static_cast<double>(promoExclCount) / static_cast<double>(m->wordCount) : 0.0;
    m->promotionalRegister = promoEmoji >= 5 && promoExcl >= 0.02;

    // Template header repetition (structured-answer genre)
    // Lines qualify if: trimmed length 4..=60 chars, 1..=8 whitespace-separated
    // words, no sentence-final punctuation, first char not a digit. Count
    // verbatim repeats; insertion order is kept so ties sort first-seen,
    // matching Python's ordered Counter.
    m->templateTotal = 0;
    m->templateDistinct = 0;
    m->templateOccurrences.clear();
    {
        std::map<std::u32string, size_t> index;  // line -> position in counts
        std::vector<std::pair<std::u32string, size_t>> counts;  // first-seen order
        std::vector<size_t> firstLineNo;
        size_t lineNo = 0;
        size_t start = 0;
        auto processLine = [&](const std::u32string& raw) {
            ++lineNo;
            std::u32string line = trim32(raw);
            if (line.size() < 4 || line.size() > 60) return;
            size_t wc = whitespaceWordCount(line);
            if (wc < 1 || wc > 8) return;
            char32_t last = line.back();
            switch (last) {
                case U'.': case U'!': case U'?': case U':': case U';': case U',':
                case 0x2026: case U'"': case 0x00BB: case 0x201E:
                    return;
                default:
                    break;
            }
            if (isDigit32(line.front())) return;
            auto it = index.find(line);
            if (it == index.end()) {
                index.emplace(line, counts.size());
                counts.emplace_back(line, 1);
                firstLineNo.push_back(lineNo);
            } else {
                counts[it->second].second++;
            }
        };
        while (start <= text.size()) {
            size_t nl = text.find(U'\n', start);
            if (nl == std::u32string::npos) {
                processLine(text.substr(start));
                break;
            }
            processLine(text.substr(start, nl - start));
            start = nl + 1;
        }
        for (size_t i = 0; i < counts.size(); ++i) {
            if (counts[i].second >= TEMPLATE_HEADER_MIN_REPEATS) {
                m->templateTotal += counts[i].second;
                m->templateDistinct++;
                m->templateOccurrences.push_back(
                    {counts[i].first, counts[i].second, firstLineNo[i]});
            }
        }
        std::stable_sort(m->templateOccurrences.begin(), m->templateOccurrences.end(),
            [](const AIMetrics::TemplateOccurrence& a, const AIMetrics::TemplateOccurrence& b) {
                return a.count > b.count;
            });
    }

    // Unicode suspicious chars - count distinct chars from the reference list
    // present in the ORIGINAL (pre-sanitization) text
    m->unicodeSymbols = 0;
    for (char32_t ch : UNICODE_SUSPICIOUS) {
        if (text.find(ch) != std::u32string::npos) m->unicodeSymbols++;
    }

    // Word length statistics
    double avgWordLen = 0.0;
    for (const auto& w : words) avgWordLen += static_cast<double>(w.size());
    avgWordLen /= static_cast<double>(words.size());
    m->avgWordLength = avgWordLen;
    if (words.size() > 1) {
        double var = 0.0;
        for (const auto& w : words) {
            double diff = static_cast<double>(w.size()) - avgWordLen;
            var += diff * diff;
        }
        // sample stdev (n-1), as in the Python reference
        m->wordLengthVariance = std::sqrt(var / static_cast<double>(words.size() - 1));
    } else {
        m->wordLengthVariance = 0.0;
    }

    // Pronoun ratio
    size_t pronounCount = 0;
    for (const auto& w : words) {
        if (PRONOUNS.find(w) != PRONOUNS.end()) pronounCount++;
    }
    m->pronounRatio = m->wordCount > 0
        ? static_cast<double>(pronounCount) / static_cast<double>(m->wordCount) : 0.0;

    // Readability (Flesch, simplified syllables)
    size_t syllableCount = 0;
    for (const auto& w : words) {
        size_t vowels = 0;
        for (char32_t ch : w) {
            if (ch == U'a' || ch == U'e' || ch == U'i' || ch == U'o' || ch == U'u' || ch == U'y') {
                vowels++;
            }
        }
        syllableCount += std::max<size_t>(1, vowels);
    }
    double avgSentenceLength = static_cast<double>(m->wordCount) / static_cast<double>(sentences.size());
    double avgSyllPerWord = static_cast<double>(syllableCount) / static_cast<double>(m->wordCount);
    double flesch = 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgSyllPerWord);
    m->readabilityScore = std::max(0.0, std::min(100.0, flesch));

    // Passive voice density
    size_t passiveCount = 0;
    for (const auto& p : AI_PASSIVE_PATTERNS) passiveCount += countNonOverlap(textLower, p);
    m->passiveVoiceDensity = static_cast<double>(passiveCount)
        / static_cast<double>(std::max<size_t>(whitespaceWordCount(text), 1));

    // Adjective-noun pair diversity (suffix heuristic, as in reference)
    std::set<std::u32string> adjectives, nouns;
    for (const auto& w : words) {
        for (const auto& ind : ADJ_INDICATORS) {
            if (endsWith32(w, ind)) { adjectives.insert(w); break; }
        }
        for (const auto& ind : NOUN_INDICATORS) {
            if (endsWith32(w, ind)) { nouns.insert(w); break; }
        }
    }
    std::set<std::u32string> pairs;
    for (size_t i = 0; i + 1 < words.size(); ++i) {
        if (adjectives.count(words[i]) && nouns.count(words[i + 1])) {
            pairs.insert(words[i] + U" " + words[i + 1]);
        }
    }
    double totalPossible = (!adjectives.empty() && !nouns.empty())
        ? static_cast<double>(adjectives.size()) * static_cast<double>(nouns.size()) : 1.0;
    m->adjNounPairDiversity = static_cast<double>(pairs.size()) / totalPossible;

    // Structural uniformity (repeated 2-word sentence starts)
    std::map<std::u32string, size_t> startCounts;
    for (const auto& s : sentences) {
        std::u32string trimmed = trim32(s);
        if (trimmed.empty()) continue;
        // first two whitespace-separated words
        size_t cnt = 0, b = 0, e = 0;
        std::u32string start;
        while (e <= trimmed.size() && cnt < 2) {
            if (e == trimmed.size() || isSpace32(trimmed[e])) {
                if (e > b) {
                    if (!start.empty()) start += U" ";
                    start += trimmed.substr(b, e - b);
                    cnt++;
                }
                b = e + 1;
            }
            e++;
        }
        startCounts[lower32(start)]++;
    }
    size_t repeatedStarts = 0;
    for (const auto& kv : startCounts) {
        if (kv.second > 1) repeatedStarts++;
    }
    m->structuralUniformity = sentences.empty() ? 0.0
        : static_cast<double>(repeatedStarts) / static_cast<double>(sentences.size());

    // Quantifier overuse
    size_t quantCount = 0;
    for (const auto& q : QUANTIFIERS) quantCount += countNonOverlap(textLower, q);
    m->quantifierOveruse = static_cast<double>(quantCount)
        / static_cast<double>(std::max<size_t>(whitespaceWordCount(text), 1));

    m->sentences = std::move(sentences);
    return m;
}

AIResult calculateAIProbability(const AIMetrics& m) {
    AIResult result;
    size_t total = 0;
    auto add = [&](const std::string& name, int points) {
        if (points > 0) {
            result.scores[name] = static_cast<size_t>(points);
            total += static_cast<size_t>(points);
        }
    };

    // --- Primary structural signals ---
    // Tier points are scaled by statistical reliability of the sample
    // (short texts get partial credit instead of a silent zero).
    double sentCv = m.burstiness;
    double sentScale = std::min(1.0, static_cast<double>(m.sentenceCount) / static_cast<double>(SENT_CV_FULL_SENTENCES))
                     * std::min(1.0, static_cast<double>(m.wordCount) / static_cast<double>(FULL_WORDS_FOR_CV));
    int sentCvPoints = 0;
    if (m.sentenceCount >= SENT_CV_MIN_SENTENCES && m.wordCount >= MIN_WORDS_FOR_CV) {
        for (const auto& t : SENT_CV_TIERS) {
            if (sentCv < t.threshold) {
                sentCvPoints = static_cast<int>(std::llround(t.points * sentScale));
                break;
            }
        }
    }
    add("sentence_cv", sentCvPoints);

    bool paraComputable = m.paragraphUniformityCv >= 0.0;
    int paraPoints = 0;
    double paraScale = 0.0;
    if (paraComputable) {
        paraScale = std::min(1.0, static_cast<double>(m.paragraphCount) / static_cast<double>(PARA_CV_FULL_PARAGRAPHS));
        for (const auto& t : PARA_CV_TIERS) {
            if (m.paragraphUniformityCv < t.threshold) {
                paraPoints = static_cast<int>(std::llround(t.points * paraScale));
                break;
            }
        }
    }
    add("paragraph_cv", paraPoints);

    if (paraComputable && sentCvPoints > 0) {
        for (const auto& t : JOINT_CV_TIERS) {
            if (sentCv < t.threshold && m.paragraphUniformityCv < t.threshold) {
                add("joint_uniformity", static_cast<int>(std::llround(t.points * std::min(sentScale, paraScale))));
                break;
            }
        }
    }

    // --- Tiered phrase scores ---
    if (m.phraseTiers[0] >= 2) {
        add("ai_phrases", HIGH_PHRASE_SCORES[0]);
    } else if (m.phraseTiers[0] == 1) {
        add("ai_phrases", HIGH_PHRASE_SCORES[1]);
    } else if (m.phraseTiers[1] >= 3) {
        add("ai_phrases", MEDIUM_PHRASE_SCORES[0]);
    } else if (m.phraseTiers[1] >= 1) {
        add("ai_phrases", MEDIUM_PHRASE_SCORES[1]);
    } else if (m.phraseTiers[2] >= 4) {
        add("ai_phrases", WEAK_PHRASE_SCORE);
    }

    // --- Connective density ---
    for (const auto& t : CONNECTIVE_TIERS) {
        if (m.connectiveDensity >= t.threshold) { add("connectives", t.points); break; }
    }

    // --- Template header repetition (structured-answer genre) ---
    if (m.templateDistinct >= 2 || m.templateTotal >= 10) {
        add("template_headers", TEMPLATE_HEADER_SCORES[0]);
    } else if (m.templateTotal >= TEMPLATE_HEADER_MIN_REPEATS) {
        add("template_headers", TEMPLATE_HEADER_SCORES[1]);
    }

    // --- Supporting statistical metrics ---
    if (m.lexicalDiversity < 0.45) add("lexical_diversity", 15);
    else if (m.lexicalDiversity < 0.55) add("lexical_diversity", 8);

    if (m.entropy < 5.0) add("entropy", 15);
    else if (m.entropy < 6.5) add("entropy", 8);

    if (m.patternRepetition > 0.35) add("pattern_repetition", 10);

    if (m.repetitionScore > 0.5) add("repetition", 8);

    if (m.punctuationDensity > 0.04) add("punctuation", 4);

    if (m.unicodeSymbols > 0) add("unicode", 4);

    if (m.avgWordLength < 4.0) add("avg_word_length", 5);
    else if (m.avgWordLength < 4.5) add("avg_word_length", 3);

    if (m.wordLengthVariance < 1.5) add("word_length_variance", 4);

    if (m.pronounRatio > 0.15) add("pronoun_ratio", 4);

    if (m.readabilityScore > 70) add("readability", 5);
    else if (m.readabilityScore > 60) add("readability", 3);

    if (m.passiveVoiceDensity > 0.05) add("passive_voice", 4);

    if (m.adjNounPairDiversity < 0.3) add("adj_noun_diversity", 3);

    if (m.structuralUniformity > 0.4) add("structural_uniformity", 4);

    if (m.quantifierOveruse > 0.02) add("quantifier_overuse", 3);

    // Length-based confidence adjustment
    if (m.wordCount < 300) {
        result.confidence = "LOW";
    } else if (m.wordCount < 1000) {
        result.confidence = "MEDIUM";
    } else {
        result.confidence = "HIGH";
    }

    double lengthFactor = std::min(1.0, static_cast<double>(m.wordCount) / 1000.0);
    double adjustedTotal = static_cast<double>(total) * (0.9 + 0.1 * lengthFactor);
    result.probability = std::min(100.0, adjustedTotal);

    return result;
}

// =========================================================
// EVIDENCE (AI_SIGNALS_SPEC.md section 6)
// =========================================================

static std::string truncateMiddle(const std::u32string& s, size_t width = 110) {
    if (s.size() <= width) return u8from32(s);
    size_t half = width / 2 - 5;
    std::u32string mid = s.substr(0, half) + U" ... " + s.substr(s.size() - half);
    return u8from32(mid);
}

static std::string excerptFor(const std::u32string& text, size_t idx, const std::u32string& phrase) {
    const std::u32string dotSp = U". ", exclSp = U"! ", questSp = U"? ", nl = U"\n";
    size_t sentStart = 0;
    size_t best = std::u32string::npos;
    size_t r;
    if ((r = rfindBefore(text, dotSp, idx)) != std::u32string::npos && r > best) best = r;
    if ((r = rfindBefore(text, exclSp, idx)) != std::u32string::npos && r > best) best = r;
    if ((r = rfindBefore(text, questSp, idx)) != std::u32string::npos && r > best) best = r;
    if ((r = rfindBefore(text, nl, idx)) != std::u32string::npos && r > best) best = r;
    if (best != std::u32string::npos) sentStart = best + 1;

    size_t sentEnd = text.size();
    size_t bestEnd = std::u32string::npos;
    size_t f;
    if ((f = text.find(dotSp, idx)) != std::u32string::npos && f < bestEnd) bestEnd = f;
    if ((f = text.find(exclSp, idx)) != std::u32string::npos && f < bestEnd) bestEnd = f;
    if ((f = text.find(questSp, idx)) != std::u32string::npos && f < bestEnd) bestEnd = f;
    if ((f = text.find(nl, idx)) != std::u32string::npos && f < bestEnd) bestEnd = f;
    if (bestEnd != std::u32string::npos) sentEnd = bestEnd;

    std::u32string fragment = trim32(text.substr(sentStart, sentEnd - sentStart));
    std::u32string fLower = lower32(fragment);
    size_t pos = fLower.find(phrase);
    if (pos == std::u32string::npos) {
        return truncateMiddle(fragment);
    }
    if (fragment.size() > 110) {
        const size_t wLeft = 45, wRight = 60;
        size_t start = pos > wLeft ? pos - wLeft : 0;
        size_t end = std::min(fragment.size(), pos + phrase.size() + wRight);
        std::u32string prefix = start > 0 ? U"... " : U"";
        std::u32string suffix = end < fragment.size() ? U" ..." : U"";
        fragment = prefix + fragment.substr(start, end - start) + suffix;
        pos = pos - start + prefix.size();
    }
    std::u32string out = fragment.substr(0, pos) + U">>>" +
                         fragment.substr(pos, phrase.size()) + U"<<<" +
                         fragment.substr(pos + phrase.size());
    return u8from32(out);
}

static size_t countNewlinesBefore(const std::u32string& text, size_t idx) {
    size_t cnt = 0;
    for (size_t i = 0; i < idx && i < text.size(); ++i) {
        if (text[i] == U'\n') cnt++;
    }
    return cnt;
}

std::vector<EvidenceItem> buildEvidence(const std::u32string& text, const AIMetrics& m) {
    std::vector<EvidenceItem> evidence;
    const auto& sentences = m.sentences;

    // 1. Phrase hits with locations (high tier first)
    size_t shown = 0;
    for (const auto& occ : m.phraseOccurrences) {
        if (shown >= 10) break;
        const char* label = occ.tier == 0 ? "HIGH-risk"
                          : occ.tier == 1 ? "typical" : "weak";
        EvidenceItem ev;
        ev.type = "phrase";
        ev.detail = std::string(label) + " AI phrase '" + u8from32(occ.phrase) + "'";
        ev.hasLine = true;
        ev.line = countNewlinesBefore(text, occ.idx) + 1;
        ev.hasExcerpt = true;
        ev.excerpt = excerptFor(text, occ.idx, occ.phrase);
        evidence.push_back(std::move(ev));
        shown++;
    }

    // 1b. Repeated template headers (structured-answer genre)
    for (size_t i = 0; i < m.templateOccurrences.size() && i < 4; ++i) {
        const auto& occ = m.templateOccurrences[i];
        std::u32string detail32 = U"repeated template header '" + occ.line +
                                  U"' ×";
        EvidenceItem ev;
        ev.type = "template";
        ev.detail = u8from32(detail32) + std::to_string(occ.count);
        ev.hasLine = true;
        ev.line = occ.firstLineNo;
        ev.hasExcerpt = false;
        evidence.push_back(std::move(ev));
    }

    // 2. Sentence-length uniformity
    if (m.burstiness < 0.50 && m.wordCount >= MIN_WORDS_FOR_CV) {
        std::ostringstream detail;
        detail << "sentence lengths are uniform: CV=" << std::fixed << std::setprecision(2)
               << m.burstiness << " (human prose is typically > 0.50); first lengths:";
        size_t shownLens = 0;
        for (const auto& s : sentences) {
            size_t wc = whitespaceWordCount(s);
            if (wc == 0) continue;
            if (shownLens >= 25) break;
            detail << " " << wc;
            shownLens++;
        }
        evidence.push_back({"uniformity", detail.str(), false, 0, false, ""});
    }

    // 3. Paragraph-length uniformity
    if (m.paragraphUniformityCv >= 0.0 && m.paragraphUniformityCv < 0.45) {
        std::ostringstream detail;
        detail << "paragraph lengths are uniform: CV=" << std::fixed << std::setprecision(2)
               << m.paragraphUniformityCv << " across " << m.paragraphLengths.size()
               << " paragraphs (human prose is typically > 0.50); lengths:";
        size_t n = 0;
        for (size_t len : m.paragraphLengths) {
            if (n >= 20) break;
            detail << " " << len;
            n++;
        }
        evidence.push_back({"uniformity", detail.str(), false, 0, false, ""});
    }

    // 4. Connective overuse with example sentences
    if (m.connectiveDensity >= 0.10) {
        std::vector<std::pair<size_t, const std::u32string*>> ranked;
        for (const auto& sent : sentences) {
            std::u32string lowerSent = lower32(sent);
            size_t n = 0;
            for (const auto& c : CONNECTIVES) {
                if (lowerSent.find(c) != std::u32string::npos) n++;
            }
            if (n >= 2) ranked.emplace_back(n, &sent);
        }
        std::stable_sort(ranked.begin(), ranked.end(),
            [](const auto& a, const auto& b) { return a.first > b.first; });
        for (size_t i = 0; i < ranked.size() && i < 2; ++i) {
            std::ostringstream detail;
            detail << "sentence carries " << ranked[i].first << " discourse connectives";
            evidence.push_back({"connective", detail.str(), false, 0, true,
                                truncateMiddle(trim32(*ranked[i].second), 130)});
        }
    }

    // 5. Most suspicious sentences
    std::vector<std::pair<size_t, const std::u32string*>> sentenceScores;
    for (const auto& sent : sentences) {
        std::u32string lowerSent = lower32(sent);
        size_t markers = 0;
        static const int tierWeights[3] = {3, 2, 1};
        for (int tier = 0; tier < 3; ++tier) {
            for (const auto& p : AI_PHRASES_BY_TIER[tier]) {
                if (lowerSent.find(p) != std::u32string::npos) markers += tierWeights[tier];
            }
        }
        for (const auto& c : CONNECTIVES) {
            if (lowerSent.find(c) != std::u32string::npos) markers += 1;
        }
        sentenceScores.emplace_back(markers, &sent);
    }
    std::stable_sort(sentenceScores.begin(), sentenceScores.end(),
        [](const auto& a, const auto& b) { return a.first > b.first; });
    std::u32string textLower = lower32(text);
    for (size_t i = 0; i < sentenceScores.size() && i < 3; ++i) {
        size_t markers = sentenceScores[i].first;
        const std::u32string& sent = *sentenceScores[i].second;
        if (markers < 2) break;
        EvidenceItem ev;
        ev.type = "sentence";
        ev.detail = "sentence with " + std::to_string(markers) + " AI markers";
        std::u32string head = sent.size() > 40 ? sent.substr(0, 40) : sent;
        size_t idx = textLower.find(lower32(head));
        if (idx != std::u32string::npos) {
            ev.hasLine = true;
            ev.line = countNewlinesBefore(text, idx) + 1;
        }
        ev.hasExcerpt = true;
        ev.excerpt = truncateMiddle(trim32(sent), 130);
        evidence.push_back(std::move(ev));
    }

    return evidence;
}

// =========================================================
// INTERPRETATION
// =========================================================

std::pair<std::string, std::vector<std::string>> getInterpretation(const AIMetrics& m, double aiProbability) {
    std::vector<std::string> interpretations;
    std::string verdict;

    std::ostringstream prob;
    prob << std::fixed << std::setprecision(1) << aiProbability << "%";

    if (aiProbability > 70.0) {
        verdict = "Strong AI-like statistical profile (" + prob.str() + ")";
    } else if (aiProbability > 55.0) {
        verdict = "Probable AI-generated text with multiple indicators (" + prob.str() + ")";
    } else if (aiProbability > 35.0) {
        verdict = "Mixed profile: human-like and AI-like signals (" + prob.str() + ")";
    } else {
        verdict = "Text statistically appears more human-like (" + prob.str() + ")";
    }

    // Honest abstention: below the structural-signal horizon the "human-like"
    // verdict would be an artifact of missing data, not evidence.
    if (m.wordCount < FULL_WORDS_FOR_CV || m.sentenceCount < SENT_CV_MIN_SENTENCES) {
        verdict += " NOTE: text is too short for reliable structural analysis — "
                   "this verdict is unreliable, not evidence of human authorship.";
    }

    // Genre abstention: promotional/social register - verdict withdrawn, no AI points
    if (m.promotionalRegister) {
        verdict += " NOTE: promotional/social-media register (emoji- and "
                   "exclamation-heavy) is outside the calibration corpus — "
                   "this verdict is unreliable for this genre.";
    }

    if (m.burstiness < 0.35) {
        interpretations.push_back("⚠️ Uniform sentence lengths (low burstiness) - strong AI signal");
    } else if (m.burstiness < 0.45) {
        interpretations.push_back("⚠️ Somewhat uniform sentence lengths - AI-like");
    }

    if (m.paragraphUniformityCv >= 0.0 && m.paragraphUniformityCv < 0.35) {
        interpretations.push_back("⚠️ Uniform paragraph lengths - AI-like");
    }

    if (m.lexicalDiversity < 0.45) {
        interpretations.push_back("⚠️ Low lexical diversity - limited vocabulary variation");
    } else if (m.lexicalDiversity > 0.65) {
        interpretations.push_back("✓ High lexical diversity - rich vocabulary variation");
    }

    if (m.entropy < 5.0) {
        interpretations.push_back("⚠️ Low entropy - unnaturally uniform word distribution");
    } else if (m.entropy > 6.0) {
        interpretations.push_back("✓ Good entropy - natural word distribution");
    }

    if (m.phraseTiers[0] > 0 || m.phraseTiers[1] > 0) {
        interpretations.push_back("⚠️ AI phrases: high=" + std::to_string(m.phraseTiers[0]) +
                                  ", medium=" + std::to_string(m.phraseTiers[1]));
    }

    if (m.connectiveDensity >= 0.12) {
        interpretations.push_back("⚠️ High discourse-connective density");
    }

    if (m.patternRepetition > 0.35) {
        interpretations.push_back("⚠️ High pattern repetition - template-like structure");
    }

    if (m.unicodeSymbols > 0) {
        interpretations.push_back("⚠️ Found " + std::to_string(m.unicodeSymbols) + " suspicious Unicode characters");
    }

    return {verdict, interpretations};
}

// =========================================================
// REPORTING FUNCTIONS
// =========================================================

std::string buildReport(const std::string& inputFile, const std::string& outputFile,
                       const std::map<char32_t, size_t>& replaced,
                       const std::map<char32_t, size_t>& watermarkRemoved,
                       const std::map<std::string, size_t>& wordFreq,
                       double elapsed,
                       const AIMetrics* aiMetrics, const AIResult* aiResult,
                       bool removeWatermark, const std::string& lang,
                       const std::vector<EvidenceItem>* aiEvidence) {

    std::ostringstream builder;

    // Header
    builder << std::string(70, '=') << "\n";
    builder << "aiparstxt-ext — Enhanced AI Forensic Analyzer Report\n";
    builder << "Language: " << lang << "\n";
    builder << std::string(70, '=') << "\n";
    builder << "\n";

    // Basic info
    builder << "Input file:  " << inputFile << "\n";
    builder << "Output file: " << outputFile << "\n";
    builder << "Execution time: " << std::fixed << std::setprecision(6) << elapsed << "s\n";
    builder << "\n";

    // Watermark analysis
    builder << "--- AI Watermark Analysis ---\n";
    size_t totalWatermark = 0;
    for (const auto& pair : watermarkRemoved) {
        totalWatermark += pair.second;
    }
    builder << "Watermark characters removed: " << totalWatermark << "\n";

    if (totalWatermark > 0) {
        builder << "Removed watermark character types:\n";
        // Sort by count
        std::vector<std::pair<char32_t, size_t>> sorted(watermarkRemoved.begin(), watermarkRemoved.end());
        std::sort(sorted.begin(), sorted.end(),
            [](const auto& a, const auto& b) { return a.second > b.second; });

        for (size_t i = 0; i < std::min(sorted.size(), static_cast<size_t>(20)); ++i) {
            char32_t ch = sorted[i].first;
            size_t count = sorted[i].second;
            std::ostringstream codepoint;
            codepoint << "U+" << std::hex << std::setw(4) << std::setfill('0') << std::uppercase << static_cast<uint32_t>(ch);
            builder << "  " << codepoint.str() << ": " << count << "\n";
        }
        if (sorted.size() > 20) {
            builder << "  ... and " << (sorted.size() - 20) << " more types\n";
        }
    } else {
        builder << "No AI watermark characters detected\n";
    }
    builder << "\n";

    // Replaced characters
    builder << "--- Replaced Characters ---\n";
    size_t totalReplaced = 0;
    for (const auto& pair : replaced) {
        totalReplaced += pair.second;
    }
    builder << "Characters replaced: " << totalReplaced << "\n";

    if (totalReplaced > 0) {
        builder << "Replaced character types:\n";
        std::vector<std::pair<char32_t, size_t>> sorted(replaced.begin(), replaced.end());
        std::sort(sorted.begin(), sorted.end(),
            [](const auto& a, const auto& b) { return a.second > b.second; });

        for (size_t i = 0; i < std::min(sorted.size(), static_cast<size_t>(10)); ++i) {
            char32_t ch = sorted[i].first;
            size_t count = sorted[i].second;
            std::ostringstream codepoint;
            codepoint << "U+" << std::hex << std::setw(4) << std::setfill('0') << std::uppercase << static_cast<uint32_t>(ch);
            builder << "  " << codepoint.str() << ": " << count << "\n";
        }
        if (sorted.size() > 10) {
            builder << "  ... and " << (sorted.size() - 10) << " more types\n";
        }
    } else {
        builder << "No characters replaced\n";
    }
    builder << "\n";

    // AI Forensic Analysis
    if (aiMetrics != nullptr && aiResult != nullptr) {
        builder << std::string(70, '=') << "\n";
        builder << "AI FORENSIC ANALYSIS\n";
        builder << std::string(70, '=') << "\n";
        builder << "\n";

        auto [verdict, interpretations] = getInterpretation(*aiMetrics, aiResult->probability);

        builder << "Overall Verdict: " << verdict << "\n";
        builder << "Confidence Level: " << aiResult->confidence << "\n";
        builder << "\n";

        builder << "Detailed Metrics:\n";
        builder << "  Word count:            " << aiMetrics->wordCount << "\n";
        builder << "  Sentence count:        " << aiMetrics->sentenceCount << "\n";
        builder << "  Sentence length CV:    " << std::fixed << std::setprecision(3) << aiMetrics->burstiness << "\n";
        if (aiMetrics->paragraphUniformityCv >= 0.0) {
            builder << "  Paragraph length CV:   " << std::fixed << std::setprecision(3) << aiMetrics->paragraphUniformityCv << "\n";
        } else {
            builder << "  Paragraph length CV:   n/a (<4 paragraphs)\n";
        }
        builder << "  Lexical diversity:     " << std::fixed << std::setprecision(3) << aiMetrics->lexicalDiversity << "\n";
        builder << "  Repetition score:      " << std::fixed << std::setprecision(3) << aiMetrics->repetitionScore << "\n";
        builder << "  Entropy:               " << std::fixed << std::setprecision(3) << aiMetrics->entropy << "\n";
        builder << "  Connective density:    " << std::fixed << std::setprecision(3) << aiMetrics->connectiveDensity << "\n";
        builder << "  Template headers:      " << aiMetrics->templateTotal
                << " repeats (" << aiMetrics->templateDistinct << " distinct)\n";
        builder << "  Pattern repetition:    " << std::fixed << std::setprecision(3) << aiMetrics->patternRepetition << "\n";
        builder << "  Punctuation density:   " << std::fixed << std::setprecision(3) << aiMetrics->punctuationDensity << "\n";
        builder << "  AI phrases (tiers):    high=" << aiMetrics->phraseTiers[0]
                << ", medium=" << aiMetrics->phraseTiers[1]
                << ", weak=" << aiMetrics->phraseTiers[2] << "\n";
        builder << "  AI phrase hits:        " << aiMetrics->aiPhraseHits << "\n";
        builder << "  Unicode suspicious:    " << aiMetrics->unicodeSymbols << "\n";
        builder << "  Avg word length:       " << std::fixed << std::setprecision(2) << aiMetrics->avgWordLength << "\n";
        builder << "  Word length variance:  " << std::fixed << std::setprecision(2) << aiMetrics->wordLengthVariance << "\n";
        builder << "\n";

        if (aiEvidence != nullptr && !aiEvidence->empty()) {
            builder << "AI EVIDENCE (locations in the text):\n";
            for (size_t i = 0; i < aiEvidence->size() && i < 15; ++i) {
                const auto& ev = (*aiEvidence)[i];
                std::string loc = ev.hasLine ? ("line " + std::to_string(ev.line)) : "text-wide";
                builder << "  [" << (i + 1) << "] " << loc << ": " << ev.detail << "\n";
                if (ev.hasExcerpt && !ev.excerpt.empty()) {
                    builder << "      \"" << ev.excerpt << "\"\n";
                }
            }
            builder << "\n";
        }

        if (!interpretations.empty()) {
            builder << "Signal Analysis:\n";
            for (const auto& interp : interpretations) {
                builder << "  " << interp << "\n";
            }
            builder << "\n";
        }

        builder << std::string(70, '=') << "\n";
        builder << "\n";
    }

    // Word frequency
    builder << "--- Top Word Frequencies (Filtered) ---\n";
    if (!wordFreq.empty()) {
        std::vector<std::pair<std::string, size_t>> sorted(wordFreq.begin(), wordFreq.end());
        std::sort(sorted.begin(), sorted.end(),
            [](const auto& a, const auto& b) { return a.second > b.second; });

        for (size_t i = 0; i < std::min(sorted.size(), static_cast<size_t>(20)); ++i) {
            builder << "  " << sorted[i].first << ": " << sorted[i].second << "\n";
        }
    } else {
        builder << "(skipped)\n";
    }

    return builder.str();
}

// =========================================================
// MAIN FUNCTION
// =========================================================

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file> [options]\n";
        return 1;
    }

    std::string inputFile = argv[1];
    std::string outputFile = "";
    std::string reportFile = "report_cpp-ext.txt";
    bool noEdit = false;
    bool noReport = false;
    bool noWords = false;
    bool removeWatermark = false;

    // Parse arguments
    for (int i = 2; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "-o" || arg == "--output") {
            if (i + 1 < argc) {
                outputFile = argv[++i];
            }
        } else if (arg == "-r" || arg == "--report") {
            if (i + 1 < argc) {
                reportFile = argv[++i];
            }
        } else if (arg == "--no-edit") {
            noEdit = true;
        } else if (arg == "--no-report") {
            noReport = true;
        } else if (arg == "--no-words") {
            noWords = true;
        } else if (arg == "--remove-watermark") {
            removeWatermark = true;
        }
    }

    // Set default output file
    if (outputFile.empty()) {
        size_t dotPos = inputFile.find_last_of('.');
        if (dotPos != std::string::npos && dotPos > 0) {
            outputFile = inputFile.substr(0, dotPos) + ".ed.txt";
        } else {
            outputFile = inputFile + ".ed.txt";
        }
    }

    // Read input file
    std::ifstream file(inputFile, std::ios::binary);
    if (!file) {
        std::cerr << "Error reading " << inputFile << "\n";
        return 1;
    }

    std::string text((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    // Convert to UTF-32 for processing
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter;
    std::u32string text32;
    try {
        text32 = converter.from_bytes(text);
    } catch (...) {
        std::cerr << "Error converting text to UTF-32\n";
        return 1;
    }

    // Process text
    auto start = std::chrono::high_resolution_clock::now();
    ProcessResult result = process(text32, removeWatermark);

    // Calculate word frequency (on sanitized text, for the report)
    std::map<std::string, size_t> wordFreq;
    if (!noWords) {
        wordFreq = wordFrequency(result.cleaned);
    }

    // AI forensic analysis runs on the ORIGINAL text: sanitization
    // replaces disallowed characters with '?', which would corrupt
    // sentence splitting and phrase positions.
    AIMetrics* aiMetrics = nullptr;
    AIResult* aiResult = nullptr;
    std::vector<EvidenceItem> evidence;
    if (!result.cleaned.empty()) {
        aiMetrics = calculateAIForensicMetrics(text32);
        if (aiMetrics != nullptr) {
            aiResult = new AIResult(calculateAIProbability(*aiMetrics));
            evidence = buildEvidence(text32, *aiMetrics);
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();

    // Write output file
    if (!noEdit) {
        try {
            std::string outputUtf8 = converter.to_bytes(result.cleaned);
            std::ofstream out(outputFile, std::ios::binary);
            out.write(outputUtf8.data(), outputUtf8.size());
        } catch (...) {
            std::cerr << "Error writing " << outputFile << "\n";
        }
    }

    // Generate and write report
    if (!noReport) {
        std::string reportContent = buildReport(
            inputFile, outputFile,
            result.replaced, result.watermarkRemoved,
            wordFreq, elapsed,
            aiMetrics, aiResult,
            removeWatermark, "C++-Ext",
            &evidence
        );

        std::ofstream report(reportFile, std::ios::binary);
        report.write(reportContent.data(), reportContent.size());
    }

    // Print summary
    size_t totalReplaced = 0;
    for (const auto& pair : result.replaced) {
        totalReplaced += pair.second;
    }
    size_t totalWatermark = 0;
    for (const auto& pair : result.watermarkRemoved) {
        totalWatermark += pair.second;
    }

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Processed in " << elapsed << "s\n";
    std::cout << "Replacements: " << totalReplaced << "\n";
    std::cout << "Watermarks removed: " << totalWatermark << "\n";
    if (aiResult != nullptr) {
        std::cout << "AI Probability: " << std::fixed << std::setprecision(1) << aiResult->probability << "% (confidence: " << aiResult->confidence << ")\n";
        if (!evidence.empty()) {
            std::cout << "AI Evidence (top " << std::min<size_t>(3, evidence.size())
                      << " of " << evidence.size() << "):\n";
            for (size_t i = 0; i < evidence.size() && i < 3; ++i) {
                const auto& ev = evidence[i];
                std::string loc = ev.hasLine ? ("line " + std::to_string(ev.line)) : "text-wide";
                std::cout << "  " << loc << ": " << ev.detail << "\n";
            }
        }
    }
    std::cout << "Output: " << (noEdit ? "(skipped)" : outputFile) << "\n";
    std::cout << "Report: " << (noReport ? "(skipped)" : reportFile) << "\n";

    // Cleanup
    delete aiMetrics;
    delete aiResult;

    return 0;
}
