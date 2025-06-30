"""
Close confirmation view.
"""

import discord


class CloseConfirmationView(discord.ui.View):
    """View for confirming ticket closure."""
    
    def __init__(self, reason: str = None):
        """Initialize close confirmation view."""
        super().__init__(timeout=300)  # 5 minute timeout
        self.reason = reason
    
    @discord.ui.button(
        label="Confirm Close",
        style=discord.ButtonStyle.danger,
        emoji="✅"
    )
    async def confirm_close(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Confirm ticket closure."""
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(view=self)
        
        # Close the ticket
        from commands.close import CloseCommand
        close_command = CloseCommand(interaction.client)
        await close_command.close_ticket(
            interaction.channel,
            str(interaction.user.id),
            self.reason
        )
    
    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def cancel_close(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Cancel ticket closure."""
        embed = discord.Embed(
            title="❌ Close Cancelled",
            description="The ticket will remain open.",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)