import feedparser
import asyncio
from telegram import Bot
from datetime import datetime
import os

# Получаем данные из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Ссылки на фиды скидок
RSS_FEEDS = [
    "https://slickdeals.net/newsearch.php?searchin=first&rss=1&sort=popularity&filter=Amazon",
    "https://www.hotukdeals.com/tag/amazon.rss"
]

bot = Bot(token=BOT_TOKEN)
posted_links = set()
LOG_FILE = "bot_log.txt"

def log_message(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

async def fetch_and_post_deals():
    # Тестовое сообщение при запуске
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot успешно запущен и следит за скидками!")
        log_message("✅ Бот стартовал и отправил тестовое сообщение.")
    except Exception as test_error:
        log_message(f"❌ Ошибка при отправке тестового сообщения: {test_error}")

    while True:
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    link = entry.link
                    title = entry.title
                    if link not in posted_links:
                        posted_links.add(link)
                        message = f"🔥 {title}\n\n👉 [Посмотреть предложение]({link})"
                        try:
                            await bot.send_message(
                                chat_id=CHANNEL_ID,
                                text=message,
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

        await asyncio.sleep(30 * 60)

# Важно! Здесь правильный синтаксис
if"__name__"== "__main__":
    print("🚀 Бот запущен и следит за скидками!")
    log_message("🚀 Бот запущен.")
    asyncio.run(fetch_and_post_deals())