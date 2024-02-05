
from datetime import datetime
from typing import List, Literal, Optional

import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord import colour
from constants import (ADMIN_CHANNEL, BOT_TOKEN, SUBTEAMS)


bot = commands.Bot(command_prefix="i", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("READY")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="log", description= "Command used for logging hours.")
@app_commands.describe(subteam= "Your subteam", time= "Hours spent", description= "Explanation of tasks")
async def log(interaction: discord.Interaction, subteam: str, time: int, description: str):
        if (SUBTEAMS.count(subteam) != 0):
            try: # attempt to send message to admin channel
                channel = discord.Guild.get_channel(interaction.guild, ADMIN_CHANNEL)
                rEmbed = discord.Embed(color = discord.Color.dark_blue(), title = "Hour Request", description =f"**User**\n{interaction.user.display_name}\n**Subteam**\n{subteam}\n**Time spent**\n{time} hour(s)\n**Tasks**\n{description}")
                await channel.send(embed = rEmbed) # keep ephemeral false
            except Exception as e: # if fails, print error
                print(e)
                eEmbed = discord.Embed(color = discord.Color.red(), title = "Hour Logging", description =f"Failed to send hour request due to an error.\nError(s): \n{e}")
                await interaction.response.send_message(embed = eEmbed, ephemeral = False)
            else: # if succeeds, gives success message
                sEmbed = discord.Embed(color = discord.Color.green(), title = "Hour Logging", description =f"Successfully sent hour request!\n**User**\n{interaction.user.display_name}\n**Subteam**\n{subteam}\n**Time spent**\n{time} hour(s)\n**Tasks**\n{description}")
                await interaction.response.send_message(embed = sEmbed, ephemeral = False) #TODO set all ephemeral true after testing
        else: # if subteam is invalid
            uEmbed = discord.Embed(color = discord.Color.red(), title = "Hour Logging", description =f"Failed to send hour request because '{subteam}' is not a valid subteam.")
            await interaction.response.send_message(embed = uEmbed, ephemeral = False) 

@log.autocomplete("subteam")
async def log_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name = subteam, value = subteam)
        for subteam in SUBTEAMS if current.lower() in subteam.lower()
    ]

@bot.tree.command()
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
    # | no params sync all | ~ syncs guild | * syncs global commands to guild | ^ removes all commands from guild |


bot.run(BOT_TOKEN)