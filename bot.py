
from datetime import datetime
from typing import List

import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord import colour
from constants import (BOT_TOKEN, SUBTEAMS)



bot = commands.Bot(command_prefix="i", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("READY")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="log")
async def log(interaction: discord.Interaction, subteam: str, time: int, description: str):
    try:
        Embed = discord.Embed(color = discord.Color.blue(), title = "Hour Logging", description =f"Sent hour request of {time} hours in {subteam} subteam for {interaction.user.name}. Description: {description}")
        await interaction.response.send_message(embed = Embed)
    except Exception as e:
        print(e)

@log.autocomplete("subteam")
async def log_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name = subteam, value = subteam)
        for subteam in SUBTEAMS if current.lower() in subteam.lower()
    ]


bot.run(BOT_TOKEN)