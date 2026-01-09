# Supabase Setup Guide

## Why Supabase?

Instead of manually editing `strikes.py` every time you add an insider, the bot now automatically saves insider data to Supabase (or local storage as fallback). No more code changes needed! 🎉

## Setup Steps

### Option 1: Use Supabase (Recommended)

1. **Create a Supabase Project**
   - Go to https://supabase.com
   - Sign up/login
   - Create a new project

2. **Create the Table**
   - Go to "Table Editor" in your Supabase dashboard
   - Click "New Table"
   - Name it: `insiders`
   - Add these columns:
     - `name` (text, primary key)
     - `wallet_address` (text)
     - `webhook` (text)
     - `min_dollar_amount` (numeric, default: 0)
     - `tag_everyone` (boolean, default: false)
     - `min_price` (numeric, default: 0)
     - `max_price` (numeric, default: 1)

3. **Get Your Credentials**
   - Go to "Settings" → "API"
   - Copy your "Project URL" (SUPABASE_URL)
   - Copy your "anon public" key (SUPABASE_KEY)

4. **Add to .env File**
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

5. **Install Supabase Client**
   ```bash
   pip install supabase
   ```

### Option 2: Use Local Storage (No Setup)

If you don't want to use Supabase, the system will automatically:
- Save to `insiders_data.json` locally
- Load from there when `strikes.py` runs
- No configuration needed!

## How It Works

1. **Adding Insiders**: When you use `/adduser`, the bot automatically saves to Supabase/local storage
2. **Loading Insiders**: `strikes.py` automatically loads from Supabase/local storage on startup
3. **No Code Changes**: You never need to edit `strikes.py` again!

## Migration from Hardcoded Users

Your existing hardcoded users in `strikes.py` will still work as a fallback. To migrate them to Supabase:

1. Set up Supabase (see above)
2. Use `/adduser` for each existing insider (or write a migration script)
3. Once all are in Supabase, the hardcoded dict becomes just a fallback

## Troubleshooting

- **"Could not load from Supabase"**: Check your SUPABASE_URL and SUPABASE_KEY in `.env`
- **"Falling back to local storage"**: Supabase not configured - using `insiders_data.json` instead
- **"Using hardcoded USERS dict"**: Both Supabase and local storage failed - using code fallback
