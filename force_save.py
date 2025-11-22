"""
Скрипт для принудительного сохранения текущих статей
Запустите этот скрипт, если скрапер работает и нужно сохранить уже собранные данные
"""

import logging
import json
from scraper import RBScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("ВНИМАНИЕ: Этот скрипт работает только если скрапер еще не завершился")
logger.info("Если скрапер работает в другом процессе, данные недоступны")
logger.info("")
logger.info("Варианты решения:")
logger.info("1. Дождитесь завершения текущего раздела - сохранение произойдет автоматически")
logger.info("2. Прервите скрапер (Ctrl+C) - он сохранит данные при завершении")
logger.info("3. Проверьте логи scraper.log - там видно, когда происходит сохранение")
logger.info("")
logger.info("Если у вас есть доступ к объекту scraper с данными:")
logger.info("  scraper = RBScraper()")
logger.info("  scraper.articles = [...]  # Ваши 1310 статей")
logger.info("  scraper.save_to_json('rb_articles_current.json')")
logger.info("  scraper.save_to_csv('rb_articles_current.csv')")

