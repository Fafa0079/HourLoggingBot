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
        
        
    # @discord.ui.ChannelSelect(placeholder="Select channel...", channel_types=[ChannelType.text])
    async def selectChannel(self, interaction: discord.Interaction):
        selected_channel = self.channel_select.values[0]
        self.admin_channel = selected_channel
        self.admin_channel_id = selected_channel.id
        
        await self.create_server_table(interaction=interaction, spreadsheet_url=self.spreadsheet_url)
        sEmbed = discord.Embed(color=discord.Color.blue(), 
                               title="Add Subteams", 
                               description=f"Hour approval channel {self.admin_channel.name} selected! Now, please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
        await interaction.response.edit_message(embed=sEmbed, view=views.PlusMinus(self.gc, self.subteams))
    
    async def create_server_table(self, interaction: discord.Interaction, spreadsheet_url):
        try:
            async with asqlite.connect('serverlist.db') as conn:
                async with conn.cursor() as cursor:
                    # Create table
                    await cursor.execute('''CREATE TABLE IF NOT EXISTS
                                            sheet(server_id INTEGER, sheet_link TEXT, admin_channel INTEGER)''')

                    # Insert a row of data
                    await cursor.execute("REPLACE INTO sheet VALUES (?, ?, ?)", (interaction.guild_id, spreadsheet_url, self.admin_channel.id))

                    # Save (commit) the changes
                    await conn.commit()
        except Exception as e:
            print(f"Database error: {e}")