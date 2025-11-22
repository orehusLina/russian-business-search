"""Скрипт для индексации данных в Elasticsearch"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from tqdm import tqdm
from load_synonyms_for_index import get_synonyms_list

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ES_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
ES_USE_SSL = os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true"
ES_VERIFY_CERTS = os.getenv("ELASTICSEARCH_VERIFY_CERTS", "false").lower() == "true"
ES_INDEX = "rb_articles"
DATA_FILE = Path(__file__).parent.parent.parent / "rb_articles.json"


def preprocess_article(article: Dict[str, Any]) -> Dict[str, Any]:
    processed = article.copy()
    
    if "date" in processed:
        date_str = processed.get("date", "")
        if not date_str or not isinstance(date_str, str):
            processed.pop("date", None)
    
    if "money" in processed and isinstance(processed["money"], list):
        normalized_money = []
        for money_item in processed["money"]:
            if isinstance(money_item, dict) and "amount" in money_item:
                try:
                    money_item["amount"] = float(money_item["amount"])
                    normalized_money.append(money_item)
                except (ValueError, TypeError):
                    continue
        processed["money"] = normalized_money
    
    for field in ["tags", "companies", "people", "categories"]:
        if field in processed:
            if not isinstance(processed[field], list):
                processed[field] = [processed[field]] if processed[field] else []
            processed[field] = [item for item in processed[field] if item and str(item).strip()]
    
    for field in ["title", "text", "description", "author"]:
        if field in processed and processed[field]:
            processed[field] = str(processed[field]).strip()
            if not processed[field]:
                processed[field] = ""
    
    if "scraped_at" not in processed or not processed["scraped_at"]:
        processed["scraped_at"] = datetime.now().isoformat()
    
    return processed


def create_index(es: Elasticsearch, index_name: str):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    
    mapping = {
        "mappings": {
            "properties": {
                "url": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "russian",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "content_type": {"type": "keyword"},
                "author": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "date": {"type": "text"},
                "tags": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "categories": {"type": "keyword"},
                "text": {"type": "text", "analyzer": "russian"},
                "description": {"type": "text", "analyzer": "russian"},
                "companies": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "people": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "money": {
                    "type": "nested",
                    "properties": {
                        "amount": {"type": "float"},
                        "multiplier": {"type": "keyword"},
                        "currency": {"type": "keyword"},
                        "original": {"type": "text"}
                    }
                },
                "scraped_at": {"type": "date"}
            }
        },
        "settings": {
            "number_of_replicas": 0,
            "number_of_shards": 1,
            "refresh_interval": "30s",
            "index": {
                "max_result_window": 50000,
                "translog": {
                    "durability": "async",
                    "sync_interval": "5s"
                }
            },
            "analysis": {
                "analyzer": {
                    "russian": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "russian_synonyms", "russian_stop", "russian_stemmer"]
                    }
                },
                "filter": {
                    "russian_stop": {
                        "type": "stop",
                        "stopwords": "_russian_"
                    },
                    "russian_synonyms": {
                        "type": "synonym",
                        "synonyms": get_synonyms_list()
                    },
                    "russian_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                }
            }
        }
    }
    
    es.options(request_timeout=120).indices.create(index=index_name, body=mapping)
    time.sleep(2)


def index_articles(es: Elasticsearch, index_name: str, data_file: Path):
    with open(data_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    def generate_actions():
        for article in articles:
            processed = preprocess_article(article)
            doc_id = processed.get("url", "").replace("/", "_").replace(":", "_")
            if not doc_id:
                doc_id = f"article_{hash(str(processed))}"
            yield {
                "_index": index_name,
                "_id": doc_id,
                "_source": processed
            }
    
    es_with_timeout = es.options(request_timeout=180)
    success_count = 0
    
    with tqdm(total=len(articles), unit="статей", desc="Индексация") as pbar:
        for ok, response in streaming_bulk(
            es_with_timeout,
            generate_actions(),
            chunk_size=200,
            raise_on_error=False,
            max_retries=2
        ):
            if ok:
                success_count += 1
            pbar.update(1)
    
    es.indices.put_settings(
        index=index_name,
        body={"refresh_interval": "1s"}
    )
    es.indices.refresh(index=index_name)


def main():
    es = Elasticsearch([{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}], request_timeout=60)
    
    if not DATA_FILE.exists():
        return
    
    create_index(es, ES_INDEX)
    index_articles(es, ES_INDEX, DATA_FILE)


if __name__ == "__main__":
    main()
