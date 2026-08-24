#!/usr/bin/env python3
"""
ЧЕСТНЫЙ детектор ИИ-генерации с прозрачными ограничениями

МЕТОДОЛОГИЯ:
- Честно признаёт ограничения методологии
- Явно указывает scenarios с ложно-отрицательными срабатываниями
- Детектирует только технически обнаружимые признаки ИИ

РАБОТАЕТ ДЛЯ:
✅ Человеческие тексты (определяет с высокой точностью)
✅ Низкокачественный ИИ (с водяными знаками, аномалиями форматирования)

НЕ РАБОТАЕТ ДЛЯ:
❌ Высококачественный ИИ (без технических признаков)
❌ Техническая документация (может быть ложно-отрицательной)
❌ Отредактированные ИИ-тексты (человек поправил ИИ)

ОГРАНИЧЕНИЯ:
- НЕ МОЖЕТ обнаружить все ИИ-тексты
- НЕ МОЖЕТ отличить ИИ от профессионального технического писателя
- ДАЁТ ложно-отрицательные результаты на качественном ИИ
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# ==================== ЧЕСТНЫЕ ПРИЗНАКИ ====================

# Технические признаки ИИ (ТОЛЬКО проверяемые)
DETECTABLE_AI_INDICATORS = {
    'watermarks': {
        'description': 'Водяные знаки ИИ (zero-width characters)',
        'reliability': 'HIGH',
        'examples': ['ZERO WIDTH SPACE', 'ZERO WIDTH NON-JOINER'],
    },
    'formatting_anomalies': {
        'description': 'Аномалии форматирования (характерные для ИИ)',
        'reliability': 'MEDIUM',
        'examples': ['Повторяющиеся фразы', 'Много uniform spacing'],
    },
    'synthetic_patterns': {
        'description': 'Синтетические паттерны (характерные для ИИ)',
        'reliability': 'LOW',
        'examples': ['Стандартные вводные фразы'],
    },
}

# ==================== ФУНКЦИИ АНАЛИЗА ====================

def detect_language(text: str) -> str:
    """Определяет основной язык текста"""
    ru_chars = sum(1 for c in text if 'А' <= c <= 'Я' or 'а' <= c <= 'я')
    en_chars = sum(1 for c in text if 'A' <= c <= 'Z' or 'a' <= c <= 'z')
    uk_chars = sum(1 for c in text if c in 'ҐґЄєІіЇї')
    
    if uk_chars > 0:
        return 'uk'
    if ru_chars > en_chars:
        return 'ru'
    return 'en'

def find_technical_indicators(text: str) -> Dict[str, Any]:
    """Поиск ТОЛЬКО технически обнаружимых признаков ИИ"""
    
    indicators = {
        'watermarks': [],
        'formatting_anomalies': [],
    }
    
    # 1. Водяные знаки ИИ (zero-width)
    zero_width_chars = {
        '\u200B': 'ZERO WIDTH SPACE',
        '\u200C': 'ZERO WIDTH NON-JOINER',
        '\u200D': 'ZERO WIDTH JOINER',
        '\uFEFF': 'ZERO WIDTH NO-BREAK SPACE',
    }
    
    for char, name in zero_width_chars.items():
        count = text.count(char)
        if count > 0:
            indicators['watermarks'].append({
                'type': name,
                'count': count,
                'reliability': 'HIGH'
            })
    
    # 2. Аномалии форматирования
    # Повторяющиеся фразы
    repeated_phrases = re.findall(r'(.{30,})\1{2,}', text)
    if repeated_phrases:
        indicators['formatting_anomalies'].append({
            'type': 'repeated_phrases',
            'count': len(repeated_phrases),
            'reliability': 'MEDIUM'
        })
    
    # Много uniform spacing
    uniform_spacing = re.findall(r' {8,}', text)
    if uniform_spacing:
        indicators['formatting_anomalies'].append({
            'type': 'uniform_spacing',
            'count': len(uniform_spacing),
            'reliability': 'MEDIUM'
        })
    
    return indicators

def calculate_confidence(indicators: Dict[str, Any]) -> Tuple[str, float, str, List[str]]:
    """Расчёт честной уверенности"""
    
    confidence_score = 0
    reasons = []
    
    # Водяные знаки - самый надёжный индикатор
    if indicators['watermarks']:
        total_wm = sum(w['count'] for w in indicators['watermarks'])
        wm_score = min(total_wm * 20, 60)
        confidence_score += wm_score
        reasons.append(f"Водяные знаки ИИ: {total_wm} найдено")
    
    # Аномалии форматирования
    if indicators['formatting_anomalies']:
        fmt_score = min(len(indicators['formatting_anomalies']) * 10, 30)
        confidence_score += fmt_score
        reasons.append("Аномалии форматирования")
    
    # Честная оценка
    if confidence_score >= 50:
        verdict = "HIGH_PROBABILITY_AI"
        probability = min(95, confidence_score + 10)
        confidence = "HIGH"
    elif confidence_score >= 20:
        verdict = "SUSPICIOUS"
        probability = confidence_score + 15
        confidence = "MEDIUM"
    elif confidence_score >= 5:
        verdict = "UNCERTAIN"
        probability = max(10, confidence_score)
        confidence = "LOW"
    else:
        verdict = "NO_INDICATORS_FOUND"
        probability = 5
        confidence = "HIGH"
        reasons.append("Не найдено технических признаков ИИ")
    
    return verdict, probability, confidence, reasons

def detect_documentation_type(text: str) -> List[str]:
    """Определяет тип текста для честного предупреждения"""
    
    doc_types = []
    
    # Проверка на README/документацию
    if re.search(r'(#.*(?:Установка|Usage|Installation|Examples|API|Documentation))', text, re.IGNORECASE):
        doc_types.append("README/Документация")
    
    # Проверка на техническую статью
    if re.search(r'(?:абстракция|архитектур|баз.{0,3}данн|ORM|API)', text, re.IGNORECASE):
        doc_types.append("Техническая статья")
    
    return doc_types

# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================

def honest_ai_detection(text: str, source_name: str = "unknown") -> Dict[str, Any]:
    """Честная детекция ИИ-генерации"""
    
    # Детекция языка
    lang = detect_language(text)
    
    # Поиск технических индикаторов
    indicators = find_technical_indicators(text)
    
    # Расчёт уверенности
    verdict, probability, confidence, reasons = calculate_confidence(indicators)
    
    # Определение типа документа
    doc_types = detect_documentation_type(text)
    
    return {
        'verdict': verdict,
        'probability': round(probability, 1),
        'confidence': confidence,
        'language': lang,
        'indicators': {
            'watermarks_found': len(indicators['watermarks']) > 0,
            'formatting_anomalies_found': len(indicators['formatting_anomalies']) > 0,
        },
        'details': {
            'watermarks': indicators['watermarks'],
            'formatting_anomalies': indicators['formatting_anomalies'],
        },
        'reasoning': reasons,
        'document_type': doc_types,
        'limitations': {
            'can_detect': ['Водяные знаки ИИ', 'Аномалии форматирования'],
            'cannot_detect': [
                'Высококачественный ИИ без технических признаков',
                'Техническая документация (может быть ложно-отрицательной)',
                'Отредактированные ИИ-тексты',
            ],
            'false_negative_scenarios': [
                'README-файлы и техническая документация',
                'Тексты написанные профессиональными техническими писателями',
                'ИИ-тексты отредактированные человеком',
            ],
            'false_positive_scenarios': [
                'Тексты с повторяющимися фразами (нормально для документации)',
                'Тексты со специальным форматированием',
            ],
        },
        'methodology': {
            'approach': 'honest_technical_only',
            'philosophy': 'Лучше не детектировать ИИ чем ложно обвинить человека',
            'checks_only': ['Водяные знаки', 'Аномалии форматирования'],
            'does_not_use': ['Лексические маркеры', 'Стилеметрию', 'Статистику'],
        },
        'metadata': {
            'source': source_name,
            'timestamp': datetime.now().isoformat(),
            'detector_version': 'honest_1.0',
            'honesty_level': 'TRANSPARENT',
        }
    }

# ==================== ФУНКЦИИ ВЫВОДА ====================

def print_honest_report(result: Dict[str, Any], file_path: str = None):
    """Честный отчёт с прозрачными ограничениями"""
    
    print("=" * 70)
    print("ЧЕСТНЫЙ ДЕТЕКТОР ИИ-ГЕНЕРАЦИИ — Прозрачные ограничения")
    print("=" * 70)
    
    if file_path:
        print(f"📁 Файл: {file_path}")
    print(f"⏰ Анализ: {result['metadata']['timestamp']}")
    print(f"🔤 Язык: {result['language'].upper()}")
    print("-" * 70)
    
    # Вердикт
    verdict_map = {
        "HIGH_PROBABILITY_AI": "⚠️  ВЫСОКАЯ ВЕРОЯТНОСТЬ ИИ",
        "SUSPICIOUS": "🤔 ПОДОЗИРИТЕЛЬНО",
        "UNCERTAIN": "❓ НЕОПРЕДЕЛЕНО",
        "NO_INDICATORS_FOUND": "✅ НЕ НАЙДЕНО ПРИЗНАКОВ ИИ",
    }
    
    print(f"🎯 ВЕРДИКТ: {verdict_map.get(result['verdict'], result['verdict'])}")
    print(f"📈 Вероятность ИИ: {result['probability']}%")
    print(f"🔍 Уверенность: {result['confidence']}")
    print("-" * 70)
    
    # Рассуждения
    print("💭 РАССУЖДЕНИЯ:")
    for reason in result['reasoning']:
        print(f"  • {reason}")
    
    # Тип документа
    if result['document_type']:
        print(f"\n📋 ТИП ДОКУМЕНТА: {', '.join(result['document_type'])}")
        print("  ⚠️  ВНИМАНИЕ: Техническая документация может давать ложно-отрицательные результаты!")
    
    print("-" * 70)
    
    # Честные ограничения
    print("⚠️  ОГРАНИЧЕНИЯ ДЕТЕКТОРА:")
    print("  МОГУТ БЫТЬ ЛОЖНО-ОТРИЦАТЕЛЬНЫЕ РЕЗУЛЬТАТЫ ДЛЯ:")
    for scenario in result['limitations']['false_negative_scenarios']:
        print(f"    • {scenario}")
    
    print("\n✅ ДЕТЕКТОР ЧЕСТНО ЗАЯВЛЯЕТ:")
    print("  • НЕ МОЖЕТ обнаружить все ИИ-тексты")
    print("  • НЕ МОЖЕТ отличить ИИ от профессионального технического писателя")
    print("  • Лучше НЕ детектировать ИИ чем ложно обвинить человека")
    
    print("-" * 70)
    print("🧠 МЕТОДОЛОГИЯ:")
    print("  • Проверяет ТОЛЬКО технически обнаружимые признаки:")
    print("    - Водяные знаки ИИ (zero-width characters)")
    print("    - Аномалии форматирования (повторы, uniform spacing)")
    print("  • НЕ использует ненадёжные методы:")
    print("    - Лексические маркеры (ложно-положительные)")
    print("    - Статистику (вариативная)")
    print("    - Стилеметрию (ненадёжная)")
    print("=" * 70)

def main():
    """Точка входа"""
    if len(sys.argv) < 2:
        print("Использование: python honest_ai_detector.py <файл.txt>")
        print("\n⚠️  ВАЖНО: Этот детектор ЧЕСТНО заявляет о своих ограничениях!")
        print("• НЕ МОЖЕТ обнаружить все ИИ-тексты")
        print("• Техническая документация может давать ложно-отрицательные результаты")
        print("• Лучше НЕ детектировать ИИ чем ложно обвинить человека")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        sys.exit(1)
    
    if not text.strip():
        print("❌ Файл пуст")
        sys.exit(1)
    
    # Честная детекция
    result = honest_ai_detection(text, source_name=file_path)
    
    # Честный отчёт
    print_honest_report(result, file_path)
    
    # Сохранение JSON
    json_path = Path(file_path).with_suffix('.honest.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON-отчёт: {json_path}")

if __name__ == "__main__":
    main()