"""Загрузка синонимов для индексации"""
from pathlib import Path

SYNONYMS_FILE = Path(__file__).parent / "synonyms.txt"

def get_synonyms_list():
    """
    Возвращает список синонимов в формате для Elasticsearch
    Формат: каждая строка - это группа синонимов, разделенных запятыми
    """
    synonyms_list = []
    
    with open(SYNONYMS_FILE, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                # Разбиваем по запятым и очищаем от пробелов
                words = [w.strip() for w in line.split(',') if w.strip()]
                
                # Удаляем пустые слова
                words = [w for w in words if w and len(w) > 0]
                
                if len(words) > 1:
                    # Очищаем слова от проблемных символов
                    cleaned_words = []
                    seen_words = set()  # Для удаления дубликатов
                    
                    for word in words:
                        # Заменяем специальные символы валют на текстовые эквиваленты
                        word_clean = word.replace('$', 'USD').replace('€', 'EUR').replace('₽', 'RUB')
                        # Убираем переносы строк, табы, кавычки
                        word_clean = word_clean.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
                        word_clean = word_clean.replace('"', '').replace("'", '')
                        # Убираем множественные пробелы
                        word_clean = ' '.join(word_clean.split())
                        # Убираем пробелы в начале и конце
                        word_clean = word_clean.strip()
                        
                        # Проверяем, что слово не пустое и не слишком длинное
                        if word_clean and len(word_clean) > 0 and len(word_clean) < 80:
                            # Проверяем, что нет проблемных символов
                            if not any(c in word_clean for c in ['\n', '\r', '\t', '=>']):
                                # Убираем дубликаты (регистронезависимо)
                                word_lower = word_clean.lower()
                                if word_lower not in seen_words:
                                    seen_words.add(word_lower)
                                    cleaned_words.append(word_clean)
                    
                    if len(cleaned_words) > 1:
                        # Формат для Elasticsearch: многословные синонимы нужно обернуть в кавычки
                        formatted_words = []
                        for word in cleaned_words:
                            # Если синоним содержит пробелы (многословный), оборачиваем в кавычки
                            if ' ' in word:
                                formatted_words.append(f'"{word}"')
                            else:
                                formatted_words.append(word)
                        
                        synonym_line = ', '.join(formatted_words)
                        # Проверяем финальную строку
                        if len(synonym_line) < 500 and '\n' not in synonym_line and '\r' not in synonym_line:
                            synonyms_list.append(synonym_line)
            except Exception:
                continue
    
    return synonyms_list

