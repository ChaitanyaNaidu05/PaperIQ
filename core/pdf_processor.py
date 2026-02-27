import re
import pdfplumber
import docx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text(x_tolerance=3, y_tolerance=3)
                if extracted:
                    text += extracted + "\n"
        
        if not text.strip():
            return "[Error: This PDF appears to be image-only. PaperIQ currently requires text-based PDFs for analysis.]"
            
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return f"[Error: Failed to extract text from PDF. {str(e)}]"


def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
        return f"[Error: Failed to extract text from DOCX. {str(e)}]"


def clean_text(text):
    if text.startswith("[Error:"):
        return text
        
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)
    
    lines = text.split('\n')
    line_counts = {}
    for line in lines:
        stripped = line.strip()
        if 0 < len(stripped) < 30:
            line_counts[stripped] = line_counts.get(stripped, 0) + 1
            
    noise_lines = {line for line, count in line_counts.items() if count >= 3}
    cleaned_lines = [line for line in lines if line.strip() not in noise_lines]
    
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()
