# Reply Bot for BestChange

Автоответчик на отзывы BestChange. Автоматически отвечает на новые отзывы случайными готовыми сообщениями.

## Использование локально

```bash
# Установить зависимости
pip install -r requirements.txt

# Установить Playwright браузер
playwright install chromium

# Отредактировать config.py с нужными данными
nano config.py

# Запустить
python main.py
```

### Настройка config.py

```python
HEADLESS = False  # False = с браузером, True = без визуала (для контейнеров)
USERNAME = "ваш_логин"
PASSWORD = "ваш_пароль"
EXCHANGER_NAME = "Название обменника"
```

## Использование Docker

### Запуск через docker-compose

```bash
# Редактируем config.py с нужными данными
nano config.py

# Запускаем контейнер
docker-compose up -d

# Смотрим логи
docker-compose logs -f reply-bot

# Останавливаем
docker-compose down
```

### Запуск через Docker напрямую

```bash
docker build -t reply-bot .
docker run -d --name reply-bot \
  -v $(pwd)/config.py:/app/config.py \
  -v $(pwd)/logs:/app/logs \
  reply-bot
```

## Как это работает

1. ✅ Входит в админку BestChange
2. 🔄 В бесконечном цикле:
   - Проверяет новые отзывы без ответов
   - Отвечает на найденные отзывы (до первого отзыва с ответом)
   - Случайно выбирает один из 20 вариантов ответа
   - Ждет 15 секунд перед следующей проверкой

## Варианты ответов

В `config.py` есть 20 готовых вариантов ответов. Программа случайно выбирает один из них для каждого отзыва.

## Требования

- Python 3.11+
- Playwright
- Docker & Docker Compose (для контейнера)
