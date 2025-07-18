import json
import os
from pathlib import Path

def load_theme(theme_name, _visited=None):
    """
    Load a theme configuration from a JSON file with inheritance support.
    
    Args:
        theme_name (str): Name of the theme to load
        _visited (set): Internal parameter to track visited themes for cycle detection
        
    Returns:
        dict: Theme configuration with inheritance resolved
        
    Raises:
        FileNotFoundError: If the theme file doesn't exist
        json.JSONDecodeError: If the theme file contains invalid JSON
        ValueError: If circular inheritance is detected
    """
    # Initialize visited set for cycle detection
    if _visited is None:
        _visited = set()
    
    # Check for circular inheritance
    if theme_name in _visited:
        raise ValueError(f"Circular theme inheritance detected: {' -> '.join(_visited)} -> {theme_name}")
    
    # Add current theme to visited set
    _visited.add(theme_name)
    
    # Get the path to the themes directory relative to this file
    themes_dir = Path(__file__).parent.parent / "themes"
    theme_path = themes_dir / f"{theme_name}.json"
    
    if not theme_path.exists():
        raise FileNotFoundError(f"Theme '{theme_name}' not found at {theme_path}")
    
    with open(theme_path, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
    
    # Check if this theme inherits from another theme
    if "inherits_from" in theme_data:
        base_theme_name = theme_data["inherits_from"]
        
        # Recursively load the base theme
        base_theme = load_theme(base_theme_name, _visited.copy())
        
        # Deep merge the current theme over the base theme
        merged_theme = _deep_merge_themes(base_theme, theme_data)
        
        # Remove the inherits_from key from the final theme
        if "inherits_from" in merged_theme:
            del merged_theme["inherits_from"]
        
        return merged_theme
    
    return theme_data


def _deep_merge_themes(base_theme, custom_theme):
    """
    Deep merge two theme dictionaries, with custom theme values taking precedence.
    
    Special handling for color_variants: merge color variants rather than replacing them entirely.
    
    Args:
        base_theme (dict): Base theme dictionary
        custom_theme (dict): Custom theme dictionary to merge over base
        
    Returns:
        dict: Merged theme dictionary
    """
    import copy
    
    # Start with a deep copy of the base theme
    merged = copy.deepcopy(base_theme)
    
    for key, value in custom_theme.items():
        if key == "inherits_from":
            # Skip the inheritance key
            continue
        elif key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # For nested dictionaries, recursively merge
            if key == "color_variants":
                # Special handling for color variants - merge color by color
                merged[key] = _merge_color_variants(merged[key], value)
            else:
                # Regular deep merge for other nested dictionaries
                merged[key] = _deep_merge_themes(merged[key], value)
        else:
            # For non-dict values or new keys, use the custom theme value
            merged[key] = copy.deepcopy(value)
    
    return merged


def _merge_color_variants(base_variants, custom_variants):
    """
    Merge color variants, allowing partial color overrides.
    
    Args:
        base_variants (dict): Base color variants
        custom_variants (dict): Custom color variants to merge
        
    Returns:
        dict: Merged color variants
    """
    import copy
    
    merged_variants = copy.deepcopy(base_variants)
    
    for color_name, color_config in custom_variants.items():
        if color_name in merged_variants and isinstance(color_config, dict) and isinstance(merged_variants[color_name], dict):
            # Merge individual color properties
            merged_variants[color_name].update(color_config)
        else:
            # Replace entire color configuration
            merged_variants[color_name] = copy.deepcopy(color_config)
    
    return merged_variants

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
