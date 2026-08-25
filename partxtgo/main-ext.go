package main

import (
	"fmt"
	"log"
	"math"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
	"unicode"
	"unicode/utf8"
)

// =========================================================
// ENHANCED ALLOWED CHARACTERS
// =========================================================

const allowedChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" +
	"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" +
	"ҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ[]{}():()-=_+!@#$%&*;'/.,<>\"`~—«» \t\n\r"

func isAllowed(ch rune) bool {
	return strings.ContainsRune(allowedChars, ch)
}

// =========================================================
// ENHANCED AI WATERMARK CHARACTERS
// =========================================================

func isWatermark(ch rune) bool {
	cp := uint32(ch)

	// Core zero-width characters
	switch cp {
	case 0x200B, // Zero Width Space (ZWSP)
		0x200C,  // Zero Width Non-Joiner (ZWNJ)
		0x200D,  // Zero Width Joiner (ZWJ)
		0xFEFF,  // Zero Width No-Break Space (ZWNBSP, BOM)
		0x00AD,  // Soft Hyphen (SHY)
		0x2060,  // Word Joiner
		0x2061,  // Function Application
		0x2062,  // Invisible Times
		0x2063,  // Invisible Separator
		0x2064,  // Invisible Plus
		0x202A,  // Left-to-Right Embedding
		0x202B,  // Right-to-Left Embedding
		0x202C,  // Pop Directional Formatting
		0x202D,  // Left-to-Right Override
		0x202E,  // Right-to-Left Override
		0x2028,  // Line Separator
		0x2029,  // Paragraph Separator
		0xE0001, // Language Tag
		0x180E:  // Mongolian Separator
		return true
	}

	// Variation Selectors
	if cp >= 0xFE00 && cp <= 0xFE0F {
		return true
	}

	// Tag characters
	if cp >= 0xE0020 && cp <= 0xE007F {
		return true
	}

	// Private Use Area - commonly abused for watermarking
	if cp >= 0xE000 && cp <= 0xE07F {
		return true
	}

	// Additional suspicious characters
	switch cp {
	case 0xFFF9, 0xFFFA, 0xFFFB, 0xFFFC, 0xFFFD, // Interlinear annotation
		0x2010, 0x2011, // Hyphen variants
		0x2012, 0x2013, 0x2014, // Em-dash variants
		0x2018, 0x2019, 0x201B, // Smart quotes
		0x201C, 0x201D, 0x201E, 0x201F, // Smart double quotes
		0x2026, // Ellipsis
		0x202F, // Narrow no-break space
		0x205F, // Medium mathematical space
		0x00A0: // Non-breaking space
		return true
	}

	// Space variants
	if cp >= 0x2000 && cp <= 0x200A {
		return true
	}

	return false
}

// =========================================================
// TEXT PROCESSING STRUCTS
// =========================================================

type ProcessResult struct {
	Cleaned          string
	Replaced         map[rune]int
	WatermarkRemoved map[rune]int
}

func process(text string, removeWatermark bool) ProcessResult {
	replaced := make(map[rune]int)
	watermarkRemoved := make(map[rune]int)
	var out strings.Builder

	out.Grow(len(text))

	for _, ch := range text {
		if removeWatermark && isWatermark(ch) {
			watermarkRemoved[ch]++
			continue
		}

		if isAllowed(ch) {
			out.WriteRune(ch)
		} else {
			out.WriteRune('?')
			replaced[ch]++
		}
	}

	return ProcessResult{
		Cleaned:          out.String(),
		Replaced:         replaced,
		WatermarkRemoved: watermarkRemoved,
	}
}

// =========================================================
// AI FORENSIC PATTERNS (v0.4.0 — aligned with parscgpt-ext.py
// reference / AI_SIGNALS_SPEC.md)
// =========================================================

// Suspicious Unicode characters - aligned with the parscgpt-ext.py reference
var unicodeSuspicious = []rune{
	'—', '–', '“', '”', '‘', '’',
	'…', '•', '→', '←', '↑', '↓',
	'©', '®', '™', '°', '±', '×', '÷',
}

// AI-typical phrases: tiered multilingual database (v0.4.0).
// HIGH   - distinctive LLM template phrases, zero hits in human validation corpus
// MEDIUM - typical AI connective/register markers, rare in human corpus
// WEAK   - markers that also occur in human prose; evidence-only, tiny weight
var phraseTierOrder = []string{"high", "medium", "weak"}

var aiPhrases = map[string][]string{
	"high": {
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
	},
	"medium": {
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
	},
	"weak": {
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
	},
}

// Discourse connectives (all languages merged); used for connective_density.
var connectives = []string{
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
}

// Passive voice patterns (reference basis for passive_voice_density)
var passivePatterns = []string{
	"is considered to be", "are considered to be",
	"is often said to be", "are often said to be",
	"is generally regarded as", "are generally regarded as",
	"is typically characterized by", "are typically characterized by",
	"is commonly associated with", "are commonly associated with",
	"is widely recognized as", "are widely recognized as",
	"is frequently observed to", "are frequently observed to",
	"is usually understood to", "are usually understood to",
}

func buildSet(list string) map[string]bool {
	set := make(map[string]bool)
	for _, w := range strings.Fields(list) {
		set[w] = true
	}
	return set
}

// Stopwords - large multilingual reference set (see parscgpt-ext.py)
var stopwords = buildSet(`the a an and or but if then
	else when at from by on off for in out over to into with about against
	between through during before after above below up down of again further
	once here there why how all any both each few more most other some
	such no nor not only own same so than too very can will just should now
	i me my myself we our ours ourselves you your yours yourself yourselves
	he him his himself she her hers herself it its itself they them their
	theirs themselves what which who whom this that these those am is are
	was were be been being have has had having do does did doing
	и в во не на я с что а как его она оно к но они мы вы бы был было быть
	если это того потом себя чтобы от так для тем под когда же ну пока еще
	были который своей или тебя через ни ему будет них там ее им про этом
	этому куда этого раз можно два где ли без чем эти нас за своих какой
	сам всех любой один между была вас чей которой сейчас также свои ей
	которого либо ваш нужно каждый том потому дело после над очень даже
	вам кроме моего хоть чего свой впрочем он него ваша затем которые твой
	кого их все её может такой кому зачем впереди мой хотя другой твоего
	твоей лишь никогда перед каких тоже кое-кого эту пять дальше почему
	вашей вторых каждой каждое твоих мной ним вами мною тобой ею тобою
	собой ими о об обо ото из изо ко по при ради сквозь у из-за из-под
	вокруг позади посреди против среди шесть семь восемь девять десять
	нуль ноль три четыре миллион миллиарда`)

// =========================================================
// SCORING WEIGHTS (v0.4.0) - canonical values, see AI_SIGNALS_SPEC.md
// =========================================================

type tierPoint struct {
	threshold float64
	points    int
}

var sentCVTiers = []tierPoint{{0.30, 32}, {0.35, 26}, {0.40, 19}, {0.45, 11}, {0.50, 5}}
var paraCVTiers = []tierPoint{{0.15, 28}, {0.25, 22}, {0.35, 16}, {0.45, 7}}
var jointCVTiers = []tierPoint{{0.40, 14}, {0.45, 10}}
var connectiveTiers = []tierPoint{{0.12, 13}, {0.08, 7}}

const (
	highPhraseScoreMulti  = 24 // >=2 hits
	highPhraseScoreSingle = 15 // ==1 hit
	medPhraseScoreMulti   = 10 // >=3 hits
	medPhraseScoreAny     = 5  // >=1 hit
	weakPhraseScore       = 4  // >=4 hits

	// Template header repetition: verbatim-repeated short non-punctuated
	// lines ("Что верно" x7 etc.) - structured LLM answers reuse section
	// templates. Zero hits in the human validation corpus.
	templateHeaderMinRepeats = 3
	templateHeaderScoreMany  = 14 // >=2 distinct templates or >=10 repeats
	templateHeaderScoreSome  = 8  // >=3 repeats
)

// Guards: CV signals are unreliable on tiny texts. Instead of a hard cutoff
// (which silently made short AI texts score as "human"), tier points are
// scaled by statistical reliability: min(1, n/sentCVFullSentences) etc.
const (
	sentCVMinSentences   = 5  // below this, sentence CV is pure noise -> 0
	sentCVFullSentences  = 15 // full weight from this many sentences on
	paraCVMinParagraphs  = 3  // below this, paragraph CV is not computed
	paraCVFullParagraphs = 4
	minWordsForCV        = 40
	fullWordsForCV       = 150
)

// =========================================================
// FORENSIC ANALYSIS STRUCTS
// =========================================================

type PhraseOccurrence struct {
	Tier   string
	Phrase string
	Idx    int
}

type TemplateOccurrence struct {
	Line   string
	Count  int
	LineNo int
}

type AIMetrics struct {
	WordCount             int
	SentenceCount         int
	LexicalDiversity      float64
	RepetitionScore       float64
	Entropy               float64
	Burstiness            float64
	ParagraphUniformityCV float64
	ParagraphCVKnown      bool
	ParagraphCount        int
	PatternRepetition     float64
	PunctuationDensity    float64
	AIPhraseHits          int
	AIPhraseTiers         map[string]int
	AIPhraseOccurrences   []PhraseOccurrence
	TemplateTotal         int
	TemplateDistinct      int
	TemplateOccurrences   []TemplateOccurrence
	ConnectiveDensity     float64
	Sentences             []string
	UnicodeSymbols        int
	AvgWordLength         float64
	WordLengthVariance    float64
	PronounRatio          float64
	ReadabilityScore      float64
	PassiveVoiceDensity   float64
	AdjNounPairDiversity  float64
	StructuralUniformity  float64
	QuantifierOveruse     float64
	PromotionalRegister   bool
}

type AIResult struct {
	Probability float64
	Confidence  string
	Scores      map[string]int
}

type Evidence struct {
	Type    string
	Detail  string
	Line    int
	HasLine bool
	Excerpt string
}

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

func wordFrequency(text string) map[string]int {
	freq := make(map[string]int)
	var currentWord strings.Builder

	for _, ch := range text {
		if unicode.IsLetter(ch) || ch == '\'' {
			currentWord.WriteRune(unicode.ToLower(ch))
		} else {
			if currentWord.Len() > 0 {
				word := currentWord.String()
				if utf8.RuneCountInString(word) > 2 && !stopwords[word] {
					freq[word]++
				}
				currentWord.Reset()
			}
		}
	}

	// Handle last word
	if currentWord.Len() > 0 {
		word := currentWord.String()
		if utf8.RuneCountInString(word) > 2 && !stopwords[word] {
			freq[word]++
		}
	}

	return freq
}

// tokenizeWords mirrors Python re.findall(r'\b\w+\b', text.lower()):
// runs of letters, digits and underscores.
func tokenizeWords(text string) []string {
	lower := strings.ToLower(text)
	var words []string
	var cur strings.Builder
	flush := func() {
		if cur.Len() > 0 {
			words = append(words, cur.String())
			cur.Reset()
		}
	}
	for _, r := range lower {
		if unicode.IsLetter(r) || unicode.IsNumber(r) || r == '_' {
			cur.WriteRune(r)
		} else {
			flush()
		}
	}
	flush()
	return words
}

var abbrevRe = regexp.MustCompile(`\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\.`)
var sentenceSplitRe = regexp.MustCompile(`[.!?]+`)
var paragraphSplitRe = regexp.MustCompile(`\n\s*\n`)

// splitSentences mirrors the Python reference: mask abbreviations
// (Mr|Mrs|Ms|Dr|Prof|Sr|Jr). as <DOT>, split on [.!?]+, keep sentences
// longer than 3 characters.
func splitSentences(text string) []string {
	masked := abbrevRe.ReplaceAllString(text, "$1<DOT>")
	parts := sentenceSplitRe.Split(masked, -1)
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		p = strings.ReplaceAll(p, "<DOT>", ".")
		if p != "" && utf8.RuneCountInString(p) > 3 {
			out = append(out, p)
		}
	}
	return out
}

func meanInts(values []int) float64 {
	if len(values) == 0 {
		return 0
	}
	sum := 0
	for _, v := range values {
		sum += v
	}
	return float64(sum) / float64(len(values))
}

// pstdev is population standard deviation (statistics.pstdev in Python).
func pstdev(values []int) float64 {
	if len(values) == 0 {
		return 0
	}
	m := meanInts(values)
	sum := 0.0
	for _, v := range values {
		d := float64(v) - m
		sum += d * d
	}
	return math.Sqrt(sum / float64(len(values)))
}

// stdev is sample standard deviation (statistics.stdev in Python).
func stdev(values []int) float64 {
	if len(values) < 2 {
		return 0
	}
	m := meanInts(values)
	sum := 0.0
	for _, v := range values {
		d := float64(v) - m
		sum += d * d
	}
	return math.Sqrt(sum / float64(len(values)-1))
}

func calculateAIForensicMetrics(text string) *AIMetrics {
	if len(text) == 0 {
		return nil
	}

	words := tokenizeWords(text)
	sentences := splitSentences(text)
	if len(words) == 0 || len(sentences) == 0 {
		return nil
	}

	wordCount := len(words)
	sentenceCount := len(sentences)

	// Filtered words (reference basis for diversity/entropy/repetition)
	filtered := make([]string, 0, wordCount)
	for _, w := range words {
		if !stopwords[w] && utf8.RuneCountInString(w) > 2 {
			filtered = append(filtered, w)
		}
	}
	filteredCounter := make(map[string]int)
	for _, w := range filtered {
		filteredCounter[w]++
	}

	// Lexical diversity (on filtered words, as in reference)
	lexicalDiv := 0.0
	if len(filtered) > 0 {
		lexicalDiv = float64(len(filteredCounter)) / float64(len(filtered))
	}

	// Repetition score (distinct repeated filtered words / filtered words)
	repeated := 0
	for _, count := range filteredCounter {
		if count > 1 {
			repeated++
		}
	}
	repScore := 0.0
	if len(filtered) > 0 {
		repScore = float64(repeated) / float64(len(filtered))
	}

	// Entropy (on filtered words, as in reference)
	entropy := 0.0
	if len(filtered) > 0 {
		for _, count := range filteredCounter {
			p := float64(count) / float64(len(filtered))
			entropy -= p * math.Log2(p)
		}
	}

	// Sentence length analysis (burstiness = CV of sentence word counts);
	// word count per sentence uses whitespace split, as in the reference
	sentLengths := make([]int, len(sentences))
	for i, s := range sentences {
		sentLengths[i] = len(strings.Fields(s))
	}
	avgSentLen := meanInts(sentLengths)
	burstiness := 0.0
	if avgSentLen > 0 && len(sentLengths) > 1 {
		burstiness = pstdev(sentLengths) / avgSentLen
	}

	// Paragraph length uniformity (CV of paragraph word counts)
	paragraphs := make([]string, 0, 8)
	for _, p := range paragraphSplitRe.Split(text, -1) {
		if len(strings.Fields(p)) > 15 {
			paragraphs = append(paragraphs, p)
		}
	}
	paraLengths := make([]int, len(paragraphs))
	for i, p := range paragraphs {
		paraLengths[i] = len(strings.Fields(p))
	}
	paraCV := 0.0
	paraCVKnown := false
	paraCount := 0
	if len(paraLengths) >= paraCVMinParagraphs {
		paraAvg := meanInts(paraLengths)
		if paraAvg > 0 {
			paraCV = pstdev(paraLengths) / paraAvg
			paraCVKnown = true
			paraCount = len(paraLengths)
		}
	}

	// Pattern repetition
	categorizeLength := func(length int) rune {
		if length <= 10 {
			return 'S'
		} else if length <= 20 {
			return 'M'
		}
		return 'L'
	}
	patternCounts := make(map[rune]int)
	for _, l := range sentLengths {
		patternCounts[categorizeLength(l)]++
	}
	repeatedPatterns := 0
	for _, count := range patternCounts {
		if count > 1 {
			repeatedPatterns++
		}
	}
	patternRep := 0.0
	if len(sentLengths) > 0 {
		patternRep = float64(repeatedPatterns) / float64(len(sentLengths))
	}

	// Punctuation density (reference regex [,;:()-—–] / rune count of text)
	punctCount := 0
	for _, ch := range text {
		switch ch {
		case ',', ';', ':', '(', ')', '-', '—', '–':
			punctCount++
		}
	}
	punctDensity := float64(punctCount) / float64(utf8.RuneCountInString(text))

	// AI phrase detection (tiered, with occurrences for evidence)
	textLower := strings.ToLower(text)
	aiHits := 0
	phraseTiers := map[string]int{"high": 0, "medium": 0, "weak": 0}
	var phraseOccurrences []PhraseOccurrence
	for _, tier := range phraseTierOrder {
		for _, phrase := range aiPhrases[tier] {
			found := strings.Count(textLower, phrase)
			if found > 0 {
				aiHits++
				phraseTiers[tier] += found
				idx := strings.Index(textLower, phrase)
				for n := 0; n < found && n < 3; n++ {
					phraseOccurrences = append(phraseOccurrences,
						PhraseOccurrence{Tier: tier, Phrase: phrase, Idx: idx})
					next := strings.Index(textLower[idx+len(phrase):], phrase)
					if next == -1 {
						break
					}
					idx = idx + len(phrase) + next
				}
			}
		}
	}

	// Connective density (connectives per sentence)
	connTotal := 0
	for _, s := range sentences {
		sLower := strings.ToLower(s)
		for _, c := range connectives {
			if strings.Contains(sLower, c) {
				connTotal++
			}
		}
	}
	connectiveDensity := float64(connTotal) / float64(len(sentences))

	// Template header repetition (structured-answer genre)
	lineCounter := make(map[string]int)
	firstLineNo := make(map[string]int)
	tmplLastChar := ".!?:;,…\"»„"
	for i, raw := range strings.Split(text, "\n") {
		line := strings.TrimSpace(raw)
		runes := []rune(line)
		if len(runes) < 4 {
			continue
		}
		if len(runes) > 60 || len(strings.Fields(line)) > 8 {
			continue
		}
		if strings.ContainsRune(tmplLastChar, runes[len(runes)-1]) {
			continue
		}
		if unicode.IsDigit(runes[0]) {
			continue
		}
		lineCounter[line]++
		if _, ok := firstLineNo[line]; !ok {
			firstLineNo[line] = i + 1
		}
	}
	var tmplOccurrences []TemplateOccurrence
	tmplTotal := 0
	tmplDistinct := 0
	for line, count := range lineCounter {
		if count >= templateHeaderMinRepeats {
			tmplTotal += count
			tmplDistinct++
			tmplOccurrences = append(tmplOccurrences,
				TemplateOccurrence{Line: line, Count: count, LineNo: firstLineNo[line]})
		}
	}
	sort.SliceStable(tmplOccurrences, func(i, j int) bool {
		return tmplOccurrences[i].Count > tmplOccurrences[j].Count
	})

	// Unicode suspicious chars - count distinct suspicious characters
	// present in the ORIGINAL (pre-sanitization) text, matching reference
	unicodeCount := 0
	for _, r := range unicodeSuspicious {
		if strings.ContainsRune(text, r) {
			unicodeCount++
		}
	}

	// Word length statistics
	wordLengths := make([]int, len(words))
	for i, w := range words {
		wordLengths[i] = utf8.RuneCountInString(w)
	}
	avgWordLen := 0.0
	for _, l := range wordLengths {
		avgWordLen += float64(l)
	}
	avgWordLen /= float64(len(wordLengths))
	wordLenVar := stdev(wordLengths)

	// --- Supporting metrics (mirror parscgpt-ext.py reference) ---
	// Pronoun ratio
	allPronouns := buildSet(`i me my mine myself we us our ours ourselves ` +
		`you your yours yourself yourselves ` +
		`he him his himself she her hers herself it its itself they them their theirs themselves ` +
		`this that these those ` +
		`anyone anything everyone everything someone something noone nothing each every either neither both few many several`)
	pronounCount := 0
	for _, w := range words {
		if allPronouns[w] {
			pronounCount++
		}
	}
	pronounRatio := float64(pronounCount) / float64(wordCount)

	// Readability (Flesch, simplified syllables)
	syllableCount := 0
	for _, w := range words {
		syll := 0
		for _, ch := range w {
			if strings.ContainsRune("aeiouy", ch) {
				syll++
			}
		}
		if syll < 1 {
			syll = 1
		}
		syllableCount += syll
	}
	avgSentenceLength := float64(wordCount) / float64(len(sentences))
	avgSyllablesPerWord := float64(syllableCount) / float64(wordCount)
	flesch := 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgSyllablesPerWord)
	readability := math.Max(0, math.Min(100, flesch))

	// Passive voice density
	whitespaceWords := len(strings.Fields(text))
	passiveCount := 0
	for _, p := range passivePatterns {
		passiveCount += strings.Count(textLower, p)
	}
	passiveDensity := float64(passiveCount) / float64(maxInt(whitespaceWords, 1))

	// Adjective-noun pair diversity
	adjIndicators := []string{"al", "ble", "cal", "ful", "ic", "ive", "less", "ous"}
	nounIndicators := []string{"er", "ism", "ment", "ness", "tion", "ship", "cy", "dom"}
	hasSuffix := func(w string, inds []string) bool {
		for _, ind := range inds {
			if strings.HasSuffix(w, ind) {
				return true
			}
		}
		return false
	}
	adjectives := make(map[string]bool)
	nouns := make(map[string]bool)
	for _, w := range words {
		if hasSuffix(w, adjIndicators) {
			adjectives[w] = true
		}
		if hasSuffix(w, nounIndicators) {
			nouns[w] = true
		}
	}
	pairs := make(map[string]bool)
	for i := 0; i+1 < len(words); i++ {
		if adjectives[words[i]] && nouns[words[i+1]] {
			pairs[words[i]+" "+words[i+1]] = true
		}
	}
	totalPossible := 1
	if len(adjectives) > 0 && len(nouns) > 0 {
		totalPossible = len(adjectives) * len(nouns)
	}
	adjNounDiv := float64(len(pairs)) / float64(totalPossible)

	// Structural uniformity (repeated 2-word sentence starts)
	starts := make([]string, 0, len(sentences))
	startCounter := make(map[string]int)
	for _, s := range sentences {
		f := strings.Fields(s)
		if len(f) == 0 {
			continue
		}
		if len(f) > 1 {
			f = f[:2]
		}
		start := strings.ToLower(strings.Join(f, " "))
		starts = append(starts, start)
		startCounter[start]++
	}
	repeatedStarts := 0
	for _, count := range startCounter {
		if count > 1 {
			repeatedStarts++
		}
	}
	structUnif := float64(repeatedStarts) / float64(len(sentences))

	// Quantifier overuse
	quantifiers := []string{"relatively", "somewhat", "quite", "rather", "fairly",
		"reasonably", "comparatively", "moderately", "substantially",
		"considerably", "significantly", "notably", "remarkably"}
	quantCount := 0
	for _, q := range quantifiers {
		quantCount += strings.Count(textLower, q)
	}
	quantOveruse := float64(quantCount) / float64(maxInt(whitespaceWords, 1))

	// Genre abstention: promotional/social-media register (emoji- and
	// exclamation-heavy). Not a scored signal - verdict note only.
	promoEmoji := 0
	for _, r := range text {
		if r >= 0x2600 {
			promoEmoji++
		}
	}
	promoExcl := float64(strings.Count(text, "!")) / float64(wordCount)
	promo := promoEmoji >= 5 && promoExcl >= 0.02

	return &AIMetrics{
		WordCount:             wordCount,
		SentenceCount:         sentenceCount,
		LexicalDiversity:      lexicalDiv,
		RepetitionScore:       repScore,
		Entropy:               entropy,
		Burstiness:            burstiness,
		ParagraphUniformityCV: paraCV,
		ParagraphCVKnown:      paraCVKnown,
		ParagraphCount:        paraCount,
		PatternRepetition:     patternRep,
		PunctuationDensity:    punctDensity,
		AIPhraseHits:          aiHits,
		AIPhraseTiers:         phraseTiers,
		AIPhraseOccurrences:   phraseOccurrences,
		TemplateTotal:         tmplTotal,
		TemplateDistinct:      tmplDistinct,
		TemplateOccurrences:   tmplOccurrences,
		ConnectiveDensity:     connectiveDensity,
		Sentences:             sentences,
		UnicodeSymbols:        unicodeCount,
		AvgWordLength:         avgWordLen,
		WordLengthVariance:    wordLenVar,
		PronounRatio:          pronounRatio,
		ReadabilityScore:      readability,
		PassiveVoiceDensity:   passiveDensity,
		AdjNounPairDiversity:  adjNounDiv,
		StructuralUniformity:  structUnif,
		QuantifierOveruse:     quantOveruse,
		PromotionalRegister:   promo,
	}
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func calculateAIProbability(metrics *AIMetrics) *AIResult {
	scores := make(map[string]int)
	total := 0
	add := func(name string, points int) {
		if points > 0 {
			scores[name] = points
			total += points
		}
	}

	// --- Primary structural signals ---
	// Tier points are scaled by statistical reliability of the sample
	// (short texts get partial credit instead of a silent zero).
	sentCV := metrics.Burstiness
	sentScale := math.Min(1, float64(metrics.SentenceCount)/sentCVFullSentences) *
		math.Min(1, float64(metrics.WordCount)/fullWordsForCV)
	sentCVPoints := 0
	if metrics.SentenceCount >= sentCVMinSentences && metrics.WordCount >= minWordsForCV {
		for _, tp := range sentCVTiers {
			if sentCV < tp.threshold {
				sentCVPoints = int(math.Round(float64(tp.points) * sentScale))
				break
			}
		}
	}
	add("sentence_cv", sentCVPoints)

	paraPoints := 0
	paraScale := 0.0
	if metrics.ParagraphCVKnown {
		paraCount := metrics.ParagraphCount
		if paraCount == 0 {
			paraCount = paraCVFullParagraphs
		}
		paraScale = math.Min(1, float64(paraCount)/paraCVFullParagraphs)
		for _, tp := range paraCVTiers {
			if metrics.ParagraphUniformityCV < tp.threshold {
				paraPoints = int(math.Round(float64(tp.points) * paraScale))
				break
			}
		}
	}
	add("paragraph_cv", paraPoints)

	if metrics.ParagraphCVKnown && sentCVPoints > 0 {
		for _, tp := range jointCVTiers {
			if sentCV < tp.threshold && metrics.ParagraphUniformityCV < tp.threshold {
				add("joint_uniformity", int(math.Round(float64(tp.points)*math.Min(sentScale, paraScale))))
				break
			}
		}
	}

	// --- Tiered phrase scores ---
	tiers := metrics.AIPhraseTiers
	switch {
	case tiers["high"] >= 2:
		add("ai_phrases", highPhraseScoreMulti)
	case tiers["high"] == 1:
		add("ai_phrases", highPhraseScoreSingle)
	case tiers["medium"] >= 3:
		add("ai_phrases", medPhraseScoreMulti)
	case tiers["medium"] >= 1:
		add("ai_phrases", medPhraseScoreAny)
	case tiers["weak"] >= 4:
		add("ai_phrases", weakPhraseScore)
	}

	// --- Connective density ---
	for _, tp := range connectiveTiers {
		if metrics.ConnectiveDensity >= tp.threshold {
			add("connectives", tp.points)
			break
		}
	}

	// --- Template header repetition (structured-answer genre) ---
	if metrics.TemplateDistinct >= 2 || metrics.TemplateTotal >= 10 {
		add("template_headers", templateHeaderScoreMany)
	} else if metrics.TemplateTotal >= templateHeaderMinRepeats {
		add("template_headers", templateHeaderScoreSome)
	}

	// --- Supporting statistical metrics ---
	if metrics.LexicalDiversity < 0.45 {
		add("lexical_diversity", 15)
	} else if metrics.LexicalDiversity < 0.55 {
		add("lexical_diversity", 8)
	}

	if metrics.Entropy < 5.0 {
		add("entropy", 15)
	} else if metrics.Entropy < 6.5 {
		add("entropy", 8)
	}

	if metrics.PatternRepetition > 0.35 {
		add("pattern_repetition", 10)
	}

	if metrics.RepetitionScore > 0.5 {
		add("repetition", 8)
	}

	if metrics.PunctuationDensity > 0.04 {
		add("punctuation", 4)
	}

	if metrics.UnicodeSymbols > 0 {
		add("unicode", 4)
	}

	if metrics.AvgWordLength < 4.0 {
		add("avg_word_length", 5)
	} else if metrics.AvgWordLength < 4.5 {
		add("avg_word_length", 3)
	}

	if metrics.WordLengthVariance < 1.5 {
		add("word_length_variance", 4)
	}

	if metrics.PronounRatio > 0.15 {
		add("pronoun_ratio", 4)
	}

	if metrics.ReadabilityScore > 70 {
		add("readability", 5)
	} else if metrics.ReadabilityScore > 60 {
		add("readability", 3)
	}

	if metrics.PassiveVoiceDensity > 0.05 {
		add("passive_voice", 4)
	}

	if metrics.AdjNounPairDiversity < 0.3 {
		add("adj_noun_diversity", 3)
	}

	if metrics.StructuralUniformity > 0.4 {
		add("structural_uniformity", 4)
	}

	if metrics.QuantifierOveruse > 0.02 {
		add("quantifier_overuse", 3)
	}

	// Length-based confidence adjustment
	wordCount := metrics.WordCount
	confidence := "HIGH"
	if wordCount < 300 {
		confidence = "LOW"
	} else if wordCount < 1000 {
		confidence = "MEDIUM"
	}

	lengthFactor := math.Min(1.0, float64(wordCount)/1000.0)
	adjustedTotal := float64(total) * (0.9 + 0.1*lengthFactor)
	probability := math.Min(100.0, adjustedTotal)

	return &AIResult{
		Probability: probability,
		Confidence:  confidence,
		Scores:      scores,
	}
}

func getInterpretation(metrics *AIMetrics, aiProbability float64, confidence string) (string, []string) {
	var interpretations []string

	var verdict string
	if aiProbability > 70 {
		verdict = fmt.Sprintf("Strong AI-like statistical profile (%.1f%%)", aiProbability)
	} else if aiProbability > 55 {
		verdict = fmt.Sprintf("Probable AI-generated text with multiple indicators (%.1f%%)", aiProbability)
	} else if aiProbability > 35 {
		verdict = fmt.Sprintf("Mixed profile: human-like and AI-like signals (%.1f%%)", aiProbability)
	} else {
		verdict = fmt.Sprintf("Text statistically appears more human-like (%.1f%%)", aiProbability)
	}

	// Honest abstention: below the structural-signal horizon the "human-like"
	// verdict would be an artifact of missing data, not evidence.
	if metrics.WordCount < fullWordsForCV || metrics.SentenceCount < sentCVMinSentences {
		verdict += " NOTE: text is too short for reliable structural analysis — " +
			"this verdict is unreliable, not evidence of human authorship."
	}

	// Genre abstention: promotional/social register - verdict withdrawn, no AI points
	if metrics.PromotionalRegister {
		verdict += " NOTE: promotional/social-media register (emoji- and " +
			"exclamation-heavy) is outside the calibration corpus — " +
			"this verdict is unreliable for this genre."
	}

	if metrics.Burstiness < 0.35 {
		interpretations = append(interpretations, "⚠️ Uniform sentence lengths (low burstiness) - strong AI signal")
	} else if metrics.Burstiness < 0.45 {
		interpretations = append(interpretations, "⚠️ Somewhat uniform sentence lengths - AI-like")
	}

	if metrics.ParagraphCVKnown && metrics.ParagraphUniformityCV < 0.35 {
		interpretations = append(interpretations, "⚠️ Uniform paragraph lengths - AI-like")
	}

	if metrics.LexicalDiversity < 0.45 {
		interpretations = append(interpretations, "⚠️ Low lexical diversity - limited vocabulary variation")
	} else if metrics.LexicalDiversity > 0.65 {
		interpretations = append(interpretations, "✓ High lexical diversity - rich vocabulary variation")
	}

	if metrics.Entropy < 5.0 {
		interpretations = append(interpretations, "⚠️ Low entropy - unnaturally uniform word distribution")
	} else if metrics.Entropy > 6.0 {
		interpretations = append(interpretations, "✓ Good entropy - natural word distribution")
	}

	if metrics.AIPhraseTiers["high"] > 0 || metrics.AIPhraseTiers["medium"] > 0 {
		interpretations = append(interpretations,
			fmt.Sprintf("⚠️ AI phrases: high=%d, medium=%d",
				metrics.AIPhraseTiers["high"], metrics.AIPhraseTiers["medium"]))
	}

	if metrics.ConnectiveDensity >= 0.12 {
		interpretations = append(interpretations, "⚠️ High discourse-connective density")
	}

	if metrics.PatternRepetition > 0.35 {
		interpretations = append(interpretations, "⚠️ High pattern repetition - template-like structure")
	}

	if metrics.UnicodeSymbols > 0 {
		interpretations = append(interpretations,
			fmt.Sprintf("⚠️ Found %d suspicious Unicode characters", metrics.UnicodeSymbols))
	}

	return verdict, interpretations
}

// =========================================================
// EVIDENCE (v0.4.0) - port of build_evidence from partxtpy/partxt-ext.py
// =========================================================

func truncateMiddleRunes(s string, width int) string {
	r := []rune(s)
	if len(r) <= width {
		return s
	}
	half := width/2 - 5
	if half < 0 {
		half = 0
	}
	return string(r[:half]) + " ... " + string(r[len(r)-half:])
}

func excerptFor(text, phrase string, idx int) string {
	prefix := text[:idx]
	starts := []int{
		strings.LastIndex(prefix, ". "),
		strings.LastIndex(prefix, "! "),
		strings.LastIndex(prefix, "? "),
		strings.LastIndex(prefix, "\n"),
	}
	sentStart := starts[0]
	for _, s := range starts {
		if s > sentStart {
			sentStart = s
		}
	}
	sentStart++

	ends := []int{len(text)}
	for _, sep := range []string{". ", "! ", "? ", "\n"} {
		if p := strings.Index(text[idx:], sep); p != -1 {
			ends = append(ends, idx+p)
		}
	}
	sentEnd := ends[0]
	for _, e := range ends {
		if e < sentEnd {
			sentEnd = e
		}
	}

	fragment := strings.TrimSpace(text[sentStart:sentEnd])
	pos := strings.Index(strings.ToLower(fragment), phrase)
	if pos == -1 {
		return truncateMiddleRunes(fragment, 110)
	}
	if len(fragment) > 110 {
		const wLeft, wRight = 45, 60
		start := pos - wLeft
		if start < 0 {
			start = 0
		}
		end := pos + len(phrase) + wRight
		if end > len(fragment) {
			end = len(fragment)
		}
		var pfx, sfx string
		if start > 0 {
			pfx = "... "
		}
		if end < len(fragment) {
			sfx = " ..."
		}
		fragment = pfx + fragment[start:end] + sfx
		pos = pos - start + len(pfx)
	}
	return fragment[:pos] + ">>>" + fragment[pos:pos+len(phrase)] + "<<<" + fragment[pos+len(phrase):]
}

func buildEvidence(text string, metrics *AIMetrics) []Evidence {
	var evidence []Evidence
	sentences := metrics.Sentences
	occurrences := metrics.AIPhraseOccurrences
	textLower := strings.ToLower(text)

	lineFor := func(idx int) int {
		return strings.Count(text[:idx], "\n") + 1
	}

	// 1. Phrase hits with locations (already in tier order: high, medium, weak)
	shown := 0
	for _, occ := range occurrences {
		if shown >= 10 {
			break
		}
		var label string
		switch occ.Tier {
		case "high":
			label = "HIGH-risk"
		case "medium":
			label = "typical"
		default:
			label = "weak"
		}
		evidence = append(evidence, Evidence{
			Type:    "phrase",
			Detail:  fmt.Sprintf("%s AI phrase '%s'", label, occ.Phrase),
			Line:    lineFor(occ.Idx),
			HasLine: true,
			Excerpt: excerptFor(text, occ.Phrase, occ.Idx),
		})
		shown++
	}

	// 1b. Repeated template headers (structured-answer genre)
	for n, occ := range metrics.TemplateOccurrences {
		if n >= 4 {
			break
		}
		evidence = append(evidence, Evidence{
			Type:    "template",
			Detail:  fmt.Sprintf("repeated template header '%s' ×%d", occ.Line, occ.Count),
			Line:    occ.LineNo,
			HasLine: true,
		})
	}

	// 2. Sentence-length uniformity
	if metrics.Burstiness < 0.50 && metrics.WordCount >= minWordsForCV {
		var lengths []string
		n := 0
		for _, s := range sentences {
			if len(strings.Fields(s)) > 0 {
				lengths = append(lengths, fmt.Sprintf("%d", len(strings.Fields(s))))
				n++
				if n >= 25 {
					break
				}
			}
		}
		evidence = append(evidence, Evidence{
			Type: "uniformity",
			Detail: fmt.Sprintf("sentence lengths are uniform: CV=%.2f "+
				"(human prose is typically > 0.50); first lengths: %s",
				metrics.Burstiness, strings.Join(lengths, " ")),
		})
	}

	// 3. Paragraph-length uniformity
	if metrics.ParagraphCVKnown && metrics.ParagraphUniformityCV < 0.45 {
		var paraLengths []string
		for _, p := range paragraphSplitRe.Split(text, -1) {
			if len(strings.Fields(p)) > 15 {
				paraLengths = append(paraLengths, fmt.Sprintf("%d", len(strings.Fields(p))))
				if len(paraLengths) >= 20 {
					break
				}
			}
		}
		evidence = append(evidence, Evidence{
			Type: "uniformity",
			Detail: fmt.Sprintf("paragraph lengths are uniform: CV=%.2f across "+
				"%d paragraphs (human prose is typically > 0.50); lengths: %s",
				metrics.ParagraphUniformityCV, len(paraLengths), strings.Join(paraLengths, " ")),
		})
	}

	// 4. Connective overuse with example sentences
	if metrics.ConnectiveDensity >= 0.10 {
		type ranked struct {
			n    int
			sent string
		}
		var list []ranked
		for _, sent := range sentences {
			lower := strings.ToLower(sent)
			n := 0
			for _, c := range connectives {
				if strings.Contains(lower, c) {
					n++
				}
			}
			if n >= 2 {
				list = append(list, ranked{n, sent})
			}
		}
		sort.SliceStable(list, func(i, j int) bool { return list[i].n > list[j].n })
		for i := 0; i < 2 && i < len(list); i++ {
			evidence = append(evidence, Evidence{
				Type:    "connective",
				Detail:  fmt.Sprintf("sentence carries %d discourse connectives", list[i].n),
				Excerpt: truncateMiddleRunes(strings.TrimSpace(list[i].sent), 130),
			})
		}
	}

	// 5. Most suspicious sentences
	type scored struct {
		markers int
		sent    string
	}
	var sentenceScores []scored
	for _, sent := range sentences {
		lower := strings.ToLower(sent)
		markers := 0
		for _, tier := range phraseTierOrder {
			weight := 1
			switch tier {
			case "high":
				weight = 3
			case "medium":
				weight = 2
			}
			for _, p := range aiPhrases[tier] {
				if strings.Contains(lower, p) {
					markers += weight
				}
			}
		}
		for _, c := range connectives {
			if strings.Contains(lower, c) {
				markers++
			}
		}
		sentenceScores = append(sentenceScores, scored{markers, sent})
	}
	sort.SliceStable(sentenceScores, func(i, j int) bool { return sentenceScores[i].markers > sentenceScores[j].markers })
	for i := 0; i < 3 && i < len(sentenceScores); i++ {
		if sentenceScores[i].markers < 2 {
			break
		}
		sent := sentenceScores[i].sent
		sentRunes := []rune(sent)
		if len(sentRunes) > 40 {
			sentRunes = sentRunes[:40]
		}
		idx := strings.Index(textLower, strings.ToLower(string(sentRunes)))
		ev := Evidence{
			Type:    "sentence",
			Detail:  fmt.Sprintf("sentence with %d AI markers", sentenceScores[i].markers),
			Excerpt: truncateMiddleRunes(strings.TrimSpace(sent), 130),
		}
		if idx != -1 {
			ev.Line = lineFor(idx)
			ev.HasLine = true
		}
		evidence = append(evidence, ev)
	}

	return evidence
}

// =========================================================
// REPORTING FUNCTIONS
// =========================================================

func buildReport(inputFile, outputFile string, replaced, watermarkRemoved map[rune]int,
	wordFreq map[string]int, elapsed time.Duration, aiMetrics *AIMetrics, aiResult *AIResult,
	aiEvidence []Evidence, removeWatermark bool, lang string) string {

	var builder strings.Builder

	// Header
	builder.WriteString(strings.Repeat("=", 70) + "\n")
	builder.WriteString("aiparstxt-ext — Enhanced AI Forensic Analyzer Report\n")
	builder.WriteString(fmt.Sprintf("Language: %s\n", lang))
	builder.WriteString(strings.Repeat("=", 70) + "\n")
	builder.WriteString("\n")

	// Basic info
	builder.WriteString(fmt.Sprintf("Input file:  %s\n", inputFile))
	builder.WriteString(fmt.Sprintf("Output file: %s\n", outputFile))
	builder.WriteString(fmt.Sprintf("Execution time: %.6fs\n", elapsed.Seconds()))
	builder.WriteString("\n")

	// Watermark analysis
	builder.WriteString("--- AI Watermark Analysis ---\n")
	totalWatermark := 0
	for _, count := range watermarkRemoved {
		totalWatermark += count
	}
	builder.WriteString(fmt.Sprintf("Watermark characters removed: %d\n", totalWatermark))

	if totalWatermark > 0 {
		builder.WriteString("Removed watermark character types:\n")
		type charCount struct {
			char  rune
			count int
		}
		var sorted []charCount
		for ch, count := range watermarkRemoved {
			sorted = append(sorted, charCount{ch, count})
		}
		sort.Slice(sorted, func(i, j int) bool {
			return sorted[i].count > sorted[j].count
		})

		for i, item := range sorted {
			if i >= 20 {
				break
			}
			codepoint := fmt.Sprintf("U+%04X", uint32(item.char))
			builder.WriteString(fmt.Sprintf("  %s: %d\n", codepoint, item.count))
		}
		if len(sorted) > 20 {
			builder.WriteString(fmt.Sprintf("  ... and %d more types\n", len(sorted)-20))
		}
	} else {
		builder.WriteString("No AI watermark characters detected\n")
	}
	builder.WriteString("\n")

	// Replaced characters
	builder.WriteString("--- Replaced Characters ---\n")
	totalReplaced := 0
	for _, count := range replaced {
		totalReplaced += count
	}
	builder.WriteString(fmt.Sprintf("Characters replaced: %d\n", totalReplaced))

	if totalReplaced > 0 {
		builder.WriteString("Replaced character types:\n")
		type charCount struct {
			char  rune
			count int
		}
		var sorted []charCount
		for ch, count := range replaced {
			sorted = append(sorted, charCount{ch, count})
		}
		sort.Slice(sorted, func(i, j int) bool {
			return sorted[i].count > sorted[j].count
		})

		for i, item := range sorted {
			if i >= 10 {
				break
			}
			codepoint := fmt.Sprintf("U+%04X", uint32(item.char))
			builder.WriteString(fmt.Sprintf("  %s: %d\n", codepoint, item.count))
		}
		if len(sorted) > 10 {
			builder.WriteString(fmt.Sprintf("  ... and %d more types\n", len(sorted)-10))
		}
	} else {
		builder.WriteString("No characters replaced\n")
	}
	builder.WriteString("\n")

	// AI Forensic Analysis
	if aiMetrics != nil && aiResult != nil {
		builder.WriteString(strings.Repeat("=", 70) + "\n")
		builder.WriteString("AI FORENSIC ANALYSIS\n")
		builder.WriteString(strings.Repeat("=", 70) + "\n")
		builder.WriteString("\n")

		verdict, interpretations := getInterpretation(aiMetrics, aiResult.Probability, aiResult.Confidence)

		builder.WriteString(fmt.Sprintf("Overall Verdict: %s\n", verdict))
		builder.WriteString(fmt.Sprintf("Confidence Level: %s\n", aiResult.Confidence))
		builder.WriteString("\n")

		builder.WriteString("Detailed Metrics:\n")
		builder.WriteString(fmt.Sprintf("  Word count:            %d\n", aiMetrics.WordCount))
		builder.WriteString(fmt.Sprintf("  Sentence count:        %d\n", aiMetrics.SentenceCount))
		builder.WriteString(fmt.Sprintf("  Sentence length CV:    %.3f\n", aiMetrics.Burstiness))
		if aiMetrics.ParagraphCVKnown {
			builder.WriteString(fmt.Sprintf("  Paragraph length CV:   %.3f\n", aiMetrics.ParagraphUniformityCV))
		} else {
			builder.WriteString("  Paragraph length CV:   n/a (<4 paragraphs)\n")
		}
		builder.WriteString(fmt.Sprintf("  Lexical diversity:     %.3f\n", aiMetrics.LexicalDiversity))
		builder.WriteString(fmt.Sprintf("  Repetition score:      %.3f\n", aiMetrics.RepetitionScore))
		builder.WriteString(fmt.Sprintf("  Entropy:               %.3f\n", aiMetrics.Entropy))
		builder.WriteString(fmt.Sprintf("  Connective density:    %.3f\n", aiMetrics.ConnectiveDensity))
		builder.WriteString(fmt.Sprintf("  Template headers:      %d repeats (%d distinct)\n",
			aiMetrics.TemplateTotal, aiMetrics.TemplateDistinct))
		builder.WriteString(fmt.Sprintf("  Pattern repetition:    %.3f\n", aiMetrics.PatternRepetition))
		builder.WriteString(fmt.Sprintf("  Punctuation density:   %.3f\n", aiMetrics.PunctuationDensity))
		builder.WriteString(fmt.Sprintf("  AI phrases (tiers):    high=%d, medium=%d, weak=%d\n",
			aiMetrics.AIPhraseTiers["high"], aiMetrics.AIPhraseTiers["medium"], aiMetrics.AIPhraseTiers["weak"]))
		builder.WriteString(fmt.Sprintf("  AI phrase hits:        %d\n", aiMetrics.AIPhraseHits))
		builder.WriteString(fmt.Sprintf("  Unicode suspicious:    %d\n", aiMetrics.UnicodeSymbols))
		builder.WriteString(fmt.Sprintf("  Avg word length:       %.2f\n", aiMetrics.AvgWordLength))
		builder.WriteString(fmt.Sprintf("  Word length variance:  %.2f\n", aiMetrics.WordLengthVariance))
		builder.WriteString("\n")

		if len(aiEvidence) > 0 {
			builder.WriteString("AI EVIDENCE (locations in the text):\n")
			limit := len(aiEvidence)
			if limit > 15 {
				limit = 15
			}
			for i := 0; i < limit; i++ {
				ev := aiEvidence[i]
				loc := "text-wide"
				if ev.HasLine {
					loc = fmt.Sprintf("line %d", ev.Line)
				}
				builder.WriteString(fmt.Sprintf("  [%d] %s: %s\n", i+1, loc, ev.Detail))
				if ev.Excerpt != "" {
					builder.WriteString(fmt.Sprintf("      \"%s\"\n", ev.Excerpt))
				}
			}
			builder.WriteString("\n")
		}

		if len(interpretations) > 0 {
			builder.WriteString("Signal Analysis:\n")
			for _, interp := range interpretations {
				builder.WriteString(fmt.Sprintf("  %s\n", interp))
			}
			builder.WriteString("\n")
		}

		builder.WriteString(strings.Repeat("=", 70) + "\n")
		builder.WriteString("\n")
	}

	// Word frequency
	builder.WriteString("--- Top Word Frequencies (Filtered) ---\n")
	if len(wordFreq) > 0 {
		type wordCount struct {
			word  string
			count int
		}
		var sorted []wordCount
		for word, count := range wordFreq {
			sorted = append(sorted, wordCount{word, count})
		}
		sort.Slice(sorted, func(i, j int) bool {
			return sorted[i].count > sorted[j].count
		})

		for i, item := range sorted {
			if i >= 20 {
				break
			}
			builder.WriteString(fmt.Sprintf("  %s: %d\n", item.word, item.count))
		}
	} else {
		builder.WriteString("(skipped)\n")
	}

	return builder.String()
}

// =========================================================
// MAIN FUNCTION
// =========================================================

func main() {
	if len(os.Args) < 2 {
		log.Fatal("Usage: go run . <input_file> [options]")
	}

	inputFile := os.Args[1]
	outputFile := ""
	reportFile := "report_go-ext.txt"
	noEdit := false
	noReport := false
	noWords := false
	removeWatermark := false

	i := 2
	for i < len(os.Args) {
		switch os.Args[i] {
		case "-o", "--output":
			if i+1 < len(os.Args) {
				outputFile = os.Args[i+1]
				i += 2
			} else {
				i++
			}
		case "-r", "--report":
			if i+1 < len(os.Args) {
				reportFile = os.Args[i+1]
				i += 2
			} else {
				i++
			}
		case "--no-edit":
			noEdit = true
			i++
		case "--no-report":
			noReport = true
			i++
		case "--no-words":
			noWords = true
			i++
		case "--remove-watermark":
			removeWatermark = true
			i++
		case "-h", "--help":
			fmt.Println("Usage: go run . <input_file> [options]")
			fmt.Println("Options:")
			fmt.Println("  -o, --output <file>       Output file (default: <input>.ed.txt)")
			fmt.Println("  -r, --report <file>       Report file (default: report_go-ext.txt)")
			fmt.Println("  --no-edit                 Do not create .ed.txt file")
			fmt.Println("  --no-report               Do not create report file")
			fmt.Println("  --no-words                Exclude word frequency from report")
			fmt.Println("  --remove-watermark        Remove AI watermark characters")
			fmt.Println("  -h, --help                Show help")
			return
		default:
			i++
		}
	}

	// Set default output file if not specified
	if outputFile == "" {
		ext := filepath.Ext(inputFile)
		base := strings.TrimSuffix(inputFile, ext)
		outputFile = base + ".ed.txt"
	}

	// Read input file
	text, err := os.ReadFile(inputFile)
	if err != nil {
		log.Fatalf("Error reading %s: %v", inputFile, err)
	}

	// Process text
	start := time.Now()
	processResult := process(string(text), removeWatermark)

	// Calculate word frequency on sanitized text
	var wordFreq map[string]int
	if !noWords {
		wordFreq = wordFrequency(processResult.Cleaned)
	} else {
		wordFreq = map[string]int{}
	}

	// AI forensic analysis runs on the ORIGINAL text: sanitization
	// replaces disallowed characters with '?', which would corrupt
	// sentence splitting and phrase positions.
	var aiMetrics *AIMetrics
	var aiResult *AIResult
	var aiEvidence []Evidence
	if processResult.Cleaned != "" {
		aiMetrics = calculateAIForensicMetrics(string(text))
		if aiMetrics != nil {
			aiResult = calculateAIProbability(aiMetrics)
			aiEvidence = buildEvidence(string(text), aiMetrics)
		}
	}
	elapsed := time.Since(start)

	// Write output file
	if !noEdit {
		if err := os.WriteFile(outputFile, []byte(processResult.Cleaned), 0644); err != nil {
			log.Printf("Error writing %s: %v", outputFile, err)
		}
	}

	// Generate and write report
	if !noReport {
		reportContent := buildReport(
			inputFile, outputFile,
			processResult.Replaced, processResult.WatermarkRemoved,
			wordFreq, elapsed, aiMetrics, aiResult, aiEvidence,
			removeWatermark, "Go-Ext",
		)
		if err := os.WriteFile(reportFile, []byte(reportContent), 0644); err != nil {
			log.Printf("Error writing %s: %v", reportFile, err)
		}
	}

	// Print summary
	totalReplaced := 0
	for _, count := range processResult.Replaced {
		totalReplaced += count
	}
	totalWatermark := 0
	for _, count := range processResult.WatermarkRemoved {
		totalWatermark += count
	}

	fmt.Printf("Processed in %.6fs\n", elapsed.Seconds())
	fmt.Printf("Replacements: %d\n", totalReplaced)
	fmt.Printf("Watermarks removed: %d\n", totalWatermark)
	if aiResult != nil {
		fmt.Printf("AI Probability: %.1f%% (confidence: %s)\n", aiResult.Probability, aiResult.Confidence)
		if len(aiEvidence) > 0 {
			top := len(aiEvidence)
			if top > 3 {
				top = 3
			}
			fmt.Printf("AI Evidence (top %d of %d):\n", top, len(aiEvidence))
			for i := 0; i < top; i++ {
				ev := aiEvidence[i]
				loc := "text-wide"
				if ev.HasLine {
					loc = fmt.Sprintf("line %d", ev.Line)
				}
				fmt.Printf("  %s: %s\n", loc, ev.Detail)
			}
		}
	}
	fmt.Printf("Output: %s\n", map[bool]string{true: "(skipped)", false: outputFile}[noEdit])
	fmt.Printf("Report: %s\n", map[bool]string{true: "(skipped)", false: reportFile}[noReport])
}
