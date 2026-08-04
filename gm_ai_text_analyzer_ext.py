import math
import re
import sys
import os
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Автоматическая загрузка токенизаторов NLTK
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)


class AITextDetector:
    def __init__(self):
        # Список часто встретимых стоп-слов и штампов ИИ (RU / EN)
        self.ai_markers_ru = [
            r"\bв заключение\b", r"\bважно отметить\b", r"\bстоит отметить\b",
            r"\bподводя итоги\b", r"\bтаким образом\b", r"\bследует подчеркнуть\b",
            r"\bявляется ключевым\b", r"\bнесомненно\b", r"\bиграет важную роль\b",
            r"\bв современном мире\b", r"\bподводя итог\b", r"\bрезюмируя\b",
            r"\bнеобходимо заметить\b", r"\bключевую роль\b"
        ]
        
        self.ai_markers_en = [
            r"\bin conclusion\b", r"\bit is important to note\b", r"\bdelve into\b",
            r"\btapestry\b", r"\bfurthermore\b", r"\bmoreover\b", r"\btestament to\b",
            r"\bseamlessly\b", r"\bplay a crucial role\b", r"\bin summary\b",
            r"\bin today's world\b", r"\ba vital role\b", r"\bshed light on\b"
        ]

    def _calculate_entropy(self, words: list[str]) -> float:
        """Расчет Энтропии Шеннона (предсказуемости словаря)."""
        if not words:
            return 0.0
        length = len(words)
        counts = Counter(words)
        probs = [count / length for count in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def _calculate_burstiness(self, sentences: list[str]) -> float:
        """
        Расчет Burstiness (коэффициента вариации длины предложений).
        Человек: высокая вариативность (высокий показатель).
        ИИ: монотонная длина (низкий показатель).
        """
        lengths = [len(word_tokenize(s)) for s in sentences if s.strip()]
        if len(lengths) < 2:
            return 0.0
        
        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        return std_dev / mean if mean > 0 else 0.0

    def _check_ai_markers(self, text: str) -> tuple[int, list[str]]:
        """Поиск текстовых водяных знаков / ИИ-паттернов."""
        found_markers = []
        text_lower = text.lower()
        
        all_markers = self.ai_markers_ru + self.ai_markers_en
        for pattern in all_markers:
            matches = re.findall(pattern, text_lower)
            if matches:
                found_markers.extend(matches)
                
        return len(found_markers), list(set(found_markers))

    def analyze(self, text: str) -> dict:
        """Главная функция анализа текста."""
        sentences = sent_tokenize(text)
        words = [w.lower() for w in word_tokenize(text) if w.isalnum()]
        
        if not words or not sentences:
            return {"error": "Текст слишком короткий для анализа или не содержит слов."}

        burstiness = self._calculate_burstiness(sentences)
        entropy = self._calculate_entropy(words)
        marker_count, markers_found = self._check_ai_markers(text)

        # Расчет итоговой вероятности (Heuristic AI Score)
        ai_score = 0.0
        
        # 1. Анализ Burstiness
        if burstiness < 0.40:
            ai_score += 35
        elif burstiness < 0.55:
            ai_score += 20

        # 2. Анализ Энтропии
        if entropy < 4.5:
            ai_score += 30
        elif entropy < 5.2:
            ai_score += 15

        # 3. Анализ ИИ-маркеров
        ai_score += min(marker_count * 15, 35)

        probability = min(max(round(ai_score, 2), 1.0), 99.0)

        return {
            "ai_probability_percent": probability,
            "metrics": {
                "burstiness": round(burstiness, 3),
                "entropy": round(entropy, 3),
                "total_sentences": len(sentences),
                "total_words": len(words)
            },
            "ai_features": {
                "marker_count": marker_count,
                "detected_markers": markers_found,
                "is_monotonous": burstiness < 0.45
            }
        }


def print_report(file_path: str, result: dict):
    """Вывод структурированного консольного отчета."""
    print("=" * 60)
    print(f"       ОТЧЕТ ОБ АНАЛИЗЕ ТЕКСТА НА ПРИЗНАКИ ИИ")
    print("=" * 60)
    print(f"Файл: {os.path.basename(file_path)}")
    print("-" * 60)
    
    if "error" in result:
        print(f" ОШИБКА: {result['error']}")
        print("=" * 60)
        return

    prob = result["ai_probability_percent"]
    
    # Визуальный вердикт
    if prob >= 70:
        verdict = "[ ВЫСОКАЯ ВЕРОЯТНОСТЬ ИИ ]"
        verdict_desc = "Текст с высокой долей вероятности сгенерирован ИИ."
    elif prob >= 40:
        verdict = "[ СРЕДНЯЯ ВЕРОЯТНОСТЬ (СМЕШАННЫЙ / ОТРЕДАКТИРОВАННЫЙ) ]"
        verdict_desc = "Текст содержит признаки ИИ, возможно отредактирован человеком."
    else:
        verdict = "[ НИЗКАЯ ВЕРОЯТНОСТЬ (НАПИСАНО ЧЕЛОВЕКОМ) ]"
        verdict_desc = "Текст выглядит естественно, признаки ИИ минимальны."

    print(f"Вероятность сгенерированности ИИ: {prob}%")
    print(f"Вердикт: {verdict}")
    print(f"Описание: {verdict_desc}")
    print("-" * 60)
    
    print(" ОСНОВНЫЕ МЕТРИКИ:")
    metrics = result["metrics"]
    print(f"  • Всего предложений:   {metrics['total_sentences']}")
    print(f"  • Всего слов:          {metrics['total_words']}")
    print(f"  • Burstiness (ритм):   {metrics['burstiness']} " + 
          ("(Низкий — предложения монотонные/одинаковые)" if metrics['burstiness'] < 0.45 else "(Нормальный — вариативная длина)"))
    print(f"  • Entropy (словарность): {metrics['entropy']} " + 
          ("(Низкая — предсказуемый выбор слов)" if metrics['entropy'] < 4.8 else "(Высокая — разнообразный лексикон)"))
    
    print("-" * 60)
    print(" ПРИЗНАКИ И ИИ-МАРКЕРЫ (ВОДЯНЫЕ ЗНАКИ):")
    features = result["ai_features"]
    print(f"  • Найдено клише/маркеров: {features['marker_count']}")
    
    if features['detected_markers']:
        print("  • Найденные выражения/штампы:")
        for marker in features['detected_markers']:
            print(f"     - \"{marker}\"")
    else:
        print("  • Найденные выражения/штампы: Не обнаружено")
        
    print(f"  • Монотонность структуры: {'Да' if features['is_monotonous'] else 'Нет'}")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Использование: python ds_ai_text_analyzer.py <путь_к_файлу.txt>")
        print("Пример:      python ds_ai_text_analyzer.py input_text.txt")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp1251') as f:
                text = f.read()
        except Exception as e:
            print(f"Ошибка при чтении файла (проверьте кодировку UTF-8): {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка открытия файла: {e}")
        sys.exit(1)

    detector = AITextDetector()
    result = detector.analyze(text)
    print_report(file_path, result)


if __name__ == "__main__":
    main()

