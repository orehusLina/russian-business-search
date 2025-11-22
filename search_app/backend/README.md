# Backend API для поискового приложения

FastAPI бэкенд для работы с Elasticsearch.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка Elasticsearch

1. Установите и запустите Elasticsearch:
   ```bash
   # Docker
   docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:8.11.0
   
   # Или скачайте с https://www.elastic.co/downloads/elasticsearch
   ```

2. Проверьте подключение:
   ```bash
   curl http://localhost:9200
   ```

## Индексация данных

Перед запуском API нужно проиндексировать данные:

```bash
python index_data.py
```

Это создаст индекс `rb_articles` и загрузит все статьи из `rb_articles.json`.

## Запуск API

```bash
python main.py
```

Или через uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

## Переменные окружения

- `ELASTICSEARCH_HOST` - хост Elasticsearch (по умолчанию: localhost)
- `ELASTICSEARCH_PORT` - порт Elasticsearch (по умолчанию: 9200)

## API Endpoints

- `GET /` - информация о API
- `GET /health` - проверка здоровья сервиса
- `POST /search` - поиск статей
- `GET /search?q=...` - поиск статей (GET версия)
- `GET /stats` - статистика по индексу

