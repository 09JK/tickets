"""
Claim ticket command implementation.
"""

import logging
import discord
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.ticket import Ticket
from utils.permissions import is_staff

logger = logging.getLogger(__name__)


class ClaimCommand:
    """Handler for the /claim command."""
    
    def __init__(self, bot):
        """Initialize claim command handler."""
        self.bot = bot
    
    async def execute(self, ctx: discord.ApplicationContext):
        """Execute the claim ticket command."""
        await ctx.defer()
        
        async with self.bot.database.get_session() as session:
            # Check if this is a ticket channel
            ticket_result = await session.execute(
                select(Ticket).options(
                    selectinload(Ticket.category),
                    selectinload(Ticket.guild)
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
            
            # Check if claiming is enabled for this category
            if not ticket.category or not ticket.category.claiming:
                await ctx.respond(
                    "❌ Claiming is not enabled for this ticket category.",
                    ephemeral=True
                )
                return
            
            # Check if user is staff
            if not await is_staff(ctx.guild, ctx.author.id, session):
                await ctx.respond(
                    "❌ You don't have permission to claim tickets.",
                    ephemeral=True
                )
                return
            
            # Check if ticket is already claimed
            if ticket.claimed_by_id:
                claimed_member = ctx.guild.get_member(int(ticket.claimed_by_id))
                claimed_name = claimed_member.display_name if claimed_member else "Unknown User"
                await ctx.respond(
                    f"❌ This ticket is already claimed by {claimed_name}.",
                    ephemeral=True
                )
                return
            
            try:
                # Claim the ticket
                ticket.claimed_by_id = str(ctx.author.id)
                
                # Update channel permissions - only claimer can see it
                await ctx.channel.set_permissions(
                    ctx.author,
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
                
                # Remove permissions for other staff roles
                if ticket.category and ticket.category.staff_roles:
                    for role_id in ticket.category.staff_roles:
                        role = ctx.guild.get_role(int(role_id))
                        if role and role not in ctx.author.roles:
                            await ctx.channel.set_permissions(role, view_channel=False)
                
                await session.commit()
                
                # Update the opening message to show claim status
                try:
                    opening_message = await ctx.channel.fetch_message(int(ticket.opening_message_id))
                    if opening_message and opening_message.embeds:
                        embed = opening_message.embeds[0]
                        
                        # Add claimed field
                        embed.add_field(
                            name="🔒 Claimed by",
                            value=ctx.author.mention,
                            inline=True
                        )
                        
                        # Update buttons to show release option
                        from views.ticket_buttons import TicketButtonsView
                        view = TicketButtonsView(
                            claiming=True,
                            enable_feedback=ticket.category.enable_feedback,
                            is_claimed=True
                        )
                        
                        await opening_message.edit(embed=embed, view=view)
                        
                except discord.NotFound:
                    pass  # Opening message not found
                
                # Send claim confirmation
                embed = discord.Embed(
                    title="🔒 Ticket Claimed",
                    description=f"This ticket has been claimed by {ctx.author.mention}.",
                    color=discord.Color.blue()
                )
                
                await ctx.respond(embed=embed)
                
                logger.info(f"Ticket #{ticket.number} claimed by {ctx.author}")
                
            except Exception as e:
                logger.error(f"Error claiming ticket: {e}")
                await ctx.respond(
                    "❌ An error occurred while claiming the ticket.",
                    ephemeral=True
                )