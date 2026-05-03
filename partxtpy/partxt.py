#!/usr/bin/env python3
"""aiparstxt — Text sanitizer. Replaces disallowed characters with '?'."""

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

ALLOWED = set()
ALLOWED.update("0123456789")
ALLOWED.update("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
ALLOWED.update("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя")
ALLOWED.update("[]{}()-=_+!@#$%&*;'/.,<>"
               "'"
               '"`~')
ALLOWED.update(" \t\n\r")


def process(text):
    replaced = Counter()
    out = []
    for ch in text:
        if ch in ALLOWED:
            out.append(ch)
        else:
            replaced[ch] += 1
            out.append("?")
    return "".join(out), replaced


def word_frequency(text):
    words = []
    cur = []
    for ch in text:
        if ch.isalnum() or ch in ("'", "-"):
            cur.append(ch)
        else:
            if cur:
                words.append("".join(cur))
                cur = []
    if cur:
        words.append("".join(cur))
    return Counter(words)


def build_report(input_file, output_file, replaced, word_freq, elapsed, lang="Python"):
    lines = []
    lines.append(f"=== aiparstxt Report ({lang}) ===")
    import datetime
    lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Input file: {input_file}")
    lines.append(f"Output file: {output_file}")
    lines.append(f"Execution time: {elapsed:.6f} s")
    lines.append("")
    lines.append("--- Replaced Characters ---")
    if replaced:
        for ch, cnt in sorted(replaced.items(), key=lambda x: -x[1]):
            display = ch if ch != "\n" else "\\n"
            display = display if ch != "\t" else "\\t"
            lines.append(f"{display} → ? : {cnt}")
        lines.append(f"Total replacements: {sum(replaced.values())}")
    else:
        lines.append("None")
    lines.append("")
    lines.append("--- Word Frequency (ascending) ---")
    if word_freq:
        for word, cnt in sorted(word_freq.items(), key=lambda x: x[1]):
            lines.append(f"{word}: {cnt}")
        lines.append(f"Total unique words: {len(word_freq)}")
        lines.append(f"Total words: {sum(word_freq.values())}")
    else:
        lines.append("None")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="aiparstxt — text sanitizer")
    parser.add_argument("input", help="Input text file")
    parser.add_argument("-o", "--output", help="Output file (default: <input>.ed.txt)")
    parser.add_argument("-r", "--report", help="Report file (default: report_py.txt)")
    parser.add_argument("--no-edit", action="store_true", help="Do not create .ed.txt file")
    parser.add_argument("--no-report", action="store_true", help="Do not create report file")
    parser.add_argument("-w", "--no-words", action="store_true", help="Exclude word frequency from report")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".ed.txt")
    report_path = Path(args.report) if args.report else Path("report_py.txt")

    start = time.perf_counter()
    text = input_path.read_text(encoding="utf-8")
    cleaned, replaced = process(text)
    word_freq = None if args.no_words else word_frequency(cleaned)
    elapsed = time.perf_counter() - start

    if not args.no_edit:
        output_path.write_text(cleaned, encoding="utf-8")

    if not args.no_report:
        report = build_report(str(input_path), str(output_path), replaced, word_freq, elapsed)
        report_path.write_text(report, encoding="utf-8")

    print(f"Done in {elapsed:.6f}s. Replacements: {sum(replaced.values()) if replaced else 0}")


if __name__ == "__main__":
    main()
