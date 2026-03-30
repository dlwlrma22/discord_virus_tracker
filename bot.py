import os
import sys
import discord
from discord import app_commands
from discord.ext import tasks
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ DISCORD_TOKEN not set")
    sys.exit(1)

VIRUS_API = "https://clashofcoinscalc.com/api/timers/global-spawn-timers"
#DEX Price Endpoint
DEX_PRICE_API = "https://api.dexscreener.com/latest/dex/pairs/base/0x995985c9027e8a90c823a5e0a9112fea72d1f4dd"
TOKEN_SYMBOL = "OWB"

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

#Get token price from Dexscreener
def get_token_data():
    try:
        response = requests.get(DEX_PRICE_API, timeout=10)
        response.raise_for_status()
        data = response.json()

        pairs = data.get("pairs", [])
        if not pairs:
            return None

        pair = pairs[0]
        price = pair.get("priceUsd")
        price_change = pair.get("priceChange", {})

        return {
            "price": float(price) if price else None,
            "m5": price_change.get("m5"),
            "h1": price_change.get("h1"),
            "h6": price_change.get("h6"),
            "h24": price_change.get("h24"),
        }

    except Exception as e:
        print(f"Price fetch error: {e}")
        return None

status_index = 0

@tasks.loop(seconds=20)
async def update_status():
    global status_index
    token_data = get_token_data()

    if not token_data or token_data["price"] is None:
        text = "OWB price unavailable"
    else:
        price = token_data["price"]
        changes = [
            ("5m", token_data["m5"]),
            ("1h", token_data["h1"]),
            ("6h", token_data["h6"]),
            ("24h", token_data["h24"]),
        ]

        label, value = changes[status_index % len(changes)]
        status_index += 1

        if value is None:
            text = f"OWB ${price:.5f} | {label}: N/A"
        else:
            arrow = "▲" if value > 0 else "▼" if value < 0 else "•"
            text = f"OWB ${price:.5f} | {label} {arrow} {value:+.2f}%"

    activity = discord.Game(name=text)
    await client.change_presence(status=discord.Status.online, activity=activity)

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
    if not update_status.is_running():
        update_status.start()
    print(f"Logged in as {client.user}")
client.run(TOKEN)








