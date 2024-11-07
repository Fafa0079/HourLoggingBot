import asqlite
import modals
from views import SetupPages

import discord
from discord.ui import View
from discord import ButtonStyle

import views

class PlusMinus(View):
    def __init__(self, gc, subteams, spreadsheet_url, verify_required):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
        self.spreadsheet_url = spreadsheet_url
        self.verify_required = verify_required
        
    @discord.ui.button(label="+", style=ButtonStyle.green, custom_id="plus")
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(modals.AddSubteam(self.gc, self.subteams, self.spreadsheet_url, self.verify_required))
        
    @discord.ui.button(label="-", style=ButtonStyle.red, custom_id="minus")
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.subteams.pop()
        except IndexError:
            rEmbed = discord.Embed(color=discord.Color.yellow(), 
                title="Add Subteams", 
                description=f"**Error: Cannot remove a subteam/group that does not exist. Please add more subteams/groups.**\n\nPlease add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
            await interaction.response.edit_message(embed=rEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url, self.verify_required))
        else:
            sEmbed = discord.Embed(color=discord.Color.blue(), 
                title="Add Subteams", 
                description=f"Please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
            await interaction.response.edit_message(embed=sEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url, self.verify_required))
        
    @discord.ui.button(label="Next", style=ButtonStyle.primary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.subteams) <= 0:
            rEmbed = discord.Embed(color=discord.Color.yellow(),
                title="Add Subteams", 
                description=f"**Error: Must have at least one subteam/group. Please add more subteams/groups.**\n\nPlease add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
            await interaction.response.edit_message(embed=rEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url, self.verify_required))
        else:
            try:
                await self.create_server_table(interaction=interaction, subteams=self.subteams)
            except Exception as e:
                rEmbed = discord.Embed(color=discord.Color.red(), 
                                title="Database Error", 
                                description=f"An error has occured with the database. Please contact the bot creator. \n\nDatabase Error: {e}")
                print(f"Database error: {e}")
                await interaction.response.edit_message(embed=rEmbed, view=None)
            else:
                sEmbed = discord.Embed(color=discord.Color.green(), 
                    title="Hour Logging Setup Complete", 
                    description=f"Congratulations! You have completed the setup for the bot. You now may log hours to your newly created [spreadsheet]({self.spreadsheet_url}) using the `/log` command!)\n\nThis message will be cleared in 30 seconds.")
                await interaction.response.edit_message(embed=sEmbed, view=None, delete_after=30)
    
    async def create_server_table(self, interaction: discord.Interaction, subteams):
        columns = []
        for subteam in subteams:
            columns.append(f"{str(subteam)} TEXT,")
        columns = ", ".join([f"{str(subteam)} TEXT" for subteam in subteams])
        async with asqlite.connect('bot_storage.db') as conn:
            async with conn.cursor() as cursor:
                # Delete original table if it exists
                await cursor.execute(f'DROP TABLE IF EXISTS "{str(interaction.guild_id)}"')
                # Create new table depending on if verifying is required
                if self.verify_required == 1:
                    await cursor.execute(f'''CREATE TABLE
                                            "{str(interaction.guild_id)}"(first_name TEXT, last_name TEXT, discord_username TEXT, {columns})''')
                elif self.verify_required == 0:
                    await cursor.execute(f'''CREATE TABLE
                                            "{str(interaction.guild_id)}"(discord_username TEXT, {columns})''')
                else:
                    raise Exception(f"verify_required variable is not set to a correct value.\nCorrect values: [0, 1]\nCurrent value: {self.verify.required}")

                # Save (commit) the changes
                await conn.commit()