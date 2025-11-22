"""
Основной класс скрапера
"""

import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .config import BASE_URL, SECTIONS, DEFAULT_MAX_WORKERS, DEFAULT_DELAY
from .http_client import HTTPClient
from .parsers import HTMLParser
from .storage import DataStorage

logger = logging.getLogger(__name__)


class RBScraper:
    def __init__(self, max_workers: int = DEFAULT_MAX_WORKERS, delay: float = DEFAULT_DELAY):
        self.http_client = HTTPClient(delay=delay)
        self.parser = HTMLParser()
        self.storage = DataStorage()
        self.max_workers = max_workers
        self.scraped_urls = set()
        self.articles = []
    
    def get_article_urls_from_listing(self, section: str, max_pages: int = 50) -> List[str]:
        urls = []
        section_path = SECTIONS.get(section, '/')
        
        # Сначала пробуем главную страницу раздела
        section_url = f"{BASE_URL}{section_path}" if section_path != '/' else BASE_URL
        soup = self.http_client.fetch_page(section_url)
        if soup:
            article_links = self.parser.extract_article_links(soup)
            urls.extend(article_links)
            logger.info(f"Найдено {len(article_links)} статей на главной странице раздела {section}")
        
        # Затем скрапим страницы пагинации
        # Правильный формат: https://rb.ru/news/?page=2
        for page in range(2, max_pages + 1):
            if section_path == '/':
                url = f"{BASE_URL}/?page={page}"
            else:
                url = f"{BASE_URL}{section_path}?page={page}"
            
            logger.info(f"Загружаю страницу {page}: {url}")
            soup = self.http_client.fetch_page(url)
            if not soup:
                logger.warning(f"Не удалось загрузить страницу {page}, прекращаю пагинацию")
                break
            
            page_urls = self.parser.extract_article_links(soup)
            
            if not page_urls:
                logger.info(f"Не найдено статей на странице {page} раздела {section}, прекращаю пагинацию")
                break
            
            # Проверяем, что это новые статьи (не дубликаты)
            new_urls = [u for u in page_urls if u not in urls]
            if not new_urls:
                logger.warning(f"Все статьи на странице {page} уже были найдены ранее, прекращаю пагинацию")
                break
            
            urls.extend(new_urls)
            logger.info(f"Найдено {len(new_urls)} новых статей на странице {page} (всего уникальных: {len(set(urls))})")
        
        return list(set(urls))
    
    def parse_article_page(self, url: str) -> Dict:
        if url in self.scraped_urls:
            return None
        
        soup = self.http_client.fetch_page(url)
        if not soup:
            return None
        
        self.scraped_urls.add(url)
        return self.parser.parse_article(url, soup)
    
    def scrape_section(self, section: str, max_pages: int = 50, save_milestone: bool = False,
                       milestone_interval: int = None, total_before_section: int = 0) -> List[Dict]:
        logger.info(f"Начинаю скрапинг раздела: {section}")
        logger.info(f"[MILESTONE DEBUG] Параметры функции: milestone_interval={milestone_interval} (type: {type(milestone_interval)}), total_before_section={total_before_section}")
        urls = self.get_article_urls_from_listing(section, max_pages)
        logger.info(f"Найдено {len(urls)} URL для скрапинга в разделе {section}")
        if milestone_interval:
            logger.info(f"[MILESTONE] Milestone сохранение включено: каждые {milestone_interval} статей (уже собрано: {total_before_section})")
        else:
            logger.warning(f"[MILESTONE] Milestone сохранение ОТКЛЮЧЕНО! milestone_interval={milestone_interval}")
        
        articles = []
        last_saved_count = 0
        
        logger.info(f"[MILESTONE] Начало скрапинга раздела {section}: milestone_interval={milestone_interval}, total_before_section={total_before_section}")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.parse_article_page, url): url for url in urls}
            
            with tqdm(total=len(urls), desc=f"Скрапинг {section}") as pbar:
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        article = future.result()
                        if article:
                            articles.append(article)
                            pbar.update(1)
                            
                            # каждые N статей
                            if milestone_interval and milestone_interval > 0:
                                total_articles = total_before_section + len(articles)
                                
                                # логируем каждые 10 статей для отладки
                                if len(articles) % 10 == 0:
                                    logger.info(f"[PROGRESS] Статей в разделе: {len(articles)}, всего: {total_articles}, last_saved: {last_saved_count}")
                                
                                # просто проверяем разницу
                                if total_articles >= milestone_interval:
                                    # Вычисляем сколько статей прошло с последнего сохранения
                                    articles_since_last_save = total_articles - last_saved_count
                                    
                                    # Логируем при приближении к milestone
                                    if total_articles % 25 == 0 or articles_since_last_save >= milestone_interval - 5:
                                        logger.info(f"[CHECK] total={total_articles}, last_saved={last_saved_count}, разница={articles_since_last_save}, нужно_сохранить={articles_since_last_save >= milestone_interval}")
                                    
                                    # Сохраняем если прошло >= milestone_interval статей с последнего сохранения
                                    if articles_since_last_save >= milestone_interval:
                                        logger.info(f"[MILESTONE] СОХРАНЯЮ: {total_articles} статей (было сохранено: {last_saved_count}, разница: {articles_since_last_save})")
                                        
                                        # Сохраняем все накопленные статьи
                                        temp_articles = list(self.articles) + articles
                                        logger.info(f"[MILESTONE] Всего статей для сохранения: {len(temp_articles)} (предыдущие: {len(self.articles)}, текущие: {len(articles)})")
                                        
                                        original_articles = self.articles
                                        self.articles = temp_articles
                                        
                                        try:
                                            logger.info(f"[MILESTONE] Записываю в файлы...")
                                            self.save_to_json('rb_articles_milestone.json')
                                            logger.info(f"[MILESTONE] JSON сохранен!")
                                            self.save_to_csv('rb_articles_milestone.csv')
                                            logger.info(f"[MILESTONE] CSV сохранен!")
                                            logger.info(f"[MILESTONE] УСПЕШНО СОХРАНЕНО {len(temp_articles)} СТАТЕЙ!")
                                        except Exception as e:
                                            logger.error(f"[MILESTONE] ОШИБКА: {e}", exc_info=True)
                                        finally:
                                            self.articles = original_articles
                                        
                                        # Обновляем last_saved_count на текущее количество
                                        last_saved_count = total_articles
                                        logger.info(f"[MILESTONE] Обновлен last_saved_count = {last_saved_count}")
                    except Exception as e:
                        logger.error(f"Ошибка при обработке {url}: {e}")
                        pbar.update(1)
            
            # ФИНАЛЬНАЯ ПРОВЕРКА: сохраняем если пропустили milestone
            if milestone_interval and milestone_interval > 0:
                total_articles = total_before_section + len(articles)
                if total_articles >= milestone_interval:
                    articles_since_last_save = total_articles - last_saved_count
                    if articles_since_last_save >= milestone_interval:
                        logger.info(f"[MILESTONE FINAL] ФИНАЛЬНОЕ СОХРАНЕНИЕ: {total_articles} статей (разница: {articles_since_last_save})")
                        temp_articles = list(self.articles) + articles
                        original_articles = self.articles
                        self.articles = temp_articles
                        try:
                            self.save_to_json('rb_articles_milestone.json')
                            self.save_to_csv('rb_articles_milestone.csv')
                            logger.info(f"[MILESTONE FINAL] Сохранено {len(temp_articles)} статей")
                        except Exception as e:
                            logger.error(f"[MILESTONE FINAL] ОШИБКА: {e}", exc_info=True)
                        finally:
                            self.articles = original_articles
        
        logger.info(f"Скраплено {len(articles)} статей из раздела {section}")
        
        # Сохранение milestone после раздела
        if save_milestone:
            # Временно сохраняем все накопленные статьи для milestone
            temp_articles = list(self.articles) + articles
            json_file = f'rb_articles_milestone_{section}.json'
            csv_file = f'rb_articles_milestone_{section}.csv'
            # Используем временный список для сохранения
            original_articles = self.articles
            self.articles = temp_articles
            self.save_to_json(json_file)
            self.save_to_csv(csv_file)
            self.articles = original_articles  # Восстанавливаем
            logger.info(f"Milestone сохранен: {len(temp_articles)} статей в {json_file} и {csv_file}")
        
        return articles
    
    def scrape_all(self, max_pages_per_section: int = 20, pages_config: dict = None, 
                   save_milestones: bool = True, milestone_interval: int = None) -> List[Dict]:
        all_articles = []
        self.articles = []  # Сбрасываем для накопления
        
        logger.info(f"Настройки сохранения: save_milestones={save_milestones}, milestone_interval={milestone_interval}")
        
        for section in SECTIONS.keys():
            try:
                # Используем настройки из pages_config или значение по умолчанию
                max_pages = pages_config.get(section, max_pages_per_section) if pages_config else max_pages_per_section
                logger.info(f"Скрапинг раздела {section} с максимумом {max_pages} страниц")
                
                # Передаем milestone_interval и текущее количество статей в scrape_section
                # передаем все накопленные статьи через self.articles для правильного сохранения
                self.articles = all_articles  # Обновляем перед началом раздела
                logger.info(f"Передаю в scrape_section: milestone_interval={milestone_interval}, total_before_section={len(all_articles)}")
                articles = self.scrape_section(
                    section, 
                    max_pages, 
                    save_milestone=save_milestones,
                    milestone_interval=milestone_interval,
                    total_before_section=len(all_articles)
                )
                all_articles.extend(articles)
                self.articles = all_articles  # Обновляем для milestone сохранения
                
                logger.info(f"Всего скраплено статей: {len(all_articles)}")
                    
            except Exception as e:
                logger.error(f"Ошибка при скрапинге раздела {section}: {e}")
        
        self.articles = all_articles
        
        if milestone_interval and len(all_articles) >= milestone_interval:
            self.save_to_json('rb_articles_milestone.json')
            self.save_to_csv('rb_articles_milestone.csv')
            logger.info(f"Финальный milestone сохранен: {len(all_articles)} статей")
        
        return all_articles
    
    def save_to_json(self, filename: str = 'rb_articles.json'):
        """Сохранение данных в JSON"""
        self.storage.save_to_json(self.articles, filename)
    
    def save_to_csv(self, filename: str = 'rb_articles.csv'):
        """Сохранение данных в CSV"""
        self.storage.save_to_csv(self.articles, filename)

