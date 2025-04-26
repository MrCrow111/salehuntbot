import feedparser
import time
import threading
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

# === SETTINGS ===
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

# Default SaleHunt Image
DEFAULT_IMAGE = "https://sdmntpritalynorth.oaiusercontent.com/files/00000000-1880-6246-a358-63d72dce9191/raw?se=2025-04-26T20%3A30%3A46Z&sp=r&sv=2024-08-04&sr=b&scid=0216e62e-be76-57bc-8714-2cf7c2291b14&skoid=cbbaa726-4a2e-4147-932c-56e6e553f073&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-04-26T16%3A47%3A43Z&ske=2025-04-27T16%3A47%3A43Z&sks=b&skv=2024-08-04&sig=RIAq69ozifY67Y%2BnMzjFebXmetR//lHWZ1pBsuCFzXg%3D"

bot = Bot(token=BOT_TOKEN)
posted_links = set()

# === Flask Mini Server ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ SaleHunt Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Function to Send Beautiful Post ===
def send_message(title, url, image_url=None):
    try:
        if not image_url:
            image_url = DEFAULT_IMAGE

        button = InlineKeyboardButton("👉 Check Deal", url=url)
        markup = InlineKeyboardMarkup([[button]])

        caption = (
            f"🔥 **NEW DEAL!**\n\n"
            f"🛍️ *{title}*\n\n"
            f"📎 Tap the button below to see more details!"
        )

        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=image_url,
            caption=caption,
            reply_markup=markup,
            parse_mode='Markdown'
        )

        print(f"✅ Posted: {title}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

# === Main Deals Fetching Logic ===
def fetch_and_post_deals():
    try:
        bot.send_message(chat_id=CHANNEL_ID, text="✅ SaleHunt Bot has started and is watching for hot deals!", parse_mode='Markdown')
        print("✅ Startup message sent.")
    except Exception as e:
        print(f"❌ Error sending startup message: {e}")

    while True:
        print("🔄 New round of deal checking started...")
        for feed_url in RSS_FEEDS:
            try:
                print(f"📥 Checking feed: {feed_url}")
                feed = feedparser.parse(feed_url)

                if not feed.entries:
                    print(f"⚠️ Feed is empty: {feed_url}")
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

                        time.sleep(60)  # Pause 1 minute between posts

            except Exception as feed_error:
                print(f"❌ Error processing feed {feed_url}: {feed_error}")

        print("🟢 Deal checking finished. Sleeping for 1 minute...")
        time.sleep(60)

# === Bot Startup ===
if __name__ == "__main__":
    print("🚀 Bot is starting...")

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    bot_thread = threading.Thread(target=fetch_and_post_deals)
    bot_thread.start()
