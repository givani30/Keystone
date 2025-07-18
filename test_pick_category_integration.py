#!/usr/bin/env python3
"""
Integration test for pick_category functionality.
This test verifies that the pick_category feature works end-to-end.
"""

import json
import tempfile
import yaml
from pathlib import Path
from keystone.core.layout_parser import parse_layout


def test_pick_category_integration():
    """Test pick_category functionality with a complete workflow."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a source data file with multiple categories
        source_data = {
            "tool": "Test Editor",
            "version": "1.0",
            "categories": [
                {
                    "name": "File Operations",
                    "keybinds": [
                        {"action": "New File", "keys": "Ctrl+N", "description": "Create new file"},
                        {"action": "Open File", "keys": "Ctrl+O", "description": "Open existing file"},
                        {"action": "Save File", "keys": "Ctrl+S", "description": "Save current file"}
                    ]
                },
                {
                    "name": "Editing",
                    "keybinds": [
                        {"action": "Copy", "keys": "Ctrl+C", "description": "Copy selection"},
                        {"action": "Paste", "keys": "Ctrl+V", "description": "Paste from clipboard"},
                        {"action": "Undo", "keys": "Ctrl+Z", "description": "Undo last action"}
                    ]
                },
                {
                    "name": "Navigation",
                    "keybinds": [
                        {"action": "Go to Line", "keys": "Ctrl+G", "description": "Navigate to line"},
                        {"action": "Find", "keys": "Ctrl+F", "description": "Find text"}
                    ]
                }
            ]
        }
        
        source_file = temp_path / "test_source.json"
        with open(source_file, 'w') as f:
            json.dump(source_data, f, indent=2)
        
        # Create a layout file that uses pick_category
        layout_data = {
            "title": "Test Layout",
            "template": "skill_tree", 
            "theme": "default",
            "output_name": "test",
            "categories": [
                {
                    "name": "Selected Operations",
                    "sources": [
                        {
                            "file": str(source_file),
                            "pick_category": "File Operations"  # Pick only File Operations
                        }
                    ]
                },
                {
                    "name": "Multiple Categories",
                    "sources": [
                        {
                            "file": str(source_file),
                            "pick_category": ["Editing", "Navigation"]  # Pick multiple categories
                        }
                    ]
                }
            ]
        }
        
        layout_file = temp_path / "test_layout.yml"
        with open(layout_file, 'w') as f:
            yaml.dump(layout_data, f)
        
        # Parse the layout
        result = parse_layout(str(layout_file))
        
        # Verify the results
        assert "categories" in result
        assert len(result["categories"]) == 2
        
        # Check first category (File Operations only)
        selected_ops = result["categories"][0]
        assert selected_ops["name"] == "Selected Operations"
        assert len(selected_ops["keybinds"]) == 3
        actions = [kb["action"] for kb in selected_ops["keybinds"]]
        assert "New File" in actions
        assert "Open File" in actions
        assert "Save File" in actions
        # Should not contain editing or navigation actions
        assert "Copy" not in actions
        assert "Go to Line" not in actions
        
        # Check second category (Editing + Navigation)
        multiple_cats = result["categories"][1]
        assert multiple_cats["name"] == "Multiple Categories"
        assert len(multiple_cats["keybinds"]) == 5  # 3 from Editing + 2 from Navigation
        actions = [kb["action"] for kb in multiple_cats["keybinds"]]
        # Should contain editing actions
        assert "Copy" in actions
        assert "Paste" in actions
        assert "Undo" in actions
        # Should contain navigation actions
        assert "Go to Line" in actions
        assert "Find" in actions
        # Should not contain file operations
        assert "New File" not in actions
        assert "Open File" not in actions
        assert "Save File" not in actions
        
        print("✅ pick_category integration test passed!")
        print(f"   - Single category selection: {len(selected_ops['keybinds'])} keybinds")
        print(f"   - Multiple category selection: {len(multiple_cats['keybinds'])} keybinds")


if __name__ == "__main__":
    test_pick_category_integration()
