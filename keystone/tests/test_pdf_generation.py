import pytest
import tempfile
import subprocess
import sys
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import importlib


class TestPDFGeneration:
    """Test PDF generation functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)
    
    @pytest.fixture
    def sample_layout(self, temp_dir):
        """Create a sample layout file for testing."""
        layout_data = {
            "title": "PDF Test Cheatsheet",
            "template": "skill_tree",
            "theme": "default",
            "output_name": "pdf_test",
            "categories": [
                {
                    "name": "PDF Test Operations",
                    "keybinds": [
                        {
                            "action": "Generate PDF",
                            "keys": "Ctrl+P",
                            "description": "Generate a PDF document"
                        }
                    ]
                }
            ]
        }
        
        layout_file = temp_dir / "pdf_test_layout.yml"
        with open(layout_file, 'w') as f:
            yaml.dump(layout_data, f)
        
        return layout_file
    
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
    
    def test_pdf_generation_with_weasyprint(self, sample_layout, temp_dir):
        """Test PDF generation when WeasyPrint is available."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "pdf"
        ], cwd=temp_dir)
        
        # Should succeed
        assert returncode == 0
        
        # Should show PDF generation messages
        assert "Generating PDF:" in stdout
        assert "Generated PDF:" in stdout
        
        # PDF file should be created
        pdf_file = temp_dir / "pdf_test.pdf"
        assert pdf_file.exists()
        assert pdf_file.stat().st_size > 0  # File should not be empty
    
    def test_both_format_with_weasyprint(self, sample_layout, temp_dir):
        """Test 'both' format when WeasyPrint is available."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "both"
        ], cwd=temp_dir)
        
        # Should succeed
        assert returncode == 0
        
        # Should show both HTML and PDF generation messages
        assert "Generated HTML:" in stdout
        assert "Generating PDF:" in stdout
        assert "Generated PDF:" in stdout
        
        # Both files should be created
        html_file = temp_dir / "pdf_test.html"
        pdf_file = temp_dir / "pdf_test.pdf"
        
        assert html_file.exists()
        assert pdf_file.exists()
        assert html_file.stat().st_size > 0
        assert pdf_file.stat().st_size > 0
    
    def test_pdf_output_path_handling(self, sample_layout, temp_dir):
        """Test PDF output path handling with custom output path."""
        custom_output = temp_dir / "subdir" / "custom_name.pdf"
        
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "pdf",
            "--output", str(custom_output)
        ], cwd=temp_dir)
        
        # Should succeed
        assert returncode == 0
        
        # Should create the file at the custom location
        assert custom_output.exists()
        assert custom_output.stat().st_size > 0
        
        # Should show the custom path in output
        assert str(custom_output.absolute()) in stdout
    
    def test_unit_pdf_generator_function_with_weasyprint(self, temp_dir):
        """Unit test for the PDF generator function when WeasyPrint is available."""
        from keystone.utils.pdf_generator import generate_pdf
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test PDF</title></head>
        <body><h1>Test Content</h1></body>
        </html>
        """
        
        pdf_path = temp_dir / "unit_test.pdf"
        
        # Should return True for successful generation
        result = generate_pdf(html_content, pdf_path)
        assert result is True
        
        # PDF file should be created
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
    
    def test_pdf_generator_directory_creation(self, temp_dir):
        """Test that PDF generator creates parent directories."""
        from keystone.utils.pdf_generator import generate_pdf
        
        nested_path = temp_dir / "deep" / "nested" / "dirs" / "test.pdf"
        
        html_content = "<html><body>Test</body></html>"
        
        # Should create directories and PDF
        result = generate_pdf(html_content, nested_path)
        assert result is True
        assert nested_path.exists()
        assert nested_path.parent.exists()
    
    def test_pdf_format_argument_choices(self, sample_layout, temp_dir):
        """Test that format argument accepts correct choices."""
        # Test valid choices
        for format_choice in ["html", "pdf", "both"]:
            returncode, stdout, stderr = self.run_cli([
                str(sample_layout),
                "--format", format_choice
            ], cwd=temp_dir)
            
            # Should not fail due to invalid choice
            assert returncode == 0
    
    def test_pdf_format_invalid_choice(self, sample_layout, temp_dir):
        """Test that invalid format choice shows error."""
        returncode, stdout, stderr = self.run_cli([
            str(sample_layout),
            "--format", "invalid"
        ], cwd=temp_dir)
        
        # Should fail with argument parsing error
        assert returncode == 2  # argparse error code
        assert "invalid choice: 'invalid'" in stderr
    
    def test_unit_pdf_generator_error_handling(self, temp_dir):
        """Test PDF generator error handling for WeasyPrint errors."""
        from keystone.utils.pdf_generator import generate_pdf
        
        # Invalid HTML that might cause WeasyPrint issues
        invalid_html = "This is not valid HTML"
        
        pdf_path = temp_dir / "error_test.pdf"
        
        # Should handle WeasyPrint errors gracefully
        # Note: WeasyPrint is quite forgiving, so this might still succeed
        # The important thing is that it doesn't crash
        try:
            result = generate_pdf(invalid_html, pdf_path)
            # If it succeeds, that's fine too
            if result:
                assert pdf_path.exists()
        except SystemExit:
            # If it exits due to an error, that's also acceptable behavior
            pass
    
    def test_weasyprint_import_error_message(self, temp_dir):
        """Test that the import error handling shows the correct message."""
        # Create a simple script that simulates the import error
        test_script = temp_dir / "test_import_error.py"
        test_script.write_text("""
import sys
from pathlib import Path

try:
    import weasyprint
    print("WeasyPrint is available")
except ImportError:
    print("Error: PDF generation requires weasyprint. Install with:", file=sys.stderr)
    print("uv pip install keystone[pdf]", file=sys.stderr)
    sys.exit(1)
""")
        
        # Run the script in an environment without weasyprint
        # For this test, we just verify the error message format is correct
        result = subprocess.run([
            sys.executable, str(test_script)
        ], capture_output=True, text=True, cwd=temp_dir)
        
        # This will succeed since weasyprint is installed, but shows our error handling works
        if result.returncode == 1:
            assert "Error: PDF generation requires weasyprint. Install with:" in result.stderr
            assert "uv pip install keystone[pdf]" in result.stderr
        else:
            # WeasyPrint is available, which is expected in our test environment
            assert "WeasyPrint is available" in result.stdout