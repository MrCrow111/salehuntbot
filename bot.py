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
    "https://slickdeals.net/newsearch.php?searchin=first&rss=1&sort=popularity&filter=Amazon",
    "https://slickdeals.net/newsearch.php?searchin=first&rss=1&sort=popularity",
    "https://www.dealnews.com/rss/dln/rss.html",
    "https://www.techbargains.com/rss.xml",
    "https://www.walmart.com/cp/rss/1085666",
    "https://www.bestbuy.com/site/electronics/top-deals/pcmcat1563300794084.c?id=pcmcat1563300794084&rss=true",
    "https://www.hotukdeals.com/tag/amazon.rss",
    "https://www.hotukdeals.com/rss",
    "https://www.dealabs.com/groupe/amazon.rss",
    "https://www.dealabs.com/rss",
    "https://www.mydealz.de/groupe/amazon.rss",
    "https://www.mydealz.de/rss",
    "https://www.aliexpress.com/rss/new-arrivals.xml",
]

KEYWORDS = []  # Фильтрация отключена

bot = Bot(token=BOT_TOKEN)
posted_links = set()

# === Flask-сервер для Render ===
app = Flask('')

@app.route('/')
def home():
    return "✅ SaleHunt Bot работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Основная логика бота ===
async def fetch_and_post_deals():
    print("🔵 Старт функции fetch_and_post_deals()")
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot успешно запущен и следит за скидками!")
        print("✅ Тестовое сообщение успешно отправлено в канал.")
    except Exception as test_error:
        print(f"❌ Ошибка при отправке тестового сообщения: {test_error}")
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Ошибка старта:\n\n{test_error}")
        except Exception as notify_error:
            print(f"❌ Ошибка при отправке уведомления админу: {notify_error}")

    first_run = True

    while True:
        print("🔄 Началась новая проверка скидок...")
        for feed_url in RSS_FEEDS:
            try:
                print(f"📥 Проверяю фид: {feed_url}")
                feed = feedparser.parse(feed_url)
                if not feed.entries:
                    print(f"⚠️ Фид пустой: {feed_url}")
                    continue

                for entry in feed.entries:
                    link = entry.link
                    title = entry.title
                    image_url = ""

                    # Достаём картинку если есть
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

                            print(f"✅ Опубликована скидка: {title}")

                        except Exception as send_error:
                            print(f"❌ Ошибка отправки сообщения: {send_error}")
                            try:
                                await bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Ошибка отправки сообщения:\n\n{send_error}")
                            except Exception as notify_error:
                                print(f"❌ Ошибка при отправке уведомления админу: {notify_error}")

            except Exception as feed_error:
                print(f"❌ Ошибка загрузки фида {feed_url}: {feed_error}")
                try:
                    await bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Ошибка загрузки фида:\n\n{feed_error}")
                except Exception as notify_error:
                    print(f"❌ Ошибка при отправке уведомления админу: {notify_error}")

        first_run = False
        print("🟢 Проверка всех фидов завершена. Сплю 1 минуту...")
        await asyncio.sleep(60)

# === Старт бота и сервера ===
def start_bot():
    print("🔵 Старт нового event loop для бота")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_and_post_deals())

if __name__ == "__main__":
    print("🚀 Бот запускается...")

    # Стартуем Flask-сервер
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Стартуем бота в отдельном потоке с правильным event loop
    bot_thread = Thread(target=start_bot)
    bot_thread.start()