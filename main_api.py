from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import re

# Import scrapers
from scraper.blog_scraper import scrape_blog
from scraper.youtube_scraper import scrape_youtube
from scraper.pubmed_scraper import scrape_pubmed

app = FastAPI(title="GutBut Trust API + Dynamic Analytics")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join("output", "scraped_data.json")

class AnalyzeRequest(BaseModel):
    url: str

@app.get("/api/scraped")
async def get_scraped_data():
    """Returns the unified trust registry from local storage."""
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            return {"error": f"Failed to load data: {str(e)}"}
    return {"error": "Registry not found. Run main.py to seed."}

@app.post("/api/analyze")
async def analyze_url(request: AnalyzeRequest):
    """
    Dynamically scrapes and scores any provided URL in real-time.
    Supports YouTube, PubMed, and Blogs.
    """
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        # 1. Source Type Detection
        source_type = "blog"
        if "youtube.com" in url or "youtu.be" in url:
            source_type = "youtube"
        elif "pubmed.ncbi.nlm.nih.gov" in url:
            source_type = "pubmed"

        # 2. Scrape & Score in Real-time
        if source_type == "youtube":
            result = scrape_youtube(url)
        elif source_type == "pubmed":
            result = scrape_pubmed(url)
        else:
            result = scrape_blog(url)

        return result
    except Exception as e:
        print(f"Server-side analysis error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis engine failure: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
