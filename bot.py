import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from typing import Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Load configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    print("⚠️  Warning: DISCORD_BOT_TOKEN not set. Bot will not start.")
    print("   Set it in your environment or .env file")

DATA_FILE = "data.json"
USERS_FILE = "strikes.py"

# Load user data from strikes.py (we'll need to parse it or import)
# For now, we'll manage it separately in data.json

def load_data():
    """Load insider data from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"insiders": {}, "next_serial_id": 1}

def save_data(data):
    """Save insider data to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_insider_list():
    """Get list of insiders from strikes.py"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple extraction of user names from USERS dict
            import re
            pattern = r'"([^"]+)":\s*\{'
            matches = re.findall(pattern, content)
            return matches
    except Exception as e:
        print(f"Error reading users: {e}")
        return []

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'✅ Bot ID: {bot.user.id}')
    print(f'✅ Bot is in {len(bot.guilds)} guild(s)')
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
        # Check bot permissions in each guild
        bot_member = guild.get_member(bot.user.id)
        if bot_member:
            perms = bot_member.guild_permissions
            print(f'     Permissions: send_messages={perms.send_messages}, embed_links={perms.embed_links}')
    try:
        # Sync globally (can take up to 1 hour)
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} command(s) globally:')
        for cmd in synced:
            print(f'   - /{cmd.name}')
        
        # Also sync to each guild for instant availability
        for guild in bot.guilds:
            try:
                bot.tree.copy_global_to(guild=guild)
                synced_guild = await bot.tree.sync(guild=guild)
                print(f'✅ Synced {len(synced_guild)} command(s) to guild "{guild.name}"')
            except Exception as e:
                print(f'⚠️  Could not sync to {guild.name}: {e}')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')
        import traceback
        traceback.print_exc()

@bot.event
async def on_message(message):
    """Handle regular messages"""
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Log all interactions"""
    print(f"[DEBUG] Interaction received: type={interaction.type}, id={interaction.id}")
    if interaction.type == discord.InteractionType.application_command:
        cmd_name = interaction.command.name if interaction.command else 'unknown'
        print(f"[INFO] Command received: /{cmd_name} by {interaction.user} in {interaction.guild.name if interaction.guild else 'DM'}")
    elif interaction.type == discord.InteractionType.autocomplete:
        print(f"[INFO] Autocomplete received for: {interaction.command.name if interaction.command else 'unknown'}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle command errors"""
    print(f"[ERROR] Command error: {error}", exc_info=True)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(f"❌ Error: {str(error)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {str(error)}", ephemeral=True)
    except Exception as e:
        print(f"[ERROR] Failed to send error message: {e}")

@bot.tree.command(name="updatebio", description="Update an insider's bio information")
@app_commands.describe(
    insider="The name of the insider to update",
    trading_style="Trading style (e.g., 'Aggressive', 'Conservative', 'Swing Trader')",
    hit_rate="Hit rate percentage (e.g., '75%' or '0.75')",
    main_markets="Main markets traded (e.g., 'Politics, Sports, Crypto')",
    notes="Additional notes or insights"
)
async def updatebio(
    interaction: discord.Interaction,
    insider: str,
    trading_style: Optional[str] = None,
    hit_rate: Optional[str] = None,
    main_markets: Optional[str] = None,
    notes: Optional[str] = None
):
    """Update bio for an insider"""
    data = load_data()
    
    # Check if insider exists
    if insider not in data["insiders"]:
        # Try to find by partial match
        matches = [name for name in data["insiders"].keys() if insider.lower() in name.lower()]
        if len(matches) == 1:
            insider = matches[0]
        elif len(matches) > 1:
            await interaction.response.send_message(
                f"❌ Multiple matches found. Please be more specific:\n" + "\n".join(f"• {m}" for m in matches),
                ephemeral=True
            )
            return
        else:
            await interaction.response.send_message(
                f"❌ Insider '{insider}' not found. Use `/listinsiders` to see all insiders.",
                ephemeral=True
            )
            return
    
    # Update bio fields
    bio = data["insiders"][insider]["bio"]
    updated_fields = []
    
    if trading_style is not None:
        bio["trading_style"] = trading_style
        updated_fields.append(f"**Trading Style**: {trading_style}")
    
    if hit_rate is not None:
        bio["hit_rate"] = hit_rate
        updated_fields.append(f"**Hit Rate**: {hit_rate}")
    
    if main_markets is not None:
        bio["main_markets"] = main_markets
        updated_fields.append(f"**Main Markets**: {main_markets}")
    
    if notes is not None:
        bio["notes"] = notes
        updated_fields.append(f"**Notes**: {notes}")
    
    if not updated_fields:
        await interaction.response.send_message(
            "❌ Please provide at least one field to update (trading_style, hit_rate, main_markets, or notes).",
            ephemeral=True
        )
        return
    
    save_data(data)
    
    embed = discord.Embed(
        title=f"✅ Bio Updated: {insider}",
        description="\n".join(updated_fields),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Serial ID: #{data['insiders'][insider]['serial_id']}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="viewbio", description="View an insider's bio information")
@app_commands.describe(insider="The name of the insider to view")
async def viewbio(interaction: discord.Interaction, insider: str):
    """View bio for an insider"""
    data = load_data()
    
    # Try to find by partial match
    if insider not in data["insiders"]:
        matches = [name for name in data["insiders"].keys() if insider.lower() in name.lower()]
        if len(matches) == 1:
            insider = matches[0]
        elif len(matches) > 1:
            await interaction.response.send_message(
                f"❌ Multiple matches found. Please be more specific:\n" + "\n".join(f"• {m}" for m in matches),
                ephemeral=True
            )
            return
        else:
            await interaction.response.send_message(
                f"❌ Insider '{insider}' not found. Use `/listinsiders` to see all insiders.",
                ephemeral=True
            )
            return
    
    insider_data = data["insiders"][insider]
    bio = insider_data["bio"]
    
    embed = discord.Embed(
        title=f"📊 {insider}",
        color=discord.Color.blue()
    )
    embed.add_field(name="🆔 Serial ID", value=f"#{insider_data['serial_id']}", inline=False)
    embed.add_field(name="📈 Trading Style", value=bio.get("trading_style", "Not set"), inline=True)
    embed.add_field(name="🎯 Hit Rate", value=bio.get("hit_rate", "Not set"), inline=True)
    embed.add_field(name="📊 Main Markets", value=bio.get("main_markets", "Not set"), inline=False)
    embed.add_field(name="📝 Notes", value=bio.get("notes", "No additional notes"), inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="listinsiders", description="List all tracked insiders with their serial IDs")
async def listinsiders(interaction: discord.Interaction):
    """List all insiders"""
    try:
        print(f"[DEBUG] listinsiders command invoked by {interaction.user}")
        data = load_data()
        print(f"[DEBUG] Data loaded: {len(data.get('insiders', {}))} insiders")
        
        if not data.get("insiders"):
            print("[DEBUG] No insiders found, sending message")
            await interaction.response.send_message("❌ No insiders found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Tracked Insiders",
            color=discord.Color.blue()
        )
        
        # Sort by serial ID
        sorted_insiders = sorted(data["insiders"].items(), key=lambda x: x[1]["serial_id"])
        print(f"[DEBUG] Processing {len(sorted_insiders)} insiders")
        
        # Discord embed limit is 25 fields
        for name, info in sorted_insiders:
            field_name = f"#{info['serial_id']} - {name}"
            field_value = f"Style: {info['bio']['trading_style']} | Hit Rate: {info['bio']['hit_rate']}"
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        print(f"[DEBUG] Sending embed with {len(embed.fields)} fields")
        await interaction.response.send_message(embed=embed)
        print("[DEBUG] Response sent successfully")
    except Exception as e:
        print(f"[ERROR] listinsiders error: {e}", exc_info=True)
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Error: {str(e)}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
        except Exception as e2:
            print(f"[ERROR] Failed to send error message: {e2}")

@bot.tree.command(name="adduser", description="Add a new insider to track")
@app_commands.describe(
    name="The display name of the insider",
    wallet_address="The wallet address (0x...)",
    webhook="Discord webhook URL for notifications",
    min_dollar_amount="Minimum dollar amount to trigger notifications (default: 0)",
    tag_everyone="Whether to tag @everyone (default: false)"
)
async def adduser(
    interaction: discord.Interaction,
    name: str,
    wallet_address: str,
    webhook: str,
    min_dollar_amount: Optional[float] = 0.0,
    tag_everyone: Optional[bool] = False
):
    """Add a new insider to track"""
    # Validate wallet address
    if not wallet_address.startswith("0x") or len(wallet_address) != 42:
        await interaction.response.send_message(
            "❌ Invalid wallet address. Must start with '0x' and be 42 characters long.",
            ephemeral=True
        )
        return
    
    # Validate webhook URL
    if not webhook.startswith("https://discord.com/api/webhooks/"):
        await interaction.response.send_message(
            "❌ Invalid webhook URL. Must be a Discord webhook URL.",
            ephemeral=True
        )
        return
    
    data = load_data()
    
    # Check if already exists
    if name in data["insiders"]:
        await interaction.response.send_message(
            f"❌ Insider '{name}' already exists. Use `/updatebio` to modify their bio.",
            ephemeral=True
        )
        return
    
    # Add new insider
    serial_id = data["next_serial_id"]
    data["insiders"][name] = {
        "serial_id": serial_id,
        "bio": {
            "trading_style": "Not set",
            "hit_rate": "Not set",
            "main_markets": "Not set",
            "notes": "No additional notes"
        },
        "wallet_address": wallet_address,
        "webhook": webhook,
        "min_dollar_amount": min_dollar_amount,
        "tag_everyone": tag_everyone
    }
    data["next_serial_id"] += 1
    
    save_data(data)
    
    embed = discord.Embed(
        title=f"✅ Insider Added: {name}",
        description=f"Serial ID: #{serial_id}\nWallet: `{wallet_address[:10]}...{wallet_address[-8:]}`",
        color=discord.Color.green()
    )
    embed.add_field(name="Min Dollar Amount", value=f"${min_dollar_amount}", inline=True)
    embed.add_field(name="Tag @everyone", value="Yes" if tag_everyone else "No", inline=True)
    embed.set_footer(text="⚠️ Remember to add this user to strikes.py USERS dict manually!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="test", description="Test command to verify bot is working")
async def test_command(interaction: discord.Interaction):
    """Simple test command"""
    print(f"[DEBUG] test command received from {interaction.user}")
    try:
        await interaction.response.send_message("✅ Bot is working! Commands are functional.", ephemeral=False)
        print("[DEBUG] Test command response sent successfully")
    except Exception as e:
        print(f"[ERROR] Failed to send test response: {e}", exc_info=True)
        try:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
        except:
            pass

@bot.tree.command(name="sync", description="Manually sync commands to this guild (admin only)")
async def sync_commands(interaction: discord.Interaction):
    """Manually sync commands to the current guild"""
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer(thinking=True)
        bot.tree.copy_global_to(guild=interaction.guild)
        synced = await bot.tree.sync(guild=interaction.guild)
        await interaction.followup.send(f"✅ Synced {len(synced)} command(s) to this guild!", ephemeral=False)
        print(f"[INFO] Commands synced to {interaction.guild.name} by {interaction.user}")
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}", exc_info=True)
        await interaction.followup.send(f"❌ Failed to sync: {str(e)}", ephemeral=True)

@bot.tree.command(name="help", description="Show help for all commands")
async def help_command(interaction: discord.Interaction):
    """Show help message"""
    embed = discord.Embed(
        title="🤖 Insiders Monitor Bot - Commands",
        description="Manage insider tracking and bios",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="/updatebio",
        value="Update an insider's bio\n"
              "• `insider`: Name of the insider\n"
              "• `trading_style`: How they trade\n"
              "• `hit_rate`: Success percentage\n"
              "• `main_markets`: Markets they focus on\n"
              "• `notes`: Additional insights",
        inline=False
    )
    
    embed.add_field(
        name="/viewbio",
        value="View an insider's complete bio information",
        inline=False
    )
    
    embed.add_field(
        name="/listinsiders",
        value="List all tracked insiders with their serial IDs",
        inline=False
    )
    
    embed.add_field(
        name="/adduser",
        value="Add a new insider to track\n"
              "⚠️ You'll also need to add them to strikes.py manually",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ Cannot start bot without DISCORD_BOT_TOKEN")

