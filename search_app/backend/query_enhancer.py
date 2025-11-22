import re
from typing import Dict, List, Tuple


def analyze_query(query: str) -> Dict:
    words = query.split()
    query_lower = query.lower()
    
    return {
        "word_count": len(words),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "has_numbers": bool(re.search(r'\d', query)),
        "has_special_terms": bool(re.search(r'\b(состояние|выручка|прибыль|инвестиции|ipo)\b', query_lower)),
        "is_single_word": len(words) == 1,
        "is_short": len(words) <= 2,
        "is_long": len(words) >= 4
    }


def determine_fuzziness(query: str, analysis: Dict) -> str:
    if analysis["is_single_word"]:
        if len(query) > 5:
            return "AUTO"
        else:
            return "1"
    elif analysis["is_short"]:
        return "1"
    else:
        return "0"


def build_search_query(query: str, analysis: Dict) -> Dict:
    fuzziness = determine_fuzziness(query, analysis)
    must_queries = []
    should_queries = []
    
    must_queries.append({
        "multi_match": {
            "query": query,
            "fields": ["title^3", "text^2", "description^1.5", "companies^2", "people^1.5"],
            "type": "best_fields"
        }
    })
    
    if analysis["word_count"] > 0:
        words = query.split()
        fuzzy_terms = [w for w in words if len(w) > 3]
        
        if fuzzy_terms and fuzziness != "0":
            should_queries.append({
                "multi_match": {
                    "query": " ".join(fuzzy_terms),
                    "fields": ["title^2", "text^1.5", "description^1"],
                    "type": "best_fields",
                    "fuzziness": fuzziness,
                    "prefix_length": 2
                }
            })
    
    if analysis["word_count"] >= 2:
        should_queries.append({
            "match_phrase": {
                "text": {
                    "query": query,
                    "slop": 2,
                    "boost": 0.5
                }
            }
        })
    
    query_body = {
        "bool": {
            "must": must_queries
        }
    }
    
    if should_queries:
        query_body["bool"]["should"] = should_queries
        query_body["bool"]["minimum_should_match"] = 0
    
    return query_body

