import re
from collections import Counter

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
            # Use safe slicing
            try:
                content = text[end_pos:next_pos].strip()
            except IndexError:
                content = ""
        else:
            try:
                content = text[end_pos:].strip()
            except IndexError:
                content = ""
        
        header_clean = header.strip()
        
        keywords = extract_keywords(content, top_n=8)
        
        sections[header_clean] = {
            "content": content,
            "keywords": keywords
        }
    
    return sections
