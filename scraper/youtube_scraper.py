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
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Common headers with a consent cookie to bypass redirects
    base_headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    # Consent cookie often bypasses the "Before you continue" wall
    cookies = {'CONSENT': 'YES+cb.20210328-17-p0.en+FX+435'}

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    ]
    
    metadata = {
        "title": "Unknown",
        "channel": "Channel not available",
        "publishDate": "Unknown",
        "description": ""
    }
    
    for ua in user_agents:
        try:
            headers = {**base_headers, 'User-Agent': ua}
            res = requests.get(url, headers=headers, cookies=cookies, timeout=15)
            html = res.text
            
            # 1. Primary Method: ytInitialPlayerResponse (Added re.DOTALL for safety)
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
                except Exception:
                    pass

            # 2. Secondary Method: ytInitialData (Deep Search)
            data_match = re.search(r'ytInitialData\s*=\s*({.*?});', html, re.DOTALL)
            if data_match:
                try:
                    initial_data = json.loads(data_match.group(1))
                    # Try to find channel in the renderer chain
                    try:
                        # Attempt to get title if playerResponse failed
                        metadata["title"] = initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['title']['runs'][0]['text']
                    except (KeyError, IndexError):
                        pass

                    try:
                        # Common path in ytInitialData for channel name
                        runs = initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs']
                        metadata["channel"] = runs[0]['text']
                    except (KeyError, IndexError):
                        pass
                        
                    if metadata["channel"] != "Channel not available":
                        return metadata
                except Exception:
                    pass

            # 3. Fallback: Microdata / Meta Tags
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if title_match:
                metadata["title"] = title_match.group(1).split(" - YouTube")[0].strip()

            author_patterns = [r'"author" content="(.*?)"', r'"author":"(.*?)"', r'"ownerName":"(.*?)"', r'<link itemprop="name" content="(.*?)">']
            for pattern in author_patterns:
                match = re.search(pattern, html)
                if match and match.group(1):
                    metadata["channel"] = match.group(1).strip()
                    break
            
            if metadata["channel"] != "Channel not available":
                return metadata
                
        except Exception as e:
            print(f"Scrape attempt with UA {ua[:20]}... failed: {e}")
            
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
        # Multi-tiered transcript fetch
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try prioritized fetch
        try:
            # 1. Try manual English
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except Exception:
            try:
                # 2. Try any manual
                transcript = transcript_list.find_manually_created_transcript([])
            except Exception:
                try:
                    # 3. Try auto-generated English
                    transcript = transcript_list.find_generated_transcript(['en'])
                except Exception:
                    # 4. Try any auto-generated
                    transcript = transcript_list.find_generated_transcript([])

        transcript_data = transcript.fetch()
        transcript_text = " ".join([t['text'] for t in transcript_data])
    except Exception as e:
        print(f"Transcript discovery failed for {video_id}: {e}")
        
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
