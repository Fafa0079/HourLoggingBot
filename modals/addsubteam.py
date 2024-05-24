import views

import discord
import traceback

class AddSubteam(discord.ui.Modal, title="Add Subteam"):
    def __init__(self, gc, subteams):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
    
    subteam_name = discord.ui.TextInput(label="Subteam Name", placeholder="Enter the name of the subteam to add...")
    
    async def on_submit(self, interaction: discord.Interaction):
        self.subteams.append(self.subteam_name)
        await interaction.response.edit_message(view=views.PlusMinus(self.gc, self.subteams))
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), title="Edit Hours", description=f"Failed to add subteam due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)