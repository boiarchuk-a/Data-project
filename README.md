# Проект по машинному обучению: **Модель прогнозирования отклика клиента на скидку**

## Цель

- Решать задачу: *«оценить вероятность отклика клиента на маркетинговое предложение»*.

## Архитектура

**Компоненты:**

- `FastAPI` – веб-фреймворк и REST-интерфейс.
- `SQLite + SQLModel` – хранилище для клиентов и результатов предсказаний.
- `scikit-learn + imbalanced-learn` – обученная ML-модель 
- `Jinja2 + чистый JS` – простая HTML-страница для ввода признаков и просмотра результата.
- `Docker + uvicorn` – упаковка и запуск сервиса с несколькими воркерами.

## Доменная модель

- **Customer**
  - `id`: int
  - `Income`, `Recency`, `MntWines`, … – числовые признаки
  - `created_at`: datetime

- **PredictionResult**
  - `id`: int
  - `customer_id`: int 
  - `score`: float – вероятность отклика
  - `label`: int – бинарное решение (0/1)
  - `model_version`: str
  - `created_at`: datetime

## Структура проекта

```text
app/
  main.py          # точка входа FastAPI
  config.py        # конфигурация 
  db.py            # engine и Session
  models.py        # ORM-модели 
  schemas.py       # Pydantic-схемы
  api/
    predict.py     
    customers.py   
  ml/
    model_smote_lr.pkl      # сохранённая модель
    inference.py   # обёртка для загрузки и predict
  rmq/
    rmq_rpc.py
    rmq_worker.py
frontend/
  templates/index.html
  static/style.css
  static/app.js
tests/
  test_api_predict.py
Dockerfile
requirements.txt
README.md
```

ИНСТРУКЦИЯ по настройке, сборке и запуску:
Далее все пути приводятся относительно корневого каталога
1. Клонировать репозиторий: git clone https://github.com/boiarchuk-a/Data-project
2. Осуществить настройку приложения:

-Cоздать файл арp/rmq/.env, определив в нем значения переменных окружения для
RMQ;

3. Собрать образы: docker-compose build
4. Запустить сервис: docker-compose up
5. Открыть localhost для начала работы.