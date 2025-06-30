"""Discord Tickets Bot Client."""

import os
from typing import Optional

import discord
from discord.ext import commands
from ezcord import Bot

from config.env import get_settings
from utils.logger import get_bot_logger
from database.models import init_db
from bot.tickets.manager import TicketManager


class TicketsBot(Bot):
    """Main Discord Tickets Bot client."""
    
    def __init__(self):
        """Initialize the bot client."""
        self.settings = get_settings()
        self.log = get_bot_logger()
        
        # Setup intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_members = True
        intents.guild_messages = True
        intents.direct_messages = True
        intents.direct_message_reactions = True
        intents.direct_message_typing = True
        
        # Add guild presences for non-public bots
        if not self.settings.public_bot:
            intents.guild_presences = True
        
        super().__init__(
            command_prefix="!",  # Slash commands only, but required
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Initialize components
        self.ticket_manager: Optional[TicketManager] = None
        self.db_engine = None
        self.db_session_factory = None
        
    async def setup_hook(self) -> None:
        """Setup hook called when bot is starting."""
        self.log.base.info("Setting up bot...")
        
        # Initialize database
        from database.models import init_db
        self.db_engine, self.db_session_factory = await init_db(self.settings.db_connection_url or "sqlite:///tickets.db")
        
        # Initialize ticket manager
        self.ticket_manager = TicketManager(self)
        
        # Load extensions
        await self.load_extensions()
        
        # Sync commands if enabled
        if self.settings.publish_commands:
            self.log.base.info("Syncing application commands...")
            try:
                await self.tree.sync()
                self.log.base.info("Commands synced successfully")
            except Exception as e:
                self.log.base.error(f"Failed to sync commands: {e}")
    
    async def load_extensions(self) -> None:
        """Load all bot extensions."""
        extensions = [
            "bot.commands.tickets",
            # More extensions will be added here
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                self.log.base.debug(f"Loaded extension: {extension}")
            except Exception as e:
                self.log.base.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self) -> None:
        """Called when bot is ready."""
        self.log.base.info(f"Bot is ready! Logged in as {self.user}")
        self.log.base.info(f"Serving {len(self.guilds)} guilds")
        
        # Set status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for tickets | /new"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_error(self, event: str, *args, **kwargs) -> None:
        """Handle errors."""
        self.log.base.error(f"Error in event {event}", exc_info=True)
    
    async def start(self) -> None:
        """Start the bot."""
        try:
            await super().start(self.settings.discord_token)
        except Exception as e:
            self.log.base.error(f"Failed to start bot: {e}")
            raise
    
    async def close(self) -> None:
        """Close the bot and cleanup resources."""
        self.log.base.info("Shutting down bot...")
        
        # Close database engine
        if self.db_engine:
            await self.db_engine.dispose()
        
        await super().close()
        self.log.base.info("Bot shutdown complete")