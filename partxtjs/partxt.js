#!/usr/bin/env bun
"use strict";

const fs = require("fs");
const path = require("path");

const ALLOWED = new Set(
  "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" +
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" +
    "[]{}()-=_+!@#$%&*;'/.,<>'\"`~ \t\n\r".split("")
);

function processText(text) {
  const replaced = new Map();
  const out = [];
  for (const ch of text) {
    if (ALLOWED.has(ch)) {
      out.push(ch);
    } else {
      replaced.set(ch, (replaced.get(ch) || 0) + 1);
      out.push("?");
    }
  }
  return { cleaned: out.join(""), replaced };
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

function buildReport(inputFile, outputFile, replaced, wordFreq, elapsed) {
  const lines = [];
  const now = new Date().toISOString().replace("T", " ").slice(0, 19);
  lines.push("=== aiparstxt Report (Bun) ===");
  lines.push(`Date: ${now}`);
  lines.push(`Input file: ${inputFile}`);
  lines.push(`Output file: ${outputFile}`);
  lines.push(`Execution time: ${elapsed.toFixed(6)} s`);
  lines.push("");
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
  const args = { input: null, output: null, report: null, noEdit: false, noReport: false, noWords: false };
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
    } else if (a === "-h" || a === "--help") {
      console.log("Usage: partxt <input_file> [options]");
      console.log("  -o, --output <file>   Output file");
      console.log("  -r, --report <file>   Report file");
      console.log("  --no-edit             Do not create .ed.txt");
      console.log("  --no-report           Do not create report");
      console.log("  -w, --no-words        Exclude word frequency");
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
  const reportFile = args.report || "report_bun.txt";

  const start = performance.now();
  const text = fs.readFileSync(inputFile, "utf-8");
  const { cleaned, replaced } = processText(text);
  const wordFreq = args.noWords ? null : wordFrequency(cleaned);
  const elapsed = (performance.now() - start) / 1000;

  if (!args.noEdit) {
    fs.writeFileSync(outputFile, cleaned, "utf-8");
  }

  if (!args.noReport) {
    const report = buildReport(inputFile, outputFile, replaced, wordFreq, elapsed);
    fs.writeFileSync(reportFile, report, "utf-8");
  }

  let total = 0;
  for (const c of replaced.values()) total += c;
  console.log(`Done in ${elapsed.toFixed(6)}s. Replacements: ${total}`);
}

main();
