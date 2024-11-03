import views

import discord
import traceback
import asqlite

class SetSheetName(discord.ui.Modal, title="Set Spreadsheet Name"):
    def __init__(self, gc, pages):
        super().__init__()
        self.gc = gc
        self.pages = pages
        self.name = discord.ui.TextInput(label="Spreadsheet Name", placeholder="Enter a name for the spreadsheet...", min_length=1, max_length=250)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        message_id = interaction.message.id
        await interaction.response.defer(thinking=True)
        spreadsheet = self.gc.create(str(self.name.value)) # Blocker, be aware. No other commands will work while this one is running. (bruh the async ver of this doesn't have oauth end user support :sob:)
        spreadsheet_url = spreadsheet.url
        sEmbed = discord.Embed(color=discord.Color.blue(), 
                               title="Select Hour Approval Channel", 
                               description=f"Google Sheets document created with the name '{self.name.value}'! \n\nLink to spreadsheet: {spreadsheet_url} \n\n Now, please select an output channel for hour logging requests to be set to. **It is highly recommended to make this an administrator-only channel, as anyone who can access this channel can accept or deny any hour logging request.**")
        await interaction.followup.edit_message(message_id=message_id, embed=sEmbed, view=views.AdminChannel(self.gc, spreadsheet_url))
        await interaction.delete_original_response()
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        message_id = interaction.message.id
        rEmbed = discord.Embed(color = discord.Color.red(), 
                               title="Create Spreadsheet", 
                               description=f"Failed to create spreadsheet due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.followup.edit_message(message_id=message_id, embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)
        