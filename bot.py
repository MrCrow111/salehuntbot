import feedparser
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from flask import Flask
from threading import Thread

# === НАСТРОЙКИ ===
BOT_TOKEN = "7758500745:AAGF3Vr0GLbQgk_XudSHGxZVbC33Spwtm3o"
CHANNEL_ID = -1002650552114
ADMIN_ID = 7039411923

RSS_FEEDS = [
    "https://www.techbargains.com/rss.xml",
    "https://www.dealnews.com/rss/dln/rss.html",
    "https://www.slickdeals.net/newsearch.php?searchin=first&rss=1&sort=latest",
    "https://www.hotukdeals.com/rss",
    "https://www.dealabs.com/rss",
    "https://www.mydealz.de/rss",
    "https://9to5toys.com/feed/",
    "https://www.kotaku.com.au/rss",
    "https://www.polygon.com/rss/index.xml",
    "https://www.bountii.com/rss",
]

KEYWORDS = []

bot = Bot(token=BOT_TOKEN)
posted_links = set()
LOG_FILE = "bot_log.txt"

def log_message(message: str):
    print(message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"❌ Ошибка записи в лог: {e}")

# === Мини-сервер Flask ===
app = Flask('')

@app.route('/')
def home():
    return "✅ SaleHunt Bot работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Тест подключения к Telegram API ===
async def check_telegram_connection():
    print("🔍 Проверка подключения к Telegram API...")
    try:
        me = await bot.get_me()
        print(f"✅ Бот подключен к Telegram как: @{me.username}")
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram API: {e}")

# === Основная логика ===
async def fetch_and_post_deals():
    print("🔵 Старт функции fetch_and_post_deals()")

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot успешно запущен и следит за скидками!")
        log_message("✅ Бот стартовал и отправил тестовое сообщение.")
    except Exception as e:
        log_message(f"❌ Ошибка при отправке стартового сообщения: {e}")
        print(f"❌ Ошибка при отправке стартового сообщения: {e}")
        return  # если ошибка — дальше не продолжаем

    first_run = True

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

                    if first_run:
                        posted_links.add(link)
                        continue

                    if link not in posted_links:
                        if KEYWORDS:
                            if not any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                                continue

                        posted_links.add(link)

                        message_text = f"🔥 {title}"
                        button = InlineKeyboardButton("👉 Перейти на сайт", url=link)
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

                        except Exception as send_error:
                            log_message(f"❌ Ошибка отправки сообщения: {send_error}")

            except Exception as feed_error:
                log_message(f"❌ Ошибка загрузки фида: {feed_url} — {feed_error}")

        first_run = False
        print("🟢 Проверка всех фидов завершена. Сплю 1 минуту...")
        await asyncio.sleep(60)

# === Асинхронный запуск бота ===
async def main():
    await check_telegram_connection()
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
