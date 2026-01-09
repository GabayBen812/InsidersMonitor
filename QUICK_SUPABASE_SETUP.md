# Quick Supabase Setup

## Step 1: Get Your Supabase Credentials

1. Go to https://supabase.com and sign in
2. Select your project (or create a new one)
3. Go to **Settings** → **API**
4. Copy these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

## Step 2: Add to .env File

Open your `.env` file and add these two lines:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

**Example:**
```env
DISCORD_BOT_TOKEN=your_bot_token_here
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNjIzOTAyMiwiZXhwIjoxOTMxODE1MDIyfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Step 3: Run SQL Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the entire `supabase_migration.sql` file
4. Click **Run**

## Step 4: Run Bio Migration

```bash
python migrate_bio_to_supabase.py
```

You should see:
```
📦 Found X insiders to migrate...
✅ Migrated: Insider Name (ID: #1)
...
✅ Migration complete!
```

## Done! ✅

Now all your data is safely stored in Supabase and will survive VM restarts!
