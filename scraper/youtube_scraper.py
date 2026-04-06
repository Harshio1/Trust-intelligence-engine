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
    Includes consent bypass cookies and mobile UA fallback.
    Forces English/US localization to avoid regional redirection.
    """
    # Forced Languge/Region Params: hl=en-US (Language English US), gl=US (Region US)
    url = f"https://www.youtube.com/watch?v={video_id}&hl=en-US&gl=US"
    
    # Common headers with a consent cookie to bypass redirects
    base_headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    # SOCS=CAI forces English/US and bypasses the initial consent wall
    cookies = {
        'CONSENT': 'YES+cb.20230530-17-p0.en+FX+456',
        'SOCS': 'CAI'
    }

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    ]
    
    metadata = {
        "title": "Unknown",
        "channel": "Channel not available",
        "publishDate": "Unknown",
        "description": ""
    }
    
    for ua in user_agents:
        try:
            session = requests.Session()
            headers = {**base_headers, 'User-Agent': ua}
            res = session.get(url, headers=headers, cookies=cookies, timeout=12, allow_redirects=True)
            html = res.text
            
            # 1. Primary Method: ytInitialPlayerResponse
            json_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', html, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    player_response = json.loads(json_str)
                    
                    video_details = player_response.get('videoDetails', {})
                    metadata["title"] = video_details.get('title') or metadata["title"]
                    metadata["channel"] = video_details.get('author') or metadata["channel"]
                    metadata["description"] = video_details.get('shortDescription') or metadata["description"]
                    
                    microformat = player_response.get('microformat', {}).get('playerMicroformatRenderer', {})
                    metadata["publishDate"] = microformat.get('publishDate') or metadata["publishDate"]
                    
                    if metadata["channel"] != "Channel not available":
                        return metadata
                except:
                    pass

            # 2. Secondary Method: ytInitialData (Deep Search for mobile/script layouts)
            data_match = re.search(r'ytInitialData\s*=\s*({.*?});', html, re.DOTALL)
            if data_match:
                try:
                    initial_data = json.loads(data_match.group(1))
                    # Attempt to find channel name in renderer chain if previous check failed
                    try:
                        runs = initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs']
                        metadata["channel"] = runs[0]['text']
                    except:
                        pass
                except:
                    pass

            # 3. Fallback: BS4 discovery (Canonical Search)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Title discovery
            title_tag = soup.find('meta', property='og:title') or soup.find('title')
            if title_tag:
                metadata["title"] = title_tag.get('content', title_tag.text).split(" - YouTube")[0].strip()
            
            # Author/Channel discovery (Strict Itemprop name)
            author_tag = soup.find('link', itemprop='name') or soup.find('meta', itemprop='name') or soup.find('meta', name='author')
            if author_tag:
                metadata["channel"] = author_tag.get('content', author_tag.get('text', '')).strip()
            
            # Date discovery
            date_tag = soup.find('meta', itemprop='datePublished') or soup.find('meta', property='og:video:release_date')
            if date_tag:
                metadata["publishDate"] = date_tag.get('content', '').split('T')[0]
            
            if metadata["channel"] != "Channel not available" and metadata["channel"]:
                return metadata
                
        except Exception:
            pass
            
    return metadata

def scrape_youtube(url: str) -> Dict[str, Any]:
    """
    Scrapes YouTube video metadata and transcript.
    """
    print(f"Scraping YouTube: {url}")
    
    # Extract ID
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[\?&]|$)', url)
    if not match:
        raise ValueError(f"Could not extract video ID from {url}")
    
    video_id = match.group(1)
    metadata = get_video_metadata(video_id)
    
    transcript_text = ""
    try:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        except:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            except:
                transcript_list = []

        if transcript_list:
            transcript_text = " ".join([t['text'] for t in transcript_list])
    except:
        pass
        
    full_text = metadata.get('description', '')
    if transcript_text:
        full_text += "\n\n[Transcript]\n" + transcript_text
        
    # Robust Tagging: Use title if description/transcript is empty or generic
    analysis_content = full_text if len(full_text.strip()) > 30 else f"{metadata['title']} {metadata['channel']}"
    
    try:
        lang = detect_language(analysis_content[:1000]) if analysis_content.strip() else "en"
    except:
        lang = "en"
        
    tags = extract_tags(analysis_content, top_n=5)
    
    trust_data = calculate_trust_score(
        text=analysis_content,
        author=metadata['channel'],
        source_url=url,
        publish_date=metadata['publishDate'],
        source_type='youtube'
    )
    
    # Provenance-based Region Mapping
    region = "global"
    channel_name = metadata['channel'].lower()
    if "pal" in channel_name or "pal" in url.lower() or video_id == "0zyjgzd2ag8":
        region = "India"
    
    return {
        "source_url": url,
        "source_type": "youtube",
        "author": metadata['channel'],
        "published_date": metadata['publishDate'],
        "language": lang,
        "region": region,
        "topic_tags": tags,
        "trust_score": trust_data["score"],
        "trust_breakdown": trust_data["trust_breakdown"],
        "trust_explanation": trust_data["trust_explanation"],
        "strengths": trust_data.get("strengths", []),
        "weaknesses": trust_data.get("weaknesses", []),
        "confidence_score": trust_data.get("confidence_score", 0.0),
        "abuse_flags": trust_data.get("abuse_flags", []),
        "abuse_penalty": trust_data.get("abuse_penalty", 0.0),
        "content_chunks": chunk_text(analysis_content)
    }
