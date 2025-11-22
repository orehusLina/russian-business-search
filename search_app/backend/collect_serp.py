import json
import csv
import os
import requests
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

API_URL = os.getenv("SEARCH_API_URL", "http://localhost:8000")
QUERIES_FILE = Path(__file__).parent / "search_queries.txt"
OUTPUT_JSON_FILE = Path(__file__).parent / "serp_results.json"
OUTPUT_CSV_FILE = Path(__file__).parent / "serp_results.csv"


def parse_queries_file(file_path: Path) -> List[str]:
    queries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                queries.append(line)
    return queries


def search_query(query: str, size: int = 20) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={"query": query, "size": size, "from": 0},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе '{query}': {e}")
        return {"results": [], "total": 0, "error": str(e)}


def format_serp_result(query: str, search_response: Dict[str, Any]) -> Dict[str, Any]:
    serp = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "total_results": search_response.get("total", 0),
        "results": []
    }
    
    articles = search_response.get("results", [])
    for idx, article in enumerate(articles, start=1):
        result = {
            "query": query,
            "rank": idx,
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "description": article.get("description", ""),
            "author": article.get("author", ""),
            "date": article.get("date", ""),
            "companies": article.get("companies", []),
            "people": article.get("people", []),
            "tags": article.get("tags", []),
            "relevance_1_3": None,
            "relevance_0_1": None
        }
        serp["results"].append(result)
    
    return serp


def collect_serp(queries: List[str]) -> List[Dict[str, Any]]:
    all_serp = []
    
    print(f"Начинаю сбор SERP для {len(queries)} запросов...")
    print(f"API URL: {API_URL}\n")
    
    for idx, query in enumerate(queries, start=1):
        print(f"[{idx}/{len(queries)}] Запрос: '{query}'")
        search_response = search_query(query)
        serp_result = format_serp_result(query, search_response)
        all_serp.append(serp_result)
        
        total = serp_result["total_results"]
        print(f"  Найдено результатов: {total}")
        if total > 0:
            print(f"  Первый результат: {serp_result['results'][0]['title'][:60]}...")
        print()
    
    return all_serp


def main():
    if not QUERIES_FILE.exists():
        print(f"Файл с запросами не найден: {QUERIES_FILE}")
        return
    
    queries = parse_queries_file(QUERIES_FILE)
    if not queries:
        print("Не найдено запросов в файле")
        return
    
    print(f"Загружено {len(queries)} запросов из {QUERIES_FILE}\n")
    
    all_serp = collect_serp(queries)
    
    output_data = {
        "collection_date": datetime.now().isoformat(),
        "total_queries": len(queries),
        "api_url": API_URL,
        "serp_results": all_serp
    }
    
    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    with open(OUTPUT_CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Запрос",
            "Ранг",
            "Название документа",
            "Описание",
            "Релевантность (1-3)",
            "Релевантность (0/1)"
        ])
        
        for serp in all_serp:
            for result in serp["results"]:
                writer.writerow([
                    result["query"],
                    result["rank"],
                    result["title"],
                    result["description"],
                    result["relevance_1_3"] if result["relevance_1_3"] is not None else "",
                    result["relevance_0_1"] if result["relevance_0_1"] is not None else ""
                ])
    
    print(f"\n✓ SERP результаты сохранены:")
    print(f"  JSON: {OUTPUT_JSON_FILE}")
    print(f"  CSV:  {OUTPUT_CSV_FILE}")
    print(f"  Всего запросов: {len(queries)}")
    print(f"  Всего результатов: {sum(len(s['results']) for s in all_serp)}")


if __name__ == "__main__":
    main()

