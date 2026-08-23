import re
import math
import sys
import os
from collections import Counter
from typing import Dict, List, Tuple, Optional
import statistics
import json
from datetime import datetime

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
                'additionally', 'ultimately', 'overall', 'accordingly',
                'explore', 'journey', 'discover', 'insight', 'perspective',
                'framework', 'methodology', 'implementation', 'optimization'
            ],
            'russian': [
                'погружение', 'рассмотрение', 'выявление', 'трансформационный',
                'синергия', 'парадигма', 'революционный', 'прорывной',
                'передовой', 'инновационный', 'всесторонний', 'значительный',
                'примечательный', 'критический', 'существенный', 'более того',
                'кроме того', 'следовательно', 'дополнительно', 'в конечном счете',
                'в целом', 'соответственно', 'отметим', 'подчеркнем',
                'рассмотрим', 'проанализируем', 'выделим', 'ключевой',
                'оптимизация', 'имплементация', 'методология', 'фреймворк'
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
            r'<\|[^|]+\|>',  # Специальные маркеры
            r'\[INST\]',  # Маркеры инструкций
            r'\[/INST\]',
            r'<s>', r'</s>',
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
                'error': 'Текст слишком короткий для анализа (минимум 10 символов)',
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


def print_report(result: Dict, filename: str = None):
    """
    Красивое отображение отчета в консоли
    """
    print("\n" + "=" * 80)
    print("📊 ОТЧЕТ ПО АНАЛИЗУ ТЕКСТА НА ПРИЗНАКИ ИИ")
    print("=" * 80)
    
    if filename:
        print(f"📁 Файл: {filename}")
    
    print(f"⏰ Время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    if 'error' in result:
        print(f"❌ ОШИБКА: {result['error']}")
        print("=" * 80)
        return
    
    # Основные результаты
    print(f"\n🎯 ВЕРОЯТНОСТЬ ИИ: {result['ai_probability']}%")
    print(f"📈 Уровень: {result['probability_level']}")
    
    # Прогресс-бар
    prob = result['ai_probability'] / 100
    bar_length = 50
    filled = int(bar_length * prob)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n   [{bar}] {result['ai_probability']}%")
    
    print("\n" + "-" * 80)
    print("📋 ДЕТАЛЬНЫЙ АНАЛИЗ:")
    print("-" * 80)
    
    details = result['details']
    
    # Основные метрики
    metrics = [
        ('Язык', details.get('language', 'N/A'), ''),
        ('Количество слов', details.get('word_count', 0), ''),
        ('Количество символов', details.get('character_count', 0), ''),
        ('Перплексия', details.get('perplexity', 0), f"(скop: {details.get('perplexity_score', 0)})"),
        ('Всплески (burstiness)', details.get('burstiness', 0), f"(скop: {details.get('burstiness_score', 0)})"),
        ('Повторяемость', details.get('repetition', 0), f"(скop: {details.get('repetition_score', 0)})"),
        ('Энтропия', details.get('entropy', 0), f"(скop: {details.get('entropy_score', 0)})"),
        ('Разнообразие пунктуации', details.get('punctuation_diversity', 0), ''),
        ('Найдено маркеров ИИ', details.get('ai_markers_found', 0), ''),
        ('Водяные знаки', '✅ Да' if details.get('has_watermark') else '❌ Нет', ''),
    ]
    
    for label, value, extra in metrics:
        print(f"  • {label:25} : {value} {extra}")
    
    # Список маркеров
    markers = details.get('ai_markers_list', [])
    if markers:
        print(f"\n  🔍 Найденные маркеры ИИ ({len(markers)}):")
        for marker in markers[:5]:  # Показываем первые 5
            print(f"    - {marker}")
        if len(markers) > 5:
            print(f"    ... и еще {len(markers) - 5}")
    
    # Водяные знаки
    watermarks = details.get('watermarks_found', [])
    if watermarks:
        print(f"\n  💧 Найденные водяные знаки ({len(watermarks)}):")
        for wm in watermarks[:3]:
            print(f"    - {wm}")
    
    print("\n" + "=" * 80)
    
    # Рекомендации
    prob_value = result['ai_probability']
    print("\n💡 РЕКОМЕНДАЦИИ:")
    if prob_value < 30:
        print("  ✅ Текст, скорее всего, написан человеком")
        print("  📝 Отсутствуют характерные признаки ИИ-генерации")
    elif prob_value < 50:
        print("  ⚠️ Текст имеет некоторые признаки ИИ, но неоднозначно")
        print("  🔍 Рекомендуется дополнительный анализ")
    elif prob_value < 75:
        print("  ⚠️ Текст демонстрирует признаки ИИ-генерации")
        print("  🔍 Рекомендуется проверка другими методами")
    else:
        print("  🚨 Текст с высокой вероятностью сгенерирован ИИ")
        print("  🔍 Характерные признаки: однообразие структуры, шаблонные фразы")
    
    print("=" * 80 + "\n")


def main():
    """
    Основная функция для запуска из командной строки
    """
    if len(sys.argv) < 2:
        print("❌ ОШИБКА: Укажите путь к файлу с текстом")
        print("\nИспользование:")
        print(f"  python {os.path.basename(__file__)} input_text.txt")
        print(f"  python {os.path.basename(__file__)} input_text.txt --json  # для JSON вывода")
        sys.exit(1)
    
    file_path = sys.argv[1]
    json_output = '--json' in sys.argv
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"❌ ОШИБКА: Файл '{file_path}' не найден")
        sys.exit(1)
    
    # Читаем текст из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"❌ ОШИБКА при чтении файла: {e}")
        sys.exit(1)
    
    if not text.strip():
        print("❌ ОШИБКА: Файл пуст")
        sys.exit(1)
    
    # Анализируем текст
    analyzer = AITextAnalyzer()
    result = analyzer.analyze_text(text)
    
    # Выводим результат
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result, file_path)


if __name__ == "__main__":
    main()

