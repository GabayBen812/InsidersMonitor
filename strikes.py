import time
import requests
import re
import json
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo  # py>=3.9
except Exception:
    ZoneInfo = None

DATA_FILE = "data.json"

USERS = {
    "Tyrone - DigitalPost (ALT)": {
    "api": "https://data-api.polymarket.com/activity?user=0x80cabdce3dd662f94d410e23152ee2fd66df2bf7&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 100
    },
    "Tyrone - JubileeSun (ALT)": {
    "api": "https://data-api.polymarket.com/activity?user=0xc9762a84234edd08592cbba44bf8fd6943520ad5&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": False,
    "min_dollar_amount": 50
    },
    "Tyrone - PastaPizza (Main)": {
    "api": "https://data-api.polymarket.com/activity?user=0xec0bc5b9d6f9cf4e88706d1e3efe333c6ee669e6&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 50
    },
    "Tyrone - Lovecountry (ALT)": {
    "api": "https://data-api.polymarket.com/activity?user=0xc18f1a8fc24eb3cfc424ffb2405348d532e9605a&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": False,
    "min_dollar_amount": 50
    },
    "Tyrone - 0XdAF (ALT)": {
    "api": "https://data-api.polymarket.com/activity?user=0xdaf51a2383f994537f851e5827fbab20d597661d&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 100
    },
    "BAdiosB - Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0x909fa9f89976058b8b3ab87adc502ec7415ea8c3&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 10
    },
    "9TungSahur - Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0x6c2c072a0aa8fb8b4faf9aecae5520541f3b2d2a&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 0
    },
    "ricosuave666 - Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0x0afc7ce56285bde1fbe3a75efaffdfc86d6530b2&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 0
    },
    "PorcoRosso - Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0xd5de5cad9ef22b16317fe30a4234c72ece3eac1a&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 0
    },
    "KoolAid - Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0x711cf2d57de4c9aa53dd2c0bff3a2bf818688495&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 100
    },
    "Violet-Vinyl - Strike Markets Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0x9eb1f9602242b2218f55275fbab16e7eb239fc21&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 50
    },
    "Dumbeldor2003 - IDF Insider": {
    "api": "https://data-api.polymarket.com/activity?user=0x31646fb225a7743287e760e44923345644513033&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 50
    },
}


old_tx = {user: None for user in USERS}
my_holdings = set()


def load_insider_data():
    """Load insider data (bios and serial IDs) from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"insiders": {}, "next_serial_id": 1}


def get_insider_info(user_name):
    """Get serial ID and bio for an insider"""
    data = load_insider_data()
    if user_name in data.get("insiders", {}):
        insider = data["insiders"][user_name]
        return insider.get("serial_id", "?"), insider.get("bio", {})
    return None, {}


def format_bio(bio):
    """Format bio information for display"""
    if not bio or all(v in ["Not set", "No additional notes"] for v in bio.values()):
        return ""
    
    parts = []
    if bio.get("trading_style") and bio["trading_style"] != "Not set":
        parts.append(f"**Style**: {bio['trading_style']}")
    if bio.get("hit_rate") and bio["hit_rate"] != "Not set":
        parts.append(f"**Hit Rate**: {bio['hit_rate']}")
    if bio.get("main_markets") and bio["main_markets"] != "Not set":
        parts.append(f"**Markets**: {bio['main_markets']}")
    if bio.get("notes") and bio["notes"] != "No additional notes":
        parts.append(f"**Notes**: {bio['notes']}")
    
    if parts:
        return "\n\n📊 **Insider Bio**\n" + "\n".join(parts)
    return ""


def fetch_data(url):
    return requests.get(url).json()


def title_to_slug(title):
    return re.sub(r'[^a-z0-9 ]+', '', title.lower()).strip().replace(' ', '-')


def send_discord(webhook, msg):
    requests.post(webhook, json={"content": msg})


def extract_trade_epoch_and_local(trade, tz="Asia/Jerusalem"):
    """
    מחזיר (epoch_sec:int, local_str:str)
    מנסה שדות זמן נפוצים ומפרש גם epoch וגם ISO8601.
    """
    candidates = ["timestamp", "blockTimestamp", "block_time", "time", "createdAt", "created_at"]
    val = None
    for k in candidates:
        if k in trade and trade[k]:
            val = trade[k]
            break
    if val is None:
        # fallback: עכשיו (לא מומלץ, אבל לא יפיל)
        now = int(datetime.now(tz=timezone.utc).timestamp())
        return now, "unknown"

    # parse to epoch seconds
    epoch = None
    if isinstance(val, (int, float)):
        epoch = int(val / 1000) if val > 1e12 else int(val)
    elif isinstance(val, str):
        s = val.strip()
        if s.isdigit():
            n = int(s)
            epoch = int(n / 1000) if n > 1e12 else n
        else:
            # ISO8601
            try:
                iso = s.replace("Z", "+00:00")
                dt = datetime.fromisoformat(iso)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                epoch = int(dt.timestamp())
            except Exception:
                # אם נכשל – ניפול ל-now
                epoch = int(datetime.now(tz=timezone.utc).timestamp())

    # בונים מחרוזת מקומית יפה (אופציונלי בנוסף ל־<t:...>)
    try:
        tzinfo = ZoneInfo(tz) if ZoneInfo else timezone.utc
        local_dt = datetime.fromtimestamp(epoch, tz=tzinfo)
        local_str = local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        local_str = "unknown"

    return epoch, local_str



def process_trade(user, trade):
    title = trade['title']
    side = trade['side']
    outcome = trade['outcome']
    price = float(trade['price'])
    size = float(trade['size'])
    cost = price * size
    slug = trade['slug']
    url = f"https://polymarket.com/event/{title_to_slug(title)}/{slug}"

    # Check minimum dollar amount filter
    min_dollar_amount = USERS[user].get('min_dollar_amount', 0)
    if cost < min_dollar_amount:
        return  # Skip sending to Discord if cost is below minimum

    ts_epoch, ts_local = extract_trade_epoch_and_local(trade)

    # Check if we should tag @everyone
    should_tag = USERS[user].get('tag', False)
    tag_prefix = "@everyone\n\n" if should_tag else ""

    # Get serial ID and bio
    serial_id, bio = get_insider_info(user)
    serial_display = f"🆔 **ID**: #{serial_id}\n" if serial_id else ""
    bio_display = format_bio(bio)

    msg = (
        f"{tag_prefix}**{user} Trade Detected**\n\n"
        f"{serial_display}"
        f"**Title**: {title}\n"
        f"**Slug**: {slug}\n"
        f"**Side**: {side}\n"
        f"**Outcome**: {outcome}\n"
        f"**Price**: {price * 100:.2f}%\n"
        f"**Shares**: {size}\n"
        f"**Cost**: {cost:.2f} USDC\n"
        f"🕒 **Executed**: <t:{ts_epoch}:f> (<t:{ts_epoch}:R>) — {ts_local}\n"
        f"🔗 [Open Event]({url})"
        f"{bio_display}"
    )
    send_discord(USERS[user]['webhook'], msg)


def main():
    while True:
        for user, config in USERS.items():
            try:
                data = fetch_data(config['api'])
                if data and isinstance(data, list):
                    latest = data[0]
                    tx = latest['transactionHash']
                    if tx != old_tx[user] and latest['type'] == 'TRADE':
                        process_trade(user, latest)
                        old_tx[user] = tx
            except Exception as e:
                print(f"Error fetching {user}:", e)
        time.sleep(5)


if __name__ == "__main__":
    main()
