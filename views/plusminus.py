import modals
from views import SetupPages

import discord
from discord.ui import View
from discord import ButtonStyle

class PlusMinus(View):
    def __init__(self, gc, subteams):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
        
    @discord.ui.button(label="+", style=ButtonStyle.green, custom_id="plus")
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(modals.AddSubteam(self.gc, self.subteams))
        
    @discord.ui.button(label="-", style=ButtonStyle.red, custom_id="minus")
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.subteams.pop()
        await interaction.response.edit_message(self.gc, self.subteams)
        
    @discord.ui.button(label="Next", style=ButtonStyle.primary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.pages[self.page], view=SetupPages(self.pages))
        print("Placeholder")