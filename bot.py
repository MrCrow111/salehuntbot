import feedparser
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from flask import Flask
from threading import Thread

# === НАСТРОЙКИ ===
BOT_TOKEN = "7758500745:AAGF3Vr0GLbQgk_XudSHGxZVbC33Spwtm3o"
CHANNEL_ID = -1002650552114

# === Новый список проверенных RSS-фидов ===
RSS_FEEDS = [
    "https://9to5toys.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.engadget.com/rss.xml",
    "https://www.gizmodo.com.au/rss",
    "https://www.wired.com/feed/rss",
    "https://www.cnet.com/rss/news/",
    "https://www.techbargains.com/rss.xml",
    "https://slickdeals.net/newsearch.php?searchin=first&rss=1&sort=latest&forumid[]=9",
]

bot = Bot(token=BOT_TOKEN)
posted_links = set()
LOG_FILE = "bot_log.txt"

# === Мини-сервер Flask ===
app = Flask('')

@app.route('/')
def home():
    return "✅ SaleHunt Bot работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Логирование ===
def log_message(message: str):
    print(message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"❌ Ошибка записи в лог: {e}")

# === Основная логика проверки скидок ===
async def fetch_and_post_deals():
    print("🔵 Старт функции fetch_and_post_deals()")

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot успешно запущен и сразу публикует скидки!")
        log_message("✅ Бот стартовал и сразу публикует скидки.")
    except Exception as e:
        log_message(f"❌ Ошибка при отправке стартового сообщения: {e}")
        print(f"❌ Ошибка при отправке стартового сообщения: {e}")

    while True:
        print("🔄 Началась новая проверка скидок...")
        for feed_url in RSS_FEEDS:
            try:
                print(f"📥 Проверяю фид: {feed_url}")
                feed = feedparser.parse(feed_url, request_headers={'User-Agent': 'Mozilla/5.0 (compatible; SaleHuntBot/1.0)'})

                if feed.bozo:
                    raise Exception(feed.bozo_exception)

                if not feed.entries:
                    log_message(f"⚠️ Фид пустой: {feed_url}")
                    continue

                for entry in feed.entries:
                    link = entry.link
                    title = entry.title
                    image_url = ""

                    if 'media_content' in entry:
                        media = entry.media_content
                        if isinstance(media, list) and media:
                            image_url = media[0].get('url', '')
                        elif isinstance(media, dict):
                            image_url = media.get('url', '')

                    if link not in posted_links:
                        posted_links.add(link)

                        message_text = f"🔥 {title}"
                        button = InlineKeyboardButton("👉 Посмотреть", url=link)
                        markup = InlineKeyboardMarkup([[button]])

                        try:
                            if image_url:
                                await bot.send_photo(
                                    chat_id=CHANNEL_ID,
                                    photo=image_url,
                                    caption=message_text,
                                    reply_markup=markup,
                                    parse_mode='Markdown'
                                )
                            else:
                                await bot.send_message(
                                    chat_id=CHANNEL_ID,
                                    text=message_text,
                                    reply_markup=markup,
                                    parse_mode='Markdown',
                                    disable_web_page_preview=False
                                )

                            log_message(f"✅ Опубликована скидка: {title}")

                            # Пауза 1 минута между отправками
                            print("⏳ Пауза 60 секунд перед следующей отправкой...")
                            await asyncio.sleep(60)

                        except Exception as send_error:
                            log_message(f"❌ Ошибка отправки сообщения: {send_error}")

            except Exception as feed_error:
                log_message(f"❌ Ошибка загрузки фида: {feed_url} — {feed_error}")

        print("🟢 Проверка всех фидов завершена. Следующая через 1 минуту...")
        await asyncio.sleep(60)

# === Асинхронный запуск бота ===
async def main():
    await fetch_and_post_deals()

def start_asyncio_loop():
    asyncio.run(main())

# === Старт программы ===
if __name__ == "__main__":
    print("🚀 Бот запускается...")
    
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    bot_thread = Thread(target=start_asyncio_loop)
    bot_thread.start()
