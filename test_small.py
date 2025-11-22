"""
Тестовый скрипт для проверки скрапера на небольшом количестве страниц
Использует модульную структуру
"""

import logging
from scraper import RBScraper
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_small_scrape():
    """Тест скрапера на большем количестве страниц"""
    scraper = RBScraper(max_workers=5, delay=1.0)
    
    print("Тестирую скрапинг раздела 'news' на 10 страницах...")
    articles = scraper.scrape_section('news', max_pages=10)
    
    # Сохраняем статьи в скрапер для методов save_to_*
    scraper.articles = articles
    
    print(f"\nСкраплено статей: {len(articles)}")
    
    if articles:
        # Статистика
        articles_with_companies = sum(1 for a in articles if a.get('companies'))
        articles_with_money = sum(1 for a in articles if a.get('money'))
        all_companies = []
        for article in articles:
            all_companies.extend(article.get('companies', []))
        
        print(f"\nСтатистика:")
        print(f"  Статей с компаниями: {articles_with_companies} ({articles_with_companies/len(articles)*100:.1f}%)")
        print(f"  Статей с деньгами: {articles_with_money} ({articles_with_money/len(articles)*100:.1f}%)")
        print(f"  Всего найдено компаний: {len(set(all_companies))}")
        if all_companies:
            from collections import Counter
            top_companies = Counter(all_companies).most_common(5)
            print(f"  Топ-5 компаний: {', '.join([f'{c[0]} ({c[1]})' for c in top_companies])}")
        
        print("\nПримеры скрапленных статей:")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('title', 'Без заголовка')}")
            print(f"   URL: {article.get('url', '')}")
            print(f"   Тип: {article.get('content_type', 'unknown')}")
            print(f"   Автор: {article.get('author', 'Не указан')}")
            print(f"   Дата: {article.get('date', 'Не указана')}")
            companies = article.get('companies', [])
            money = article.get('money', [])
            print(f"   Компании: {', '.join(companies[:5]) if companies else 'Не найдено'}")
            if money:
                money_str = ', '.join([f"{m.get('amount', '')} {m.get('multiplier', '')} {m.get('currency', '')}" for m in money[:3]])
                print(f"   Деньги: {money_str}")
            else:
                print(f"   Деньги: Не найдено")
        
        # Сохраняем результаты
        scraper.save_to_json('test_articles.json')
        scraper.save_to_csv('test_articles.csv')
        print(f"\nРезультаты сохранены в test_articles.json и test_articles.csv")
    else:
        print("Не удалось скрапить статьи. Проверьте подключение к интернету и структуру сайта.")

if __name__ == '__main__':
    test_small_scrape()

