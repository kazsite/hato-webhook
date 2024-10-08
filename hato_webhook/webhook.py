import asyncio
import random
import json
from io import StringIO
from pathlib import Path

import requests
from twikit import Client

class Xlyzer:
    def __init__(self):
        self._client = Client(language='ja-jp',
                              user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.3')
    
    async def login(self, fname_login: str, fname_cookie: str) -> None:
        fpath = Path(f'token')
        if not (fpath / fname_cookie).exists():
            with open(fpath / fname_login, 'r') as f:
                login_info = json.load(f)
            await self._client.login(auth_info_1=login_info['userid'],
                                auth_info_2=login_info['mail'],
                                password=login_info['password'])
            self._client.save_cookies(fpath / fname_cookie)
        else:
            self._client.load_cookies(fpath / fname_cookie)
    
    async def get_active_latest_tweet_url(self, user_id: str) -> str:
        tweet = (await self._client.get_user_tweets(user_id, tweet_type='Tweets', count=1))[0]
        tweet_id = tweet.id
        screen_name = (await self._client.get_user_by_id(user_id)).screen_name
        if not f'RT @{screen_name}:' in tweet.text:
            url = f'https://fxtwitter.com/{screen_name}/status/{tweet_id}'
            return tweet_id, url
        else:
            return None

class DiscordWebhook(Xlyzer):
    def __init__(self):
        super().__init__()
    
    async def auto_tweet(self, webhook_url: str, user_id: str):
        with StringIO() as sio:
            while True:
                try:
                    tweet_id, url = await super().get_active_latest_tweet_url(user_id)
                except Exception as e:
                    print(e)
                if not tweet_id == sio.getvalue():
                    sio.write(tweet_id)
                    sio.seek(0)
                    self.send_discord_messages(webhook_url, message=url)
                else:
                    pass
                await asyncio.sleep(random.uniform(45.5, 83.7))

    def send_discord_messages(self, webhook_url: str, message: str):
        data = {
            "content": message
        }
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print(f"Message sent successfully.\n  message: {message}")
        else:
            print(f"Failed to send message.\n  message: {message}")