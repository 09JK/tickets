"""
New ticket command implementation.
"""

import logging
import discord
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from models.guild import Guild
from models.category import Category
from models.ticket import Ticket
from models.user import User
from views.category_select import CategorySelectView
from views.ticket_modals import TicketQuestionModal

logger = logging.getLogger(__name__)


class NewCommand:
    """Handler for the /new command."""
    
    def __init__(self, bot):
        """Initialize new command handler."""
        self.bot = bot
    
    async def execute(self, ctx: discord.ApplicationContext, references: str = None):
        """Execute the new ticket command."""
        await ctx.defer()
        
        async with self.bot.database.get_session() as session:
            # Get guild settings
            guild_result = await session.execute(
                select(Guild).options(
                    selectinload(Guild.categories)
                ).where(Guild.id == str(ctx.guild.id))
            )
            guild = guild_result.scalar_one_or_none()
            
            if not guild:
                await ctx.respond(
                    "This server is not configured for tickets. Please ask an administrator to run `/setup`.",
                    ephemeral=True
                )
                return
            
            # Check if categories exist
            if not guild.categories:
                embed = discord.Embed(
                    title="❌ No Categories",
                    description=(
                        "No ticket categories have been configured for this server.\n\n"
                        f"[Configure categories]({self.bot.settings.http_external}/settings/{ctx.guild.id})"
                    ),
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return
            
            # Check user's open tickets
            open_tickets_result = await session.execute(
                select(func.count(Ticket.id)).where(
                    Ticket.guild_id == str(ctx.guild.id),
                    Ticket.created_by_id == str(ctx.author.id),
                    Ticket.open == True
                )
            )
            open_tickets_count = open_tickets_result.scalar()
            
            # For now, allow unlimited tickets per user
            # In the future, this could be configurable per category
            
            # If only one category, create ticket directly
            if len(guild.categories) == 1:
                category = guild.categories[0]
                await self._create_ticket(ctx, session, category, references)
            else:
                # Multiple categories, show selection menu
                view = CategorySelectView(guild.categories, references)
                embed = discord.Embed(
                    title="🎫 Create New Ticket",
                    description="Please select a category for your ticket:",
                    color=discord.Color.blue()
                )
                await ctx.respond(embed=embed, view=view, ephemeral=True)
    
    async def _create_ticket(
        self, 
        ctx: discord.ApplicationContext, 
        session, 
        category: Category, 
        references: str = None
    ):
        """Create a new ticket in the specified category."""
        try:
            # Get next ticket number for this guild
            max_number_result = await session.execute(
                select(func.max(Ticket.number)).where(Ticket.guild_id == str(ctx.guild.id))
            )
            max_number = max_number_result.scalar() or 0
            ticket_number = max_number + 1
            
            # Get Discord category
            discord_category = ctx.guild.get_channel(int(category.discord_category))
            if not discord_category:
                await ctx.respond(
                    f"❌ Category channel not found. Please check the configuration.",
                    ephemeral=True
                )
                return
            
            # Generate channel name
            channel_name = category.channel_name.format(
                username=ctx.author.name,
                displayName=ctx.author.display_name,
                number=ticket_number
            )
            
            # Create channel permissions
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                ctx.author: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),
                ctx.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True
                )
            }
            
            # Add staff roles
            for role_id in category.staff_roles:
                role = ctx.guild.get_role(int(role_id))
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True
                    )
            
            # Create the channel
            channel = await discord_category.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"Support ticket #{ticket_number} | Created by {ctx.author}"
            )
            
            # Create ticket record
            ticket = Ticket(
                id=str(channel.id),
                guild_id=str(ctx.guild.id),
                category_id=category.id,
                number=ticket_number,
                created_by_id=str(ctx.author.id),
                references_ticket_id=references if references else None,
                opening_message_id="0"  # Will be updated after sending
            )
            
            session.add(ticket)
            await session.commit()
            
            # Send opening message
            embed = discord.Embed(
                title=f"🎫 Ticket #{ticket_number}",
                description=category.opening_message.format(
                    user=ctx.author.mention,
                    username=ctx.author.name,
                    displayName=ctx.author.display_name
                ),
                color=discord.Color.green()
            )
            
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.display_avatar.url
            )
            
            # Add ticket buttons
            from views.ticket_buttons import TicketButtonsView
            view = TicketButtonsView(category.claiming, category.enable_feedback)
            
            opening_message = await channel.send(embed=embed, view=view)
            
            # Update ticket with opening message ID
            ticket.opening_message_id = str(opening_message.id)
            await session.commit()
            
            # Ping roles if configured
            if category.ping_roles:
                ping_content = " ".join([
                    f"<@&{role_id}>" for role_id in category.ping_roles
                ])
                await channel.send(ping_content, delete_after=5)
            
            # If category has questions, show modal
            if category.questions:
                # For now, skip questions modal and just notify about ticket creation
                pass
            
            # Respond to user
            await ctx.respond(
                f"✅ Ticket created! {channel.mention}",
                ephemeral=True
            )
            
            logger.info(f"Ticket #{ticket_number} created by {ctx.author} in {ctx.guild.name}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await ctx.respond(
                "❌ An error occurred while creating your ticket. Please try again.",
                ephemeral=True
            )