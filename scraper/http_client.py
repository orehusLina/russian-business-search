"""
Модуль для работы с HTTP запросами
"""

import time
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from .config import DEFAULT_TIMEOUT, DEFAULT_RETRIES

logger = logging.getLogger(__name__)


class HTTPClient:
    """Клиент для выполнения HTTP запросов"""
    
    def __init__(self, delay: float = 1.0, timeout: int = DEFAULT_TIMEOUT):
        """
        Инициализация HTTP клиента
        
        Args:
            delay: Задержка между запросами (секунды)
            timeout: Таймаут запроса (секунды)
        """
        self.session = requests.Session()
        self.ua = UserAgent()
        self.delay = delay
        self.timeout = timeout
    
    def get_headers(self) -> dict:
        """Генерация заголовков для запроса"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'close',  # Используем close вместо keep-alive для избежания проблем с соединением
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
        }
    
    def fetch_page(self, url: str, retries: int = DEFAULT_RETRIES) -> Optional[BeautifulSoup]:
        """
        Загрузка страницы с обработкой ошибок
        
        Args:
            url: URL страницы
            retries: Количество попыток при ошибке
            
        Returns:
            BeautifulSoup объект или None при ошибке
        """
        for attempt in range(retries):
            try:
                # Добавляем небольшую задержку перед запросом для избежания перегрузки
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка при повторах
                
                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    timeout=self.timeout,
                    allow_redirects=True,
                    stream=False  # Не используем stream для избежания проблем с соединением
                )
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                # Задержка после успешного запроса (минимальная для скорости)
                if self.delay > 0:
                    time.sleep(self.delay)
                return BeautifulSoup(response.text, 'lxml')
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.Timeout) as e:
                # Специальная обработка ошибок соединения
                wait_time = min(2 ** attempt, 30)  # Максимум 30 секунд
                logger.warning(f"Ошибка соединения при загрузке {url} (попытка {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    logger.info(f"Ожидание {wait_time} секунд перед повтором...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Не удалось загрузить {url} после {retries} попыток")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Ошибка при загрузке {url} (попытка {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Не удалось загрузить {url} после {retries} попыток")
        
        return None

