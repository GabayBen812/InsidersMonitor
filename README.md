# Insiders Monitor

A Discord bot and monitoring system for tracking Polymarket insider trading activity with bio management.

## Features

- 🔍 **Real-time Monitoring**: Tracks trades from multiple Polymarket insiders
- 📊 **Bio Management**: Store and display trading styles, hit rates, and market insights per insider
- 🆔 **Serial IDs**: Each insider has a unique serial ID for easy tracking
- 🤖 **Discord Bot**: Manage insiders directly from Discord with slash commands
- 💰 **Filtering**: Configurable minimum dollar amounts per insider

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select an existing one
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Go to "OAuth2" > "URL Generator"
   - Select `bot` and `applications.commands` scopes
   - Select necessary permissions (Send Messages, Embed Links, etc.)
   - Copy the generated URL and open it to invite the bot to your server

### 3. Environment Variables

Create a `.env` file (or set environment variables):

```env
DISCORD_BOT_TOKEN=your_bot_token_here
```

### 4. Configuration

Edit `strikes.py` to configure your insiders:
- `api`: Polymarket API endpoint for the user
- `webhook`: Discord webhook URL for notifications
- `min_price` / `max_price`: Price range filters
- `tag`: Whether to tag @everyone
- `min_dollar_amount`: Minimum trade value to notify

## Usage

### Running the Monitor

Start the monitoring script:

```bash
python strikes.py
```

This will continuously monitor all configured insiders and send notifications to Discord.

### Running the Bot

In a separate terminal, start the Discord bot:

```bash
python bot.py
```

The bot will sync slash commands and be ready to use in your Discord server.

### Discord Commands

#### `/updatebio`
Update an insider's bio information.

**Parameters:**
- `insider` (required): The name of the insider
- `trading_style` (optional): Trading style description
- `hit_rate` (optional): Success rate (e.g., "75%" or "0.75")
- `main_markets` (optional): Main markets they trade
- `notes` (optional): Additional insights

**Example:**
```
/updatebio insider:"BAdiosB - Insider" trading_style:"Aggressive swing trader" hit_rate:"78%" main_markets:"Politics, Sports"
```

#### `/viewbio`
View an insider's complete bio information.

**Parameters:**
- `insider` (required): The name of the insider

**Example:**
```
/viewbio insider:"BAdiosB - Insider"
```

#### `/listinsiders`
List all tracked insiders with their serial IDs and basic info.

#### `/adduser`
Add a new insider to track.

**Parameters:**
- `name` (required): Display name
- `wallet_address` (required): Ethereum wallet address (0x...)
- `webhook` (required): Discord webhook URL
- `min_dollar_amount` (optional): Minimum trade value (default: 0)
- `tag_everyone` (optional): Tag @everyone on trades (default: false)

**Note:** After adding via bot, you'll need to manually add the user to `strikes.py` USERS dict.

#### `/help`
Show help for all commands.

## Data Storage

Insider bios and serial IDs are stored in `data.json`. This file is automatically created and managed by the bot.

## Trade Notifications

When a trade is detected, the notification includes:
- Serial ID
- Trade details (title, side, outcome, price, shares, cost)
- Execution timestamp
- Link to Polymarket event
- Insider bio (if configured)

## Notes

- The monitor checks for new trades every 5 seconds
- Only trades above the configured `min_dollar_amount` trigger notifications
- Bios are displayed at the bottom of trade notifications if configured
- Serial IDs are automatically assigned when insiders are added

