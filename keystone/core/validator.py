import jsonschema
from typing import Dict, Any, Tuple, Optional


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate data against a JSON schema.
    
    Args:
        data: The data to validate
        schema: The JSON schema to validate against
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.ValidationError as err:
        return False, str(err)


def validate_references(layout_data: Dict[str, Any], theme: Dict[str, Any], icons: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that theme_color and icon_name references in the layout exist in their respective manifests.
    
    Args:
        layout_data: The parsed layout configuration
        theme: The loaded theme dictionary
        icons: The loaded icons dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    errors = []
    
    # Get theme name for error reporting
    theme_name = theme.get('name', 'unknown')
    
    # Check each category for theme_color and icon_name references
    categories = layout_data.get('categories', [])
    
    for i, category in enumerate(categories):
        category_name = category.get('name', f'category_{i}')
        
        # Validate theme_color reference
        theme_color = category.get('theme_color')
        if theme_color is not None:
            color_variants = theme.get('color_variants', {})
            if theme_color not in color_variants:
                available_colors = ', '.join(f'"{color}"' for color in sorted(color_variants.keys()))
                errors.append(f'Theme color "{theme_color}" in category "{category_name}" not found in theme "{theme_name}". Available colors: {available_colors}')
        
        # Validate icon_name reference
        icon_name = category.get('icon_name')
        if icon_name is not None:
            if icon_name not in icons:
                available_icons = ', '.join(f'"{icon}"' for icon in sorted(icons.keys()))
                errors.append(f'Icon "{icon_name}" in category "{category_name}" not found. Available icons: {available_icons}')
    
    if errors:
        return False, '. '.join(errors)
    
    return True, None
