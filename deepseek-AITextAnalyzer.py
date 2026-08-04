# https://chat.deepseek.com/a/chat/s/adeacbcc-1f11-4ea9-bd52-f404afae5321 mzothing@gmail.com
import re
import math
from collections import Counter
from typing import Dict, List, Tuple, Optional
import statistics

class AITextAnalyzer:
    """
    Анализатор текста для выявления признаков ИИ-генерации
    """

    def __init__(self):
        # Стоп-слова и маркеры ИИ
        self.ai_markers = {
            'english': [
                'delve', 'unveil', 'navigate', 'realm', 'transformative',
                'leverage', 'synergy', 'landscape', 'paradigm', 'pivotal',
                'resonate', 'embark', 'unprecedented', 'cutting-edge',
                'state-of-the-art', 'groundbreaking', 'revolutionary',
                'comprehensive', 'significant', 'notable', 'crucial',
                'essential', 'moreover', 'furthermore', 'consequently',
                'additionally', 'ultimately', 'overall', 'accordingly'
            ],
            'russian': [
                'погружение', 'рассмотрение', 'выявление', 'трансформационный',
                'синергия', 'парадигма', 'революционный', 'прорывной',
                'передовой', 'инновационный', 'всесторонний', 'значительный',
                'примечательный', 'критический', 'существенный', 'более того',
                'кроме того', 'следовательно', 'дополнительно', 'в конечном счете',
                'в целом', 'соответственно', 'отметим', 'подчеркнем'
            ]
        }

        # Шаблоны для водяных знаков
        self.watermark_patterns = [
            r'\[[A-Za-z0-9]{8,}\]',  # [ABC12345]
            r'\{[A-Za-z0-9]{6,}\}',  # {abc123}
            r'<[A-Za-z0-9]{6,}>',    # <abc123>
            r'#[A-Za-z0-9]{6,}',     # #abc123
            r'генерировано\s+ИИ',
            r'создано\s+нейросетью',
            r'generated\s+by\s+AI',
            r'AI-generated',
            r'chatgpt',
            r'gpt-\d+',
            r'claude',
            r'bard',
            r'copilot',
            r'💬',
            r'🤖',
            r'✨',
            r'［[^］]+］',  # Японские скобки
            r'【[^】]+】',  # Китайские скобки
        ]

        # Базовые статистические пороги
        self.thresholds = {
            'perplexity_high': 80,    # Низкая перплексия = возможный ИИ
            'burstiness_low': 0.4,    # Низкая вариативность = возможный ИИ
            'repetition_high': 0.15,  # Высокий повтор = возможный ИИ
            'entropy_low': 4.0,       # Низкая энтропия = возможный ИИ
        }

    def detect_language(self, text: str) -> str:
        """Определение языка текста"""
        # Простая эвристика по символам
        cyrillic = len(re.findall(r'[а-яА-ЯёЁ]', text))
        latin = len(re.findall(r'[a-zA-Z]', text))

        if cyrillic > latin:
            return 'russian'
        elif latin > cyrillic:
            return 'english'
        else:
            # Проверка по частоте слов
            words = text.lower().split()
            english_words = ['the', 'to', 'and', 'for', 'of', 'with', 'on', 'at']
            russian_words = ['и', 'в', 'на', 'с', 'по', 'для', 'от', 'из']

            eng_count = sum(1 for w in words if w in english_words)
            rus_count = sum(1 for w in words if w in russian_words)

            return 'russian' if rus_count > eng_count else 'english'

    def analyze_perplexity(self, text: str) -> float:
        """
        Анализ перплексии (сложности предсказания текста)
        Низкая перплексия может указывать на ИИ
        """
        words = text.lower().split()
        if len(words) < 3:
            return 0

        # Используем частоты униграмм и биграмм
        unigrams = Counter(words)
        bigrams = Counter([' '.join(words[i:i+2]) for i in range(len(words)-1)])

        # Вычисляем среднюю вероятность
        log_prob = 0
        count = 0

        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            prob = (bigrams[bigram] + 1) / (unigrams[words[i]] + len(unigrams))
            if prob > 0:
                log_prob += -math.log2(prob)
                count += 1

        if count == 0:
            return 100  # Высокая перплексия для коротких текстов

        perplexity = 2 ** (log_prob / count)
        return min(perplexity, 200)  # Ограничиваем для стабильности

    def analyze_burstiness(self, text: str) -> float:
        """
        Анализ всплесков (вариативность длины предложений)
        Низкая вариативность может указывать на ИИ
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

        if len(sentences) < 3:
            return 0

        lengths = [len(s.split()) for s in sentences]
        mean_len = statistics.mean(lengths)
        if mean_len == 0:
            return 0

        variance = statistics.variance(lengths) if len(lengths) > 1 else 0
        burstiness = variance / mean_len

        return min(burstiness, 2.0)  # Ограничиваем для стабильности

    def analyze_repetition(self, text: str) -> float:
        """
        Анализ повторяемости слов и фраз
        Высокая повторяемость может указывать на ИИ
        """
        words = text.lower().split()
        if len(words) < 10:
            return 0

        word_freq = Counter(words)
        total_words = len(words)

        # Доля слов, которые встречаются более 1 раза
        repeated_words = sum(1 for count in word_freq.values() if count > 1)
        repetition_ratio = repeated_words / len(word_freq)

        # Доля повторяющихся биграмм
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        bigram_freq = Counter(bigrams)
        repeated_bigrams = sum(1 for count in bigram_freq.values() if count > 1)
        bigram_ratio = repeated_bigrams / len(bigram_freq) if bigram_freq else 0

        return min((repetition_ratio + bigram_ratio) / 2, 1.0)

    def analyze_entropy(self, text: str) -> float:
        """
        Анализ энтропии (разнообразия) текста
        Низкая энтропия может указывать на ИИ
        """
        words = text.lower().split()
        if len(words) < 5:
            return 0

        freq = Counter(words)
        total = len(words)

        entropy = 0
        for count in freq.values():
            prob = count / total
            entropy -= prob * math.log2(prob)

        return entropy

    def analyze_punctuation(self, text: str) -> float:
        """
        Анализ пунктуации
        ИИ часто использует ограниченный набор знаков препинания
        """
        total_chars = len(text)
        if total_chars == 0:
            return 0

        punctuation = re.findall(r'[.,!?;:]', text)
        punc_ratio = len(punctuation) / total_chars

        # Проверяем разнообразие пунктуации
        unique_punc = set(punctuation)
        diversity = len(unique_punc) / 5  # максимум 5 типов знаков

        return punc_ratio * diversity

    def detect_ai_markers(self, text: str, lang: str) -> Tuple[int, List[str]]:
        """
        Поиск маркеров ИИ в тексте
        """
        text_lower = text.lower()
        markers = self.ai_markers.get(lang, [])
        found_markers = []

        for marker in markers:
            if marker.lower() in text_lower:
                found_markers.append(marker)

        return len(found_markers), found_markers

    def detect_watermarks(self, text: str) -> Tuple[bool, List[str]]:
        """
        Поиск водяных знаков в тексте
        """
        found_patterns = []

        for pattern in self.watermark_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_patterns.extend(matches)

        return len(found_patterns) > 0, found_patterns

    def analyze_text(self, text: str) -> Dict:
        """
        Комплексный анализ текста
        """
        if not text or len(text.strip()) < 10:
            return {
                'error': 'Текст слишком короткий для анализа',
                'ai_probability': 0,
                'details': {}
            }

        # Определяем язык
        lang = self.detect_language(text)

        # Собираем все метрики
        perplexity = self.analyze_perplexity(text)
        burstiness = self.analyze_burstiness(text)
        repetition = self.analyze_repetition(text)
        entropy = self.analyze_entropy(text)
        punctuation = self.analyze_punctuation(text)
        marker_count, found_markers = self.detect_ai_markers(text, lang)
        has_watermark, watermarks = self.detect_watermarks(text)

        # Нормализуем показатели (0-1)
        perplexity_score = max(0, min(1, 1 - (perplexity / self.thresholds['perplexity_high'])))
        burstiness_score = max(0, min(1, 1 - (burstiness / self.thresholds['burstiness_low'])))
        repetition_score = max(0, min(1, repetition / self.thresholds['repetition_high']))
        entropy_score = max(0, min(1, 1 - (entropy / self.thresholds['entropy_low'])))

        # Ограничиваем маркеры
        marker_score = min(1, marker_count / 5)  # 5 маркеров = 100%

        # Веса для каждого признака
        weights = {
            'perplexity': 0.25,
            'burstiness': 0.20,
            'repetition': 0.15,
            'entropy': 0.15,
            'markers': 0.15,
            'punctuation': 0.10
        }

        # Водяные знаки дают большой бонус
        watermark_bonus = 0.3 if has_watermark else 0

        # Вычисляем общую вероятность
        ai_probability = (
            perplexity_score * weights['perplexity'] +
            burstiness_score * weights['burstiness'] +
            repetition_score * weights['repetition'] +
            entropy_score * weights['entropy'] +
            marker_score * weights['markers'] +
            (1 - punctuation) * weights['punctuation']
        ) + watermark_bonus

        ai_probability = min(1.0, ai_probability)

        # Формируем детализированный отчет
        details = {
            'language': lang,
            'perplexity': round(perplexity, 2),
            'perplexity_score': round(perplexity_score, 3),
            'burstiness': round(burstiness, 3),
            'burstiness_score': round(burstiness_score, 3),
            'repetition': round(repetition, 3),
            'repetition_score': round(repetition_score, 3),
            'entropy': round(entropy, 3),
            'entropy_score': round(entropy_score, 3),
            'punctuation_diversity': round(punctuation, 3),
            'ai_markers_found': marker_count,
            'ai_markers_list': found_markers[:10],  # Ограничиваем список
            'has_watermark': has_watermark,
            'watermarks_found': watermarks[:5],  # Ограничиваем список
            'word_count': len(text.split()),
            'character_count': len(text)
        }

        return {
            'ai_probability': round(ai_probability * 100, 1),
            'probability_level': self._get_probability_level(ai_probability),
            'details': details
        }

    def _get_probability_level(self, probability: float) -> str:
        """Определение уровня вероятности"""
        if probability < 0.2:
            return 'Низкая (вероятно, написан человеком)'
        elif probability < 0.4:
            return 'Низкая-средняя'
        elif probability < 0.6:
            return 'Средняя (возможно, смешанный)'
        elif probability < 0.8:
            return 'Высокая (вероятно, ИИ)'
        else:
            return 'Очень высокая (почти точно ИИ)'


# Функция для быстрого использования
def analyze_ai_text(text: str) -> Dict:
    """
    Быстрый анализ текста на признаки ИИ

    Args:
        text: Текст для анализа

    Returns:
        Словарь с результатами анализа
    """
    analyzer = AITextAnalyzer()
    return analyzer.analyze_text(text)


# Пример использования
if __name__ == "__main__":
    # Пример текста от ИИ
    ai_text = """
    В современном мире технологии развиваются стремительными темпами.
    Искусственный интеллект становится неотъемлемой частью нашей повседневной жизни.
    Важно отметить, что внедрение ИИ-технологий открывает новые горизонты для развития.
    Более того, интеграция нейросетей в различные сферы деятельности позволяет
    достичь беспрецедентных результатов. В конечном счете, это приводит к
    трансформации существующих парадигм и созданию инновационных решений.
    """

    # Пример текста от человека
    human_text = """
    Вчера я купил новую книгу в местном книжном магазине.
    Продавец посоветовал мне роман одного современного автора.
    Честно говоря, я не ожидал, что книга окажется настолько захватывающей.
    Прочитал уже половину и не могу оторваться!
    Наверное, буду читать всю ночь, чтобы узнать, чем закончится история.
    """

    print("=" * 60)
    print("АНАЛИЗ ТЕКСТА НА ПРИЗНАКИ ИИ")
    print("=" * 60)

    # Анализ ИИ-текста
    print("\n📝 Анализ ИИ-текста:")
    result_ai = analyze_ai_text(ai_text)
    print(f"Вероятность ИИ: {result_ai['ai_probability']}%")
    print(f"Уровень: {result_ai['probability_level']}")
    print("\nДетали:")
    for key, value in result_ai['details'].items():
        if not key.endswith('_list') and not key.startswith('has_'):
            print(f"  {key}: {value}")

    print("\n" + "-" * 60)

    # Анализ человеческого текста
    print("\n📝 Анализ человеческого текста:")
    result_human = analyze_ai_text(human_text)
    print(f"Вероятность ИИ: {result_human['ai_probability']}%")
    print(f"Уровень: {result_human['probability_level']}")
    print("\nДетали:")
    for key, value in result_human['details'].items():
        if not key.endswith('_list') and not key.startswith('has_'):
            print(f"  {key}: {value}")

