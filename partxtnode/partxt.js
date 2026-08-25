#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const ALLOWED = new Set(
  "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" +
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" +
    "[]{}()-=_+!@#$%&*;'/.,<>'\"`~ \t\n\r".split("")
);

for (const ch of "ҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ—«»") ALLOWED.add(ch);
ALLOWED.add(":");
ALLOWED.delete("|");

// AI Watermark Characters (невидимые маркеры, которые ИИ-системы используют для watermarking)
const WATERMARK_CHARS = new Set([
  "\u200B", // Zero Width Space (ZWSP)
  "\u200C", // Zero Width Non-Joiner (ZWNJ)
  "\u200D", // Zero Width Joiner (ZWJ)
  "\uFEFF", // Zero Width No-Break Space (ZWNBSP, BOM)
  "\u00AD", // Soft Hyphen (SHY)
  "\u2060", // Word Joiner
  "\u2061", // Function Application
  "\u2062", // Invisible Times
  "\u2063", // Invisible Separator
  "\u2064", // Invisible Plus
  "\u202A", // Left-to-Right Embedding
  "\u202B", // Right-to-Left Embedding
  "\u202C", // Pop Directional Formatting
  "\u202D", // Left-to-Right Override
  "\u202E", // Right-to-Left Override
  "\u2028", // Line Separator
  "\u2029", // Paragraph Separator
  "\uE0001", // Language Tag
  "\u180E", // Mongolian Separator (often abused as watermark)
]);
// Variation Selectors (FE00-FE0F)
for (let cp = 0xFE00; cp <= 0xFE0F; cp++) {
  WATERMARK_CHARS.add(String.fromCodePoint(cp));
}
// Tag characters (E0020-E007F)
for (let cp = 0xE0020; cp <= 0xE007F; cp++) {
  WATERMARK_CHARS.add(String.fromCodePoint(cp));
}
// Private Use Area - commonly abused for watermarking (E000-E07F, 128 chars)
for (let cp = 0xE000; cp <= 0xE07F; cp++) {
  WATERMARK_CHARS.add(String.fromCodePoint(cp));
}


function processText(text, removeWatermark = false) {
  const replaced = new Map();
  const watermarkRemoved = new Map();
  const out = [];
  for (const ch of text) {
    // Сначала проверяем watermark - он удаляется всегда, если включено
    if (removeWatermark && WATERMARK_CHARS.has(ch)) {
      watermarkRemoved.set(ch, (watermarkRemoved.get(ch) || 0) + 1);
      continue;
    }
    if (ALLOWED.has(ch)) {
      out.push(ch);
    } else {
      replaced.set(ch, (replaced.get(ch) || 0) + 1);
      out.push("?");
    }
  }
  return { cleaned: out.join(""), replaced, watermarkRemoved };
}

function wordFrequency(text) {
  const freq = new Map();
  let cur = "";
  for (const ch of text) {
    if (isAlphaNum(ch) || ch === "'" || ch === "-") {
      cur += ch;
    } else {
      if (cur) {
        freq.set(cur, (freq.get(cur) || 0) + 1);
        cur = "";
      }
    }
  }
  if (cur) freq.set(cur, (freq.get(cur) || 0) + 1);
  return freq;
}

function isAlphaNum(ch) {
  const c = ch.charCodeAt(0);
  return (
    (c >= 48 && c <= 57) ||
    (c >= 65 && c <= 90) ||
    (c >= 97 && c <= 122) ||
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя".includes(ch)
  );
}

function buildReport(inputFile, outputFile, replaced, watermarkRemoved, wordFreq, elapsed, removeWatermark = false) {
  const lines = [];
  const now = new Date().toISOString().replace("T", " ").slice(0, 19);
  lines.push("=== aiparstxt Report (Node.js) ===");
  lines.push(`Date: ${now}`);
  lines.push(`Input file: ${inputFile}`);
  lines.push(`Output file: ${outputFile}`);
  let mode = "replace with '?'";
  if (removeWatermark) mode += " + watermark removal";
  lines.push(`Mode: ${mode}`);
  lines.push(`Execution time: ${elapsed.toFixed(6)} s`);
  lines.push("");
  if (watermarkRemoved && watermarkRemoved.size > 0) {
    lines.push("--- Watermark Characters Removed ---");
    const sorted = [...watermarkRemoved.entries()].sort((a, b) => b[1] - a[1]);
    let total = 0;
    for (const [ch, cnt] of sorted) {
      const cp = ch.codePointAt(0);
      lines.push(`U+${cp.toString(16).toUpperCase().padStart(4, "0")} : ${cnt}`);
      total += cnt;
    }
    lines.push(`Total watermark chars removed: ${total}`);
    lines.push("");
  }
  lines.push("--- Replaced Characters ---");
  if (replaced.size === 0) {
    lines.push("None");
  } else {
    const sorted = [...replaced.entries()].sort((a, b) => b[1] - a[1]);
    let total = 0;
    for (const [ch, cnt] of sorted) {
      const display = ch === "\n" ? "\\n" : ch === "\t" ? "\\t" : ch;
      lines.push(`${display} → ? : ${cnt}`);
      total += cnt;
    }
    lines.push(`Total replacements: ${total}`);
  }
  lines.push("");
  lines.push("--- Word Frequency (ascending) ---");
  if (wordFreq) {
    if (wordFreq.size === 0) {
      lines.push("None");
    } else {
      const sorted = [...wordFreq.entries()].sort((a, b) => a[1] - b[1]);
      let totalWords = 0;
      for (const [word, cnt] of sorted) {
        lines.push(`${word}: ${cnt}`);
        totalWords += cnt;
      }
      lines.push(`Total unique words: ${wordFreq.size}`);
      lines.push(`Total words: ${totalWords}`);
    }
  } else {
    lines.push("(skipped)");
  }
  return lines.join("\n") + "\n";
}

function parseArgs(argv) {
  const args = { input: null, output: null, report: null, noEdit: false, noReport: false, noWords: false, removeWatermark: false };
  let i = 2;
  while (i < argv.length) {
    const a = argv[i];
    if ((a === "-o" || a === "--output") && i + 1 < argv.length) {
      args.output = argv[++i];
    } else if ((a === "-r" || a === "--report") && i + 1 < argv.length) {
      args.report = argv[++i];
    } else if (a === "--no-edit") {
      args.noEdit = true;
    } else if (a === "--no-report") {
      args.noReport = true;
    } else if (a === "-w" || a === "--no-words") {
      args.noWords = true;
    } else if (a === "--remove-watermark") {
      args.removeWatermark = true;
    } else if (a === "-h" || a === "--help") {
      console.log("Usage: partxt <input_file> [options]");
      console.log("  -o, --output <file>   Output file");
      console.log("  -r, --report <file>   Report file");
      console.log("  --no-edit             Do not create .ed.txt");
      console.log("  --no-report           Do not create report");
      console.log("  -w, --no-words        Exclude word frequency");
      console.log("  --remove-watermark    Remove AI watermark characters");
      process.exit(0);
    } else if (!args.input) {
      args.input = a;
    }
    i++;
  }
  return args;
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.input) {
    console.error("Usage: partxt <input_file> [options]");
    process.exit(1);
  }

  if (!fs.existsSync(args.input)) {
    console.error(`Error: file not found: ${args.input}`);
    process.exit(1);
  }

  const inputFile = args.input;
  const outputFile = args.output || inputFile.replace(/\.txt$/, ".ed.txt");
  const reportFile = args.report || "report_node.txt";

  const start = performance.now();
  const text = fs.readFileSync(inputFile, "utf-8");
  const { cleaned, replaced, watermarkRemoved } = processText(text, args.removeWatermark);
  const wordFreq = args.noWords ? null : wordFrequency(cleaned);
  const elapsed = (performance.now() - start) / 1000;

  if (!args.noEdit) {
    fs.writeFileSync(outputFile, cleaned, "utf-8");
  }

  if (!args.noReport) {
    const report = buildReport(inputFile, outputFile, replaced, watermarkRemoved, wordFreq, elapsed, args.removeWatermark);
    fs.writeFileSync(reportFile, report, "utf-8");
  }

  let total = 0;
  for (const c of replaced.values()) total += c;
  let wmTotal = 0;
  if (watermarkRemoved) {
    for (const c of watermarkRemoved.values()) wmTotal += c;
  }
  console.log(`Done in ${elapsed.toFixed(6)}s. Replacements: ${total}, Watermark removed: ${wmTotal}`);
}

main();
