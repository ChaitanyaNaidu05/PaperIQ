import re
import pdfplumber
import docx

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def clean_text(text):
    """Aggressive cleaning: fix hyphenation, remove page noise, normalize whitespace."""

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
