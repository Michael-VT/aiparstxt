#!/usr/bin/env python3
"""aiparstxt — Text sanitizer. Replaces or removes disallowed characters."""

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

# AI Watermark Characters (невидимые маркеры, которые ИИ-системы используют для watermarking)
WATERMARK_CHARS = set([
    '\u200B',  # Zero Width Space (ZWSP) - самый частый маркер
    '\u200C',  # Zero Width Non-Joiner (ZWNJ)
    '\u200D',  # Zero Width Joiner (ZWJ)
    '\uFEFF',  # Zero Width No-Break Space (ZWNBSP, BOM)
    '\u00AD',  # Soft Hyphen (SHY)
    '\u2060',  # Word Joiner
    '\u2061',  # Function Application
    '\u2062',  # Invisible Times
    '\u2063',  # Invisible Separator
    '\u2064',  # Invisible Plus
    '\u202A',  # Left-to-Right Embedding
    '\u202B',  # Right-to-Left Embedding
    '\u202C',  # Pop Directional Formatting
    '\u202D',  # Left-to-Right Override
    '\u202E',  # Right-to-Left Override
    '\u2028',  # Line Separator
    '\u2029',  # Paragraph Separator
    '\uFE00', '\uFE01', '\uFE02', '\uFE03', '\uFE04', '\uFE05', '\uFE06', '\uFE07',
    '\uFE08', '\uFE09', '\uFE0A', '\uFE0B', '\uFE0C', '\uFE0D', '\uFE0E', '\uFE0F',  # Variation Selectors 1-16
    '\uE0001',  # Language Tag
    '\u180E',  # Mongolian Separator (often abused as watermark)
])
# Tag characters (E0020-E007F)
for cp in range(0xE0020, 0xE0080):
    WATERMARK_CHARS.add(chr(cp))
# Private Use Area - commonly abused for watermarking (E000-E07F, 128 chars)
for cp in range(0xE000, 0xE080):
    WATERMARK_CHARS.add(chr(cp))


def process(text, replacement="?", remove=False, remove_watermark=False):
    replaced = Counter()
    watermark_removed = Counter()
    out = []
    for ch in text:
        # Сначала проверяем watermark - он удаляется всегда, если включено
        if remove_watermark and ch in WATERMARK_CHARS:
            watermark_removed[ch] += 1
            continue
        if ch in ALLOWED:
            out.append(ch)
        else:
            replaced[ch] += 1
            if not remove:
                out.append(replacement)
    return "".join(out), replaced, watermark_removed



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


def build_report(input_file, output_file, replaced, watermark_removed, word_freq, elapsed, lang="Python", replacement="?", remove=False, remove_watermark=False):
    lines = []
    lines.append(f"=== aiparstxt Report ({lang}) ===")
    import datetime
    lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Input file: {input_file}")
    lines.append(f"Output file: {output_file}")
    mode = "remove" if remove else f"replace with '{replacement}'"
    if remove_watermark:
        mode += " + watermark removal"
    lines.append(f"Mode: {mode}")
    lines.append(f"Execution time: {elapsed:.6f} s")
    lines.append("")
    if watermark_removed:
        lines.append("--- Watermark Characters Removed ---")
        for ch, cnt in sorted(watermark_removed.items(), key=lambda x: -x[1]):
            lines.append(f"U+{ord(ch):04X} : {cnt}")
        lines.append(f"Total watermark chars removed: {sum(watermark_removed.values())}")
        lines.append("")
    lines.append("--- Replaced Characters ---")
    action = "removed" if remove else f"→ {replacement}"
    if replaced:
        for ch, cnt in sorted(replaced.items(), key=lambda x: -x[1]):
            display = ch if ch != "\n" else "\\n"
            display = display if ch != "\t" else "\\t"
            lines.append(f"{display} {action} : {cnt}")
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
    parser.add_argument("--replace", metavar="CHAR", default="?", help="Replacement character (default: '?')")
    parser.add_argument("--remove", action="store_true", help="Remove disallowed characters instead of replacing")
    parser.add_argument("--remove-watermark", action="store_true", help="Remove AI watermark characters (zero-width, invisible formatting)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".ed.txt")
    report_path = Path(args.report) if args.report else Path("report_py.txt")

    start = time.perf_counter()
    text = input_path.read_text(encoding="utf-8")
    cleaned, replaced, watermark_removed = process(text, replacement=args.replace, remove=args.remove, remove_watermark=args.remove_watermark)

    word_freq = None if args.no_words else word_frequency(cleaned)
    elapsed = time.perf_counter() - start

    if not args.no_edit:
        output_path.write_text(cleaned, encoding="utf-8")

    if not args.no_report:
        report = build_report(str(input_path), str(output_path), replaced, watermark_removed, word_freq, elapsed, replacement=args.replace, remove=args.remove, remove_watermark=args.remove_watermark)
        report_path.write_text(report, encoding="utf-8")

    print(f"Done in {elapsed:.6f}s. Replacements: {sum(replaced.values()) if replaced else 0}, Watermark removed: {sum(watermark_removed.values()) if watermark_removed else 0}")




if __name__ == "__main__":
    main()
