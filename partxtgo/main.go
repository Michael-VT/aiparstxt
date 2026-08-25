package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

var allowed = func() map[rune]bool {
	m := make(map[rune]bool)
	for _, ch := range "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" +
		"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" +
		"ҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ[]{}():()-=_+!@#$%&*;'/.,<>\"`~—«» \t\n\r" {
		m[ch] = true
	}
	return m
}()

// AI Watermark Characters (невидимые маркеры, которые ИИ-системы используют для watermarking)
var watermarkChars = func() map[rune]bool {
	m := make(map[rune]bool)
	// Zero Width Characters
	watermarks := []rune{
		'\u200B', // Zero Width Space (ZWSP)
		'\u200C', // Zero Width Non-Joiner (ZWNJ)
		'\u200D', // Zero Width Joiner (ZWJ)
		'\uFEFF', // Zero Width No-Break Space (ZWNBSP, BOM)
		'\u00AD', // Soft Hyphen (SHY)
		'\u2060', // Word Joiner
		'\u2061', // Function Application
		'\u2062', // Invisible Times
		'\u2063', // Invisible Separator
		'\u2064', // Invisible Plus
		'\u202A', // Left-to-Right Embedding
		'\u202B', // Right-to-Left Embedding
		'\u202C', // Pop Directional Formatting
		'\u202D', // Left-to-Right Override
		'\u202E', // Right-to-Left Override
		'\u2028', // Line Separator
		'\u2029', // Paragraph Separator
		'\u180E', // Mongolian Separator (often abused as watermark)
	}

	for _, ch := range watermarks {
		m[ch] = true
	}
	// Variation Selectors (FE00-FE0F)
	for cp := 0xFE00; cp <= 0xFE0F; cp++ {
		m[rune(cp)] = true
	}
	// Tag characters (E0020-E007F)
	for cp := 0xE0020; cp <= 0xE007F; cp++ {
		m[rune(cp)] = true
	}
	m[rune(0xE0001)] = true // Language Tag
	// Private Use Area - commonly abused for watermarking (E000-E07F, 128 chars)
	for cp := 0xE000; cp <= 0xE07F; cp++ {
		m[rune(cp)] = true
	}


	return m
}()

type replacement struct {
	ch  rune
	cnt int
}




func process(text string, removeWatermark bool) (string, map[rune]int, map[rune]int) {
	replaced := make(map[rune]int)
	watermarkRemoved := make(map[rune]int)
	var out strings.Builder
	out.Grow(len(text))
	for _, ch := range text {


		// Сначала проверяем watermark - он удаляется всегда, если включено
		if removeWatermark && watermarkChars[ch] {
			watermarkRemoved[ch]++
			continue
		}


		if allowed[ch] {
			out.WriteRune(ch)
		} else {
			replaced[ch]++
			out.WriteRune('?')
		}
	}
	return out.String(), replaced, watermarkRemoved
}


func wordFrequency(text string) map[string]int {
	freq := make(map[string]int)
	var cur strings.Builder
	for _, ch := range text {
		if isAlphaNum(ch) || ch == '\'' || ch == '-' {
			cur.WriteRune(ch)
		} else {
			if cur.Len() > 0 {
				freq[cur.String()]++
				cur.Reset()
			}
		}
	}
	if cur.Len() > 0 {
		freq[cur.String()]++
	}
	return freq
}

func isAlphaNum(ch rune) bool {
	return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
		(ch >= 'а' && ch <= 'я') || (ch >= 'А' && ch <= 'Я') ||
		ch == 'ё' || ch == 'Ё' ||
		(ch >= '0' && ch <= '9')
}

func buildReport(inputFile, outputFile string, replaced map[rune]int, watermarkRemoved map[rune]int, wordFreq *map[string]int, elapsed time.Duration, removeWatermark bool) string {
	var lines []string
	lines = append(lines, "=== aiparstxt Report (Go) ===")
	lines = append(lines, fmt.Sprintf("Date: %s", time.Now().Format("2006-01-02 15:04:05")))
	lines = append(lines, fmt.Sprintf("Input file: %s", inputFile))
	lines = append(lines, fmt.Sprintf("Output file: %s", outputFile))
	mode := "replace with '?'"
	if removeWatermark {
		mode += " + watermark removal"
	}
	lines = append(lines, fmt.Sprintf("Mode: %s", mode))
	lines = append(lines, fmt.Sprintf("Execution time: %.6f s", elapsed.Seconds()))
	lines = append(lines, "")
	if len(watermarkRemoved) > 0 {
		lines = append(lines, "--- Watermark Characters Removed ---")
		type wmRep struct {
			ch  rune
			cnt int
		}
		var sorted []wmRep
		total := 0
		for ch, cnt := range watermarkRemoved {
			sorted = append(sorted, wmRep{ch, cnt})
			total += cnt
		}
		sort.Slice(sorted, func(i, j int) bool {
			return sorted[i].cnt > sorted[j].cnt
		})
		for _, r := range sorted {
			lines = append(lines, fmt.Sprintf("U+%04X : %d", r.ch, r.cnt))
		}
		lines = append(lines, fmt.Sprintf("Total watermark chars removed: %d", total))
		lines = append(lines, "")
	}
	lines = append(lines, "--- Replaced Characters ---")
	if len(replaced) == 0 {
		lines = append(lines, "None")
	} else {
		var sorted []replacement
		total := 0
		for ch, cnt := range replaced {
			sorted = append(sorted, replacement{ch, cnt})
			total += cnt
		}
		sort.Slice(sorted, func(i, j int) bool {
			return sorted[i].cnt > sorted[j].cnt
		})
		for _, r := range sorted {
			display := string(r.ch)
			if r.ch == '\n' {
				display = "\\n"
			} else if r.ch == '\t' {
				display = "\\t"
			}
			lines = append(lines, fmt.Sprintf("%s → ? : %d", display, r.cnt))
		}
		lines = append(lines, fmt.Sprintf("Total replacements: %d", total))
	}
	lines = append(lines, "")
	lines = append(lines, "--- Word Frequency (ascending) ---")
	if wordFreq != nil {
		wf := *wordFreq
		if len(wf) == 0 {
			lines = append(lines, "None")
		} else {
			type kv struct {
				word string
				cnt  int
			}
			var sorted []kv
			totalWords := 0
			for w, c := range wf {
				sorted = append(sorted, kv{w, c})
				totalWords += c
			}
			sort.Slice(sorted, func(i, j int) bool {
				return sorted[i].cnt < sorted[j].cnt
			})
			for _, s := range sorted {
				lines = append(lines, fmt.Sprintf("%s: %d", s.word, s.cnt))
			}
			lines = append(lines, fmt.Sprintf("Total unique words: %d", len(wf)))
			lines = append(lines, fmt.Sprintf("Total words: %d", totalWords))
		}
	} else {
		lines = append(lines, "(skipped)")
	}
	return strings.Join(lines, "\n") + "\n"
}


func main() {
	// Accept options both before and after the positional input file, matching
	// the CLI behavior of the other implementations.
	var options, positional []string
	for i := 1; i < len(os.Args); i++ {
		arg := os.Args[i]
		if arg == "-o" || arg == "--output" || arg == "-r" || arg == "--report" {
			options = append(options, arg)
			if i+1 < len(os.Args) {
				options = append(options, os.Args[i+1])
				i++
			}
		} else if strings.HasPrefix(arg, "-") {
			options = append(options, arg)
		} else {
			positional = append(positional, arg)
		}
	}
	os.Args = append([]string{os.Args[0]}, append(options, positional...)...)

	output := flag.String("o", "", "Output file (default: <input>.ed.txt)")
	outputLong := flag.String("output", "", "Output file (default: <input>.ed.txt)")
	report := flag.String("r", "", "Report file (default: report_go.txt)")
	reportLong := flag.String("report", "", "Report file (default: report_go.txt)")
	noEdit := flag.Bool("no-edit", false, "Do not create .ed.txt file")
	noReport := flag.Bool("no-report", false, "Do not create report file")
	noWords := flag.Bool("no-words", false, "Exclude word frequency from report")
	removeWatermark := flag.Bool("remove-watermark", false, "Remove AI watermark characters (zero-width, invisible formatting)")
	flag.Bool("w", false, "Exclude word frequency from report (shorthand)")
	flag.Parse()



	outFile := *output
	if outFile == "" {
		outFile = *outputLong
	}
	repFile := *report
	if repFile == "" {
		repFile = *reportLong
	}
	// Handle -w shorthand
	noW := *noWords
	flag.Visit(func(f *flag.Flag) {
		if f.Name == "w" {
			noW = true
		}
	})

	args := flag.Args()
	if len(args) < 1 {
		fmt.Fprintf(os.Stderr, "Usage: partxt <input_file> [options]\n")
		flag.PrintDefaults()
		os.Exit(1)
	}
	inputPath := args[0]

	data, err := os.ReadFile(inputPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	if outFile == "" {
		ext := filepath.Ext(inputPath)
		stem := strings.TrimSuffix(inputPath, ext)
		outFile = stem + ".ed" + ext
	}
	if repFile == "" {
		repFile = "report_go.txt"
	}

	start := time.Now()
	text := string(data)
	cleaned, replaced, watermarkRemoved := process(text, *removeWatermark)

	var wfPtr *map[string]int
	if !noW {
		wf := wordFrequency(cleaned)
		wfPtr = &wf
	}
	elapsed := time.Since(start)

	if !*noEdit {
		os.WriteFile(outFile, []byte(cleaned), 0644)
	}

	if !*noReport {
		rpt := buildReport(inputPath, outFile, replaced, watermarkRemoved, wfPtr, elapsed, *removeWatermark)

		os.WriteFile(repFile, []byte(rpt), 0644)
	}

	// Debug: print watermarkChars size


	total := 0
	for _, c := range replaced {
		total += c
	}
	wmTotal := 0
	for _, c := range watermarkRemoved {
		wmTotal += c
	}
	fmt.Printf("Done in %.6fs. Replacements: %d, Watermark removed: %d\n", elapsed.Seconds(), total, wmTotal)

}
