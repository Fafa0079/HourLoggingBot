import asqlite
from views import SetupPages

import discord
from discord.ui import View
from discord import ButtonStyle

import views

class ToggleVerify(View):
    def __init__(self, gc, subteams, spreadsheet_url, admin_channel_id):
        super().__init__()
        self.gc = gc
        self.subteams = subteams
        self.spreadsheet_url = spreadsheet_url
        self.admin_channel_id = admin_channel_id
        self.sEmbed = discord.Embed(color=discord.Color.blue(), 
                               title="Add Subteams", 
                               description=f"Please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
        
    @discord.ui.button(label="✅", style=ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_server_table(interaction=interaction, spreadsheet_url=self.spreadsheet_url, verifyRequired=1)
        await interaction.response.edit_message(embed=self.sEmbed, view=views.PlusMinus(self.gc, self.subteams))
        
    @discord.ui.button(label="❌", style=ButtonStyle.red, custom_id="decline")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_server_table(interaction=interaction, spreadsheet_url=self.spreadsheet_url, verifyRequired=0)
        await interaction.response.edit_message(embed=self.sEmbed, view=views.PlusMinus(self.gc, self.subteams))
        
    async def create_server_table(self, interaction: discord.Interaction, spreadsheet_url, verifyRequired):
        try:
            async with asqlite.connect('serverlist.db') as conn:
                async with conn.cursor() as cursor:
                    # Create table
                    await cursor.execute('''CREATE TABLE IF NOT EXISTS
                                            sheet(server_id INTEGER, sheet_link TEXT, admin_channel INTEGER, verify_required INTEGER)''')

                    # Insert a row of data
                    await cursor.execute("REPLACE INTO sheet VALUES (?, ?, ?, ?)", (interaction.guild_id, spreadsheet_url, self.admin_channel_id, verifyRequired))

                    # Save (commit) the changes
                    await conn.commit()
        except Exception as e:
            print(f"Database error: {e}")