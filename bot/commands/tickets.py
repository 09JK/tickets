"""Tickets command - List user's tickets."""

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models import Ticket, Category
from utils.embed import ExtendedEmbedBuilder


class TicketsCommand(commands.Cog):
    """Tickets command for listing user tickets."""
    
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log.commands
    
    @app_commands.command(name="tickets", description="List your tickets")
    async def tickets(self, interaction: discord.Interaction) -> None:
        """List user's tickets."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get user's tickets
            async with self.bot.db_session_factory() as session:
                # Get open tickets
                open_result = await session.execute(
                    select(Ticket)
                    .options(selectinload(Ticket.category))
                    .where(
                        Ticket.created_by_id == str(interaction.user.id),
                        Ticket.guild_id == str(interaction.guild.id),
                        Ticket.open == True
                    )
                )
                open_tickets = open_result.scalars().all()
                
                # Get recent closed tickets (last 10)
                closed_result = await session.execute(
                    select(Ticket)
                    .options(selectinload(Ticket.category))
                    .where(
                        Ticket.created_by_id == str(interaction.user.id),
                        Ticket.guild_id == str(interaction.guild.id),
                        Ticket.open == False
                    )
                    .order_by(Ticket.closed_at.desc())
                    .limit(10)
                )
                closed_tickets = closed_result.scalars().all()
            
            # Create embed
            embed = ExtendedEmbedBuilder(
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
                text="Discord Tickets"
            )
            embed.set_color_from_hex("#009999")
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_title("Your Tickets")
            
            # Add open tickets field
            if open_tickets:
                open_list = []
                for ticket in open_tickets:
                    topic_preview = ""
                    if ticket.topic:
                        topic_preview = f" - `{ticket.topic[:30]}{'...' if len(ticket.topic) > 30 else ''}`"
                    
                    open_list.append(
                        f"> {ticket.category.name} #{ticket.number} (`{ticket.id}`){topic_preview}"
                    )
                
                embed.add_field(
                    name="Open Tickets",
                    value="\n".join(open_list),
                    inline=False
                )
            else:
                embed.add_field(
                    name="Open Tickets",
                    value="No open tickets",
                    inline=False
                )
            
            # Add closed tickets field
            if closed_tickets:
                closed_list = []
                for ticket in closed_tickets:
                    topic_preview = ""
                    if ticket.topic:
                        topic_preview = f" - `{ticket.topic[:30]}{'...' if len(ticket.topic) > 30 else ''}`"
                    
                    closed_list.append(
                        f"> {ticket.category.name} #{ticket.number} (`{ticket.id}`){topic_preview}"
                    )
                
                embed.add_field(
                    name="Recent Closed Tickets",
                    value="\n".join(closed_list),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            self.log.info(f"{interaction.user} used tickets command")
            
        except Exception as e:
            self.log.error(f"Error in tickets command: {e}")
            
            error_embed = ExtendedEmbedBuilder()
            error_embed.set_error_color()
            error_embed.set_title("Error")
            error_embed.set_description("An error occurred while fetching your tickets.")
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(TicketsCommand(bot))