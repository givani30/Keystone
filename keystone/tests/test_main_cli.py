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
        # Set the project root and add to PYTHONPATH
        project_root = Path(__file__).parent.parent.parent
        
        # Get current environment and add PYTHONPATH
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        
        cmd = [sys.executable, "-m", "keystone"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or project_root,
                timeout=30,
                env=env
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
    
    def test_template_override_reference_card(self, sample_layout, temp_dir):
        """Test template override with reference_card template."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "reference_card"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Using template: reference_card" in stdout
        assert "Generated HTML:" in stdout
        
        # Check that output file was created
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
        
        # Check content contains template-specific elements
        content = output_file.read_text()
        assert "Test Cheatsheet" in content
        assert "Reference Card" in content or "reference" in content.lower()
    
    def test_pdf_format_generation(self, sample_layout, temp_dir):
        """Test PDF format generates PDF file."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "pdf"
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Generating PDF:" in stdout
        assert "Generated PDF:" in stdout
        
        # PDF file should be created
        pdf_file = temp_dir / "test_output.pdf"
        assert pdf_file.exists()
    
    def test_both_format(self, sample_layout, temp_dir):
        """Test 'both' format generates both HTML and PDF files."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "both"
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Generated HTML:" in stdout
        assert "Generating PDF:" in stdout
        assert "Generated PDF:" in stdout
        
        # Both files should be generated
        html_file = temp_dir / "test_output.html"
        pdf_file = temp_dir / "test_output.pdf"
        assert html_file.exists()
        assert pdf_file.exists()
    
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
    
    # New comprehensive tests for template and theme combinations
    
    def test_skill_tree_template_with_default_theme(self, sample_layout, temp_dir):
        """Test skill_tree template with default theme."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "skill_tree",
            "--theme", "default"
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Using template: skill_tree" in stdout
        assert "Using theme: default" in stdout
        assert "Generated HTML:" in stdout
        
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
    
    def test_skill_tree_template_with_dark_theme(self, sample_layout, temp_dir):
        """Test skill_tree template with dark theme.""" 
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "skill_tree",
            "--theme", "dark"
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Using template: skill_tree" in stdout
        assert "Using theme: dark" in stdout
        
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
    
    def test_reference_card_template_with_default_theme(self, sample_layout, temp_dir):
        """Test reference_card template with default theme."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "reference_card",
            "--theme", "default"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Using template: reference_card" in stdout
        assert "Using theme: default" in stdout
        
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
    
    def test_reference_card_template_with_minimal_theme(self, sample_layout, temp_dir):
        """Test reference_card template with minimal theme."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "reference_card", 
            "--theme", "minimal"
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Using template: reference_card" in stdout
        assert "Using theme: minimal" in stdout
        
        output_file = temp_dir / "test_output.html"
        assert output_file.exists()
    
    def test_all_template_theme_combinations_with_pdf(self, sample_layout, temp_dir):
        """Test all template and theme combinations with PDF output."""
        templates = ["skill_tree", "reference_card"]
        themes = ["default", "dark", "minimal", "dark_simple"]
        
        for template in templates:
            for theme in themes:
                output_name = f"test_{template}_{theme}"
                
                returncode, stdout, stderr = self.run_cli([
                    str(sample_layout),
                    "--template", template,
                    "--theme", theme,
                    "--format", "both",
                    "--output", output_name
                ], cwd=temp_dir)
                
                if returncode != 0:
                    print(f"Failed for template={template}, theme={theme}")
                    print(f"STDOUT: {stdout}")
                    print(f"STDERR: {stderr}")
                
                assert returncode == 0
                assert f"Using template: {template}" in stdout
                assert f"Using theme: {theme}" in stdout
                assert "Generated HTML:" in stdout
                assert "Generated PDF:" in stdout
                
                # Check both files were created
                html_file = temp_dir / f"{output_name}.html"
                pdf_file = temp_dir / f"{output_name}.pdf"
                assert html_file.exists(), f"HTML file missing for {template}/{theme}"
                assert pdf_file.exists(), f"PDF file missing for {template}/{theme}"
    
    def test_template_theme_override_layout_file(self, temp_dir):
        """Test that CLI flags override template and theme specified in layout file."""
        # Create layout with specific template and theme
        layout_data = {
            "title": "Override Test",
            "template": "skill_tree",  # Will be overridden
            "theme": "default",        # Will be overridden
            "output_name": "override_test",
            "categories": [
                {
                    "name": "Test Category",
                    "keybinds": [
                        {
                            "action": "Test Action",
                            "keys": "Ctrl+T",
                            "description": "Test description"
                        }
                    ]
                }
            ]
        }
        
        layout_file = temp_dir / "override_layout.yml"
        with open(layout_file, 'w') as f:
            yaml.dump(layout_data, f)
        
        # Test that CLI overrides take precedence
        returncode, stdout, stderr = self.run_cli([
            str(layout_file),
            "--template", "reference_card",  # Override layout file
            "--theme", "dark"                # Override layout file
        ], cwd=temp_dir)
        
        assert returncode == 0
        assert "Using template: reference_card" in stdout
        assert "Using theme: dark" in stdout
        
        output_file = temp_dir / "override_test.html"
        assert output_file.exists()
    
    def test_invalid_template_choice_error(self, sample_layout, temp_dir):
        """Test error handling for invalid template choice."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "invalid_template"
        ], cwd=temp_dir)
        
        # Should fail at argument parsing level
        assert returncode == 2
        assert "invalid choice" in stderr
        assert "choose from 'skill_tree', 'reference_card'" in stderr
    
    def test_complex_flag_combination(self, sample_layout, temp_dir):
        """Test complex combination of all flags together."""
        custom_output = temp_dir / "complex" / "nested" / "output.html"
        
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--template", "reference_card",
            "--theme", "dark_simple", 
            "--format", "both",
            "--output", str(custom_output)
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Using template: reference_card" in stdout
        assert "Using theme: dark_simple" in stdout
        assert "Generated HTML:" in stdout
        assert "Generated PDF:" in stdout
        
        # Check files were created in nested directory
        assert custom_output.exists()
        
        # When output has .html extension, PDF gets _pdf suffix 
        pdf_output = custom_output.parent / f"{custom_output.stem}_pdf.pdf"
        assert pdf_output.exists()

    def test_validate_command_with_valid_layout(self, sample_layout, temp_dir):
        """Test --validate command with a valid layout file."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--validate"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "✓ Validation successful!" in stdout
        assert "All references are valid" in stdout

    def test_validate_command_auto_discovery(self, temp_dir):
        """Test --validate command with auto-discovery."""
        # Create a keystone.yml file in the temp directory
        layout_data = {
            "title": "Auto-discovered Test Cheatsheet",
            "template": "skill_tree",
            "theme": "default",
            "output_name": "test_output",
            "categories": [
                {
                    "name": "File Operations",
                    "theme_color": "blue",
                    "icon_name": "terminal",
                    "keybinds": [
                        {
                            "action": "Open file",
                            "keys": "Ctrl+O",
                            "description": "Open a file"
                        }
                    ]
                }
            ]
        }
        
        keystone_file = temp_dir / "keystone.yml"
        with open(keystone_file, 'w') as f:
            yaml.dump(layout_data, f)
        
        returncode, stdout, stderr = self.run_cli([
            "--validate"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Found configuration file:" in stdout
        assert "✓ Validation successful!" in stdout

    def test_validate_command_with_invalid_layout(self, temp_dir):
        """Test --validate command with an invalid layout file."""
        # Create a layout file with invalid theme/icon references
        invalid_layout_data = {
            "title": "Invalid Test Cheatsheet",
            "template": "skill_tree",
            "theme": "default",
            "output_name": "test_output",
            "categories": [
                {
                    "name": "File Operations",
                    "theme_color": "nonexistent_color",
                    "icon_name": "nonexistent_icon",
                    "keybinds": [
                        {
                            "action": "Open file",
                            "keys": "Ctrl+O",
                            "description": "Open a file"
                        }
                    ]
                }
            ]
        }
        
        invalid_layout = temp_dir / "invalid_layout.yml"
        with open(invalid_layout, 'w') as f:
            yaml.dump(invalid_layout_data, f)
        
        returncode, stdout, stderr = self.run_cli([
            str(invalid_layout),
            "--validate"
        ], cwd=temp_dir)
        
        assert returncode == 1
        assert "✗ Validation failed:" in stderr

    def test_list_themes_command(self, temp_dir):
        """Test --list-themes command."""
        returncode, stdout, stderr = self.run_cli([
            "--list-themes"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Available themes:" in stdout
        assert "• default" in stdout
        assert "• dark" in stdout
        assert "• minimal" in stdout
        assert "To use a theme, run:" in stdout

    def test_init_command(self, temp_dir):
        """Test --init command creates example files."""
        returncode, stdout, stderr = self.run_cli([
            "--init"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Created: keystone.yml" in stdout
        assert "Created: example_keybinds.json" in stdout
        assert "📁 Example files created successfully!" in stdout
        
        # Check that files were actually created
        keystone_file = temp_dir / "keystone.yml"
        keybinds_file = temp_dir / "example_keybinds.json"
        
        assert keystone_file.exists()
        assert keybinds_file.exists()
        
        # Check that created files have valid content
        with open(keystone_file, 'r') as f:
            layout_content = yaml.safe_load(f)
            assert layout_content["title"] == "Example Cheatsheet"
            assert layout_content["template"] == "skill_tree"
            assert layout_content["theme"] == "default"
            assert len(layout_content["categories"]) == 2
        
        with open(keybinds_file, 'r') as f:
            keybinds_content = json.load(f)
            assert keybinds_content["tool"] == "Example Editor"
            assert keybinds_content["version"] == "1.0"
            assert len(keybinds_content["categories"]) == 2

    def test_init_command_handles_existing_files(self, temp_dir):
        """Test --init command handles existing files gracefully."""
        # Create existing files
        existing_keystone = temp_dir / "keystone.yml"
        existing_keybinds = temp_dir / "example_keybinds.json"
        
        existing_keystone.write_text("existing content")
        existing_keybinds.write_text("existing content")
        
        returncode, stdout, stderr = self.run_cli([
            "--init"
        ], cwd=temp_dir)
        
        if returncode != 0:
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        assert returncode == 0
        assert "Warning: keystone.yml already exists, skipping..." in stdout
        assert "Warning: example_keybinds.json already exists, skipping..." in stdout
        
        # Check that existing files were not overwritten
        assert existing_keystone.read_text() == "existing content"
        assert existing_keybinds.read_text() == "existing content"

    def test_init_and_validate_integration(self, temp_dir):
        """Test that files created by --init pass --validate."""
        # First run init
        init_returncode, init_stdout, init_stderr = self.run_cli([
            "--init"
        ], cwd=temp_dir)
        
        assert init_returncode == 0
        
        # Then run validate
        validate_returncode, validate_stdout, validate_stderr = self.run_cli([
            "--validate"
        ], cwd=temp_dir)
        
        if validate_returncode != 0:
            print(f"VALIDATE STDOUT: {validate_stdout}")
            print(f"VALIDATE STDERR: {validate_stderr}")
        
        assert validate_returncode == 0
        assert "✓ Validation successful!" in validate_stdout

    def test_init_and_generate_integration(self, temp_dir):
        """Test that files created by --init can generate output."""
        # First run init
        init_returncode, init_stdout, init_stderr = self.run_cli([
            "--init"
        ], cwd=temp_dir)
        
        assert init_returncode == 0
        
        # Then generate output
        generate_returncode, generate_stdout, generate_stderr = self.run_cli([
            "keystone.yml"
        ], cwd=temp_dir)
        
        if generate_returncode != 0:
            print(f"GENERATE STDOUT: {generate_stdout}")
            print(f"GENERATE STDERR: {generate_stderr}")
        
        assert generate_returncode == 0
        assert "Generated HTML:" in generate_stdout
        
        # Check that output file was created
        output_file = temp_dir / "cheatsheet.html"
        assert output_file.exists()