"""
Admin cog for administrative commands.
"""

import logging
import discord
from discord.ext import commands
from ezcord import Cog
from sqlalchemy import select, func
from models.guild import Guild
from models.ticket import Ticket
from models.category import Category
from utils.permissions import is_staff

logger = logging.getLogger(__name__)


class AdminCog(Cog):
    """Administrative commands for managing the ticket system."""
    
    def __init__(self, bot):
        """Initialize admin cog."""
        self.bot = bot
    
    @discord.slash_command(
        name="setup",
        description="Setup the ticket system for this server"
    )
    async def setup_command(self, ctx: discord.ApplicationContext):
        """Setup command for configuring the ticket system."""
        await ctx.defer()
        
        # Check permissions
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond("You need Manage Guild permission to use this command.", ephemeral=True)
            return
        
        async with self.bot.database.get_session() as session:
            # Get or create guild
            result = await session.execute(
                select(Guild).where(Guild.id == str(ctx.guild.id))
            )
            guild = result.scalar_one_or_none()
            
            if not guild:
                guild = Guild(
                    id=str(ctx.guild.id),
                    locale=ctx.guild.preferred_locale or "en-GB"
                )
                session.add(guild)
                await session.commit()
            
            # Check if categories exist
            cat_result = await session.execute(
                select(func.count(Category.id)).where(Category.guild_id == str(ctx.guild.id))
            )
            category_count = cat_result.scalar()
            
            embed = discord.Embed(
                title="🎫 Discord Tickets Setup",
                description="Welcome to Discord Tickets! Here's what you need to know:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 Current Status",
                value=f"Categories configured: {category_count}",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Next Steps",
                value=(
                    "1. Visit the web dashboard to configure categories\n"
                    f"2. Dashboard URL: {self.bot.settings.http_external}/settings/{ctx.guild.id}\n"
                    "3. Create ticket categories with staff roles\n"
                    "4. Configure channel names and permissions"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📚 Documentation",
                value="[Read the docs](https://discordtickets.app/docs) for detailed setup instructions",
                inline=False
            )
            
            embed.set_footer(text="Discord Tickets by eartharoid")
            
            await ctx.respond(embed=embed)
    
    @discord.slash_command(
        name="stats",
        description="View ticket statistics for this server"
    )
    async def stats_command(self, ctx: discord.ApplicationContext):
        """Show ticket statistics."""
        await ctx.defer()
        
        async with self.bot.database.get_session() as session:
            # Check if user is staff
            if not await is_staff(ctx.guild, ctx.author.id, session):
                await ctx.respond("You don't have permission to view statistics.", ephemeral=True)
                return
            
            # Get ticket counts
            total_result = await session.execute(
                select(func.count(Ticket.id)).where(Ticket.guild_id == str(ctx.guild.id))
            )
            total_tickets = total_result.scalar()
            
            open_result = await session.execute(
                select(func.count(Ticket.id)).where(
                    Ticket.guild_id == str(ctx.guild.id),
                    Ticket.open == True
                )
            )
            open_tickets = open_result.scalar()
            
            closed_tickets = total_tickets - open_tickets
            
            embed = discord.Embed(
                title="📊 Ticket Statistics",
                color=discord.Color.green()
            )
            
            embed.add_field(name="🎫 Total Tickets", value=str(total_tickets), inline=True)
            embed.add_field(name="📂 Open Tickets", value=str(open_tickets), inline=True)
            embed.add_field(name="✅ Closed Tickets", value=str(closed_tickets), inline=True)
            
            embed.set_footer(text=f"Server: {ctx.guild.name}")
            
            await ctx.respond(embed=embed)
    
    @discord.slash_command(
        name="settings",
        description="Get a link to the web dashboard"
    )
    async def settings_command(self, ctx: discord.ApplicationContext):
        """Provide link to web dashboard."""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond("You need Manage Guild permission to access settings.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚙️ Settings Dashboard",
            description=f"Access the web dashboard to configure your ticket system:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔗 Dashboard Link",
            value=f"[Open Dashboard]({self.bot.settings.http_external}/settings/{ctx.guild.id})",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ What you can configure:",
            value=(
                "• Ticket categories and permissions\n"
                "• Staff roles and ping settings\n"  
                "• Channel names and topics\n"
                "• Auto-close and working hours\n"
                "• Feedback and archiving settings"
            ),
            inline=False
        )
        
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(AdminCog(bot))