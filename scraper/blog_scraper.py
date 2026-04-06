import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

from utils.chunking import chunk_text
from utils.tagging import extract_tags, detect_language
from scoring.trust_score import calculate_trust_score

def scrape_blog(url: str) -> Dict[str, Any]:
    """
    Scrapes a gut health blog post, extracts metadata and content,
    and returns a structured dictionary matching the required JSON format.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Scraping blog: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract Metadata from JSON-LD (Highest Reliability)
    json_ld_data = {}
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            import json as json_lib
            raw_data = json_lib.loads(script.string)
            # Support @graph or lists
            items = raw_data.get('@graph') if isinstance(raw_data, dict) and '@graph' in raw_data else (raw_data if isinstance(raw_data, list) else [raw_data])
            
            for item in items:
                if item.get('@type') in ['Article', 'BlogPosting', 'NewsArticle', 'WebPage']:
                    json_ld_data = item
                    break
            if json_ld_data: break
        except: continue

    # Extract Title
    title = soup.title.string if soup.title else ""
    if not title:
        title = json_ld_data.get('headline') or (soup.find('h1').get_text(strip=True) if soup.find('h1') else "Unknown")
        
    # Extract Author
    author = "Unknown"
    # 1. Try JSON-LD
    author_obj = json_ld_data.get('author')
    if isinstance(author_obj, list): author_obj = author_obj[0]
    if isinstance(author_obj, dict): author = author_obj.get('name', "Unknown")
    elif isinstance(author_obj, str): author = author_obj

    # 2. Try common meta tags
    if author == "Unknown":
        author_selectors = [
            {'name': 'author'}, {'property': 'article:author'}, {'name': 'citation_author'},
            {'property': 'og:article:author'}, {'name': 'sailthru.author'}
        ]
        for selector in author_selectors:
            meta = soup.find('meta', attrs=selector)
            if meta and meta.get('content'):
                author = meta.get('content')
                break
    
    # 3. Try visible byline
    if author == "Unknown":
        author_tag = (soup.find(class_=lambda c: c and any(x in c.lower() for x in ['author', 'byline', 'writer'])) or 
                     soup.find('a', rel='author'))
        if author_tag:
            author = author_tag.get_text(separator=' ', strip=True)
            for prefix in ['by ', 'written by ', 'medical review by ', 'reviewed by ']:
                if author.lower().startswith(prefix):
                    author = author[len(prefix):]
                    break

    # Extract Publish Date
    publish_date = "Unknown"
    # 1. Try JSON-LD
    publish_date = json_ld_data.get('datePublished') or json_ld_data.get('dateModified') or "Unknown"

    # 2. Try meta tags
    if publish_date == "Unknown":
        date_selectors = [
            {'property': 'article:published_time'}, {'name': 'date'}, {'name': 'citation_date'},
            {'property': 'og:article:published_time'}, {'name': 'sailthru.date'}
        ]
        for selector in date_selectors:
            meta = soup.find('meta', attrs=selector)
            if meta and meta.get('content'):
                publish_date = meta.get('content')
                break
            
    # 3. Try time tag
    if publish_date == "Unknown":
        time_tag = soup.find('time')
        if time_tag:
            publish_date = time_tag.get('datetime') or time_tag.get_text(strip=True)

    # Remove non-content elements early
    for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "button", "iframe"]):
        element.decompose()
        
    # Find main article content using specific selectors for high-quality blogs (like The Conversation)
    content_selectors = [
        {'class': 'article-body'}, 
        {'class': 'content-body'}, 
        {'itemprop': 'articleBody'},
        {'class': 'post-content'},
        {'class': 'entry-content'}
    ]
    
    article_body = None
    for selector in content_selectors:
        article_body = soup.find(None, attrs=selector)
        if article_body:
            break
            
    if not article_body:
        article_body = soup.find('article') or soup.find('main') or soup.find('div', id='main-content') or soup.body

    if not article_body:
        full_text = ""
    else:
        # Avoid pulling in 'Related Articles' or 'Read More' sections often found at the end of the body
        # Many sites put these in 'aside' or specific divs - we already decomposed 'aside'
        paragraphs = article_body.find_all(['p', 'h2', 'h3'])
        
        # Filter out very short strings or strings matching common UI patterns
        cleaned_paragraphs = []
        for p in paragraphs:
            text = p.get_text(separator=' ', strip=True)
            if len(text) > 40 and not any(x in text.lower() for x in ['read more', 'related articles', 'subscribe to', 'follow us']):
                cleaned_paragraphs.append(text)
        
        full_text = "\n\n".join(cleaned_paragraphs)

    lang = detect_language(full_text[:1000])
    chunks = chunk_text(full_text)
    tags = extract_tags(full_text, top_n=5)
    
    # Compute Trust Score during scraping
    trust_data = calculate_trust_score(
        text=full_text,
        author=author,
        source_url=url,
        publish_date=publish_date,
        source_type='blog'
    )
    
    return {
        "source_url": url,
        "source_type": "blog",
        "author": author[:100] if author else "Unknown",
        "published_date": publish_date,
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
