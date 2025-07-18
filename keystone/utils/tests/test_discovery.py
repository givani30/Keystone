import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from keystone.utils.discovery import find_layout_file


class TestConfigFileDiscovery:
    """Test suite for config file auto-discovery functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    def test_find_file_in_current_directory(self, temp_dir):
        """Test finding config file in the current directory."""
        # Create a layout file in the temp directory
        layout_file = temp_dir / "keystone.yml"
        layout_file.write_text("title: Test")
        
        # Search from that directory
        result = find_layout_file(str(temp_dir))
        
        assert result == str(layout_file)
    
    def test_find_file_in_parent_directory(self, temp_dir):
        """Test finding config file in a parent directory."""
        # Create a layout file in the root temp directory
        layout_file = temp_dir / "layout.yml"
        layout_file.write_text("title: Test")
        
        # Create a subdirectory and search from there
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        result = find_layout_file(str(subdir))
        
        assert result == str(layout_file)
    
    def test_find_file_multiple_levels_up(self, temp_dir):
        """Test finding config file multiple levels up the directory tree."""
        # Create a layout file in the root temp directory
        layout_file = temp_dir / ".keystone.yml"
        layout_file.write_text("title: Test")
        
        # Create nested subdirectories and search from the deepest one
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        nested_dir.mkdir(parents=True)
        
        result = find_layout_file(str(nested_dir))
        
        assert result == str(layout_file)
    
    def test_no_config_file_found(self, temp_dir):
        """Test behavior when no config file is found."""
        # Search in an empty directory
        result = find_layout_file(str(temp_dir))
        
        assert result is None
    
    def test_max_depth_limit(self, temp_dir):
        """Test that the search respects the max_depth limit."""
        # Create a layout file in the root temp directory
        layout_file = temp_dir / "keystone.yml"
        layout_file.write_text("title: Test")
        
        # Create many nested subdirectories (more than default max_depth)
        deep_dir = temp_dir
        for i in range(15):  # More than default max_depth of 10
            deep_dir = deep_dir / f"level{i}"
            deep_dir.mkdir()
        
        # Search from the deep directory with default max_depth
        result = find_layout_file(str(deep_dir))
        
        # Should not find the file due to max_depth limit
        assert result is None
        
        # But should find it with increased max_depth
        result = find_layout_file(str(deep_dir), max_depth=20)
        assert result == str(layout_file)
    
    def test_file_priority_order(self, temp_dir):
        """Test that files are found in the correct priority order."""
        # Create multiple config files in the same directory
        keystone_file = temp_dir / "keystone.yml"
        layout_file = temp_dir / "layout.yml"
        dot_keystone_file = temp_dir / ".keystone.yml"
        
        # Create them in reverse priority order to test preference
        dot_keystone_file.write_text("title: Hidden")
        layout_file.write_text("title: Layout")
        keystone_file.write_text("title: Keystone")
        
        result = find_layout_file(str(temp_dir))
        
        # Should find keystone.yml first (highest priority)
        assert result == str(keystone_file)
    
    def test_file_priority_layout_first_when_no_keystone(self, temp_dir):
        """Test that layout.yml is found when keystone.yml doesn't exist."""
        # Create only layout.yml and .keystone.yml
        layout_file = temp_dir / "layout.yml"
        dot_keystone_file = temp_dir / ".keystone.yml"
        
        dot_keystone_file.write_text("title: Hidden")
        layout_file.write_text("title: Layout")
        
        result = find_layout_file(str(temp_dir))
        
        # Should find layout.yml (next in priority)
        assert result == str(layout_file)
    
    def test_file_priority_hidden_file_last(self, temp_dir):
        """Test that .keystone.yml is found only when others don't exist."""
        # Create only .keystone.yml
        dot_keystone_file = temp_dir / ".keystone.yml"
        dot_keystone_file.write_text("title: Hidden")
        
        result = find_layout_file(str(temp_dir))
        
        # Should find .keystone.yml (lowest priority but only option)
        assert result == str(dot_keystone_file)
    
    def test_unreadable_file_is_skipped(self, temp_dir):
        """Test that unreadable files are skipped and search continues."""
        # Create two config files
        unreadable_file = temp_dir / "keystone.yml"
        readable_file = temp_dir / "layout.yml"
        
        unreadable_file.write_text("title: Unreadable")
        readable_file.write_text("title: Readable")
        
        # Make the first file unreadable
        unreadable_file.chmod(0o000)
        
        try:
            result = find_layout_file(str(temp_dir))
            
            # Should skip the unreadable file and find the readable one
            assert result == str(readable_file)
        finally:
            # Restore permissions for cleanup
            unreadable_file.chmod(0o644)
    
    def test_search_stops_at_filesystem_root(self, temp_dir):
        """Test that search stops at filesystem root."""
        # This test is tricky to implement reliably across different systems
        # We'll use a mock to simulate reaching the root
        
        with patch('pathlib.Path.resolve') as mock_resolve:
            # Mock the path resolution to simulate reaching root quickly
            root_path = Path("/")
            mock_resolve.return_value = root_path
            
            result = find_layout_file(str(temp_dir))
            
            # Should return None when no file is found
            assert result is None
    
    def test_default_start_directory(self, temp_dir):
        """Test that function uses current working directory when start_dir is None."""
        # Create a config file in temp directory
        layout_file = temp_dir / "keystone.yml"
        layout_file.write_text("title: Test")
        
        # Change to the temp directory and search without specifying start_dir
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = find_layout_file()  # No start_dir argument
            
            assert result == str(layout_file)
        finally:
            os.chdir(original_cwd)
    
    def test_empty_file_is_readable(self, temp_dir):
        """Test that empty config files are still considered valid."""
        # Create an empty config file
        empty_file = temp_dir / "keystone.yml"
        empty_file.touch()  # Create empty file
        
        result = find_layout_file(str(temp_dir))
        
        assert result == str(empty_file)
    
    def test_directory_with_config_name_ignored(self, temp_dir):
        """Test that directories with config file names are ignored."""
        # Create a directory with a config file name
        config_dir = temp_dir / "keystone.yml"
        config_dir.mkdir()
        
        # Create an actual config file with different name
        actual_config = temp_dir / "layout.yml"
        actual_config.write_text("title: Test")
        
        result = find_layout_file(str(temp_dir))
        
        # Should find the actual file, not the directory
        assert result == str(actual_config)
