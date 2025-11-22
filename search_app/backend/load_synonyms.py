"""Загрузка синонимов из файла"""
from pathlib import Path

SYNONYMS_FILE = Path(__file__).parent / "synonyms.txt"

def load_synonyms():
    """Загружает синонимы из файла и возвращает словарь"""
    synonyms_dict = {}
    
    with open(SYNONYMS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            words = [w.strip() for w in line.split(',') if w.strip()]
            if len(words) > 1:
                for word in words:
                    word_lower = word.lower()
                    if word_lower not in synonyms_dict:
                        synonyms_dict[word_lower] = []
                    for other_word in words:
                        if other_word.lower() != word_lower:
                            if other_word.lower() not in synonyms_dict[word_lower]:
                                synonyms_dict[word_lower].append(other_word.lower())
    
    return synonyms_dict

