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

class AnalyzeRequest(BaseModel):
    url: str

# Session-persistent registry
def load_registry() -> List[Dict[str, Any]]:
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # STRICT FILTER: Ensure we only keep the 6 high-fidelity defaults 
                    # and any newly analyzed valid entries. Remove stale "Unknown" blogs.
                    return [
                        s for s in data 
                        if not (s.get('title') == "Unknown" and s.get('source_type') == "blog")
                    ]
        except Exception as e:
            print(f"Error loading registry: {e}")
    return []

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
        
        # Prevent duplicates and append to registry
        if not any(s.get('source_url') == url for s in active_registry):
            active_registry.append(result)

        return result
    except Exception as e:
        print(f"Server-side analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis engine failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
