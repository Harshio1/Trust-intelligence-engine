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

# Session-persistent registry with hard-coded durability
def load_registry() -> List[Dict[str, Any]]:
    registry = []
    
    # 1. Load the baseline (Absolute persistence for the 6 core sources)
    if os.path.exists(BASELINE_PATH):
        try:
            with open(BASELINE_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception as e:
            print(f"Error loading baseline: {e}")
    
    # 2. Try to update with newer data from the dynamic file if available
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                dynamic_data = json.load(f)
                if isinstance(dynamic_data, list):
                    # Map existing registry by URL for easy patching
                    reg_map = {s['source_url']: s for s in registry if 'source_url' in s}
                    for s in dynamic_data:
                        url = s.get('source_url')
                        if url in EXPERT_SOURCES:
                            # Only update if the new data is valid
                            if s.get('content_chunks') and len(s.get('content_chunks')) > 0:
                                reg_map[url] = s
                    registry = list(reg_map.values())
        except Exception as e:
            print(f"Error patching registry with dynamic data: {e}")
            
    # ABSOLUTE FILTER: Only allow the 6 pre-verified Expert Sources
    # This ensures "stale" or "unknown" entries from scraping never appear.
    return [
        s for s in registry 
        if s.get('source_url') in EXPERT_SOURCES
    ]

# State for the current session
active_registry = load_registry()

@app.get("/api/scraped")
async def get_scraped_data():
    """Returns the unified trust registry including defaults and newly analyzed URLs."""
    global active_registry
    return active_registry

@app.post("/api/analyze")
async def analyze_url(request: AnalyzeRequest):
    """Dynamically scrapes and scores any provided URL in real-time."""
    global active_registry
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
        
        # Return the result immediately without persisting to the global registry
        # This ensures the new content disappears on refresh as requested.
        return result
    except Exception as e:
        print(f"Server-side analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis engine failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
