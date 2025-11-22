"""
Модуль для парсинга HTML страниц
"""

import re
import logging
from typing import Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .config import BASE_URL, SECTIONS, ARTICLE_URL_PATTERN, FULL_URL_PATTERN
from .extractors import DataExtractor

logger = logging.getLogger(__name__)


class HTMLParser:
    """Класс для парсинга HTML страниц"""
    
    def __init__(self):
        self.extractor = DataExtractor()
    
    def detect_content_type(self, url: str, soup: BeautifulSoup) -> str:
        """
        Определение типа контента (новость, история, мнение и т.д.)
        
        Args:
            url: URL страницы
            soup: BeautifulSoup объект
            
        Returns:
            Тип контента
        """
        url_lower = url.lower()
        # Проверяем columns для мнений
        if '/columns/' in url_lower:
            return 'opinions'
        
        for content_type, path in SECTIONS.items():
            if path.replace('/', '') in url_lower:
                return content_type
        
        # Попытка определить по классам или структуре страницы
        if soup.find('div', class_=re.compile(r'news', re.I)):
            return 'news'
        elif soup.find('div', class_=re.compile(r'story', re.I)):
            return 'stories'
        elif soup.find('div', class_=re.compile(r'opinion|column', re.I)):
            return 'opinions'
        
        return 'unknown'
    
    def parse_article(self, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Парсинг страницы статьи
        
        Args:
            url: URL статьи
            soup: BeautifulSoup объект
            
        Returns:
            Словарь с данными статьи или None
        """
        try:
            from datetime import datetime
            
            article = {
                'url': url,
                'title': '',
                'content_type': self.detect_content_type(url, soup),
                'author': '',
                'date': '',
                'tags': [],
                'categories': [],
                'text': '',
                'companies': [],
                'people': [],
                'money': [],
                'description': '',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Заголовок (множественные варианты поиска)
            # Сначала проверяем мета-теги (они более надежны), потом h1, потом title
            title_elem = None
            title_text = ''
            
            # 1. Мета-тег og:title (самый надежный)
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title_text = og_title.get('content', '').strip()
            
            # 2. Если не нашли, ищем h1 с текстом
            if not title_text:
                h1_elem = (soup.find('h1', class_=re.compile(r'title|heading|article', re.I)) or
                          soup.find('h1'))
                if h1_elem:
                    h1_text = h1_elem.get_text(strip=True)
                    if h1_text:  # Проверяем что h1 не пустой
                        title_text = h1_text
            
            # 3. Если все еще не нашли, берем из тега <title>
            if not title_text:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    # Убираем " | RB.RU" из конца если есть
                    if ' | RB.RU' in title_text:
                        title_text = title_text.replace(' | RB.RU', '').strip()
            
            if title_text:
                article['title'] = title_text
            
            # Автор (множественные варианты поиска)
            author_elem = (soup.find('a', class_=re.compile(r'author|writer|journalist', re.I)) or
                          soup.find('span', class_=re.compile(r'author', re.I)) or
                          soup.find('div', class_=re.compile(r'author', re.I)) or
                          soup.find('meta', property='article:author') or
                          soup.find('span', itemprop='author') or
                          soup.find('div', itemprop='author'))
            if author_elem:
                if author_elem.name == 'meta':
                    article['author'] = author_elem.get('content', '')
                else:
                    article['author'] = author_elem.get_text(strip=True)
            
            # Дата (множественные варианты поиска)
            date_elem = (soup.find('time') or
                        soup.find('time', datetime=True) or
                        soup.find('span', class_=re.compile(r'date|time', re.I)) or
                        soup.find('div', class_=re.compile(r'date|time', re.I)) or
                        soup.find('meta', property='article:published_time') or
                        soup.find('span', itemprop='datePublished'))
            if date_elem:
                if date_elem.name == 'meta':
                    article['date'] = date_elem.get('content', '')
                elif date_elem.get('datetime'):
                    article['date'] = date_elem.get('datetime')
                else:
                    article['date'] = date_elem.get_text(strip=True)
            
            # Основной текст статьи (множественные варианты поиска)
            content_elem = (soup.find('article') or
                           soup.find('div', class_=re.compile(r'content|article|text|body|post', re.I)) or
                           soup.find('main') or
                           soup.find('div', itemprop='articleBody') or
                           soup.find('section', class_=re.compile(r'content|article', re.I)))
            if content_elem:
                # Удаляем скрипты, стили и ненужные элементы
                for script in content_elem(["script", "style", "nav", "footer", "header", "aside", "form"]):
                    script.decompose()
                article['text'] = content_elem.get_text(separator=' ', strip=True)
            
            # Описание/краткое содержание
            desc_elem = (soup.find('meta', property='og:description') or
                        soup.find('meta', attrs={'name': 'description'}) or
                        soup.find('div', class_=re.compile(r'description|excerpt|lead', re.I)))
            if desc_elem:
                if desc_elem.name == 'meta':
                    article['description'] = desc_elem.get('content', '')
                else:
                    article['description'] = desc_elem.get_text(strip=True)
            
            # Теги (множественные варианты поиска)
            # Важно: ищем теги ТОЛЬКО внутри контента статьи, исключая глобальную навигацию
            tags_elems = []
            
            # 1. Мета-теги для тегов статьи (самый надежный способ)
            meta_tags = soup.find_all('meta', property=re.compile(r'article:tag|og:tag', re.I))
            for meta in meta_tags:
                tag_content = meta.get('content', '').strip()
                if tag_content:
                    tags_elems.append(tag_content)
            
            # 2. Ищем теги внутри контента статьи (исключаем header, footer, nav, aside)
            article_content = (soup.find('article') or 
                             soup.find('div', class_=re.compile(r'content|article|text|body|post', re.I)) or
                             soup.find('main'))
            
            if article_content:
                # Исключаем глобальные элементы
                excluded_parents = article_content.find_parents(['header', 'nav', 'footer', 'aside'])
                if not excluded_parents:
                    # Ищем теги только внутри контента статьи
                    content_tags = article_content.find_all(['a', 'span', 'div', 'li'], 
                                                           class_=re.compile(r'tag', re.I))
                    for tag in content_tags:
                        # Проверяем, что тег не в глобальной навигации
                        if not tag.find_parents(['header', 'nav', 'footer', 'aside']):
                            tag_text = tag.get_text(strip=True)
                            # Исключаем общие теги сайта (которые есть везде)
                            common_tags = {'Тренды', 'Деньги', 'Бизнес', 'Россия', 'Технологии', 
                                         'Маркетплейсы', 'Стартапы', 'Искусственный интеллект', 
                                         'IT', 'Личное'}
                            if tag_text and tag_text not in common_tags and tag_text not in tags_elems:
                                tags_elems.append(tag_text)
            
            # 3. Ищем в специальных блоках тегов статьи (обычно внизу статьи, но не в футере)
            tags_section = (soup.find('section', class_=re.compile(r'tag', re.I)) or
                          soup.find('div', class_=re.compile(r'tags|tag-list|tag-cloud', re.I)) or
                          soup.find('ul', class_=re.compile(r'tag', re.I)))
            
            if tags_section:
                # Исключаем навигацию и глобальные элементы
                if not tags_section.find_parents(['header', 'nav', 'footer', 'aside']):
                    section_tags = tags_section.find_all(['a', 'span', 'li'], 
                                                        class_=re.compile(r'tag', re.I))
                    for tag in section_tags:
                        tag_text = tag.get_text(strip=True)
                        if tag_text and tag_text not in tags_elems:
                            tags_elems.append(tag_text)
            
            # 4. Ищем по data-атрибутам или rel (только внутри статьи)
            data_tags = soup.find_all(attrs={'data-tag': True}) + \
                       soup.find_all(attrs={'rel': re.compile(r'tag', re.I)})
            for tag in data_tags:
                # Проверяем, что тег не в глобальной навигации
                if not tag.find_parents(['header', 'nav', 'footer', 'aside']):
                    tag_text = tag.get('data-tag') or tag.get_text(strip=True)
                    if tag_text and tag_text not in tags_elems:
                        tags_elems.append(tag_text)
            
            # Убираем дубликаты и пустые значения
            article['tags'] = list(set([tag.strip() for tag in tags_elems if tag.strip()]))
            
            # Категории (из хлебных крошек, навигации или мета-тегов)
            breadcrumbs = (soup.find('nav', class_=re.compile(r'breadcrumb', re.I)) or
                          soup.find('div', class_=re.compile(r'breadcrumb', re.I)) or
                          soup.find('ol', class_=re.compile(r'breadcrumb', re.I)))
            if breadcrumbs:
                links = breadcrumbs.find_all('a')
                article['categories'] = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
            
            # Также пробуем извлечь категории из мета-тегов
            category_meta = soup.find('meta', property='article:section')
            if category_meta:
                article['categories'].append(category_meta.get('content', ''))
            
            # Извлечение уникальных полей из текста
            full_text = article['text'] + ' ' + article['description'] + ' ' + article['title']
            article['money'] = self.extractor.extract_money(full_text)
            article['companies'] = self.extractor.extract_companies(full_text)
            article['people'] = self.extractor.extract_people(full_text)
            
            return article
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге {url}: {e}")
            return None
    
    def extract_article_links(self, soup: BeautifulSoup) -> list:
        """
        Извлечение ссылок на статьи из HTML
        
        Args:
            soup: BeautifulSoup объект
            
        Returns:
            Список URL статей
        """
        urls = []
        article_links = []
        
        # Паттерн для поиска ссылок на статьи
        article_pattern = re.compile(ARTICLE_URL_PATTERN)
        
        # Различные способы поиска ссылок на статьи
        # 1. Поиск по паттерну в href (самый надежный способ)
        links_by_pattern = soup.find_all('a', href=article_pattern)
        article_links.extend(links_by_pattern)
        logger.debug(f"Найдено ссылок по паттерну: {len(links_by_pattern)}")
        
        # 2. Поиск в статьях
        articles = soup.find_all('article')
        logger.debug(f"Найдено тегов <article>: {len(articles)}")
        for article in articles:
            link = article.find('a', href=True)
            if link and link not in article_links:
                article_links.append(link)
        
        # 3. Поиск в карточках/блоках статей (расширенный поиск)
        cards = soup.find_all(['div', 'section', 'li'], class_=re.compile(r'article|card|post|item|news|story|column|opinion', re.I))
        logger.debug(f"Найдено карточек: {len(cards)}")
        for card in cards:
            # Ищем все ссылки внутри карточки, не только первую
            links_in_card = card.find_all('a', href=True)
            for link in links_in_card:
                if link not in article_links:
                    article_links.append(link)
        
        # 4. Поиск всех ссылок и фильтрация по паттерну (более широкий поиск)
        all_links = soup.find_all('a', href=True)
        logger.debug(f"Всего ссылок на странице: {len(all_links)}")
        for link in all_links:
            href = link.get('href', '')
            if href:
                # Проверяем относительные и абсолютные ссылки
                if article_pattern.search(href):
                    if link not in article_links:
                        article_links.append(link)
        
        # 5. Дополнительный поиск в списках статей (часто статьи в <ul><li>)
        list_items = soup.find_all('li')
        for li in list_items:
            link = li.find('a', href=True)
            if link and article_pattern.search(link.get('href', '')):
                if link not in article_links:
                    article_links.append(link)
        
        logger.debug(f"Всего найдено потенциальных ссылок на статьи: {len(article_links)}")
        
        # Обработка найденных ссылок
        url_pattern = re.compile(FULL_URL_PATTERN)
        for link in article_links:
            href = link.get('href', '')
            if href:
                full_url = urljoin(BASE_URL, href)
                # Фильтруем только прямые ссылки на статьи
                if url_pattern.match(full_url):
                    # Убираем параметры и слеш в конце для нормализации
                    normalized_url = full_url.rstrip('/').split('?')[0] + '/'
                    # Исключаем страницы пагинации и другие служебные страницы
                    if '/page/' not in normalized_url and normalized_url not in urls:
                        urls.append(normalized_url)
        
        logger.debug(f"После фильтрации осталось уникальных URL: {len(urls)}")
        return urls

