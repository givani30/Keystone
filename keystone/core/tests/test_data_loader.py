import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from keystone.core.data_loader import load_keybind_source


class TestDataLoader:
    
    def test_load_valid_keybind_file(self, tmp_path):
        """Test loading a valid keybind file."""
        valid_data = {
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
                }
            ]
        }
        
        test_file = tmp_path / "valid_keybinds.json"
        test_file.write_text(json.dumps(valid_data))
        
        result = load_keybind_source(str(test_file))
        
        assert result == valid_data
        assert result["tool"] == "VSCode"
        assert len(result["categories"]) == 1
        assert result["categories"][0]["name"] == "File Operations"
        assert len(result["categories"][0]["keybinds"]) == 2
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Keybind data file not found"):
            load_keybind_source("nonexistent_file.json")
    
    def test_load_directory_instead_of_file(self, tmp_path):
        """Test loading a directory instead of a file raises ValueError."""
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()
        
        with pytest.raises(ValueError, match="Path is not a file"):
            load_keybind_source(str(test_dir))
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading a file with invalid JSON."""
        invalid_json = '''
        {
            "tool": "VSCode",
            "categories": []
            // This comment makes it invalid JSON
        }
        '''
        
        test_file = tmp_path / "invalid.json"
        test_file.write_text(invalid_json)
        
        with pytest.raises(json.JSONDecodeError, match="Invalid JSON in file"):
            load_keybind_source(str(test_file))
    
    def test_load_file_missing_required_tool_field(self, tmp_path):
        """Test loading a file missing required 'tool' field."""
        invalid_data = {
            "version": "1.0.0",
            "categories": [
                {
                    "name": "File Operations",
                    "keybinds": [
                        {
                            "action": "Open file",
                            "keys": "Ctrl+O"
                        }
                    ]
                }
            ]
        }
        
        test_file = tmp_path / "missing_tool.json"
        test_file.write_text(json.dumps(invalid_data))
        
        with pytest.raises(ValueError, match="Schema validation failed"):
            load_keybind_source(str(test_file))
    
    def test_load_file_missing_required_keys_field(self, tmp_path):
        """Test loading a file with keybind missing required 'keys' field."""
        invalid_data = {
            "tool": "VSCode",
            "categories": [
                {
                    "name": "File Operations",
                    "keybinds": [
                        {
                            "action": "Open file"
                        }
                    ]
                }
            ]
        }
        
        test_file = tmp_path / "missing_keys.json"
        test_file.write_text(json.dumps(invalid_data))
        
        with pytest.raises(ValueError, match="Schema validation failed"):
            load_keybind_source(str(test_file))
    
    def test_load_file_with_keys_as_array(self, tmp_path):
        """Test loading a file with keys as an array (valid schema)."""
        valid_data = {
            "tool": "VSCode",
            "categories": [
                {
                    "name": "File Operations",
                    "keybinds": [
                        {
                            "action": "Multi-key action",
                            "keys": ["Ctrl+K", "Ctrl+O"]
                        }
                    ]
                }
            ]
        }
        
        test_file = tmp_path / "keys_array.json"
        test_file.write_text(json.dumps(valid_data))
        
        result = load_keybind_source(str(test_file))
        assert result == valid_data
        assert result["categories"][0]["keybinds"][0]["keys"] == ["Ctrl+K", "Ctrl+O"]