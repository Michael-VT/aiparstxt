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
// FORENSIC ANALYSIS STRUCTS
// =========================================================

struct AIMetrics {
    size_t wordCount;
    size_t sentenceCount;
    double lexicalDiversity;
    double repetitionScore;
    double entropy;
    double burstiness;
    double patternRepetition;
    double punctuationDensity;
    size_t aiPhraseHits;
    size_t unicodeSymbols;
    double avgWordLength;
    double wordLengthVariance;
};

struct AIResult {
    double probability;
    std::string confidence;
    std::map<std::string, size_t> scores;
};

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

std::map<std::string, size_t> wordFrequency(const std::u32string& text) {
    std::map<std::string, size_t> freq;
    std::u32string currentWord;
    
    // Simple stopwords set
    std::set<std::string> stopwords = {
        // English
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
        "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
        // Russian (transliterated for simplicity)
        "и", "в", "не", "что", "он", "на", "я", "с", "как", "а", "то", "но", "они", "мы"
    };
    
    // Convert to UTF-32 for processing
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter;
    
    for (char32_t ch : text) {
        if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || 
            (ch >= 0x0430 && ch <= 0x044F) || // Russian lowercase
            (ch >= 0x0410 && ch <= 0x042F) || // Russian uppercase
            ch == '\'') {
            currentWord.push_back(std::tolower(ch));
        } else {
            if (!currentWord.empty()) {
                std::string word;
                try {
                    std::u32string temp(1, currentWord[0]);
                    word = converter.to_bytes(currentWord);
                    if (word.length() > 2 && stopwords.find(word) == stopwords.end()) {
                        freq[word]++;
                    }
                } catch (...) {
                    // Handle conversion errors gracefully
                }
                currentWord.clear();
            }
        }
    }
    
    // Handle last word
    if (!currentWord.empty()) {
        std::string word;
        try {
            word = converter.to_bytes(currentWord);
            if (word.length() > 2 && stopwords.find(word) == stopwords.end()) {
                freq[word]++;
            }
        } catch (...) {
            // Handle conversion errors
        }
    }
    
    return freq;
}

std::vector<std::u32string> splitSentences(const std::u32string& text) {
    std::vector<std::u32string> sentences;
    std::u32string current;
    bool sentenceEnd = false;
    
    for (char32_t ch : text) {
        if (ch == '.' || ch == '!' || ch == '?') {
            sentenceEnd = true;
            current.push_back(ch);
        } else if (sentenceEnd && std::isspace(static_cast<char>(ch))) {
            sentenceEnd = false;
            if (!current.empty() && current.size() > 3) {
                sentences.push_back(current);
            }
            current.clear();
        } else {
            current.push_back(ch);
        }
    }
    
    // Handle last sentence
    if (!current.empty() && current.size() > 3) {
        sentences.push_back(current);
    }
    
    return sentences;
}

AIMetrics* calculateAIForensicMetrics(const std::u32string& text, const std::map<std::string, size_t>& wordFreq) {
    if (text.empty()) {
        return nullptr;
    }
    
    // Simple word splitting
    std::vector<std::u32string> words;
    std::u32string currentWord;
    
    for (char32_t ch : text) {
        if (std::isalpha(static_cast<char>(ch)) || ch == '\'') {
            currentWord.push_back(ch);
        } else {
            if (!currentWord.empty()) {
                words.push_back(currentWord);
                currentWord.clear();
            }
        }
    }
    if (!currentWord.empty()) {
        words.push_back(currentWord);
    }
    
    if (words.empty()) {
        return nullptr;
    }
    
    auto sentences = splitSentences(text);
    if (sentences.empty()) {
        return nullptr;
    }
    
    AIMetrics* metrics = new AIMetrics();
    
    // Core metrics
    metrics->wordCount = words.size();
    metrics->sentenceCount = sentences.size();
    
    std::set<std::u32string> uniqueWords(words.begin(), words.end());
    metrics->lexicalDiversity = static_cast<double>(uniqueWords.size()) / static_cast<double>(words.size());
    
    // Repetition score
    size_t repeated = 0;
    for (const auto& pair : wordFreq) {
        if (pair.second > 1) {
            repeated++;
        }
    }
    metrics->repetitionScore = static_cast<double>(repeated) / static_cast<double>(wordFreq.size());
    
    // Entropy calculation
    size_t total = 0;
    for (const auto& pair : wordFreq) {
        total += pair.second;
    }
    metrics->entropy = 0.0;
    if (total > 0) {
        for (const auto& pair : wordFreq) {
            double p = static_cast<double>(pair.second) / static_cast<double>(total);
            metrics->entropy -= p * std::log2(p);
        }
    }
    
    // Sentence length analysis (burstiness)
    std::vector<size_t> sentLengths;
    for (const auto& sent : sentences) {
        size_t wordCount = 0;
        for (char32_t ch : sent) {
            if (std::isalpha(static_cast<char>(ch))) {
                wordCount++;
            }
        }
        sentLengths.push_back(wordCount);
    }
    
    double avgSentLen = 0.0;
    for (size_t len : sentLengths) {
        avgSentLen += static_cast<double>(len);
    }
    avgSentLen /= static_cast<double>(sentLengths.size());
    
    double variance = 0.0;
    for (size_t len : sentLengths) {
        double diff = static_cast<double>(len) - avgSentLen;
        variance += diff * diff;
    }
    variance /= static_cast<double>(sentLengths.size());
    
    metrics->burstiness = (avgSentLen > 0.0) ? std::sqrt(variance) / avgSentLen : 0.0;
    
    // Pattern repetition
    auto categorizeLength = [](size_t length) -> char32_t {
        if (length < 10) return 'S';
        if (length < 20) return 'M';
        return 'L';
    };
    
    std::vector<char32_t> patterns;
    for (size_t len : sentLengths) {
        patterns.push_back(categorizeLength(len));
    }
    
    std::map<char32_t, size_t> patternCounts;
    for (char32_t pattern : patterns) {
        patternCounts[pattern]++;
    }
    
    size_t repeatedPatterns = 0;
    for (const auto& pair : patternCounts) {
        if (pair.second > 1) {
            repeatedPatterns++;
        }
    }
    metrics->patternRepetition = static_cast<double>(repeatedPatterns) / static_cast<double>(patterns.size());
    
    // Punctuation density
    size_t punctCount = 0;
    for (char32_t ch : text) {
        switch (ch) {
            case ',': case '.': case '!': case '?': case ';': case ':':
            case '(': case ')': case '-': case 0x2014: case 0x2013: // Em-dash variants
                punctCount++;
                break;
        }
    }
    metrics->punctuationDensity = static_cast<double>(punctCount) / static_cast<double>(text.size());
    
    // AI phrase detection (simplified)
    std::vector<std::string> aiPhrases = {
        "in conclusion", "in summary", "it is worth noting", "basically", "essentially",
        "furthermore", "moreover", "however", "nevertheless", "as an ai"
    };
    
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter;
    std::string textUtf8;
    try {
        textUtf8 = converter.to_bytes(text);
        std::transform(textUtf8.begin(), textUtf8.end(), textUtf8.begin(), ::tolower);
        
        metrics->aiPhraseHits = 0;
        for (const auto& phrase : aiPhrases) {
            if (textUtf8.find(phrase) != std::string::npos) {
                metrics->aiPhraseHits++;
            }
        }
    } catch (...) {
        metrics->aiPhraseHits = 0;
    }
    
    // Unicode suspicious characters
    metrics->unicodeSymbols = 0;
    for (char32_t ch : text) {
        uint32_t cp = static_cast<uint32_t>(ch);
        if ((cp >= 0x2010 && cp <= 0x2014) || // Hyphen/dash variants
            (cp >= 0x2018 && cp <= 0x201F) || // Quotes
            cp == 0x2026 || cp == 0x202F || cp == 0x205F || cp == 0x00A0 ||
            (cp >= 0x2000 && cp <= 0x200A)) {
            metrics->unicodeSymbols++;
        }
    }
    
    // Word length statistics
    std::vector<size_t> wordLengths;
    for (const auto& word : words) {
        wordLengths.push_back(word.size());
    }
    
    double avgWordLen = 0.0;
    for (size_t len : wordLengths) {
        avgWordLen += static_cast<double>(len);
    }
    avgWordLen /= static_cast<double>(wordLengths.size());
    metrics->avgWordLength = avgWordLen;
    
    double wordLenVariance = 0.0;
    if (wordLengths.size() > 1) {
        for (size_t len : wordLengths) {
            double diff = static_cast<double>(len) - avgWordLen;
            wordLenVariance += diff * diff;
        }
        wordLenVariance /= static_cast<double>(wordLengths.size());
        metrics->wordLengthVariance = std::sqrt(wordLenVariance);
    } else {
        metrics->wordLengthVariance = 0.0;
    }
    
    return metrics;
}

AIResult calculateAIProbability(const AIMetrics& metrics) {
    AIResult result;
    result.scores = {};
    size_t total = 0;
    
    // Core metrics with enhanced weighting
    if (metrics.lexicalDiversity < 0.45) {
        result.scores["lexical_diversity"] = 25;
        total += 25;
    } else if (metrics.lexicalDiversity < 0.55) {
        result.scores["lexical_diversity"] = 15;
        total += 15;
    }
    
    if (metrics.entropy < 5.0) {
        result.scores["entropy"] = 25;
        total += 25;
    } else if (metrics.entropy < 5.8) {
        result.scores["entropy"] = 15;
        total += 15;
    }
    
    if (metrics.burstiness < 0.35) {
        result.scores["burstiness"] = 20;
        total += 20;
    } else if (metrics.burstiness < 0.45) {
        result.scores["burstiness"] = 10;
        total += 10;
    }
    
    if (metrics.patternRepetition > 0.35) {
        result.scores["pattern_repetition"] = 20;
        total += 20;
    } else if (metrics.patternRepetition > 0.25) {
        result.scores["pattern_repetition"] = 10;
        total += 10;
    }
    
    if (metrics.aiPhraseHits >= 3) {
        result.scores["ai_phrases"] = 20;
        total += 20;
    } else if (metrics.aiPhraseHits >= 1) {
        result.scores["ai_phrases"] = 10;
        total += 10;
    }
    
    if (metrics.repetitionScore > 0.5) {
        result.scores["repetition"] = 15;
        total += 15;
    }
    
    if (metrics.punctuationDensity > 0.04) {
        result.scores["punctuation"] = 5;
        total += 5;
    }
    
    if (metrics.unicodeSymbols > 0) {
        result.scores["unicode"] = 5;
        total += 5;
    }
    
    // Extended metrics
    if (metrics.avgWordLength < 4.0) {
        result.scores["word_length"] = 10;
        total += 10;
    } else if (metrics.avgWordLength < 4.5) {
        result.scores["word_length"] = 5;
        total += 5;
    }
    
    if (metrics.wordLengthVariance < 1.5) {
        result.scores["word_variance"] = 8;
        total += 8;
    }
    
    // Length-based confidence adjustment
    double confidenceFactor;
    if (metrics.wordCount < 300) {
        confidenceFactor = 0.8;
        result.confidence = "LOW";
    } else if (metrics.wordCount < 1000) {
        confidenceFactor = 0.9;
        result.confidence = "MEDIUM";
    } else {
        confidenceFactor = 1.0;
        result.confidence = "HIGH";
    }
    
    double adjustedTotal = static_cast<double>(total) * confidenceFactor;
    result.probability = std::min(100.0, adjustedTotal);
    
    return result;
}

std::pair<std::string, std::vector<std::string>> getInterpretation(const AIMetrics& metrics, double aiProbability, const std::string& confidence) {
    std::vector<std::string> interpretations;
    std::string verdict;
    
    if (aiProbability > 60.0) {
        verdict = "High probability of AI-generated content (" + std::to_string(static_cast<int>(aiProbability)) + "%)";
    } else if (aiProbability > 30.0) {
        verdict = "Moderate probability of AI involvement (" + std::to_string(static_cast<int>(aiProbability)) + "%)";
    } else if (aiProbability > 10.0) {
        verdict = "Low probability of AI-generated content (" + std::to_string(static_cast<int>(aiProbability)) + "%)";
    } else {
        verdict = "Text appears predominantly human-written (" + std::to_string(static_cast<int>(aiProbability)) + "%)";
    }
    
    if (metrics.lexicalDiversity < 0.45) {
        interpretations.push_back("⚠️ Low lexical diversity - limited vocabulary variation");
    } else if (metrics.lexicalDiversity > 0.65) {
        interpretations.push_back("✓ High lexical diversity - rich vocabulary variation");
    }
    
    if (metrics.entropy < 5.0) {
        interpretations.push_back("⚠️ Low entropy - unnaturally uniform word distribution");
    } else if (metrics.entropy > 6.0) {
        interpretations.push_back("✓ Good entropy - natural word distribution");
    }
    
    if (metrics.burstiness < 0.35) {
        interpretations.push_back("⚠️ Low burstiness - overly uniform sentence structure");
    } else if (metrics.burstiness > 0.7) {
        interpretations.push_back("✓ Good burstiness - natural sentence variation");
    }
    
    if (metrics.aiPhraseHits > 0) {
        interpretations.push_back("⚠️ Found " + std::to_string(metrics.aiPhraseHits) + " AI-typical phrases");
    }
    
    if (metrics.patternRepetition > 0.35) {
        interpretations.push_back("⚠️ High pattern repetition - template-like structure");
    }
    
    if (metrics.unicodeSymbols > 0) {
        interpretations.push_back("⚠️ Found " + std::to_string(metrics.unicodeSymbols) + " suspicious Unicode characters");
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
                       bool removeWatermark, const std::string& lang) {
    
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
        
        auto [verdict, interpretations] = getInterpretation(*aiMetrics, aiResult->probability, aiResult->confidence);
        
        builder << "Overall Verdict: " << verdict << "\n";
        builder << "Confidence Level: " << aiResult->confidence << "\n";
        builder << "\n";
        
        builder << "Detailed Metrics:\n";
        builder << "  Word count:            " << aiMetrics->wordCount << "\n";
        builder << "  Sentence count:        " << aiMetrics->sentenceCount << "\n";
        builder << "  Lexical diversity:     " << std::fixed << std::setprecision(3) << aiMetrics->lexicalDiversity << "\n";
        builder << "  Repetition score:      " << std::fixed << std::setprecision(3) << aiMetrics->repetitionScore << "\n";
        builder << "  Entropy:               " << std::fixed << std::setprecision(3) << aiMetrics->entropy << "\n";
        builder << "  Burstiness:            " << std::fixed << std::setprecision(3) << aiMetrics->burstiness << "\n";
        builder << "  Pattern repetition:    " << std::fixed << std::setprecision(3) << aiMetrics->patternRepetition << "\n";
        builder << "  Punctuation density:   " << std::fixed << std::setprecision(3) << aiMetrics->punctuationDensity << "\n";
        builder << "  AI phrase hits:        " << aiMetrics->aiPhraseHits << "\n";
        builder << "  Unicode suspicious:    " << aiMetrics->unicodeSymbols << "\n";
        builder << "  Avg word length:       " << std::fixed << std::setprecision(2) << aiMetrics->avgWordLength << "\n";
        builder << "  Word length variance:  " << std::fixed << std::setprecision(2) << aiMetrics->wordLengthVariance << "\n";
        builder << "\n";
        
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
    auto end = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    
    // Calculate forensic metrics
    std::map<std::string, size_t> wordFreq;
    if (!noWords) {
        wordFreq = wordFrequency(result.cleaned);
    }
    
    AIMetrics* aiMetrics = calculateAIForensicMetrics(result.cleaned, wordFreq);
    AIResult* aiResult = nullptr;
    if (aiMetrics != nullptr) {
        aiResult = new AIResult(calculateAIProbability(*aiMetrics));
    }
    
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
            removeWatermark, "C++-Ext"
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
    }
    std::cout << "Output: " << (noEdit ? "(skipped)" : outputFile) << "\n";
    std::cout << "Report: " << (noReport ? "(skipped)" : reportFile) << "\n";
    
    // Cleanup
    delete aiMetrics;
    delete aiResult;
    
    return 0;
}
