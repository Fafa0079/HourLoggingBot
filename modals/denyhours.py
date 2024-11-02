import discord
import traceback

class DenyHours(discord.ui.Modal, title='Deny Hours'):
    def __init__(self, user, time, subteam):
        super().__init__()
        self.user = user
        self.time = time
        self.subteam = subteam
    reason = discord.ui.TextInput(
        label="Denial Reason",
        placeholder="Enter reason for denial here..."
    )
    async def on_submit(self, interaction: discord.Interaction):
        sEmbed = discord.Embed(color = discord.Color.green(), 
                               title="Deny Hours", 
                               description=f"Denied hour request and messaged {self.user}.\n\nReason:{self.reason}")
        uEmbed = discord.Embed(color = discord.Color.red(), 
                               title="Hour Request Declined", 
                               description=f"Your hour request of **{self.time}** hours in the **{self.subteam}** subteam was denied.\n\nReason: {self.reason}")
        await self.user.send(embed=uEmbed)
        await interaction.response.edit_message(embed=sEmbed, view=None, delete_after=30)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
        rEmbed = discord.Embed(color = discord.Color.red(), 
                               title="Edit Hours", 
                               description=f"Failed to decline hour request due to an unexpected error.\n\nError(s):\n\n{error}")
        await interaction.response.edit_message(embed=rEmbed, view=None)
        traceback.print_exception(type(error), error, error.__traceback__)