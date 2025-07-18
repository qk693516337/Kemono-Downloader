# SinglePDF.py

import os
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

class PDF(FPDF):
    """Custom PDF class to handle headers and footers."""
    def header(self):
        # No header
        pass

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

def create_single_pdf_from_content(posts_data, output_filename, font_path, logger=print):
    """
    Creates a single PDF from a list of post titles and content.

    Args:
        posts_data (list): A list of dictionaries, where each dict has 'title' and 'content' keys.
        output_filename (str): The full path for the output PDF file.
        font_path (str): Path to the DejaVuSans.ttf font file.
        logger (function, optional): A function to log progress and errors. Defaults to print.
    """
    if not FPDF_AVAILABLE:
        logger("❌ PDF Creation failed: 'fpdf2' library is not installed. Please run: pip install fpdf2")
        return False

    if not posts_data:
        logger("   No text content was collected to create a PDF.")
        return False

    pdf = PDF()
    
    try:
        if not os.path.exists(font_path):
            raise RuntimeError("Font file not found.")
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.add_font('DejaVu', 'B', font_path, uni=True) # Add Bold variant
    except Exception as font_error:
        logger(f"   ⚠️ Could not load DejaVu font: {font_error}")
        logger("      PDF may not support all characters. Falling back to default Arial font.")
        pdf.set_font('Arial', '', 12)
        pdf.set_font('Arial', 'B', 16)

    logger(f"   Starting PDF creation with content from {len(posts_data)} posts...")

    for post in posts_data:
        pdf.add_page()
        # Post Title
        pdf.set_font('DejaVu', 'B', 16)

        # vvv THIS LINE IS CORRECTED vvv
        # We explicitly set align='L' and remove the incorrect positional arguments.
        pdf.multi_cell(w=0, h=10, text=post.get('title', 'Untitled Post'), align='L')
        
        pdf.ln(5) # Add a little space after the title

        # Post Content
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(w=0, h=7, text=post.get('content', 'No Content'))
    
    try:
        pdf.output(output_filename)
        logger(f"✅ Successfully created single PDF: '{os.path.basename(output_filename)}'")
        return True
    except Exception as e:
        logger(f"❌ A critical error occurred while saving the final PDF: {e}")
        return False