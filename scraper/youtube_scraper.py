import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
from typing import Dict, Any

from utils.chunking import chunk_text
from utils.tagging import extract_tags, detect_language
from scoring.trust_score import calculate_trust_score

def get_video_metadata(video_id: str) -> Dict[str, str]:
    """
    Robust fallback page scrape for YouTube video info.
    Uses multiple patterns to find channel, date, and description.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    metadata = {
        "title": "Unknown",
        "channel": "Channel not available",
        "publishDate": "Unknown",
        "description": ""
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        html = res.text
        
        # 1. Extract Title
        title_match = re.search(r'<title>(.*?)</title>', html)
        if title_match:
            metadata["title"] = title_match.group(1).replace(" - YouTube", "").strip()

        # 2. Extract Channel / Author
        author_patterns = [
            r'"author":"(.*?)"', 
            r'"ownerName":"(.*?)"',
            r'"ownerChannelName":"(.*?)"',
            r'<link itemprop="name" content="(.*?)">'
        ]
        for pattern in author_patterns:
            match = re.search(pattern, html)
            if match and match.group(1):
                metadata["channel"] = match.group(1).strip()
                break
        
        # 3. Extract Publish Date
        date_patterns = [
            r'"publishDate":"(.*?)"',
            r'"uploadDate":"(.*?)"',
            r'<meta itemprop="datePublished" content="(.*?)">',
            r'<meta itemprop="uploadDate" content="(.*?)">'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, html)
            if match and match.group(1):
                metadata["publishDate"] = match.group(1).strip()
                break
                
        # 4. Extract Description
        desc_patterns = [
            r'"shortDescription":"(.*?)"',
            r'<meta name="description" content="(.*?)">'
        ]
        for pattern in desc_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match and match.group(1):
                clean_desc = match.group(1).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                metadata["description"] = clean_desc.strip()
                break
    except Exception as e:
        print(f"Error in get_video_metadata for {video_id}: {e}")
        
    return metadata

def scrape_youtube(url: str) -> Dict[str, Any]:
    """
    Scrapes YouTube video metadata and transcript.
    """
    print(f"Scraping YouTube: {url}")
    
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if not match:
        raise ValueError(f"Could not extract video ID from {url}")
    
    video_id = match.group(1)
    metadata = get_video_metadata(video_id)
    
    transcript_text = ""
    try:
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([t['text'] for t in transcript_list])
        elif hasattr(YouTubeTranscriptApi, 'fetch'):
            try:
                transcript_obj = YouTubeTranscriptApi().fetch(video_id=video_id)
                if hasattr(transcript_obj, 'snippets'):
                    transcript_text = " ".join([s.text for s in transcript_obj.snippets])
                else:
                    transcript_text = str(transcript_obj)
            except Exception as e:
                print(f"Instance fetch failed for {video_id}: {e}")
    except Exception as e:
        print(f"Could not get transcript for {video_id}: {e}")
        
    full_text = metadata.get('description', '')
    if transcript_text:
        full_text += "\n\n[Transcript]\n" + transcript_text
        
    try:
        lang = detect_language(full_text[:1000]) if full_text.strip() else "en"
    except Exception:
        lang = "en"
        
    chunks = chunk_text(full_text)
    tags = extract_tags(full_text, top_n=5)
    
    trust_data = calculate_trust_score(
        text=full_text,
        author=metadata['channel'],
        source_url=url,
        publish_date=metadata['publishDate'],
        source_type='youtube'
    )
    
    return {
        "source_url": url,
        "source_type": "youtube",
        "author": metadata['channel'],
        "published_date": metadata['publishDate'],
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
