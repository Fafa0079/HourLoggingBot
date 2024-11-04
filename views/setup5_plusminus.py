import modals
from views import SetupPages

import discord
from discord.ui import View
from discord import ButtonStyle

import views

class PlusMinus(View):
    def __init__(self, gc, subteams, spreadsheet_url):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
        self.spreadsheet_url = spreadsheet_url
        
    @discord.ui.button(label="+", style=ButtonStyle.green, custom_id="plus")
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(modals.AddSubteam(self.gc, self.subteams, self.spreadsheet_url))
        
    @discord.ui.button(label="-", style=ButtonStyle.red, custom_id="minus")
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.subteams.pop()
        except IndexError:
            rEmbed = discord.Embed(color=discord.Color.yellow(), 
                title="Add Subteams", 
                description=f"**Error: Cannot remove a subteam/group that does not exist. Please add more subteams/groups.**\n\nPlease add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
            await interaction.response.edit_message(embed=rEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url))
        else:
            sEmbed = discord.Embed(color=discord.Color.blue(), 
                title="Add Subteams", 
                description=f"Please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
            await interaction.response.edit_message(embed=sEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url))
        
    @discord.ui.button(label="Next", style=ButtonStyle.primary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.subteams) <= 0:
            rEmbed = discord.Embed(color=discord.Color.yellow(),
                title="Add Subteams", 
                description=f"**Error: Must have at least one subteam/group. Please add more subteams/groups.**\n\nPlease add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
            await interaction.response.edit_message(embed=rEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url))
        else:
            sEmbed = discord.Embed(color=discord.Color.green(), 
                title="Hour Logging Setup Complete", 
                description=f"Congratulations! You have completed the setup for the bot. You now may log hours to your newly created [spreadsheet]({self.spreadsheet_url}) using the `/log` command!)\n\nThis message will be cleared in 30 seconds.")
            await interaction.response.edit_message(embed=sEmbed, view=None, delete_after=30)