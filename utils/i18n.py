"""Internationalization support."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class I18n:
    """Internationalization manager."""
    
    def __init__(self, locales_dir: str = "locales"):
        """Initialize the i18n manager."""
        self.locales_dir = Path(locales_dir)
        self.locales: Dict[str, Dict[str, Any]] = {}
        self.default_locale = "en-GB"
        
        # Load locales
        self.load_locales()
    
    def load_locales(self) -> None:
        """Load all locale files."""
        if not self.locales_dir.exists():
            return
        
        for locale_file in self.locales_dir.glob("*.yml"):
            locale_name = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.locales[locale_name] = yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading locale {locale_name}: {e}")
    
    def get_locale(self, locale: str = None) -> "LocaleGetter":
        """Get a locale getter for the specified locale."""
        if locale is None or locale not in self.locales:
            locale = self.default_locale
        
        return LocaleGetter(self.locales.get(locale, {}), self.locales.get(self.default_locale, {}))


class LocaleGetter:
    """Locale string getter."""
    
    def __init__(self, locale_data: Dict[str, Any], fallback_data: Dict[str, Any]):
        """Initialize the locale getter."""
        self.locale_data = locale_data
        self.fallback_data = fallback_data
    
    def __call__(self, key: str, **kwargs) -> str:
        """Get a localized string."""
        return self.get(key, **kwargs)
    
    def get(self, key: str, **kwargs) -> str:
        """Get a localized string with optional formatting."""
        # Navigate through nested keys (e.g., "commands.slash.tickets.response.title")
        keys = key.split('.')
        
        # Try primary locale first
        value = self._get_nested_value(self.locale_data, keys)
        
        # Fallback to default locale
        if value is None:
            value = self._get_nested_value(self.fallback_data, keys)
        
        # If still not found, return the key
        if value is None:
            return key
        
        # Format with kwargs if provided
        try:
            return value.format(**kwargs) if kwargs else value
        except (KeyError, ValueError):
            return value
    
    def _get_nested_value(self, data: Dict[str, Any], keys: list) -> Optional[str]:
        """Get a nested value from dictionary using key path."""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current if isinstance(current, str) else None


# Global i18n instance
_i18n_instance: Optional[I18n] = None


def get_i18n() -> I18n:
    """Get the global i18n instance."""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance