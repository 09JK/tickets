"""
Permission utilities for checking user privileges.
"""

import logging
from typing import List, Optional
import discord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.guild import Guild
from models.category import Category

logger = logging.getLogger(__name__)


async def is_staff(guild: discord.Guild, user_id: int, session: AsyncSession) -> bool:
    """
    Check if a user is staff in a guild.
    
    Args:
        guild: Discord guild
        user_id: User ID to check
        session: Database session
        
    Returns:
        True if user is staff, False otherwise
    """
    try:
        # Check if user has Manage Guild permission
        member = guild.get_member(user_id)
        if not member:
            try:
                member = await guild.fetch_member(user_id)
            except discord.NotFound:
                return False
        
        if member.guild_permissions.manage_guild:
            return True
        
        # Get staff roles from categories
        result = await session.execute(
            select(Category.staff_roles).where(Category.guild_id == str(guild.id))
        )
        categories = result.fetchall()
        
        staff_roles = set()
        for category in categories:
            if category.staff_roles:
                staff_roles.update(category.staff_roles)
        
        # Check if user has any staff roles
        member_role_ids = [str(role.id) for role in member.roles]
        return bool(staff_roles.intersection(member_role_ids))
        
    except Exception as e:
        logger.error(f"Error checking staff status for user {user_id}: {e}")
        return False


async def get_privilege_level(member: Optional[discord.Member], super_users: List[str]) -> int:
    """
    Get user privilege level.
    
    Returns:
        4 = OPERATOR (SUPER)
        3 = GUILD_OWNER  
        2 = GUILD_ADMIN
        1 = GUILD_STAFF
        0 = GUILD_MEMBER
        -1 = NONE (NOT A MEMBER)
    """
    if not member:
        return -1
    
    if str(member.id) in super_users:
        return 4
    
    if member.guild.owner_id == member.id:
        return 3
        
    if member.guild_permissions.manage_guild:
        return 2
    
    # Would need database session to check staff status
    # For now, return member level
    return 0


def has_permission(user: discord.Member, required_level: int, super_users: List[str]) -> bool:
    """Check if user has required permission level."""
    user_level = get_privilege_level(user, super_users)
    return user_level >= required_level