from keystone.core.validator import validate_references


def test_validate_references_valid():
    """Test validation with valid theme colors and icon names."""
    layout_data = {
        'categories': [
            {
                'name': 'Category 1',
                'theme_color': 'blue',
                'icon_name': 'terminal'
            },
            {
                'name': 'Category 2',
                'theme_color': 'purple',
                'icon_name': 'grid'
            }
        ]
    }
    
    theme = {
        'name': 'Test Theme',
        'color_variants': {
            'blue': {'header': 'bg-blue-50', 'accent': 'text-blue-600'},
            'purple': {'header': 'bg-purple-50', 'accent': 'text-purple-600'}
        }
    }
    
    icons = {
        'terminal': '<svg>...</svg>',
        'grid': '<svg>...</svg>',
        'wrench': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is True
    assert error is None


def test_validate_references_invalid_theme_color():
    """Test validation with invalid theme color."""
    layout_data = {
        'categories': [
            {
                'name': 'Category 1',
                'theme_color': 'orange',  # Invalid color
                'icon_name': 'terminal'
            }
        ]
    }
    
    theme = {
        'name': 'Test Theme',
        'color_variants': {
            'blue': {'header': 'bg-blue-50', 'accent': 'text-blue-600'},
            'purple': {'header': 'bg-purple-50', 'accent': 'text-purple-600'}
        }
    }
    
    icons = {
        'terminal': '<svg>...</svg>',
        'grid': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is False
    assert error is not None
    assert 'orange' in error
    assert 'Category 1' in error
    assert 'Test Theme' in error
    assert 'blue' in error
    assert 'purple' in error


def test_validate_references_invalid_icon():
    """Test validation with invalid icon name."""
    layout_data = {
        'categories': [
            {
                'name': 'Category 1',
                'theme_color': 'blue',
                'icon_name': 'invalid_icon'  # Invalid icon
            }
        ]
    }
    
    theme = {
        'name': 'Test Theme',
        'color_variants': {
            'blue': {'header': 'bg-blue-50', 'accent': 'text-blue-600'}
        }
    }
    
    icons = {
        'terminal': '<svg>...</svg>',
        'grid': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is False
    assert error is not None
    assert 'invalid_icon' in error
    assert 'Category 1' in error
    assert 'terminal' in error
    assert 'grid' in error


def test_validate_references_multiple_errors():
    """Test validation with multiple invalid references."""
    layout_data = {
        'categories': [
            {
                'name': 'Category 1',
                'theme_color': 'orange',  # Invalid color
                'icon_name': 'terminal'
            },
            {
                'name': 'Category 2',
                'theme_color': 'blue',
                'icon_name': 'invalid_icon'  # Invalid icon
            }
        ]
    }
    
    theme = {
        'name': 'Test Theme',
        'color_variants': {
            'blue': {'header': 'bg-blue-50', 'accent': 'text-blue-600'}
        }
    }
    
    icons = {
        'terminal': '<svg>...</svg>',
        'grid': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is False
    assert error is not None
    assert 'orange' in error
    assert 'invalid_icon' in error
    assert 'Category 1' in error
    assert 'Category 2' in error


def test_validate_references_optional_fields():
    """Test validation with optional theme_color and icon_name fields."""
    layout_data = {
        'categories': [
            {
                'name': 'Category 1',
                'theme_color': 'blue'
                # No icon_name - optional
            },
            {
                'name': 'Category 2',
                'icon_name': 'terminal'
                # No theme_color - optional
            },
            {
                'name': 'Category 3'
                # Neither field - both optional
            }
        ]
    }
    
    theme = {
        'name': 'Test Theme',
        'color_variants': {
            'blue': {'header': 'bg-blue-50', 'accent': 'text-blue-600'}
        }
    }
    
    icons = {
        'terminal': '<svg>...</svg>',
        'grid': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is True
    assert error is None


def test_validate_references_empty_color_variants():
    """Test validation when theme has no color_variants."""
    layout_data = {
        'categories': [
            {
                'name': 'Category 1',
                'theme_color': 'blue',
                'icon_name': 'terminal'
            }
        ]
    }
    
    theme = {
        'name': 'Test Theme',
        # No color_variants key
    }
    
    icons = {
        'terminal': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is False
    assert error is not None
    assert 'blue' in error
    assert 'Category 1' in error


def test_validate_references_empty_categories():
    """Test validation with empty categories list."""
    layout_data = {
        'categories': []
    }
    
    theme = {
        'name': 'Test Theme',
        'color_variants': {
            'blue': {'header': 'bg-blue-50', 'accent': 'text-blue-600'}
        }
    }
    
    icons = {
        'terminal': '<svg>...</svg>'
    }
    
    is_valid, error = validate_references(layout_data, theme, icons)
    assert is_valid is True
    assert error is None
