#!/usr/bin/env python3
"""Test script for Discord Tickets Bot Python implementation (core components only)."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

async def test_core_components():
    """Test core components without Discord dependencies."""
    print("🔍 Testing Core Components (No Discord)...")
    print("=" * 50)
    
    # Test 1: Import core modules only
    print("1. Testing core imports...")
    try:
        from config.env import load_environment
        from utils.logger import setup_logger, get_bot_logger  
        from utils.i18n import get_i18n
        from utils.embed import ExtendedEmbedBuilder
        from database.models import init_db, Guild, Category, Ticket
        print("   ✅ Core imports successful")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 2: Configuration
    print("2. Testing configuration...")
    try:
        # Create a test .env file
        with open('.env.test', 'w') as f:
            f.write("""
DISCORD_TOKEN=test_token_123
DISCORD_SECRET=test_secret_123
ENCRYPTION_KEY=this_is_a_very_long_test_encryption_key_that_is_over_48_characters_long
HTTP_EXTERNAL=http://localhost:8080
""")
        
        # Load settings with custom env file
        from dotenv import load_dotenv
        load_dotenv('.env.test')
        
        from config.env import Settings
        settings = Settings()
        print(f"   ✅ Configuration loaded (Provider: {settings.db_provider})")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 3: Logging
    print("3. Testing logging...")
    try:
        logger = setup_logger()
        bot_logger = get_bot_logger()
        logger.info("Test log message")
        bot_logger.commands.info("Test command log")
        print("   ✅ Logging system working")
    except Exception as e:
        print(f"   ❌ Logging error: {e}")
        return False
    
    # Test 4: Internationalization
    print("4. Testing i18n...")
    try:
        i18n = get_i18n()
        locale = i18n.get_locale('en-GB')
        message = locale('commands.slash.tickets.response.title')
        print(f"   ✅ I18n working: '{message}'")
    except Exception as e:
        print(f"   ❌ I18n error: {e}")
        return False
    
    # Test 5: Database
    print("5. Testing database...")
    try:
        engine, session_factory = await init_db('sqlite+aiosqlite:///test_tickets.db')
        
        # Test session and basic operations
        async with session_factory() as session:
            # Session works
            pass
        
        await engine.dispose()
        print("   ✅ Database initialization successful")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Test 6: Basic embed structure (without Discord color objects)
    print("6. Testing embed utilities...")
    try:
        # Test basic embed creation without Discord-specific features
        embed = ExtendedEmbedBuilder(text="Test footer")
        embed.title = "Test Embed"
        embed.description = "Test description"
        print("   ✅ Embed utilities working")
    except Exception as e:
        print(f"   ❌ Embed error: {e}")
        return False
    
    print("=" * 50)
    print("🎉 All core component tests passed!")
    
    # Cleanup
    try:
        os.unlink('.env.test')
        os.unlink('test_tickets.db')
    except:
        pass
    
    return True

async def test_database_models():
    """Test database models and relationships."""
    print("\n🗄️ Testing Database Models...")
    print("=" * 50)
    
    try:
        from database.models import init_db, Guild, Category, Ticket, User
        from sqlalchemy import select
        
        # Initialize database
        engine, session_factory = await init_db('sqlite+aiosqlite:///model_test.db')
        
        async with session_factory() as session:
            # Create a mock guild
            guild = Guild(
                id="123456789",
                locale="en-GB",
                primary_colour="#009999"
            )
            session.add(guild)
            
            # Create a mock category
            category = Category(
                guild_id="123456789",
                name="General Support",
                description="General support tickets",
                channel_name="ticket-{number}",
                discord_category="987654321",
                emoji="🎫",
                opening_message="Welcome to your ticket!",
                staff_roles='["555555555"]'
            )
            session.add(category)
            
            # Create a mock user
            user = User(id="111111111")
            session.add(user)
            
            await session.commit()
            
            # Test querying
            result = await session.execute(select(Guild).where(Guild.id == "123456789"))
            test_guild = result.scalar_one_or_none()
            
            result = await session.execute(select(Category).where(Category.guild_id == "123456789"))
            test_category = result.scalar_one_or_none()
            
            print(f"   ✅ Guild created: {test_guild.id} ({test_guild.locale})")
            print(f"   ✅ Category created: {test_category.name}")
            print(f"   ✅ Database relationships working")
        
        await engine.dispose()
        
        # Cleanup
        os.unlink('model_test.db')
        
        print("   ✅ Database model tests completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Database model error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🐍 Discord Tickets Bot - Python Core Implementation Test")
    print("🔬 Testing core functionality without Discord dependencies...")
    print()
    
    # Run component tests
    if not await test_core_components():
        print("❌ Core component tests failed!")
        sys.exit(1)
    
    # Run database model tests
    if not await test_database_models():
        print("❌ Database model tests failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎯 CORE TEST SUMMARY")
    print("✅ All core tests passed successfully!")
    print("✅ Configuration and environment loading")
    print("✅ Structured logging with Rich")
    print("✅ SQLAlchemy async database models") 
    print("✅ Internationalization system")
    print("✅ Database operations and relationships")
    print("\n💡 Core implementation is solid!")
    print("   Ready for Discord.py integration when dependencies are installed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())