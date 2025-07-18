import argparse
import sys
import importlib
from pathlib import Path
from typing import Dict, Any

from .core.layout_parser import parse_layout
from .core.validator import validate_references
from .utils.theme_loader import load_theme, load_icons
from .utils.pdf_generator import generate_pdf
from .utils.discovery import find_layout_file


def main():
    parser = argparse.ArgumentParser(
        description="Keystone Cheatsheet Generator",
        prog="keystone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  keystone layout.yml                         # Generate HTML with default settings
  keystone layout.yml --output cheatsheet.html
  keystone layout.yml --format pdf --output cheatsheet.pdf
  keystone layout.yml --template skill_tree --theme dark
        """
    )
    
    # Layout file argument (now optional)
    parser.add_argument(
        "layout_file", 
        nargs="?",  # Make it optional
        help="The layout configuration file (YAML format). If not provided, will search for keystone.yml, layout.yml, or .keystone.yml"
    )
    
    # Optional arguments
    parser.add_argument(
        "--template", 
        choices=["skill_tree", "reference_card"],
        help="Override the template specified in the layout file (choices: skill_tree, reference_card)"
    )
    parser.add_argument(
        "--theme", 
        help="Override the theme specified in the layout file"
    )
    parser.add_argument(
        "--format", 
        choices=["html", "pdf", "both"], 
        default="html", 
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--output", 
        help="Output file name (default: derived from layout file)"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate the configuration files without generating output"
    )
    parser.add_argument(
        "--init", 
        action="store_true", 
        help="Create example files in current directory"
    )
    parser.add_argument(
        "--list-themes", 
        action="store_true", 
        help="List available themes"
    )

    args = parser.parse_args()

    try:
        # For now, focus on basic HTML generation
        if args.validate:
            print("Validation mode not yet implemented.")
            return 1
        
        if args.init:
            print("Init mode not yet implemented.")
            return 1
            
        if args.list_themes:
            print("List themes mode not yet implemented.")
            return 1

        # Determine layout file to use
        if args.layout_file:
            # Use the provided layout file
            layout_file_path = args.layout_file
        else:
            # Try to auto-discover layout file
            print("No layout file specified, searching for configuration file...")
            discovered_file = find_layout_file()
            if discovered_file:
                layout_file_path = discovered_file
                print(f"Found configuration file: {layout_file_path}")
            else:
                print("Error: No layout file specified and no configuration file found.", file=sys.stderr)
                print("Searched for: keystone.yml, layout.yml, .keystone.yml", file=sys.stderr)
                print("Please provide a layout file as an argument or create one of the above files.", file=sys.stderr)
                return 1

        # Check if layout file exists
        layout_path = Path(layout_file_path)
        if not layout_path.exists():
            print(f"Error: Layout file '{layout_file_path}' not found.", file=sys.stderr)
            return 1

        # Parse the layout file
        print(f"Loading layout from: {layout_file_path}")
        layout_data = parse_layout(layout_file_path)
        
        # Determine theme to use (CLI override takes precedence)
        theme_name = args.theme or layout_data.get("theme", "default")
        print(f"Using theme: {theme_name}")
        
        # Load theme and icons
        theme = load_theme(theme_name)
        icons = load_icons()
        
        # Validate theme and icon references
        print("Validating theme and icon references...")
        is_valid, error_message = validate_references(layout_data, theme, icons)
        if not is_valid:
            print(f"Error: {error_message}", file=sys.stderr)
            return 1
        
        # Generate HTML using dynamically imported template
        template_name = args.template or layout_data.get("template", "skill_tree")
        
        try:
            # Dynamically import the template module
            template_module = importlib.import_module(f"keystone.templates.{template_name}")
            generate_html = template_module.generate_html
        except ImportError:
            print(f"Error: Template '{template_name}' not found. Available templates: skill_tree, reference_card", file=sys.stderr)
            return 1
        except AttributeError:
            print(f"Error: Template '{template_name}' does not have a generate_html function.", file=sys.stderr)
            return 1
            
        print(f"Using template: {template_name}")
        print("Generating HTML...")
        html_content = generate_html(layout_data, theme, icons)
        
        # Determine output file paths
        if args.output:
            output_base = Path(args.output)
            if output_base.suffix:
                # User provided full filename with extension
                output_dir = output_base.parent
                output_name = output_base.stem
                output_extension = output_base.suffix
            else:
                # User provided just a name/path without extension
                output_dir = output_base.parent if str(output_base) != output_base.name else Path(".")
                output_name = output_base.name
                output_extension = None
        else:
            # Use output_name from layout or derive from layout file
            output_dir = Path(".")
            output_name = layout_data.get("output_name", layout_path.stem)
            output_extension = None
        
        # Handle different output formats
        if args.format == "html" or args.format == "both":
            # Write HTML output
            if output_extension == ".html":
                html_output = output_dir / f"{output_name}{output_extension}"
            elif output_extension is None:
                html_output = output_dir / f"{output_name}.html"
            else:
                html_output = output_dir / f"{output_name}_html.html"
            
            html_path = Path(html_output)
            try:
                # Create parent directory if it doesn't exist
                html_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Generated HTML: {html_path.absolute()}")
            except PermissionError:
                print(f"Error: Permission denied when writing to '{html_path}'", file=sys.stderr)
                return 1
            except OSError as e:
                print(f"Error: Could not write to '{html_path}': {e}", file=sys.stderr)
                return 1
        
        if args.format == "pdf" or args.format == "both":
            # Generate PDF output
            if output_extension == ".pdf":
                pdf_output = output_dir / f"{output_name}{output_extension}"
            elif output_extension is None:
                pdf_output = output_dir / f"{output_name}.pdf"
            else:
                pdf_output = output_dir / f"{output_name}_pdf.pdf"
            
            print(f"Generating PDF: {pdf_output}")
            generate_pdf(html_content, pdf_output)
            print(f"Generated PDF: {Path(pdf_output).absolute()}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())