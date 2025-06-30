"""
Internationalization (i18n) utilities.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class I18nManager:
    """Manages internationalization strings."""
    
    def __init__(self):
        """Initialize i18n manager."""
        self.locales: Dict[str, Dict[str, Any]] = {}
        self.default_locale = "en-GB"
    
    def load_locales(self, locale_dir: Path):
        """Load locale files from directory."""
        try:
            for locale_file in locale_dir.glob("*.yml"):
                locale_name = locale_file.stem
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.locales[locale_name] = yaml.safe_load(f)
                logger.info(f"Loaded locale: {locale_name}")
        except Exception as e:
            logger.error(f"Error loading locales: {e}")
    
    def get_string(self, key: str, locale: str = None, **kwargs) -> str:
        """
        Get localized string by key.
        
        Args:
            key: Dot-separated key path (e.g., "commands.slash.new.description")
            locale: Locale code (defaults to default_locale)
            **kwargs: Formatting arguments
            
        Returns:
            Localized string
        """
        locale = locale or self.default_locale
        
        # Get locale data
        locale_data = self.locales.get(locale, self.locales.get(self.default_locale, {}))
        
        # Navigate to the key
        current = locale_data
        for part in key.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Key not found, return the key itself
                logger.warning(f"i18n key not found: {key} (locale: {locale})")
                return key
        
        # If we have a string, format it with kwargs
        if isinstance(current, str):
            try:
                return current.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.error(f"Error formatting i18n string {key}: {e}")
                return current
        
        # If not a string, return the key
        return key
    
    def get_all_strings(self, key: str) -> Dict[str, str]:
        """Get string for all available locales."""
        result = {}
        for locale in self.locales.keys():
            result[locale] = self.get_string(key, locale)
        return result


# Global i18n manager
_i18n_manager = None


def setup_i18n(locale_dir: Optional[Path] = None) -> I18nManager:
    """Setup global i18n manager."""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
        if locale_dir and locale_dir.exists():
            _i18n_manager.load_locales(locale_dir)
    return _i18n_manager


def get_locale_string(key: str, locale: str = None, **kwargs) -> str:
    """Get localized string using global i18n manager."""
    if _i18n_manager is None:
        return key
    return _i18n_manager.get_string(key, locale, **kwargs)