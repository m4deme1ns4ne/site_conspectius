FROM python:3.12-slim

WORKDIR /SITE_CONSPECTIUS

ENV PYTHONUNBUFFERED=1

# Установка Poetry
RUN pip install poetry==1.8.2
    
# Копируем только файлы конфигурации Poetry перед установкой зависимостей
COPY pyproject.toml poetry.lock ./
    
# Установка зависимостей
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi
    
# Копируем остальные файлы проекта
COPY . .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
