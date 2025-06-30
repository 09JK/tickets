"""
Core tickets cog with main ticket functionality.
"""

import logging
import discord
from discord.ext import commands
from ezcord import Cog
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from models.guild import Guild
from models.ticket import Ticket
from models.category import Category
from models.user import User
from utils.permissions import is_staff
from utils.i18n import get_locale_string
from views.ticket_buttons import TicketView
# from commands.new import NewCommand
# from commands.close import CloseCommand  
# from commands.claim import ClaimCommand

logger = logging.getLogger(__name__)


class TicketsCog(Cog):
    """Main cog for ticket functionality."""
    
    def __init__(self, bot):
        """Initialize tickets cog."""
        self.bot = bot
        
        # Add persistent views
        self.bot.add_view(TicketView())
    
    @discord.slash_command(
        name="new",
        description="Create a new support ticket"
    )
    async def new_ticket(
        self, 
        ctx: discord.ApplicationContext,
        references: str = discord.Option(
            str,
            description="Reference another ticket by ID",
            required=False
        )
    ):
        """Create a new ticket."""
        from commands.new import NewCommand
        await NewCommand(self.bot).execute(ctx, references)
    
    @discord.slash_command(
        name="close", 
        description="Close the current ticket"
    )
    async def close_ticket(
        self,
        ctx: discord.ApplicationContext,
        reason: str = discord.Option(
            str,
            description="Reason for closing the ticket",
            required=False
        )
    ):
        """Close a ticket."""
        from commands.close import CloseCommand
        await CloseCommand(self.bot).execute(ctx, reason)
    
    @discord.slash_command(
        name="claim",
        description="Claim the current ticket"
    )
    async def claim_ticket(self, ctx: discord.ApplicationContext):
        """Claim a ticket."""
        from commands.claim import ClaimCommand
        await ClaimCommand(self.bot).execute(ctx)
    
    @discord.slash_command(
        name="release",
        description="Release the current ticket"
    )
    async def release_ticket(self, ctx: discord.ApplicationContext):
        """Release a claimed ticket."""
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
                await ctx.respond("This command can only be used in ticket channels.", ephemeral=True)
                return
            
            # Check if user is staff
            if not await is_staff(ctx.guild, ctx.author.id, session):
                await ctx.respond("You don't have permission to release tickets.", ephemeral=True)
                return
            
            # Check if ticket is claimed
            if not ticket.claimed_by_id:
                await ctx.respond("This ticket is not claimed.", ephemeral=True)
                return
            
            # Check if user is the one who claimed it or has higher privileges
            if ticket.claimed_by_id != str(ctx.author.id) and not ctx.author.guild_permissions.manage_guild:
                await ctx.respond("You can only release tickets that you have claimed.", ephemeral=True)
                return
            
            # Release the ticket
            ticket.claimed_by_id = None
            
            # Update channel permissions
            if ticket.category:
                for role_id in ticket.category.staff_roles:
                    role = ctx.guild.get_role(int(role_id))
                    if role:
                        await ctx.channel.set_permissions(role, view_channel=True)
            
            await session.commit()
            
            embed = discord.Embed(
                title="🔓 Ticket Released",
                description=f"This ticket has been released by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            
            await ctx.respond(embed=embed)
    
    @discord.slash_command(
        name="tickets",
        description="View your tickets"
    )
    async def list_tickets(self, ctx: discord.ApplicationContext):
        """List user's tickets."""
        await ctx.defer()
        
        async with self.bot.database.get_session() as session:
            # Get user's open tickets
            open_result = await session.execute(
                select(Ticket).options(
                    selectinload(Ticket.category)
                ).where(
                    Ticket.guild_id == str(ctx.guild.id),
                    Ticket.created_by_id == str(ctx.author.id),
                    Ticket.open == True
                )
            )
            open_tickets = open_result.scalars().all()
            
            # Get user's recent closed tickets
            closed_result = await session.execute(
                select(Ticket).options(
                    selectinload(Ticket.category)
                ).where(
                    Ticket.guild_id == str(ctx.guild.id),
                    Ticket.created_by_id == str(ctx.author.id),
                    Ticket.open == False
                ).order_by(desc(Ticket.created_at)).limit(10)
            )
            closed_tickets = closed_result.scalars().all()
            
            embed = discord.Embed(
                title="🎫 Your Tickets",
                color=discord.Color.blue()
            )
            
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.display_avatar.url
            )
            
            if open_tickets:
                open_value = "\n".join([
                    f"• {ticket.category.name if ticket.category else 'Unknown'} #{ticket.number} (<#{ticket.id}>)"
                    for ticket in open_tickets
                ])
                embed.add_field(
                    name="📂 Open Tickets",
                    value=open_value,
                    inline=False
                )
            
            if closed_tickets:
                closed_value = "\n".join([
                    f"• {ticket.category.name if ticket.category else 'Unknown'} #{ticket.number}"
                    for ticket in closed_tickets[:5]  # Limit to 5 for display
                ])
                embed.add_field(
                    name="✅ Recent Closed Tickets",
                    value=closed_value,
                    inline=False
                )
            
            if not open_tickets and not closed_tickets:
                embed.description = "You don't have any tickets in this server."
            
            embed.set_footer(text=f"Use /new to create a new ticket")
            
            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(TicketsCog(bot))