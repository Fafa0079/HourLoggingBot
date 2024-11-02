import gspread
import traceback
import asqlite

from views import *

from pathlib import Path
from datetime import datetime
from typing import List, Literal, Optional

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
from constants import (ADMIN_CHANNEL, BOT_TOKEN, SUBTEAMS, PROJECT_FILEPATH)


bot = commands.Bot(command_prefix="-", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("READY")

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    # | no params syncs all | ~ syncs guild | * syncs global commands to guild | ^ removes all commands from guild |
            
@bot.tree.command(name="setup", description="Guided setup for hour logging.")
@commands.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    p1Embed = discord.Embed(color=discord.Color.blue(), title="Hour Logging Setup", description=f"Welcome to the hour logging setup, {interaction.user.display_name}! This guided setup will walk you through multiple steps to setup hour logging in your discord server. Listed here are the steps:\n1. Allow integration of discord bot w/ google sheets\n2. Add all subteams/groups\n3. Selection of admin channel to send hour logging approval messages\n4. Toggle use of /verify command")
    p2Embed = discord.Embed(color=discord.Color.blue(), title="Google Sheets Integration", description=f"Press the (+) button to create a new google sheets document! You may be prompted to give permissions to the bot. Don't worry, you'll only have to grant permissions once!")
    p3Embed = discord.Embed(color=discord.Color.blue(), title="Create Sheets Document", description="Press the (+) button to create a new google sheets document!")
    p4Embed = discord.Embed(color=discord.Color.blue(), title="Admin Channel Selection", description="placeholder")
    p5Embed = discord.Embed(color=discord.Color.blue(), title= "Verify Command Usage", description="placeholder")
    pages = [p1Embed, p2Embed, p3Embed, p4Embed, p5Embed]
    try:
        await interaction.response.send_message(embed=p1Embed, view = SetupPages(pages))
    except Exception as e:
        rEmbed = discord.Embed(color=discord.Color.red(), title="Setup Failed", description=f"Setup command failed due to an unexpected error.\n\nError:\n\n{e}")
        await interaction.response.send_message(embed=rEmbed)
        traceback.print_exception(type(e), e, e.__traceback__)          

@bot.tree.command(name="log", description= "Command used for logging hours.")
@app_commands.describe(subteam= "Your subteam", time= "Hours spent", description= "Explanation of tasks")
async def log(interaction: discord.Interaction, subteam: str, time: float, description: str):
    if (SUBTEAMS.count(subteam) != 0):
        if time > 0:
            try: # attempt to send message to admin channel
                user = interaction.user
                rEmbed = discord.Embed(color = discord.Color.dark_blue(), 
                                       title = "Hour Request", 
                                       description =f"**User**\n{user.display_name}\n\n**Subteam**\n{subteam}\n\n**Time spent**\n{time} hour(s)\n\n**Tasks**\n{description}")# extra spacing to make it look nice
                await discord.Guild.get_channel(interaction.guild, ADMIN_CHANNEL).send(embed = rEmbed, view=VerifyHours(time, user, subteam))
            except Exception as e: # if fails, print error
                print(e)
                eEmbed = discord.Embed(color = discord.Color.red(), 
                                       title = "Hour Logging", 
                                       description =f"Failed to send hour request due to an unexpected error.\n\n**Error(s):**\n\n{e}")
                await interaction.response.send_message(embed = eEmbed, ephemeral = True)
            else: # if succeeds, gives success message
                sEmbed = discord.Embed(color = discord.Color.green(), 
                                       title = "Hour Logging", 
                                       description =f"Successfully sent hour request!\n\n**User**\n{interaction.user.display_name}\n\n**Subteam**\n{subteam}\n\n**Time spent**\n{time} hour(s)\n\n**Tasks**\n{description}")
                await interaction.response.send_message(embed = sEmbed, ephemeral = True)
        else:
            rEmbed = discord.Embed(color=discord.Color.red(), 
                                   title="Edit Hours", 
                                   description=f"Error: Cannot log a number of {time} hours. Please input a positive and valid number.")
            await interaction.response.send_message(embed=rEmbed)
            
    else: # if subteam is invalid
        uEmbed = discord.Embed(color = discord.Color.red(), 
                               title = "Hour Logging", 
                               description =f"Failed to send hour request because '{subteam}' is not a valid subteam. Please input a valid subteam.")
        await interaction.response.send_message(embed = uEmbed, ephemeral = True) 

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