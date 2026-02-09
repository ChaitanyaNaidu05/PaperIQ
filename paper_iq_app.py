import streamlit as st
import pdfplumber
import re
from collections import Counter

st.set_page_config(
    page_title="PaperIQ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #3B82F6;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E40AF;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stExpander {
        border: 1px solid #DBEAFE;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .upload-section {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .keyword-chip {
        display: inline-block;
        background: #DBEAFE;
        color: #1E40AF;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        margin: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .keywords-container {
        margin-top: 1rem;
        padding: 1rem;
        background: #F0F9FF;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">PaperIQ - Research Paper Analyzer</div>', unsafe_allow_html=True)
st.write("Upload a research paper PDF to dynamically extract sections and keywords.")

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'can', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
    'we', 'our', 'us', 'you', 'your', 'he', 'she', 'his', 'her', 'i', 'me', 'my',
    'who', 'whom', 'which', 'what', 'where', 'when', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now',
    'here', 'there', 'then', 'if', 'else', 'because', 'about', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again',
    'further', 'once', 'any', 'being', 'while', 'using', 'used', 'use', 'based',
    'however', 'thus', 'therefore', 'hence', 'et', 'al', 'fig', 'figure', 'table',
    'section', 'chapter', 'page', 'pp', 'vol', 'issue', 'see', 'shown', 'show',
    'shows', 'given', 'give', 'gives', 'one', 'two', 'three', 'first', 'second'
}


def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return ""
    return text


def preprocess_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def is_valid_section_header(text):
    if not text or len(text) < 5:
        return False
    
    text = text.strip()
    
    if len(text) < 5:
        return False
    
    if re.match(r'^[\d\.\-\s\(\)]+$', text):
        return False
    
    if re.match(r'^[A-Za-z]?\d+(\.\d+)+\s*$', text):
        return False
    
    digit_count = sum(1 for c in text if c.isdigit())
    if digit_count > len(text) * 0.5:
        return False
    
    noise_patterns = [
        r'^page\s*\d+',
        r'^\d+\s*$',
        r'^fig\.?\s*\d+',
        r'^table\s*\d+',
        r'^eq\.?\s*\d+',
        r'^\[\d+\]',
        r'^et\s+al',
        r'^\d{4}$',
        r'^vol\.?\s*\d+',
        r'^issue\s*\d+',
        r'^pp?\.?\s*\d+',
        r'^\d+\s*[-–]\s*\d+$',
    ]
    
    text_lower = text.lower()
    for pattern in noise_patterns:
        if re.match(pattern, text_lower):
            return False
    
    alpha_count = sum(1 for c in text if c.isalpha())
    if alpha_count < 4:
        return False
    
    return True


def detect_section_headers(text):
    headers_found = []
    
    common_sections = [
        'abstract', 'introduction', 'background', 'literature review',
        'methodology', 'methods', 'materials and methods', 'experimental',
        'results', 'findings', 'discussion', 'results and discussion',
        'conclusion', 'conclusions', 'summary', 'future work',
        'references', 'bibliography', 'acknowledgements', 'acknowledgments',
        'appendix', 'appendices', 'supplementary', 'related work',
        'problem statement', 'objectives', 'hypothesis', 'research questions',
        'data analysis', 'data collection', 'limitations', 'implications',
        'theoretical framework', 'conceptual framework', 'research design',
        'sample', 'sampling', 'participants', 'procedure', 'instruments',
        'ethical considerations', 'recommendations', 'contributions'
    ]
    
    text_lines = text.split('\n')
    current_pos = 0
    
    for line in text_lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        if len(line_stripped) < 4:
            current_pos += len(line) + 1
            continue
        
        header_name = None
        
        for section in common_sections:
            if (line_lower == section or 
                line_lower.startswith(section + ':') or
                re.match(rf'^{re.escape(section)}\s*$', line_lower) or
                re.match(rf'^\d+\.?\s+{re.escape(section)}\s*$', line_lower) or
                re.match(rf'^[ivx]+\.?\s+{re.escape(section)}\s*$', line_lower)):
                header_name = section.title()
                break
        
        if not header_name:
            numbered_match = re.match(r'^(\d+\.?|\d+\.\d+\.?|[IVX]+\.?)\s+([A-Z][A-Za-z\s&-]{4,40})$', line_stripped)
            if numbered_match:
                potential_header = numbered_match.group(2).strip()
                if is_valid_section_header(potential_header) and len(potential_header.split()) <= 6:
                    header_name = potential_header
        
        if not header_name:
            if (line_stripped.isupper() and 
                len(line_stripped) >= 6 and 
                len(line_stripped) <= 40 and
                is_valid_section_header(line_stripped)):
                if sum(1 for c in line_stripped if c.isalpha()) >= len(line_stripped) * 0.7:
                    header_name = line_stripped.title()
        
        if header_name and is_valid_section_header(header_name):
            end_pos = current_pos + len(line)
            headers_found.append((current_pos, header_name, end_pos))
        
        current_pos += len(line) + 1
    
    seen_headers = {}
    unique_headers = []
    for pos, header, end_pos in headers_found:
        header_normalized = header.lower().strip()
        if header_normalized not in seen_headers:
            seen_headers[header_normalized] = True
            unique_headers.append((pos, header, end_pos))
    
    unique_headers.sort(key=lambda x: x[0])
    
    return unique_headers


def extract_keywords(text, top_n=10):
    if not text or len(text) < 50:
        return []
    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) >= 3]
    
    if not filtered_words:
        return []
    
    word_counts = Counter(filtered_words)
    
    top_keywords = word_counts.most_common(top_n)
    
    return [word for word, count in top_keywords if count >= 2]


def identify_sections_dynamic(text):
    sections = {}
    
    headers = detect_section_headers(text)
    
    if not headers:
        keywords = extract_keywords(text, top_n=15)
        sections["Full Document"] = {
            "content": text,
            "keywords": keywords
        }
        return sections
    
    for i, (pos, header, end_pos) in enumerate(headers):
        if i + 1 < len(headers):
            next_pos = headers[i + 1][0]
            content = text[end_pos:next_pos].strip()
        else:
            content = text[end_pos:].strip()
        
        header_clean = header.strip()
        
        keywords = extract_keywords(content, top_n=8)
        
        sections[header_clean] = {
            "content": content,
            "keywords": keywords
        }
    
    return sections


col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="section-header">Upload PDF</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Select a research paper",
        type=["pdf"],
        label_visibility="collapsed"
    )

if uploaded_file is not None:
    st.success("PDF Uploaded Successfully!")

    with st.spinner("Extracting text from PDF..."):
        raw_text = extract_text_from_pdf(uploaded_file)
    
    if raw_text:
        cleaned_text = preprocess_text(raw_text)

        st.markdown('<div class="section-header">Extracted Text Preview</div>', unsafe_allow_html=True)
        st.text_area(
            "Raw Extracted Text",
            cleaned_text[:3000],
            height=200,
            label_visibility="collapsed"
        )

        st.markdown('<div class="section-header">Dynamically Identified Sections</div>', unsafe_allow_html=True)
        
        with st.spinner("Analyzing document structure..."):
            sections = identify_sections_dynamic(cleaned_text)

        detected_count = len(sections)
        
        if detected_count > 0:
            st.info(f"Dynamically detected {detected_count} section(s)")
        else:
            st.warning("No sections detected. The document may have non-standard formatting.")

        for section_name, section_data in sections.items():
            content = section_data.get("content", "")
            keywords = section_data.get("keywords", [])
            
            with st.expander(f"{section_name}", expanded=(len(sections) <= 5)):
                if content:
                    st.write("**Content Preview:**")
                    st.write(content[:2000] + ("..." if len(content) > 2000 else ""))
                    
                    if keywords:
                        st.markdown('<div class="keywords-container">', unsafe_allow_html=True)
                        st.write("**Extracted Keywords:**")
                        keywords_html = " ".join([f'<span class="keyword-chip">{kw}</span>' for kw in keywords])
                        st.markdown(keywords_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.caption("No significant keywords extracted from this section.")
                    
                    st.success("Section detected successfully")
                else:
                    st.warning("Section header found but no content detected")
    else:
        st.error("Failed to extract text from the PDF. Please try a different file.")

else:
    st.info("Please upload a research paper PDF to begin analysis")
