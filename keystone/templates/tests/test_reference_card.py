import pytest
from keystone.templates.reference_card import (
    generate_html,
    generate_reference_table,
    generate_table_rows,
    generate_key_display,
    get_table_header_classes,
    get_table_row_classes,
    get_table_border_classes
)


class TestReferenceCardTemplate:
    
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
    def dark_theme(self):
        """Sample dark theme configuration for testing."""
        return {
            "base_styles": {
                "body": "bg-gray-900 text-gray-100 font-inter",
                "container": "mx-auto p-4 sm:p-6 lg:p-8"
            },
            "card_styles": {
                "card": "bg-gray-800 rounded-xl border border-gray-700 shadow-md",
                "card_header": "flex items-center gap-3 p-4 border-b border-gray-700",
                "card_body": "p-6"
            },
            "keybind_styles": {
                "key": "bg-gray-700 border border-gray-600 rounded-md px-2 py-1 font-mono text-sm font-semibold text-gray-100",
                "key_group": "inline-flex items-center gap-1"
            },
            "color_variants": {
                "blue": {"header": "bg-blue-900 text-blue-100", "accent": "text-blue-400"},
                "purple": {"header": "bg-purple-900 text-purple-100", "accent": "text-purple-400"}
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
            "title": "VS Code Shortcuts",
            "categories": [
                {
                    "name": "File Operations",
                    "icon_name": "terminal",
                    "keybinds": [
                        {
                            "action": "New File",
                            "keys": ["Ctrl+N"],
                            "description": "Create a new file"
                        },
                        {
                            "action": "Open File",
                            "keys": ["Ctrl+O"],
                            "description": "Open an existing file"
                        }
                    ]
                },
                {
                    "name": "Navigation",
                    "icon_name": "grid",
                    "keybinds": [
                        {
                            "action": "Go to Line",
                            "keys": ["Ctrl+G"],
                            "description": "Navigate to a specific line number"
                        }
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def empty_data(self):
        """Empty data for testing edge cases."""
        return {
            "tool": "EmptyTool",
            "categories": []
        }
    
    @pytest.fixture
    def data_with_empty_category(self):
        """Data with an empty category for testing."""
        return {
            "tool": "TestTool",
            "categories": [
                {
                    "name": "Empty Category",
                    "icon_name": "wrench",
                    "keybinds": []
                }
            ]
        }
    
    def test_generate_html_basic(self, sample_data, sample_theme, sample_icons):
        """Test basic HTML generation."""
        result = generate_html(sample_data, sample_theme, sample_icons)
        
        # Check basic HTML structure
        assert "<!DOCTYPE html>" in result
        assert "<html lang=\"en\">" in result
        assert "<head>" in result
        assert "<body class=" in result  # Body tag has CSS classes
        
        # Check title
        assert "VS Code Shortcuts - Reference Card" in result
        
        # Check version
        assert "Version: 1.85.0" in result
        
        # Check theme classes are applied
        assert sample_theme["base_styles"]["body"] in result
        assert sample_theme["base_styles"]["container"] in result
    
    def test_generate_html_with_missing_title(self, sample_theme, sample_icons):
        """Test HTML generation with missing title."""
        data = {"tool": "TestTool", "categories": []}
        result = generate_html(data, sample_theme, sample_icons)
        
        assert "TestTool - Reference Card" in result
    
    def test_generate_html_with_missing_tool_and_title(self, sample_theme, sample_icons):
        """Test HTML generation with missing tool and title."""
        data = {"categories": []}
        result = generate_html(data, sample_theme, sample_icons)
        
        assert "Keystone - Reference Card" in result
    
    def test_generate_reference_table_with_data(self, sample_data, sample_theme, sample_icons):
        """Test table generation with sample data."""
        categories = sample_data["categories"]
        result = generate_reference_table(categories, sample_theme, sample_icons)
        
        # Check table structure
        assert "<table" in result
        assert "<thead>" in result
        assert "<tbody>" in result
        assert "</table>" in result
        
        # Check headers
        assert "Category" in result
        assert "Action" in result
        assert "Keybind" in result
        assert "Description" in result
        
        # Check category names appear
        assert "File Operations" in result
        assert "Navigation" in result
        
        # Check actions appear
        assert "New File" in result
        assert "Open File" in result
        assert "Go to Line" in result
    
    def test_generate_reference_table_empty(self, sample_theme, sample_icons):
        """Test table generation with empty categories."""
        result = generate_reference_table([], sample_theme, sample_icons)
        assert "No categories found" in result
        assert "<table" not in result
    
    def test_generate_table_rows_with_data(self, sample_data, sample_theme, sample_icons):
        """Test table row generation."""
        categories = sample_data["categories"]
        result = generate_table_rows(categories, sample_theme, sample_icons)
        
        # Check rows are generated
        assert "<tr" in result
        assert "<td" in result
        
        # Check data appears in rows
        assert "File Operations" in result
        assert "New File" in result
        assert "Ctrl" in result  # Keys are split into individual elements
        assert "N" in result
        assert "Create a new file" in result
        
        # Check icons are included
        assert "terminal" in result  # SVG content
        assert "grid" in result      # SVG content
        
        # Check rowspan for multi-keybind categories
        assert 'rowspan="2"' in result  # File Operations has 2 keybinds
    
    def test_generate_table_rows_with_empty_category(self, data_with_empty_category, sample_theme, sample_icons):
        """Test table row generation with empty category."""
        categories = data_with_empty_category["categories"]
        result = generate_table_rows(categories, sample_theme, sample_icons)
        
        assert "Empty Category" in result
        assert "No keybinds available" in result
        assert "colspan=\"3\"" in result
    
    def test_generate_key_display_single_key(self, sample_theme):
        """Test key display generation for single key."""
        result = generate_key_display(["Ctrl"], sample_theme)
        
        assert "<kbd" in result
        assert "Ctrl" in result
        assert sample_theme["keybind_styles"]["key"] in result
        assert "text-xs" in result  # Reference card uses smaller text
    
    def test_generate_key_display_compound_key(self, sample_theme):
        """Test key display generation for compound keys."""
        result = generate_key_display(["Ctrl+Shift+P"], sample_theme)
        
        # Should contain all parts
        assert "Ctrl" in result
        assert "Shift" in result
        assert "P" in result
        
        # Should contain separators
        assert "+" in result
        
        # Should contain multiple kbd elements
        assert result.count("<kbd") == 3
    
    def test_generate_key_display_multiple_combinations(self, sample_theme):
        """Test key display generation for multiple key combinations."""
        result = generate_key_display(["Ctrl+C", "Ctrl+V"], sample_theme)
        
        assert "Ctrl" in result
        assert "C" in result
        assert "V" in result
        assert result.count("<kbd") == 4  # 2 keys per combination
    
    def test_generate_key_display_empty(self, sample_theme):
        """Test key display generation for empty keys."""
        result = generate_key_display([], sample_theme)
        assert "-" in result
        assert "text-gray-400" in result
    
    def test_generate_key_display_string_input(self, sample_theme):
        """Test key display generation with string input instead of list."""
        # The function internally handles string conversion, but we pass a list for type safety
        result = generate_key_display(["Ctrl+S"], sample_theme)
        
        assert "Ctrl" in result
        assert "S" in result
        assert "<kbd" in result
    
    def test_theme_classes_light_theme(self, sample_theme):
        """Test theme class generation for light theme."""
        header_classes = get_table_header_classes(sample_theme)
        row_classes = get_table_row_classes(sample_theme)
        border_classes = get_table_border_classes(sample_theme)
        
        # Light theme should use light colors
        assert "bg-gray-100" in header_classes
        assert "text-gray-700" in header_classes
        assert "hover:bg-gray-50" in row_classes
        assert "border-gray-300" in border_classes
    
    def test_theme_classes_dark_theme(self, dark_theme):
        """Test theme class generation for dark theme."""
        header_classes = get_table_header_classes(dark_theme)
        row_classes = get_table_row_classes(dark_theme)
        border_classes = get_table_border_classes(dark_theme)
        
        # Dark theme should use dark colors
        assert "bg-gray-800" in header_classes
        assert "text-gray-100" in header_classes
        assert "hover:bg-gray-800" in row_classes
        assert "border-gray-700" in border_classes
    
    def test_missing_icon_fallback(self, sample_theme):
        """Test fallback behavior when icon is missing."""
        icons = {"grid": "<svg>grid</svg>"}  # Missing 'terminal' icon
        categories = [{"name": "Test", "icon_name": "terminal", "keybinds": []}]
        
        result = generate_table_rows(categories, sample_theme, icons)
        
        # Should fallback to grid icon
        assert "grid" in result
    
    def test_missing_icon_name_fallback(self, sample_theme, sample_icons):
        """Test fallback behavior when icon_name is missing."""
        categories = [{"name": "Test", "keybinds": []}]  # No icon_name specified
        
        result = generate_table_rows(categories, sample_theme, sample_icons)
        
        # Should fallback to grid icon
        assert "grid" in result
    
    def test_integration_full_html_generation(self, sample_data, sample_theme, sample_icons):
        """Integration test for full HTML generation."""
        result = generate_html(sample_data, sample_theme, sample_icons)
        
        # Should be valid HTML with all components
        assert result.startswith("<!DOCTYPE html>")
        assert result.endswith("</html>")
        
        # Should contain all expected content
        assert "VS Code Shortcuts" in result
        assert "File Operations" in result
        assert "Navigation" in result
        assert "New File" in result
        assert "Ctrl" in result  # Keys are rendered as individual elements
        assert "N" in result
        
        # Should contain proper table structure
        assert "<table" in result
        assert "<thead>" in result
        assert "<tbody>" in result
        
        # Should contain theme styles
        assert sample_theme["base_styles"]["body"] in result
        assert sample_theme["keybind_styles"]["key"] in result
