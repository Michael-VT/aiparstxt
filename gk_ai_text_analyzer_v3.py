#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GK AI Text Analyzer
Анализатор текста на признаки генерации ИИ (русский / английский).
Поддерживает:
  - Обычный анализ
  - JSON-вывод (--json)
  - Очистку текста от маркеров и водяных знаков (--clean)
"""

import argparse
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# ====================== КОНСТАНТЫ И СЛОВАРИ ======================

# Маркеры ИИ (английский)
AI_MARKERS_EN = {
    "delve", "delves", "delving",
    "tapestry", "landscape", "realm",
    "nestled", "embark", "embarked", "embarking",
    "journey", "pivotal", "crucial", "essential",
    "underscore", "underscores", "underscoring",
    "highlight", "highlights", "highlighting",
    "showcase", "showcases", "showcasing",
    "leverage", "leverages", "leveraging",
    "utilize", "utilizes", "utilizing", "utilisation",
    "facilitate", "facilitates", "facilitating",
    "enhance", "enhances", "enhancing",
    "optimize", "optimizes", "optimizing", "optimisation",
    "streamline", "streamlines", "streamlining",
    "robust", "comprehensive", "holistic",
    "synergy", "synergies", "synergistic",
    "paradigm", "paradigms", "paradigm shift",
    "cutting-edge", "state-of-the-art", "groundbreaking",
    "innovative", "transformative", "revolutionary",
    "furthermore", "moreover", "additionally",
    "consequently", "therefore", "thus",
    "in conclusion", "to summarize", "in summary",
    "it is important to note", "it is worth noting",
    "it should be noted", "notably",
    "a wide range of", "a variety of", "a myriad of",
    "plays a crucial role", "plays a pivotal role",
    "in today's", "in the modern", "in the digital age",
    "navigating", "landscape of", "ever-evolving",
    "multifaceted", "nuanced", "intricate",
    "foster", "fosters", "fostering",
    "empower", "empowers", "empowering",
    "harness", "harnesses", "harnessing",
    "seamless", "seamlessly",
    "game-changer", "game changer",
    "unpack", "unpacked", "unpacking",
    "deep dive", "deep-dive",
    "at the end of the day",
    "moving forward",
    "it's worth mentioning",
    "one cannot overstate",
    "shed light on",
    "pave the way",
    "bridge the gap",
}

# Маркеры ИИ (русский)
AI_MARKERS_RU = {
    "следует отметить", "важно отметить", "стоит отметить",
    "необходимо отметить", "следует подчеркнуть",
    "таким образом", "в связи с этим", "в рамках",
    "в контексте", "в условиях", "на сегодняшний день",
    "в современном мире", "в наше время",
    "играет важную роль", "играет ключевую роль",
    "играет значительную роль", "занимает важное место",
    "нельзя не упомянуть", "нельзя не отметить",
    "особый интерес представляет", "особый интерес вызывает",
    "актуальность темы", "актуальность исследования",
    "целью работы является", "задачей исследования",
    "в заключение", "подводя итог", "резюмируя",
    "на основании изложенного", "исходя из вышеизложенного",
    "можно сделать вывод", "позволяет сделать вывод",
    "в результате", "в итоге",
    "комплексный подход", "системный подход",
    "интеграция", "синергия", "синергетический",
    "парадигма", "трансформационный", "трансформация",
    "инновационный", "инновации", "прорывной",
    "передовой", "современный подход",
    "оптимизация", "оптимизировать",
    "эффективность", "повышение эффективности",
    "ключевой фактор", "ключевые аспекты",
    "многогранный", "многоаспектный",
    "всесторонний", "комплексный анализ",
    "несмотря на", "несмотря на то что",
    "в то же время", "вместе с тем",
    "кроме того", "помимо этого",
    "более того", "кроме всего прочего",
    "следует учитывать", "необходимо учитывать",
    "принимая во внимание", "с учетом",
    "в частности", "в особенности",
    "прежде всего", "в первую очередь",
    "с одной стороны", "с другой стороны",
    "с одной стороны,", "с другой стороны,",
    "безусловно", "несомненно", "очевидно",
    "как известно", "известно что",
    "по мнению экспертов", "по оценкам специалистов",
    "согласно исследованиям", "данные показывают",
    "результаты свидетельствуют",
    "это позволяет", "это дает возможность",
    "способствует", "способствуют",
    "обеспечивает", "обеспечивают",
    "реализация", "реализовать",
    "внедрение", "внедрить",
    "совершенствование", "улучшение",
    "развитие", "расширение",
    "формирование", "создание условий",
}

# Простые синонимы для очистки (EN)
SYNONYMS_EN = {
    "delve": "explore",
    "delves": "explores",
    "delving": "exploring",
    "tapestry": "fabric",
    "landscape": "scene",
    "realm": "area",
    "nestled": "located",
    "embark": "begin",
    "embarked": "began",
    "embarking": "beginning",
    "journey": "process",
    "pivotal": "important",
    "crucial": "important",
    "essential": "necessary",
    "underscore": "emphasize",
    "underscores": "emphasizes",
    "underscoring": "emphasizing",
    "highlight": "show",
    "highlights": "shows",
    "highlighting": "showing",
    "showcase": "display",
    "showcases": "displays",
    "showcasing": "displaying",
    "leverage": "use",
    "leverages": "uses",
    "leveraging": "using",
    "utilize": "use",
    "utilizes": "uses",
    "utilizing": "using",
    "facilitate": "help",
    "facilitates": "helps",
    "facilitating": "helping",
    "enhance": "improve",
    "enhances": "improves",
    "enhancing": "improving",
    "optimize": "improve",
    "optimizes": "improves",
    "optimizing": "improving",
    "streamline": "simplify",
    "streamlines": "simplifies",
    "streamlining": "simplifying",
    "robust": "strong",
    "comprehensive": "complete",
    "holistic": "complete",
    "synergy": "cooperation",
    "synergies": "cooperations",
    "synergistic": "cooperative",
    "paradigm": "model",
    "paradigms": "models",
    "paradigm shift": "major change",
    "cutting-edge": "advanced",
    "state-of-the-art": "modern",
    "groundbreaking": "new",
    "innovative": "new",
    "transformative": "changing",
    "revolutionary": "new",
    "furthermore": "also",
    "moreover": "also",
    "additionally": "also",
    "consequently": "so",
    "therefore": "so",
    "thus": "so",
    "notably": "especially",
    "multifaceted": "complex",
    "nuanced": "subtle",
    "intricate": "complex",
    "foster": "encourage",
    "fosters": "encourages",
    "fostering": "encouraging",
    "empower": "enable",
    "empowers": "enables",
    "empowering": "enabling",
    "harness": "use",
    "harnesses": "uses",
    "harnessing": "using",
    "seamless": "smooth",
    "seamlessly": "smoothly",
    "unpack": "examine",
    "unpacked": "examined",
    "unpacking": "examining",
    "it is important to note": "note that",
    "it is worth noting": "worth noting",
    "it should be noted": "note that",
    "plays a crucial role": "is important",
    "plays a pivotal role": "is important",
    "in today's": "in current",
    "in the modern": "in current",
    "in the digital age": "today",
    "to summarize": "in short",
    "in conclusion": "finally",
    "in summary": "in short",
    "a wide range of": "many",
    "a variety of": "various",
    "a myriad of": "many",
    "deep dive": "detailed look",
    "deep-dive": "detailed look",
    "ever-evolving": "changing",
    "game-changer": "important change",
    "game changer": "important change",
    "at the end of the day": "ultimately",
    "moving forward": "in the future",
    "shed light on": "explain",
    "pave the way": "prepare",
    "bridge the gap": "connect",
}

# Простые синонимы для очистки (RU)
SYNONYMS_RU = {
    "следует отметить": "важно сказать",
    "важно отметить": "стоит сказать",
    "стоит отметить": "можно сказать",
    "необходимо отметить": "нужно сказать",
    "следует подчеркнуть": "важно подчеркнуть",
    "таким образом": "итак",
    "в связи с этим": "поэтому",
    "в рамках": "в пределах",
    "в контексте": "в связи с",
    "в условиях": "при",
    "на сегодняшний день": "сейчас",
    "в современном мире": "сейчас",
    "в наше время": "сейчас",
    "играет важную роль": "важен",
    "играет ключевую роль": "ключевой",
    "играет значительную роль": "значим",
    "занимает важное место": "важен",
    "нельзя не упомянуть": "стоит упомянуть",
    "нельзя не отметить": "стоит отметить",
    "особый интерес представляет": "интересно",
    "особый интерес вызывает": "интересно",
    "актуальность темы": "важность темы",
    "актуальность исследования": "важность исследования",
    "целью работы является": "цель работы —",
    "задачей исследования": "задача исследования —",
    "в заключение": "в конце",
    "подводя итог": "итого",
    "резюмируя": "коротко",
    "на основании изложенного": "исходя из сказанного",
    "исходя из вышеизложенного": "из сказанного",
    "можно сделать вывод": "вывод:",
    "позволяет сделать вывод": "вывод:",
    "в результате": "итог",
    "в итоге": "итог",
    "комплексный подход": "полный подход",
    "системный подход": "системный взгляд",
    "интеграция": "объединение",
    "синергия": "взаимодействие",
    "синергетический": "взаимодействующий",
    "парадигма": "модель",
    "трансформационный": "изменяющий",
    "трансформация": "изменение",
    "инновационный": "новый",
    "инновации": "новшества",
    "прорывной": "новый",
    "передовой": "современный",
    "оптимизация": "улучшение",
    "оптимизировать": "улучшить",
    "эффективность": "результативность",
    "повышение эффективности": "улучшение результатов",
    "ключевой фактор": "главный фактор",
    "ключевые аспекты": "главные стороны",
    "многогранный": "сложный",
    "многоаспектный": "сложный",
    "всесторонний": "полный",
    "комплексный анализ": "полный анализ",
    "несмотря на": "хотя",
    "несмотря на то что": "хотя",
    "в то же время": "одновременно",
    "вместе с тем": "также",
    "кроме того": "также",
    "помимо этого": "также",
    "более того": "даже",
    "кроме всего прочего": "также",
    "следует учитывать": "нужно помнить",
    "необходимо учитывать": "нужно помнить",
    "принимая во внимание": "учитывая",
    "с учетом": "учитывая",
    "в частности": "особенно",
    "в особенности": "особенно",
    "прежде всего": "сначала",
    "в первую очередь": "сначала",
    "с одной стороны": "с одной стороны",
    "с другой стороны": "с другой стороны",
    "безусловно": "конечно",
    "несомненно": "конечно",
    "очевидно": "ясно",
    "как известно": "известно",
    "известно что": "известно, что",
    "по мнению экспертов": "по оценкам",
    "по оценкам специалистов": "по оценкам",
    "согласно исследованиям": "по данным",
    "данные показывают": "данные говорят",
    "результаты свидетельствуют": "результаты показывают",
    "это позволяет": "это даёт",
    "это дает возможность": "это даёт шанс",
    "способствует": "помогает",
    "способствуют": "помогают",
    "обеспечивает": "даёт",
    "обеспечивают": "дают",
    "реализация": "выполнение",
    "реализовать": "выполнить",
    "внедрение": "введение",
    "внедрить": "ввести",
    "совершенствование": "улучшение",
    "улучшение": "улучшение",
    "развитие": "рост",
    "расширение": "увеличение",
    "формирование": "создание",
    "создание условий": "создание условий",
}

# Известные водяные знаки / подозрительные unicode
ZERO_WIDTH_CHARS = {
    '\u200b': 'ZERO WIDTH SPACE',
    '\u200c': 'ZERO WIDTH NON-JOINER',
    '\u200d': 'ZERO WIDTH JOINER',
    '\u200e': 'LEFT-TO-RIGHT MARK',
    '\u200f': 'RIGHT-TO-LEFT MARK',
    '\u2060': 'WORD JOINER',
    '\u2061': 'FUNCTION APPLICATION',
    '\u2062': 'INVISIBLE TIMES',
    '\u2063': 'INVISIBLE SEPARATOR',
    '\u2064': 'INVISIBLE PLUS',
    '\ufeff': 'ZERO WIDTH NO-BREAK SPACE (BOM)',
    '\u00ad': 'SOFT HYPHEN',
    '\u034f': 'COMBINING GRAPHEME JOINER',
    '\u061c': 'ARABIC LETTER MARK',
    '\u180e': 'MONGOLIAN VOWEL SEPARATOR',
    '\u202a': 'LEFT-TO-RIGHT EMBEDDING',
    '\u202b': 'RIGHT-TO-LEFT EMBEDDING',
    '\u202c': 'POP DIRECTIONAL FORMATTING',
    '\u202d': 'LEFT-TO-RIGHT OVERRIDE',
    '\u202e': 'RIGHT-TO-LEFT OVERRIDE',
    '\u2066': 'LEFT-TO-RIGHT ISOLATE',
    '\u2067': 'RIGHT-TO-LEFT ISOLATE',
    '\u2068': 'FIRST STRONG ISOLATE',
    '\u2069': 'POP DIRECTIONAL ISOLATE',
}

# Паттерны машинного перевода / неестественности
MT_PATTERNS_EN = [
    r'\b(the the|a a|an an)\b',
    r'\b(is is|are are|was was|were were)\b',
    r'\b(of of|in in|to to|for for)\b',
    r'\b(this this|that that)\b',
]

MT_PATTERNS_RU = [
    r'\b(и и|в в|на на|с с|по по)\b',
    r'\b(это это|что что|как как)\b',
    r'\b(не не|да да)\b',
]

# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================

def detect_language(text: str) -> str:
    """Простое определение языка по наличию кириллицы."""
    cyrillic = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    latin = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    if cyrillic > latin * 0.3:
        return "russian"
    return "english"


def tokenize_words(text: str, lang: str) -> List[str]:
    """Простая токенизация слов."""
    if lang == "russian":
        # Русские слова + латиница
        words = re.findall(r'[а-яА-ЯёЁa-zA-Z0-9]+(?:-[а-яА-ЯёЁa-zA-Z0-9]+)*', text)
    else:
        words = re.findall(r"[a-zA-Z0-9]+(?:'[a-zA-Z]+)?(?:-[a-zA-Z0-9]+)*", text)
    return [w.lower() for w in words if w]


def split_sentences(text: str) -> List[str]:
    """Разбиение на предложения."""
    # Простой сплиттер
    sentences = re.split(r'(?<=[.!?…])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def calculate_entropy(data: List[str]) -> float:
    """Энтропия Шеннона по списку токенов."""
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def calculate_char_entropy(text: str) -> float:
    """Энтропия по символам."""
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def approximate_perplexity(words: List[str], n: int = 2) -> float:
    """
    Приближённая перплексия на основе n-грамм.
    Чем ниже — тем более предсказуем текст (типично для ИИ).
    """
    if len(words) < n + 1:
        return 100.0  # нейтральное значение

    ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    counts = Counter(ngrams)
    total = len(ngrams)

    # Сглаженная вероятность
    log_prob = 0.0
    vocab_size = len(set(words)) + 1  # +1 для сглаживания

    for ng in ngrams:
        # Простое аддитивное сглаживание
        p = (counts[ng] + 0.1) / (total + 0.1 * vocab_size)
        log_prob += math.log2(p)

    avg_log_prob = log_prob / total
    perplexity = 2 ** (-avg_log_prob)
    return min(perplexity, 500.0)  # ограничиваем


def calculate_burstiness(sentences: List[str]) -> float:
    """
    Burstiness: вариативность длины предложений.
    Низкая burstiness (равномерная длина) — признак ИИ.
    Возвращаем коэффициент вариации (std / mean).
    """
    if len(sentences) < 2:
        return 0.5
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    return std / mean


def calculate_repetitiveness(words: List[str]) -> float:
    """Доля повторяющихся слов (1 - unique/total). Высокая — признак ИИ."""
    if not words:
        return 0.0
    unique = len(set(words))
    return 1.0 - (unique / len(words))


def calculate_punctuation_diversity(text: str) -> float:
    """Разнообразие пунктуации (отношение уникальных знаков к общему числу)."""
    punct = re.findall(r'[^\w\s]', text)
    if not punct:
        return 0.0
    return len(set(punct)) / len(punct)


def find_ai_markers(text: str, lang: str) -> List[Tuple[str, int]]:
    """Находит маркеры ИИ и их количество вхождений."""
    markers = AI_MARKERS_RU if lang == "russian" else AI_MARKERS_EN
    found = []
    text_lower = text.lower()
    used_spans = []  # чтобы не считать перекрывающиеся

    # Сначала длинные фразы
    sorted_markers = sorted(markers, key=len, reverse=True)
    for marker in sorted_markers:
        if ' ' in marker or '-' in marker:
            pattern = re.escape(marker)
        else:
            # Для русских слов — допускаем морфологические окончания (осторожно)
            if lang == "russian" and len(marker) >= 6 and ' ' not in marker:
                # Берём более длинный стем, чтобы меньше ложных срабатываний
                stem = marker[:max(5, len(marker)-3)]
                pattern = r'\b' + re.escape(stem) + r'[а-яё]*'
            else:
                pattern = r'\b' + re.escape(marker) + r'\b'

        for m in re.finditer(pattern, text_lower, flags=re.IGNORECASE):
            start, end = m.start(), m.end()
            # Проверка на перекрытие
            if any(not (end <= s or start >= e) for s, e in used_spans):
                continue
            used_spans.append((start, end))
            # Добавляем оригинальный маркер (или найденную форму)
            found_form = m.group(0)
            # Ищем, есть ли уже такой
            existing = next((i for i, (mk, _) in enumerate(found) if mk == marker), None)
            if existing is not None:
                found[existing] = (marker, found[existing][1] + 1)
            else:
                found.append((marker, 1))
    return found


def find_watermarks(text: str) -> List[Dict[str, Any]]:
    """Ищет водяные знаки: zero-width, невидимые символы, подозрительные unicode."""
    found = []
    for i, char in enumerate(text):
        if char in ZERO_WIDTH_CHARS:
            found.append({
                "type": "zero_width",
                "char": repr(char),
                "name": ZERO_WIDTH_CHARS[char],
                "position": i,
                "code": f"U+{ord(char):04X}"
            })
        else:
            # Другие невидимые / управляющие
            cat = unicodedata.category(char)
            if cat in ('Cf', 'Cc', 'Zl', 'Zp') and char not in '\n\r\t':
                name = unicodedata.name(char, "UNKNOWN")
                found.append({
                    "type": "control/format",
                    "char": repr(char),
                    "name": name,
                    "position": i,
                    "code": f"U+{ord(char):04X}"
                })
    return found


def detect_machine_translation(text: str, lang: str) -> List[str]:
    """Простые признаки машинного перевода / неестественных повторов."""
    patterns = MT_PATTERNS_RU if lang == "russian" else MT_PATTERNS_EN
    found = []
    for pat in patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            found.extend(matches)
    # Дополнительно: очень короткие предложения подряд или неестественная структура
    return list(set(found))


def score_ai_probability(
    perplexity: float,
    burstiness: float,
    repetitiveness: float,
    entropy: float,
    markers_count: int,
    total_words: int,
    watermarks_count: int,
    punct_div: float,
) -> Tuple[float, Dict[str, float]]:
    """
    Вычисляет итоговую вероятность ИИ (0-100) и вклад каждого фактора.
    Эвристические веса, подогнанные эмпирически.
    """
    scores = {}

    # Перплексия: низкая → высокий балл ИИ
    # Типичный диапазон: 10-80 для ИИ, 40-200 для человека
    if perplexity < 25:
        scores["perplexity"] = 0.9
    elif perplexity < 40:
        scores["perplexity"] = 0.7
    elif perplexity < 60:
        scores["perplexity"] = 0.45
    elif perplexity < 90:
        scores["perplexity"] = 0.25
    else:
        scores["perplexity"] = 0.1

    # Burstiness: низкая (равномерность) → ИИ
    if burstiness < 0.25:
        scores["burstiness"] = 0.85
    elif burstiness < 0.4:
        scores["burstiness"] = 0.6
    elif burstiness < 0.6:
        scores["burstiness"] = 0.35
    else:
        scores["burstiness"] = 0.15

    # Повторяемость
    if repetitiveness > 0.45:
        scores["repetitiveness"] = 0.8
    elif repetitiveness > 0.3:
        scores["repetitiveness"] = 0.55
    elif repetitiveness > 0.2:
        scores["repetitiveness"] = 0.3
    else:
        scores["repetitiveness"] = 0.1

    # Энтропия слов (низкая → ИИ)
    if entropy < 6.5:
        scores["entropy"] = 0.7
    elif entropy < 8.0:
        scores["entropy"] = 0.45
    elif entropy < 9.5:
        scores["entropy"] = 0.25
    else:
        scores["entropy"] = 0.1

    # Маркеры (нормализовано по длине)
    marker_density = markers_count / max(total_words / 100, 1)
    if marker_density > 5:
        scores["markers"] = 0.95
    elif marker_density > 2:
        scores["markers"] = 0.75
    elif marker_density > 0.8:
        scores["markers"] = 0.5
    elif marker_density > 0.2:
        scores["markers"] = 0.3
    else:
        scores["markers"] = 0.05

    # Водяные знаки — сильный сигнал
    if watermarks_count > 0:
        scores["watermarks"] = min(0.95, 0.4 + watermarks_count * 0.15)
    else:
        scores["watermarks"] = 0.0

    # Пунктуация (очень низкое разнообразие подозрительно)
    if punct_div < 0.15:
        scores["punctuation"] = 0.4
    else:
        scores["punctuation"] = 0.1

    # Взвешенная сумма
    weights = {
        "perplexity": 0.22,
        "burstiness": 0.18,
        "repetitiveness": 0.15,
        "entropy": 0.12,
        "markers": 0.22,
        "watermarks": 0.08,
        "punctuation": 0.03,
    }

    total = sum(scores[k] * weights[k] for k in weights)
    # Нормализация к 0-100
    probability = min(99.5, max(1.0, total * 100))

    return probability, scores


def get_level(prob: float) -> str:
    if prob >= 75:
        return "Высокая (вероятно, ИИ)"
    elif prob >= 55:
        return "Средняя (подозрительно)"
    elif prob >= 35:
        return "Низкая-средняя (смешанные признаки)"
    else:
        return "Низкая (скорее человек)"


def progress_bar(prob: float, width: int = 45) -> str:
    filled = int(width * prob / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {prob:.1f}%"


# ====================== ОЧИСТКА ======================

def clean_text(text: str, lang: str, markers_found: List[Tuple[str, int]], watermarks: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Заменяет маркеры ИИ на «синоним» и водяные знаки на маркеры.
    Возвращает очищенный текст и список замен.
    """
    replacements = []
    result = text

    # 1. Водяные знаки (с конца, чтобы позиции не съезжали)
    for wm in sorted(watermarks, key=lambda x: x["position"], reverse=True):
        pos = wm["position"]
        char = text[pos]
        marker = f"◄ВОДЯНОЙ_ЗНАК: {wm['name']} ({wm['code']})►"
        result = result[:pos] + marker + result[pos+1:]
        replacements.append({
            "type": "watermark",
            "original": repr(char),
            "replacement": marker,
            "position": pos,
            "info": wm["name"]
        })

    # 2. Маркеры (замена на синонимы в кавычках)
    synonyms = SYNONYMS_RU if lang == "russian" else SYNONYMS_EN
    # Сортируем по длине (длинные сначала)
    sorted_markers = sorted([m[0] for m in markers_found], key=len, reverse=True)

    for marker in sorted_markers:
        syn = synonyms.get(marker, marker)
        replacement = f"«{syn}»"

        if lang == "russian" and ' ' not in marker and len(marker) >= 6:
            # Морфологически гибкая замена
            stem = marker[:max(5, len(marker)-3)]
            pattern = re.compile(r'\b' + re.escape(stem) + r'[а-яё]*', re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(marker), re.IGNORECASE)

        def make_repl(repl=replacement):
            def repl_func(m):
                orig = m.group(0)
                # Сохраняем заглавную букву
                if orig and orig[0].isupper():
                    # «Синоним»
                    inner = repl[1:-1]  # без кавычек
                    if inner:
                        return f"«{inner[0].upper() + inner[1:]}»"
                return repl
            return repl_func

        new_result, count = pattern.subn(make_repl(), result)
        if count > 0:
            result = new_result
            replacements.append({
                "type": "ai_marker",
                "original": marker,
                "replacement": replacement,
                "count": count
            })

    return result, replacements


# ====================== ОТЧЁТ ======================

def print_report(report: Dict[str, Any], file_path: str):
    """Красивый вывод отчёта в терминал."""
    print("=" * 60)
    print("📊  ОТЧЕТ ПО АНАЛИЗУ ТЕКСТА НА ПРИЗНАКИ ИИ")
    print("=" * 60)
    print(f"📁 Файл: {file_path}")
    print(f"⏰ Время анализа: {report['timestamp']}")
    print("-" * 60)
    print(f"🎯 ВЕРОЯТНОСТЬ ИИ: {report['ai_probability']:.1f}%")
    print(f"📈 Уровень: {report['level']}")
    print(f"   {progress_bar(report['ai_probability'])}")
    print("-" * 60)
    print("📋 ДЕТАЛЬНЫЙ АНАЛИЗ:")
    print("-" * 60)

    stats = report["statistics"]
    print(f"  • Язык                    : {stats['language']}")
    print(f"  • Количество слов         : {stats['word_count']}")
    print(f"  • Количество символов     : {stats['char_count']}")
    print(f"  • Количество предложений  : {stats['sentence_count']}")
    print(f"  • Перплексия (approx)     : {stats['perplexity']:.2f}  (score: {report['factor_scores']['perplexity']:.3f})")
    print(f"  • Всплески (burstiness)   : {stats['burstiness']:.3f}  (score: {report['factor_scores']['burstiness']:.3f})")
    print(f"  • Повторяемость           : {stats['repetitiveness']:.3f}  (score: {report['factor_scores']['repetitiveness']:.3f})")
    print(f"  • Энтропия слов           : {stats['word_entropy']:.3f}  (score: {report['factor_scores']['entropy']:.3f})")
    print(f"  • Энтропия символов       : {stats['char_entropy']:.3f}")
    print(f"  • Разнообразие пунктуации : {stats['punctuation_diversity']:.3f}")
    print(f"  • Найдено маркеров ИИ     : {stats['markers_count']}")
    print(f"  • Водяные знаки           : {'✅ Да (' + str(stats['watermarks_count']) + ')' if stats['watermarks_count'] else '❌ Нет'}")
    print(f"  • Признаки маш. перевода  : {stats['mt_signs_count']}")

    if report["markers"]:
        print()
        print(f"  🔍 Найденные маркеры ИИ ({len(report['markers'])}):")
        for marker, count in report["markers"][:20]:  # максимум 20
            print(f"    - {marker}  (×{count})")
        if len(report["markers"]) > 20:
            print(f"    ... и ещё {len(report['markers']) - 20}")

    if report["watermarks"]:
        print()
        print(f"  💧 Найденные водяные знаки ({len(report['watermarks'])}):")
        # Группируем
        by_type = defaultdict(int)
        for wm in report["watermarks"]:
            by_type[f"{wm['name']} ({wm['code']})"] += 1
        for name, cnt in list(by_type.items())[:10]:
            print(f"    - {name}  ×{cnt}")

    if report["mt_signs"]:
        print()
        print(f"  🔄 Признаки машинного перевода / повторов:")
        for sign in report["mt_signs"][:10]:
            print(f"    - {sign}")

    print("=" * 60)
    print("💡 РЕКОМЕНДАЦИИ:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    print("=" * 60)


def generate_recommendations(prob: float, markers_count: int, watermarks_count: int, mt_count: int) -> List[str]:
    recs = []
    if prob >= 70:
        recs.append("⚠️  Текст демонстрирует сильные признаки ИИ-генерации")
        recs.append("🔍 Рекомендуется проверка другими детекторами (GPTZero, Originality.ai, Winston и т.д.)")
        recs.append("✏️  При необходимости — перепишите ключевые фрагменты своими словами")
    elif prob >= 50:
        recs.append("⚠️  Текст содержит заметные признаки возможной ИИ-генерации")
        recs.append("🔍 Рекомендуется дополнительная проверка и ручная редактура")
    elif prob >= 30:
        recs.append("ℹ️  Текст имеет смешанные признаки. Возможна частичная генерация или сильная редактура")
        recs.append("✍️  Обратите внимание на выделенные маркеры")
    else:
        recs.append("✅ Текст выглядит преимущественно человеческим")
        recs.append("ℹ️  Статистические показатели в пределах нормы для авторского текста")

    if watermarks_count > 0:
        recs.append(f"💧 Обнаружены невидимые символы / водяные знаки ({watermarks_count}). Это сильный индикатор возможной генерации или копирования.")
    if markers_count > 5:
        recs.append(f"📝 Много типичных ИИ-маркеров ({markers_count}). Рекомендуется замена на более естественные формулировки.")
    if mt_count > 0:
        recs.append("🔄 Обнаружены признаки возможного машинного перевода или автоматической генерации повторов.")

    return recs


# ====================== ГЛАВНАЯ ЛОГИКА ======================

def analyze_text(text: str, source_name: str = "stdin") -> Dict[str, Any]:
    lang = detect_language(text)
    words = tokenize_words(text, lang)
    sentences = split_sentences(text)

    word_count = len(words)
    char_count = len(text)
    sentence_count = len(sentences)

    perplexity = approximate_perplexity(words)
    burstiness = calculate_burstiness(sentences)
    repetitiveness = calculate_repetitiveness(words)
    word_entropy = calculate_entropy(words)
    char_entropy = calculate_char_entropy(text)
    punct_div = calculate_punctuation_diversity(text)

    markers = find_ai_markers(text, lang)
    markers_count = sum(c for _, c in markers)
    watermarks = find_watermarks(text)
    mt_signs = detect_machine_translation(text, lang)

    probability, factor_scores = score_ai_probability(
        perplexity, burstiness, repetitiveness, word_entropy,
        markers_count, word_count, len(watermarks), punct_div
    )

    level = get_level(probability)
    recommendations = generate_recommendations(probability, markers_count, len(watermarks), len(mt_signs))

    report = {
        "source": source_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ai_probability": round(probability, 2),
        "level": level,
        "statistics": {
            "language": lang,
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "perplexity": round(perplexity, 2),
            "burstiness": round(burstiness, 4),
            "repetitiveness": round(repetitiveness, 4),
            "word_entropy": round(word_entropy, 3),
            "char_entropy": round(char_entropy, 3),
            "punctuation_diversity": round(punct_div, 4),
            "markers_count": markers_count,
            "watermarks_count": len(watermarks),
            "mt_signs_count": len(mt_signs),
        },
        "factor_scores": {k: round(v, 3) for k, v in factor_scores.items()},
        "markers": markers,
        "watermarks": watermarks,
        "mt_signs": mt_signs,
        "recommendations": recommendations,
    }
    return report


def main():
    parser = argparse.ArgumentParser(
        description="GK AI Text Analyzer — анализ текста на признаки генерации ИИ (RU/EN)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python gk_ai_text_analyzer.py input.txt
  python gk_ai_text_analyzer.py input.txt --json
  python gk_ai_text_analyzer.py input.txt --clean
  python gk_ai_text_analyzer.py input.txt --clean --json
        """
    )
    parser.add_argument("input_file", help="Путь к текстовому файлу для анализа")
    parser.add_argument("--json", action="store_true", help="Сохранить полный отчёт в JSON-файл")
    parser.add_argument("--clean", action="store_true", help="Создать очищенную версию текста (_cleaned.txt)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Не выводить отчёт в терминал (только файлы)")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Ошибка: файл '{input_path}' не найден.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("❌ Файл пуст.", file=sys.stderr)
        sys.exit(1)

    # Анализ
    report = analyze_text(text, source_name=str(input_path))

    # Вывод в терминал
    if not args.quiet:
        print_report(report, str(input_path))

    # JSON
    if args.json:
        json_path = input_path.with_suffix(".json")
        # Делаем watermarks сериализуемыми
        report_json = report.copy()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_json, f, ensure_ascii=False, indent=2)
        print(f"\n💾 JSON-отчёт сохранён: {json_path}")

    # Очистка
    if args.clean:
        lang = report["statistics"]["language"]
        cleaned_text, replacements = clean_text(
            text, lang, report["markers"], report["watermarks"]
        )
        cleaned_path = input_path.with_name(input_path.stem + "_cleaned.txt")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print("\n" + "=" * 60)
        print("🧹 РЕЖИМ ОЧИСТКИ (--clean)")
        print("=" * 60)
        print(f"📁 Очищенный файл: {cleaned_path}")
        print(f"🔄 Произведено замен: {len(replacements)}")
        if replacements:
            print("\nСписок замен:")
            for r in replacements[:30]:
                if r["type"] == "ai_marker":
                    print(f"  • [{r['type']}] «{r['original']}» → {r['replacement']}  (×{r.get('count', 1)})")
                else:
                    print(f"  • [{r['type']}] {r['original']} → {r['replacement']}")
            if len(replacements) > 30:
                print(f"  ... и ещё {len(replacements) - 30}")
        print("=" * 60)

        # Если --json, добавляем информацию об очистке
        if args.json:
            report["cleaning"] = {
                "cleaned_file": str(cleaned_path),
                "replacements_count": len(replacements),
                "replacements": replacements
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
