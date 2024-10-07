import asyncio
import json

from hato_webhook.webhook import DiscordWebhook

async def main():
    webhook = DiscordWebhook()

    await webhook.login()
    with open('url_id.json', 'r') as f:
        url_id = json.load(f)
    tasks = [webhook.auto_tweet(x['webhook_url'], x['user_id']) for x in url_id]
    _ = await asyncio.gather(*tasks)