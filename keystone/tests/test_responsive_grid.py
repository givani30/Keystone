"""
Tests for responsive grid layout functionality in themes and templates.
"""
import pytest
from keystone.templates.skill_tree import generate_html
from keystone.utils.theme_loader import load_theme


class TestResponsiveGridLayouts:
    """Test responsive grid layout implementation."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            "tool": "VSCode",
            "title": "VSCode Keyboard Shortcuts",
            "version": "1.85.0",
            "categories": [
                {
                    "name": "Navigation",
                    "icon_name": "terminal",
                    "keybinds": [
                        {"action": "Go to File", "keys": ["Ctrl+P"], "description": "Open file picker"},
                        {"action": "Go to Symbol", "keys": ["Ctrl+Shift+O"], "description": "Navigate to symbol"}
                    ]
                },
                {
                    "name": "Editing",
                    "icon_name": "wrench",
                    "keybinds": [
                        {"action": "Copy Line", "keys": ["Ctrl+C"], "description": "Copy current line"},
                        {"action": "Delete Line", "keys": ["Ctrl+Shift+K"], "description": "Delete current line"}
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def sample_icons(self):
        """Sample icons for testing."""
        return {
            "terminal": '<svg class="h-6 w-6"><path d="M3 3h18v18H3z"/></svg>',
            "wrench": '<svg class="h-6 w-6"><path d="M3 3h18v18H3z"/></svg>',
            "grid": '<svg class="h-6 w-6"><path d="M3 3h18v18H3z"/></svg>'
        }
    
    def test_default_theme_has_grid_styles(self):
        """Test that default theme includes responsive grid styles."""
        theme = load_theme("default")
        
        assert "grid_styles" in theme
        grid_styles = theme["grid_styles"]
        
        # Check that all required responsive grid properties exist
        assert "container" in grid_styles
        assert "auto_fit" in grid_styles
        assert "responsive_cols" in grid_styles
        assert "card_min_width" in grid_styles
        assert "gap_small" in grid_styles
        assert "gap_medium" in grid_styles
        assert "gap_large" in grid_styles
        
        # Verify responsive breakpoints in container
        container_class = grid_styles["container"]
        assert "grid-cols-1" in container_class
        assert "md:grid-cols-2" in container_class
        assert "lg:grid-cols-3" in container_class
        assert "xl:grid-cols-4" in container_class
    
    def test_dark_theme_has_grid_styles(self):
        """Test that dark theme includes responsive grid styles."""
        theme = load_theme("dark")
        
        assert "grid_styles" in theme
        grid_styles = theme["grid_styles"]
        
        # Check consistency with default theme structure
        assert "container" in grid_styles
        assert "responsive_cols" in grid_styles
        assert "card_min_width" in grid_styles
    
    def test_minimal_theme_has_grid_styles(self):
        """Test that minimal theme includes responsive grid styles."""
        theme = load_theme("minimal")
        
        assert "grid_styles" in theme
        grid_styles = theme["grid_styles"]
        
        # Check consistency with other themes
        assert "container" in grid_styles
        assert "responsive_cols" in grid_styles
    
    def test_skill_tree_uses_theme_grid_styles(self, sample_data, sample_icons):
        """Test that skill tree template uses grid styles from theme."""
        theme = load_theme("default")
        html = generate_html(sample_data, theme, sample_icons)
        
        # Check that the theme's grid container class is used
        grid_container_class = theme["grid_styles"]["container"]
        assert grid_container_class in html
        
        # Verify responsive grid classes are present
        assert "grid-cols-1" in html
        assert "md:grid-cols-2" in html
        assert "lg:grid-cols-3" in html
        assert "xl:grid-cols-4" in html
    
    def test_card_min_width_applied(self, sample_data, sample_icons):
        """Test that card minimum width is applied when available."""
        theme = load_theme("default")
        html = generate_html(sample_data, theme, sample_icons)
        
        # Check that card minimum width is applied
        card_min_width = theme["grid_styles"]["card_min_width"]
        if card_min_width:
            assert card_min_width in html
    
    def test_fallback_grid_when_theme_missing_grid_styles(self, sample_data, sample_icons):
        """Test fallback behavior when theme doesn't have grid_styles."""
        # Create a theme without grid_styles
        theme = {
            "base_styles": {
                "body": "bg-gray-50 text-gray-800",
                "container": "mx-auto p-4"
            },
            "card_styles": {
                "card": "bg-white border",
                "card_header": "p-4 border-b",
                "card_body": "p-6"
            },
            "keybind_styles": {
                "key": "bg-gray-200 px-2 py-1",
                "key_group": "inline-flex gap-1"
            },
            "color_variants": {
                "blue": {"header": "bg-blue-50", "accent": "text-blue-600"}
            }
        }
        
        html = generate_html(sample_data, theme, sample_icons)
        
        # Should use fallback grid classes
        assert "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" in html
    
    def test_print_styles_responsive_grid(self):
        """Test that print styles include responsive grid layout."""
        theme = load_theme("default")
        print_styles = theme.get("print_styles", "")
        
        # Check that print styles maintain grid layout
        assert "display: grid" in print_styles
        assert "grid-template-columns: repeat(2, 1fr)" in print_styles
        assert "grid-template-columns: 1fr" in print_styles  # For narrow print
        assert "gap: 0.5cm" in print_styles
    
    def test_all_themes_have_consistent_grid_structure(self):
        """Test that all themes have consistent grid style structures."""
        theme_names = ["default", "dark", "minimal", "dark_simple"]
        
        for theme_name in theme_names:
            theme = load_theme(theme_name)
            
            # Each theme should have grid_styles
            assert "grid_styles" in theme, f"Theme {theme_name} missing grid_styles"
            
            grid_styles = theme["grid_styles"]
            
            # Core responsive properties should exist
            required_props = ["container", "auto_fit", "responsive_cols", "card_min_width"]
            for prop in required_props:
                assert prop in grid_styles, f"Theme {theme_name} missing {prop} in grid_styles"
    
    def test_responsive_breakpoints_coverage(self):
        """Test that responsive breakpoints cover all major screen sizes."""
        theme = load_theme("default")
        container_class = theme["grid_styles"]["container"]
        
        # Check all major Tailwind breakpoints are covered
        assert "grid-cols-1" in container_class  # Mobile (default)
        assert "sm:" in container_class or "grid-cols-1" in container_class  # Small screens
        assert "md:" in container_class  # Medium screens (768px+)
        assert "lg:" in container_class  # Large screens (1024px+)
        assert "xl:" in container_class  # Extra large screens (1280px+)
    
    def test_gap_variations_available(self):
        """Test that different gap sizes are available for flexibility."""
        theme = load_theme("default")
        grid_styles = theme["grid_styles"]
        
        # Check that different gap options exist
        assert "gap_small" in grid_styles
        assert "gap_medium" in grid_styles
        assert "gap_large" in grid_styles
        
        # Verify they contain gap classes
        assert "gap-" in grid_styles["gap_small"]
        assert "gap-" in grid_styles["gap_medium"]
        assert "gap-" in grid_styles["gap_large"]
