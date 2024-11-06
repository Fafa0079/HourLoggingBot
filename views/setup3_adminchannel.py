import asqlite
import modals
from views import SetupPages

import discord
from discord.ui import View
from discord import ButtonStyle, ChannelType

import views

class AdminChannel(View):
    def __init__(self, gc, spreadsheet_url):
        super().__init__()
        self.gc = gc
        self.spreadsheet_url = spreadsheet_url
        self.subteams = []
        self.channel_select = discord.ui.ChannelSelect(placeholder="Select channel...", channel_types=[ChannelType.text])
        self.channel_select.callback = self.selectChannel
        self.add_item(self.channel_select)
        
    async def selectChannel(self, interaction: discord.Interaction):
        selected_channel = self.channel_select.values[0]
        self.admin_channel = selected_channel
        self.admin_channel_id = selected_channel.id
        
        sEmbed = discord.Embed(color=discord.Color.blue(), 
                               title="Verify Command Usage", 
                               description=f"Hour approval channel *#{self.admin_channel.name}* selected! Now, please specify if you want to require users to *verify* with their first and last name before being able to log hours. First and last names will be displayed in the Google Sheets document if required.\n\n✅** = required**\n❌** = not required**")
        await interaction.response.edit_message(embed=sEmbed, view=views.ToggleVerify(self.gc, self.subteams, self.spreadsheet_url, self.admin_channel_id))