#!/usr/bin/env bun
"use strict";

/**
 * aiparstxt-ext — Enhanced Text Sanitizer with AI Forensic Analysis
 * 
 * Enhanced version with:
 * - Extended AI watermark character detection
 * - Statistical AI pattern analysis  
 * - Probability-based AI detection scoring
 * - Advanced forensic reporting
 */

const fs = require("fs");
const path = require("path");

// =========================================================
// ENHANCED ALLOWED CHARACTERS
// =========================================================

const ALLOWED = new Set(
  "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" +
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" +
    "[]{}()-=_+!@#$%&*;'/.,<>'\"`~ \t\n\r".split("")
);

for (const ch of "ҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ—«»") ALLOWED.add(ch);
ALLOWED.add(":");
ALLOWED.delete("|");

// =========================================================
// ENHANCED AI WATERMARK CHARACTERS
// =========================================================

const WATERMARK_CHARS = new Set([
  // Core zero-width characters
  "\u200B", // Zero Width Space (ZWSP)
  "\u200C", // Zero Width Non-Joiner (ZWNJ)
  "\u200D", // Zero Width Joiner (ZWJ)
  "\uFEFF", // Zero Width No-Break Space (ZWNBSP, BOM)
  
  // Invisible formatting characters
  "\u00AD", // Soft Hyphen (SHY)
  "\u2060", // Word Joiner
  "\u2061", // Function Application
  "\u2062", // Invisible Times
  "\u2063", // Invisible Separator
  "\u2064", // Invisible Plus
  
  // Bidirectional control characters
  "\u202A", // Left-to-Right Embedding
  "\u202B", // Right-to-Left Embedding
  "\u202C", // Pop Directional Formatting
  "\u202D", // Left-to-Right Override
  "\u202E", // Right-to-Left Override
  
  // Separators
  "\u2028", // Line Separator
  "\u2029", // Paragraph Separator
  
  // Variation Selectors
  "\uFE00", "\uFE01", "\uFE02", "\uFE03", "\uFE04", "\uFE05", "\uFE06", "\uFE07",
  "\uFE08", "\uFE09", "\uFE0A", "\uFE0B", "\uFE0C", "\uFE0D", "\uFE0E", "\uFE0F",
  
  // Language and script tags
  "\uE0001", // Language Tag
  "\u180E",  // Mongolian Separator
  
  // Additional Unicode suspicious characters
  "\uFFF9", "\uFFFA", "\uFFFB", "\uFFFC", "\uFFFD", // Interlinear annotation
]);

// Tag characters and Private Use Areas
for (let cp = 0xE0020; cp < 0xE0080; cp++) {
  WATERMARK_CHARS.add(String.fromCharCode(cp));
}

for (let cp = 0xE000; cp < 0xE080; cp++) {
  WATERMARK_CHARS.add(String.fromCharCode(cp));
}

// =========================================================
// AI FORENSIC PATTERNS
// =========================================================

const UNICODE_SUSPICIOUS = [
  "\u2010", "\u2011", // Hyphen variants
  "\u2012", "\u2013", "\u2014", // Em-dash variants
  "\u2018", "\u2019", "\u201B", // Smart quotes
  "\u201C", "\u201D", "\u201E", "\u201F", // Smart double quotes
  "\u2026", // Ellipsis
  "\u202F", // Narrow no-break space
  "\u205F", // Medium mathematical space
  "\u00A0", // Non-breaking space
  "\u2000", "\u2001", "\u2002", "\u2003", "\u2004", "\u2005",
  "\u2006", "\u2007", "\u2008", "\u2009", "\u200A", // Space variants
];

const AI_PHRASES = [
  // Language model typical phrases
  "в заключение", "в целом", "важно отметить", "值得注意的是", "重要的是",
  "in conclusion", "in summary", "it is worth noting", "it is important to note",
  "综上所述", "总的来说", "值得注意的是", "总之", "basically", "essentially",
  "в самом деле", "в действительности", "в самом", "на самом деле",
  
  // Overused connectors
  "furthermore", "moreover", "additionally", "in addition",
  "более того", "кроме того", "следует отметить", "следует упомянуть",
  
  // Hedging language
  "it could be argued", "one might argue", "it appears that", "seems that",
  "можно утверждать", "можно сказать", "кажется", "по-видимому",
  
  // Generic transitions
  "on the other hand", "however", "nevertheless", "nonetheless",
  "с одной стороны", "с другой стороны", "однако", "тем не менее",
  
  // AI disclaimer patterns
  "as an ai", "as a language model", "i cannot", "i'm not able to",
  "как искусственный интеллект", "как языковая модель",
  
  // Over-structured patterns
  "first and foremost", "last but not least", "firstly", "secondly",
  "во-первых", "во-вторых", "в-третьих", "с одной стороны", "с другой стороны",
];

const STOPWORDS = new Set([
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
]);

// =========================================================
// TEXT PROCESSING FUNCTIONS
// =========================================================

function processText(text, replacement = "?", remove = false, removeWatermark = false) {
  const replaced = new Map();
  const watermarkRemoved = new Map();
  const out = [];

  for (const ch of text) {
    if (removeWatermark && WATERMARK_CHARS.has(ch)) {
      watermarkRemoved.set(ch, (watermarkRemoved.get(ch) || 0) + 1);
      continue;
    }

    if (ALLOWED.has(ch)) {
      out.push(ch);
    } else {
      if (remove) {
        continue;
      }
      out.push(replacement);
      replaced.set(ch, (replaced.get(ch) || 0) + 1);
    }
  }

  return { cleaned: out.join(""), replaced, watermarkRemoved };
}

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

function wordFrequency(text) {
  const freq = new Map();
  let currentWord = [];

  const processWord = () => {
    if (currentWord.length > 0) {
      const word = currentWord.join("").toLowerCase();
      if (word.length > 2 && !STOPWORDS.has(word)) {
        freq.set(word, (freq.get(word) || 0) + 1);
      }
      currentWord = [];
    }
  };

  for (const ch of text) {
    if (/[a-zA-Zа-яА-ЯёЁ]/.test(ch) || ch === "'") {
      currentWord.push(ch);
    } else {
      processWord();
    }
  }
  processWord();

  return freq;
}

function splitSentences(text) {
  const sentenceEndings = /[.!?]+[\s\n]+/;
  const sentences = text.split(sentenceEndings);
  return sentences.filter(s => s.trim().length > 3).map(s => s.trim());
}

function calculateAIForensicMetrics(text, wordFreq) {
  if (!text || text.length === 0) {
    return null;
  }

  const words = text.toLowerCase().match(/\b\w+\b/g) || [];
  const sentences = splitSentences(text);

  if (words.length === 0 || sentences.length === 0) {
    return null;
  }

  // Core metrics
  const wordCount = words.length;
  const sentenceCount = sentences.length;
  const uniqueWords = new Set(words).size;
  
  // Lexical diversity
  const lexicalDiv = uniqueWords / wordCount;
  
  // Convert Map to array for calculations
  const freqArray = Array.from(wordFreq.values());
  const repeated = freqArray.filter(count => count > 1).length;
  const repScore = repeated / freqArray.length || 0;
  
  // Entropy calculation
  const total = words.length;
  let entropy = 0;
  for (const [word, count] of wordFreq) {
    const p = count / total;
    entropy -= p * Math.log2(p);
  }
  
  // Sentence length analysis (burstiness)
  const sentLengths = sentences.map(s => (s.match(/\b\w+\b/g) || []).length);
  const avgSentLen = sentLengths.reduce((a, b) => a + b, 0) / sentLengths.length;
  const variance = sentLengths.reduce((sum, len) => sum + Math.pow(len - avgSentLen, 2), 0) / sentLengths.length;
  const burstiness = Math.sqrt(variance) / avgSentLen || 0;
  
  // Pattern repetition
  const categorizeLength = (length) => {
    if (length < 10) return 'S';
    if (length < 20) return 'M';
    return 'L';
  };
  
  const patterns = sentLengths.map(categorizeLength);
  const patternCounts = {};
  patterns.forEach(p => patternCounts[p] = (patternCounts[p] || 0) + 1);
  const repeatedPatterns = Object.values(patternCounts).filter(c => c > 1).length;
  const patternRep = repeatedPatterns / patterns.length;
  
  // Punctuation density
  const punctMatches = text.match(/[,.!?;:()\-\—–]/g) || [];
  const punctDensity = punctMatches.length / text.length;
  
  // AI phrase detection
  const textLower = text.toLowerCase();
  let aiHits = 0;
  for (const phrase of AI_PHRASES) {
    if (textLower.includes(phrase)) {
      aiHits++;
    }
  }
  
  // Unicode suspicious characters
  let unicodeCount = 0;
  for (const char of UNICODE_SUSPICIOUS) {
    if (text.includes(char)) {
      unicodeCount++;
    }
  }
  
  // Word length statistics
  const wordLengths = words.map(w => w.length);
  const avgWordLen = wordLengths.reduce((a, b) => a + b, 0) / wordLengths.length;
  const wordLenVariance = Math.sqrt(
    wordLengths.reduce((sum, len) => sum + Math.pow(len - avgWordLen, 2), 0) / wordLengths.length
  );

  return {
    word_count: wordCount,
    sentence_count: sentenceCount,
    lexical_diversity: lexicalDiv,
    repetition_score: repScore,
    entropy,
    burstiness,
    pattern_repetition: patternRep,
    punctuation_density: punctDensity,
    ai_phrase_hits: aiHits,
    unicode_symbols: unicodeCount,
    avg_word_length: avgWordLen,
    word_length_variance: wordLenVariance,
  };
}

function calculateAIProbability(metrics) {
  if (!metrics) {
    return { probability: 0, scores: {}, confidence: "LOW" };
  }

  const scores = {};
  let total = 0;

  // Core metrics with enhanced weighting
  if (metrics.lexical_diversity < 0.45) {
    scores.lexical_diversity = 25;
    total += 25;
  } else if (metrics.lexical_diversity < 0.55) {
    scores.lexical_diversity = 15;
    total += 15;
  }

  if (metrics.entropy < 5.0) {
    scores.entropy = 25;
    total += 25;
  } else if (metrics.entropy < 5.8) {
    scores.entropy = 15;
    total += 15;
  }

  if (metrics.burstiness < 0.35) {
    scores.burstiness = 20;
    total += 20;
  } else if (metrics.burstiness < 0.45) {
    scores.burstiness = 10;
    total += 10;
  }

  if (metrics.pattern_repetition > 0.35) {
    scores.pattern_repetition = 20;
    total += 20;
  } else if (metrics.pattern_repetition > 0.25) {
    scores.pattern_repetition = 10;
    total += 10;
  }

  if (metrics.ai_phrase_hits >= 3) {
    scores.ai_phrases = 20;
    total += 20;
  } else if (metrics.ai_phrase_hits >= 1) {
    scores.ai_phrases = 10;
    total += 10;
  }

  if (metrics.repetition_score > 0.5) {
    scores.repetition = 15;
    total += 15;
  }

  if (metrics.punctuation_density > 0.04) {
    scores.punctuation = 5;
    total += 5;
  }

  if (metrics.unicode_symbols > 0) {
    scores.unicode = 5;
    total += 5;
  }

  // Extended metrics
  if (metrics.avg_word_length < 4.0) {
    scores.word_length = 10;
    total += 10;
  } else if (metrics.avg_word_length < 4.5) {
    scores.word_length = 5;
    total += 5;
  }

  if (metrics.word_length_variance < 1.5) {
    scores.word_variance = 8;
    total += 8;
  }

  // Length-based confidence adjustment
  let confidenceFactor, confidence;
  if (metrics.word_count < 300) {
    confidenceFactor = 0.8;
    confidence = "LOW";
  } else if (metrics.word_count < 1000) {
    confidenceFactor = 0.9;
    confidence = "MEDIUM";
  } else {
    confidenceFactor = 1.0;
    confidence = "HIGH";
  }

  const adjustedTotal = total * confidenceFactor;
  const probability = Math.min(100, adjustedTotal);

  return { probability, scores, confidence };
}

function getInterpretation(metrics, aiProbability, confidence) {
  const interpretations = [];

  let verdict;
  if (aiProbability > 60) {
    verdict = `High probability of AI-generated content (${aiProbability.toFixed(1)}%)`;
  } else if (aiProbability > 30) {
    verdict = `Moderate probability of AI involvement (${aiProbability.toFixed(1)}%)`;
  } else if (aiProbability > 10) {
    verdict = `Low probability of AI-generated content (${aiProbability.toFixed(1)}%)`;
  } else {
    verdict = `Text appears predominantly human-written (${aiProbability.toFixed(1)}%)`;
  }

  if (metrics.lexical_diversity < 0.45) {
    interpretations.push("⚠️ Low lexical diversity - limited vocabulary variation");
  } else if (metrics.lexical_diversity > 0.65) {
    interpretations.push("✓ High lexical diversity - rich vocabulary variation");
  }

  if (metrics.entropy < 5.0) {
    interpretations.push("⚠️ Low entropy - unnaturally uniform word distribution");
  } else if (metrics.entropy > 6.0) {
    interpretations.push("✓ Good entropy - natural word distribution");
  }

  if (metrics.burstiness < 0.35) {
    interpretations.push("⚠️ Low burstiness - overly uniform sentence structure");
  } else if (metrics.burstiness > 0.7) {
    interpretations.push("✓ Good burstiness - natural sentence variation");
  }

  if (metrics.ai_phrase_hits > 0) {
    interpretations.push(`⚠️ Found ${metrics.ai_phrase_hits} AI-typical phrases`);
  }

  if (metrics.pattern_repetition > 0.35) {
    interpretations.push("⚠️ High pattern repetition - template-like structure");
  }

  if (metrics.unicode_symbols > 0) {
    interpretations.push(`⚠️ Found ${metrics.unicode_symbols} suspicious Unicode characters`);
  }

  return { verdict, interpretations };
}

// =========================================================
// REPORTING FUNCTIONS
// =========================================================

function buildReport(inputFile, outputFile, replaced, watermarkRemoved, wordFreq, elapsed, aiMetrics, aiResult, lang = "Bun-Ext") {
  const lines = [];

  // Header
  lines.push("=".repeat(70));
  lines.push("aiparstxt-ext — Enhanced AI Forensic Analyzer Report");
  lines.push(`Language: ${lang}`);
  lines.push("=".repeat(70));
  lines.push("");

  // Basic info
  lines.push(`Input file:  ${inputFile}`);
  lines.push(`Output file: ${outputFile}`);
  lines.push(`Execution time: ${elapsed.toFixed(6)}s`);
  lines.push("");

  // Watermark analysis
  lines.push("--- AI Watermark Analysis ---");
  let totalWatermark = 0;
  for (const count of watermarkRemoved.values()) {
    totalWatermark += count;
  }
  lines.push(`Watermark characters removed: ${totalWatermark}`);
  
  if (totalWatermark > 0) {
    lines.push("Removed watermark character types:");
    const sorted = Array.from(watermarkRemoved.entries()).sort((a, b) => b[1] - a[1]);
    for (const [char, count] of sorted.slice(0, 20)) {
      const codePoint = `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, "0")}`;
      lines.push(`  ${codePoint}: ${count}`);
    }
    if (sorted.length > 20) {
      lines.push(`  ... and ${sorted.length - 20} more types`);
    }
  } else {
    lines.push("No AI watermark characters detected");
  }
  lines.push("");

  // Replaced characters
  lines.push("--- Replaced Characters ---");
  let totalReplaced = 0;
  for (const count of replaced.values()) {
    totalReplaced += count;
  }
  lines.push(`Characters replaced: ${totalReplaced}`);
  
  if (totalReplaced > 0) {
    lines.push("Replaced character types:");
    const sorted = Array.from(replaced.entries()).sort((a, b) => b[1] - a[1]).slice(0, 10);
    for (const [char, count] of sorted) {
      const codePoint = `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, "0")}`;
      lines.push(`  ${codePoint}: ${count}`);
    }
    if (replaced.size > 10) {
      lines.push(`  ... and ${replaced.size - 10} more types`);
    }
  } else {
    lines.push("No characters replaced");
  }
  lines.push("");

  // AI Forensic Analysis
  if (aiMetrics && aiResult) {
    lines.push("=".repeat(70));
    lines.push("AI FORENSIC ANALYSIS");
    lines.push("=".repeat(70));
    lines.push("");

    const { verdict, interpretations } = getInterpretation(aiMetrics, aiResult.probability, aiResult.confidence);

    lines.push(`Overall Verdict: ${verdict}`);
    lines.push(`Confidence Level: ${aiResult.confidence}`);
    lines.push("");

    lines.push("Detailed Metrics:");
    lines.push(`  Word count:            ${aiMetrics.word_count}`);
    lines.push(`  Sentence count:        ${aiMetrics.sentence_count}`);
    lines.push(`  Lexical diversity:     ${aiMetrics.lexical_diversity.toFixed(3)}`);
    lines.push(`  Repetition score:      ${aiMetrics.repetition_score.toFixed(3)}`);
    lines.push(`  Entropy:               ${aiMetrics.entropy.toFixed(3)}`);
    lines.push(`  Burstiness:            ${aiMetrics.burstiness.toFixed(3)}`);
    lines.push(`  Pattern repetition:    ${aiMetrics.pattern_repetition.toFixed(3)}`);
    lines.push(`  Punctuation density:   ${aiMetrics.punctuation_density.toFixed(3)}`);
    lines.push(`  AI phrase hits:        ${aiMetrics.ai_phrase_hits}`);
    lines.push(`  Unicode suspicious:    ${aiMetrics.unicode_symbols}`);
    lines.push(`  Avg word length:       ${aiMetrics.avg_word_length.toFixed(2)}`);
    lines.push(`  Word length variance:  ${aiMetrics.word_length_variance.toFixed(2)}`);
    lines.push("");

    if (interpretations.length > 0) {
      lines.push("Signal Analysis:");
      for (const interp of interpretations) {
        lines.push(`  ${interp}`);
      }
      lines.push("");
    }

    lines.push("=".repeat(70));
    lines.push("");
  }

  // Word frequency
  lines.push("--- Top Word Frequencies (Filtered) ---");
  if (wordFreq && wordFreq.size > 0) {
    const sorted = Array.from(wordFreq.entries()).sort((a, b) => b[1] - a[1]).slice(0, 20);
    for (const [word, count] of sorted) {
      lines.push(`  ${word}: ${count}`);
    }
  } else {
    lines.push("(skipped)");
  }

  return lines.join("\n") + "\n";
}

// =========================================================
// CLI INTERFACE
// =========================================================

function parseArgs(argv) {
  const args = {
    inputFile: null,
    outputFile: null,
    reportFile: null,
    noEdit: false,
    noReport: false,
    noWords: false,
    removeWatermark: false,
    replacement: "?",
    remove: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "-o":
      case "--output":
        args.outputFile = argv[++i];
        break;
      case "-r":
      case "--report":
        args.reportFile = argv[++i];
        break;
      case "--no-edit":
        args.noEdit = true;
        break;
      case "--no-report":
        args.noReport = true;
        break;
      case "--no-words":
        args.noWords = true;
        break;
      case "--remove-watermark":
        args.removeWatermark = true;
        break;
      case "--replacement":
        args.replacement = argv[++i];
        break;
      case "--remove":
        args.remove = true;
        break;
      default:
        if (!arg.startsWith("-")) {
          args.inputFile = arg;
        }
    }
  }

  return args;
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.inputFile) {
    console.error("Error: No input file specified");
    process.exit(1);
  }

  // Set default paths
  const inputPath = args.inputFile;
  const defaultOutput = inputPath.replace(/\.[^.]+$/, ".ed.txt");
  const defaultReport = "report_bun-ext.txt";

  const outputFile = args.outputFile || defaultOutput;
  const reportFile = args.reportFile || defaultReport;

  // Read input file
  let text;
  try {
    text = fs.readFileSync(inputPath, "utf8");
  } catch (e) {
    console.error(`Error reading ${inputPath}: ${e.message}`);
    process.exit(1);
  }

  // Process text
  const startTime = Date.now();
  const { cleaned, replaced, watermarkRemoved } = processText(
    text,
    args.replacement,
    args.remove,
    args.removeWatermark
  );

  // Calculate forensic metrics
  let aiMetrics = null;
  let aiResult = null;
  let wordFreq = null;

  if (cleaned && cleaned.length > 0) {
    wordFreq = args.noWords ? null : wordFrequency(cleaned);
    aiMetrics = calculateAIForensicMetrics(cleaned, wordFreq || new Map());
    if (aiMetrics) {
      aiResult = calculateAIProbability(aiMetrics);
    }
  }

  const elapsed = (Date.now() - startTime) / 1000;

  // Write output file
  if (!args.noEdit) {
    try {
      fs.writeFileSync(outputFile, cleaned, "utf8");
    } catch (e) {
      console.error(`Error writing ${outputFile}: ${e.message}`);
    }
  }

  // Generate and write report
  if (!args.noReport) {
    const reportContent = buildReport(
      inputFile,
      outputFile,
      replaced,
      watermarkRemoved,
      wordFreq,
      elapsed,
      aiMetrics,
      aiResult
    );
    try {
      fs.writeFileSync(reportFile, reportContent, "utf8");
    } catch (e) {
      console.error(`Error writing ${reportFile}: ${e.message}`);
    }
  }

  // Print summary
  console.log(`Processed in ${elapsed.toFixed(6)}s`);
  console.log(`Replacements: ${Array.from(replaced.values()).reduce((a, b) => a + b, 0)}`);
  console.log(`Watermarks removed: ${Array.from(watermarkRemoved.values()).reduce((a, b) => a + b, 0)}`);
  if (aiResult) {
    console.log(`AI Probability: ${aiResult.probability.toFixed(1)}% (confidence: ${aiResult.confidence})`);
  }
  console.log(`Output: ${args.noEdit ? "(skipped)" : outputFile}`);
  console.log(`Report: ${args.noReport ? "(skipped)" : reportFile}`);
}

main();
