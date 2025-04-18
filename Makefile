.PHONY: setup run clean docker-run

# Настройка виртуального окружения и установка зависимостей
setup:
	python -m pip install --upgrade pip
	pip install poetry
	poetry install

# Запуск приложения локально 
run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запуск с помощью Docker
docker-run:
	docker-compose up --build

# Остановка Docker контейнеров
docker-stop:
	docker-compose down

# Очистка кэша Python и временных файлов
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Инициализация базы данных локально (PostgreSQL должен быть установлен)
init-db:
	docker run -d -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=starspin postgres:14

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  make setup       - Установка зависимостей с помощью Poetry"
	@echo "  make run         - Запуск приложения локально"
	@echo "  make docker-run  - Запуск с помощью Docker"
	@echo "  make docker-stop - Остановка Docker контейнеров"
	@echo "  make clean       - Очистка временных файлов"
	@echo "  make init-db     - Запуск PostgreSQL в Docker для локальной разработки"
	@echo "  make help        - Показать эту подсказку" 