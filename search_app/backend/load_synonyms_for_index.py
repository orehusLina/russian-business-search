"""Загрузка синонимов для индексации"""
from pathlib import Path

SYNONYMS_FILE = Path(__file__).parent / "synonyms.txt"

def get_synonyms_list():
    """Возвращает список синонимов в формате для Elasticsearch"""
    synonyms_list = []
    
    with open(SYNONYMS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            words = [w.strip() for w in line.split(',') if w.strip()]
            if len(words) > 1:
                synonyms_list.append(', '.join(words))
    
    return synonyms_list

