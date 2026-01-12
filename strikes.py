import time
import requests
import re
import json
import sys
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo  # py>=3.9
except Exception:
    ZoneInfo = None

# Force unbuffered output for systemd/journalctl
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except:
        pass

# Helper function for immediate output flushing
def log(msg, flush=True):
    """Print with automatic flushing for systemd compatibility"""
    print(msg, flush=flush)

DATA_FILE = "data.json"

# Load USERS from Supabase or local storage
def load_users():
    """Load users from Supabase or local storage"""
    try:
        from supabase_storage import load_insiders_from_supabase
        users = load_insiders_from_supabase()
        if users:
            log(f"✅ Loaded {len(users)} insiders from database")
            # Debug: print first few user names
            if users:
                user_names = list(users.keys())[:3]
                log(f"   Sample: {', '.join(user_names)}")
            return users
    except Exception as e:
        log(f"⚠️  Could not load from Supabase: {e}")
        import traceback
        traceback.print_exc()
        log("   Falling back to hardcoded USERS dict")
    
    # Fallback to hardcoded dict (defined below)
    return _FALLBACK_USERS

# Fallback users dict (used if Supabase/local storage fails)
_FALLBACK_USERS = {
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
    "Rico - AugsburgFClover": {
    "api": "https://data-api.polymarket.com/activity?user=0x509cd9d117e06a082df649a06e317195f048240a&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 1
    },
    "Rico - Alt (metushelah)": {
    "api": "https://data-api.polymarket.com/activity?user=0x4e74acf9447df43029fedc1fe592775110de6a9f&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 1
    },
    "Rico - Alt (ddinhouse)": {
    "api": "https://data-api.polymarket.com/activity?user=0x03727dd8df63b9aaedebb30db24a7f07522fa86b&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 1
    },
    "Rico - Alt (Roimeo5)": {
    "api": "https://data-api.polymarket.com/activity?user=0xe03e96656bb81d7079a3a84694b7a4a73bb7f375&limit=10&offset=0",
    "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
    "min_price": 0,
    "max_price": 1,
    "tag": True,
    "min_dollar_amount": 1
    },
}

# Note: load_users() is defined above, this is just the fallback dict
_FALLBACK_USERS = {
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
        "Rico - AugsburgFClover": {
        "api": "https://data-api.polymarket.com/activity?user=0x509cd9d117e06a082df649a06e317195f048240a&limit=10&offset=0",
        "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
        "min_price": 0,
        "max_price": 1,
        "tag": True,
        "min_dollar_amount": 1
        },
        "Rico - Alt (metushelah)": {
        "api": "https://data-api.polymarket.com/activity?user=0x4e74acf9447df43029fedc1fe592775110de6a9f&limit=10&offset=0",
        "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
        "min_price": 0,
        "max_price": 1,
        "tag": True,
        "min_dollar_amount": 1
        },
        "Rico - Alt (ddinhouse)": {
        "api": "https://data-api.polymarket.com/activity?user=0x03727dd8df63b9aaedebb30db24a7f07522fa86b&limit=10&offset=0",
        "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
        "min_price": 0,
        "max_price": 1,
        "tag": True,
        "min_dollar_amount": 1
        },
        "Rico - Alt (Roimeo5)": {
        "api": "https://data-api.polymarket.com/activity?user=0xe03e96656bb81d7079a3a84694b7a4a73bb7f375&limit=10&offset=0",
        "webhook": "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk",
        "min_price": 0,
        "max_price": 1,
        "tag": True,
        "min_dollar_amount": 1
        },
    }

USERS = load_users()

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
    """Get serial ID and bio for an insider - tries Supabase first, then local data.json"""
    # Try Supabase first
    try:
        from supabase_storage import load_bio_data_from_supabase
        supabase_data = load_bio_data_from_supabase()
        if user_name in supabase_data.get("insiders", {}):
            insider = supabase_data["insiders"][user_name]
            return insider.get("serial_id"), insider.get("bio", {})
    except Exception as e:
        print(f"⚠️  Could not load bio from Supabase: {e}")
    
    # Fallback to local data.json
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


def fetch_data(url, timeout=10):
    """Fetch data from API with error handling"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.Timeout:
        log(f"⚠️  API timeout for {url[:50]}...")
        return None
    except requests.exceptions.RequestException as e:
        log(f"⚠️  API error: {e}")
        return None
    except ValueError as e:  # JSON decode error
        log(f"⚠️  Invalid JSON response: {e}")
        return None


def title_to_slug(title):
    return re.sub(r'[^a-z0-9 ]+', '', title.lower()).strip().replace(' ', '-')


def send_discord(webhook, msg_or_embed):
    """Send message to Discord webhook - supports both plain text and embeds"""
    try:
        if isinstance(msg_or_embed, dict) and "embeds" in msg_or_embed:
            # It's an embed payload
            requests.post(webhook, json=msg_or_embed, timeout=10)
        else:
            # Plain text message
            requests.post(webhook, json={"content": msg_or_embed}, timeout=10)
    except Exception as e:
        log(f"⚠️  Discord webhook error: {e}")

def send_startup_notification(users_dict, initialized_count, total_count):
    """Send a nice startup notification to Discord"""
    # Get the first webhook from any user (or use a default)
    webhook = None
    for user, config in users_dict.items():
        if config.get('webhook'):
            webhook = config['webhook']
            break
    
    if not webhook:
        log("⚠️  No webhook found for startup notification")
        return
    
    # Get list of insider names (first 10)
    insider_names = list(users_dict.keys())[:10]
    names_text = "\n".join([f"• {name}" for name in insider_names])
    if len(users_dict) > 10:
        names_text += f"\n• ... and {len(users_dict) - 10} more"
    
    # Create embed
    embed = {
        "embeds": [{
            "title": "🚀 Insider Monitor Started",
            "description": f"Successfully initialized and monitoring **{total_count} insiders**",
            "color": 0x00ff00,  # Green
            "fields": [
                {
                    "name": "📊 Status",
                    "value": f"**{initialized_count}/{total_count}** insiders initialized\n✅ Ready to monitor trades",
                    "inline": True
                },
                {
                    "name": "⏰ Monitoring",
                    "value": "Checking for new trades every 5 seconds",
                    "inline": True
                },
                {
                    "name": "👥 Tracked Insiders",
                    "value": names_text[:1024],  # Discord field limit
                    "inline": False
                }
            ],
            "footer": {
                "text": "Insider Monitor v2.0"
            },
            "timestamp": datetime.now(tz=timezone.utc).isoformat()
        }]
    }
    
    try:
        send_discord(webhook, embed)
        log("📤 Sent startup notification to Discord")
    except Exception as e:
        log(f"⚠️  Failed to send startup notification: {e}")

def send_keepalive_notification(users_dict):
    """Send a daily keepalive notification to confirm the script is running"""
    # Get the first webhook from any user
    webhook = None
    for user, config in users_dict.items():
        if config.get('webhook'):
            webhook = config['webhook']
            break
    
    if not webhook:
        return
    
    # Count active insiders
    total_count = len(users_dict)
    now = datetime.now(tz=timezone.utc)
    
    # Create embed
    embed = {
        "embeds": [{
            "title": "💚 Keepalive - Monitor Running",
            "description": f"Insider Monitor is active and monitoring **{total_count} insiders**",
            "color": 0x00ff00,  # Green
            "fields": [
                {
                    "name": "📊 Status",
                    "value": "✅ All systems operational\n🔄 Monitoring active",
                    "inline": True
                },
                {
                    "name": "⏰ Time",
                    "value": f"<t:{int(now.timestamp())}:F>\nDaily check-in",
                    "inline": True
                },
                {
                    "name": "📈 Activity",
                    "value": f"Monitoring **{total_count} insiders**\nChecking every 5 seconds",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Insider Monitor - Daily Keepalive"
            },
            "timestamp": now.isoformat()
        }]
    }
    
    try:
        send_discord(webhook, embed)
        log("📤 Sent daily keepalive notification to Discord")
    except Exception as e:
        log(f"⚠️  Failed to send keepalive notification: {e}")

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

    # Get serial ID and bio
    serial_id, bio = get_insider_info(user)
    
    # Determine embed color based on side
    embed_color = 0x00ff00 if side.upper() == "BUY" else 0xff0000  # Green for BUY, Red for SELL
    
    # Build embed
    embed = {
        "embeds": [{
            "title": f"💰 {user}",
            "description": title,
            "url": url,
            "color": embed_color,
            "fields": [
                {
                    "name": "📊 Trade Details",
                    "value": f"**Side**: {side}\n**Outcome**: {outcome}\n**Price**: {price * 100:.2f}%\n**Size**: {size:,.2f} shares",
                    "inline": True
                },
                {
                    "name": "💵 Cost",
                    "value": f"**{cost:,.2f} USDC**",
                    "inline": True
                },
                {
                    "name": "🕒 Executed",
                    "value": f"<t:{ts_epoch}:R>\n<t:{ts_epoch}:f>",
                    "inline": True
                }
            ],
            "footer": {
                "text": f"ID: #{serial_id}" if serial_id else "Insider Monitor"
            },
            "timestamp": datetime.fromtimestamp(ts_epoch, tz=timezone.utc).isoformat()
        }]
    }
    
    # Add bio information if available
    if bio and any(v not in ["Not set", "No additional notes"] for v in bio.values()):
        bio_fields = []
        if bio.get("trading_style") and bio["trading_style"] != "Not set":
            bio_fields.append(f"**Style**: {bio['trading_style']}")
        if bio.get("hit_rate") and bio["hit_rate"] != "Not set":
            bio_fields.append(f"**Hit Rate**: {bio['hit_rate']}")
        if bio.get("main_markets") and bio["main_markets"] != "Not set":
            bio_fields.append(f"**Markets**: {bio['main_markets']}")
        
        if bio_fields:
            embed["embeds"][0]["fields"].append({
                "name": "📈 Insider Profile",
                "value": "\n".join(bio_fields),
                "inline": False
            })
        
        # Add notes if available
        if bio.get("notes") and bio["notes"] != "No additional notes":
            embed["embeds"][0]["fields"].append({
                "name": "📝 Notes",
                "value": bio["notes"][:500],  # Limit length
                "inline": False
            })
    
    # Prepare payload
    payload = embed
    
    # Add @everyone mention if needed
    should_tag = USERS[user].get('tag', False)
    if should_tag:
        payload["content"] = "@everyone"
    
    webhook_url = USERS[user].get('webhook')
    if not webhook_url:
        print(f"❌ No webhook configured for {user}", flush=True)
        return
    
    try:
        send_discord(webhook_url, payload)
        print(f"📤 Sent notification for {user} trade")
    except Exception as e:
        print(f"❌ Failed to send Discord message for {user}: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error in process_trade for {user}: {e}")
        import traceback
        traceback.print_exc()


def main():
    global USERS, old_tx
    reload_counter = 0
    RELOAD_INTERVAL = 60  # Reload users every 60 iterations (5 minutes)
    iteration_count = 0
    last_keepalive_date = None  # Track last date keepalive was sent
    
    log(f"🚀 Starting monitor for {len(USERS)} insiders...")
    log(f"📋 Tracking: {', '.join(list(USERS.keys())[:5])}{'...' if len(USERS) > 5 else ''}")
    log(f"⏰ Checking for new trades every 5 seconds...\n")
    
    # Initialize old_tx with None for all users (will process latest trade on first run)
    log(f"🔧 Initializing tracking for {len(USERS)} insiders...")
    
    # Initialize baseline transaction hashes BEFORE entering main loop
    # This ensures we have a baseline even if API calls fail
    for user, config in USERS.items():
        if user not in old_tx:
            old_tx[user] = None
            try:
                # Try to get the latest trade to set as baseline
                data = fetch_data(config['api'])
                if data and isinstance(data, list) and len(data) > 0:
                    latest = data[0]
                    if latest.get('type') == 'TRADE':
                        tx = latest.get('transactionHash')
                        if tx:
                            old_tx[user] = tx
                            log(f"📌 Initialized tracking for {user} (baseline tx: {tx[:10]}...)")
                        else:
                            log(f"⚠️  No transactionHash for {user} - will retry in main loop")
                    else:
                        log(f"⚠️  Latest activity for {user} is {latest.get('type')}, not TRADE - will retry in main loop")
                else:
                    log(f"⚠️  No data returned for {user} - will retry in main loop")
            except Exception as e:
                log(f"⚠️  Error initializing {user}: {e} - will retry in main loop")
    
    # Summary: Count how many insiders were successfully initialized
    initialized_count = sum(1 for tx in old_tx.values() if tx is not None)
    total_count = len(old_tx)
    log(f"📊 Initialization complete: {initialized_count}/{total_count} insiders have baseline transactions")
    if initialized_count < total_count:
        log(f"   (The remaining {total_count - initialized_count} will be initialized when their API returns data)")
    
    # Send startup notification to Discord
    send_startup_notification(USERS, initialized_count, total_count)
    
    log(f"✅ Ready to monitor! Starting main loop...\n")
    
    while True:
        iteration_count += 1
        # Periodically reload users from database to pick up new insiders
        reload_counter += 1
        if reload_counter >= RELOAD_INTERVAL:
            try:
                new_users = load_users()
                # Add new users to old_tx tracking
                for user in new_users:
                    if user not in old_tx:
                        old_tx[user] = None
                        print(f"✅ New insider detected: {user}")
                # Remove users that were deleted
                removed_users = set(USERS.keys()) - set(new_users.keys())
                for user in removed_users:
                    if user in old_tx:
                        del old_tx[user]
                        print(f"⚠️  Insider removed: {user}")
                USERS = new_users
                reload_counter = 0
            except Exception as e:
                print(f"⚠️  Error reloading users: {e}")
        
        iteration_start = time.time()
        checked_count = 0
        for user, config in USERS.items():
            try:
                data = fetch_data(config['api'])
                if not data:
                    # Only log this occasionally to avoid spam
                    if iteration_count % 12 == 0:
                        print(f"⚠️  No data returned for {user}", flush=True)
                    continue
                    
                if not isinstance(data, list):
                    print(f"⚠️  Unexpected data format for {user}: {type(data)}", flush=True)
                    continue
                
                if len(data) == 0:
                    # Only log this occasionally to avoid spam
                    if iteration_count % 12 == 0:
                        print(f"⚠️  Empty data array for {user}", flush=True)
                    continue
                
                latest = data[0]
                
                # Check if it's a trade
                activity_type = latest.get('type')
                if activity_type != 'TRADE':
                    # Silently skip non-trade activities (but log occasionally for debugging)
                    if iteration_count % 24 == 0 and checked_count == 0:
                        print(f"ℹ️  Latest activity for {user} is {activity_type}, not TRADE")
                    continue
                
                tx = latest.get('transactionHash')
                if not tx:
                    print(f"⚠️  No transactionHash for {user}")
                    continue
                
                checked_count += 1
                
                # Check if this is a new trade
                if old_tx.get(user) is None:
                    # First time seeing this user - set the hash as baseline (don't process old trades on startup)
                    old_tx[user] = tx
                    print(f"📌 Initialized tracking for {user} (baseline tx: {tx[:10]}...)")
                    continue
                
                if tx != old_tx[user]:
                    print(f"🆕 New trade detected for {user}: {tx[:10]}... (was: {old_tx[user][:10] if old_tx[user] else 'None'}...)")
                    try:
                        process_trade(user, latest)
                        old_tx[user] = tx
                        print(f"✅ Trade processed and sent for {user}")
                    except Exception as e:
                        print(f"❌ Error processing trade for {user}: {e}")
                        import traceback
                        traceback.print_exc()
                # else: same trade, no action needed (this is normal - waiting for new trades)
                    
            except KeyError as e:
                print(f"❌ Missing key in data for {user}: {e}")
            except Exception as e:
                print(f"❌ Error fetching {user}: {e}")
                import traceback
                traceback.print_exc()
        
        # Log iteration summary every 12 iterations (1 minute)
        if iteration_count % 12 == 0:
            elapsed = time.time() - iteration_start
            log(f"🔄 Iteration {iteration_count}: Checked {checked_count} insiders in {elapsed:.2f}s")
            log(f"   Still monitoring for new trades... (baseline hashes set for all insiders)\n")
        
        # Daily keepalive notification at 16:00 (4 PM)
        now = datetime.now(tz=timezone.utc)
        current_hour = now.hour
        current_date = now.date()
        
        # Check if it's 16:00 (4 PM) and we haven't sent keepalive today
        if current_hour == 16 and last_keepalive_date != current_date:
            send_keepalive_notification(USERS)
            last_keepalive_date = current_date
        
        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n⚠️  Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        log(f"\n❌ Fatal error in main(): {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
