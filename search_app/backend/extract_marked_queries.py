import csv
from pathlib import Path
from collections import defaultdict

CSV_FILE = Path(__file__).parent / "serp_results.csv"
OUTPUT_FILE = Path(__file__).parent / "serp_results_marked.csv"


def extract_marked_queries():
    query_results = defaultdict(list)
    marked_queries = set()
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row['Запрос']
            relevance_0_1 = row.get('Релевантность (0/1)', '').strip()
            relevance_1_3 = row.get('Релевантность (1-3)', '').strip()
            
            if relevance_0_1 or relevance_1_3:
                marked_queries.add(query)
                query_results[query].append(row)
    
    if not marked_queries:
        print("Нет размеченных запросов!")
        return
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Запрос', 'Ранг', 'Название документа', 'Описание', 
                     'Релевантность (1-3)', 'Релевантность (0/1)']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for query in sorted(marked_queries):
            for row in query_results[query]:
                writer.writerow({
                    'Запрос': row['Запрос'],
                    'Ранг': row['Ранг'],
                    'Название документа': row['Название документа'],
                    'Описание': row['Описание'],
                    'Релевантность (1-3)': row.get('Релевантность (1-3)', ''),
                    'Релевантность (0/1)': row.get('Релевантность (0/1)', '')
                })
    
    print(f"Извлечено {len(marked_queries)} размеченных запросов")
    print(f"Результаты сохранены в: {OUTPUT_FILE}")
    print(f"\nРазмеченные запросы:")
    for q in sorted(marked_queries):
        print(f"  - {q}")


if __name__ == "__main__":
    extract_marked_queries()


