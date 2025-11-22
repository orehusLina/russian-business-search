"""
Скрипт для принудительного сохранения текущих статей
Используйте если скрапер работает и нужно сохранить уже собранные данные
"""

import logging
from scraper import RBScraper
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Если у вас уже есть скрапер с данными, можно сохранить их так:
# Но проще всего - дождаться завершения раздела или использовать Ctrl+C и сохранить

# Альтернатива: если скрапер работает в другом процессе,
# можно прочитать логи и понять, сколько статей собрано

logger.info("Для сохранения текущих данных:")
logger.info("1. Если скрапер еще работает - дождитесь завершения раздела (сохранение происходит автоматически)")
logger.info("2. Или прервите скрапер (Ctrl+C) и он сохранит данные при завершении")
logger.info("3. Или используйте этот скрипт, если у вас есть доступ к объекту scraper")

# Если у вас есть доступ к scraper объекту:
# scraper = RBScraper()
# scraper.articles = [...]  # Ваши статьи
# scraper.save_to_json('rb_articles_current.json')
# scraper.save_to_csv('rb_articles_current.csv')

