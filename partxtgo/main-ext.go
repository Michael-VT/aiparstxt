package main

import (
	"fmt"
	"log"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
	"unicode"
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
		0x200C, // Zero Width Non-Joiner (ZWNJ)
		0x200D, // Zero Width Joiner (ZWJ)
		0xFEFF, // Zero Width No-Break Space (ZWNBSP, BOM)
		0x00AD, // Soft Hyphen (SHY)
		0x2060, // Word Joiner
		0x2061, // Function Application
		0x2062, // Invisible Times
		0x2063, // Invisible Separator
		0x2064, // Invisible Plus
		0x202A, // Left-to-Right Embedding
		0x202B, // Right-to-Left Embedding
		0x202C, // Pop Directional Formatting
		0x202D, // Left-to-Right Override
		0x202E, // Right-to-Left Override
		0x2028, // Line Separator
		0x2029, // Paragraph Separator
		0xE0001, // Language Tag
		0x180E: // Mongolian Separator
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
	Cleaned         string
	Replaced        map[rune]int
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
		Cleaned:         out.String(),
		Replaced:        replaced,
		WatermarkRemoved: watermarkRemoved,
	}
}

// =========================================================
// FORENSIC ANALYSIS STRUCTS
// =========================================================

type AIMetrics struct {
	WordCount           int
	SentenceCount       int
	LexicalDiversity    float64
	RepetitionScore     float64
	Entropy             float64
	Burstiness          float64
	PatternRepetition   float64
	PunctuationDensity  float64
	AIPhraseHits        int
	UnicodeSymbols      int
	AvgWordLength       float64
	WordLengthVariance  float64
}

type AIResult struct {
	Probability float64
	Confidence  string
	Scores      map[string]int
}

// =========================================================
// FORENSIC ANALYSIS FUNCTIONS
// =========================================================

func wordFrequency(text string) map[string]int {
	freq := make(map[string]int)
	var currentWord strings.Builder

	stopwords := map[string]bool{
		// English
		"the": true, "be": true, "to": true, "of": true, "and": true, "a": true,
		"in": true, "that": true, "have": true, "i": true, "it": true, "for": true,
		"not": true, "on": true, "with": true, "he": true, "as": true, "you": true,
		"do": true, "at": true, "this": true, "but": true, "his": true, "by": true,
		"from": true, "they": true, "we": true, "say": true, "her": true, "she": true,
		"or": true, "an": true, "will": true, "my": true, "one": true, "all": true,
		"would": true, "there": true, "their": true, "what": true, "so": true,
		"up": true, "out": true, "if": true, "about": true, "who": true, "get": true,
		"which": true, "go": true, "me": true, "when": true, "make": true, "can": true,
		"like": true, "time": true, "no": true, "just": true, "him": true, "know": true,
		"take": true, "people": true, "into": true, "year": true, "your": true,
		"good": true, "some": true, "could": true, "them": true, "see": true,
		"other": true, "than": true,
		// Russian
		"и": true, "в": true, "во": true, "не": true, "что": true, "он": true,
		"на": true, "я": true, "с": true, "со": true, "как": true, "а": true,
		"то": true, "всё": true, "она": true, "так": true, "быть": true,
		"его": true, "к": true, "но": true, "они": true, "мы": true, "ее": true,
		"бы": true, "было": true, "всего": true, "себе": true, "еще": true,
		"нет": true, "может": true, "это": true, "тебя": true, "тем": true,
		"ими": true, "ему": true, "если": true, "уже": true, "или": true,
		"где": true, "зачем": true, "когда": true, "куда": true, "от": true,
		"почему": true, "чем": true, "чтобы": true, "чье": true, "чей": true,
		"кто": true, "чём": true, "кому": true,
	}

	for _, ch := range text {
		if unicode.IsLetter(ch) || ch == '\'' {
			currentWord.WriteRune(unicode.ToLower(ch))
		} else {
			if currentWord.Len() > 0 {
				word := currentWord.String()
				if len(word) > 2 && !stopwords[word] {
					freq[word]++
				}
				currentWord.Reset()
			}
		}
	}

	// Handle last word
	if currentWord.Len() > 0 {
		word := currentWord.String()
		if len(word) > 2 && !stopwords[word] {
			freq[word]++
		}
	}

	return freq
}

func splitSentences(text string) []string {
	var sentences []string
	var current strings.Builder
	sentenceEnd := false

	for _, ch := range text {
		if ch == '.' || ch == '!' || ch == '?' {
			sentenceEnd = true
			current.WriteRune(ch)
		} else if sentenceEnd && unicode.IsSpace(ch) {
			sentenceEnd = false
			if trimmed := strings.TrimSpace(current.String()); len(trimmed) > 3 {
				sentences = append(sentences, trimmed)
			}
			current.Reset()
		} else {
			current.WriteRune(ch)
		}
	}

	// Handle last sentence
	if trimmed := strings.TrimSpace(current.String()); len(trimmed) > 3 {
		sentences = append(sentences, trimmed)
	}

	return sentences
}

func calculateAIForensicMetrics(text string, wordFreq map[string]int) *AIMetrics {
	if len(text) == 0 {
		return nil
	}

	words := strings.Fields(text)
	if len(words) == 0 {
		return nil
	}

	sentences := splitSentences(text)
	if len(sentences) == 0 {
		return nil
	}

	// Core metrics
	wordCount := len(words)
	sentenceCount := len(sentences)

	uniqueWords := make(map[string]bool)
	for _, word := range words {
		uniqueWords[strings.ToLower(word)] = true
	}
	lexicalDiv := float64(len(uniqueWords)) / float64(wordCount)

	// Repetition score
	repeated := 0
	for _, count := range wordFreq {
		if count > 1 {
			repeated++
		}
	}
	repScore := float64(repeated) / float64(len(wordFreq))

	// Entropy calculation
	total := 0
	for _, count := range wordFreq {
		total += count
	}
	entropy := 0.0
	if total > 0 {
		for _, count := range wordFreq {
			p := float64(count) / float64(total)
			entropy -= p * math.Log2(p)
		}
	}

	// Sentence length analysis (burstiness)
	sentLengths := make([]int, len(sentences))
	for i, sent := range sentences {
		sentLengths[i] = len(strings.Fields(sent))
	}

	avgSentLen := 0.0
	for _, length := range sentLengths {
		avgSentLen += float64(length)
	}
	avgSentLen /= float64(len(sentLengths))

	variance := 0.0
	for _, length := range sentLengths {
		diff := float64(length) - avgSentLen
		variance += diff * diff
	}
	variance /= float64(len(sentLengths))

	burstiness := 0.0
	if avgSentLen > 0 {
		burstiness = math.Sqrt(variance) / avgSentLen
	}

	// Pattern repetition
	categorizeLength := func(length int) rune {
		if length < 10 {
			return 'S'
		} else if length < 20 {
			return 'M'
		}
		return 'L'
	}

	patterns := make([]rune, len(sentLengths))
	for i, length := range sentLengths {
		patterns[i] = categorizeLength(length)
	}

	patternCounts := make(map[rune]int)
	for _, pattern := range patterns {
		patternCounts[pattern]++
	}

	repeatedPatterns := 0
	for _, count := range patternCounts {
		if count > 1 {
			repeatedPatterns++
		}
	}
	patternRep := float64(repeatedPatterns) / float64(len(patterns))

	// Punctuation density
	punctCount := 0
	for _, ch := range text {
		switch ch {
		case ',', '.', '!', '?', ';', ':', '(', ')', '-', '—', '–':
			punctCount++
		}
	}
	punctDensity := float64(punctCount) / float64(len(text))

	// AI phrase detection
	aiPhrases := []string{
		"in conclusion", "in summary", "it is worth noting", "it is important to note",
		"basically", "essentially", "furthermore", "moreover", "additionally", "in addition",
		"it could be argued", "one might argue", "it appears that", "seems that",
		"on the other hand", "however", "nevertheless", "nonetheless",
		"as an ai", "as a language model", "i cannot", "i'm not able to",
		"в заключение", "в целом", "важно отметить", "более того", "кроме того",
		"можно утверждать", "можно сказать", "с одной стороны", "с другой стороны",
		"как искусственный интеллект", "как языковая модель", "во-первых", "во-вторых",
	}

	textLower := strings.ToLower(text)
	aiHits := 0
	for _, phrase := range aiPhrases {
		if strings.Contains(textLower, phrase) {
			aiHits++
		}
	}

	// Unicode suspicious characters
	unicodeCount := 0
	for _, ch := range text {
		cp := uint32(ch)
		switch cp {
		case 0x2010, 0x2011, 0x2012, 0x2013, 0x2014,
			0x2018, 0x2019, 0x201B,
			0x201C, 0x201D, 0x201E, 0x201F,
			0x2026, 0x202F, 0x205F, 0x00A0,
			0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005,
			0x2006, 0x2007, 0x2008, 0x2009, 0x200A:
			unicodeCount++
		}
	}

	// Word length statistics
	wordLengths := make([]int, len(words))
	for i, word := range words {
		wordLengths[i] = len([]rune(word))
	}

	avgWordLen := 0.0
	for _, length := range wordLengths {
		avgWordLen += float64(length)
	}
	avgWordLen /= float64(len(wordLengths))

	wordLenVariance := 0.0
	if len(wordLengths) > 1 {
		for _, length := range wordLengths {
			diff := float64(length) - avgWordLen
			wordLenVariance += diff * diff
		}
		wordLenVariance /= float64(len(wordLengths))
		wordLenVariance = math.Sqrt(wordLenVariance)
	}

	return &AIMetrics{
		WordCount:          wordCount,
		SentenceCount:      sentenceCount,
		LexicalDiversity:   lexicalDiv,
		RepetitionScore:    repScore,
		Entropy:            entropy,
		Burstiness:         burstiness,
		PatternRepetition:  patternRep,
		PunctuationDensity: punctDensity,
		AIPhraseHits:       aiHits,
		UnicodeSymbols:     unicodeCount,
		AvgWordLength:      avgWordLen,
		WordLengthVariance: wordLenVariance,
	}
}

func calculateAIProbability(metrics *AIMetrics) *AIResult {
	scores := make(map[string]int)
	total := 0

	// Core metrics with enhanced weighting
	if metrics.LexicalDiversity < 0.45 {
		scores["lexical_diversity"] = 25
		total += 25
	} else if metrics.LexicalDiversity < 0.55 {
		scores["lexical_diversity"] = 15
		total += 15
	}

	if metrics.Entropy < 5.0 {
		scores["entropy"] = 25
		total += 25
	} else if metrics.Entropy < 5.8 {
		scores["entropy"] = 15
		total += 15
	}

	if metrics.Burstiness < 0.35 {
		scores["burstiness"] = 20
		total += 20
	} else if metrics.Burstiness < 0.45 {
		scores["burstiness"] = 10
		total += 10
	}

	if metrics.PatternRepetition > 0.35 {
		scores["pattern_repetition"] = 20
		total += 20
	} else if metrics.PatternRepetition > 0.25 {
		scores["pattern_repetition"] = 10
		total += 10
	}

	if metrics.AIPhraseHits >= 3 {
		scores["ai_phrases"] = 20
		total += 20
	} else if metrics.AIPhraseHits >= 1 {
		scores["ai_phrases"] = 10
		total += 10
	}

	if metrics.RepetitionScore > 0.5 {
		scores["repetition"] = 15
		total += 15
	}

	if metrics.PunctuationDensity > 0.04 {
		scores["punctuation"] = 5
		total += 5
	}

	if metrics.UnicodeSymbols > 0 {
		scores["unicode"] = 5
		total += 5
	}

	// Extended metrics
	if metrics.AvgWordLength < 4.0 {
		scores["word_length"] = 10
		total += 10
	} else if metrics.AvgWordLength < 4.5 {
		scores["word_length"] = 5
		total += 5
	}

	if metrics.WordLengthVariance < 1.5 {
		scores["word_variance"] = 8
		total += 8
	}

	// Length-based confidence adjustment
	var confidenceFactor float64
	var confidence string
	if metrics.WordCount < 300 {
		confidenceFactor = 0.8
		confidence = "LOW"
	} else if metrics.WordCount < 1000 {
		confidenceFactor = 0.9
		confidence = "MEDIUM"
	} else {
		confidenceFactor = 1.0
		confidence = "HIGH"
	}

	adjustedTotal := float64(total) * confidenceFactor
	probability := math.Min(100.0, adjustedTotal)

	return &AIResult{
		Probability: probability,
		Confidence:  confidence,
		Scores:      scores,
	}
}

func getInterpretation(metrics *AIMetrics, aiProbability float64, confidence string) (string, []string) {
	var interpretations []string

	verdict := ""
	if aiProbability > 60.0 {
		verdict = fmt.Sprintf("High probability of AI-generated content (%.1f%%)", aiProbability)
	} else if aiProbability > 30.0 {
		verdict = fmt.Sprintf("Moderate probability of AI involvement (%.1f%%)", aiProbability)
	} else if aiProbability > 10.0 {
		verdict = fmt.Sprintf("Low probability of AI-generated content (%.1f%%)", aiProbability)
	} else {
		verdict = fmt.Sprintf("Text appears predominantly human-written (%.1f%%)", aiProbability)
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

	if metrics.Burstiness < 0.35 {
		interpretations = append(interpretations, "⚠️ Low burstiness - overly uniform sentence structure")
	} else if metrics.Burstiness > 0.7 {
		interpretations = append(interpretations, "✓ Good burstiness - natural sentence variation")
	}

	if metrics.AIPhraseHits > 0 {
		interpretations = append(interpretations, fmt.Sprintf("⚠️ Found %d AI-typical phrases", metrics.AIPhraseHits))
	}

	if metrics.PatternRepetition > 0.35 {
		interpretations = append(interpretations, "⚠️ High pattern repetition - template-like structure")
	}

	if metrics.UnicodeSymbols > 0 {
		interpretations = append(interpretations, fmt.Sprintf("⚠️ Found %d suspicious Unicode characters", metrics.UnicodeSymbols))
	}

	return verdict, interpretations
}

// =========================================================
// REPORTING FUNCTIONS
// =========================================================

func buildReport(inputFile, outputFile string, replaced, watermarkRemoved map[rune]int,
	wordFreq map[string]int, elapsed time.Duration, aiMetrics *AIMetrics, aiResult *AIResult,
	removeWatermark bool, lang string) string {

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
		builder.WriteString(fmt.Sprintf("  Lexical diversity:     %.3f\n", aiMetrics.LexicalDiversity))
		builder.WriteString(fmt.Sprintf("  Repetition score:      %.3f\n", aiMetrics.RepetitionScore))
		builder.WriteString(fmt.Sprintf("  Entropy:               %.3f\n", aiMetrics.Entropy))
		builder.WriteString(fmt.Sprintf("  Burstiness:            %.3f\n", aiMetrics.Burstiness))
		builder.WriteString(fmt.Sprintf("  Pattern repetition:    %.3f\n", aiMetrics.PatternRepetition))
		builder.WriteString(fmt.Sprintf("  Punctuation density:   %.3f\n", aiMetrics.PunctuationDensity))
		builder.WriteString(fmt.Sprintf("  AI phrase hits:        %d\n", aiMetrics.AIPhraseHits))
		builder.WriteString(fmt.Sprintf("  Unicode suspicious:    %d\n", aiMetrics.UnicodeSymbols))
		builder.WriteString(fmt.Sprintf("  Avg word length:       %.2f\n", aiMetrics.AvgWordLength))
		builder.WriteString(fmt.Sprintf("  Word length variance:  %.2f\n", aiMetrics.WordLengthVariance))
		builder.WriteString("\n")

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
	elapsed := time.Since(start)

	// Calculate forensic metrics
	wordFreq := map[string]int{}
	if !noWords {
		wordFreq = wordFrequency(processResult.Cleaned)
	}
	aiMetrics := calculateAIForensicMetrics(processResult.Cleaned, wordFreq)
	var aiResult *AIResult
	if aiMetrics != nil {
		aiResult = calculateAIProbability(aiMetrics)
	}

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
			wordFreq, elapsed, aiMetrics, aiResult,
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
	}
	fmt.Printf("Output: %s\n", map[bool]string{true: "(skipped)", false: outputFile}[noEdit])
	fmt.Printf("Report: %s\n", map[bool]string{true: "(skipped)", false: reportFile}[noReport])
}
