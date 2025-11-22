"""Модуль для исправления опечаток в поисковых запросах"""
import re
from pathlib import Path

CUSTOM_WORDS_FILE = Path(__file__).parent / "custom_words.txt"

# Загружаем словарь специфичных слов
CUSTOM_WORDS = set()
if CUSTOM_WORDS_FILE.exists():
    with open(CUSTOM_WORDS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                CUSTOM_WORDS.add(line.lower())
                CUSTOM_WORDS.add(line)  # Сохраняем оригинальный регистр


def load_custom_words():
    return CUSTOM_WORDS


def is_likely_typo(word: str, custom_words: set) -> bool:
    word_lower = word.lower()
    
    # Если слово в словаре - не опечатка
    if word_lower in custom_words or word in custom_words:
        return False
    
    # Если слово слишком короткое - не проверяем
    if len(word) < 3:
        return False
    
    # Если слово содержит только буквы и достаточно длинное - возможно опечатка
    if word.isalpha() and len(word) >= 4:
        return True
    
    return False


def fix_common_typos(word: str) -> str:
    # Частые опечатки в русском языке
    common_typos = {
        'инвестицйи': 'инвестиции',
        'инвестицй': 'инвестиции',
        'стартапп': 'стартап',
        'старта': 'стартап',
        'бизнесс': 'бизнес',
        'бизнез': 'бизнес',
        'компани': 'компания',
        'компаниа': 'компания',
        'предпринимательсво': 'предпринимательство',
        'технолгии': 'технологии',
        'технолги': 'технологии',
        'разработчк': 'разработчик',
        'приложенние': 'приложение',
        'приложеня': 'приложение',
        'маркетплей': 'маркетплейс',
        'маркетплес': 'маркетплейс',
        'продаж': 'продажи',
        'продажы': 'продажи',
        'клиен': 'клиент',
        'управлене': 'управление',
        'управлени': 'управление',
        'манагер': 'менеджер',
        'менеджр': 'менеджер',
        'команд': 'команда',
    }
    
    word_lower = word.lower()
    if word_lower in common_typos:
        # Сохраняем регистр первой буквы
        if word[0].isupper():
            return common_typos[word_lower].capitalize()
        return common_typos[word_lower]
    
    return word


def suggest_corrections(word: str, custom_words: set) -> list:
    word_lower = word.lower()
    suggestions = []
    
    # Проверяем точные совпадения с разным регистром
    for known_word in custom_words:
        if known_word.lower() == word_lower and known_word != word:
            suggestions.append(known_word)
    
    # Простой алгоритм: ищем слова с похожим началом
    if len(word) >= 3:
        prefix = word_lower[:3]
        for known_word in custom_words:
            known_lower = known_word.lower()
            if known_lower.startswith(prefix) and known_lower != word_lower:
                # Простая проверка расстояния Левенштейна (упрощенная)
                if abs(len(known_lower) - len(word_lower)) <= 2:
                    suggestions.append(known_word)
    
    return suggestions[:3]  # Возвращаем до 3 вариантов


def fix_query_typos(query: str) -> str:
    custom_words = load_custom_words()
    words = re.findall(r'\b\w+\b', query)
    fixed_words = []
    
    for word in words:
        # Сначала пробуем исправить частые опечатки
        fixed = fix_common_typos(word)
        
        # Если не исправили и похоже на опечатку - ищем в словаре
        if fixed == word and is_likely_typo(word, custom_words):
            suggestions = suggest_corrections(word, custom_words)
            if suggestions:
                # Используем первое предложение
                fixed = suggestions[0]
        
        fixed_words.append(fixed)
    
    # Восстанавливаем запрос с исправленными словами
    result = query
    for original, fixed in zip(words, fixed_words):
        if original != fixed:
            result = result.replace(original, fixed, 1)
    
    return result

