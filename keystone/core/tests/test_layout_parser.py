import pytest
import yaml
from keystone.core import layout_parser

@pytest.fixture
def valid_layout_file(tmp_path):
    content = """
    title: Test Cheatsheet
    template: test_template
    theme: test_theme
    output_name: test_output
    categories:
      - name: Test Category
    """
    file_path = tmp_path / "layout.yml"
    file_path.write_text(content)
    return file_path

@pytest.fixture
def invalid_layout_file(tmp_path):
    content = """
    title: Test Cheatsheet
    template: test_template
    theme: test_theme
    output_name: test_output
    categories: 
      - name: Test Category
      foo: bar # Invalid YAML
    """
    file_path = tmp_path / "layout.yml"
    file_path.write_text(content)
    return file_path

def test_parse_layout_valid(valid_layout_file):
    layout = layout_parser.parse_layout(valid_layout_file)
    assert layout["title"] == "Test Cheatsheet"

def test_parse_layout_invalid(invalid_layout_file):
    with pytest.raises(yaml.YAMLError):
        layout_parser.parse_layout(invalid_layout_file)
