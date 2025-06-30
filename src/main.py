"""
Discord Tickets Bot - Python Migration
A comprehensive ticket management bot for Discord servers.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import Settings
from config.database import Database
from utils.logger import setup_logging
import discord
from ezcord import Bot


async def main():
    """Main entry point for the Discord Tickets Bot."""
    # Load configuration
    settings = Settings()
    
    # Setup logging
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    
    # Initialize database
    database = Database(settings.database_url)
    await database.initialize()
    
    # Create bot instance
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    
    bot = Bot(
        intents=intents,
        sync_commands_on_cog_reload=True,
    )
    
    # Store settings and database in bot
    bot.settings = settings
    bot.database = database
    
    # Load cogs
    await bot.load_extension("cogs.tickets")
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.events")
    
    # Start the bot
    logger.info(f"Starting Discord Tickets Bot v{settings.version}")
    async with bot:
        await bot.start(settings.bot_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Failed to start bot: {e}")
        sys.exit(1)