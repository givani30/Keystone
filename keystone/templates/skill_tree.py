from typing import Dict, List, Any


def generate_html(data: Dict[str, Any], theme: Dict[str, Any], icons: Dict[str, str]) -> str:
    """
    Generate the complete HTML document for the 'Skill Tree' template.
    
    Args:
        data: Merged keybind data containing tool info and categories
        theme: Theme configuration with styling classes
        icons: Dictionary mapping icon names to SVG strings
        
    Returns:
        Complete HTML document as a string
    """
    # Get print styles from theme if available
    print_styles = theme.get("print_styles", "")
    
    # Generate the HTML structure
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get("title", data.get("tool", "Keystone"))} - Keybind Cheatsheet</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .keybind-key {{ 
            display: inline-block;
            min-width: 1.5rem;
            text-align: center;
        }}
        {print_styles}
    </style>
</head>
<body class="{theme["base_styles"]["body"]}">
    <div class="{theme["base_styles"]["container"]}">
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">{data.get("title", data.get("tool", "Keystone"))}</h1>
            {f'<p class="text-gray-600">Version: {data["version"]}</p>' if data.get("version") else ''}
        </header>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {generate_categories(data.get("categories", []), theme, icons)}
        </div>
    </div>
</body>
</html>'''
    
    return html_content


def generate_categories(categories: List[Dict[str, Any]], theme: Dict[str, Any], icons: Dict[str, str]) -> str:
    """
    Generate HTML for all categories.
    
    Args:
        categories: List of category dictionaries
        theme: Theme configuration
        icons: Icon dictionary
        
    Returns:
        HTML string for all categories
    """
    if not categories:
        return '<div class="col-span-full text-center text-gray-500">No categories found</div>'
    
    category_html = []
    color_keys = list(theme["color_variants"].keys())
    
    for i, category in enumerate(categories):
        # Assign color variants cyclically
        color_variant = color_keys[i % len(color_keys)]
        category_html.append(generate_category_card(category, theme, icons, color_variant))
    
    return '\n'.join(category_html)


def generate_category_card(category: Dict[str, Any], theme: Dict[str, Any], icons: Dict[str, str], color_variant: str) -> str:
    """
    Generate HTML for a single category card.
    
    Args:
        category: Category dictionary with name and keybinds
        theme: Theme configuration
        icons: Icon dictionary
        color_variant: Color variant key from theme
        
    Returns:
        HTML string for the category card
    """
    category_name = category.get("name", "Unknown Category")
    keybinds = category.get("keybinds", [])
    
    # Get icon (use default if not specified or not found)
    icon_name = category.get("icon_name", "grid")
    icon_svg = icons.get(icon_name, icons.get("grid", ""))
    
    # Get color variant styles
    color_styles = theme["color_variants"][color_variant]
    
    # Build the card HTML
    card_html = f'''
    <div class="{theme["card_styles"]["card"]}">
        <div class="{theme["card_styles"]["card_header"]} {color_styles["header"]}">
            <div class="flex items-center gap-3">
                {icon_svg}
                <h2 class="text-lg font-semibold">{category_name}</h2>
            </div>
        </div>
        <div class="{theme["card_styles"]["card_body"]}">
            {generate_keybinds(keybinds, theme)}
        </div>
    </div>'''
    
    return card_html


def generate_keybinds(keybinds: List[Dict[str, Any]], theme: Dict[str, Any]) -> str:
    """
    Generate HTML for keybinds within a category.
    
    Args:
        keybinds: List of keybind dictionaries
        theme: Theme configuration
        
    Returns:
        HTML string for the keybinds
    """
    if not keybinds:
        return '<p class="text-gray-500 text-sm">No keybinds available</p>'
    
    keybind_html = []
    
    for keybind in keybinds:
        action = keybind.get("action", "Unknown Action")
        keys = keybind.get("keys", [])
        description = keybind.get("description", "")
        
        # Handle keys as string or list
        if isinstance(keys, str):
            keys = [keys]
        
        # Generate key display
        key_display = generate_key_display(keys, theme)
        
        # Build keybind HTML
        keybind_item = f'''
        <div class="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
            <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-800">{action}</div>
                {f'<div class="text-sm text-gray-600 mt-1">{description}</div>' if description else ''}
            </div>
            <div class="flex-shrink-0 ml-4">
                {key_display}
            </div>
        </div>'''
        
        keybind_html.append(keybind_item)
    
    return f'<div class="space-y-1">{"".join(keybind_html)}</div>'


def generate_key_display(keys: List[str], theme: Dict[str, Any]) -> str:
    """
    Generate HTML for displaying keyboard keys.
    
    Args:
        keys: List of key strings
        theme: Theme configuration
        
    Returns:
        HTML string for key display
    """
    if not keys:
        return '<span class="text-gray-400">-</span>'
    
    key_combinations = []
    key_class = theme["keybind_styles"]["key"]
    
    for key in keys:
        # Split compound keys like "Ctrl+S" into individual key boxes
        individual_keys = key.split('+')
        key_boxes = []
        
        for i, individual_key in enumerate(individual_keys):
            # Clean up the key (remove extra spaces)
            clean_key = individual_key.strip()
            key_boxes.append(f'<kbd class="{key_class} keybind-key">{clean_key}</kbd>')
            
            # Add "+" separator between keys (but not after the last one)
            if i < len(individual_keys) - 1:
                key_boxes.append('<span class="text-gray-500 mx-1">+</span>')
        
        key_combinations.append(''.join(key_boxes))
    
    # Join multiple key combinations with spacing
    return f'<div class="{theme["keybind_styles"]["key_group"]}">{"<span class=\"mx-2\"></span>".join(key_combinations)}</div>'