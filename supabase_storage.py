"""
Supabase storage for insider configurations.
Falls back to local storage if Supabase is not configured.
"""
import json
import os
from typing import Dict, Optional, List

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  supabase-py not installed. Install with: pip install supabase")
    print("   Falling back to local storage (data.json)")

# Load .env file if available (do this AFTER checking for supabase)
try:
    from dotenv import load_dotenv
    # Try to load from current directory and common locations
    env_loaded = False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for env_path in ['.env', os.path.join(script_dir, '.env'), os.path.expanduser('~/InsidersMonitor/.env')]:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            print(f"✅ Loaded .env from: {env_path}")
            env_loaded = True
            break
    if not env_loaded:
        # Try default location (current working directory)
        load_dotenv(override=True)
        if os.path.exists('.env'):
            print(f"✅ Loaded .env from current directory")
        else:
            print(f"⚠️  No .env file found - will use system environment variables")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Will use system environment variables only")

# Configuration - read from environment (will be empty if not set)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
TABLE_NAME = "insiders"  # Table name in Supabase

# Local fallback
LOCAL_DATA_FILE = "insiders_data.json"

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if configured"""
    if not SUPABASE_AVAILABLE:
        print("⚠️  Supabase library not available (pip install supabase)")
        return None
    
    # Re-check environment variables (in case .env was loaded after module import)
    url = os.getenv("SUPABASE_URL", SUPABASE_URL)
    key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)
    
    if not url or not key:
        print(f"⚠️  Supabase credentials missing!")
        print(f"   SUPABASE_URL: {'SET' if url else 'NOT SET'}")
        print(f"   SUPABASE_KEY: {'SET' if key else 'NOT SET'}")
        print(f"   Current working directory: {os.getcwd()}")
        print(f"   .env file exists: {os.path.exists('.env')}")
        return None
    
    try:
        client = create_client(url, key)
        print(f"✅ Supabase client created successfully")
        return client
    except Exception as e:
        print(f"⚠️  Failed to connect to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_insiders_from_supabase() -> Dict:
    """Load all insiders from Supabase"""
    client = get_supabase_client()
    if not client:
        print("⚠️  No Supabase client available - falling back to local storage")
        return load_insiders_local()
    
    try:
        response = client.table(TABLE_NAME).select("*").execute()
        total_rows = len(response.data) if response.data else 0
        print(f"📊 Supabase returned {total_rows} total rows from database")
        
        insiders = {}
        skipped = 0
        for row in response.data:
            name = row.get("name")
            if name:
                wallet = row.get("wallet_address", "")
                if not wallet:
                    print(f"⚠️  Skipping {name}: no wallet_address")
                    skipped += 1
                    continue
                insiders[name] = {
                    "api": f"https://data-api.polymarket.com/activity?user={wallet}&limit=10&offset=0",
                    "webhook": row.get("webhook", ""),
                    "min_price": row.get("min_price", 0),
                    "max_price": row.get("max_price", 1),
                    "tag": row.get("tag_everyone", False),
                    "min_dollar_amount": row.get("min_dollar_amount", 0)
                }
            else:
                print(f"⚠️  Skipping row with no name: {row}")
                skipped += 1
        
        print(f"✅ Loaded {len(insiders)} insiders from Supabase (skipped {skipped} invalid rows)")
        if len(insiders) != total_rows:
            print(f"⚠️  Warning: Expected {total_rows} insiders but only loaded {len(insiders)}")
        
        return insiders
    except Exception as e:
        print(f"⚠️  Error loading from Supabase: {e}")
        import traceback
        traceback.print_exc()
        print("   Falling back to local storage")
        return load_insiders_local()

def load_bio_data_from_supabase() -> Dict:
    """Load all bio data from Supabase (for data.json replacement)"""
    client = get_supabase_client()
    if not client:
        return {"insiders": {}, "next_serial_id": 1}
    
    try:
        response = client.table(TABLE_NAME).select("name, serial_id, trading_style, hit_rate, main_markets, notes").execute()
        insiders = {}
        max_serial_id = 0
        
        for row in response.data:
            name = row.get("name")
            if name:
                serial_id = row.get("serial_id") or 0
                max_serial_id = max(max_serial_id, serial_id)
                insiders[name] = {
                    "serial_id": serial_id,
                    "bio": {
                        "trading_style": row.get("trading_style") or "Not set",
                        "hit_rate": row.get("hit_rate") or "Not set",
                        "main_markets": row.get("main_markets") or "Not set",
                        "notes": row.get("notes") or "No additional notes"
                    }
                }
        
        return {"insiders": insiders, "next_serial_id": max_serial_id + 1}
    except Exception as e:
        print(f"⚠️  Error loading bio data from Supabase: {e}")
        return {"insiders": {}, "next_serial_id": 1}

def load_insiders_local() -> Dict:
    """Load insiders from local JSON file"""
    try:
        with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("insiders", {})
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"⚠️  Error loading local data: {e}")
        return {}

def save_insider_to_supabase(name: str, wallet_address: str, webhook: str, 
                             min_dollar_amount: float = 0.0, tag_everyone: bool = False,
                             min_price: float = 0, max_price: float = 1,
                             serial_id: Optional[int] = None) -> bool:
    """Save or update insider in Supabase"""
    client = get_supabase_client()
    if not client:
        return save_insider_local(name, wallet_address, webhook, min_dollar_amount, tag_everyone, min_price, max_price)
    
    try:
        # Check if exists
        existing = client.table(TABLE_NAME).select("name, serial_id").eq("name", name).execute()
        
        data = {
            "name": name,
            "wallet_address": wallet_address,
            "webhook": webhook,
            "min_dollar_amount": min_dollar_amount,
            "tag_everyone": tag_everyone,
            "min_price": min_price,
            "max_price": max_price
        }
        
        # Only set serial_id if provided (for new insiders)
        if serial_id is not None:
            data["serial_id"] = serial_id
        elif existing.data and existing.data[0].get("serial_id"):
            # Keep existing serial_id if updating
            data["serial_id"] = existing.data[0]["serial_id"]
        
        if existing.data:
            # Update existing
            client.table(TABLE_NAME).update(data).eq("name", name).execute()
        else:
            # Insert new
            client.table(TABLE_NAME).insert(data).execute()
        
        return True
    except Exception as e:
        print(f"⚠️  Error saving to Supabase: {e}")
        print("   Falling back to local storage")
        return save_insider_local(name, wallet_address, webhook, min_dollar_amount, tag_everyone, min_price, max_price)

def update_bio_in_supabase(name: str, trading_style: Optional[str] = None,
                           hit_rate: Optional[str] = None, main_markets: Optional[str] = None,
                           notes: Optional[str] = None) -> bool:
    """Update bio information in Supabase"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        data = {}
        if trading_style is not None:
            data["trading_style"] = trading_style
        if hit_rate is not None:
            data["hit_rate"] = hit_rate
        if main_markets is not None:
            data["main_markets"] = main_markets
        if notes is not None:
            data["notes"] = notes
        
        if data:
            client.table(TABLE_NAME).update(data).eq("name", name).execute()
            return True
        return False
    except Exception as e:
        print(f"⚠️  Error updating bio in Supabase: {e}")
        return False

def save_insider_local(name: str, wallet_address: str, webhook: str,
                      min_dollar_amount: float = 0.0, tag_everyone: bool = False,
                      min_price: float = 0, max_price: float = 1) -> bool:
    """Save insider to local JSON file"""
    try:
        try:
            with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"insiders": {}}
        
        data["insiders"][name] = {
            "api": f"https://data-api.polymarket.com/activity?user={wallet_address}&limit=10&offset=0",
            "webhook": webhook,
            "min_price": min_price,
            "max_price": max_price,
            "tag": tag_everyone,
            "min_dollar_amount": min_dollar_amount
        }
        
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"❌ Error saving locally: {e}")
        return False

def delete_insider_from_supabase(name: str) -> bool:
    """Delete insider from Supabase"""
    client = get_supabase_client()
    if not client:
        return delete_insider_local(name)
    
    try:
        client.table(TABLE_NAME).delete().eq("name", name).execute()
        return True
    except Exception as e:
        print(f"⚠️  Error deleting from Supabase: {e}")
        return delete_insider_local(name)

def delete_insider_local(name: str) -> bool:
    """Delete insider from local storage"""
    try:
        with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if name in data.get("insiders", {}):
            del data["insiders"][name]
        
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"❌ Error deleting locally: {e}")
        return False
