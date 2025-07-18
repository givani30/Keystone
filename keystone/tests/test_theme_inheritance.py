import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from keystone.utils.theme_loader import load_theme, _deep_merge_themes, _merge_color_variants


class TestThemeInheritance:
    """Test theme inheritance functionality."""
    
    def test_load_theme_without_inheritance(self):
        """Test loading a theme that doesn't inherit from anything."""
        theme = load_theme("default")
        
        # Should load successfully and contain expected structure
        assert "name" in theme
        assert "base_styles" in theme
        assert "card_styles" in theme
        assert "keybind_styles" in theme
        assert "color_variants" in theme
        
        # Should not contain inherits_from key
        assert "inherits_from" not in theme
    
    def test_load_theme_with_inheritance(self):
        """Test loading a theme that inherits from default."""
        theme = load_theme("test_inherited")
        
        # Should contain inherited structure
        assert "name" in theme
        assert "base_styles" in theme
        assert "card_styles" in theme
        assert "keybind_styles" in theme
        assert "color_variants" in theme
        
        # Should not contain inherits_from key in final result
        assert "inherits_from" not in theme
        
        # Should have overridden body style
        assert theme["base_styles"]["body"] == "bg-green-50 text-green-800 font-inter"
        
        # Should have inherited container style from default
        assert theme["base_styles"]["container"] == "mx-auto p-4 sm:p-6 lg:p-8"
        
        # Should have inherited card_styles from default
        assert "card" in theme["card_styles"]
        assert "card_header" in theme["card_styles"]
        assert "card_body" in theme["card_styles"]
        
        # Should have inherited keybind_styles from default
        assert "key" in theme["keybind_styles"]
        assert "key_group" in theme["keybind_styles"]
    
    def test_color_variants_merging(self):
        """Test that color variants are merged correctly."""
        theme = load_theme("test_inherited")
        
        # Should have blue color variant with overridden header
        assert "blue" in theme["color_variants"]
        assert theme["color_variants"]["blue"]["header"] == "bg-green-100 text-green-800"
        # Should keep inherited accent from default
        assert theme["color_variants"]["blue"]["accent"] == "text-blue-600"
        
        # Should have purple color variant inherited entirely from default
        assert "purple" in theme["color_variants"]
        assert theme["color_variants"]["purple"]["header"] == "bg-purple-50 text-purple-700"
        assert theme["color_variants"]["purple"]["accent"] == "text-purple-600"
        
        # Should have new green color variant
        assert "green" in theme["color_variants"]
        assert theme["color_variants"]["green"]["header"] == "bg-emerald-50 text-emerald-700"
        assert theme["color_variants"]["green"]["accent"] == "text-emerald-600"
    
    def test_circular_inheritance_detection(self):
        """Test that circular inheritance is detected and raises an error."""
        with pytest.raises(ValueError, match="Circular theme inheritance detected"):
            load_theme("test_circular")
    
    def test_missing_base_theme(self):
        """Test that missing base theme raises FileNotFoundError."""
        # Create a temporary theme that inherits from non-existent theme
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "name": "Test Missing Base",
                "inherits_from": "nonexistent_theme",
                "base_styles": {"body": "test"}
            }, f)
            temp_path = Path(f.name)
        
        try:
            # Mock the themes directory to include our temp file
            themes_dir = Path(__file__).parent.parent / "themes"
            temp_theme_path = themes_dir / "temp_missing_base.json"
            
            # Copy temp file to themes directory
            temp_theme_path.write_text(temp_path.read_text())
            
            with pytest.raises(FileNotFoundError, match="Theme 'nonexistent_theme' not found"):
                load_theme("temp_missing_base")
        finally:
            # Clean up
            temp_path.unlink()
            if temp_theme_path.exists():
                temp_theme_path.unlink()
    
    def test_deep_merge_themes_function(self):
        """Test the _deep_merge_themes function directly."""
        base_theme = {
            "name": "Base",
            "base_styles": {
                "body": "base-body",
                "container": "base-container"
            },
            "card_styles": {
                "card": "base-card"
            },
            "color_variants": {
                "blue": {"header": "base-blue-header", "accent": "base-blue-accent"},
                "red": {"header": "base-red-header"}
            }
        }
        
        custom_theme = {
            "name": "Custom",
            "inherits_from": "base",
            "base_styles": {
                "body": "custom-body"
            },
            "new_section": {
                "new_key": "new-value"
            },
            "color_variants": {
                "blue": {"header": "custom-blue-header"},
                "green": {"header": "custom-green-header"}
            }
        }
        
        merged = _deep_merge_themes(base_theme, custom_theme)
        
        # Should override existing values
        assert merged["name"] == "Custom"
        assert merged["base_styles"]["body"] == "custom-body"
        
        # Should keep inherited values
        assert merged["base_styles"]["container"] == "base-container"
        assert merged["card_styles"]["card"] == "base-card"
        
        # Should add new sections
        assert merged["new_section"]["new_key"] == "new-value"
        
        # Should not include inherits_from in final result
        assert "inherits_from" not in merged
        
        # Should merge color variants correctly
        assert merged["color_variants"]["blue"]["header"] == "custom-blue-header"
        assert merged["color_variants"]["blue"]["accent"] == "base-blue-accent"
        assert merged["color_variants"]["red"]["header"] == "base-red-header"
        assert merged["color_variants"]["green"]["header"] == "custom-green-header"
    
    def test_merge_color_variants_function(self):
        """Test the _merge_color_variants function directly."""
        base_variants = {
            "blue": {"header": "base-blue-header", "accent": "base-blue-accent"},
            "red": {"header": "base-red-header", "accent": "base-red-accent"},
            "purple": {"header": "base-purple-header"}
        }
        
        custom_variants = {
            "blue": {"header": "custom-blue-header"},
            "green": {"header": "custom-green-header", "accent": "custom-green-accent"},
            "purple": "custom-purple-string"  # Test non-dict override
        }
        
        merged = _merge_color_variants(base_variants, custom_variants)
        
        # Should merge blue color (partial override)
        assert merged["blue"]["header"] == "custom-blue-header"
        assert merged["blue"]["accent"] == "base-blue-accent"
        
        # Should keep red color as-is
        assert merged["red"]["header"] == "base-red-header"
        assert merged["red"]["accent"] == "base-red-accent"
        
        # Should add new green color
        assert merged["green"]["header"] == "custom-green-header"
        assert merged["green"]["accent"] == "custom-green-accent"
        
        # Should replace purple entirely (non-dict override)
        assert merged["purple"] == "custom-purple-string"
    
    def test_multi_level_inheritance(self):
        """Test inheritance chains (A inherits from B inherits from C)."""
        # Create a temporary multi-level inheritance chain
        themes_dir = Path(__file__).parent.parent / "themes"
        
        # Level 1: Base theme
        level1_theme = {
            "name": "Level 1",
            "base_styles": {"body": "level1-body", "container": "level1-container"},
            "color_variants": {"blue": {"header": "level1-blue"}}
        }
        
        # Level 2: Inherits from level 1
        level2_theme = {
            "name": "Level 2", 
            "inherits_from": "test_level1",
            "base_styles": {"body": "level2-body"},
            "color_variants": {"blue": {"accent": "level2-blue-accent"}, "red": {"header": "level2-red"}}
        }
        
        # Level 3: Inherits from level 2
        level3_theme = {
            "name": "Level 3",
            "inherits_from": "test_level2", 
            "color_variants": {"green": {"header": "level3-green"}}
        }
        
        # Write temporary theme files
        level1_path = themes_dir / "test_level1.json"
        level2_path = themes_dir / "test_level2.json" 
        level3_path = themes_dir / "test_level3.json"
        
        try:
            level1_path.write_text(json.dumps(level1_theme))
            level2_path.write_text(json.dumps(level2_theme))
            level3_path.write_text(json.dumps(level3_theme))
            
            # Load the final theme
            final_theme = load_theme("test_level3")
            
            # Should have values from all levels
            assert final_theme["name"] == "Level 3"
            assert final_theme["base_styles"]["body"] == "level2-body"  # From level 2
            assert final_theme["base_styles"]["container"] == "level1-container"  # From level 1
            
            # Should merge color variants from all levels
            assert final_theme["color_variants"]["blue"]["header"] == "level1-blue"  # From level 1
            assert final_theme["color_variants"]["blue"]["accent"] == "level2-blue-accent"  # From level 2
            assert final_theme["color_variants"]["red"]["header"] == "level2-red"  # From level 2
            assert final_theme["color_variants"]["green"]["header"] == "level3-green"  # From level 3
            
        finally:
            # Clean up temp files
            for path in [level1_path, level2_path, level3_path]:
                if path.exists():
                    path.unlink()
    
    def test_inheritance_preserves_original_themes(self):
        """Test that loading inherited themes doesn't modify the original theme files."""
        # Load default theme directly
        default_theme_original = load_theme("default")
        
        # Load inherited theme
        inherited_theme = load_theme("test_inherited")
        
        # Load default theme again
        default_theme_after = load_theme("default")
        
        # Default theme should be unchanged
        assert default_theme_original == default_theme_after
        
        # Inherited theme should be different from default
        assert inherited_theme != default_theme_original
        assert inherited_theme["base_styles"]["body"] != default_theme_original["base_styles"]["body"]