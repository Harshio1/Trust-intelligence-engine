import requests
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any

from utils.chunking import chunk_text
from utils.tagging import extract_tags, detect_language
from scoring.trust_score import calculate_trust_score

def scrape_pubmed(url_or_id: str) -> Dict[str, Any]:
    """
    Scrapes PubMed article abstract and metadata using Entrez E-utilities.
    """
    print(f"Scraping PubMed: {url_or_id}")
    
    # Extract ID
    pmid_match = re.search(r'(\d{8,})', url_or_id)
    if not pmid_match:
        raise ValueError(f"Could not extract PMID from {url_or_id}")
    
    pmid = pmid_match.group(1)
    
    # Fetch data using Entrez eFetch
    api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    article = root.find('.//Article')
    if article is None:
        raise ValueError("Article not found in PubMed response")
        
    title = article.findtext('.//ArticleTitle', default="Unknown Title")
    
    # Extract Author(s)
    author_list = []
    for author_node in article.findall('.//Author'):
        last_name = author_node.findtext('LastName', default='')
        initials = author_node.findtext('Initials', default='')
        if last_name:
            author_list.append(f"{last_name} {initials}".strip())
    
    author_str = ", ".join(author_list) if author_list else "Unknown"
    
    # Extract Publication Year
    pub_date = article.find('.//Journal/JournalIssue/PubDate')
    pub_year = pub_date.findtext('Year', default="Unknown") if pub_date is not None else "Unknown"
    
    # Extract Abstract
    abstract_nodes = article.findall('.//AbstractText')
    abstract_text = "\n\n".join([n.text for n in abstract_nodes if n.text])
    
    full_text = f"{title}\n\n{abstract_text}"
    
    lang = detect_language(full_text[:1000])
    chunks = chunk_text(full_text)
    tags = extract_tags(full_text, top_n=5)
    
    final_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    
    trust_data = calculate_trust_score(
        text=full_text,
        author=author_list, # Passing list for averaging logic
        source_url=final_url,
        publish_date=pub_year,
        source_type='pubmed'
    )
    
    return {
        "source_url": final_url,
        "source_type": "pubmed",
        "author": author_str,
        "published_date": pub_year,
        "language": lang,
        "region": "global",
        "topic_tags": tags,
        "trust_score": trust_data["score"],
        "trust_breakdown": trust_data["trust_breakdown"],
        "trust_explanation": trust_data["trust_explanation"],
        "strengths": trust_data.get("strengths", []),
        "weaknesses": trust_data.get("weaknesses", []),
        "confidence_score": trust_data.get("confidence_score", 0.0),
        "abuse_flags": trust_data.get("abuse_flags", []),
        "abuse_penalty": trust_data.get("abuse_penalty", 0.0),
        "content_chunks": chunks
    }
