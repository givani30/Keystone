import pytest
import yaml
import json
import tempfile
from pathlib import Path
from keystone.core.layout_parser import (
    parse_layout,
    process_layout,
    merge_category_data,
    load_source_keybinds,
    extract_categories,
    merge_keybinds
)


class TestLayoutParser:
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def sample_keybind_data(self):
        """Sample keybind data for testing."""
        return {
            "tool": "TestTool",
            "version": "1.0.0",
            "categories": [
                {
                    "name": "File Operations",
                    "keybinds": [
                        {
                            "action": "Open file",
                            "keys": "Ctrl+O",
                            "description": "Open a file"
                        },
                        {
                            "action": "Save file",
                            "keys": "Ctrl+S",
                            "description": "Save the current file"
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
    
    def test_merge_keybinds_basic(self):
        """Test basic keybind merging."""
        base_keybinds = [
            {"action": "Open file", "keys": "Ctrl+O"},
            {"action": "Save file", "keys": "Ctrl+S", "description": "Original"}
        ]
        
        new_keybinds = [
            {"action": "Save file", "keys": "Ctrl+S", "description": "Updated"},
            {"action": "New file", "keys": "Ctrl+N"}
        ]
        
        result = merge_keybinds(base_keybinds, new_keybinds)
        
        assert len(result) == 3
        
        # Check that Save file was overridden
        save_keybind = next(kb for kb in result if kb["action"] == "Save file")
        assert save_keybind["description"] == "Updated"
        
        # Check that Open file was preserved
        open_keybind = next(kb for kb in result if kb["action"] == "Open file")
        assert open_keybind["keys"] == "Ctrl+O"
        
        # Check that New file was added
        new_keybind = next(kb for kb in result if kb["action"] == "New file")
        assert new_keybind["keys"] == "Ctrl+N"
    
    def test_merge_keybinds_empty(self):
        """Test merging with empty lists."""
        base_keybinds = [{"action": "Open file", "keys": "Ctrl+O"}]
        new_keybinds = []
        
        result = merge_keybinds(base_keybinds, new_keybinds)
        assert len(result) == 1
        assert result[0]["action"] == "Open file"
        
        # Test with empty base
        result = merge_keybinds([], base_keybinds)
        assert len(result) == 1
        assert result[0]["action"] == "Open file"
    
    def test_extract_categories_single(self, sample_keybind_data):
        """Test extracting a single category."""
        result = extract_categories(sample_keybind_data, "File Operations")
        
        assert len(result) == 2
        assert result[0]["action"] == "Open file"
        assert result[1]["action"] == "Save file"
    
    def test_extract_categories_multiple(self, sample_keybind_data):
        """Test extracting multiple categories."""
        result = extract_categories(sample_keybind_data, ["File Operations", "Editing"])
        
        assert len(result) == 3
        actions = [kb["action"] for kb in result]
        assert "Open file" in actions
        assert "Save file" in actions
        assert "Copy" in actions
    
    def test_extract_categories_nonexistent(self, sample_keybind_data):
        """Test extracting non-existent category."""
        result = extract_categories(sample_keybind_data, "NonExistent")
        assert len(result) == 0
    
    def test_load_source_keybinds_with_pick_category(self, temp_dir, sample_keybind_data):
        """Test loading source keybinds with pick_category."""
        # Create a test source file
        source_file = temp_dir / "test_source.json"
        with open(source_file, 'w') as f:
            json.dump(sample_keybind_data, f)
        
        source_config = {
            "file": str(source_file),
            "pick_category": "File Operations"
        }
        
        result = load_source_keybinds(source_config, temp_dir)
        
        assert len(result) == 2
        assert result[0]["action"] == "Open file"
        assert result[1]["action"] == "Save file"
    
    def test_load_source_keybinds_all_categories(self, temp_dir, sample_keybind_data):
        """Test loading source keybinds without pick_category."""
        # Create a test source file
        source_file = temp_dir / "test_source.json"
        with open(source_file, 'w') as f:
            json.dump(sample_keybind_data, f)
        
        source_config = {
            "file": str(source_file)
        }
        
        result = load_source_keybinds(source_config, temp_dir)
        
        assert len(result) == 3
        actions = [kb["action"] for kb in result]
        assert "Open file" in actions
        assert "Save file" in actions
        assert "Copy" in actions
    
    def test_priority_order_multiple_sources(self, temp_dir):
        """Test that sources are processed in order and inline has highest priority."""
        # Create first source
        source1_data = {
            "tool": "Test",
            "categories": [
                {
                    "name": "Test Category",
                    "keybinds": [
                        {"action": "Test Action", "keys": "Key1", "description": "From source 1"},
                        {"action": "Source1 Only", "keys": "Key2"}
                    ]
                }
            ]
        }
        source1_file = temp_dir / "source1.json"
        with open(source1_file, 'w') as f:
            json.dump(source1_data, f)
        
        # Create second source
        source2_data = {
            "tool": "Test",
            "categories": [
                {
                    "name": "Test Category",
                    "keybinds": [
                        {"action": "Test Action", "keys": "Key1", "description": "From source 2"},
                        {"action": "Source2 Only", "keys": "Key3"}
                    ]
                }
            ]
        }
        source2_file = temp_dir / "source2.json"
        with open(source2_file, 'w') as f:
            json.dump(source2_data, f)
        
        # Create layout with multiple sources and inline
        layout_data = {
            "title": "Priority Test",
            "template": "skill_tree",
            "theme": "default",
            "output_name": "test",
            "categories": [
                {
                    "name": "Test Category",
                    "sources": [
                        {"file": str(source1_file), "pick_category": "Test Category"},
                        {"file": str(source2_file), "pick_category": "Test Category"}
                    ],
                    "keybinds": [
                        {"action": "Test Action", "keys": "Key1", "description": "From inline"}
                    ]
                }
            ]
        }
        
        result = process_layout(layout_data, temp_dir)
        keybinds = result["categories"][0]["keybinds"]
        
        # Should have 3 keybinds total
        assert len(keybinds) == 3
        
        # Test Action should be overridden by inline (highest priority)
        test_action = next(kb for kb in keybinds if kb["action"] == "Test Action")
        assert test_action["description"] == "From inline"
        
        # Both source-only actions should be present
        source1_only = next(kb for kb in keybinds if kb["action"] == "Source1 Only")
        assert source1_only["keys"] == "Key2"
        
        source2_only = next(kb for kb in keybinds if kb["action"] == "Source2 Only")
        assert source2_only["keys"] == "Key3"
