import time
import requests
import re

USER_ADDRESS = "0xdaa6a2cd4ba545befb3dbdc25d2b444c46873e62"

API_URL = f"https://data-api.polymarket.com/activity?user={USER_ADDRESS}&limit=10&offset=0"

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1413954774809972756/8PawR57XmF4uxm21UhnS1ZBuEf8f8KIw6ldJSf0AZzI1XlTCF9mmxAHB0MZ4wQ9c5o1J"

old_tx = None

def fetch_data(url):
    return requests.get(url).json()

def title_to_slug(title):
    return re.sub(r'[^a-z0-9 ]+', '', title.lower()).strip().replace(' ', '-')

def send_discord(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def process_trade(trade):
    title = trade['title']
    side = trade['side']
    outcome = trade['outcome']
    price = float(trade['price'])
    size = float(trade['size'])
    cost = price * size
    slug = trade['slug']
    url = f"https://polymarket.com/event/{title_to_slug(title)}/{slug}"

    msg = (
        f"📢 **Nbest55 Activity** 📢\n\n"
        f"🎯 {title}\n"
        f"👉 {side} {outcome}\n"
        f"💰 {size} shares @ {price*100:.2f}% (~{cost:.2f} USDC)\n"
        f"🔗 [Open Event]({url})"
    )
    send_discord(msg)

def main():
    global old_tx
    while True:
        try:
            data = fetch_data(API_URL)
            if data and isinstance(data, list):
                latest = data[0]
                tx = latest['transactionHash']
                if tx != old_tx and latest['type'] == 'TRADE':
                    process_trade(latest)
                    old_tx = tx
        except Exception as e:
            print("Error:", e)
        time.sleep(5)

if __name__ == "__main__":
    main()
