import discord

class EditHours(discord.ui.Modal, title="Edit Hours"):
    time = discord.ui.TextInput(
        label="Hours",
        placeholder="Enter new number of hours here...")
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            float(self.time.value)
        except (TypeError, ValueError) as e:
            rEmbed = discord.Embed(color=discord.Color.red(), 
                                   title="Edit Hours", 
                                   description=f"Error: Failed to edit hour request because {self.time.value} is not a number. Please input a valid number.\n\nFull error:{e}")
            await interaction.response.edit_message(embed=rEmbed)
            print("Likely user error above, ignore ^^^^^^^^^^^^^^^^^^")
        else:
            if float(self.time.value) < 0:
                rEmbed = discord.Embed(color=discord.Color.red(), 
                                       title="Edit Hours", 
                                       description=f"Error: Cannot log a negative number of {self.time.value} hours. Please input a positive number.")
                await interaction.response.edit_message(embed=rEmbed)
            else:
                # send google api request to add hours to spreadsheet
                sEmbed = discord.Embed(color = discord.Color.green(), 
                                       title="Edit Hours", 
                                       description=f"Sucessfully changed time to **{self.time.value}** hours and submitted hour request.")
                await interaction.response.edit_message(embed=sEmbed, view=None, delete_after=30)