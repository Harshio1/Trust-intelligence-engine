import traceback
from typing import List
from langdetect import detect, DetectorFactory

# Step 1: Wrap KeyBERT initialization for low-memory environments (Render Free Tier)
try:
    from keybert import KeyBERT
    kw_model = KeyBERT(model="all-MiniLM-L6-v2")
    USE_KEYBERT = True
except Exception as e:
    print(f"KeyBERT unavailable (Memory/CPU limit), using fallback heuristic: {e}")
    kw_model = None
    USE_KEYBERT = False

# Consistent language detection
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Detect the ISO 639-1 language code."""
    if not text or len(text.strip()) < 5:
        return 'unknown'
    try:
        return detect(text)
    except Exception:
        return 'unknown'

def extract_tags(text: str, top_n: int = 5) -> List[str]:
    """
    Extracts tags using KeyBERT or a frequency-based fallback.
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
            return [kw[0] for kw in keywords]
        except Exception as e:
            print(f"KeyBERT runtime failure: {e}. Defaulting to frequency heuristic.")

    # FALLBACK: Heuristic Frequency-based Tagging
    try:
        # Filter symbols but keep tokens clean
        words = ''.join(c if c.isalnum() else ' ' for c in text.lower()).split()
        
        # Comprehensive noise list (media patterns, URL remnants, common stopwords)
        media_noise = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'with', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'as', 'be', 'by', 'if', 'at', 'from', 'each', 'what', 'which', 'their', 'when',
            'video', 'channel', 'watch', 'like', 'subscribe', 'probably', 'likely', 'actually', 'maybe',
            'signs', 'damage', 'using', 'going', 'doing', 'things', 'about', 'just', 'more', 'even',
            'title', 'youtube', 'transcript', 'published', 'posted', 'written', 'medical', 'reviewed',
            'source', 'available', 'visit', 'check', 'link', 'below', 'titled', 'unavailable'
        }
        
        filtered = [
            w for w in words 
            if w not in media_noise 
            and len(w) > 3 
            and not any(x in w for x in ['http', 'www', '.com', 'https'])
        ]
        
        from collections import Counter
        return [item[0].upper() for item in Counter(filtered).most_common(top_n)]
    except Exception:
        return []
