from typing import Dict, List, Any


def generate_html(data: Dict[str, Any], theme: Dict[str, Any], icons: Dict[str, str]) -> str:
    """
    Generate the complete HTML document for the 'Reference Card' template.
    
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
    <title>{data.get("title", data.get("tool", "Keystone"))} - Reference Card</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .keybind-key {{ 
            display: inline-block;
            min-width: 1.5rem;
            text-align: center;
        }}
        table {{
            border-collapse: collapse;
        }}
        {print_styles}
    </style>
</head>
<body class="{theme["base_styles"]["body"]}">
    <div class="{theme["base_styles"]["container"]}">
        <header class="mb-6">
            <h1 class="text-2xl font-bold text-gray-800 mb-2">{data.get("title", data.get("tool", "Keystone"))}</h1>
            {f'<p class="text-gray-600 text-sm">Version: {data["version"]}</p>' if data.get("version") else ''}
        </header>
        
        {generate_reference_table(data.get("categories", []), theme, icons)}
    </div>
</body>
</html>'''
    
    return html_content


def generate_reference_table(categories: List[Dict[str, Any]], theme: Dict[str, Any], icons: Dict[str, str]) -> str:
    """
    Generate HTML table for all categories in a dense reference format.
    
    Args:
        categories: List of category dictionaries
        theme: Theme configuration
        icons: Icon dictionary
        
    Returns:
        HTML string for the reference table
    """
    if not categories:
        return '<div class="text-center text-gray-500">No categories found</div>'
    
    border_class = get_table_border_classes(theme)
    
    # Build the complete table
    table_html = f'''
    <table class="w-full border {border_class}">
        <thead>
            <tr class="{get_table_header_classes(theme)}">
                <th class="border {border_class} px-3 py-2 text-left w-1/4">Category</th>
                <th class="border {border_class} px-3 py-2 text-left w-1/3">Action</th>
                <th class="border {border_class} px-3 py-2 text-left w-1/4">Keybind</th>
                <th class="border {border_class} px-3 py-2 text-left">Description</th>
            </tr>
        </thead>
        <tbody>
            {generate_table_rows(categories, theme, icons)}
        </tbody>
    </table>'''
    
    return table_html


def generate_table_rows(categories: List[Dict[str, Any]], theme: Dict[str, Any], icons: Dict[str, str]) -> str:
    """
    Generate table rows for all keybinds across all categories.
    
    Args:
        categories: List of category dictionaries
        theme: Theme configuration
        icons: Icon dictionary
        
    Returns:
        HTML string for table rows
    """
    rows = []
    border_class = get_table_border_classes(theme)
    row_class = get_table_row_classes(theme)
    
    for category in categories:
        category_name = category.get("name", "Unknown Category")
        keybinds = category.get("keybinds", [])
        
        # Get icon (use default if not specified or not found)
        icon_name = category.get("icon_name", "grid")
        icon_svg = icons.get(icon_name, icons.get("grid", ""))
        
        if not keybinds:
            # Empty category row
            rows.append(f'''
            <tr class="{row_class}">
                <td class="border {border_class} px-3 py-2 font-medium">
                    <div class="flex items-center gap-2">
                        {icon_svg}
                        <span>{category_name}</span>
                    </div>
                </td>
                <td class="border {border_class} px-3 py-2 text-gray-500 italic" colspan="3">No keybinds available</td>
            </tr>''')
        else:
            # Generate rows for each keybind in the category
            for j, keybind in enumerate(keybinds):
                action = keybind.get("action", "Unknown Action")
                keys = keybind.get("keys", [])
                description = keybind.get("description", "")
                
                # Show category name only for the first keybind in each category
                category_cell = ""
                if j == 0:
                    rowspan = f' rowspan="{len(keybinds)}"' if len(keybinds) > 1 else ""
                    category_cell = f'''
                    <td class="border {border_class} px-3 py-2 font-medium align-top"{rowspan}>
                        <div class="flex items-center gap-2">
                            {icon_svg}
                            <span>{category_name}</span>
                        </div>
                    </td>'''
                
                # Generate key display
                key_display = generate_key_display(keys, theme)
                
                rows.append(f'''
                <tr class="{row_class}">
                    {category_cell}
                    <td class="border {border_class} px-3 py-2">{action}</td>
                    <td class="border {border_class} px-3 py-2">{key_display}</td>
                    <td class="border {border_class} px-3 py-2 text-sm text-gray-600">{description}</td>
                </tr>''')
    
    return '\n'.join(rows)


def generate_key_display(keys: List[str], theme: Dict[str, Any]) -> str:
    """
    Generate HTML for displaying keyboard keys in table format.
    
    Args:
        keys: List of key strings
        theme: Theme configuration
        
    Returns:
        HTML string for key display
    """
    if not keys:
        return '<span class="text-gray-400">-</span>'
    
    # Handle keys as string or list
    if isinstance(keys, str):
        keys = [keys]
    
    key_combinations = []
    key_class = theme["keybind_styles"]["key"]
    
    for key in keys:
        # Split compound keys like "Ctrl+S" into individual key boxes
        individual_keys = key.split('+')
        key_boxes = []
        
        for i, individual_key in enumerate(individual_keys):
            # Clean up the key (remove extra spaces)
            clean_key = individual_key.strip()
            key_boxes.append(f'<kbd class="{key_class} keybind-key text-xs">{clean_key}</kbd>')
            
            # Add "+" separator between keys (but not after the last one)
            if i < len(individual_keys) - 1:
                key_boxes.append('<span class="text-gray-500 mx-1">+</span>')
        
        key_combinations.append(''.join(key_boxes))
    
    # Join multiple key combinations with spacing
    return f'<div class="inline-flex items-center gap-1 flex-wrap">{"<span class=\"mx-1\"></span>".join(key_combinations)}</div>'


def get_table_header_classes(theme: Dict[str, Any]) -> str:
    """
    Get CSS classes for table header rows.
    
    Args:
        theme: Theme configuration
        
    Returns:
        CSS class string for table headers
    """
    # Use theme's body style to determine if it's a dark theme
    body_style = theme["base_styles"]["body"]
    if "bg-gray-900" in body_style or "dark" in body_style:
        return "bg-gray-800 text-gray-100 font-semibold border-gray-600"
    else:
        return "bg-gray-100 text-gray-700 font-semibold border-gray-300"


def get_table_row_classes(theme: Dict[str, Any]) -> str:
    """
    Get CSS classes for table data rows.
    
    Args:
        theme: Theme configuration
        
    Returns:
        CSS class string for table rows
    """
    # Use theme's body style to determine if it's a dark theme
    body_style = theme["base_styles"]["body"]
    if "bg-gray-900" in body_style or "dark" in body_style:
        return "hover:bg-gray-800 border-gray-700"
    else:
        return "hover:bg-gray-50 border-gray-300"


def get_table_border_classes(theme: Dict[str, Any]) -> str:
    """
    Get CSS classes for table borders.
    
    Args:
        theme: Theme configuration
        
    Returns:
        CSS class string for table borders
    """
    body_style = theme["base_styles"]["body"]
    if "bg-gray-900" in body_style or "dark" in body_style:
        return "border-gray-700"
    else:
        return "border-gray-300"
