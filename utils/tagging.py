import os
import re
from langdetect import detect
from typing import List

try:
    from keybert import KeyBERT
    kw_model = KeyBERT()
    USE_KEYBERT = True
except ImportError:
    kw_model = None
    USE_KEYBERT = False

def detect_language(text: str) -> str:
    """
    Detects the language of a text snippet, defaulting to 'en'.
    """
    if not text:
        return "en"
    try:
        return detect(text)
    except:
        return "en"

def extract_tags(text: str, top_n: int = 5) -> List[str]:
    """
    Extracts relevant topic tags from text using KeyBERT or a frequency-based fallback.
    Optimized for deployment on low-memory servers.
    """
    if not text or len(text.strip()) < 10:
        return []
    
    # Try KeyBERT if available and not memory-restricted
    if USE_KEYBERT and kw_model:
        try:
            keywords = kw_model.extract_keywords(
                text, 
                keyphrase_ngram_range=(1, 2), 
                stop_words='english', 
                top_n=top_n
            )
            return [kw[0].upper() for kw in keywords]
        except:
            pass

    # FALLBACK: Heuristic Frequency-based Tagging
    try:
        # Filter symbols but keep tokens clean
        # IMPORTANT: Replace hyphens and underscores with spaces to break up IDs
        clean_text = text.replace('-', ' ').replace('_', ' ')
        words = ''.join(c if c.isalnum() else ' ' for c in clean_text.lower()).split()
        
        # Comprehensive noise list (media patterns, URL remnants, common stopwords)
        media_noise = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'with', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'as', 'be', 'by', 'if', 'at', 'from', 'each', 'what', 'their', 'when',
            'video', 'channel', 'watch', 'like', 'subscribe', 'probably', 'likely', 'actually', 'maybe',
            'signs', 'damage', 'using', 'going', 'doing', 'things', 'about', 'just', 'more', 'even',
            'title', 'youtube', 'transcript', 'published', 'posted', 'written', 'medical', 'reviewed',
            'source', 'available', 'visit', 'check', 'link', 'below', 'titled', 'unavailable',
            'http', 'https', 'www', 'com', 'youtu', 'be', 'html', 'polymer', 'initialdata', 'ytinitial'
        }
        
        # Enhanced filter to ignore tokens that match typical YouTube video IDs (11 chars Alphanumeric mix)
        # And filter out generic URL remnants
        filtered = [
            w for w in words 
            if w not in media_noise 
            and len(w) > 3 
            and not (len(w) >= 10 and len(w) <= 12 and any(c.isdigit() for c in w) and any(c.isalpha() for c in w))
            and not any(x in w for x in ['.com', 'http', 'www', 'https'])
        ]
        
        counts = {}
        for word in filtered:
            counts[word] = counts.get(word, 0) + 1
            
        # Return top N keywords by frequency
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [word.upper() for word, count in sorted_counts[:top_n]]
    except:
        return []
