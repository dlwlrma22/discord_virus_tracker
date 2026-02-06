import os
import sys
import discord
from discord import app_commands
import requests
from datetime import datetime, timezone

# Environmental variable for Discord token
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ DISCORD_TOKEN not set")
    sys.exit(1)

# Constants for time calculations
HARD_DURATION = 870         # 14m 30s
NIGHTMARE_DURATION = 14400 # 4 hours
VIRUS_API = "https://clashofcoinscalc.com/api/timers/global-spawn-timers"

# Discord setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Helpers
def format_time(seconds):
    seconds = max(0, seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def remaining_time(last_spawn, duration):
    last = datetime.fromisoformat(last_spawn.replace("Z", "+00:00")).timestamp()
    now = datetime.now(timezone.utc).timestamp()
    return int(last + duration - now)

# /hard for Hard Virus timer
@tree.command(name="hard", description="Shows time until next Hard Virus spawn")
async def hard(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last = data.get("last_hard_spawn")

        if not last:
            await interaction.response.send_message("No Hard Virus data yet.")
            return

        remaining = remaining_time(last, HARD_DURATION)
        await interaction.response.send_message(
            f"🦠 **Hard Virus spawns in:** `{format_time(remaining)}`"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

# /nm for Nightmare Virus timer
@tree.command(name="nm", description="Shows time until next Nightmare Virus spawn")
async def nm(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last = data.get("last_nightmare_spawn")

        if not last:
            await interaction.response.send_message("No Nightmare Virus data yet.")
            return

        remaining = remaining_time(last, NIGHTMARE_DURATION)
        await interaction.response.send_message(
            f"🦠 **Nightmare Virus spawns in:** `{format_time(remaining)}`"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

# Ready event to sync commands and confirm bot is online
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user}")

client.run(TOKEN)
