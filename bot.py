
from datetime import datetime
import traceback
from typing import List, Literal, Optional

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
from constants import (ADMIN_CHANNEL, BOT_TOKEN, SUBTEAMS)


bot = commands.Bot(command_prefix="i", intents = discord.Intents.all())

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
async def config(interaction: discord.Interaction):
    print("placeholder")

class EditHours(discord.ui.Modal, title="Edit Hours"):
    time = discord.ui.TextInput(
        label="Hours",
        placeholder="Enter new number of hours here...")
    
    async def on_submit(self, interaction: discord.Interaction, time=time):
        # send google api request to add hours to spreadsheet
        sEmbed = discord.Embed(color = discord.Color.green(), title="Edit Hours", description=f"Sucessfully changed hours to {time} and submitted hour request.")
        await interaction.edit(embed=sEmbed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to change hours because of an error.\n\nError(s):\n\n{error}")
        await interaction.edit(embed=rEmbed)
        traceback.print_exception(type(error), error, error.__traceback__)

class DenyHours(discord.ui.Modal, title='Deny Hours'):
    reason = discord.ui.TextInput(
        label="Denial Reason",
        placeholder="Enter reason for denial here..."
    )
    async def on_submit(self, interaction: discord.Interaction, reason):
        # send google api request to add hours to spreadsheet
        sEmbed = discord.Embed(color = discord.Color.green(), title="Edit Hours", description=f"Declined hour request.\nReason:\n{reason}")
        await interaction.edit(embed=sEmbed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to decline hours due of an error.\n\nError(s):\n\n{error}")
        await interaction.edit(embed=rEmbed)
        traceback.print_exception(type(error), error, error.__traceback__)

class VerifyHours(View):
    def __init__(self):
        super().__init__()

        self.add_item(Button(label="Confirm", emoji="✅", style=ButtonStyle.green, custom_id="confirm"))
        self.add_item(Button(label="Edit Hours", emoji="⚠", style=ButtonStyle.secondary, custom_id="edit"))
        self.add_item(Button(label="Deny", emoji="⛔", style=ButtonStyle.red, custom_id="deny"))

        @discord.ui.button(custom_id="confirm")
        async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
            # send google api request to add hours to spreadsheet
            try:
                cEmbed = discord.Embed(color=discord.Color.green(), title="Hour Request", description=f"Confirmed hour request.")
                await interaction.response.edit(embed=cEmbed)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
        @discord.ui.button(custom_id="edit")
        async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.send_modal(EditHours())
        
        @discord.ui.button(custom_id="deny")
        async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.respondse.send_modal(DenyHours())
            

@bot.tree.command(name="log", description= "Command used for logging hours.")
@app_commands.describe(subteam= "Your subteam", time= "Hours spent", description= "Explanation of tasks")
async def log(interaction: discord.Interaction, subteam: str, time: int, description: str):
        if (SUBTEAMS.count(subteam) != 0):
            try: # attempt to send message to admin channel
                rEmbed = discord.Embed(color = discord.Color.dark_blue(), title = "Hour Request", description =f"**User**\n{interaction.user.display_name}\n\n**Subteam**\n{subteam}\n\n**Time spent**\n{time} hour(s)\n\n**Tasks**\n{description}")
                await discord.Guild.get_channel(interaction.guild, ADMIN_CHANNEL).send(embed = rEmbed, view=VerifyHours()) # keep ephemeral false
            except Exception as e: # if fails, print error
                print(e)
                eEmbed = discord.Embed(color = discord.Color.red(), title = "# Hour Logging", description =f"Failed to send hour request due to an error.\n\n**Error(s):**\n\n{e}")
                await interaction.response.send_message(embed = eEmbed, ephemeral = False)
            else: # if succeeds, gives success message
                sEmbed = discord.Embed(color = discord.Color.green(), title = "# Hour Logging", description =f"Successfully sent hour request!\n\n**User**\n{interaction.user.display_name}\n\n**Subteam**\n{subteam}\n\n**Time spent**\n{time} hour(s)\n\n**Tasks**\n{description}")
                await interaction.response.send_message(embed = sEmbed, ephemeral = False) #TODO set all ephemeral true after testing
                return time
        else: # if subteam is invalid
            uEmbed = discord.Embed(color = discord.Color.red(), title = "# Hour Logging", description =f"Failed to send hour request because '{subteam}' is not a valid subteam.")
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

bot.run(BOT_TOKEN)