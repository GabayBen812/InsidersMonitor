#!/usr/bin/env python3
"""
Helper script to run the Discord bot.
Usage: python run_bot.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    if not os.getenv("DISCORD_BOT_TOKEN"):
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("   Create a .env file with: DISCORD_BOT_TOKEN=your_token_here")
        print("   Or set it in your environment.")
        sys.exit(1)
    
    print("🚀 Starting Discord bot...")
    print("   Make sure the bot is invited to your server with proper permissions!")
    print("   Press Ctrl+C to stop.\n")
    
    try:
        subprocess.run([sys.executable, "bot.py"])
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")

