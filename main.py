import os
import requests
import time
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_USERNAME = "rivxlabs"
POLL_INTERVAL = 60

bot = Bot(token=TELEGRAM_BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print("Twitter API Error:", res.status_code, res.text)
        return None
    data = res.json().get("data")
    return data["id"] if data else None

user_id = get_user_id(TWITTER_USERNAME)
if not user_id:
    print("Bot stopped: Could not fetch user ID")
    exit()

bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Telegram bot is connected!")  # test msg
exit()
