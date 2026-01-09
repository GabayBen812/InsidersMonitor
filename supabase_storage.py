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

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
TABLE_NAME = "insiders"  # Table name in Supabase

# Local fallback
LOCAL_DATA_FILE = "insiders_data.json"

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if configured"""
    if not SUPABASE_AVAILABLE:
        return None
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️  Failed to connect to Supabase: {e}")
        return None

def load_insiders_from_supabase() -> Dict:
    """Load all insiders from Supabase"""
    client = get_supabase_client()
    if not client:
        return load_insiders_local()
    
    try:
        response = client.table(TABLE_NAME).select("*").execute()
        insiders = {}
        for row in response.data:
            name = row.get("name")
            if name:
                insiders[name] = {
                    "api": f"https://data-api.polymarket.com/activity?user={row.get('wallet_address', '')}&limit=10&offset=0",
                    "webhook": row.get("webhook", ""),
                    "min_price": row.get("min_price", 0),
                    "max_price": row.get("max_price", 1),
                    "tag": row.get("tag_everyone", False),
                    "min_dollar_amount": row.get("min_dollar_amount", 0)
                }
        return insiders
    except Exception as e:
        print(f"⚠️  Error loading from Supabase: {e}")
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
