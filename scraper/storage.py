import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class DataStorage:  
    @staticmethod
    def save_to_json(articles: List[Dict], filename: str = 'rb_articles.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"Данные сохранены в {filename}")
    
    @staticmethod
    def save_to_csv(articles: List[Dict], filename: str = 'rb_articles.csv'):
        if not articles:
            logger.warning("Нет данных для сохранения")
            return
        
        try:
            import pandas as pd
        except ImportError:
            logger.error("Для сохранения в CSV требуется библиотека pandas")
            return
        
        csv_data = []
        for article in articles:
            row = {
                'url': article.get('url', ''),
                'title': article.get('title', ''),
                'content_type': article.get('content_type', ''),
                'author': article.get('author', ''),
                'date': article.get('date', ''),
                'tags': '; '.join(article.get('tags', [])),
                'categories': '; '.join(article.get('categories', [])),
                'text': article.get('text', '')[:1000],  # Ограничиваем длину текста
                'description': article.get('description', ''),
                'companies': '; '.join(article.get('companies', [])),
                'people': '; '.join(article.get('people', [])),
                'money': '; '.join([f"{m.get('amount', '')} {m.get('multiplier', '')} {m.get('currency', '')}" for m in article.get('money', [])]),
                'scraped_at': article.get('scraped_at', '')
            }
            csv_data.append(row)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"Данные сохранены в {filename}")

