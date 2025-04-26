import feedparser
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from flask import Flask
from threading import Thread

# === НАСТРОЙКИ ===
BOT_TOKEN = "твой токен сюда"
CHANNEL_ID = -1002650552114

RSS_FEEDS = [
    "https://slickdeals.net/newsearch.php?searchin=first&rss=1&sort=popularity&filter=Amazon",
    "https://www.hotukdeals.com/tag/amazon.rss",
    "https://www.dealabs.com/groupe/amazon.rss",
    "https://www.mydealz.de/groupe/amazon.rss",
    # Можно добавить еще фиды
]

# Ключевые слова для фильтрации (если пусто, постит всё)
KEYWORDS = ["amazon", "iphone", "laptop", "gaming", "aliexpress", "playstation", "ssd", "sneakers", "watch"]

bot = Bot(token=BOT_TOKEN)
posted_links = set()
LOG_FILE = "bot_log.txt"

# === Функция логирования ===
def log_message(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

# === Мини-сервер Flask для Render/хостинга ===
app = Flask('')

@app.route('/')
def home():
    return "✅ SaleHunt Bot работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Основная логика бота ===
async def fetch_and_post_deals():
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot успешно запущен и следит за скидками!")
        log_message("✅ Бот стартовал и отправил тестовое сообщение.")
    except Exception as test_error:
        log_message(f"❌ Ошибка при отправке тестового сообщения: {test_error}")

    first_run = True

    while True:
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                if not feed.entries:
                    log_message(f"ℹ️ Фид пустой: {feed_url}")
                    continue

                for entry in feed.entries:
                    link = entry.link
                    title = entry.title

                    if first_run:
                        posted_links.add(link)
                        continue

                    if link not in posted_links:
                        # Фильтрация по ключевым словам
                        if KEYWORDS:
                            if not any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                                continue  # если ключевое слово не найдено — пропускаем

                        posted_links.add(link)
                        message_text = f"🔥 {title}"

                        # Кнопка "Перейти на сайт"
                        button = InlineKeyboardButton("👉 Перейти на сайт", url=link)
                        markup = InlineKeyboardMarkup([[button]])

                        try:
                            await bot.send_message(
                                chat_id=CHANNEL_ID,
                                text=message_text,
                                reply_markup=markup,
                                parse_mode='Markdown',
                                disable_web_page_preview=False
                            )
                            print(f"✅ Опубликовано: {title}")
                            log_message(f"✅ Опубликовано: {title}")
                        except Exception as send_error:
                            print(f"❌ Ошибка отправки сообщения: {send_error}")
                            log_message(f"❌ Ошибка отправки сообщения: {send_error}")
            except Exception as feed_error:
                print(f"❌ Ошибка загрузки фида: {feed_error}")
                log_message(f"❌ Ошибка загрузки фида: {feed_error}")

        first_run = False
        log_message("🔄 Проверка фидов завершена. Жду 3 минуты...")
        await asyncio.sleep(3 * 60)

# === Автоматический перезапуск при ошибках ===
async def main():
    while True:
        try:
            await fetch_and_post_deals()
        except Exception as e:
            log_message(f"💥 Бот упал с ошибкой: {e}")
            await asyncio.sleep(10)

# === Старт бота ===
if __name__ == "__main__":
    keep_alive()
    print("🚀 Бот запущен и следит за скидками!")
    log_message("🚀 Бот запущен.")
    asyncio.run(main())
