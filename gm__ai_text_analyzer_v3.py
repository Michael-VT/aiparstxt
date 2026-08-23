import math
import re
import sys
import os
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Тихая загрузка токенизаторов NLTK
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)


class LightweightAITextDetector:
    def __init__(self):
        # Расширенный набор языковых клише и маркерных фраз ИИ
        self.ai_markers = {
            "ru": [
                r"\bв заключение\b", r"\bважно отметить\b", r"\bстоит отметить\b",
                r"\bподводя итоги\b", r"\bтаким образом\b", r"\bследует подчеркнуть\b",
                r"\bявляется ключевым\b", r"\bнесомненно\b", r"\bиграет важную роль\b",
                r"\bв современном мире\b", r"\bрезюмируя\b", r"\bнеобходимо заметить\b",
                r"\bгармоничное сочетание\b", r"\bключевой фактор\b"
            ],
            "en": [
                r"\bin conclusion\b", r"\bit is important to note\b", r"\bdelve into\b",
                r"\btapestry\b", r"\bfurthermore\b", r"\bmoreover\b", r"\btestament to\b",
                r"\bseamlessly\b", r"\bplay a crucial role\b", r"\bin summary\b",
                r"\bin today's world\b", r"\bshed light on\b", r"\bever-evolving\b"
            ]
        }

    def _calculate_entropy(self, words: list[str]) -> float:
        """Энтропия Шеннона: оценка предсказуемости словаря."""
        if not words:
            return 0.0
        length = len(words)
        counts = Counter(words)
        probs = [count / length for count in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def _calculate_burstiness(self, sentences: list[str]) -> float:
        """Burstiness: вариативность длины предложений (человек пишет неравномерно, ИИ — монотонно)."""
        lengths = [len(word_tokenize(s)) for s in sentences if s.strip()]
        if len(lengths) < 2:
            return 0.0
        
        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        return std_dev / mean if mean > 0 else 0.0

    def _find_watermarks(self, text: str) -> list[str]:
        """Поиск текстовых штампов ИИ."""
        text_lower = text.lower()
        found = []
        for lang, patterns in self.ai_markers.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    found.extend(matches)
        return list(set(found))

    def analyze(self, text: str) -> dict:
        sentences = sent_tokenize(text)
        words = [w.lower() for w in word_tokenize(text) if w.isalnum()]

        if len(words) < 10:
            return {"error": "Текст слишком короткий для корректного анализа (нужно минимум 10 слов)."}

        burstiness = round(self._calculate_burstiness(sentences), 3)
        entropy = round(self._calculate_entropy(words), 3)
        markers = self._find_watermarks(text)

        # Расчет комплексной вероятности
        score = 0.0
        
        # 1. Монотонность длины предложений
        if burstiness < 0.35:
            score += 40
        elif burstiness < 0.50:
            score += 20

        # 2. Низкое лексическое разнообразие
        if entropy < 4.5:
            score += 35
        elif entropy < 5.2:
            score += 15

        # 3. Маркерные фразы
        score += min(len(markers) * 15, 30)

        probability = min(max(round(score, 2), 1.0), 99.0)

        return {
            "ai_probability_percent": probability,
            "metrics": {
                "total_sentences": len(sentences),
                "total_words": len(words),
                "burstiness": burstiness,
                "entropy": entropy
            },
            "watermarks": {
                "count": len(markers),
                "detected": markers
            }
        }


def print_report(file_path: str, result: dict):
    print("=" * 60)
    print("         ОТЧЕТ ОБ АНАЛИЗЕ ТЕКСТА НА ПРИЗНАКИ ИИ")
    print("=" * 60)
    print(f"Файл: {os.path.basename(file_path)}")
    print("-" * 60)
    
    if "error" in result:
        print(f" ОШИБКА: {result['error']}")
        print("=" * 60)
        return

    prob = result["ai_probability_percent"]
    
    if prob >= 70:
        verdict = "[ ВЫСОКАЯ ВЕРОЯТНОСТЬ ИИ ]"
    elif prob >= 40:
        verdict = "[ СМЕШАННЫЙ / ОТРЕДАКТИРОВАННЫЙ ТЕКСТ ]"
    else:
        verdict = "[ НИЗКАЯ ВЕРОЯТНОСТЬ (НАПИСАНО ЧЕЛОВЕКОМ) ]"

    print(f"Вероятность ИИ: {prob}%")
    print(f"Вердикт:       {verdict}")
    print("-" * 60)
    
    metrics = result["metrics"]
    print(" МЕТРИКИ СТРУКТУРЫ И СЛОВАРЯ:")
    print(f"  • Всего предложений:      {metrics['total_sentences']}")
    print(f"  • Всего слов:             {metrics['total_words']}")
    print(f"  • Вариативность (Burstiness): {metrics['burstiness']} " + 
          ("(Монотонная структура)" if metrics['burstiness'] < 0.45 else "(Естественный ритм)"))
    print(f"  • Энтропия (Entropy):         {metrics['entropy']} " + 
          ("(Низкое разнообразие)" if metrics['entropy'] < 4.8 else "(Богатый лексикон)"))
    
    print("-" * 60)
    wm = result["watermarks"]
    print(" ИИ-КЛИШЕ И ТЕКСТОВЫЕ МАРКЕРЫ:")
    print(f"  • Найдено совпадений: {wm['count']}")
    if wm['detected']:
        for item in wm['detected']:
            print(f"     - \"{item}\"")
    else:
        print("  • Клише и водяные знаки не обнаружены.")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Использование: python ds_ai_text_analyzer.py <путь_к_файлу.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1251') as f:
            text = f.read()

    detector = LightweightAITextDetector()
    result = detector.analyze(text)
    print_report(file_path, result)


if __name__ == "__main__":
    main()

