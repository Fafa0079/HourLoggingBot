import modals

import discord
from discord.ui import Button, View
from discord import ButtonStyle
import gspread
from pathlib import Path

class SetupPages(View):
    def __init__(self, pages):
        super().__init__()
        self.page = 0
        self.pages = pages
       # Create buttons with unique custom_ids
        self.prev_button = Button(label="<", style=ButtonStyle.primary, custom_id="prev_button")
        self.pageinfo = Button(label=f"Step 1/{len(pages)}", style=ButtonStyle.secondary, custom_id="pageinfo", disabled=True)
        self.next_button = Button(label=">", style=ButtonStyle.primary, custom_id="next_button")
        self.plus_button = Button(label="+", style=ButtonStyle.green, custom_id="plus_button", disabled=True)

        # Add buttons to the view
        self.add_item(self.prev_button)
        self.add_item(self.pageinfo)
        self.add_item(self.next_button)
        self.add_item(self.plus_button)

        # Bind the buttons to their callback methods
        self.prev_button.callback = self.prev
        self.next_button.callback = self.next
        self.plus_button.callback = self.plus
        
    async def update_buttons(self):
        self.pageinfo.label = f"Step {self.page + 1}/{len(self.pages)}"
        self.plus_button.disabled = self.page != 1
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page == len(self.pages)-1
        self.next_button.disabled = self.page == 1

    async def prev(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.page], view=self)
    async def next(self, interaction: discord.Interaction):
        if self.page < len(self.pages) - 1:
            self.page += 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.page], view=self)
            
    async def plus(self, interaction: discord.Interaction):
        if self.page == 1:
            project_filepath = Path(__file__).parents[1]
            if not Path(fr"{project_filepath}\authorized_user.json").exists():   
                await interaction.response.defer() # blocker
                gspread.oauth(
                    credentials_filename=fr"{project_filepath}\credentials.json",
                    authorized_user_filename=fr"{project_filepath}\authorized_user.json",
                    scopes="https://www.googleapis.com/auth/drive.file"               
                )
            else:
                gc = gspread.oauth(
                    credentials_filename=fr"{project_filepath}\credentials.json",
                    authorized_user_filename=fr"{project_filepath}\authorized_user.json",
                    scopes="https://www.googleapis.com/auth/drive.file"               
                )
    
                await interaction.response.send_modal(modals.SetSheetName(gc, self.pages))
        else:
            print("Placeholder")