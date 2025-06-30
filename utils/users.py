"""User utility functions."""

import json
from typing import List, Optional

import discord
from sqlalchemy import select

from database.models import Guild, Category


async def is_staff(
    member: discord.Member,
    guild_settings: Optional[Guild] = None,
    category: Optional[Category] = None
) -> bool:
    """Check if a member is staff."""
    if member.guild_permissions.administrator:
        return True
    
    # Check if member has staff roles from category
    if category:
        staff_roles = json.loads(category.staff_roles)
        member_role_ids = [str(role.id) for role in member.roles]
        if any(role_id in member_role_ids for role_id in staff_roles):
            return True
    
    return False


async def get_user_permissions(
    member: discord.Member,
    guild_settings: Optional[Guild] = None
) -> dict:
    """Get user permissions and privilege level."""
    permissions = {
        "is_admin": member.guild_permissions.administrator,
        "is_staff": await is_staff(member, guild_settings),
        "can_create_tickets": True,  # Most users can create tickets
        "can_manage_tickets": False,
        "can_view_all_tickets": False,
    }
    
    if permissions["is_admin"]:
        permissions.update({
            "can_manage_tickets": True,
            "can_view_all_tickets": True,
        })
    elif permissions["is_staff"]:
        permissions.update({
            "can_manage_tickets": True,
            "can_view_all_tickets": True,
        })
    
    return permissions


def format_user_mention(user_id: str) -> str:
    """Format user ID as mention."""
    return f"<@{user_id}>"


def get_user_display_name(user: discord.Member) -> str:
    """Get user's display name."""
    return user.display_name or user.name