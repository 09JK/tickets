"""
Events cog for handling Discord events.
"""

import logging
import discord
from discord.ext import commands
from ezcord import Cog
from sqlalchemy import select
from models.guild import Guild
from models.user import User

logger = logging.getLogger(__name__)


class EventsCog(Cog):
    """Handle Discord events."""
    
    def __init__(self, bot):
        """Initialize events cog."""
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.bot.user}")
        logger.info(f"Connected to {len(self.bot.guilds)} guilds")
    
    @commands.Cog.listener() 
    async def on_guild_join(self, guild: discord.Guild):
        """Called when bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} ({guild.id})")
        
        # Create guild record if it doesn't exist
        async with self.bot.database.get_session() as session:
            result = await session.execute(
                select(Guild).where(Guild.id == str(guild.id))
            )
            existing_guild = result.scalar_one_or_none()
            
            if not existing_guild:
                new_guild = Guild(
                    id=str(guild.id),
                    locale=guild.preferred_locale or "en-GB"
                )
                session.add(new_guild)
                await session.commit()
                logger.info(f"Created guild record for {guild.name}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} ({guild.id})")
    
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        """Handle application command errors."""
        logger.error(f"Command error in {ctx.command}: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Send error message to user
        error_msg = "An error occurred while processing your request."
        if hasattr(ctx, "respond"):
            try:
                if ctx.response.is_done():
                    await ctx.followup.send(error_msg, ephemeral=True)
                else:
                    await ctx.respond(error_msg, ephemeral=True)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Called for all interactions."""
        # Ensure guild and user exist in database
        if interaction.guild:
            async with self.bot.database.get_session() as session:
                # Ensure guild exists
                guild_result = await session.execute(
                    select(Guild).where(Guild.id == str(interaction.guild.id))
                )
                guild_record = guild_result.scalar_one_or_none()
                
                if not guild_record:
                    guild_record = Guild(
                        id=str(interaction.guild.id),
                        locale=interaction.guild.preferred_locale or "en-GB"
                    )
                    session.add(guild_record)
                
                # Ensure user exists
                user_result = await session.execute(
                    select(User).where(User.id == str(interaction.user.id))
                )
                user_record = user_result.scalar_one_or_none()
                
                if not user_record:
                    user_record = User(id=str(interaction.user.id))
                    session.add(user_record)
                
                await session.commit()


def setup(bot):
    bot.add_cog(EventsCog(bot))