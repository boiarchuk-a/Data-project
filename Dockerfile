FROM python:3.12-slim

WORKDIR /app

# Ставим зависимости
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . .

# Настройки по умолчанию
ENV PORT=8000
ENV WORKERS=4

# Запуск uvicorn с несколькими воркерами
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}"]
