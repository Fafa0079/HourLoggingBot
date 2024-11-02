import views

import discord
import traceback
import asqlite

class SetSheetName(discord.ui.Modal, title="Set Spreadsheet Name"):
    def __init__(self, gc, pages):
        super().__init__()
        self.gc = gc
        self.pages = pages
        self.name = discord.ui.TextInput(label="Spreadsheet Name", placeholder="Enter a name for the spreadsheet...")
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        message_id = interaction.message.id
        await interaction.response.defer(thinking=True)
        spreadsheet = self.gc.create(str(self.name.value)) # Blocker, be aware. No other commands will work while this one is running. (bruh the async ver of this doesn't have oauth end user support :sob:)
        spreadsheet_url = spreadsheet.url
        self.subteams = {}
        sEmbed = discord.Embed(color=discord.Color.blue(), 
                               title="Add Subteams", 
                               description=f"Google Sheets document created with the name '{self.name.value}'! Now, please add all the subteams you want to be logged using the + button. **Please enter only one subteam at a time.**\n\nLink to spreadsheet: {spreadsheet_url} \n\nCurrent list: \n {self.subteams}\n\nIf you accidentally typed a subteam name wrong, or would like to remove a subteam, please press the - button.")
        await self.create_server_table(interaction=interaction, spreadsheet_url=spreadsheet_url)
        await interaction.followup.edit_message(message_id=message_id, embed=sEmbed, view=views.PlusMinus(self.gc, self.subteams))
        await interaction.delete_original_response()
        # else:
        #     rEmbed = discord.Embed(color=discord.Color.red(), title="Error", description="Error: No spreadsheet name provided. Please insert a valid spreadsheet name.")
        #     await interaction.response.edit_message(embed=rEmbed, view=SetupPages(self.pages))
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        message_id = interaction.message.id
        rEmbed = discord.Embed(color = discord.Color.red(), 
                               title="Create Spreadsheet", 
                               description=f"Failed to create spreadsheet due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.followup.edit_message(message_id=message_id, embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)
        
    async def create_server_table(self, interaction: discord.Interaction, spreadsheet_url):
        try:
            async with asqlite.connect('serverlist.db') as conn:
                async with conn.cursor() as cursor:
                    # Create table
                    await cursor.execute('''CREATE TABLE IF NOT EXISTS
                                            sheet(server_id INTEGER, sheet_link TEXT)''')

                    # Insert a row of data
                    await cursor.execute("REPLACE INTO sheet VALUES (?, ?)", (interaction.guild_id, spreadsheet_url))

                    # Save (commit) the changes
                    await conn.commit()
        except Exception as e:
            print(f"Database error: {e}")