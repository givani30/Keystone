import json
import os
from pathlib import Path

def load_theme(theme_name):
    """
    Load a theme configuration from a JSON file.
    
    Args:
        theme_name (str): Name of the theme to load
        
    Returns:
        dict: Theme configuration
        
    Raises:
        FileNotFoundError: If the theme file doesn't exist
        json.JSONDecodeError: If the theme file contains invalid JSON
    """
    # Get the path to the themes directory relative to this file
    themes_dir = Path(__file__).parent.parent / "themes"
    theme_path = themes_dir / f"{theme_name}.json"
    
    if not theme_path.exists():
        raise FileNotFoundError(f"Theme '{theme_name}' not found at {theme_path}")
    
    with open(theme_path, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
    
    return theme_data

def load_icons():
    """
    Load the icon manifest from the assets directory.
    
    Returns:
        dict: Icon name to SVG string mapping
        
    Raises:
        FileNotFoundError: If the icons.json file doesn't exist
        json.JSONDecodeError: If the icons.json file contains invalid JSON
    """
    # Get the path to the assets directory relative to this file
    assets_dir = Path(__file__).parent.parent / "assets"
    icons_path = assets_dir / "icons.json"
    
    if not icons_path.exists():
        raise FileNotFoundError(f"Icons file not found at {icons_path}")
    
    with open(icons_path, 'r', encoding='utf-8') as f:
        icons_data = json.load(f)
    
    return icons_data
