# RB.RU Search

Веб-приложение для поиска по статьям RB.RU на Flutter с бэкендом FastAPI и Elasticsearch.

## Структура

```
search_app/
├── lib/              # Flutter приложение
├── backend/          # FastAPI бэкенд
└── web/              # Веб-конфигурация
```

## Установка

1. Установите зависимости Flutter:
```bash
cd search_app
flutter pub get
```

2. Установите Python зависимости:
```bash
cd backend
pip install -r requirements.txt
```

3. Запустите Elasticsearch:
```bash
# Скачайте с https://www.elastic.co/downloads/elasticsearch
# Запустите bin/elasticsearch.bat (Windows) или bin/elasticsearch (Linux/Mac)
```

## Запуск

1. Индексация данных:
```bash
cd search_app/backend
python index_data.py
```

2. Запуск бэкенда:
```bash
python main.py
```

3. Запуск фронтенда:
```bash
cd search_app
flutter run -d chrome
```

## API

- `GET /search?q=...` - поиск статей
- `GET /stats` - статистика по индексу
- `GET /health` - проверка здоровья сервиса

Документация: http://localhost:8000/docs

## Переменные окружения

- `ELASTICSEARCH_HOST` - хост Elasticsearch (по умолчанию: localhost)
- `ELASTICSEARCH_PORT` - порт Elasticsearch (по умолчанию: 9200)
