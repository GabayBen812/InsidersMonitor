#!/usr/bin/env python3
"""
Script to migrate bio data from data.json to Supabase.
Run this after setting up Supabase to transfer all your existing bio data.
"""
import json
import os

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from supabase_storage import get_supabase_client, update_bio_in_supabase, save_insider_to_supabase

DATA_FILE = "data.json"

def migrate_bio_data():
    """Migrate all bio data from data.json to Supabase"""
    client = get_supabase_client()
    if not client:
        print("❌ Supabase not configured!")
        print("\n📝 To fix this, add these lines to your .env file:")
        print("   SUPABASE_URL=https://your-project-id.supabase.co")
        print("   SUPABASE_KEY=your-anon-key-here")
        print("\n💡 Get these from: Supabase Dashboard → Settings → API")
        return
    
    # Load data.json
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ {DATA_FILE} not found!")
        return
    except Exception as e:
        print(f"❌ Error reading {DATA_FILE}: {e}")
        return
    
    insiders = data.get("insiders", {})
    if not insiders:
        print("⚠️  No insiders found in data.json")
        return
    
    print(f"📦 Found {len(insiders)} insiders to migrate...")
    
    migrated = 0
    failed = 0
    
    for name, info in insiders.items():
        try:
            serial_id = info.get("serial_id")
            bio = info.get("bio", {})
            
            # Update bio in Supabase
            update_bio_in_supabase(
                name=name,
                trading_style=bio.get("trading_style"),
                hit_rate=bio.get("hit_rate"),
                main_markets=bio.get("main_markets"),
                notes=bio.get("notes")
            )
            
            # Also update serial_id if it exists
            if serial_id:
                try:
                    client.table("insiders").update({"serial_id": serial_id}).eq("name", name).execute()
                except Exception as e:
                    print(f"⚠️  Could not update serial_id for {name}: {e}")
            
            migrated += 1
            print(f"✅ Migrated: {name} (ID: #{serial_id})")
        except Exception as e:
            failed += 1
            print(f"❌ Failed to migrate {name}: {e}")
    
    print(f"\n✅ Migration complete!")
    print(f"   Migrated: {migrated}")
    print(f"   Failed: {failed}")
    print(f"\n💡 Your bio data is now safely stored in Supabase!")

if __name__ == "__main__":
    migrate_bio_data()
