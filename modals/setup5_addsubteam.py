import views

import discord
import traceback

class AddSubteam(discord.ui.Modal, title="Add Subteam"):
    def __init__(self, gc, subteams, spreadsheet_url):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
        self.spreadsheet_url = spreadsheet_url
    
    subteam_name = discord.ui.TextInput(label="Subteam Name", placeholder="Enter the name of the subteam to add...", min_length=1, max_length=250)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.subteams.append(str(self.subteam_name.value))
        sEmbed = discord.Embed(color=discord.Color.blue(), 
                title="Add Subteams", 
                description=f"Please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
        await interaction.response.edit_message(embed=sEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url))
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), 
                               title="Edit Hours", 
                               description=f"Failed to add subteam due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)