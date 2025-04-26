import feedparser
import time
import threading
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

# === НАСТРОЙКИ ===
BOT_TOKEN = "7758500745:AAGF3Vr0GLbQgk_XudSHGxZVbC33Spwtm3o"
CHANNEL_ID = -1002650552114

RSS_FEEDS = [
    "https://9to5toys.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.engadget.com/rss.xml",
    "https://www.wired.com/feed/rss",
    "https://www.cnet.com/rss/news/",
    "https://www.techbargains.com/rss.xml",
    "https://slickdeals.net/newsearch.php?searchin=first&rss=1&sort=latest&forumid[]=9",
]

# Запасная картинка SaleHunt
DEFAULT_IMAGE = "https://sdmntpritalynorth.oaiusercontent.com/files/00000000-1880-6246-a358-63d72dce9191/raw?se=2025-04-26T20%3A30%3A46Z&sp=r&sv=2024-08-04&sr=b&scid=0216e62e-be76-57bc-8714-2cf7c2291b14&skoid=cbbaa726-4a2e-4147-932c-56e6e553f073&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-04-26T16%3A47%3A43Z&ske=2025-04-27T16%3A47%3A43Z&sks=b&skv=2024-08-04&sig=RIAq69ozifY67Y%2BnMzjFebXmetR//lHWZ1pBsuCFzXg%3D"

bot = Bot(token=BOT_TOKEN)
posted_links = set()

# === Мини-сервер Flask ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SaleHunt Bot работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Функция отправки красивого сообщения ===
def send_message(title, url, image_url=None):
    try:
        if not image_url:
            image_url = DEFAULT_IMAGE

        button = InlineKeyboardButton("👉 Перейти к скидке", url=url)
        markup = InlineKeyboardMarkup([[button]])

        caption = (
            f"🔥 **НОВАЯ СКИДКА!**\n\n"
            f"🛍️ *{title}*\n\n"
            f"📎 Нажми кнопку ниже, чтобы узнать подробности!"
        )

        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=image_url,
            caption=caption,
            reply_markup=markup,
            parse_mode='Markdown'
        )

        print(f"✅ Опубликовано: {title}")
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}")

# === Основная логика проверки скидок ===
def fetch_and_post_deals():
    try:
        bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot запущен и начинает публикацию лучших скидок!", parse_mode='Markdown')
        print("✅ Стартовое сообщение отправлено.")
    except Exception as e:
        print(f"❌ Ошибка отправки стартового сообщения: {e}")

    while True:
        print("🔄 Началась проверка скидок...")
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
                    image_url = None

                    if 'media_content' in entry:
                        media = entry.media_content
                        if isinstance(media, list) and media:
                            image_url = media[0].get('url', '')
                        elif isinstance(media, dict):
                            image_url = media.get('url', '')

                    if link not in posted_links:
                        posted_links.add(link)

                        send_message(title=title, url=link, image_url=image_url)

                        time.sleep(60)  # Пауза 1 минута между отправками

            except Exception as feed_error:
                print(f"❌ Ошибка обработки фида {feed_url}: {feed_error}")

        print("🟢 Проверка завершена. Сплю 1 минуту...")
        time.sleep(60)

# === Старт бота ===
if __name__ == "__main__":
    print("🚀 Бот запускается...")

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    bot_thread = threading.Thread(target=fetch_and_post_deals)
    bot_thread.start()
