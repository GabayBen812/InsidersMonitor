# Bot Setup Fix - Slash Commands Not Working

## The Problem
If slash commands aren't appearing or working, the bot was likely invited **without** the `applications.commands` scope.

## Solution: Re-invite the Bot

### Step 1: Get the Invite URL
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application (the one with your bot token)
3. Go to **OAuth2** → **URL Generator**

### Step 2: Select Required Scopes
**CRITICAL:** You MUST select both:
- ✅ `bot`
- ✅ `applications.commands` ← **This is the missing one!**

### Step 3: Select Bot Permissions
Select these permissions:
- ✅ Send Messages
- ✅ Embed Links
- ✅ Use Slash Commands
- ✅ Read Message History
- ✅ View Channels

### Step 4: Copy and Use the URL
1. Copy the generated URL at the bottom
2. Open it in your browser
3. Select your server ("Apex")
4. Authorize the bot

### Step 5: Restart the Bot
After re-inviting, restart your bot:
```bash
python bot.py
```

The bot will now sync commands to your guild immediately!

## Verify It Works
1. Type `/` in Discord - you should see the bot's commands appear
2. Try `/test` - should respond immediately
3. Check terminal - should show "[INFO] ✨ Command received: /test"

## Alternative: Manual Guild Sync
If you can't re-invite, the bot now has a `/sync` command (admin only) that will sync commands to your guild.

