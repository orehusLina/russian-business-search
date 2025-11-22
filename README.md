# Russian Business

Проект для сбора и поиска статей с сайта RB.RU.

![Project Overview](pic.jpg)

## Структура

- `scraper/` - скрапер для сбора статей
- `search_app/` - веб-приложение для поиска

## Быстрый старт

### Скрапинг данных

```bash
pip install -r requirements.txt
python main.py
```

Данные сохраняются в `rb_articles.json`.

### Поисковое приложение

1. Запустите Elasticsearch
2. Индексируйте данные: `cd search_app/backend && python index_data.py`
3. Запустите бэкенд: `python main.py`
4. Запустите фронтенд: `cd search_app && flutter run -d chrome`

Подробнее см. `search_app/README.md`.
