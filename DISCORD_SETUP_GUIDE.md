# Discord Bot Setup Guide - Slash Commands

## Step-by-Step Instructions

### Step 1: Open Discord Developer Portal
1. Go to: https://discord.com/developers/applications
2. Log in with your Discord account

### Step 2: Select Your Bot Application
1. Find and click on your bot application (the one with your bot token)
2. If you don't see it, you may need to create a new application first

### Step 3: Go to OAuth2 URL Generator
1. In the left sidebar, click on **"OAuth2"**
2. Then click on **"URL Generator"** (submenu under OAuth2)

### Step 4: Select Scopes (CRITICAL!)
In the **"SCOPES"** section, you MUST check:
- ✅ **`bot`** - Allows the bot to join servers
- ✅ **`applications.commands`** - **THIS IS THE KEY ONE!** Allows slash commands to work

### Step 5: Select Bot Permissions
In the **"BOT PERMISSIONS"** section, check:
- ✅ **Send Messages** - Bot can send messages
- ✅ **Embed Links** - Bot can send rich embeds
- ✅ **Use Slash Commands** - Bot can use slash commands (usually auto-checked)
- ✅ **Read Message History** - Bot can read messages
- ✅ **View Channels** - Bot can see channels

### Step 6: Copy the Generated URL
1. Scroll down to see the **"Generated URL"** at the bottom
2. It will look something like:
   ```
   https://discord.com/api/oauth2/authorize?client_id=...&permissions=...&scope=bot%20applications.commands
   ```
3. **Important:** Make sure the URL contains `applications.commands` in the `scope` parameter!

### Step 7: Invite the Bot
1. Copy the entire URL
2. Open it in a new browser tab/window
3. Select your server ("Apex" in your case)
4. Click **"Authorize"**
5. Complete any CAPTCHA if prompted

### Step 8: Restart Your Bot
1. Stop your bot (Ctrl+C in terminal)
2. Restart it: `python bot.py`
3. You should see: `✅ Synced X command(s) to guild "Apex"`

### Step 9: Test Slash Commands
1. Go to your Discord server
2. Type `/` in any channel
3. You should see your bot's commands appear:
   - `/listinsiders`
   - `/viewbio`
   - `/updatebio`
   - `/adduser`
   - `/test`
   - `/help`
4. Try `/test` first - it should respond immediately!

## Troubleshooting

### Commands Still Don't Appear?
1. **Wait a few minutes** - Sometimes Discord needs a moment to sync
2. **Check the URL** - Make sure `applications.commands` is in the scope
3. **Re-invite the bot** - Remove the bot from your server and invite again with the new URL
4. **Check bot permissions** - Make sure the bot has permission to use slash commands in the channel

### Bot Shows "Synced" But Commands Don't Work?
- The bot might be synced globally (takes up to 1 hour)
- The guild-specific sync should work immediately
- Check terminal for: `✅ Synced X command(s) to guild "Apex"`

### Still Having Issues?
- Make sure you're using the **same bot token** in your `.env` file
- Verify the bot is online in your server (green dot)
- Try the `/sync` command (admin only) to manually sync commands

## Quick Checklist
- [ ] Opened Discord Developer Portal
- [ ] Selected OAuth2 → URL Generator
- [ ] Checked `bot` scope
- [ ] Checked `applications.commands` scope ← **MOST IMPORTANT!**
- [ ] Selected bot permissions
- [ ] Copied the generated URL
- [ ] Invited bot to server using the URL
- [ ] Restarted the bot
- [ ] Tested `/test` command

Once you complete these steps, your slash commands should work perfectly! 🎉

