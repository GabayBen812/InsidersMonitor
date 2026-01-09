# Supabase Migration Guide

## Quick Setup Steps

### 1. Create Supabase Project
- Go to https://supabase.com
- Create a new project (or use existing)
- Wait for project to finish setting up

### 2. Run the SQL Script

1. In Supabase dashboard, go to **"SQL Editor"** (left sidebar)
2. Click **"New Query"**
3. Copy and paste the entire contents of `supabase_migration.sql`
4. Click **"Run"** (or press Ctrl+Enter)
5. You should see "Success. No rows returned" or similar

### 3. Verify Data

Run this query to see all your insiders:

```sql
SELECT name, wallet_address, min_dollar_amount, tag_everyone 
FROM insiders 
ORDER BY name;
```

You should see all 16 insiders listed!

### 4. Get Your Credentials

1. Go to **Settings** → **API**
2. Copy your **Project URL** (looks like: `https://xxxxx.supabase.co`)
3. Copy your **anon public** key (long string starting with `eyJ...`)

### 5. Add to .env File

Add these lines to your `.env` file:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### 6. Test It

1. Restart `strikes.py` - it should load insiders from Supabase
2. You should see: `✅ Loaded 16 insiders from database`
3. Use `/adduser` in Discord - new insiders will be saved automatically!

## What the SQL Script Does

1. **Creates the table** with all required columns
2. **Sets up auto-update** for `updated_at` timestamp
3. **Inserts all 16 existing insiders** from your code
4. **Uses ON CONFLICT** so you can run it multiple times safely

## Troubleshooting

### "Table already exists"
- That's fine! The script uses `CREATE TABLE IF NOT EXISTS`
- Just continue - it will insert/update the data

### "Duplicate key error"
- The script uses `ON CONFLICT` to handle this
- It will update existing records instead of failing

### "Permission denied"
- Make sure you're using the SQL Editor in Supabase dashboard
- You need to be the project owner or have SQL access

### Data not loading in strikes.py
- Check your `.env` file has correct SUPABASE_URL and SUPABASE_KEY
- Check the table name is exactly `insiders` (lowercase)
- Restart `strikes.py` after adding credentials

## Next Steps

After migration:
- ✅ All existing insiders are in Supabase
- ✅ New insiders added via `/adduser` will be saved automatically
- ✅ No more manual code editing needed!
- ✅ `strikes.py` auto-reloads every 5 minutes to pick up new insiders
