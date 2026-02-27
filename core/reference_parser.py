import re
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_references(text: str) -> List[Dict[str, Any]]:
    ref_section = ""
    ref_patterns = [
        r"(?i)\n(?:References|Bibliography|Works Cited)\n(.*?)$",
        r"(?i)\n\d+\s+(?:References|Bibliography|Works Cited)\n(.*?)$"
    ]
    
    for pattern in ref_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            ref_section = match.group(1)
            break
            
    if not ref_section:
        lines = text.split('\n')
        for i, line in enumerate(reversed(lines)):
            if re.match(r"(?i)^(?:References|Bibliography|Works Cited)$", line.strip()):
                ref_section = "\n".join(lines[len(lines)-i:])
                break
                
    if not ref_section:
        return []
        
    entries = re.split(r'\n(?=\[?\d+\]?\s|[A-Z][a-z]+,?\s\w\.)', ref_section)
    parsed_refs = []
    
    for entry in entries:
        entry = entry.replace('\n', ' ').strip()
        if len(entry) < 10:
            continue
            
        ref_obj = {
            "raw": entry,
            "authors": "",
            "year": "",
            "title": "",
            "venue": ""
        }
        
        year_match = re.search(r'\((\d{4})\)|\s(\d{4})\.', entry)
        if year_match:
            ref_obj["year"] = year_match.group(1) or year_match.group(2)
            
        author_match = re.match(r'^(.*?)(?:\(|\d{4})', entry)
        if author_match:
            ref_obj["authors"] = author_match.group(1).strip().rstrip(',')
            
        title_patterns = [
            r'“([^”]+)”',
            r'"([^"]+)"',
            r'\.\s+([A-Z][^.]+?)\.\s+',
            r'\]\s+(.*?)\.\s+[A-I]'
        ]
        
        for p in title_patterns:
            tm = re.search(p, entry)
            if tm:
                ref_obj["title"] = tm.group(1).strip()
                break
                
        parsed_refs.append(ref_obj)
        
    return parsed_refs

def extract_citations_from_text(text: str) -> List[str]:
    patterns = [
        r'\[\d+(?:,\s*\d+)*\]',
        r'\([A-Z][a-z]+,\s*\d{4}\)',
        r'[A-Z][a-z]+\s+et\s+al\.\s+\(\d{4}\)'
    ]
    all_citations = []
    for p in patterns:
        all_citations.extend(re.findall(p, text))
    return list(set(all_citations))
