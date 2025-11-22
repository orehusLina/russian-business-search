import csv
import math
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

CSV_FILE = Path(__file__).parent / "serp_results_marked.csv"
OUTPUT_CSV = Path(__file__).parent / "search_metrics.csv"


def calculate_precision_at_k(relevances: List[int], k: int) -> float:
    if len(relevances) < k:
        k = len(relevances)
    if k == 0:
        return 0.0
    relevant_count = sum(1 for r in relevances[:k] if r > 0)
    return relevant_count / k


def calculate_average_precision(relevances: List[int]) -> float:
    if not relevances:
        return 0.0
    
    relevant_positions = [i + 1 for i, r in enumerate(relevances) if r > 0]
    if not relevant_positions:
        return 0.0
    
    precisions = []
    for pos in relevant_positions:
        precision_at_pos = calculate_precision_at_k(relevances, pos)
        precisions.append(precision_at_pos)
    
    return sum(precisions) / len(precisions) if precisions else 0.0


def calculate_dcg(relevances: List[int], k: int) -> float:
    if len(relevances) < k:
        k = len(relevances)
    dcg = 0.0
    for i in range(k):
        if i < len(relevances):
            relevance = relevances[i]
            if relevance > 0:
                dcg += relevance / math.log2(i + 2)
    return dcg


def calculate_ndcg_at_k(relevances: List[int], k: int) -> float:
    dcg = calculate_dcg(relevances, k)
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = calculate_dcg(ideal_relevances, k)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def load_data_from_csv() -> Dict[str, List[Tuple[int, int]]]:
    query_results = defaultdict(list)
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row['Запрос']
            relevance_0_1 = row.get('Релевантность (0/1)', '').strip()
            relevance_1_3 = row.get('Релевантность (1-3)', '').strip()
            
            rel_binary = 1 if relevance_0_1 == '1' else 0
            rel_graded = int(relevance_1_3) if relevance_1_3 and relevance_1_3.isdigit() else 0
            
            query_results[query].append((rel_binary, rel_graded))
    
    return query_results


def calculate_metrics_for_query(relevances_binary: List[int], relevances_graded: List[int]) -> Dict[str, float]:
    precision_5 = calculate_precision_at_k(relevances_binary, 5)
    precision_10 = calculate_precision_at_k(relevances_binary, 10)
    avg_precision = calculate_average_precision(relevances_binary)
    ndcg_5 = calculate_ndcg_at_k(relevances_graded, 5)
    
    return {
        'Precision@5': precision_5,
        'Precision@10': precision_10,
        'Average Precision': avg_precision,
        'NDCG@5': ndcg_5
    }


def main():
    query_results = load_data_from_csv()
    metrics_data = []
    
    for query in sorted(query_results.keys()):
        results = query_results[query]
        relevances_binary = [r[0] for r in results]
        relevances_graded = [r[1] for r in results]
        
        metrics = calculate_metrics_for_query(relevances_binary, relevances_graded)
        metrics_data.append({
            'query': query,
            **metrics
        })
    
    print("\n" + "="*120)
    print(f"{'':<4} {'Запрос':<50} {'Precision@5':<15} {'Precision@10':<15} {'Average Precision':<20} {'NDCG@5':<15}")
    print("="*120)
    
    for i, data in enumerate(metrics_data):
        query = data['query'][:48] + '..' if len(data['query']) > 50 else data['query']
        p5 = f"{data['Precision@5']:.1f}"
        p10 = f"{data['Precision@10']:.1f}"
        ap = f"{data['Average Precision']:.6f}"
        ndcg = f"{data['NDCG@5']:.6f}"
        print(f"{i:<4} {query:<50} {p5:<15} {p10:<15} {ap:<20} {ndcg:<15}")
    
    mean_ap = sum(m['Average Precision'] for m in metrics_data) / len(metrics_data) if metrics_data else 0.0
    mean_ndcg = sum(m['NDCG@5'] for m in metrics_data) / len(metrics_data) if metrics_data else 0.0
    
    print("="*110)
    print(f"Mean Average Precision (MAP) по всем запросам: {mean_ap:.3f}")
    print(f"Mean NDCG@5 по всем запросам: {mean_ndcg:.3f}")
    print("="*110 + "\n")
    
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Запрос', 'Precision@5', 'Precision@10', 'Average Precision', 'NDCG@5'])
        writer.writeheader()
        for data in metrics_data:
            writer.writerow({
                'Запрос': data['query'],
                'Precision@5': f"{data['Precision@5']:.6f}",
                'Precision@10': f"{data['Precision@10']:.6f}",
                'Average Precision': f"{data['Average Precision']:.6f}",
                'NDCG@5': f"{data['NDCG@5']:.6f}"
            })
    
    print(f"Метрики сохранены в файл: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

