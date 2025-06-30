"""New ticket command."""

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy import select

from database.models import Category
from utils.embed import ExtendedEmbedBuilder


class NewTicketView(discord.ui.View):
    """View for selecting ticket category."""
    
    def __init__(self, categories):
        super().__init__(timeout=300)
        self.categories = categories
        
        # Create select menu for categories
        if len(categories) > 1:
            options = []
            for category in categories[:25]:  # Discord limit
                options.append(discord.SelectOption(
                    label=category.name,
                    description=category.description[:100],
                    value=str(category.id),
                    emoji=category.emoji if category.emoji else None
                ))
            
            select = CategorySelect(options=options)
            self.add_item(select)
        else:
            # Single category, just show a button
            button = CreateTicketButton(category_id=categories[0].id, label=categories[0].name)
            self.add_item(button)


class CategorySelect(discord.ui.Select):
    """Select menu for choosing ticket category."""
    
    def __init__(self, options):
        super().__init__(
            placeholder="Choose a ticket category...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle category selection."""
        category_id = int(self.values[0])
        
        # Get the bot and ticket manager
        bot = interaction.client
        
        # Create the ticket
        async with bot.db_session_factory() as session:
            result = await session.execute(
                select(Category).where(Category.id == category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                await interaction.response.send_message(
                    "❌ Category not found!", ephemeral=True
                )
                return
            
            # Create ticket
            ticket = await bot.ticket_manager.create_ticket(
                guild=interaction.guild,
                category=category,
                user=interaction.user
            )
            
            if ticket:
                embed = ExtendedEmbedBuilder()
                embed.set_success_color()
                embed.set_title("Ticket Created!")
                embed.set_description(f"Your ticket has been created: <#{ticket.id}>")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = ExtendedEmbedBuilder()
                embed.set_error_color()
                embed.set_title("Error")
                embed.set_description("Failed to create ticket. Please try again.")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)


class CreateTicketButton(discord.ui.Button):
    """Button for creating a ticket in a specific category."""
    
    def __init__(self, category_id: int, label: str):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=f"Create {label} Ticket",
            emoji="🎫"
        )
        self.category_id = category_id
    
    async def callback(self, interaction: discord.Interaction):
        """Handle ticket creation."""
        # Get the bot and ticket manager
        bot = interaction.client
        
        # Create the ticket
        async with bot.db_session_factory() as session:
            result = await session.execute(
                select(Category).where(Category.id == self.category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                await interaction.response.send_message(
                    "❌ Category not found!", ephemeral=True
                )
                return
            
            # Create ticket
            ticket = await bot.ticket_manager.create_ticket(
                guild=interaction.guild,
                category=category,
                user=interaction.user
            )
            
            if ticket:
                embed = ExtendedEmbedBuilder()
                embed.set_success_color()
                embed.set_title("Ticket Created!")
                embed.set_description(f"Your ticket has been created: <#{ticket.id}>")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = ExtendedEmbedBuilder()
                embed.set_error_color()
                embed.set_title("Error")
                embed.set_description("Failed to create ticket. Please try again.")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)


class NewCommand(commands.Cog):
    """New ticket command."""
    
    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log.commands
    
    @app_commands.command(name="new", description="Create a new ticket")
    async def new_ticket(self, interaction: discord.Interaction) -> None:
        """Create a new ticket."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get available categories for this guild
            async with self.bot.db_session_factory() as session:
                result = await session.execute(
                    select(Category).where(Category.guild_id == str(interaction.guild.id))
                )
                categories = result.scalars().all()
            
            if not categories:
                embed = ExtendedEmbedBuilder()
                embed.set_error_color()
                embed.set_title("No Categories")
                embed.set_description("No ticket categories are configured for this server.")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create view with category selection
            view = NewTicketView(categories)
            
            embed = ExtendedEmbedBuilder()
            embed.set_color_from_hex("#009999")
            embed.set_title("Create New Ticket")
            embed.set_description("Please select a category for your ticket:")
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            self.log.info(f"{interaction.user} used new ticket command")
            
        except Exception as e:
            self.log.error(f"Error in new ticket command: {e}")
            
            error_embed = ExtendedEmbedBuilder()
            error_embed.set_error_color()
            error_embed.set_title("Error")
            error_embed.set_description("An error occurred while creating the ticket menu.")
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)


async def setup(bot):
    """Setup the cog."""
    await bot.add_cog(NewCommand(bot))