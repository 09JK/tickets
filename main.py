#!/usr/bin/env python3
"""
Discord Tickets Bot - Python Version
Copyright (C) 2024 eartharoid & 09JK

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from config.env import load_environment
from utils.logger import setup_logger
from bot.client import TicketsBot


def print_banner() -> None:
    """Print the startup banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                     Discord Tickets Bot                      ║
║                      Python Version                          ║
║                                                               ║
║  An open-source Discord bot for ticket management            ║
║  https://discordtickets.app                                   ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version() -> None:
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


async def main() -> None:
    """Main entry point for the Discord Tickets Bot."""
    print_banner()
    check_python_version()
    
    # Load environment variables
    load_environment()
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Discord Tickets Bot...")
    
    try:
        # Initialize and start the bot
        bot = TicketsBot()
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")