"""
Close ticket command implementation.
"""

import logging
import discord
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.ticket import Ticket
from utils.permissions import is_staff
from views.close_confirmation import CloseConfirmationView

logger = logging.getLogger(__name__)


class CloseCommand:
    """Handler for the /close command."""
    
    def __init__(self, bot):
        """Initialize close command handler."""
        self.bot = bot
    
    async def execute(self, ctx: discord.ApplicationContext, reason: str = None):
        """Execute the close ticket command."""
        await ctx.defer()
        
        async with self.bot.database.get_session() as session:
            # Check if this is a ticket channel
            ticket_result = await session.execute(
                select(Ticket).options(
                    selectinload(Ticket.category),
                    selectinload(Ticket.guild),
                    selectinload(Ticket.created_by)
                ).where(Ticket.id == str(ctx.channel.id))
            )
            ticket = ticket_result.scalar_one_or_none()
            
            if not ticket:
                await ctx.respond(
                    "❌ This command can only be used in ticket channels.",
                    ephemeral=True
                )
                return
            
            if not ticket.open:
                await ctx.respond(
                    "❌ This ticket is already closed.",
                    ephemeral=True
                )
                return
            
            # Check permissions
            user_is_staff = await is_staff(ctx.guild, ctx.author.id, session)
            is_ticket_owner = ticket.created_by_id == str(ctx.author.id)
            
            if not user_is_staff and not is_ticket_owner:
                await ctx.respond(
                    "❌ You don't have permission to close this ticket.",
                    ephemeral=True
                )
                return
            
            # If ticket owner is closing and feedback is enabled, show feedback modal first
            if (is_ticket_owner and 
                ticket.category and 
                ticket.category.enable_feedback and 
                not ticket.feedback):
                
                from views.feedback_modal import FeedbackModal
                modal = FeedbackModal(reason)
                await ctx.response.send_modal(modal)
                return
            
            # Show confirmation dialog
            embed = discord.Embed(
                title="🔒 Close Ticket",
                description="Are you sure you want to close this ticket?",
                color=discord.Color.orange()
            )
            
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            
            view = CloseConfirmationView(reason)
            await ctx.respond(embed=embed, view=view)
    
    async def close_ticket(self, channel: discord.TextChannel, closed_by_id: str, reason: str = None):
        """Actually close the ticket."""
        async with self.bot.database.get_session() as session:
            # Get ticket
            ticket_result = await session.execute(
                select(Ticket).options(
                    selectinload(Ticket.category),
                    selectinload(Ticket.guild)
                ).where(Ticket.id == str(channel.id))
            )
            ticket = ticket_result.scalar_one_or_none()
            
            if not ticket or not ticket.open:
                return
            
            try:
                # Update ticket in database
                ticket.open = False
                ticket.closed_by_id = closed_by_id
                ticket.closed_reason = reason
                
                await session.commit()
                
                # Send closing message
                embed = discord.Embed(
                    title="✅ Ticket Closed",
                    description="This ticket has been closed.",
                    color=discord.Color.green()
                )
                
                if reason:
                    embed.add_field(name="Reason", value=reason, inline=False)
                
                embed.add_field(
                    name="Closed by",
                    value=f"<@{closed_by_id}>",
                    inline=True
                )
                
                await channel.send(embed=embed)
                
                # Archive or delete channel after delay
                import asyncio
                await asyncio.sleep(5)  # 5 second delay
                
                if ticket.guild.archive:
                    # In a full implementation, we'd create an archive here
                    # For now, just rename the channel to indicate it's closed
                    try:
                        await channel.edit(name=f"closed-{ticket.number}")
                        
                        # Remove user permissions but keep staff
                        creator = channel.guild.get_member(int(ticket.created_by_id))
                        if creator:
                            await channel.set_permissions(creator, view_channel=False)
                        
                    except discord.HTTPException:
                        pass
                else:
                    # Delete the channel
                    try:
                        await channel.delete(reason="Ticket closed")
                    except discord.HTTPException:
                        pass
                
                logger.info(f"Ticket #{ticket.number} closed by {closed_by_id}")
                
            except Exception as e:
                logger.error(f"Error closing ticket: {e}")