#!/usr/bin/env python3
"""aiparstxt — Text sanitizer with multi-language support. Replaces or removes disallowed characters."""

import argparse
from collections import Counter
from pathlib import Path
import time
import sys
import re

# Base character sets (common to all languages)
BASE_LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
RUSSIAN_CYRILLIC = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
UKRAINIAN_CYRILLIC = "ҐґЄєІіЇї"
PORTUGUESE_LATIN = "àáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ"
DIGITS = "0123456789"
PUNCTUATION = "[]{}():()-=_+!@#$%&*;'/.,<>\"'`~—«»"
WHITESPACE = " \t\n\r"

# Language-specific character sets
LANGUAGE_CHARS = {
    'en': {
        'name': 'English',
        'chars': BASE_LATIN,
        'extra': ''
    },
    'ru': {
        'name': 'Русский',
        'chars': BASE_LATIN + RUSSIAN_CYRILLIC,
        'extra': 'Ёё'
    },
    'uk': {
        'name': 'Українська',
        'chars': BASE_LATIN + RUSSIAN_CYRILLIC + UKRAINIAN_CYRILLIC,
        'extra': 'ҐґЄєІіЇї'
    },
    'fr': {
        'name': 'Français',
        'chars': BASE_LATIN + RUSSIAN_CYRILLIC + 'àâçéèêëîïôùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŸŒÆ',
        'extra': 'àâçéèêëîïôùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŸŒÆ'
    },
    'de': {
        'name': 'Deutsch',
        'chars': BASE_LATIN + RUSSIAN_CYRILLIC + 'äöüßÄÖÜ',
        'extra': 'äöüßÄÖÜ'
    },
    'pt': {
        'name': 'Português',
        'chars': BASE_LATIN + RUSSIAN_CYRILLIC + PORTUGUESE_LATIN,
        'extra': 'àáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ'
    }
}

# Universal character set (all supported languages combined)
UNIVERSAL_CHARS = (
    BASE_LATIN + RUSSIAN_CYRILLIC + UKRAINIAN_CYRILLIC + PORTUGUESE_LATIN
)

# AI Watermark Characters
WATERMARK_CHARS = set([
    '\u200B',  # Zero Width Space
    '\u200C',  # Zero Width Non-Joiner
    '\u200D',  # Zero Width Joiner
    '\uFEFF',  # Zero Width No-Break Space
    '\u00AD',  # Soft Hyphen
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
    '\u2066',  # Left-to-Right Isolate
    '\u2067',  # Right-to-Left Isolate
    '\u2068',  # First Strong Isolate
    '\u2069',  # Pop Directional Isolate
    '\u180E',  # Mongolian Separator
    '\uE0001', # Language Tag
])
# Variation selectors (FE00-FE0F)
for cp in range(0xFE00, 0xFE10):
    WATERMARK_CHARS.add(chr(cp))
# Tag characters (E0020-E007F)
for cp in range(0xE0020, 0xE0080):
    WATERMARK_CHARS.add(chr(cp))
# Private Use Area - commonly abused for watermarking (E000-E07F, 128 chars)
for cp in range(0xE000, 0xE080):
    WATERMARK_CHARS.add(chr(cp))


def detect_language(text):
    """
    Auto-detect language based on character frequency.
    Returns language code or 'universal' if unclear.
    """
    char_counts = Counter(text)

    # Count language-specific characters
    lang_scores = {}
    for lang_code, lang_data in LANGUAGE_CHARS.items():
        score = sum(char_counts.get(c, 0) for c in lang_data['extra'])
        if score > 0:
            lang_scores[lang_code] = score

    # Check Cyrillic languages
    cyrillic_count = sum(char_counts.get(c, 0) for c in RUSSIAN_CYRILLIC + UKRAINIAN_CYRILLIC)
    if cyrillic_count > 0:
        # Distinguish between Russian and Ukrainian
        uk_specific = sum(char_counts.get(c, 0) for c in 'ҐґІіЇїЄє')
        ru_specific = sum(char_counts.get(c, 0) for c in 'Ёё')

        if uk_specific > 0:
            return 'uk'
        elif ru_specific > 0:
            return 'ru'
        else:
            # Default to Russian for Cyrillic without specific markers
            return 'ru'

    # Check Latin languages
    latin_count = sum(char_counts.get(c, 0) for c in BASE_LATIN)
    if latin_count > 0:
        if lang_scores:
            # Return the language with highest specific character count
            return max(lang_scores.items(), key=lambda x: x[1])[0]

    return 'universal'


def get_allowed_chars(language=None):
    """
    Get allowed character set for specified language.
    If language is None, returns universal set (all supported languages).
    """
    base_chars = DIGITS + PUNCTUATION + WHITESPACE

    if language is None or language == 'universal':
        return set(UNIVERSAL_CHARS + base_chars)
    elif language in LANGUAGE_CHARS:
        return set(LANGUAGE_CHARS[language]['chars'] + base_chars)
    else:
        # Default to universal if language not recognized
        return set(UNIVERSAL_CHARS + base_chars)


def process(text, replacement="?", remove=False, remove_watermark=False, language=None):
    """
    Process text with language-aware character filtering.
    """
    replaced = Counter()
    watermark_removed = Counter()

    allowed = get_allowed_chars(language)

    out = []
    for char in text:
        if remove_watermark and char in WATERMARK_CHARS:
            watermark_removed[char] += 1
            continue

        if char in allowed:
            out.append(char)
        else:
            if not remove:
                out.append(replacement)
            replaced[char] += 1

    return "".join(out), replaced, watermark_removed


def word_frequency(text):
    """Count word frequency, keeping apostrophes and hyphens within words."""
    words = re.findall(r"[a-zA-Zа-яА-ЯёЁҐґІіЇїЄєàâçéèêëîïôùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŸŒÆäöüßÄÖÜàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ\-']+", text)
    return Counter(words)


def build_report(input_file, output_file, replaced, watermark_removed, word_freq, elapsed, lang="Python", replacement="?", remove=False, remove_watermark=False, language=None, detected_language=None):
    """Build report with language information."""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"aiparstxt — Text Sanitizer Report ({lang})")
    lines.append(f"{'='*60}")
    lines.append(f"")
    lines.append(f"Input file:  {input_file}")
    if output_file:
        lines.append(f"Output file: {output_file}")
    lines.append(f"Execution time: {elapsed:.6f}s")
    lines.append(f"")

    # Language information
    lines.append(f"--- Language Detection ---")
    if language:
        lines.append(f"Specified language: {LANGUAGE_CHARS.get(language, {}).get('name', language)}")
    elif detected_language:
        lines.append(f"Language mode: Auto-detected ({LANGUAGE_CHARS.get(detected_language, {}).get('name', detected_language)} character set)")
        lines.append(f"Detected language: {LANGUAGE_CHARS.get(detected_language, {}).get('name', detected_language)}")
    else:
        lines.append(f"Language mode: Universal (all supported languages)")
    lines.append(f"")

    # Mode information
    lines.append(f"--- Processing Mode ---")
    if remove:
        lines.append(f"Mode: Remove disallowed characters")
    else:
        lines.append(f"Mode: Replace disallowed characters with '{replacement}'")

    if remove_watermark:
        lines.append(f"Watermark removal: ENABLED")
    else:
        lines.append(f"Watermark removal: DISABLED")
    lines.append(f"")

    # Watermark results
    if remove_watermark and watermark_removed:
        total_watermark = sum(watermark_removed.values())
        lines.append(f"--- Watermark Removal Results ---")
        lines.append(f"Watermark characters removed: {total_watermark}")
        if watermark_removed:
            lines.append(f"Removed watermark types:")
            for char, count in sorted(watermark_removed.items(), key=lambda x: -x[1]):
                lines.append(f"  {repr(char)} (U+{ord(char):04X}): {count}")
        lines.append(f"")

    # Replacement results
    if replaced:
        lines.append(f"--- Replaced Characters ---")
        lines.append(f"Total characters replaced: {sum(replaced.values())}")
        lines.append(f"Replacement character: '{replacement}'")
        lines.append(f"")
        lines.append(f"Character breakdown:")
        for char, count in sorted(replaced.items(), key=lambda x: -x[1])[:50]:  # Top 50
            try:
                lines.append(f"  {repr(char)} (U+{ord(char):04X}): {count}")
            except:
                lines.append(f"  {repr(char)}: {count}")
    else:
        lines.append(f"--- Replaced Characters ---")
        lines.append(f"No characters needed replacement")
    lines.append(f"")

    # Word frequency
    if word_freq:
        lines.append(f"--- Word Frequency (top 20) ---")
        for word, count in word_freq.most_common(20):
            lines.append(f"  {count:4d}: {word}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="aiparstxt — text sanitizer with multi-language support",
        epilog=f"Supported languages: {', '.join(LANGUAGE_CHARS.keys())}. Use 'universal' for all languages combined."
    )
    parser.add_argument("input_file", help="Input text file")
    parser.add_argument("-o", "--output", help="Output file (default: <input>.ed.txt)")
    parser.add_argument("-r", "--report", help="Report file (default: report_<lang>.txt)")
    parser.add_argument("--no-edit", action="store_true", help="Do not create .ed.txt file")
    parser.add_argument("--no-report", action="store_true", help="Do not create report file")
    parser.add_argument("-w", "--no-words", action="store_true", help="Do not include word frequency in report")
    parser.add_argument("--remove", action="store_true", help="Remove disallowed characters instead of replacing")
    parser.add_argument("--remove-watermark", action="store_true", help="Remove AI watermark characters")
    parser.add_argument("-l", "--language", choices=list(LANGUAGE_CHARS.keys()) + ['universal'],
                       help="Specify text language (auto-detect if not specified)")
    parser.add_argument("--replacement", default="?", help="Replacement character (default: '?')")
    parser.add_argument("--show-language", action="store_true", help="Show detected language and exit")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1

    start = time.time()

    # Read input
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    # Detect language if not specified
    detected_language = None
    if not args.language:
        detected_language = detect_language(text)
        language = detected_language
    else:
        language = args.language if args.language != 'universal' else None

    # Show language and exit if requested
    if args.show_language:
        if detected_language:
            lang_name = LANGUAGE_CHARS.get(detected_language, {}).get('name', detected_language)
            print(f"Detected language: {detected_language} ({lang_name})")
        else:
            print("Language: Universal (all supported languages)")
        return 0

    # Process text
    processed, replaced, watermark_removed = process(
        text,
        replacement=args.replacement,
        remove=args.remove,
        remove_watermark=args.remove_watermark,
        language=language
    )

    elapsed = time.time() - start

    # Write output
    output_file = None
    if not args.no_edit:
        if args.output:
            output_file = args.output
        else:
            output_file = str(input_path) + ".ed.txt"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(processed)
        except Exception as e:
            print(f"Error writing output file: {e}")
            return 1

    # Generate word frequency
    word_freq = None
    if not args.no_words:
        word_freq = word_frequency(processed)

    # Build and write report
    if not args.no_report:
        if args.report:
            report_file = args.report
        else:
            report_file = f"report_py.txt"

        report_content = build_report(
            str(input_path),
            output_file,
            replaced,
            watermark_removed,
            word_freq,
            elapsed,
            lang="Python",
            replacement=args.replacement,
            remove=args.remove,
            remove_watermark=args.remove_watermark,
            language=args.language,
            detected_language=detected_language
        )

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)
        except Exception as e:
            print(f"Error writing report file: {e}")
            return 1

    total_replaced = sum(replaced.values()) if replaced else 0
    total_watermark = sum(watermark_removed.values()) if watermark_removed else 0

    lang_info = ""
    if detected_language:
        lang_name = LANGUAGE_CHARS.get(detected_language, {}).get('name', detected_language)
        lang_info = f" | Language: {detected_language} ({lang_name})"
    elif args.language:
        lang_info = f" | Language: {args.language}"

    print(f"Done in {elapsed:.6f}s. Replacements: {total_replaced}, Watermark removed: {total_watermark}{lang_info}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
