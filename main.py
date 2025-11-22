"""
Точка входа для скрапера rb.ru
"""

import logging
from scraper import RBScraper

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


def main():
    """Основная функция"""
    # Максимальная параллельность для скорости
    scraper = RBScraper(max_workers=20, delay=0.3)  # 20 потоков, задержка 0.3 сек
    
    # Скрапинг всех разделов с разным количеством страниц
    # Цель: собрать 5-20к документов пропорционально объему каждого раздела
    # 
    # Всего материалов на сайте: ~61,530
    # - новости: 43,773 (71%)
    # - истории: 9,060 (15%)
    # - мнения: 8,642 (14%)
    # - остальные: 55 (<1%)
    #
    # Для 15к документов (середина диапазона):
    # - новости: ~10,500 статей = ~2,100 страниц
    # - истории: ~2,200 статей = ~440 страниц
    # - мнения: ~2,100 статей = ~420 страниц
    # - остальные: все (~55 статей)
    
    pages_config = {
        'news': 2100,         # Новости: ~10,500 статей (43,773 всего, берем ~24%)
        'stories': 440,        # Истории: ~2,200 статей (9,060 всего, берем ~24%)
        'opinions': 420,       # Мнения: ~2,100 статей (8,642 всего, берем ~24%)
        'neuroprofiles': 2,    # Нейропрофайлы: все 7 материалов (2 страницы)
        'reviews': 9,          # Обзоры: все 43 материала (9 страниц)
        'checklists': 1        # Чек-листы: все 5 материалов (1 страница)
    }
    
    # Итого: ~15,000 статей (в пределах целевого диапазона 5-20к)
    # save_milestones=True - сохраняет после каждого раздела
    # milestone_interval=100 - сохранять каждые 100 статей
    articles = scraper.scrape_all(
        max_pages_per_section=50, 
        pages_config=pages_config,
        save_milestones=True,  # Сохранять после каждого раздела
        milestone_interval=100  # И дополнительно каждые 100 статей
    )
    
    logger.info(f"Всего скраплено статей: {len(articles)}")
    
    # Финальное сохранение данных
    # Можно сохранить только в один формат, если нужно:
    scraper.save_to_json('rb_articles.json')  # Для программной обработки
    scraper.save_to_csv('rb_articles.csv')    # Для Excel/pandas анализа
    
    # Или только JSON (быстрее):
    # scraper.save_to_json('rb_articles.json')
    
    # Или только CSV:
    # scraper.save_to_csv('rb_articles.csv')
    
    logger.info("Скрапинг завершен!")


if __name__ == '__main__':
    main()

