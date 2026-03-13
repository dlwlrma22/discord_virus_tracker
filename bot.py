import os
import sys
import discord
from discord import app_commands
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ DISCORD_TOKEN not set")
    sys.exit(1)

VIRUS_API = "https://clashofcoinscalc.com/api/timers/global-spawn-timers"

HARD_DURATION = 870         # 14 min 30 sec
NIGHTMARE_DURATION = 14400 # 4 hours
BASIC_DURATION = 870         # 14 min 30 sec

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Helper: format remaining time
def format_remaining(seconds: int) -> str:
    seconds = max(0, seconds)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

# /hard command
@tree.command(name="hard", description="Shows Hard Virus spawn time (UTC & PHT)")
async def hard(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last_spawn = data.get("last_hard_spawn")

        if not last_spawn:
            await interaction.response.send_message("No data for Hard Virus yet.")
            return

        last_time = datetime.fromisoformat(last_spawn.replace("Z", "+00:00"))
        spawn_utc = last_time + timedelta(seconds=HARD_DURATION)
        now_utc = datetime.now(timezone.utc)

        remaining = int((spawn_utc - now_utc).total_seconds())

        pht = timezone(timedelta(hours=8))
        spawn_pht = spawn_utc.astimezone(pht)

        await interaction.response.send_message(
            f"🦠 **Hard Virus**\n"
            f"⏳ Spawns in: `{format_remaining(remaining)}`\n"
            f"⏰ Estimated time:\n"
            f"• **UTC:** `{spawn_utc.strftime('%I:%M %p')}`\n"
            f"• **PHT:** `{spawn_pht.strftime('%I:%M %p')}`"
        )

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

# /nm command
@tree.command(name="nm", description="Shows Nightmare Virus spawn time (UTC & PHT)")
async def nm(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last_spawn = data.get("last_nightmare_spawn")

        if not last_spawn:
            await interaction.response.send_message("No data for Nightmare Virus yet.")
            return

        last_time = datetime.fromisoformat(last_spawn.replace("Z", "+00:00"))
        spawn_utc = last_time + timedelta(seconds=NIGHTMARE_DURATION)
        now_utc = datetime.now(timezone.utc)

        remaining = int((spawn_utc - now_utc).total_seconds())

        pht = timezone(timedelta(hours=8))
        spawn_pht = spawn_utc.astimezone(pht)

        await interaction.response.send_message(
            f"🦠 **Nightmare Virus**\n"
            f"⏳ Spawns in: `{format_remaining(remaining)}`\n"
            f"⏰ Estimated time:\n"
            f"• **UTC:** `{spawn_utc.strftime('%I:%M %p')}`\n"
            f"• **PHT:** `{spawn_pht.strftime('%I:%M %p')}`"
        )

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

# /basic command
@tree.command(name="basic", description="Shows Basic Virus spawn time (UTC & PHT)")
async def basic(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last_spawn = data.get("last_basic_spawn")

        if not last_spawn:
            await interaction.response.send_message("No data for Basic Virus yet.")
            return

        last_time = datetime.fromisoformat(last_spawn.replace("Z", "+00:00"))
        spawn_utc = last_time + timedelta(seconds=BASIC_DURATION)
        now_utc = datetime.now(timezone.utc)

        remaining = int((spawn_utc - now_utc).total_seconds())

        pht = timezone(timedelta(hours=8))
        spawn_pht = spawn_utc.astimezone(pht)

        await interaction.response.send_message(
            f"🦠 **Basic Virus**\n"
            f"⏳ Spawns in: `{format_remaining(remaining)}`\n"
            f"⏰ Estimated time:\n"
            f"• **UTC:** `{spawn_utc.strftime('%I:%M %p')}`\n"
            f"• **PHT:** `{spawn_pht.strftime('%I:%M %p')}`"
        )

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")
        
#-----FOR CLEARING OLD COMMANDS ON STARTUP-----
#@client.event
#async def on_ready():
#    print("🧹 Clearing old slash commands...")
#    tree.clear_commands(guild=None)   # clears ALL global slash commands
#    await tree.sync()
#    print(f"✅ Synced fresh commands as {client.user}")

#-----ORIGINAL--------
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user}")

client.run(TOKEN)








