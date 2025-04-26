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

bot = Bot(token=BOT_TOKEN)
posted_links = set()

# === Мини-сервер Flask ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SaleHunt Bot работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Функция отправки сообщений ===
def send_message(text, url=None, image=None):
    try:
        if url:
            button = InlineKeyboardButton("👉 Перейти", url=url)
            markup = InlineKeyboardMarkup([[button]])
        else:
            markup = None

        if image:
            bot.send_photo(chat_id=CHANNEL_ID, photo=image, caption=text, reply_markup=markup)
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview=False)

        print(f"✅ Отправлено: {text}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# === Основная логика проверки скидок ===
def fetch_and_post_deals():
    try:
        bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot успешно запущен и работает!", parse_mode='Markdown')
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

                        send_message(text=message_text, url=link, image=image_url)

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
