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


def levenshtein_distance(s1: str, s2: str) -> int:
    """Вычисляет расстояние Левенштейна между двумя строками"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def suggest_corrections(word: str, custom_words: set) -> list:
    word_lower = word.lower()
    suggestions = []
    
    for known_word in custom_words:
        known_lower = known_word.lower()
        if known_lower == word_lower:
            continue
        
        distance = levenshtein_distance(word_lower, known_lower)
        max_distance = 2 if len(word) <= 6 else 3
        if distance <= max_distance:
            suggestions.append((known_word, distance))
    
    suggestions.sort(key=lambda x: x[1])
    return [word for word, _ in suggestions[:3]]


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

