import os
import sys
import json
import tempfile
import PyPDF2
from pdf2image import convert_from_path

# --- Imports setup to handle project structure ---
# Adding project root to sys.path to import constants correctly
project_root = r'D:\Projects\OmniTask_AI'
if project_root not in sys.path:
    sys.path.append(project_root)

# Import MAX_LENGTH from constants
try:
    from constants import MAX_LENGTH
except ImportError:
    print("Warning: Could not import MAX_LENGTH from constants. Using default.")
    MAX_LENGTH = 5000  # Fallback default

# Import OCR function from the sibling file ocr_agent.py
try:
    # Try absolute import first based on project structure
    from components.Agents.ocr_agent import extract_text_from_image
except ImportError:
    try:
        # Try relative import if running from within the folder
        from ocr_agent import extract_text_from_image
    except ImportError:
        raise ImportError("Could not find ocr_agent.py. Ensure it is in the same directory.")

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF. Handles both text-based and scanned PDFs.
    """
    full_text = ""
    
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            # Iterate through all pages
            for i in range(total_pages):
                page = pdf_reader.pages[i]
                text = page.extract_text()
                
                # Check if page is effectively empty (scanned) or has text
                # We use a threshold of 10 chars to decide if it's "scanned"
                if not text or len(text.strip()) < 10:
                    print(f"Page {i+1} appears to be scanned. Attempting OCR...")
                    
                    # Convert specific page to image using pdf2image
                    # poppler_path needs to be in PATH or specified here if on Windows
                    # Example: poppler_path = r'C:\Program Files\poppler-xx\bin'
                    images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
                    
                    if images:
                        # Save temp image for ocr_agent to read (since it expects a path)
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                            images[0].save(tmp_img.name, 'PNG')
                            tmp_img_path = tmp_img.name
                        
                        # Use the provided OCR agent
                        ocr_text = extract_text_from_image(tmp_img_path)
                        full_text += ocr_text + "\n"
                        
                        # Clean up temp file
                        os.remove(tmp_img_path)
                else:
                    full_text += text + "\n"
                    
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

    return full_text

def process_pdf(pdf_path):
    """
    Main entry point to process the PDF and return JSON data.
    """
    pdf_name = os.path.basename(pdf_path)
    extracted_text = extract_text_from_pdf(pdf_path)
    
    is_truncated = False
    
    # Check against MAX_LENGTH
    if len(extracted_text) > MAX_LENGTH:
        extracted_text = extracted_text[:MAX_LENGTH]
        is_truncated = True
    
    # Construct response dictionary
    response_data = {
        "pdf_name": pdf_name,
        "text": extracted_text,
        "istruncated": is_truncated
    }
    
    # Convert to JSON string (or keep as dict depending on requirement)
    # Returning dict here for Python usage; user can json.dumps() if creating a file
    return response_data

