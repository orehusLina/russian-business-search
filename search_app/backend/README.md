# Backend API

FastAPI бэкенд для поиска по статьям RB.RU.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

1. Запустите Elasticsearch на порту 9200
2. Проиндексируйте данные:
```bash
python index_data.py
```

## Запуск

```bash
python main.py
```

API доступен на http://localhost:8000

## Endpoints

- `GET /search?q=...` - поиск статей
- `GET /stats` - статистика по индексу
- `GET /health` - проверка здоровья сервиса

## Переменные окружения

- `ELASTICSEARCH_HOST` - хост Elasticsearch (по умолчанию: localhost)
- `ELASTICSEARCH_PORT` - порт Elasticsearch (по умолчанию: 9200)
