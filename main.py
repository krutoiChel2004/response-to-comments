import asyncio
import random
from playwright.async_api import async_playwright
from config import USERNAME, PASSWORD, EXCHANGER_NAME, ADMIN_URL, REVIEWS_URL, REPLY_TEMPLATES, HEADLESS

async def login_to_bestchange(page, username, password):
    """
    Выполняет вход в админ-панель BestChange
    """
    print("Пытаемся войти в систему...")
    
    # Заполняем поле username
    username_input = await page.query_selector('#username')
    if username_input:
        await username_input.fill(username)
        print(f"Заполнено имя пользователя: {username}")
    else:
        print("Поле username не найдено!")
        return False
    
    # Заполняем поле password
    password_input = await page.query_selector('#password')
    if password_input:
        await password_input.fill(password)
        print("Заполнен пароль")
    else:
        print("Поле password не найдено!")
        return False
    
    # Нажимаем кнопку Login
    login_button = await page.query_selector('input[type="submit"][value="Login"]')
    if login_button:
        # Используем expect_navigation чтобы обработать редирект правильно
        try:
            async with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
                await login_button.click(timeout=5000)
            print("Кнопка Login нажата и редирект завершен")
        except Exception as e:
            print(f"Ошибка при клике на Login: {e}")
            # Даже если навигация не прошла, пробуем дождаться загрузки
            await page.wait_for_timeout(3000)
    else:
        print("Кнопка Login не найдена!")
        return False
    
    # Проверяем, успешен ли вход
    current_url = page.url
    if "login" not in current_url.lower() and "auth" not in current_url.lower():
        print("✅ Вход выполнен успешно!")
        return True
    else:
        print("❌ Ошибка входа. Проверьте логин/пароль")
        return False

async def find_reviews_without_reply(page):
    """
    Находит ID положительных отзывов БЕЗ ответа до первого отзыва, у которого уже есть ответ.
    Останавливается при встречении первого отзыва с ответом.
    Возвращает словарь с отзывами и флагом о найденном ответленном отзыве.
    """
    print("\nИщем положительные отзывы без ответов...")
    
    # Ждем загрузки таблицы с отзывами
    await page.wait_for_selector('[id^="reviewtext"]', timeout=10000, state="attached")
    
    # Находим все строки с текстом отзывов
    review_text_elements = await page.query_selector_all('[id^="reviewtext"]')
    
    if not review_text_elements:
        print("Не найдено ни одного отзыва на странице!")
        return {'reviews': [], 'found_answered_review': False}
    
    print(f"Найдено {len(review_text_elements)} отзывов на странице")
    
    reviews_without_reply = []
    found_answered_review = False
    
    for review_text_element in review_text_elements:
        # Получаем тип отзыва из атрибута title
        review_type = await review_text_element.get_attribute('title')
        
        # Пропускаем если это не положительный отзыв
        if review_type != "Положительный отзыв":
            continue
        
        # Получаем ID элемента, например "reviewtext3697926"
        review_text_id = await review_text_element.get_attribute('id')
        if not review_text_id:
            continue
            
        # Извлекаем числовой ID отзыва
        review_id = review_text_id.replace('reviewtext', '')
        
        # Ищем span со счетчиком комментариев
        comment_count_span = await page.query_selector(f'[id="commentcount{review_id}"]')
        
        if comment_count_span:
            # Проверяем, скрыт ли элемент (display: none)
            is_visible = await comment_count_span.is_visible()
            
            if not is_visible:
                # Если элемент скрыт, значит комментариев нет
                print(f"✓ Положительный отзыв ID {review_id} - БЕЗ ОТВЕТА")
                reviews_without_reply.append({
                    'id': review_id,
                    'url': f"https://www.bestchange.ru/getbit-exchanger.html?review={review_id}"
                })
            else:
                # Элемент видим, значит есть комментарий
                count_text = await comment_count_span.text_content()
                print(f"⏹️  Положительный отзыв ID {review_id} - уже есть ответ ({count_text})")
                print("Останавливаемся - остальные отзывы уже ответленные")
                found_answered_review = True
                break
    
    print(f"\n📊 Всего найдено новых положительных отзывов без ответа: {len(reviews_without_reply)}")
    return {'reviews': reviews_without_reply, 'found_answered_review': found_answered_review}

async def main():
    # Список для отслеживания неиспользованных шаблонов
    available_templates = REPLY_TEMPLATES.copy()
    random.shuffle(available_templates)  # Перемешиваем для случайного порядка
    
    async with async_playwright() as p:
        # Запускаем браузер
        browser = await p.chromium.launch(headless=HEADLESS)
        
        # Создаем контекст с увеличенным таймаутом
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 1024}
        )
        page = await context.new_page()
        
        try:
            # ШАГ 1: Переходим на страницу входа
            print(f"Переходим на страницу входа {EXCHANGER_NAME}...")
            await page.goto(ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
            
            # ШАГ 2: Выполняем вход
            login_success = await login_to_bestchange(page, USERNAME, PASSWORD)
            
            if not login_success:
                print("Не удалось войти. Завершаем работу.")
                await browser.close()
                return
            
            # Бесконечный цикл проверки отзывов
            while True:
                # ШАГ 3: Переходим на страницу отзывов обменника
                print(f"\n{'='*60}")
                print(f"Переходим на страницу отзывов {EXCHANGER_NAME}...")
                await page.goto(REVIEWS_URL, wait_until="domcontentloaded", timeout=60000)
                
                # ШАГ 4: Ищем отзывы без ответов
                search_result = await find_reviews_without_reply(page)
                reviews_without_reply = search_result['reviews']
                found_answered_review = search_result['found_answered_review']
                
                # ШАГ 5: (Опционально) Автоматически отвечаем на отзывы
                if reviews_without_reply:
                    print("\nНачинаем отвечать на отзывы...")
                    
                    for review in reviews_without_reply:  # Обрабатываем ВСЕ найденные отзывы
                        review_id = review['id']
                        print(f"\nОбрабатываем отзыв ID: {review_id}")
                        
                        # Разворачиваем форму комментирования
                        await page.click(f'[onclick="return replyform({review_id})"]')
                        await page.wait_for_timeout(500)  # Ждем анимации
                        
                        # Выбираем шаблон из неиспользованных
                        if not available_templates:
                            # Если все шаблоны использованы, сбрасываем список
                            available_templates = REPLY_TEMPLATES.copy()
                            random.shuffle(available_templates)
                            print("  🔄 Все шаблоны использованы, сбрасываем список")
                        
                        # Берем и удаляем первый шаблон из списка
                        reply_template = available_templates.pop(0)
                        reply_text = reply_template.format(exchanger_name=EXCHANGER_NAME)
                        print(f"  📝 Использовано шаблонов: {len(REPLY_TEMPLATES) - len(available_templates)}/{len(REPLY_TEMPLATES)}")
                        
                        await page.fill(f'#replytext{review_id}', reply_text)
                        print(f"  Текст ответа заполнен")
                        
                        # Отправляем ответ
                        await page.click(f'#send_button{review_id}')
                        print(f"  ✅ Ответ отправлен для отзыва {review_id}")
                        
                        # Ждем немного между ответами
                        await page.wait_for_timeout(2000)
                        
                        # Обновляем страницу после каждого ответа
                        if len(reviews_without_reply) > 1:
                            await page.reload(wait_until="domcontentloaded", timeout=60000)
                            await page.wait_for_timeout(1000)
                    
                    # Если найден отзыв с ответом, значит мы дошли до границы
                    if found_answered_review:
                        print("\n⏳ Дошли до последнего необработанного отзыва. Ждем 5 минут перед следующей проверкой...")
                        await page.wait_for_timeout(300000)  # 5 минут = 300000 миллисекунд
                    else:
                        print("\n⏳ Все новые отзывы обработаны. Ждем 5 минут перед следующей проверкой...")
                        await page.wait_for_timeout(300000)  # 5 минут = 300000 миллисекунд
                else:
                    print("\n✅ Нет новых отзывов для ответа.")
                    
                    if found_answered_review:
                        print("⏳ Ждем 5 минут перед следующей проверкой...")
                        await page.wait_for_timeout(300000)  # 5 минут = 300000 миллисекунд
                    else:
                        print("⏳ Все отзывы уже имеют ответы. Ждем 5 минут перед следующей проверкой...")
                        await page.wait_for_timeout(300000)  # 5 минут = 300000 миллисекунд
            
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Даем посмотреть результат перед закрытием
            await page.wait_for_timeout(5000)
            await browser.close()
            print("\n👋 Браузер закрыт. Работа завершена.")

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())