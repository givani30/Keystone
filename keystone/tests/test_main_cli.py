import pytest
import tempfile
import json
import yaml
import subprocess
import sys
from pathlib import Path


class TestMainCLI:
    """End-to-end tests for the main CLI entry point."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def sample_layout(self, temp_dir):
        """Create a sample layout file for testing."""
        layout_data = {
            "title": "Test Cheatsheet",
            "template": "skill_tree",
            "theme": "default",
            "output_name": "test_output",
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
                }
            ]
        }
        
        layout_file = temp_dir / "test_layout.yml"
        with open(layout_file, 'w') as f:
            yaml.dump(layout_data, f)
        
        return layout_file
    
    @pytest.fixture 
    def sample_keybind_data(self, temp_dir):
        """Create a sample keybind data file for testing."""
        keybind_data = {
            "tool": "TestTool",
            "version": "1.0.0",
            "categories": [
                {
                    "name": "Editing",
                    "keybinds": [
                        {
                            "action": "Copy",
                            "keys": "Ctrl+C",
                            "description": "Copy selected text"
                        },
                        {
                            "action": "Paste", 
                            "keys": "Ctrl+V",
                            "description": "Paste from clipboard"
                        }
                    ]
                }
            ]
        }
        
        keybind_file = temp_dir / "keybinds.json"
        with open(keybind_file, 'w') as f:
            json.dump(keybind_data, f)
        
        return keybind_file
    
    def run_cli(self, args, cwd=None):
        """Helper to run the CLI and capture output."""
        cmd = [sys.executable, "-m", "keystone.main"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            pytest.fail("CLI command timed out")
    
    def test_help_message(self):
        """Test that help message is displayed correctly."""
        returncode, stdout, stderr = self.run_cli(["--help"])
        
        assert returncode == 0
        assert "Keystone Cheatsheet Generator" in stdout
        assert "layout_file" in stdout
        assert "--output" in stdout
        assert "--format" in stdout
        
    def test_basic_html_generation(self, sample_layout, temp_dir):
        """Test basic HTML generation with default settings."""
        # Change to temp directory for test
        returncode, stdout, stderr = self.run_cli([str(sample_layout)], cwd=temp_dir)
        
        assert returncode == 0
        assert "Loading layout from:" in stdout
        assert "Using theme: default" in stdout
        assert "Generating HTML..." in stdout
        assert "Generated HTML:" in stdout
        
        # Check that output file was created
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
        
        # Check content
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Test Cheatsheet" in content
        assert "File Operations" in content
        # Keys are split into separate boxes, so look for both parts
        assert "Ctrl" in content and "O" in content
    
    def test_custom_output_file(self, sample_layout, temp_dir):
        """Test custom output file specification."""
        output_file = temp_dir / "custom_output.html"
        
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout), 
            "--output", str(output_file)
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert output_file.exists()
        assert "Generated HTML:" in stdout
        assert str(output_file) in stdout
    
    def test_output_with_directory_creation(self, sample_layout, temp_dir):
        """Test that output directories are created automatically."""
        output_file = temp_dir / "subdir" / "nested" / "output.html"
        
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--output", str(output_file)
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert output_file.exists()
        assert output_file.parent.exists()
    
    def test_theme_override(self, sample_layout, temp_dir):
        """Test theme override via CLI argument."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--theme", "dark"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Using theme: dark" in stdout
    
    def test_template_override_error(self, sample_layout, temp_dir):
        """Test template override with unsupported template."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "reference_card"
        ], cwd=temp_dir)
        
        assert returncode == 1
        assert "Template 'reference_card' not yet implemented" in stderr
    
    def test_pdf_format_warning(self, sample_layout, temp_dir):
        """Test PDF format produces warning."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "pdf"
        ], cwd=temp_dir)
        
        assert returncode == 1
        assert "PDF generation not yet implemented" in stderr
    
    def test_both_format(self, sample_layout, temp_dir):
        """Test 'both' format generates HTML and shows PDF warning."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "both"
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Generated HTML:" in stdout
        assert "PDF generation not yet implemented" in stderr
        
        # HTML should still be generated
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
    
    def test_missing_layout_file(self, temp_dir):
        """Test error handling for missing layout file."""
        returncode, stdout, stderr = self.run_cli([
            "nonexistent.yml"
        ], cwd=temp_dir)
        
        assert returncode == 1
        assert "Layout file 'nonexistent.yml' not found" in stderr
    
    def test_invalid_yaml(self, temp_dir):
        """Test error handling for invalid YAML."""
        invalid_layout = temp_dir / "invalid.yml"
        invalid_layout.write_text("title: test\ninvalid yaml: [unclosed")
        
        returncode, stdout, stderr = self.run_cli([
            str(invalid_layout)
        ], cwd=temp_dir)
        
        assert returncode == 1
        assert "Error:" in stderr
    
    def test_invalid_theme(self, sample_layout, temp_dir):
        """Test error handling for invalid theme."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--theme", "nonexistent_theme"
        ], cwd=temp_dir)
        
        assert returncode == 1
        assert "Error:" in stderr
    
    def test_layout_with_sources(self, temp_dir, sample_keybind_data):
        """Test layout file that references external source files."""
        layout_data = {
            "title": "Combined Cheatsheet",
            "template": "skill_tree", 
            "theme": "default",
            "output_name": "combined",
            "categories": [
                {
                    "name": "Editing",
                    "sources": [
                        {
                            "file": str(sample_keybind_data),
                            "pick_category": "Editing"
                        }
                    ],
                    "keybinds": [
                        {
                            "action": "Undo",
                            "keys": "Ctrl+Z",
                            "description": "Undo last action"
                        }
                    ]
                }
            ]
        }
        
        layout_file = temp_dir / "combined_layout.yml"
        with open(layout_file, 'w') as f:
            yaml.dump(layout_data, f)
        
        returncode, stdout, stderr = self.run_cli([str(layout_file)], cwd=temp_dir)
        
        assert returncode == 0
        
        # Check that output includes both source and inline keybinds
        output_file = temp_dir / "combined.html"
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "Copy" in content  # From source
        assert "Paste" in content  # From source
        assert "Undo" in content  # Inline
    
    def test_permission_error_simulation(self, sample_layout, temp_dir):
        """Test handling of permission errors (simulated)."""
        # Create a directory without write permissions
        restricted_dir = temp_dir / "restricted"
        restricted_dir.mkdir(mode=0o444)  # Read-only
        
        try:
            output_file = restricted_dir / "output.html"
            
            returncode, stdout, stderr = self.run_cli([
                str(sample_layout),
                "--output", str(output_file)
            ], cwd=temp_dir)
            
            # Should fail with permission error
            assert returncode == 1
            assert "Error:" in stderr
        finally:
            # Restore permissions for cleanup
            restricted_dir.chmod(0o755)