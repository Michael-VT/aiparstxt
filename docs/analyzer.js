
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
// AI FORENSIC PATTERNS (v0.4.0 — canonical, see AI_SIGNALS_SPEC.md)
// =========================================================

// Suspicious Unicode characters - aligned with the parscgpt-ext.py reference
const UNICODE_SUSPICIOUS = [
  "—", "–", "“", "”", "‘", "’",
  "…", "•", "→", "←", "↑", "↓",
  "©", "®", "™", "°", "±", "×", "÷",
];

// AI-typical phrases: tiered multilingual database (v0.4.0).
// Canonical source: parscgpt-ext.py / AI_SIGNALS_SPEC.md.
// HIGH   - distinctive LLM template phrases, zero hits in human validation corpus
// MEDIUM - typical AI connective/register markers, rare in human corpus
// WEAK   - markers that also occur in human prose; evidence-only, tiny weight
const AI_PHRASES = {
  high: [
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
  ],
  medium: [
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
  ],
  weak: [
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
  ],
};

// Discourse connectives (all languages merged); used for connective_density.
const CONNECTIVES = [
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
const SENT_CV_TIERS = [[0.30, 32], [0.35, 26], [0.40, 19], [0.45, 11], [0.50, 5]];
const PARA_CV_TIERS = [[0.15, 28], [0.25, 22], [0.35, 16], [0.45, 7]];
const JOINT_CV_TIERS = [[0.40, 14], [0.45, 10]];
const HIGH_PHRASE_SCORES = [24, 15];   // (>=2 hits, ==1 hit)
const MEDIUM_PHRASE_SCORES = [10, 5];  // (>=3 hits, >=1 hit)
const WEAK_PHRASE_SCORE = 4;           // >=4 hits
const CONNECTIVE_TIERS = [[0.12, 13], [0.08, 7]];
// Template header repetition: verbatim-repeated short non-punctuated lines
// ("Что верно" x7 etc.) - structured LLM answers reuse section templates.
// Zero hits in the human validation corpus.
const TEMPLATE_HEADER_MIN_REPEATS = 3;
const TEMPLATE_HEADER_SCORES = [14, 8];  // (>=2 distinct templates or >=10 repeats, >=3 repeats)
// Guards: CV signals are unreliable on tiny texts. Instead of a hard cutoff
// (which silently made short AI texts score as "human"), tier points are
// scaled by statistical reliability: min(1, n/SENT_CV_FULL_SENTENCES) etc.
const SENT_CV_MIN_SENTENCES = 5;    // below this, sentence CV is pure noise -> 0
const SENT_CV_FULL_SENTENCES = 15;  // full weight from this many sentences on
const PARA_CV_MIN_PARAGRAPHS = 3;   // below this, paragraph CV is not computed
const PARA_CV_FULL_PARAGRAPHS = 4;
const MIN_WORDS_FOR_CV = 40;
const FULL_WORDS_FOR_CV = 150;

// Passive voice patterns (reference basis for passive_voice_density)
const AI_PASSIVE_PATTERNS = [
  "is considered to be", "are considered to be",
  "is often said to be", "are often said to be",
  "is generally regarded as", "are generally regarded as",
  "is typically characterized by", "are typically characterized by",
  "is commonly associated with", "are commonly associated with",
  "is widely recognized as", "are widely recognized as",
  "is frequently observed to", "are frequently observed to",
  "is usually understood to", "are usually understood to",
];

const STOPWORDS = new Set([
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

// Count non-overlapping substring occurrences (Python str.count semantics)
function countOccurrences(haystack, needle) {
  if (!needle) return 0;
  let count = 0;
  let idx = haystack.indexOf(needle);
  while (idx !== -1) {
    count++;
    idx = haystack.indexOf(needle, idx + needle.length);
  }
  return count;
}

// Whitespace word count (Python len(s.split()) semantics)
function wsWordCount(s) {
  const t = s.trim();
  if (!t) return 0;
  return t.split(/\s+/).length;
}

function splitSentences(text) {
  const masked = text.replace(/\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\./g, "$1<DOT>");
  return masked
    .split(/[.!?]+/)
    .map((s) => s.trim().replace(/<DOT>/g, "."))
    .filter((s) => s.length > 3);
}

function calculateAIForensicMetrics(text) {
  if (!text || text.length === 0) {
    return null;
  }

  // Python reference: re.findall(r'\b\w+\b', text.lower()) — unicode-aware
  const words = text.toLowerCase().match(/[\p{L}\p{N}_]+/gu) || [];
  const sentences = splitSentences(text);

  if (words.length === 0 || sentences.length === 0) {
    return null;
  }

  // Filtered words (reference basis for diversity/entropy/repetition)
  const filtered = words.filter((w) => !STOPWORDS.has(w) && w.length > 2);
  const filteredCounter = new Map();
  for (const w of filtered) {
    filteredCounter.set(w, (filteredCounter.get(w) || 0) + 1);
  }

  // Core metrics
  const wordCount = words.length;
  const sentenceCount = sentences.length;

  // Lexical diversity (on filtered words, as in reference)
  const lexicalDiv = filtered.length ? filteredCounter.size / filtered.length : 0;

  // Repetition score (distinct repeated filtered words / filtered words)
  let repeated = 0;
  for (const count of filteredCounter.values()) {
    if (count > 1) repeated++;
  }
  const repScore = filtered.length ? repeated / filtered.length : 0;

  // Entropy calculation (on filtered words, as in reference)
  let entropy = 0;
  if (filtered.length > 0) {
    for (const count of filteredCounter.values()) {
      const p = count / filtered.length;
      entropy -= p * Math.log2(p);
    }
  }

  // Sentence length analysis (burstiness = CV of sentence word counts);
  // word count per sentence uses whitespace split, as in the reference
  const sentLengths = sentences.map(wsWordCount);
  const avgSentLen =
    sentLengths.reduce((a, b) => a + b, 0) / (sentLengths.length || 1);
  let burstiness = 0;
  if (avgSentLen > 0 && sentLengths.length > 1) {
    const variance =
      sentLengths.reduce((sum, len) => sum + Math.pow(len - avgSentLen, 2), 0) /
      sentLengths.length;
    burstiness = Math.sqrt(variance) / avgSentLen;
  }

  // Paragraph length uniformity (CV of paragraph word counts)
  const paragraphs = text
    .split(/\n\s*\n/)
    .filter((p) => wsWordCount(p) > 15);
  const paraLengths = paragraphs.map(wsWordCount);
  let paraCv = null;
  if (paraLengths.length >= PARA_CV_MIN_PARAGRAPHS) {
    const paraAvg = paraLengths.reduce((a, b) => a + b, 0) / paraLengths.length;
    if (paraAvg > 0) {
      const pv =
        paraLengths.reduce((sum, len) => sum + Math.pow(len - paraAvg, 2), 0) /
        paraLengths.length;
      paraCv = Math.sqrt(pv) / paraAvg;
    } else {
      paraCv = 0;
    }
  }
  const paraCount =
    paraLengths.length >= PARA_CV_MIN_PARAGRAPHS ? paraLengths.length : 0;

  // Pattern repetition
  const categorizeLength = (length) => {
    if (length <= 10) return "S";
    if (length <= 20) return "M";
    return "L";
  };

  const patterns = sentLengths.map(categorizeLength);
  const patternCounts = {};
  patterns.forEach((p) => (patternCounts[p] = (patternCounts[p] || 0) + 1));
  const repeatedPatterns = Object.values(patternCounts).filter((c) => c > 1).length;
  const patternRep = patterns.length ? repeatedPatterns / patterns.length : 0;

  // Punctuation density (reference regex)
  const punctMatches = text.match(/[,;:()\-—–]/g) || [];
  const punctDensity = text.length ? punctMatches.length / text.length : 0;

  // AI phrase detection (tiered, with occurrences for evidence)
  const textLower = text.toLowerCase();
  let aiHits = 0;
  const phraseTiers = { high: 0, medium: 0, weak: 0 };
  const phraseOccurrences = [];
  for (const tier of ["high", "medium", "weak"]) {
    for (const phrase of AI_PHRASES[tier]) {
      const found = countOccurrences(textLower, phrase);
      if (found) {
        aiHits++;
        phraseTiers[tier] += found;
        let idx = textLower.indexOf(phrase);
        for (let k = 0; k < Math.min(found, 3); k++) {
          phraseOccurrences.push([tier, phrase, idx]);
          idx = textLower.indexOf(phrase, idx + phrase.length);
        }
      }
    }
  }

  // Connective density (connectives per sentence)
  let connTotal = 0;
  for (const s of sentences) {
    const sLower = s.toLowerCase();
    for (const c of CONNECTIVES) {
      if (sLower.includes(c)) connTotal++;
    }
  }
  const connectiveDensity = sentences.length ? connTotal / sentences.length : 0;

  // Template header repetition (structured-answer genre)
  const lineCounter = new Map();
  const firstLineNo = new Map();
  const headerEndPunct = ".!?:;,…\"»„";
  const rawLines = text.split("\n");
  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i].trim();
    const chars = Array.from(line);
    const lineWords = line ? line.split(/\s+/).length : 0;
    if (
      chars.length >= 4 && chars.length <= 60 &&
      lineWords >= 1 && lineWords <= 8 &&
      !headerEndPunct.includes(chars[chars.length - 1]) &&
      !/[0-9]/.test(chars[0])
    ) {
      lineCounter.set(line, (lineCounter.get(line) || 0) + 1);
      if (!firstLineNo.has(line)) firstLineNo.set(line, i + 1);
    }
  }
  const tmplOccurrences = [];
  let tmplTotal = 0;
  let tmplDistinct = 0;
  for (const [line, count] of lineCounter) {
    if (count >= TEMPLATE_HEADER_MIN_REPEATS) {
      tmplTotal += count;
      tmplDistinct++;
      tmplOccurrences.push([line, count, firstLineNo.get(line)]);
    }
  }
  tmplOccurrences.sort((a, b) => b[1] - a[1]);

  // Unicode suspicious characters - count in the ORIGINAL (pre-sanitization)
  // text, matching the reference analyzer
  let unicodeCount = 0;
  for (const char of UNICODE_SUSPICIOUS) {
    if (text.includes(char)) unicodeCount++;
  }

  // Word length statistics
  const wordLengths = words.map((w) => w.length);
  const avgWordLen = wordLengths.reduce((a, b) => a + b, 0) / wordLengths.length;
  let wordLenVariance = 0;
  if (wordLengths.length > 1) {
    // sample stdev (n-1), like Python statistics.stdev
    const v =
      wordLengths.reduce((sum, len) => sum + Math.pow(len - avgWordLen, 2), 0) /
      (wordLengths.length - 1);
    wordLenVariance = Math.sqrt(v);
  }

  // --- Supporting metrics (mirror parscgpt-ext.py reference) ---
  // Pronoun ratio
  const pronounLists = [
    ["i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"],
    ["you", "your", "yours", "yourself", "yourselves"],
    ["he", "him", "his", "himself", "she", "her", "hers", "herself",
      "it", "its", "itself", "they", "them", "their", "theirs", "themselves"],
    ["this", "that", "these", "those"],
    ["anyone", "anything", "everyone", "everything", "someone", "something",
      "noone", "nothing", "each", "every", "either", "neither", "both", "few",
      "many", "several"],
  ];
  const allPronouns = new Set([].concat(...pronounLists));
  let pronounMatches = 0;
  for (const w of words) {
    if (allPronouns.has(w)) pronounMatches++;
  }
  const pronounRatio = wordCount ? pronounMatches / wordCount : 0;

  // Readability (Flesch, simplified syllables)
  let syllableCount = 0;
  for (const w of words) {
    let vowels = 0;
    for (const ch of w) {
      if ("aeiouy".includes(ch)) vowels++;
    }
    syllableCount += Math.max(1, vowels);
  }
  const avgSentenceLength = sentenceCount ? wordCount / sentenceCount : 0;
  const avgSyllablesPerWord = wordCount ? syllableCount / wordCount : 0;
  const flesch = 206.835 - 1.015 * avgSentenceLength - 84.6 * avgSyllablesPerWord;
  const readability = Math.max(0, Math.min(100, flesch));

  // Passive voice density
  let passiveCount = 0;
  for (const p of AI_PASSIVE_PATTERNS) {
    passiveCount += countOccurrences(textLower, p);
  }
  const passiveDensity = passiveCount / Math.max(wsWordCount(text), 1);

  // Adjective-noun pair diversity
  const adjIndicators = ["al", "ble", "cal", "ful", "ic", "ive", "less", "ous"];
  const nounIndicators = ["er", "ism", "ment", "ness", "tion", "ship", "cy", "dom"];
  const adjectives = new Set(
    words.filter((w) => adjIndicators.some((ind) => w.endsWith(ind)))
  );
  const nouns = new Set(
    words.filter((w) => nounIndicators.some((ind) => w.endsWith(ind)))
  );
  const pairs = new Set();
  for (let i = 0; i < words.length - 1; i++) {
    if (adjectives.has(words[i]) && nouns.has(words[i + 1])) {
      pairs.add(`${words[i]} ${words[i + 1]}`);
    }
  }
  const totalPossible =
    adjectives.size && nouns.size ? adjectives.size * nouns.size : 1;
  const adjNounDiv = pairs.size / totalPossible;

  // Structural uniformity (repeated 2-word sentence starts)
  const starts = [];
  for (const s of sentences) {
    const ws = s.trim().split(/\s+/).filter(Boolean);
    if (ws.length) starts.push(ws.slice(0, 2).join(" ").toLowerCase());
  }
  const startCounts = new Map();
  for (const st of starts) startCounts.set(st, (startCounts.get(st) || 0) + 1);
  let repeatedStarts = 0;
  for (const count of startCounts.values()) {
    if (count > 1) repeatedStarts++;
  }
  const structUnif = sentenceCount ? repeatedStarts / sentenceCount : 0;

  // Quantifier overuse
  const quantifiers = [
    "relatively", "somewhat", "quite", "rather", "fairly",
    "reasonably", "comparatively", "moderately", "substantially",
    "considerably", "significantly", "notably", "remarkably",
  ];
  let quantCount = 0;
  for (const q of quantifiers) {
    quantCount += countOccurrences(textLower, q);
  }
  const quantOveruse = quantCount / Math.max(wsWordCount(text), 1);

  // Promotional/social-media register (genre abstention, NOT an AI score:
  // both AI hype posts and human SMM copy trigger this)
  let promoEmoji = 0;
  for (const ch of text) {
    if (ch.codePointAt(0) >= 0x2600) promoEmoji++;
  }
  const promoExcl = wordCount ? countOccurrences(text, "!") / wordCount : 0;
  const promo = promoEmoji >= 5 && promoExcl >= 0.02;

  return {
    word_count: wordCount,
    sentence_count: sentenceCount,
    lexical_diversity: lexicalDiv,
    repetition_score: repScore,
    entropy,
    burstiness,
    paragraph_uniformity_cv: paraCv,
    paragraph_count: paraCount,
    pattern_repetition: patternRep,
    punctuation_density: punctDensity,
    ai_phrase_hits: aiHits,
    ai_phrase_tiers: phraseTiers,
    ai_phrase_occurrences: phraseOccurrences,
    connective_density: connectiveDensity,
    template_header_repetition: { total: tmplTotal, distinct: tmplDistinct },
    promotional_register: promo,
    template_header_occurrences: tmplOccurrences,
    sentences,
    unicode_symbols: unicodeCount,
    avg_word_length: avgWordLen,
    word_length_variance: wordLenVariance,
    pronoun_ratio: pronounRatio,
    readability_score: readability,
    passive_voice_density: passiveDensity,
    adj_noun_pair_diversity: adjNounDiv,
    structural_uniformity: structUnif,
    quantifier_overuse: quantOveruse,
  };
}

function calculateAIProbability(metrics) {
  if (!metrics) {
    return { probability: 0, scores: {}, confidence: null };
  }

  const scores = {};
  let total = 0;

  const add = (name, points) => {
    if (points > 0) {
      scores[name] = points;
      total += points;
    }
  };

  // --- Primary structural signals ---
  // Tier points are scaled by statistical reliability of the sample
  // (short texts get partial credit instead of a silent zero).
  const sentCv = metrics.burstiness;
  const sentScale =
    Math.min(1, metrics.sentence_count / SENT_CV_FULL_SENTENCES) *
    Math.min(1, metrics.word_count / FULL_WORDS_FOR_CV);
  let sentCvPoints = 0;
  if (metrics.sentence_count >= SENT_CV_MIN_SENTENCES && metrics.word_count >= MIN_WORDS_FOR_CV) {
    for (const [threshold, points] of SENT_CV_TIERS) {
      if (sentCv < threshold) {
        sentCvPoints = Math.round(points * sentScale);
        break;
      }
    }
  }
  add("sentence_cv", sentCvPoints);

  const paraCv = metrics.paragraph_uniformity_cv;
  let paraPoints = 0;
  let paraScale = 0;
  if (paraCv !== null && paraCv !== undefined) {
    const paraCountForScale =
      metrics.paragraph_count !== null && metrics.paragraph_count !== undefined
        ? metrics.paragraph_count
        : PARA_CV_FULL_PARAGRAPHS;
    paraScale = Math.min(1, paraCountForScale / PARA_CV_FULL_PARAGRAPHS);
    for (const [threshold, points] of PARA_CV_TIERS) {
      if (paraCv < threshold) {
        paraPoints = Math.round(points * paraScale);
        break;
      }
    }
  }
  add("paragraph_cv", paraPoints);

  if (paraCv !== null && paraCv !== undefined && sentCvPoints > 0) {
    for (const [threshold, points] of JOINT_CV_TIERS) {
      if (sentCv < threshold && paraCv < threshold) {
        add("joint_uniformity", Math.round(points * Math.min(sentScale, paraScale)));
        break;
      }
    }
  }

  // --- Tiered phrase scores ---
  const tiers = metrics.ai_phrase_tiers;
  if (tiers.high >= 2) {
    add("ai_phrases", HIGH_PHRASE_SCORES[0]);
  } else if (tiers.high === 1) {
    add("ai_phrases", HIGH_PHRASE_SCORES[1]);
  } else if (tiers.medium >= 3) {
    add("ai_phrases", MEDIUM_PHRASE_SCORES[0]);
  } else if (tiers.medium >= 1) {
    add("ai_phrases", MEDIUM_PHRASE_SCORES[1]);
  } else if (tiers.weak >= 4) {
    add("ai_phrases", WEAK_PHRASE_SCORE);
  }

  // --- Connective density ---
  for (const [threshold, points] of CONNECTIVE_TIERS) {
    if (metrics.connective_density >= threshold) {
      add("connectives", points);
      break;
    }
  }

  // --- Template header repetition (structured-answer genre) ---
  const tmpl = metrics.template_header_repetition || { total: 0, distinct: 0 };
  if (tmpl.distinct >= 2 || tmpl.total >= 10) {
    add("template_headers", TEMPLATE_HEADER_SCORES[0]);
  } else if (tmpl.total >= TEMPLATE_HEADER_MIN_REPEATS) {
    add("template_headers", TEMPLATE_HEADER_SCORES[1]);
  }

  // --- Supporting statistical metrics ---
  if (metrics.lexical_diversity < 0.45) {
    add("lexical_diversity", 15);
  } else if (metrics.lexical_diversity < 0.55) {
    add("lexical_diversity", 8);
  }

  if (metrics.entropy < 5.0) {
    add("entropy", 15);
  } else if (metrics.entropy < 6.5) {
    add("entropy", 8);
  }

  if (metrics.pattern_repetition > 0.35) {
    add("pattern_repetition", 10);
  }

  if (metrics.repetition_score > 0.5) {
    add("repetition", 8);
  }

  if (metrics.punctuation_density > 0.04) {
    add("punctuation", 4);
  }

  if (metrics.unicode_symbols > 0) {
    add("unicode", 4);
  }

  if (metrics.avg_word_length < 4.0) {
    add("avg_word_length", 5);
  } else if (metrics.avg_word_length < 4.5) {
    add("avg_word_length", 3);
  }

  if (metrics.word_length_variance < 1.5) {
    add("word_length_variance", 4);
  }

  if (metrics.pronoun_ratio > 0.15) {
    add("pronoun_ratio", 4);
  }

  if (metrics.readability_score > 70) {
    add("readability", 5);
  } else if (metrics.readability_score > 60) {
    add("readability", 3);
  }

  if (metrics.passive_voice_density > 0.05) {
    add("passive_voice", 4);
  }

  if (metrics.adj_noun_pair_diversity < 0.3) {
    add("adj_noun_diversity", 3);
  }

  if (metrics.structural_uniformity > 0.4) {
    add("structural_uniformity", 4);
  }

  if (metrics.quantifier_overuse > 0.02) {
    add("quantifier_overuse", 3);
  }

  // Length-based confidence adjustment
  const wordCount = metrics.word_count;
  let confidence;
  if (wordCount < 300) {
    confidence = "LOW";
  } else if (wordCount < 1000) {
    confidence = "MEDIUM";
  } else {
    confidence = "HIGH";
  }

  const lengthFactor = Math.min(1.0, wordCount / 1000);
  const adjustedTotal = total * (0.9 + 0.1 * lengthFactor);
  const probability = Math.min(100, adjustedTotal);

  return { probability, scores, confidence };
}

function getInterpretation(metrics, aiProbability) {
  const interpretations = [];

  let verdict;
  if (aiProbability > 70) {
    verdict = `Strong AI-like statistical profile (${aiProbability.toFixed(1)}%)`;
  } else if (aiProbability > 55) {
    verdict = `Probable AI-generated text with multiple indicators (${aiProbability.toFixed(1)}%)`;
  } else if (aiProbability > 35) {
    verdict = `Mixed profile: human-like and AI-like signals (${aiProbability.toFixed(1)}%)`;
  } else {
    verdict = `Text statistically appears more human-like (${aiProbability.toFixed(1)}%)`;
  }

  // Honest abstention: below the structural-signal horizon the "human-like"
  // verdict would be an artifact of missing data, not evidence.
  if ((metrics.word_count || 0) < 150 || (metrics.sentence_count || 0) < 5) {
    verdict += " NOTE: text is too short for reliable structural analysis — this verdict is unreliable, not evidence of human authorship.";
  }

  // Genre abstention: promotional/social register - verdict withdrawn, no AI points
  if (metrics.promotional_register) {
    verdict += " NOTE: promotional/social-media register (emoji- and exclamation-heavy) is outside the calibration corpus — this verdict is unreliable for this genre.";
  }

  if (metrics.burstiness < 0.35) {
    interpretations.push("⚠️ Uniform sentence lengths (low burstiness) - strong AI signal");
  } else if (metrics.burstiness < 0.45) {
    interpretations.push("⚠️ Somewhat uniform sentence lengths - AI-like");
  }

  const paraCv = metrics.paragraph_uniformity_cv;
  if (paraCv !== null && paraCv !== undefined && paraCv < 0.35) {
    interpretations.push("⚠️ Uniform paragraph lengths - AI-like");
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

  const tiers = metrics.ai_phrase_tiers;
  if (tiers && (tiers.high || tiers.medium)) {
    interpretations.push(
      `⚠️ AI phrases: high=${tiers.high}, medium=${tiers.medium}`
    );
  }

  if (metrics.connective_density >= 0.12) {
    interpretations.push("⚠️ High discourse-connective density");
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
// EVIDENCE FUNCTIONS
// =========================================================

function truncateMiddle(s, width = 110) {
  if (s.length <= width) return s;
  const half = Math.floor(width / 2) - 5;
  return s.slice(0, half) + " ... " + s.slice(s.length - half);
}

function countNewlinesBefore(text, idx) {
  let n = 0;
  for (let i = 0; i < idx; i++) {
    if (text[i] === "\n") n++;
  }
  return n;
}

function buildEvidence(text, metrics) {
  const evidence = [];
  const sentences = metrics.sentences || [];
  const occurrences = metrics.ai_phrase_occurrences || [];

  const excerptFor = (idx, phrase) => {
    const sentStart =
      Math.max(
        text.lastIndexOf(". ", idx - 1),
        text.lastIndexOf("! ", idx - 1),
        text.lastIndexOf("? ", idx - 1),
        text.lastIndexOf("\n", idx - 1)
      ) + 1;
    const ends = [
      text.indexOf(". ", idx),
      text.indexOf("! ", idx),
      text.indexOf("? ", idx),
      text.indexOf("\n", idx),
    ].filter((p) => p !== -1);
    ends.push(text.length);
    const sentEnd = Math.min(...ends);
    let fragment = text.slice(sentStart, sentEnd).trim();
    const fLower = fragment.toLowerCase();
    let pos = fLower.indexOf(phrase);
    if (pos === -1) {
      return truncateMiddle(fragment);
    }
    if (fragment.length > 110) {
      const wLeft = 45;
      const wRight = 60;
      const start = Math.max(0, pos - wLeft);
      const end = Math.min(fragment.length, pos + phrase.length + wRight);
      const prefix = start > 0 ? "... " : "";
      const suffix = end < fragment.length ? " ..." : "";
      fragment = prefix + fragment.slice(start, end) + suffix;
      pos = pos - start + prefix.length;
    }
    return (
      fragment.slice(0, pos) +
      ">>>" +
      fragment.slice(pos, pos + phrase.length) +
      "<<<" +
      fragment.slice(pos + phrase.length)
    );
  };

  // 1. Phrase hits with locations (high tier first)
  const tierOrder = { high: 0, medium: 1, weak: 2 };
  const tierLabel = { high: "HIGH-risk", medium: "typical", weak: "weak" };
  const sortedOccurrences = occurrences
    .slice()
    .sort((a, b) => tierOrder[a[0]] - tierOrder[b[0]]);
  let shown = 0;
  for (const [tier, phrase, idx] of sortedOccurrences) {
    if (shown >= 10) break;
    evidence.push({
      type: "phrase",
      detail: `${tierLabel[tier]} AI phrase '${phrase}'`,
      line: countNewlinesBefore(text, idx) + 1,
      excerpt: excerptFor(idx, phrase),
    });
    shown++;
  }

  // 1b. Repeated template headers (structured-answer genre)
  const tmplOcc = metrics.template_header_occurrences || [];
  for (const [line, count, lineNo] of tmplOcc.slice(0, 4)) {
    evidence.push({
      type: "template",
      detail: `repeated template header '${line}' ×${count}`,
      line: lineNo,
      excerpt: null,
    });
  }

  // 2. Sentence-length uniformity
  const sentCv = metrics.burstiness;
  if (sentCv < 0.5 && metrics.word_count >= MIN_WORDS_FOR_CV) {
    const lengths = sentences
      .filter((s) => wsWordCount(s) > 0)
      .map((s) => wsWordCount(s));
    evidence.push({
      type: "uniformity",
      detail:
        `sentence lengths are uniform: CV=${sentCv.toFixed(2)} ` +
        "(human prose is typically > 0.50); first lengths: " +
        lengths.slice(0, 25).join(" "),
      line: null,
      excerpt: null,
    });
  }

  // 3. Paragraph-length uniformity
  const paraCv = metrics.paragraph_uniformity_cv;
  if (paraCv !== null && paraCv !== undefined && paraCv < 0.45) {
    const paraLengths = text
      .split(/\n\s*\n/)
      .filter((p) => wsWordCount(p) > 15)
      .map((p) => wsWordCount(p));
    evidence.push({
      type: "uniformity",
      detail:
        `paragraph lengths are uniform: CV=${paraCv.toFixed(2)} across ` +
        `${paraLengths.length} paragraphs (human prose is typically > 0.50); ` +
        "lengths: " +
        paraLengths.slice(0, 20).join(" "),
      line: null,
      excerpt: null,
    });
  }

  // 4. Connective overuse with example sentences
  if (metrics.connective_density >= 0.1) {
    const ranked = [];
    for (const sent of sentences) {
      const lowerSent = sent.toLowerCase();
      let n = 0;
      for (const c of CONNECTIVES) {
        if (lowerSent.includes(c)) n++;
      }
      if (n >= 2) ranked.push([n, sent]);
    }
    ranked.sort((a, b) => b[0] - a[0]);
    for (const [n, sent] of ranked.slice(0, 2)) {
      evidence.push({
        type: "connective",
        detail: `sentence carries ${n} discourse connectives`,
        line: null,
        excerpt: truncateMiddle(sent.trim(), 130),
      });
    }
  }

  // 5. Most suspicious sentences
  const sentenceScores = [];
  const tierWeights = { high: 3, medium: 2, weak: 1 };
  for (const sent of sentences) {
    const lowerSent = sent.toLowerCase();
    let markers = 0;
    for (const tier of ["high", "medium", "weak"]) {
      for (const p of AI_PHRASES[tier]) {
        if (lowerSent.includes(p)) markers += tierWeights[tier];
      }
    }
    for (const c of CONNECTIVES) {
      if (lowerSent.includes(c)) markers += 1;
    }
    sentenceScores.push([markers, sent]);
  }
  sentenceScores.sort((a, b) => b[0] - a[0]);
  const textLower = text.toLowerCase();
  for (const [markers, sent] of sentenceScores.slice(0, 3)) {
    if (markers >= 2) {
      const idx = textLower.indexOf(sent.slice(0, 40).toLowerCase());
      evidence.push({
        type: "sentence",
        detail: `sentence with ${markers} AI markers`,
        line: idx !== -1 ? countNewlinesBefore(text, idx) + 1 : null,
        excerpt: truncateMiddle(sent.trim(), 130),
      });
    }
  }

  return evidence;
}

// =========================================================
// REPORTING FUNCTIONS
// =========================================================

// =========================================================
// Exports (browser: globals via <script src>; Node: for the parity test)
// =========================================================
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    calculateAIForensicMetrics,
    calculateAIProbability,
    buildEvidence,
    getInterpretation,
    processText,
    AI_PHRASES,
    CONNECTIVES,
  };
}
