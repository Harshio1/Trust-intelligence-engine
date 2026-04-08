import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

try:
    from scraper.blog_scraper import scrape_blog
    from scraper.youtube_scraper import scrape_youtube
    from scraper.pubmed_scraper import scrape_pubmed
except ImportError as e:
    print(f"Warning: Scraper import failed: {e}")

app = FastAPI(title="GutBut Trust API + Dynamic Analytics")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join("scraped_data", "scraped_data.json")

# AUTHORITATIVE 6-SOURCE WHITELIST
EXPERT_SOURCES = [
    "https://my.clevelandclinic.org/health/body/25201-gut-microbiome",
    "https://www.healthline.com/nutrition/gut-microbiome-and-health",
    "https://www.medicalnewstoday.com/articles/323093",
    "https://www.youtube.com/watch?v=1sISguPDlhY",
    "https://www.youtube.com/watch?v=VzPD009qTN4",
    "https://pubmed.ncbi.nlm.nih.gov/29902436/"
]

class AnalyzeRequest(BaseModel):
    url: str

BASELINE_PATH = os.path.join("scraped_data", "expert_baseline.json")

# ABSOLUTE PERSISTENCE: Expert Baseline (Fallback when files are missing)
# This ensures 24/7 availability as requested.
HARDCODED_BASELINE = [
    {
        "source_url": "https://my.clevelandclinic.org/health/body/25201-gut-microbiome",
        "source_type": "blog",
        "title": "What Is Your Gut Microbiome?",
        "description": "Expert medical guidance from Christine Lee, MD",
        "author": "Christine Lee, MD",
        "published_date": "2023-05-15",
        "language": "en",
        "region": "global",
        "topic_tags": ["microbiome", "gut health", "microbiota", "digestive system"],
        "trust_score": 0.92,
        "trust_breakdown": {"author_credibility": 1.0, "citation_count": 1.0, "domain_authority": 0.9, "recency": 0.64, "medical_disclaimer": 0.5, "content_quality": 1.0},
        "trust_explanation": "STRENGTHS: Expert/Trusted Author | High-Authority Domain | Scientifically Referenced || WEAKNESSES: None noted.",
        "strengths": ["Expert/Trusted Author", "High-Authority Domain", "Scientifically Referenced"],
        "weaknesses": [],
        "content_chunks": ["Your gut microbiome is a microscopic world within the world of your larger body.", "Microorganisms living inside your gut make up your gut microbiome.", "Bacteria in your gut help break down certain complex carbohydrates."]
    },
    {
        "source_url": "https://www.healthline.com/nutrition/gut-microbiome-and-health",
        "source_type": "blog",
        "title": "How Does Your Gut Microbiome Affect Your Health?",
        "description": "Expert medical guidance from Healthline Medical Team",
        "author": "Healthline Medical Team",
        "published_date": "2023-06-20",
        "language": "en",
        "region": "global",
        "topic_tags": ["gut health", "microbes", "heart health", "immune system"],
        "trust_score": 0.91,
        "trust_breakdown": {"author_credibility": 0.85, "citation_count": 0.8, "domain_authority": 0.85, "recency": 0.64, "medical_disclaimer": 1.0, "content_quality": 1.0},
        "trust_explanation": "STRENGTHS: Expert/Trusted Author | High-Authority Domain | Scientifically Referenced | Strong Medical Disclaimer || WEAKNESSES: None noted.",
        "strengths": ["Expert/Trusted Author", "High-Authority Domain", "Scientifically Referenced", "Strong Medical Disclaimer"],
        "weaknesses": [],
        "content_chunks": ["Microorganisms, or microbes, include bacteria, viruses, fungi, and other microscopic living things.", "While some bacteria are associated with disease, others are crucial for your immune system.", "New evidence suggests higher microbiome diversity is considered good for your health."]
    },
    {
        "source_url": "https://www.medicalnewstoday.com/articles/323093",
        "source_type": "blog",
        "title": "Everything you need to know about the gut microbiome",
        "description": "Expert medical guidance from Medical News Today",
        "author": "Medical News Today",
        "published_date": "2023-11-10",
        "language": "en",
        "region": "global",
        "topic_tags": ["gut health", "diet", "nutrition", "wellness"],
        "trust_score": 0.84,
        "trust_breakdown": {"author_credibility": 0.85, "citation_count": 0.8, "domain_authority": 0.5, "recency": 0.64, "medical_disclaimer": 1.0, "content_quality": 1.0},
        "trust_explanation": "STRENGTHS: Expert/Trusted Author | Scientifically Referenced | Strong Medical Disclaimer || WEAKNESSES: Non-specialized domain",
        "strengths": ["Expert/Trusted Author", "Scientifically Referenced", "Strong Medical Disclaimer"],
        "weaknesses": ["Non-specialized domain"],
        "content_chunks": ["Protein powders are nutritional supplements that may help build muscle.", "Using protein powder may also aid weight loss and help people tone their muscles.", "There are many different types of protein powder."]
    },
    {
        "source_url": "https://www.youtube.com/watch?v=1sISguPDlhY",
        "source_type": "youtube",
        "author": "TED-Ed",
        "published_date": "2017-03-23",
        "language": "en",
        "region": "global",
        "topic_tags": ["gut microbiome", "healthy gut", "diet", "bacteria"],
        "trust_score": 0.51,
        "trust_breakdown": {"author_credibility": 0.85, "citation_count": 0.0, "domain_authority": 0.5, "recency": 0.26, "medical_disclaimer": 0.5, "content_quality": 0.11},
        "trust_explanation": "STRENGTHS: Expert/Trusted Author || WEAKNESSES: Non-specialized domain | Outdated information",
        "strengths": ["Expert/Trusted Author"],
        "weaknesses": ["Non-specialized domain", "Outdated information"],
        "content_chunks": ["The bacteria in our guts can break down food the body can’t digest.", "We can manipulate the balance of our microbes by paying attention to what we eat.", "How the food you eat affects your gut."]
    },
    {
        "source_url": "https://www.youtube.com/watch?v=VzPD009qTN4",
        "source_type": "youtube",
        "author": "Kurzgesagt – In a Nutshell",
        "published_date": "2017-10-05",
        "language": "en",
        "region": "global",
        "topic_tags": ["microbiome", "microbes", "kurzgesagt", "science"],
        "trust_score": 0.54,
        "trust_breakdown": {"author_credibility": 0.85, "citation_count": 0.0, "domain_authority": 0.5, "recency": 0.26, "medical_disclaimer": 0.5, "content_quality": 0.54},
        "trust_explanation": "STRENGTHS: Expert/Trusted Author || WEAKNESSES: Non-specialized domain | Outdated information",
        "strengths": ["Expert/Trusted Author"],
        "weaknesses": ["Non-specialized domain", "Outdated information"],
        "content_chunks": ["What happens when microbes talk to your brain?", "Trillions of bacteria, viruses, and fungi live inside you.", "How Bacteria Rule Over Your Body – The Microbiome."]
    },
    {
        "source_url": "https://pubmed.ncbi.nlm.nih.gov/29902436/",
        "source_type": "pubmed",
        "author": "Makki K, Deehan EC, Walter J, Bäckhed F",
        "published_date": "2018",
        "language": "en",
        "region": "global",
        "topic_tags": ["gut microbes", "gut microbiota", "dietary fiber"],
        "trust_score": 0.84,
        "trust_breakdown": {"author_credibility": 0.7, "citation_count": 1.0, "domain_authority": 1.0, "recency": 0.3, "medical_disclaimer": 0.5, "content_quality": 0.19},
        "trust_explanation": "STRENGTHS: High-Authority Domain | Scientifically Referenced || WEAKNESSES: None noted.",
        "strengths": ["High-Authority Domain", "Scientifically Referenced"],
        "weaknesses": [],
        "content_chunks": ["The Impact of Dietary Fiber on Gut Microbiota in Host Health and Disease.", "Diet is not only essential to maintain human growth but also modulates.", "Type, quality, and origin of our food shape our gut microbes."]
    }
]

# Session-persistent registry with hard-coded durability
def load_registry() -> List[Dict[str, Any]]:
    # Start with our absolute hardcoded fallback to ensure 24/7 visibility
    registry = HARDCODED_BASELINE.copy()
    reg_map = {s['source_url']: s for s in registry}
    
    # 1. Try to load and update from the baseline file (if it exists and is valid)
    if os.path.exists(BASELINE_PATH):
        try:
            with open(BASELINE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for s in data:
                        url = s.get('source_url')
                        if url in EXPERT_SOURCES:
                            reg_map[url] = s
        except Exception as e:
            print(f"Error loading baseline file: {e}")
    
    # 2. Try to update with newer data from the dynamic file if available
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                dynamic_data = json.load(f)
                if isinstance(dynamic_data, list):
                    for s in dynamic_data:
                        url = s.get('source_url')
                        if url in EXPERT_SOURCES:
                            # Only update if the new data is valid (must have content)
                            if s.get('content_chunks') and len(s.get('content_chunks')) > 0:
                                reg_map[url] = s
        except Exception as e:
            print(f"Error patching registry with dynamic data: {e}")
            
    # Always return exactly the 6 expert sources, prioritizing newest valid data
    return [reg_map[url] for url in EXPERT_SOURCES if url in reg_map]

@app.get("/api/scraped")
async def get_scraped_data():
    """Returns the unified trust registry including defaults. Always reloads to ensure persistence."""
    return load_registry()

@app.post("/api/analyze")
async def analyze_url(request: AnalyzeRequest):
    """Dynamically scrapes and scores any provided URL in real-time."""
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        source_type = "blog"
        if "youtube.com" in url or "youtu.be" in url:
            source_type = "youtube"
        elif "pubmed.ncbi.nlm.nih.gov" in url:
            source_type = "pubmed"

        if source_type == "youtube":
            result = scrape_youtube(url)
        elif source_type == "pubmed":
            result = scrape_pubmed(url)
        else:
            result = scrape_blog(url)
        
        return result
    except Exception as e:
        print(f"Server-side analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis engine failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
