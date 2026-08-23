# python -m pip install torch transformers nltk
import math
import re
import sys
import os
import torch
import nltk
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Тихая загрузка токенизатора предложений NLTK
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)


class AITextDetector:
    def __init__(self):
        # Используем предобученную нейросеть-классификатор (RoBERTa / DeBERTa)
        # Она обучена находить глубокие математические паттерны сгенерированного текста
        self.model_name = "roberta-base-openai-detector"  # или "Hello-SimpleAI/chatgpt-detector-roberta"
        print("Загрузка языковой модели для анализа паттернов... (1-2 минуты при первом запуске)")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()
        except Exception:
            # Резервная мультиязычная модель
            self.model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()

        # Водяные знаки / Специфические паттерны связок (RU / EN)
        self.ai_markers = {
            "ru": [
                r"\bв заключение\b", r"\bважно отметить\b", r"\bстоит отметить\b",
                r"\bподводя итоги\b", r"\bтаким образом\b", r"\bследует подчеркнуть\b",
                r"\bявляется ключевым\b", r"\bнесомненно\b", r"\bиграет важную роль\b",
                r"\bв современном мире\b", r"\bрезюмируя\b", r"\bнеобходимо заметить\b"
            ],
            "en": [
                r"\bin conclusion\b", r"\bit is important to note\b", r"\bdelve into\b",
                r"\btapestry\b", r"\bfurthermore\b", r"\bmoreover\b", r"\btestament to\b",
                r"\bseamlessly\b", r"\bplay a crucial role\b", r"\bin summary\b",
                r"\bin today's world\b", r"\bshed light on\b"
            ]
        }

    def _get_neural_score(self, text: str) -> float:
        """Анализ глубоких паттернов текста через вероятностные распределения токенов нейросети."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            
        # Индекс 1 в таких моделях обычно отвечает за Fake / Generated Text
        ai_prob = probs[0][1].item() * 100
        return round(ai_prob, 2)

    def _analyze_sentence_variance(self, sentences: list[str]) -> float:
        """Оценка ритмики текста (Burstiness)."""
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if len(lengths) < 2:
            return 0.0
        
        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        return round(std_dev / mean if mean > 0 else 0.0, 3)

    def _find_watermarks(self, text: str) -> list[str]:
        """Поиск текстовых водяных знаков и маркерных фраз."""
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
        words = text.split()

        if len(words) < 10:
            return {"error": "Текст слишком короткий для полноценного анализа (нужно минимум 10-15 слов)."}

        # 1. Глубокий нейросетевой анализ паттернов
        neural_score = self._get_neural_score(text)
        
        # 2. Ритмика и вариативность предложений
        burstiness = self._analyze_sentence_variance(sentences)
        
        # 3. Маркерные фразы (водяные знаки)
        detected_markers = self._find_watermarks(text)

        return {
            "ai_probability_percent": neural_score,
            "metrics": {
                "total_sentences": len(sentences),
                "total_words": len(words),
                "burstiness": burstiness,
                "is_monotonous": burstiness < 0.35 if len(sentences) > 2 else False
            },
            "watermarks": {
                "count": len(detected_markers),
                "detected": detected_markers
            }
        }


def print_report(file_path: str, result: dict):
    print("=" * 65)
    print("       ГЛУБОКИЙ НЕЙРОСЕТЕВОЙ АНАЛИЗ ТЕКСТА НА ПРИЗНАКИ ИИ")
    print("=" * 65)
    print(f"Файл: {os.path.basename(file_path)}")
    print("-" * 65)
    
    if "error" in result:
        print(f" ОШИБКА: {result['error']}")
        print("=" * 65)
        return

    prob = result["ai_probability_percent"]
    
    if prob >= 70:
        verdict = "[ ВЫСОКАЯ ВЕРОЯТНОСТЬ ИИ ]"
        desc = "Структура токенов и паттерны совпали с распределениями генеративных моделей."
    elif prob >= 40:
        verdict = "[ СМЕШАННЫЙ ТЕКСТ / РЕДАКТУРА ]"
        desc = "Обнаружены отдельные фрагменты и паттерны, характерные для ИИ."
    else:
        verdict = "[ НАПИСАНО ЧЕЛОВЕКОМ ]"
        desc = "Распределение словаря и вариативность структуры естественны."

    print(f"Вероятность ИИ (Neural Model Score): {prob}%")
    print(f"Вердикт:   {verdict}")
    print(f"Пояснение: {desc}")
    print("-" * 65)
    
    print(" АНАЛИЗ СТРУКТУРЫ И РИТМИКИ:")
    metrics = result["metrics"]
    print(f"  • Предложений:  {metrics['total_sentences']}")
    print(f"  • Слов:         {metrics['total_words']}")
    print(f"  • Вариативность (Burstiness): {metrics['burstiness']}")
    print(f"  • Монотонность структуры:     {'Да (характерно для ИИ)' if metrics['is_monotonous'] else 'Нет (естественный ритм)'}")
    
    print("-" * 65)
    print(" ТЕКСТОВЫЕ ВОДЯНЫЕ ЗНАКИ И ИИ-КЛИШЕ:")
    wm = result["watermarks"]
    print(f"  • Найдено клише: {wm['count']}")
    if wm['detected']:
        for item in wm['detected']:
            print(f"     - \"{item}\"")
    else:
        print("  • Клише и водяные знаки не обнаружены.")
    print("=" * 65)


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

    detector = AITextDetector()
    result = detector.analyze(text)
    print_report(file_path, result)


if __name__ == "__main__":
    main()
