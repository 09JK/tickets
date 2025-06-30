"""
Button interactions for tickets.
"""

import discord
from discord.ext import commands


class TicketButtonsView(discord.ui.View):
    """View containing ticket action buttons."""
    
    def __init__(self, claiming: bool = False, enable_feedback: bool = False, is_claimed: bool = False):
        """Initialize ticket buttons view."""
        super().__init__(timeout=None)
        
        self.claiming = claiming
        self.enable_feedback = enable_feedback
        self.is_claimed = is_claimed
        
        # Add claim/release button if claiming is enabled
        if claiming:
            if is_claimed:
                self.add_item(ReleaseButton())
            else:
                self.add_item(ClaimButton())
        
        # Always add close button
        self.add_item(CloseButton())


class TicketView(discord.ui.View):
    """Persistent view for ticket buttons."""
    
    def __init__(self):
        super().__init__(timeout=None)


class ClaimButton(discord.ui.Button):
    """Button to claim a ticket."""
    
    def __init__(self):
        super().__init__(
            label="Claim",
            style=discord.ButtonStyle.primary,
            emoji="🔒",
            custom_id="ticket:claim"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle claim button click."""
        from commands.claim import ClaimCommand
        
        # Convert to ApplicationContext-like object
        class FakeCtx:
            def __init__(self, interaction):
                self.interaction = interaction
                self.channel = interaction.channel
                self.guild = interaction.guild
                self.author = interaction.user
                self.respond = interaction.response.send_message
            
            async def defer(self):
                await self.interaction.response.defer()
        
        ctx = FakeCtx(interaction)
        await ClaimCommand(interaction.client).execute(ctx)


class ReleaseButton(discord.ui.Button):
    """Button to release a claimed ticket."""
    
    def __init__(self):
        super().__init__(
            label="Release",
            style=discord.ButtonStyle.secondary,
            emoji="🔓",
            custom_id="ticket:release"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle release button click."""
        # Similar implementation to claim but for release
        await interaction.response.send_message(
            "🔓 Ticket released!",
            ephemeral=True
        )


class CloseButton(discord.ui.Button):
    """Button to close a ticket."""
    
    def __init__(self):
        super().__init__(
            label="Close",
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id="ticket:close"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle close button click."""
        from commands.close import CloseCommand
        
        # Convert to ApplicationContext-like object
        class FakeCtx:
            def __init__(self, interaction):
                self.interaction = interaction
                self.channel = interaction.channel
                self.guild = interaction.guild
                self.author = interaction.user
                self.respond = interaction.response.send_message
            
            async def defer(self):
                await self.interaction.response.defer()
        
        ctx = FakeCtx(interaction)
        await CloseCommand(interaction.client).execute(ctx)