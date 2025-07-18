import sys
from pathlib import Path
from typing import Union


def generate_pdf(html_content: str, output_path: Union[str, Path]) -> bool:
    """
    Generate a PDF from HTML content using WeasyPrint.
    
    Args:
        html_content: The HTML content to convert to PDF
        output_path: Path where the PDF should be saved
        
    Returns:
        True if PDF was generated successfully, False if WeasyPrint is not available
        
    Raises:
        SystemExit: If WeasyPrint is not installed (with error code 1)
    """
    try:
        import weasyprint
    except ImportError:
        print("Error: PDF generation requires weasyprint. Install with:", file=sys.stderr)
        print("uv pip install keystone[pdf]", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate PDF using WeasyPrint
        weasyprint.HTML(string=html_content).write_pdf(str(output_path))
        return True
        
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        sys.exit(1)
