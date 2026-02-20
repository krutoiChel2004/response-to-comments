# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для Playwright
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы проекта
COPY pyproject.toml .
COPY .python-version .
COPY config.py .
COPY main.py .
COPY .env .

# Устанавливаем зависимости через uv
RUN uv sync

# Устанавливаем браузеры Playwright
RUN uv run playwright install chromium
RUN uv run playwright install-deps chromium

ENV PYTHONUNBUFFERED=1

# Запускаем скрипт
CMD ["uv", "run", "main.py"]