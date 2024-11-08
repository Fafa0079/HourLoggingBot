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
        try:
            verify_required = 1
            await self.create_server_table(interaction=interaction, spreadsheet_url=self.spreadsheet_url, verifyRequired=verify_required)
        except Exception as e:
            rEmbed = discord.Embed(color=discord.Color.red(), 
                               title="Database Error", 
                               description=f"An error has occured with the database. Please contact the bot creator. \n\nDatabase Error: {e}")
            print(f"Database error: {e}")
            await interaction.response.edit_message(embed=rEmbed, view=None)
        else:
            await interaction.response.edit_message(embed=self.sEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url, verify_required))
        
    @discord.ui.button(label="❌", style=ButtonStyle.red, custom_id="decline")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            verify_required = 0
            await self.create_server_table(interaction=interaction, spreadsheet_url=self.spreadsheet_url, verifyRequired=verify_required)
        except Exception as e:
            rEmbed = discord.Embed(color=discord.Color.red(), 
                               title="Database Error", 
                               description=f"An error has occured with the database. Please contact the bot creator. \n\nDatabase Error: {e}")
            print(f"Database error: {e}")
            await interaction.response.edit_message(embed=rEmbed, view=None)
        else:
            await interaction.response.edit_message(embed=self.sEmbed, view=views.PlusMinus(self.gc, self.subteams, self.spreadsheet_url, verify_required))
        
    async def create_server_table(self, interaction: discord.Interaction, spreadsheet_url, verifyRequired):
        async with asqlite.connect('bot_storage.db') as conn:
            async with conn.cursor() as cursor:
                # Create table if table does not exist
                await cursor.execute('''CREATE TABLE IF NOT EXISTS
                                        server_config(server_id INTEGER, sheet_link TEXT, admin_channel INTEGER, verify_required INTEGER)''')
                
                # Delete existing entries from table
                await cursor.execute('DELETE FROM server_config WHERE server_id=?', (interaction.guild_id))

                # Insert a row of data
                await cursor.execute("REPLACE INTO server_config VALUES (?, ?, ?, ?)", (interaction.guild_id, spreadsheet_url, self.admin_channel_id, verifyRequired))

                # Save (commit) the changes
                await conn.commit()