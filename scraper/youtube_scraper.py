import json
import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, Any

from utils.chunking import chunk_text
from utils.tagging import extract_tags, detect_language
from scoring.trust_score import calculate_trust_score

def get_video_metadata(video_id: str) -> Dict[str, str]:
    """
    Robust metadata extraction using YouTube's internal JSON state.
    Targets ytInitialPlayerResponse and ytInitialData for structured details.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'no-cache'
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
        
        # 1. Primary Method: Extract ytInitialPlayerResponse JSON
        json_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', html)
        if json_match:
            try:
                player_response = json.loads(json_match.group(1))
                video_details = player_response.get('videoDetails', {})
                metadata["title"] = video_details.get('title', metadata["title"])
                metadata["channel"] = video_details.get('author', metadata["channel"])
                metadata["description"] = video_details.get('shortDescription', metadata["description"])
                
                # Extract date from microformat
                microformat = player_response.get('microformat', {}).get('playerMicroformatRenderer', {})
                metadata["publishDate"] = microformat.get('publishDate', metadata["publishDate"])
                
                if metadata["channel"] != "Channel not available":
                    return metadata # Success
            except (json.JSONDecodeError, KeyError):
                pass

        # 2. Secondary Method: Extract ytInitialData
        data_match = re.search(r'ytInitialData\s*=\s*({.*?});', html)
        if data_match:
            try:
                initial_data = json.loads(data_match.group(1))
                # Deep traverse for metadata if playerResponse failed
                pass 
            except json.JSONDecodeError:
                pass

        # 3. Last Resort: Standard Meta Tags (Legacy Fallback)
        title_match = re.search(r'<title>(.*?)</title>', html)
        if title_match:
            metadata["title"] = title_match.group(1).replace(" - YouTube", "").strip()

        author_patterns = [r'"author":"(.*?)"', r'"ownerName":"(.*?)"', r'<link itemprop="name" content="(.*?)">']
        for pattern in author_patterns:
            match = re.search(pattern, html)
            if match and match.group(1):
                metadata["channel"] = match.group(1).strip()
                break
        
        date_patterns = [r'"publishDate":"(.*?)"', r'<meta itemprop="datePublished" content="(.*?)">']
        for pattern in date_patterns:
            match = re.search(pattern, html)
            if match and match.group(1):
                metadata["publishDate"] = match.group(1).strip()
                break
                
    except Exception as e:
        print(f"Error in get_video_metadata for {video_id}: {e}")
        
    return metadata

def scrape_youtube(url: str) -> Dict[str, Any]:
    """
    Scrapes YouTube video metadata and transcript.
    """
    print(f"Scraping YouTube: {url}")
    
    # Improved regex for youtu.be and watch?v= patterns
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[\?&]|$)', url)
    if not match:
        raise ValueError(f"Could not extract video ID from {url}")
    
    video_id = match.group(1)
    metadata = get_video_metadata(video_id)
    
    transcript_text = ""
    try:
        # Standard transcript fetch
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript_list])
    except Exception as e:
        print(f"Could not get transcript for {video_id}: {e}")
        
    full_text = metadata.get('description', '')
    
    # Scraping Guard: Detect generic YouTube boilerplate
    boilerplate_marker = "ENJOY THE VIDEOS AND MUSIC YOU LOVE"
    if boilerplate_marker in full_text.upper():
        print(f"Warning: Generic boilerplate detected for {video_id}. Clearing corrupted description.")
        full_text = ""

    if transcript_text:
        full_text += "\n\n[Transcript]\n" + transcript_text
        
    # Final check: If still empty or just boilerplate, use title as text
    if not full_text.strip() or boilerplate_marker in full_text.upper():
        full_text = f"Title: {metadata['title']}\nChannel: {metadata['channel']}"

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
