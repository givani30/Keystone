def generate_pdf(html_content, output_path):
    # This is a placeholder. A more robust implementation is needed.
    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(output_path)
    except ImportError:
        print("Error: PDF generation requires weasyprint. Install with:")
        print("pip install keystone[pdf]")
