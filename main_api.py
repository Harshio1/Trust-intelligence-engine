from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import re

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

DATA_PATH = os.path.join("output", "scraped_data.json")

class AnalyzeRequest(BaseModel):
    url: str

@app.get("/api/scraped")
async def get_scraped_data():
    """Returns the unified trust registry from local storage with a robust fallback."""
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    
    # Robust Fallback: Real 6 sources scraped during development
    return [
        {
            "source_url": "https://my.clevelandclinic.org/health/body/25201-gut-microbiome",
            "source_type": "blog",
            "author": "Christine Lee, MD",
            "published_date": "2023-05-15",
            "language": "en",
            "topic_tags": ["gut microbiome", "microbiome gut", "gut microbiota", "digestive", "immune system"],
            "trust_score": 0.88,
            "trust_breakdown": {"author_credibility": 0.9, "citation_count": 0.7, "domain_authority": 0.9, "recency": 0.8, "medical_disclaimer": 1.0, "content_quality": 1.0},
            "strengths": ["Expert/Trusted Author", "High-Authority Domain", "Recent Medical Data"],
            "weaknesses": ["None noted"],
            "content_chunks": ["Your gut microbiome is a microscopic world within the world of your larger body. The trillions of microorganisms that live there affect each other and their environment in various ways."]
        },
        {
            "source_url": "https://www.healthline.com/nutrition/gut-microbiome-and-health",
            "source_type": "blog",
            "author": "Healthline Medical Team",
            "published_date": "2023-06-20",
            "language": "en",
            "topic_tags": ["nutrition", "gut health", "bacteria", "weight management"],
            "trust_score": 0.82,
            "trust_breakdown": {"author_credibility": 0.8, "citation_count": 0.6, "domain_authority": 0.85, "recency": 0.8, "medical_disclaimer": 1.0, "content_quality": 0.9},
            "strengths": ["Evidence-Based Content", "Medical Review System"],
            "weaknesses": ["Commercial affiliations"],
            "content_chunks": ["The bacteria and other microbes that live in your gut are known as your gut microbiome. They help you digest food and may support immune, heart, and brain health."]
        },
        {
            "source_url": "https://www.medicalnewstoday.com/articles/323093",
            "source_type": "blog",
            "author": "Medical News Today",
            "published_date": "2023-11-10",
            "language": "en",
            "topic_tags": ["microbiome", "diet", "disease prevention", "gut-brain axis"],
            "trust_score": 0.85,
            "trust_breakdown": {"author_credibility": 0.8, "citation_count": 0.8, "domain_authority": 0.9, "recency": 0.9, "medical_disclaimer": 1.0, "content_quality": 1.0},
            "strengths": ["Peer-Reviewed Citations", "Detailed Scientific Breakdown"],
            "weaknesses": ["None noted"],
            "content_chunks": ["The gut microbiome is the name given to the trillions of bacteria and other microorganisms that live in the human digestive tract."]
        },
        {
            "source_url": "https://www.youtube.com/watch?v=1sISguPDlhY",
            "source_type": "youtube",
            "author": "TED-Ed",
            "published_date": "2017-03-23",
            "language": "en",
            "topic_tags": ["food impact", "gut health", "microbes", "digestion"],
            "trust_score": 0.70,
            "trust_breakdown": {"author_credibility": 0.85, "citation_count": 0.6, "domain_authority": 0.5, "recency": 0.26, "medical_disclaimer": 0.5, "content_quality": 0.96},
            "strengths": ["Expert/Trusted Author", "Educational Value"],
            "weaknesses": ["Outdated information"],
            "content_chunks": ["Dietary fiber from foods like fruits, vegetables, nuts, legumes, and whole grains is the best fuel for gut bacteria."]
        },
        {
            "source_url": "https://www.youtube.com/watch?v=VzPD009qTN4",
            "source_type": "youtube",
            "author": "Kurzgesagt – In a Nutshell",
            "published_date": "2017-10-05",
            "language": "en",
            "topic_tags": ["microbiome explained", "bacteria rule", "internal army"],
            "trust_score": 0.68,
            "trust_breakdown": {"author_credibility": 0.85, "citation_count": 0.4, "domain_authority": 0.5, "recency": 0.26, "medical_disclaimer": 0.5, "content_quality": 1.0},
            "strengths": ["High-Quality Animation", "Expert Consultation"],
            "weaknesses": ["Non-specialized domain"],
            "content_chunks": ["Some scientists think the microbiome does this, to communicate with the vagus nerve. The information highway of our nervous system."]
        },
        {
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/29902436/",
            "source_type": "pubmed",
            "author": "Makki K, et al.",
            "published_date": "2018",
            "language": "en",
            "topic_tags": ["dietary fiber", "gut microbiota", "host health", "clinical study"],
            "trust_score": 0.89,
            "trust_breakdown": {"author_credibility": 1.0, "citation_count": 1.0, "domain_authority": 1.0, "recency": 0.3, "medical_disclaimer": 1.0, "content_quality": 1.0},
            "strengths": ["Primary Scientific Literature", "High Domain Authority"],
            "weaknesses": ["Technical complexity"],
            "content_chunks": ["Type, quality, and origin of our food shape our gut microbes and affect their composition and function, impacting host-microbe interactions."]
        }
    ]

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
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
