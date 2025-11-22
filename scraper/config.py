"""
Конфигурация и константы скрапера
"""

BASE_URL = "https://rb.ru"

SECTIONS = {
    'news': '/news/',
    'stories': '/stories/',
    'opinions': '/columns/',  # Мнения находятся по адресу /columns/
    'neuroprofiles': '/neuro/',
    'reviews': '/reviews/',
    'checklists': '/checklists/'
}

# Настройки по умолчанию
DEFAULT_MAX_WORKERS = 20  # Увеличено для максимальной параллельности
DEFAULT_DELAY = 0.3  # Уменьшено для скорости
DEFAULT_TIMEOUT = 15  # Увеличено для медленных соединений
DEFAULT_RETRIES = 5  # Увеличено количество попыток

# Регулярные выражения для поиска статей
# Включаем columns для мнений
ARTICLE_URL_PATTERN = r'/(news|stories|columns|opinions|neuroprofiles|reviews|checklists)/[^/?]+/?$'
FULL_URL_PATTERN = r'https?://(?:www\.)?rb\.ru/(news|stories|columns|opinions|neuroprofiles|reviews|checklists)/[^/?]+/?$'

