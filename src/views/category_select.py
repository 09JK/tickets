"""
Category selection dropdown for new tickets.
"""

import discord
from typing import List
from models.category import Category


class CategorySelectView(discord.ui.View):
    """View for selecting ticket category."""
    
    def __init__(self, categories: List[Category], references: str = None):
        """Initialize category select view."""
        super().__init__(timeout=300)  # 5 minute timeout
        
        self.categories = categories
        self.references = references
        
        # Add select menu
        self.add_item(CategorySelect(categories, references))


class CategorySelect(discord.ui.Select):
    """Select menu for choosing ticket category."""
    
    def __init__(self, categories: List[Category], references: str = None):
        """Initialize category select menu."""
        self.categories = categories
        self.references = references
        
        # Create options
        options = []
        for category in categories:
            options.append(discord.SelectOption(
                label=category.name,
                description=category.description[:100],  # Max 100 chars
                emoji=category.emoji,
                value=str(category.id)
            ))
        
        super().__init__(
            placeholder="Choose a category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket:category_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle category selection."""
        # Get selected category
        category_id = int(self.values[0])
        selected_category = next(
            (cat for cat in self.categories if cat.id == category_id),
            None
        )
        
        if not selected_category:
            await interaction.response.send_message(
                "❌ Invalid category selected.",
                ephemeral=True
            )
            return
        
        # Create ticket with selected category
        from commands.new import NewCommand
        
        async with interaction.client.database.get_session() as session:
            # Create a fake context for the new command
            class FakeCtx:
                def __init__(self, interaction):
                    self.interaction = interaction
                    self.guild = interaction.guild
                    self.author = interaction.user
                    self.channel = interaction.channel
                
                async def respond(self, *args, **kwargs):
                    if interaction.response.is_done():
                        await interaction.followup.send(*args, **kwargs)
                    else:
                        await interaction.response.send_message(*args, **kwargs)
            
            ctx = FakeCtx(interaction)
            new_command = NewCommand(interaction.client)
            
            await new_command._create_ticket(
                ctx, 
                session, 
                selected_category, 
                self.references
            )