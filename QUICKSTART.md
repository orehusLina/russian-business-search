# Быстрый старт

## Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 2: Тестовый запуск (небольшой объем)

Проверьте, что все работает на небольшом количестве данных:

```bash
python test_small.py
```

**Результат:** ~20-50 статей в `test_articles.json` и `test_articles.csv`

## Шаг 3: Полный скрапинг (большой объем)

Когда убедитесь, что все работает, запустите полный скрапинг:

```bash
python main.py
```

**Результат:** 5,000-20,000 статей в `rb_articles.json` и `rb_articles.csv`

## Настройка объема данных

### Небольшой объем (быстро, для тестирования)

Отредактируйте `main.py`:

```python
# В функции main()
scraper = RBScraper(max_workers=3, delay=1.5)
articles = scraper.scrape_all(max_pages_per_section=5)  # 5 страниц на раздел
```

**Результат:** ~500-1,000 статей за ~15-30 минут

### Средний объем (рекомендуется)

```python
scraper = RBScraper(max_workers=5, delay=1.0)
articles = scraper.scrape_all(max_pages_per_section=20)  # 20 страниц на раздел
```

**Результат:** ~5,000-10,000 статей за ~1-2 часа

### Большой объем (максимум данных)

```python
scraper = RBScraper(max_workers=10, delay=0.5)
articles = scraper.scrape_all(max_pages_per_section=50)  # 50 страниц на раздел
```

**Результат:** ~15,000-30,000 статей за ~3-5 часов

⚠️ **Внимание:** Уменьшение задержки (`delay`) и увеличение потоков (`max_workers`) может привести к блокировке IP. Используйте осторожно!

## Примеры использования

### Скрапинг только новостей

```python
from scraper import RBScraper

scraper = RBScraper()
articles = scraper.scrape_section('news', max_pages=10)
scraper.save_to_json('news_only.json')
```

### Скрапинг с кастомными параметрами

```python
from scraper import RBScraper

# Медленнее, но безопаснее
scraper = RBScraper(max_workers=3, delay=2.0)
articles = scraper.scrape_all(max_pages_per_section=10)
scraper.save_to_json('custom_scrape.json')
scraper.save_to_csv('custom_scrape.csv')
```

## Что дальше?

После скрапинга данные будут в JSON и CSV форматах. Вы можете:

1. **Анализировать данные** - использовать pandas для анализа
2. **Поиск по данным** - искать статьи по компаниям, людям, инвестициям
3. **Визуализация** - строить графики и дашборды
4. **Интеграция с БД** - загрузить данные в базу данных для более сложных запросов

Подробнее см. `README.md`

