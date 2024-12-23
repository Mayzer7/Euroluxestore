# Использует минималистичный базовый образ Python 3.11. Версия slim меньше по размеру, чем стандартный образ Python.
FROM python:3.11-slim

# Устанавливаем переменные окружения
# PYTHONDONTWRITEBYTECODE=1 отключает создание файлов *.pyc для сокращения размера контейнера.
# PYTHONUNBUFFERED=1 отключает буферизацию вывода Python, что полезно для логов.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем минимальные системные зависимости

# libpq5 это минимальная библиотека PostgreSQL, необходимая для работы psycopg2-binary. Она значительно легче, чем libpq-dev.

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Указываем рабочую директорию
WORKDIR /app

# Копируем только requirements.txt для кеширования установки зависимостей
COPY requirements.txt /app/

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . /app/

# Сбор статических файлов (если необходимо)
RUN python manage.py collectstatic --noinput

# Открываем порт для приложения
EXPOSE 8000

# Указываем команду по умолчанию для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]