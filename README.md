# Response to Comments

Бот на Python + Playwright для автоматических ответов на положительные отзывы в админке обменника. Проект запускается через Docker Compose и может поднимать сразу два контейнера:

- `ex1-reply-bot`
- `ex2-reply-bot`

Оба сервиса используют один и тот же код, но берут разные учетные данные и названия обменников из переменных окружения.

## Что делает бот

- открывает страницу входа в админку;
- авторизуется;
- переходит на страницу отзывов;
- ищет положительные отзывы без ответа;
- публикует ответ;
- выбирает шаблон ответа случайно без повторов, пока не закончатся все варианты;
- повторяет проверку каждые 5 минут.

---

## 1. Что нужно перед запуском

На машине должны быть установлены:

- `git`
- Docker
- Docker Compose plugin

Проверить можно так:

```bash
git --version
docker --version
docker compose version
```

Если Docker Desktop на macOS еще не установлен, сначала установите и запустите его.

---

## 2. Клонирование репозитория

Склонируйте проект и перейдите в папку:

```bash
git clone https://github.com/krutoiChel2004/response-to-comments.git
cd response-to-comments
```

Если папка после клонирования называется иначе, используйте фактическое имя директории.

---

## 3. Подготовка `.env`

Для запуска через Docker Compose нужен файл `.env` в корне проекта. Именно из него Compose подставляет значения в контейнеры.

Создайте файл `.env` рядом с:

- `docker-compose.yml`
- `Dockerfile`
- `main.py`

Пример содержимого:

```env
# Общие настройки
ADMIN_URL=https://example.com/admin/login
REVIEWS_URL=https://example.com/reviews
HEADLESS=True

# ex1
EXCHANGER_NAME_GB=GetBit
USERNAME_GB=your_ex1_login
PASSWORD_GB=your_ex1_password

# ex2
EXCHANGER_NAME_BB=BitBuy
USERNAME_BB=your_ex2_login
PASSWORD_BB=your_ex2_password
```

### Назначение переменных

#### Общие

- `ADMIN_URL` — страница входа в админку.
- `REVIEWS_URL` — страница со списком отзывов.
- `HEADLESS` — запуск браузера без интерфейса. Для Docker обычно должно быть `True`.

#### Для сервиса `getbit-reply-bot`

- `EXCHANGER_NAME_GB` — имя обменника, подставляется в текст ответа.
- `USERNAME_GB` — логин от админки.
- `PASSWORD_GB` — пароль от админки.

#### Для сервиса `bitbuy-reply-bot`

- `EXCHANGER_NAME_BB` — имя второго обменника.
- `USERNAME_BB` — логин от админки.
- `PASSWORD_BB` — пароль от админки.

> Если нужен только один бот, второй сервис можно не запускать. Но переменные, используемые запускаемым сервисом, должны быть заполнены обязательно.

---

## 4. Проверка структуры проекта

Перед сборкой убедитесь, что в корне проекта есть основные файлы:

```text
Dockerfile
docker-compose.yml
main.py
config.py
pyproject.toml
.env
logs/
```

Папка `logs/` может быть пустой, но должна существовать. Она примонтирована в контейнер.

---

## 5. Сборка и запуск через Docker Compose

Находясь в корне проекта, выполните:

```bash
docker compose up --build -d
```

Эта команда:

- соберет Docker image;
- установит Python-зависимости;
- установит Chromium для Playwright;
- поднимет контейнеры в фоне.

Если нужен запуск в активной консоли, без фона:

```bash
docker compose up --build
```

---

## 6. Проверка, что контейнеры запустились

Посмотреть список контейнеров:

```bash
docker compose ps
```

Посмотреть логи всех сервисов:

```bash
docker compose logs -f
```

Посмотреть логи только `getbit-reply-bot`:

```bash
docker compose logs -f getbit-reply-bot
```

Посмотреть логи только `bitbuy-reply-bot`:

```bash
docker compose logs -f bitbuy-reply-bot
```

Если все настроено правильно, в логах будут сообщения о переходе на страницу входа, авторизации и поиске отзывов без ответа.

---

## 7. Полезные команды Docker Compose

### Остановить контейнеры

```bash
docker compose stop
```

### Остановить и удалить контейнеры

```bash
docker compose down
```

### Перезапустить контейнеры

```bash
docker compose restart
```

### Пересобрать и заново запустить

```bash
docker compose down
docker compose up --build -d
```

### Запустить только один сервис

Только GetBit:

```bash
docker compose up --build -d getbit-reply-bot
```

Только BitBuy:

```bash
docker compose up --build -d bitbuy-reply-bot
```

---

## 8. Как обновить проект после изменений в Git

Если код изменился в репозитории:

```bash
git pull
docker compose down
docker compose up --build -d
```

Так контейнеры будут пересобраны уже с новой версией кода.

---

## 9. Типичный порядок запуска с нуля

Полный сценарий от `git clone` до старта:

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd response-to-comments
touch .env
mkdir -p logs
docker compose up --build -d
docker compose logs -f
```

После команды `touch .env` обязательно откройте `.env` и заполните его значениями.

---

## 10. Возможные проблемы и решения

### Контейнер сразу завершается

Проверьте логи:

```bash
docker compose logs --tail=200
```

Чаще всего причина одна из следующих:

- не создан `.env`;
- в `.env` отсутствуют обязательные переменные;
- неверный `ADMIN_URL`;
- неверный `REVIEWS_URL`;
- неправильный логин или пароль.

### Ошибка авторизации

Проверьте:

- правильность `USERNAME_*` и `PASSWORD_*`;
- актуальность `ADMIN_URL`;
- не изменилась ли форма входа на сайте.

### Playwright не может открыть страницу

Проверьте:

- есть ли у Docker доступ в интернет;
- открывается ли нужный сайт с вашей машины;
- не блокируется ли сайт по IP или географии.

### Бот не отвечает на отзывы

Проверьте:

- точно ли отзывы являются положительными;
- соответствует ли `REVIEWS_URL` нужной странице;
- не изменилась ли HTML-структура страницы отзывов.

---

## 11. Как остановить автозапуск контейнеров

В `docker-compose.yml` используется политика:

```yaml
restart: unless-stopped
```

Это означает, что контейнер будет автоматически перезапускаться, пока вы явно его не остановите.

Чтобы полностью остановить проект:

```bash
docker compose down
```

---

## 12. Замечания по безопасности

- не коммитьте `.env` в Git;
- не храните реальные логины и пароли в `README.md`;
- ограничьте доступ к машине, где запущен Docker;
- регулярно меняйте пароли, если контейнер используется в проде.

---

## 13. Быстрый старт

Если нужен короткий вариант:

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd response-to-comments
mkdir -p logs
cat > .env <<'EOF'
ADMIN_URL=https://example.com/admin/login
REVIEWS_URL=https://example.com/reviews
HEADLESS=True
EXCHANGER_NAME_GB=GetBit
USERNAME_GB=login1
PASSWORD_GB=password1
EXCHANGER_NAME_BB=BitBuy
USERNAME_BB=login2
PASSWORD_BB=password2
EOF
docker compose up --build -d
docker compose logs -f
```

---

## 14. Что важно помнить

- для Docker рекомендуется `HEADLESS=True`;
- без корректного `.env` контейнеры нормально не запустятся;
- проект может запускать как один, так и два бота;
- ответы на отзывы выбираются случайно без повторения, пока не будут использованы все шаблоны.
