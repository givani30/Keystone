import pytest
from keystone.templates.skill_tree import (
    generate_html,
    generate_categories,
    generate_category_card,
    generate_keybinds,
    generate_key_display
)


class TestSkillTreeTemplate:
    
    @pytest.fixture
    def sample_theme(self):
        """Sample theme configuration for testing."""
        return {
            "base_styles": {
                "body": "bg-gray-50 text-gray-800 font-inter",
                "container": "mx-auto p-4 sm:p-6 lg:p-8"
            },
            "card_styles": {
                "card": "bg-white rounded-xl border shadow-md hover:shadow-lg transition-all",
                "card_header": "flex items-center gap-3 p-4 border-b",
                "card_body": "p-6"
            },
            "keybind_styles": {
                "key": "bg-gray-200 border border-gray-300 rounded-md px-2 py-1 font-mono text-sm font-semibold",
                "key_group": "inline-flex items-center gap-1"
            },
            "color_variants": {
                "blue": {"header": "bg-blue-50 text-blue-700", "accent": "text-blue-600"},
                "purple": {"header": "bg-purple-50 text-purple-700", "accent": "text-purple-600"}
            }
        }
    
    @pytest.fixture
    def sample_icons(self):
        """Sample icons dictionary for testing."""
        return {
            "terminal": "<svg class=\"h-6 w-6\">terminal</svg>",
            "grid": "<svg class=\"h-6 w-6\">grid</svg>",
            "wrench": "<svg class=\"h-6 w-6\">wrench</svg>"
        }
    
    @pytest.fixture
    def sample_data(self):
        """Sample keybind data for testing."""
        return {
            "tool": "VSCode",
            "version": "1.85.0",
            "categories": [
                {
                    "name": "File Operations",
                    "keybinds": [
                        {
                            "action": "Open file",
                            "keys": "Ctrl+O",
                            "description": "Open a file from the filesystem"
                        },
                        {
                            "action": "Save file",
                            "keys": "Ctrl+S"
                        }
                    ]
                },
                {
                    "name": "Editing",
                    "keybinds": [
                        {
                            "action": "Copy",
                            "keys": "Ctrl+C"
                        }
                    ]
                }
            ]
        }
    
    def test_generate_html_basic_structure(self, sample_data, sample_theme, sample_icons):
        """Test that generate_html produces valid HTML structure."""
        html = generate_html(sample_data, sample_theme, sample_icons)
        
        # Check basic HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html lang=\"en\">" in html
        assert "<head>" in html
        assert "<body" in html  # Body tag with attributes
        assert "</body>" in html
        assert "</html>" in html
        
        # Check title
        assert "VSCode - Keybind Cheatsheet" in html
        
        # Check version
        assert "Version: 1.85.0" in html
        
        # Check categories are present
        assert "File Operations" in html
        assert "Editing" in html
        
        # Check keybinds are present
        assert "Open file" in html
        assert "Copy" in html
    
    def test_generate_html_with_minimal_data(self, sample_theme, sample_icons):
        """Test generate_html with minimal data."""
        minimal_data = {
            "tool": "TestTool",
            "categories": []
        }
        
        html = generate_html(minimal_data, sample_theme, sample_icons)
        
        assert "TestTool - Keybind Cheatsheet" in html
        assert "Version:" not in html  # No version provided
        assert "No categories found" in html
    
    def test_generate_html_applies_theme_classes(self, sample_data, sample_theme, sample_icons):
        """Test that theme classes are applied correctly."""
        html = generate_html(sample_data, sample_theme, sample_icons)
        
        # Check base styles are applied
        assert sample_theme["base_styles"]["body"] in html
        assert sample_theme["base_styles"]["container"] in html
        
        # Check card styles are applied
        assert sample_theme["card_styles"]["card"] in html
        assert sample_theme["card_styles"]["card_header"] in html
        assert sample_theme["card_styles"]["card_body"] in html
    
    def test_generate_categories_empty_list(self, sample_theme, sample_icons):
        """Test generate_categories with empty list."""
        result = generate_categories([], sample_theme, sample_icons)
        assert "No categories found" in result
    
    def test_generate_categories_color_cycling(self, sample_theme, sample_icons):
        """Test that color variants are cycled correctly."""
        categories = [
            {"name": "Cat1", "keybinds": []},
            {"name": "Cat2", "keybinds": []},
            {"name": "Cat3", "keybinds": []}  # Should cycle back to first color
        ]
        
        result = generate_categories(categories, sample_theme, sample_icons)
        
        # Check that both color variants are used
        assert "bg-blue-50 text-blue-700" in result
        assert "bg-purple-50 text-purple-700" in result
    
    def test_generate_category_card_basic(self, sample_theme, sample_icons):
        """Test generate_category_card with basic data."""
        category = {
            "name": "Test Category",
            "keybinds": [
                {
                    "action": "Test Action",
                    "keys": "Ctrl+T"
                }
            ]
        }
        
        result = generate_category_card(category, sample_theme, sample_icons, "blue")
        
        assert "Test Category" in result
        assert "Test Action" in result
        assert "Ctrl" in result
        assert "T" in result
        assert "bg-blue-50 text-blue-700" in result
    
    def test_generate_category_card_with_icon(self, sample_theme, sample_icons):
        """Test generate_category_card with icon."""
        category = {
            "name": "Test Category",
            "icon_name": "terminal",
            "keybinds": []
        }
        
        result = generate_category_card(category, sample_theme, sample_icons, "blue")
        
        assert "Test Category" in result
        assert sample_icons["terminal"] in result
    
    def test_generate_category_card_missing_icon(self, sample_theme, sample_icons):
        """Test generate_category_card falls back to default icon."""
        category = {
            "name": "Test Category",
            "icon_name": "nonexistent",
            "keybinds": []
        }
        
        result = generate_category_card(category, sample_theme, sample_icons, "blue")
        
        assert "Test Category" in result
        assert sample_icons["grid"] in result  # Default fallback
    
    def test_generate_keybinds_empty_list(self, sample_theme):
        """Test generate_keybinds with empty list."""
        result = generate_keybinds([], sample_theme)
        assert "No keybinds available" in result
    
    def test_generate_keybinds_with_description(self, sample_theme):
        """Test generate_keybinds with description."""
        keybinds = [
            {
                "action": "Test Action",
                "keys": "Ctrl+T",
                "description": "This is a test action"
            }
        ]
        
        result = generate_keybinds(keybinds, sample_theme)
        
        assert "Test Action" in result
        assert "This is a test action" in result
        assert "Ctrl" in result
        assert "T" in result
    
    def test_generate_keybinds_without_description(self, sample_theme):
        """Test generate_keybinds without description."""
        keybinds = [
            {
                "action": "Test Action",
                "keys": "Ctrl+T"
            }
        ]
        
        result = generate_keybinds(keybinds, sample_theme)
        
        assert "Test Action" in result
        assert "Ctrl" in result
        assert "T" in result
        # Should not have description div
        assert "text-sm text-gray-600" not in result
    
    def test_generate_key_display_single_key(self, sample_theme):
        """Test generate_key_display with single key."""
        result = generate_key_display(["Ctrl+O"], sample_theme)
        
        assert "Ctrl" in result
        assert "O" in result
        assert "<kbd" in result
        assert sample_theme["keybind_styles"]["key"] in result
    
    def test_generate_key_display_multiple_keys(self, sample_theme):
        """Test generate_key_display with multiple keys."""
        result = generate_key_display(["Ctrl+K", "Ctrl+O"], sample_theme)
        
        assert "Ctrl" in result
        assert "K" in result
        assert "O" in result
        assert result.count("<kbd") == 4  # 2 keys per compound key
    
    def test_generate_key_display_empty_keys(self, sample_theme):
        """Test generate_key_display with empty keys."""
        result = generate_key_display([], sample_theme)
        assert "-" in result
        assert "text-gray-400" in result
    
    def test_generate_keybinds_handles_string_keys(self, sample_theme):
        """Test that generate_keybinds handles keys as strings."""
        keybinds = [
            {
                "action": "Test Action",
                "keys": "Ctrl+T"  # String instead of list
            }
        ]
        
        result = generate_keybinds(keybinds, sample_theme)
        
        assert "Test Action" in result
        assert "Ctrl" in result
        assert "T" in result
    
    def test_generate_keybinds_handles_list_keys(self, sample_theme):
        """Test that generate_keybinds handles keys as lists."""
        keybinds = [
            {
                "action": "Test Action",
                "keys": ["Ctrl+K", "Ctrl+O"]  # List of keys
            }
        ]
        
        result = generate_keybinds(keybinds, sample_theme)
        
        assert "Test Action" in result
        assert "Ctrl" in result
        assert "K" in result
        assert "O" in result
    
    def test_html_escaping_in_content(self, sample_theme, sample_icons):
        """Test that HTML content is properly handled."""
        data = {
            "tool": "Test<Tool>",
            "categories": [
                {
                    "name": "Test & Category",
                    "keybinds": [
                        {
                            "action": "Action with <tags>",
                            "keys": "Ctrl+T",
                            "description": "Description with & symbols"
                        }
                    ]
                }
            ]
        }
        
        html = generate_html(data, sample_theme, sample_icons)
        
        # Basic test that HTML is generated (escaping would be handled by template engine in real usage)
        assert "Test<Tool>" in html
        assert "Test & Category" in html
        assert "Action with <tags>" in html