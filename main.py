# -*- coding: utf-8 -*-

# Ensure the required libraries are installed before running this script:
# pip install python-telegram-bot requests python-dotenv

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
POLL_INTERVAL = 60  # seconds

bot = Bot(token=TELEGRAM_BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Telegram bot is connected!")


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

last_tweet_id = None

while True:
    url = (
        f"https://api.twitter.com/2/users/{user_id}/tweets"
        f"?max_results=5&tweet.fields=created_at,attachments,referenced_tweets"
        f"&expansions=attachments.media_keys"
        f"&media.fields=url,preview_image_url,type"
    )

    res = requests.get(url, headers=HEADERS)
    tweets = res.json().get("data", [])
    media = {m["media_key"]: m for m in res.json().get("includes", {}).get("media", [])}

    if tweets:
        latest = tweets[0]

        # Skip replies
        if any(ref.get("type") == "replied_to" for ref in latest.get("referenced_tweets", [])):
            print("⏩ Skipped reply")
            time.sleep(POLL_INTERVAL)
            continue

        tweet_id = latest["id"]
        tweet_text = latest["text"]
        tweet_url = f"https://x.com/{TWITTER_USERNAME}/status/{tweet_id}"

        if tweet_id != last_tweet_id:
            message = (
                f"🔊 New tweet from @{TWITTER_USERNAME}:\n\n"
                f"{tweet_text}\n\n"
                f"🔗 {tweet_url}"
            )

            media_sent = False

            if "attachments" in latest and "media_keys" in latest["attachments"]:
                for key in latest["attachments"]["media_keys"]:
                    media_item = media.get(key)
                    if media_item:
                        if media_item["type"] == "photo":
                            image_url = media_item.get("url") or media_item.get("preview_image_url")
                            if image_url:
                                bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image_url, caption=message)
                                media_sent = True
                                break
                        elif media_item["type"] in ["video", "animated_gif"]:
                            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message + "\n🎥 Video/GIF (see tweet)")
                            media_sent = True
                            break

            if not media_sent:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

            last_tweet_id = tweet_id

    time.sleep(POLL_INTERVAL)
