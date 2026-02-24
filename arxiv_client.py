import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"


@dataclass
class ArxivPaper:
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published: str
    updated: str
    doi: str
    pdf_url: str
    arxiv_url: str


def search_arxiv(
    query: str,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending"
) -> List[ArxivPaper]:
    papers = []
    
    try:
        search_query = urllib.parse.quote(query)
        url = (
            f"{ARXIV_API_URL}?search_query={search_query}"
            f"&start=0&max_results={max_results}"
            f"&sortBy={sort_by}&sortOrder={sort_order}"
        )
        
        logger.info(f"Searching arXiv: {url}")
        
        with urllib.request.urlopen(url, timeout=30) as response:
            xml_data = response.read().decode("utf-8")
        
        root = ET.fromstring(xml_data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom"
        }
        
        for entry in root.findall("atom:entry", ns):
            paper = parse_arxiv_entry(entry, ns)
            if paper:
                papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers from arXiv")
        
    except Exception as e:
        logger.error(f"Error searching arXiv: {e}")
    
    return papers


def parse_arxiv_entry(entry: ET.Element, ns: Dict) -> Optional[ArxivPaper]:
    try:
        paper_id = entry.find("atom:id", ns)
        paper_id_text = paper_id.text if paper_id is not None else ""
        
        title = entry.find("atom:title", ns)
        title_text = title.text.strip() if title is not None and title.text else "No title"
        
        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text.strip())
        
        abstract = entry.find("atom:summary", ns)
        abstract_text = abstract.text.strip() if abstract is not None and abstract.text else ""
        
        categories = []
        for category in entry.findall("atom:category", ns):
            term = category.get("term")
            if term:
                categories.append(term)
        
        published = entry.find("atom:published", ns)
        published_text = published.text if published is not None else ""
        
        updated = entry.find("atom:updated", ns)
        updated_text = updated.text if updated is not None else ""
        
        doi_elem = entry.find("arxiv:doi", ns)
        doi_text = doi_elem.text if doi_elem is not None else ""
        
        pdf_url = ""
        arxiv_url = paper_id_text
        
        for link in entry.findall("atom:link", ns):
            link_type = link.get("type")
            link_title = link.get("title")
            href = link.get("href")
            if link_type == "application/pdf":
                pdf_url = href
            elif href and "arxiv.org/abs" in href:
                arxiv_url = href
        
        return ArxivPaper(
            paper_id=paper_id_text.split("/")[-1] if paper_id_text else "",
            title=title_text,
            authors=authors,
            abstract=abstract_text,
            categories=categories,
            published=published_text,
            updated=updated_text,
            doi=doi_text,
            pdf_url=pdf_url,
            arxiv_url=arxiv_url
        )
        
    except Exception as e:
        logger.error(f"Error parsing arXiv entry: {e}")
        return None


def get_paper_by_id(arxiv_id: str) -> Optional[ArxivPaper]:
    results = search_arxiv(query=f"id:{arxiv_id}", max_results=1)
    return results[0] if results else None


def search_by_author(author_name: str, max_results: int = 10) -> List[ArxivPaper]:
    return search_arxiv(
        query=f"au:{author_name}",
        max_results=max_results,
        sort_by="submittedDate",
        sort_order="descending"
    )


def search_by_category(category: str, max_results: int = 10) -> List[ArxivPaper]:
    return search_arxiv(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by="submittedDate",
        sort_order="descending"
    )


def get_recent_papers(
    category: str = "cs.AI",
    days: int = 7,
    max_results: int = 20
) -> List[ArxivPaper]:
    return search_by_category(category, max_results)


def fetch_paper_metadata(arxiv_id: str) -> Dict:
    paper = get_paper_by_id(arxiv_id)
    if not paper:
        return {"error": "Paper not found"}
    
    return {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "categories": paper.categories,
        "published": paper.published,
        "doi": paper.doi,
        "pdf_url": paper.pdf_url,
        "arxiv_url": paper.arxiv_url
    }


def download_paper_pdf(pdf_url: str, save_path: str) -> bool:
    try:
        urllib.request.urlretrieve(pdf_url, save_path)
        logger.info(f"Downloaded PDF to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        return False


def format_paper_for_display(paper: ArxivPaper) -> str:
    authors_str = ", ".join(paper.authors[:3])
    if len(paper.authors) > 3:
        authors_str += " et al."
    
    published_date = paper.published[:10] if paper.published else "Unknown"
    
    return f"""
**{paper.title}**

*Authors:* {authors_str}

*Published:* {published_date}

*Categories:* {', '.join(paper.categories[:3])}

*Abstract:* {paper.abstract[:300]}...

[View on arXiv]({paper.arxiv_url}) | [PDF]({paper.pdf_url})
"""
