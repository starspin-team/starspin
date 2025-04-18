FROM python:3.9-slim

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копирование всего содержимого проекта
COPY . /app/

# Настройка Poetry для не использования виртуального окружения
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-interaction --no-ansi --no-root

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 