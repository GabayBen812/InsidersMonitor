import discord
from discord import app_commands
from discord.ext import commands
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

def load_data():
    """Load insider bio data from Supabase - Supabase only, no local fallback"""
    try:
        from supabase_storage import load_bio_data_from_supabase
        return load_bio_data_from_supabase()
    except Exception as e:
        print(f"[ERROR] Failed to load data from Supabase: {e}")
        return {"insiders": {}, "next_serial_id": 1}

# Removed save_data - all data is stored in Supabase only

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
    
    # Update bio fields in Supabase
    updated_fields = []
    
    if trading_style is not None:
        updated_fields.append(f"**Trading Style**: {trading_style}")
    
    if hit_rate is not None:
        updated_fields.append(f"**Hit Rate**: {hit_rate}")
    
    if main_markets is not None:
        updated_fields.append(f"**Main Markets**: {main_markets}")
    
    if notes is not None:
        updated_fields.append(f"**Notes**: {notes}")
    
    if not updated_fields:
        await interaction.response.send_message(
            "❌ Please provide at least one field to update (trading_style, hit_rate, main_markets, or notes).",
            ephemeral=True
        )
        return
    
    # Save to Supabase (only storage)
    try:
        from supabase_storage import update_bio_in_supabase
        success = update_bio_in_supabase(
            name=insider,
            trading_style=trading_style,
            hit_rate=hit_rate,
            main_markets=main_markets,
            notes=notes
        )
        if not success:
            await interaction.response.send_message(
                "❌ ERROR: Failed to update bio in Supabase. Check your database connection.",
                ephemeral=True
            )
            return
    except Exception as e:
        print(f"[ERROR] Failed to update bio in Supabase: {e}")
        await interaction.response.send_message(
            f"❌ ERROR: Failed to update bio. {str(e)}",
            ephemeral=True
        )
        return
    
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
    webhook="Discord webhook URL for notifications (optional, uses default if not provided)",
    min_dollar_amount="Minimum dollar amount to trigger notifications (default: 0)",
    tag_everyone="Whether to tag @everyone (default: false)"
)
async def adduser(
    interaction: discord.Interaction,
    name: str,
    wallet_address: str,
    webhook: Optional[str] = None,
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
    
    # Use default webhook if not provided
    DEFAULT_WEBHOOK = "https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk"
    
    if webhook is None:
        # Use the default webhook if none provided
        webhook = DEFAULT_WEBHOOK
    else:
        # Validate webhook URL if provided
        if not webhook.startswith("https://discord.com/api/webhooks/"):
            await interaction.response.send_message(
                "❌ Invalid webhook URL. Must be a Discord webhook URL.",
                ephemeral=True
            )
            return
    
    # Check if exists in Supabase (ONLY source of truth)
    try:
        from supabase_storage import get_supabase_client, TABLE_NAME
        client = get_supabase_client()
        if not client:
            await interaction.response.send_message(
                "❌ ERROR: Cannot connect to Supabase database. Check your SUPABASE_URL and SUPABASE_KEY.",
                ephemeral=True
            )
            return
        
        # Check by name (exact match first, then case-insensitive)
        existing_by_name = client.table(TABLE_NAME).select("name").eq("name", name).execute()
        if existing_by_name.data:
            await interaction.response.send_message(
                f"❌ Insider '{name}' already exists in database. Use `/updatebio` to modify their bio.",
                ephemeral=True
            )
            return
        
        # Check case-insensitive match
        all_insiders = client.table(TABLE_NAME).select("name").execute()
        if all_insiders.data:
            for row in all_insiders.data:
                existing_name = row.get("name", "")
                if existing_name and existing_name.lower() == name.lower():
                    await interaction.response.send_message(
                        f"❌ Insider '{name}' already exists in database (as '{existing_name}'). Use `/updatebio` to modify their bio.",
                        ephemeral=True
                    )
                    return
        
        # Also check by wallet address to catch duplicates with different names
        existing_by_wallet = client.table(TABLE_NAME).select("name, wallet_address").eq("wallet_address", wallet_address).execute()
        if existing_by_wallet.data:
            existing_name = existing_by_wallet.data[0].get("name", "Unknown")
            await interaction.response.send_message(
                f"❌ Wallet address `{wallet_address[:10]}...` is already registered to insider '{existing_name}'. "
                f"Each wallet can only be registered once.",
                ephemeral=True
            )
            return
    except Exception as e:
        print(f"[ERROR] Could not check Supabase for existing insider: {e}")
        import traceback
        traceback.print_exc()
        await interaction.response.send_message(
            f"❌ ERROR: Failed to check database. {str(e)}",
            ephemeral=True
        )
        return
    
    # Load bio data from Supabase to get next serial_id
    data = load_data()  # This now loads from Supabase only
    
    # Add new insider
    serial_id = data.get("next_serial_id", 1)
    
    embed = discord.Embed(
        title=f"✅ Insider Added: {name}",
        description=f"Serial ID: #{serial_id}\nWallet: `{wallet_address[:10]}...{wallet_address[-8:]}`",
        color=discord.Color.green()
    )
    embed.add_field(name="Min Dollar Amount", value=f"${min_dollar_amount}", inline=True)
    embed.add_field(name="Tag @everyone", value="Yes" if tag_everyone else "No", inline=True)
    
    # Show webhook status
    webhook_status = "Default" if webhook == DEFAULT_WEBHOOK else "Custom"
    embed.add_field(name="Webhook", value=webhook_status, inline=True)
    
    # Save to Supabase (only storage) with serial_id
    try:
        from supabase_storage import save_insider_to_supabase
        success = save_insider_to_supabase(
            name=name,
            wallet_address=wallet_address,
            webhook=webhook,
            min_dollar_amount=min_dollar_amount,
            tag_everyone=tag_everyone,
            serial_id=serial_id  # Include serial_id in Supabase
        )
        if success:
            embed.set_footer(text="✅ Automatically saved to database")
        else:
            await interaction.response.send_message(
                "❌ ERROR: Failed to save to Supabase. Check your database connection.",
                ephemeral=True
            )
            return
    except Exception as e:
        print(f"[ERROR] Failed to save insider: {e}")
        await interaction.response.send_message(
            f"❌ ERROR: Failed to save to Supabase. {str(e)}",
            ephemeral=True
        )
        return
    
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

