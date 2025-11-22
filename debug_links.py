"""
Скрипт для диагностики извлечения ссылок
"""

import logging
from scraper import RBScraper

# Настройка логирования (DEBUG уровень для детальной диагностики)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

scraper = RBScraper(max_workers=1, delay=1.0)

print("Проверяю главную страницу раздела news...")
urls = scraper.get_article_urls_from_listing('news', max_pages=3)

print(f"\nВсего найдено уникальных URL: {len(urls)}")
print("\nПервые 20 URL:")
for i, url in enumerate(urls[:20], 1):
    print(f"{i}. {url}")

