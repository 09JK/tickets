"""Close ticket command."""

import discord
from discord.ext import commands
from discord import app_commands

from utils.embed import ExtendedEmbedBuilder
from utils.users import is_staff


class CloseCommand(commands.Cog):
    """Close ticket command."""
    
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log.commands
    
    @app_commands.command(name="close", description="Close a ticket")
    @app_commands.describe(reason="Reason for closing the ticket")
    async def close_ticket(
        self, 
        interaction: discord.Interaction,
        reason: str = "No reason provided"
    ) -> None:
        """Close a ticket."""
        await interaction.response.defer()
        
        try:
            # Check if this is a ticket channel
            ticket = await self.bot.ticket_manager.get_ticket(str(interaction.channel.id))
            if not ticket:
                embed = ExtendedEmbedBuilder()
                embed.set_error_color()
                embed.set_title("Not a Ticket")
                embed.set_description("This command can only be used in ticket channels.")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Check permissions
            user_is_creator = ticket.created_by_id == str(interaction.user.id)
            user_is_staff = await is_staff(interaction.user, category=ticket.category)
            
            if not user_is_creator and not user_is_staff:
                embed = ExtendedEmbedBuilder()
                embed.set_error_color()
                embed.set_title("Permission Denied")
                embed.set_description("Only the ticket creator or staff can close tickets.")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Check if ticket is already closed
            if not ticket.open:
                embed = ExtendedEmbedBuilder()
                embed.set_error_color()
                embed.set_title("Already Closed")
                embed.set_description("This ticket is already closed.")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Confirm closure
            embed = ExtendedEmbedBuilder()
            embed.set_warning_color()
            embed.set_title("Closing Ticket")
            embed.set_description(f"Ticket #{ticket.number} will be closed in a few seconds...")
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
            # Close the ticket
            success = await self.bot.ticket_manager.close_ticket(
                interaction.channel,
                interaction.user,
                reason
            )
            
            if success:
                self.log.info(f"Ticket #{ticket.number} closed by {interaction.user} - Reason: {reason}")
            else:
                await interaction.followup.send("❌ Failed to close the ticket!")
            
        except Exception as e:
            self.log.error(f"Error in close command: {e}")
            
            error_embed = ExtendedEmbedBuilder()
            error_embed.set_error_color()
            error_embed.set_title("Error")
            error_embed.set_description("An error occurred while closing the ticket.")
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(CloseCommand(bot))