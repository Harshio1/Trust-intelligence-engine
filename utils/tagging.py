import traceback
from typing import List
from langdetect import detect, DetectorFactory
from keybert import KeyBERT

# To ensure consistent language detection
DetectorFactory.seed = 0

# Initialize KeyBERT lazily to avoid heavy loading if not needed immediately
_kw_model = None

def get_kw_model() -> KeyBERT:
    global _kw_model
    if _kw_model is None:
        # all-MiniLM-L6-v2 is fast and effective for keyword extraction
        _kw_model = KeyBERT('all-MiniLM-L6-v2')
    return _kw_model

def detect_language(text: str) -> str:
    """
    Detect the language of the provided text.
    Returns ISO 639-1 code (e.g., 'en', 'es') or 'unknown' on failure.
    """
    if not text or len(text.strip()) < 5:
        return 'unknown'
    try:
        return detect(text)
    except Exception:
        return 'unknown'

def extract_tags(text: str, top_n: int = 5) -> List[str]:
    """
    Extracts conceptual tags using KeyBERT.
    Falls back to a simple frequency count if KeyBERT fails.
    """
    if not text or len(text.strip()) < 10:
        return []
    
    try:
        model = get_kw_model()
        keywords = model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english', 
            top_n=top_n
        )
        return [kw[0] for kw in keywords]
    except Exception as e:
        print(f"KeyBERT extraction failed: {e}. Falling back to simple heuristic.")
        
        # Simple frequency fallback
        words = ''.join(c if c.isalnum() else ' ' for c in text.lower()).split()
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'with', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'as', 'be', 'by'}
        filtered = [w for w in words if w not in stopwords and len(w) > 3]
        
        from collections import Counter
        return [item[0] for item in Counter(filtered).most_common(top_n)]
