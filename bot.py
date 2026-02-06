import os
import discord
from discord import app_commands
import requests
from datetime import datetime, timezone

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))

HARD_DURATION = 870         # 14 min 30 sec
NIGHTMARE_DURATION = 14400  # 4 hours

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

GUILD = discord.Object(id=GUILD_ID)
VIRUS_API = "https://clashofcoinscalc.com/api/timers/global-spawn-timers"

# Helper function to calculate remaining time
def get_remaining(seconds_since_last, duration):
    remaining = max(0, duration - seconds_since_last)
    hrs = remaining // 3600
    mins = (remaining % 3600) // 60
    secs = remaining % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

# /hard command
@tree.command(name="hard", description="Shows time until next Hard Virus", guild=GUILD)
async def hard(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last_hard = data.get("last_hard_spawn")
        if last_hard:
            last_hard_time = datetime.fromisoformat(last_hard.replace("Z", "+00:00")).timestamp()
            remaining = int(last_hard_time + HARD_DURATION - datetime.now(timezone.utc).timestamp())
            await interaction.response.send_message(f"🦠 Hard Virus spawns in: {get_remaining(0, remaining)}")
        else:
            await interaction.response.send_message("No data for Hard Virus yet.")
    except Exception as e:
        await interaction.response.send_message(f"Error fetching data: {e}")

# /nm command
@tree.command(name="nm", description="Shows time until next Nightmare Virus", guild=GUILD)
async def nm(interaction: discord.Interaction):
    try:
        data = requests.get(VIRUS_API, timeout=10).json()
        last_nm = data.get("last_nightmare_spawn")
        if last_nm:
            last_nm_time = datetime.fromisoformat(last_nm.replace("Z", "+00:00")).timestamp()
            remaining = int(last_nm_time + NIGHTMARE_DURATION - datetime.now(timezone.utc).timestamp())
            await interaction.response.send_message(f"🦠 Nightmare Virus spawns in: {get_remaining(0, remaining)}")
        else:
            await interaction.response.send_message("No data for Nightmare Virus yet.")
    except Exception as e:
        await interaction.response.send_message(f"Error fetching data: {e}")

@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print(f"Logged in as {client.user}")

client.run(TOKEN)
