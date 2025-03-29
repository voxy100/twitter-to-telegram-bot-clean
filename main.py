import os
import requests
import time
import telegram
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_USERNAME = 'rivxlabs'
POLL_INTERVAL = 60  # seconds

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
HEADERS = {'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}'}

def get_user_id(username):
    url = f'https://api.twitter.com/2/users/by/username/{username}'
    res = requests.get(url, headers=HEADERS)
    return res.json()['data']['id']

user_id = get_user_id(TWITTER_USERNAME)
last_tweet_id = None

while True:
    url = f'https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at'
    res = requests.get(url, headers=HEADERS)
    tweets = res.json().get('data', [])

    if tweets:
        latest = tweets[0]
        tweet_id = latest['id']
        tweet_text = latest['text']

        if tweet_id != last_tweet_id:
            tweet_url = f"https://x.com/{TWITTER_USERNAME}/status/{tweet_id}"
            message = f"🚨 New tweet from @{TWITTER_USERNAME}:
\n{tweet_text}\n\n🔗 {tweet_url}"
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            last_tweet_id = tweet_id

    time.sleep(POLL_INTERVAL)
