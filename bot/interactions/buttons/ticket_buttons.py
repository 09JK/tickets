"""Button interactions for ticket management."""

import discord
from discord.ext import commands

from utils.embed import ExtendedEmbedBuilder


class TicketButtons(commands.Cog):
    """Cog for handling ticket button interactions."""
    
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log.buttons
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button interactions."""
        if interaction.type != discord.InteractionType.component:
            return
        
        custom_id = interaction.data.get("custom_id")
        if not custom_id:
            return
        
        # Handle ticket button interactions
        if custom_id == "ticket_claim":
            await self.handle_claim(interaction)
        elif custom_id == "ticket_close":
            await self.handle_close(interaction)
        elif custom_id == "ticket_edit":
            await self.handle_edit(interaction)
    
    async def handle_claim(self, interaction: discord.Interaction):
        """Handle ticket claim button."""
        try:
            # Check if user can claim tickets (has staff role)
            ticket = await self.bot.ticket_manager.get_ticket(str(interaction.channel.id))
            if not ticket:
                await interaction.response.send_message(
                    "❌ This is not a ticket channel!", ephemeral=True
                )
                return
            
            # Check if already claimed
            if ticket.claimed_by_id:
                await interaction.response.send_message(
                    "❌ This ticket is already claimed!", ephemeral=True
                )
                return
            
            # TODO: Check if user has staff permissions
            
            # Claim the ticket
            success = await self.bot.ticket_manager.claim_ticket(
                interaction.channel,
                interaction.user
            )
            
            if success:
                embed = ExtendedEmbedBuilder()
                embed.set_success_color()
                embed.set_title("Ticket Claimed")
                embed.set_description(f"Ticket claimed by {interaction.user.mention}")
                
                await interaction.response.send_message(embed=embed)
                self.log.info(f"Ticket {ticket.id} claimed by {interaction.user}")
            else:
                await interaction.response.send_message(
                    "❌ Failed to claim ticket!", ephemeral=True
                )
        
        except Exception as e:
            self.log.error(f"Error handling claim: {e}")
            await interaction.response.send_message(
                "❌ An error occurred!", ephemeral=True
            )
    
    async def handle_close(self, interaction: discord.Interaction):
        """Handle ticket close button."""
        try:
            ticket = await self.bot.ticket_manager.get_ticket(str(interaction.channel.id))
            if not ticket:
                await interaction.response.send_message(
                    "❌ This is not a ticket channel!", ephemeral=True
                )
                return
            
            # TODO: Check permissions (creator or staff)
            
            # Close the ticket
            embed = ExtendedEmbedBuilder()
            embed.set_warning_color()
            embed.set_title("Closing Ticket")
            embed.set_description("This ticket will be closed in a few seconds...")
            
            await interaction.response.send_message(embed=embed)
            
            # Close after a short delay
            await interaction.followup.send("Closing ticket...")
            
            success = await self.bot.ticket_manager.close_ticket(
                interaction.channel,
                interaction.user,
                "Closed via button"
            )
            
            if success:
                self.log.info(f"Ticket {ticket.id} closed by {interaction.user}")
            else:
                await interaction.followup.send("❌ Failed to close ticket!")
        
        except Exception as e:
            self.log.error(f"Error handling close: {e}")
            await interaction.response.send_message(
                "❌ An error occurred!", ephemeral=True
            )
    
    async def handle_edit(self, interaction: discord.Interaction):
        """Handle ticket edit button."""
        try:
            # TODO: Implement ticket editing (topic, questions)
            await interaction.response.send_message(
                "✏️ Ticket editing is not implemented yet!", ephemeral=True
            )
        
        except Exception as e:
            self.log.error(f"Error handling edit: {e}")
            await interaction.response.send_message(
                "❌ An error occurred!", ephemeral=True
            )


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(TicketButtons(bot))