import re
import math
from datetime import datetime
from typing import Dict, Any, List, Union

def compute_abuse_scores(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates normalized abuse metrics [0, 1].
    - spam_score: Density of sensationalist keywords.
    - metadata_missing_score: Ratio of missing critical fields.
    """
    text_lower = record.get('text', '').lower()
    author = str(record.get('author', '')).lower()
    publish_date = str(record.get('publish_date', '')).lower()
    
    # 1. Spam Score Calculation
    spam_keywords = ["miracle cure", "instant results", "guaranteed", "secret remedy", "100% cure", "completely cure", "doctors hate this"]
    spam_hits = sum(1 for kw in spam_keywords if kw in text_lower)
    spam_score = min(1.0, spam_hits / 2.0) # 2+ hits = 1.0 spam score
    
    # 2. Metadata Missing Score Calculation
    critical_fields = [
        bool(author and author not in ['unknown', 'admin', 'staff', 'channel not available']),
        bool(publish_date and publish_date != 'unknown'),
        len(text_lower) > 500  # Minimum content length
    ]
    missing_count = sum(1 for field in critical_fields if not field)
    metadata_missing_score = missing_count / len(critical_fields)
    
    # Flags for UI transparency
    flags = []
    if spam_score > 0.5: flags.append("seo_spam_detected")
    if metadata_missing_score > 0.5: flags.append("missing_metadata_risk")
    
    return {
        "spam_score": spam_score,
        "metadata_missing_score": metadata_missing_score,
        "flags": flags
    }

def score_single_author(author: str) -> float:
    """
    Returns a normalized author credibility score [0.5, 1.0].
    Unknown/Missing starts at 0.5 (Neutral baseline).
    """
    if not author:
        return 0.5
    
    author_lower = str(author).lower()
    if any(p in author_lower for p in ['unknown', 'admin', 'staff', 'guest', 'channel not available']):
        return 0.5
        
    # Expert Credentials (High)
    expert_patterns = r'\b(dr\.?|md|phd|m\.d\.|p\.h\.d\.|mbbs|do)\b'
    if re.search(expert_patterns, author_lower):
        return 1.0
        
    # Institutional Affiliation (Med-High: 0.85)
    inst_patterns = r'\b(ted|kurzgesagt|clinic|hospital|university|nih|who|cdc|mayo|cleveland|healthline|institute|academy|center|lab|research|medical|medicine|hopkins|harvard|nature|science|statnews)\b'
    if re.search(inst_patterns, author_lower):
        return 0.85
        
    # Named Identity (Medium: 0.7)
    if len(author.strip()) > 3:
        return 0.7
        
    return 0.5

def get_domain_score(url: str) -> float:
    """
    Returns a normalized domain authority score [0.1, 1.0].
    """
    url_lower = url.lower()
    
    # Map domains to scores
    authoritative_domains = {
        'nih.gov': 1.0, 'pubmed': 1.0, 'cdc.gov': 1.0, 'who.int': 1.0, 'fda.gov': 1.0,
        'mayoclinic.org': 0.9, 'clevelandclinic.org': 0.9, 'hopkinsmedicine.org': 0.9,
        'nature.com': 0.9, 'sciencedirect.com': 0.9,
        'healthline.com': 0.85, 'zoe.com': 0.8, 'theconversation.com': 0.8, 'ted.com': 0.75,
        '.gov': 0.8, '.edu': 0.8, '.org': 0.6
    }
    
    for domain, score in authoritative_domains.items():
        if domain in url_lower:
            return score
            
    # Spammy indicators
    if re.search(r'\b(seo|buy|cheap|spam|shop|blogpot)\b', url_lower):
        return 0.1
        
    return 0.5 # Default to neutral 0.5 for signal strength

def calculate_trust_score(
    text: str,
    author: Union[str, List[str]],
    source_url: str,
    publish_date: str,
    source_type: str
) -> Dict[str, Any]:
    """
    Mathematical Trust Engine based on continuous weighted combination with baseline lift.
    """
    # Initialize components [0, 1]
    author_list = author if isinstance(author, list) else [author]
    author_score = sum(score_single_author(a) for a in author_list) / len(author_list) if author_list else 0.5
    
    domain_score = get_domain_score(source_url)
    
    # Recency [0, 1] - Exponential Decay
    recency_score = 0.5
    if publish_date and str(publish_date).lower() != 'unknown':
        try:
            matches = re.search(r'(\d{4})', str(publish_date))
            if matches:
                year = int(matches.group(1))
                age_years = max(0, datetime.now().year - year)
                recency_score = round(math.exp(-0.15 * age_years), 3) 
        except Exception: pass
        
    # Disclaimer [0, 1] - Weighted keywords (Moderate default 0.5)
    disclaimer_keywords = ['medical advice', 'consult a doctor', 'not a substitute', 'informational purposes only', 'disclaimer']
    disclaimer_score = 1.0 if any(kw in text.lower() for kw in disclaimer_keywords) else 0.5
    
    # Citations [0, 1] - Continuous mapping
    citation_keywords = [r'study', r'clinical', r'research', r'journal', r'doi:', r'pubmed', r'references']
    citation_hits = sum(1 for kw in citation_keywords if re.search(kw, text.lower()))
    if source_type.lower() == 'pubmed':
        citation_score = 1.0
    else:
        citation_score = min(1.0, (citation_hits / 5.0) + (0.2 if '[' in text else 0.0))
        
    # Content Quality [0, 1]
    content_quality_score = min(1.0, len(text) / 5000.0)

    # 1. Base Score calculation (Weighted Linear Combination)
    weights = {
        "author_credibility": 0.25,
        "citation_count": 0.15,
        "domain_authority": 0.30,
        "recency": 0.15,
        "medical_disclaimer": 0.10,
        "content_quality": 0.05
    }
    
    components = {
        "author_credibility": author_score,
        "citation_count": citation_score,
        "domain_authority": domain_score,
        "recency": recency_score,
        "medical_disclaimer": disclaimer_score,
        "content_quality": content_quality_score
    }
    
    base_score = sum(components[k] * weights[k] for k in weights)

    # [REFINEMENT] 1.5 Baseline Lift (0.15 + 0.85 * score)
    score_lifted = 0.15 + (0.85 * base_score)

    # 2. Continuous Penalties
    abuse = compute_abuse_scores({
        "text": text,
        "author": str(author),
        "source_url": source_url,
        "publish_date": publish_date
    })
    
    penalty_magnitude = 0.2 * abuse["spam_score"] + 0.1 * abuse["metadata_missing_score"]
    score_adjusted = score_lifted - penalty_magnitude
    
    # 3. Sigmoid Scaling (k=7, c=0.5 for high contrast)
    score_sigmoid = 1 / (1 + math.exp(-7 * (score_adjusted - 0.5)))
    
    # 4. Confidence Weighting
    meta_present = [
        bool(author and str(author).lower() not in ['unknown', 'channel not available']),
        bool(publish_date and str(publish_date).lower() != 'unknown'),
        len(text.strip()) > 100
    ]
    confidence_score = sum(meta_present) / len(meta_present)
    
    final_score = score_sigmoid * (0.8 + 0.2 * confidence_score)
    final_score = final_score ** 1.2 # Non-linear spread
    final_score = max(0.0, min(1.0, final_score))

    # Explanation Generation & Flags
    strengths = []
    weaknesses = []
    flags = abuse["flags"]
    
    # Map low component scores to risk flags for UI badges
    if recency_score < 0.3: flags.append("outdated_content")
    if disclaimer_score < 0.6: flags.append("missing_disclaimer")
    if citation_score < 0.4: flags.append("low_citation_count")
    
    if author_score >= 0.8: strengths.append("Expert/Trusted Author")
    elif author_score < 0.6: weaknesses.append("Non-identifiable author")
    
    if domain_score >= 0.8: strengths.append("High-Authority Domain")
    elif domain_score < 0.6: weaknesses.append("Non-specialized domain")
    
    if recency_score >= 0.7: strengths.append("Recently Published")
    elif recency_score < 0.3: weaknesses.append("Outdated information")
    
    if citation_score > 0.6: strengths.append("Scientifically Referenced")
    else: weaknesses.append("Few external citations")
    
    if disclaimer_score > 0.8: strengths.append("Strong Medical Disclaimer")
    
    explanation_str = "STRENGTHS: " + (" | ".join(strengths) if strengths else "None noted.")
    explanation_str += " || WEAKNESSES: " + (" | ".join(weaknesses) if weaknesses else "None noted.")

    return {
        "score": round(final_score, 2),
        "trust_breakdown": {k: round(v, 2) for k, v in components.items()},
        "trust_explanation": explanation_str,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "confidence_score": round(confidence_score, 2),
        "abuse_flags": list(set(flags)), # Ensure uniqueness
        "abuse_penalty": -round(penalty_magnitude, 2)
    }
