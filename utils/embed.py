"""Extended Discord embed utilities."""

from typing import Optional

import discord


class ExtendedEmbedBuilder(discord.Embed):
    """Extended embed builder with additional utilities."""
    
    def __init__(
        self,
        *,
        icon_url: Optional[str] = None,
        text: Optional[str] = None,
        **kwargs
    ):
        """Initialize the extended embed builder."""
        super().__init__(**kwargs)
        
        if text:
            self.set_footer(text=text, icon_url=icon_url)
    
    def set_color_from_hex(self, hex_color: str) -> "ExtendedEmbedBuilder":
        """Set color from hex string."""
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        
        try:
            color_int = int(hex_color, 16)
            self.color = discord.Color(color_int)
        except ValueError:
            # Fallback to default color
            self.color = discord.Color.blue()
        
        return self
    
    def set_success_color(self) -> "ExtendedEmbedBuilder":
        """Set success (green) color."""
        self.color = discord.Color.green()
        return self
    
    def set_error_color(self) -> "ExtendedEmbedBuilder":
        """Set error (red) color."""
        self.color = discord.Color.red()
        return self
    
    def set_warning_color(self) -> "ExtendedEmbedBuilder":
        """Set warning (yellow) color."""
        self.color = discord.Color.yellow()
        return self
    
    def add_blank_field(self, inline: bool = False) -> "ExtendedEmbedBuilder":
        """Add a blank field for spacing."""
        self.add_field(name="\u200b", value="\u200b", inline=inline)
        return self