from pathlib import Path

SYNONYMS_FILE = Path(__file__).parent / "synonyms.txt"

def get_synonyms_list():
    synonyms_list = []
    
    with open(SYNONYMS_FILE, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                words = [w.strip() for w in line.split(',') if w.strip()]
                words = [w for w in words if w and len(w) > 0]
                
                if len(words) > 1:
                    cleaned_words = []
                    seen_words = set()
                    
                    for word in words:
                        word_clean = word.replace('$', 'USD').replace('€', 'EUR').replace('₽', 'RUB')
                        word_clean = word_clean.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
                        word_clean = word_clean.replace('"', '').replace("'", '')
                        word_clean = ' '.join(word_clean.split())
                        word_clean = word_clean.strip()
                        
                        if word_clean and len(word_clean) > 0 and len(word_clean) < 80:
                            if not any(c in word_clean for c in ['\n', '\r', '\t', '=>']):
                                word_lower = word_clean.lower()
                                if word_lower not in seen_words:
                                    seen_words.add(word_lower)
                                    cleaned_words.append(word_clean)
                    
                    if len(cleaned_words) > 1:
                        formatted_words = []
                        for word in cleaned_words:
                            if ' ' in word:
                                formatted_words.append(f'"{word}"')
                            else:
                                formatted_words.append(word)
                        
                        synonym_line = ', '.join(formatted_words)
                        if len(synonym_line) < 500 and '\n' not in synonym_line and '\r' not in synonym_line:
                            synonyms_list.append(synonym_line)
            except Exception:
                continue
    
    return synonyms_list

