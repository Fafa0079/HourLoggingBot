import modals

import traceback
import discord
from discord.ui import View
from discord import ButtonStyle

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
        await interaction.response.send_modal(modals.EditHours())
        
    @discord.ui.button(label="Deny", style=ButtonStyle.red, custom_id="deny", emoji="⛔")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(modals.DenyHours(self.user, self.time, self.subteam))