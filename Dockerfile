# Используем базовый образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем зависимости системы
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Указываем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app/

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir --upgrade pip && pip --version
RUN pip install --no-cache-dir setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Сбор статических файлов
RUN python manage.py collectstatic --noinput

# Открываем порт для приложения
EXPOSE 8000

# Указываем команду по умолчанию для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]