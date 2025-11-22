"""
FastAPI бэкенд для поискового приложения
Подключается к Elasticsearch и предоставляет REST API для поиска
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError

app = FastAPI(title="RB.RU Search API", version="1.0.0")

# CORS для Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к Elasticsearch
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ES_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
ES_USE_SSL = os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true"
ES_VERIFY_CERTS = os.getenv("ELASTICSEARCH_VERIFY_CERTS", "false").lower() == "true"
ES_INDEX = "rb_articles"

try:
    if ES_USE_SSL:
        protocol = "https"
        es_config = {
            "hosts": [f"{protocol}://{ES_HOST}:{ES_PORT}"],
            "request_timeout": 60,
            "max_retries": 3,
            "retry_on_timeout": True
        }
        if not ES_VERIFY_CERTS:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            es_config["verify_certs"] = False
            es_config["ssl_show_warn"] = False
        es = Elasticsearch(**es_config)
    else:
        es = Elasticsearch([{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}], request_timeout=60)
    
except Exception as e:
    es = None


class SearchRequest(BaseModel):
    query: str
    size: int = 20
    from_: int = 0
    content_type: Optional[str] = None
    company: Optional[str] = None
    tag: Optional[str] = None


class SearchResponse(BaseModel):
    total: int
    results: List[Dict[str, Any]]
    took: int


@app.get("/")
async def root():
    return {
        "message": "RB.RU Search API",
        "version": "1.0.0",
        "elasticsearch": "connected" if es and es.ping() else "disconnected"
    }


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    if not es:
        return {"status": "error", "message": "Elasticsearch не подключен"}
    
    try:
        es.ping()
        return {"status": "ok", "elasticsearch": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Поиск статей по запросу
    
    Args:
        request: Параметры поиска
        
    Returns:
        Результаты поиска
    """
    if not es:
        raise HTTPException(status_code=503, detail="Elasticsearch не подключен")
    
    try:
        # Формируем запрос к Elasticsearch
        query_body = {
            "size": request.size,
            "from": request.from_,
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "text": {},
                    "description": {}
                }
            }
        }
        
        # Основной поисковый запрос
        # КРИТИЧЕСКИ ВАЖНО: multi_match автоматически использует analyzer полей
        # Это обеспечивает согласованность предобработки запросов и индексации
        # Запрос проходит через тот же "russian" analyzer (lowercase, стоп-слова, стемминг)
        if request.query:
            query_body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": request.query,
                    "fields": ["title^3", "text^2", "description^1.5", "companies^2", "people^1.5"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"  # Дополнительная защита от опечаток
                }
            })
        else:
            query_body["query"]["bool"]["must"].append({"match_all": {}})
        
        # Фильтры (используем .keyword поля для точного совпадения)
        if request.content_type:
            query_body["query"]["bool"]["filter"].append({
                "term": {"content_type": request.content_type}
            })
        
        if request.company:
            # Используем .keyword для точного совпадения компании
            query_body["query"]["bool"]["filter"].append({
                "term": {"companies.keyword": request.company}
            })
        
        if request.tag:
            # Используем .keyword для точного совпадения тега
            query_body["query"]["bool"]["filter"].append({
                "term": {"tags.keyword": request.tag}
            })
        
        response = es.search(index=ES_INDEX, body=query_body)
        
        # Форматируем результаты
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            result = {
                "id": hit["_id"],
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "content_type": source.get("content_type", ""),
                "author": source.get("author", ""),
                "date": source.get("date", ""),
                "description": source.get("description", ""),
                "tags": source.get("tags", []),
                "companies": source.get("companies", []),
                "people": source.get("people", []),
                "money": source.get("money", []),
                "score": hit["_score"],
                "highlight": hit.get("highlight", {})
            }
            results.append(result)
        
        return SearchResponse(
            total=response["hits"]["total"]["value"],
            results=results,
            took=response["took"]
        )
    
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Индекс не найден. Запустите индексацию данных.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@app.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., description="Поисковый запрос"),
    size: int = Query(20, ge=1, le=100, description="Количество результатов"),
    from_: int = Query(0, ge=0, description="Смещение"),
    content_type: Optional[str] = Query(None, description="Фильтр по типу контента"),
    company: Optional[str] = Query(None, description="Фильтр по компании"),
    tag: Optional[str] = Query(None, description="Фильтр по тегу")
):
    """GET версия поиска"""
    request = SearchRequest(
        query=q,
        size=size,
        from_=from_,
        content_type=content_type,
        company=company,
        tag=tag
    )
    return await search(request)


@app.get("/stats")
async def get_stats():
    """Получить статистику по индексу"""
    if not es:
        raise HTTPException(status_code=503, detail="Elasticsearch не подключен")
    
    try:
        stats = es.count(index=ES_INDEX)
        
        # Агрегации по типам контента
        agg_query = {
            "size": 0,
            "aggs": {
                "content_types": {
                    "terms": {"field": "content_type", "size": 20}
                },
                "top_companies": {
                    "terms": {"field": "companies.keyword", "size": 10}
                },
                "top_tags": {
                    "terms": {"field": "tags.keyword", "size": 10}
                }
            }
        }
        
        aggs = es.search(index=ES_INDEX, body=agg_query)
        
        return {
            "total_articles": stats["count"],
            "content_types": {bucket["key"]: bucket["doc_count"] 
                            for bucket in aggs["aggregations"]["content_types"]["buckets"]},
            "top_companies": [{"name": bucket["key"], "count": bucket["doc_count"]}
                            for bucket in aggs["aggregations"]["top_companies"]["buckets"]],
            "top_tags": [{"name": bucket["key"], "count": bucket["doc_count"]}
                        for bucket in aggs["aggregations"]["top_tags"]["buckets"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

