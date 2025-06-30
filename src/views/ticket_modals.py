"""
Modal forms for ticket questions and feedback.
"""

import discord
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.ticket import Ticket
from models.feedback import Feedback


class TicketQuestionModal(discord.ui.Modal):
    """Modal for ticket category questions."""
    
    def __init__(self, questions, category):
        """Initialize ticket question modal."""
        super().__init__(title=f"Questions - {category.name}")
        
        self.questions = questions
        self.category = category
        
        # Add up to 5 questions (Discord limit)
        for i, question in enumerate(questions[:5]):
            text_input = discord.ui.TextInput(
                label=question.label,
                placeholder=question.placeholder or "",
                default=question.value or "",
                required=question.required,
                max_length=question.max_length or 4000,
                style=discord.TextStyle.short if question.style == 1 else discord.TextStyle.long
            )
            self.add_item(text_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        await interaction.response.send_message(
            "✅ Thank you for the additional information!",
            ephemeral=True
        )
        
        # Store answers in database
        # This would require creating QuestionAnswer records
        # For now, just acknowledge submission


class FeedbackModal(discord.ui.Modal):
    """Modal for ticket feedback."""
    
    def __init__(self, close_reason: str = None):
        """Initialize feedback modal."""
        super().__init__(title="Ticket Feedback")
        
        self.close_reason = close_reason
        
        # Rating input
        self.rating_input = discord.ui.TextInput(
            label="Rating (1-5 stars)",
            placeholder="Rate your support experience from 1 to 5",
            required=True,
            max_length=1,
            style=discord.TextStyle.short
        )
        self.add_item(self.rating_input)
        
        # Comment input
        self.comment_input = discord.ui.TextInput(
            label="Comment (optional)",
            placeholder="Tell us about your experience...",
            required=False,
            max_length=1000,
            style=discord.TextStyle.long
        )
        self.add_item(self.comment_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle feedback submission."""
        try:
            # Validate rating
            rating = int(self.rating_input.value)
            if rating < 1 or rating > 5:
                await interaction.response.send_message(
                    "❌ Rating must be between 1 and 5.",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "❌ Rating must be a number between 1 and 5.",
                ephemeral=True
            )
            return
        
        # Save feedback
        async with interaction.client.database.get_session() as session:
            # Get ticket
            ticket_result = await session.execute(
                select(Ticket).where(Ticket.id == str(interaction.channel.id))
            )
            ticket = ticket_result.scalar_one_or_none()
            
            if ticket:
                # Create feedback record
                feedback = Feedback(
                    ticket_id=ticket.id,
                    guild_id=ticket.guild_id,
                    user_id=str(interaction.user.id),
                    rating=rating,
                    comment=self.comment_input.value or None
                )
                
                session.add(feedback)
                await session.commit()
                
                # Show thank you message
                stars = "⭐" * rating
                embed = discord.Embed(
                    title="✅ Feedback Submitted",
                    description=f"Thank you for your feedback!\n\nRating: {stars} ({rating}/5)",
                    color=discord.Color.green()
                )
                
                if self.comment_input.value:
                    embed.add_field(
                        name="Comment",
                        value=self.comment_input.value,
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed)
                
                # Now close the ticket if there was a close reason
                if self.close_reason is not None:
                    from commands.close import CloseCommand
                    close_command = CloseCommand(interaction.client)
                    await close_command.close_ticket(
                        interaction.channel,
                        str(interaction.user.id),
                        self.close_reason
                    )
            else:
                await interaction.response.send_message(
                    "❌ Could not save feedback - ticket not found.",
                    ephemeral=True
                )