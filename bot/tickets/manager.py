"""Ticket management system."""

import json
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

import discord
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models import Ticket, Category, Guild, User, QuestionAnswer
from utils.embed import ExtendedEmbedBuilder

if TYPE_CHECKING:
    from bot.client import TicketsBot


class TicketManager:
    """Core ticket management functionality."""
    
    def __init__(self, bot: "TicketsBot"):
        """Initialize the ticket manager."""
        self.bot = bot
        self.log = bot.log.tickets
    
    async def get_ticket(self, channel_id: str) -> Optional[Ticket]:
        """Get a ticket by channel ID."""
        try:
            async with self.bot.db_session_factory() as session:
                result = await session.execute(
                    select(Ticket)
                    .options(
                        selectinload(Ticket.category),
                        selectinload(Ticket.guild),
                        selectinload(Ticket.created_by),
                        selectinload(Ticket.claimed_by),
                        selectinload(Ticket.question_answers).selectinload(QuestionAnswer.question)
                    )
                    .where(Ticket.id == channel_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            self.log.error(f"Error getting ticket {channel_id}: {e}")
            return None
    
    async def create_ticket(
        self,
        guild: discord.Guild,
        category: Category,
        user: discord.Member,
        topic: Optional[str] = None,
        question_answers: Optional[Dict[str, str]] = None
    ) -> Optional[Ticket]:
        """Create a new ticket."""
        try:
            # Get next ticket number
            async with self.bot.db_session_factory() as session:
                # Get highest ticket number for this category
                result = await session.execute(
                    select(Ticket.number)
                    .where(Ticket.category_id == category.id)
                    .order_by(Ticket.number.desc())
                    .limit(1)
                )
                last_number = result.scalar_one_or_none() or 0
                ticket_number = last_number + 1
                
                # Create channel
                channel_name = category.channel_name.replace("{number}", str(ticket_number))
                if "{topic}" in channel_name and topic:
                    channel_name = channel_name.replace("{topic}", topic[:50])
                
                # Create Discord channel
                discord_category = discord.utils.get(guild.categories, id=int(category.discord_category))
                if not discord_category:
                    self.log.error(f"Discord category {category.discord_category} not found")
                    return None
                
                # Set up permissions
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    user: discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                        attach_files=True,
                        embed_links=True
                    ),
                }
                
                # Add staff role permissions
                staff_roles = json.loads(category.staff_roles)
                for role_id in staff_roles:
                    role = guild.get_role(int(role_id))
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True,
                            manage_messages=True,
                            attach_files=True,
                            embed_links=True
                        )
                
                channel = await discord_category.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites
                )
                
                # Create ticket in database
                ticket = Ticket(
                    id=str(channel.id),
                    category_id=category.id,
                    guild_id=str(guild.id),
                    created_by_id=str(user.id),
                    number=ticket_number,
                    topic=topic,
                    open=True
                )
                
                session.add(ticket)
                await session.commit()
                
                # Send opening message
                await self.send_opening_message(channel, ticket, category, user)
                
                self.log.info(f"Created ticket #{ticket_number} for {user}")
                return ticket
                
        except Exception as e:
            self.log.error(f"Error creating ticket: {e}")
            return None
    
    async def send_opening_message(
        self,
        channel: discord.TextChannel,
        ticket: Ticket,
        category: Category,
        user: discord.Member
    ) -> None:
        """Send the opening message for a ticket."""
        try:
            # Get guild settings
            async with self.bot.db_session_factory() as session:
                result = await session.execute(
                    select(Guild).where(Guild.id == str(channel.guild.id))
                )
                guild_settings = result.scalar_one_or_none()
            
            if not guild_settings:
                return
            
            # Create embed
            embed = ExtendedEmbedBuilder(
                icon_url=channel.guild.icon.url if channel.guild.icon else None,
                text=guild_settings.footer
            )
            embed.set_color(guild_settings.primary_colour)
            embed.set_author(
                name=user.display_name,
                icon_url=user.display_avatar.url
            )
            embed.set_title(f"Ticket #{ticket.number}")
            embed.set_description(category.opening_message)
            
            if ticket.topic:
                embed.add_field(name="Topic", value=ticket.topic, inline=False)
            
            # Create action buttons
            view = discord.ui.View(timeout=None)
            
            if category.claiming:
                claim_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Claim",
                    emoji="🙋‍♂️",
                    custom_id="ticket_claim"
                )
                view.add_item(claim_button)
            
            close_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Close",
                emoji="🔒",
                custom_id="ticket_close"
            )
            view.add_item(close_button)
            
            # Send message
            message = await channel.send(
                content=f"<@{user.id}>",
                embed=embed,
                view=view
            )
            
            # Update ticket with opening message ID
            async with self.bot.db_session_factory() as session:
                await session.execute(
                    Ticket.__table__.update()
                    .where(Ticket.id == ticket.id)
                    .values(opening_message_id=str(message.id))
                )
                await session.commit()
                
        except Exception as e:
            self.log.error(f"Error sending opening message: {e}")
    
    async def close_ticket(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        reason: Optional[str] = None
    ) -> bool:
        """Close a ticket."""
        try:
            ticket = await self.get_ticket(str(channel.id))
            if not ticket or not ticket.open:
                return False
            
            # Update ticket in database
            async with self.bot.db_session_factory() as session:
                await session.execute(
                    Ticket.__table__.update()
                    .where(Ticket.id == ticket.id)
                    .values(
                        open=False,
                        closed_at=datetime.utcnow(),
                        closed_by_id=str(user.id),
                        closed_reason=reason
                    )
                )
                await session.commit()
            
            # Archive if enabled
            if ticket.guild.archive:
                await self.archive_ticket(ticket)
            
            # Delete channel
            await channel.delete(reason=f"Ticket closed by {user}")
            
            self.log.info(f"Closed ticket #{ticket.number}")
            return True
            
        except Exception as e:
            self.log.error(f"Error closing ticket: {e}")
            return False
    
    async def claim_ticket(
        self,
        channel: discord.TextChannel,
        user: discord.Member
    ) -> bool:
        """Claim a ticket."""
        try:
            ticket = await self.get_ticket(str(channel.id))
            if not ticket or not ticket.open or ticket.claimed_by_id:
                return False
            
            # Update ticket in database
            async with self.bot.db_session_factory() as session:
                await session.execute(
                    Ticket.__table__.update()
                    .where(Ticket.id == ticket.id)
                    .values(claimed_by_id=str(user.id))
                )
                await session.commit()
            
            # Update channel permissions
            await channel.set_permissions(
                user,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True
            )
            
            # Remove permissions for other staff
            staff_roles = json.loads(ticket.category.staff_roles)
            for role_id in staff_roles:
                role = channel.guild.get_role(int(role_id))
                if role:
                    await channel.set_permissions(role, view_channel=False)
            
            self.log.info(f"Ticket #{ticket.number} claimed by {user}")
            return True
            
        except Exception as e:
            self.log.error(f"Error claiming ticket: {e}")
            return False
    
    async def archive_ticket(self, ticket: Ticket) -> None:
        """Archive a ticket (placeholder for now)."""
        # TODO: Implement ticket archiving
        self.log.info(f"Archiving ticket #{ticket.number} (not implemented yet)")
        pass