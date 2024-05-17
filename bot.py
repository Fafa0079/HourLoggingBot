import gspread

from datetime import datetime
import traceback
from typing import List, Literal, Optional

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
from constants import (ADMIN_CHANNEL, BOT_TOKEN, SUBTEAMS, PROJECT_FILEPATH)


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
class AddSubteam(discord.ui.Modal, title="Add Subteam"):
    def __init__(self, gc, subteams):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
    
    subteam_name = discord.ui.TextInput(label="Subteam Name", placeholder="Enter the name of the subteam to add...")
    
    async def on_submit(self, interaction: discord.Interaction):
        self.subteams.append(self.subteam_name)
        await interaction.response.edit_message(view=PlusMinus(self.gc, self.subteams))
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to change hours due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)
    
class PlusMinus(View):
    def __init__(self, gc, subteams):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
        
    @discord.ui.button(label="+", style=ButtonStyle.green, custom_id="plus")
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddSubteam(self.gc, self.subteams))
        
    @discord.ui.button(label="-", style=ButtonStyle.red, custom_id="minus")
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.subteams.pop()
        await interaction.response.edit_message(self.gc, self.subteams)
        
    @discord.ui.button(label="Next", style=ButtonStyle.primary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.pages[self.page], view=SetupPages(self.pages))

class SetSheetName(discord.ui.Modal, title="Set Spreadsheet Name"):
    def __init__(self, gc, pages):
        super().__init__()
        self.gc = gc
        self.pages = pages
        self.name = discord.ui.TextInput(label="Spreadsheet Name", placeholder="Enter a name for the spreadsheet...")
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        # spreadsheet_name = self.name_input.value
        # if spreadsheet_name:
        await interaction.response.defer(thinking=True)
        self.gc.create(str(self.name))
        self.subteams = {}
        sEmbed = discord.Embed(color=discord.Color.blue(), title="Add Subteams", description=f"Google Sheets document created with the name '{self.name}'! Now, please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
        await interaction.followup.send(embed=sEmbed, view=PlusMinus(self.gc, self.subteams))
        # else:
        #     rEmbed = discord.Embed(color=discord.Color.red(), title="Error", description="Error: No spreadsheet name provided. Please insert a valid spreadsheet name.")
        #     await interaction.response.edit_message(embed=rEmbed, view=SetupPages(self.pages))
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to change hours due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)
    
        
    
class SetupPages(View):
    def __init__(self, pages):
        super().__init__()
        self.page = 0
        self.pages = pages
       # Create buttons with unique custom_ids
        self.prev_button = Button(label="<", style=ButtonStyle.primary, custom_id="prev_button")
        self.pageinfo = Button(label=f"Step 1/{len(pages)}", style=ButtonStyle.secondary, custom_id="pageinfo", disabled=True)
        self.next_button = Button(label=">", style=ButtonStyle.primary, custom_id="next_button")
        self.plus_button = Button(label="+", style=ButtonStyle.green, custom_id="plus_button", disabled=True)

        # Add buttons to the view
        self.add_item(self.prev_button)
        self.add_item(self.pageinfo)
        self.add_item(self.next_button)
        self.add_item(self.plus_button)

        # Bind the buttons to their callback methods
        self.prev_button.callback = self.prev
        self.next_button.callback = self.next
        self.plus_button.callback = self.plus
        
    async def update_buttons(self):
        self.pageinfo.label = f"Step {self.page + 1}/{len(self.pages)}"
        self.plus_button.disabled = self.page != 1
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page == len(self.pages)-1

    async def prev(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.page], view=self)
    async def next(self, interaction: discord.Interaction):
        if self.page < len(self.pages) - 1:
            self.page += 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.page], view=self)
    async def plus(self, interaction: discord.Interaction):
        if self.page == 1:
            gc = gspread.oauth(
                credentials_filename=fr"{PROJECT_FILEPATH}\credentials.json",
                authorized_user_filename=fr"{PROJECT_FILEPATH}\authorized_user.json",
                scopes="https://www.googleapis.com/auth/drive.file"               
            )
            await interaction.response.send_modal(SetSheetName(gc, self.pages))
        else:
            print("Placeholder")
            

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
        await interaction.response.send_message(embed=p1Embed, view = SetupPages(pages), ephemeral=True)
    except Exception as e:
        rEmbed = discord.Embed(color=discord.Color.red(), title="Setup Failed", description=f"Setup command failed due to an unexpected error.\n\nError:\n\n{e}")
        await interaction.response.send_message(embed=rEmbed)
        traceback.print_exception(type(e), e, e.__traceback__)
        

class EditHours(discord.ui.Modal, title="Edit Hours"):
    time = discord.ui.TextInput(
        label="Hours",
        placeholder="Enter new number of hours here...")
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            float(self.time.value)
        except TypeError as e:
            rEmbed = discord.Embed(color=discord.Color.red(), title="Edit Hours", description=f"Error: Failed to edit hours because {self.time.value} is not a number. Please input a valid number.\n\nFull error:{e}")
            await interaction.response.edit_message(embed=rEmbed)
            print("Likely user error above, ignore ^^^^^^^^^^^^^^^^^^")
        except ValueError as f:
            rEmbed = discord.Embed(color=discord.Color.red(), title="Edit Hours", description=f"Error: Failed to edit hours because {self.time.value} is not a number. Please input a valid number.\n\nFull error:{f}")
            await interaction.response.edit_message(embed=rEmbed)
            print("Likely user error above, ignore ^^^^^^^^^^^^^^^^^^")
        else:
            if float(self.time.value) < 0:
                rEmbed = discord.Embed(color=discord.Color.red(), title="Edit Hours", description=f"Error: Cannot log a negative number of {self.time.value} hours. Please input a positive number.")
                await interaction.response.edit_message(embed=rEmbed)
            else:
                # send google api request to add hours to spreadsheet
                sEmbed = discord.Embed(color = discord.Color.green(), title="Edit Hours", description=f"Sucessfully changed time to **{self.time.value}** hours and submitted hour request.")
                await interaction.response.edit_message(embed=sEmbed, view=None, delete_after=30)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to change hours due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)

class DenyHours(discord.ui.Modal, title='Deny Hours'):
    def __init__(self, user, time, subteam):
        super().__init__()
        self.user = user
        self.time = time
        self.subteam = subteam
    reason = discord.ui.TextInput(
        label="Denial Reason",
        placeholder="Enter reason for denial here..."
    )
    async def on_submit(self, interaction: discord.Interaction):
        sEmbed = discord.Embed(color = discord.Color.green(), title="Deny Hours", description=f"Denied hour request and messaged {self.user}.\n\nReason:{self.reason}")
        uEmbed = discord.Embed(color = discord.Color.red(), title="Hour Request Declined", description=f"Your hour request of **{self.time}** hours in the **{self.subteam}** subteam was denied.\n\nReason: {self.reason}")
        await self.user.send(embed=uEmbed)
        await interaction.response.edit_message(embed=sEmbed, view=None, delete_after=30)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to decline hours due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)

class VerifyHours(View):
    def __init__(self, time, user, subteam):
        super().__init__()
        self.time = time
        self.user = user
        self.subteam = subteam
    @discord.ui.button(label="Confirm", style=ButtonStyle.green, custom_id="confirm", emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # send google api request to add hours to spreadsheet
        try:
            cEmbed = discord.Embed(color=discord.Color.green(), title="Hour Request", description=f"Confirmed hour request of **{self.time}** hours")
            await interaction.response.edit_message(embed=cEmbed, view=None, delete_after=30)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to confirm hours due to an unexpected error.\n\nError(s):\n\n{e}")
            await interaction.response.edit_message(embed=rEmbed, view=None)
    @discord.ui.button(label="Edit", style=ButtonStyle.secondary, custom_id="edit", emoji="✏")
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditHours())
        
    @discord.ui.button(label="Deny", style=ButtonStyle.red, custom_id="deny", emoji="⛔")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DenyHours(self.user, self.time, self.subteam))
            

@bot.tree.command(name="log", description= "Command used for logging hours.")
@app_commands.describe(subteam= "Your subteam", time= "Hours spent", description= "Explanation of tasks")
async def log(interaction: discord.Interaction, subteam: str, time: float, description: str):
    if (SUBTEAMS.count(subteam) != 0):
        if time > 0:
            try: # attempt to send message to admin channel
                user = interaction.user
                rEmbed = discord.Embed(color = discord.Color.dark_blue(), title = "Hour Request", description =f"**User**\n{user.display_name}\n\n**Subteam**\n{subteam}\n\n**Time spent**\n{time} hour(s)\n\n**Tasks**\n{description}")# extra spacing to make it look nice
                await discord.Guild.get_channel(interaction.guild, ADMIN_CHANNEL).send(embed = rEmbed, view=VerifyHours(time, user, subteam))
            except Exception as e: # if fails, print error
                print(e)
                eEmbed = discord.Embed(color = discord.Color.red(), title = "Hour Logging", description =f"Failed to send hour request due to an unexpected error.\n\n**Error(s):**\n\n{e}")
                await interaction.response.send_message(embed = eEmbed, ephemeral = True)
            else: # if succeeds, gives success message
                sEmbed = discord.Embed(color = discord.Color.green(), title = "Hour Logging", description =f"Successfully sent hour request!\n\n**User**\n{interaction.user.display_name}\n\n**Subteam**\n{subteam}\n\n**Time spent**\n{time} hour(s)\n\n**Tasks**\n{description}")
                await interaction.response.send_message(embed = sEmbed, ephemeral = True)
        else:
            rEmbed = discord.Embed(color=discord.Color.red(), title="Edit Hours", description=f"Error: Cannot log a number of {time} hours. Please input a positive and valid number.")
            await interaction.response.send_message(embed=rEmbed)
            
    else: # if subteam is invalid
        uEmbed = discord.Embed(color = discord.Color.red(), title = "Hour Logging", description =f"Failed to send hour request because '{subteam}' is not a valid subteam. Please input a valid subteam.")
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