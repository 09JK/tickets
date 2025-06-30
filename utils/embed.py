"""Extended Discord embed utilities."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import discord


try:
    import discord
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    # Create mock classes for testing without Discord
    class MockColor:
        def __init__(self, value=0):
            self.value = value
        
        @classmethod
        def blue(cls):
            return cls(0x0099ff)
        
        @classmethod
        def green(cls):
            return cls(0x00ff00)
        
        @classmethod
        def red(cls):
            return cls(0xff0000)
        
        @classmethod
        def yellow(cls):
            return cls(0xffff00)
    
    class MockEmbed:
        def __init__(self, **kwargs):
            self.title = kwargs.get('title')
            self.description = kwargs.get('description')
            self.color = kwargs.get('color')
            self.fields = []
            self.footer = {}
            self.author = {}
        
        def set_footer(self, text=None, icon_url=None):
            self.footer = {'text': text, 'icon_url': icon_url}
            return self
        
        def set_author(self, name=None, icon_url=None):
            self.author = {'name': name, 'icon_url': icon_url}
            return self
        
        def add_field(self, name, value, inline=True):
            self.fields.append({'name': name, 'value': value, 'inline': inline})
            return self
    
    # Use mock classes
    discord = type('MockDiscord', (), {
        'Color': MockColor,
        'Embed': MockEmbed,
    })()


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
        if not DISCORD_AVAILABLE:
            return self
            
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