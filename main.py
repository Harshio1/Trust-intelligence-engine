import os
import json
import traceback

from scraper.blog_scraper import scrape_blog
from scraper.youtube_scraper import scrape_youtube
from scraper.pubmed_scraper import scrape_pubmed

# GUT-HEALTH SOURCE POOLS (Priority + Fallbacks)
BLOG_SOURCES = [
    "https://my.clevelandclinic.org/health/body/25201-gut-microbiome", 
    "https://www.healthline.com/nutrition/gut-microbiome-and-health",
    "https://www.medicalnewstoday.com/articles/323093",
    "https://www.hopkinsmedicine.org/health/wellness-and-prevention/the-brain-gut-connection",
    "https://www.hsph.harvard.edu/nutritionsource/microbiome/"
]

YOUTUBE_SOURCES = [
    "https://www.youtube.com/watch?v=1sISguPDlhY",
    "https://www.youtube.com/watch?v=VzPD009qTN4",
    "https://www.youtube.com/watch?v=B9RruVkEQXI"
]

PUBMED_SOURCES = [
    "https://pubmed.ncbi.nlm.nih.gov/29902436/",
    "https://pubmed.ncbi.nlm.nih.gov/30535917/"
]

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# AUTHORITATIVE 6-SOURCE LIST (Must persist)
EXPERT_SOURCES = [
    "https://my.clevelandclinic.org/health/body/25201-gut-microbiome",
    "https://www.healthline.com/nutrition/gut-microbiome-and-health",
    "https://www.medicalnewstoday.com/articles/323093",
    "https://www.youtube.com/watch?v=1sISguPDlhY",
    "https://www.youtube.com/watch?v=VzPD009qTN4",
    "https://pubmed.ncbi.nlm.nih.gov/29902436/"
]

def main():
    print("Starting Multi-source Data Ingestion + Trust Scoring Pipeline")
    
    output_dir = "scraped_data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "scraped_data.json")

    # 0. Load existing data to preserve if scrape fails
    existing_data_map = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    existing_data_map = {s['source_url']: s for s in raw if 'source_url' in s}
        except Exception:
            pass
    
    # 1. Scrape Blogs (Target: 3)
    print("\n--- Phase 1: Scraping Blogs ---")
    blog_data = []
    # PRIORITIZE EXPERT SOURCES FIRST
    for url in BLOG_SOURCES:
        if len(blog_data) >= 3: break
        try:
            data = scrape_blog(url)
            # Only accept if it has content and identifiable author (if possible)
            if data and data.get("content_chunks"):
                blog_data.append(data)
                print(f"✅ Successfully scraped Blog: {url} (Author: {data['author']})")
            else:
                raise ValueError("Incomplete data")
        except Exception as e:
            if url in EXPERT_SOURCES and url in existing_data_map:
                blog_data.append(existing_data_map[url])
                print(f"♻️  Preserved PERSISTENT Expert Blog: {url} (Scrape failed: {e})")
            else:
                print(f"❌ Error scraping blog {url}: {e}")
            
    # 2. Scrape YouTube (Target: 2)
    print("\n--- Phase 2: Scraping YouTube ---")
    youtube_data = []
    for url in YOUTUBE_SOURCES:
        if len(youtube_data) >= 2: break
        try:
            data = scrape_youtube(url)
            if data:
                youtube_data.append(data)
                print(f"✅ Successfully scraped YouTube: {url}")
            else:
                raise ValueError("Incomplete data")
        except Exception as e:
            if url in EXPERT_SOURCES and url in existing_data_map:
                youtube_data.append(existing_data_map[url])
                print(f"♻️  Preserved PERSISTENT Expert YouTube: {url} (Scrape failed: {e})")
            else:
                print(f"❌ Error scraping YouTube {url}: {e}")
            
    # 3. Scrape PubMed (Target: 1)
    print("\n--- Phase 3: Scraping PubMed ---")
    pubmed_data = []
    for url in PUBMED_SOURCES:
        if len(pubmed_data) >= 1: break
        try:
            data = scrape_pubmed(url)
            if data:
                pubmed_data.append(data)
                print(f"✅ Successfully scraped PubMed: {url}")
            else:
                raise ValueError("Incomplete data")
        except Exception as e:
            if url in EXPERT_SOURCES and url in existing_data_map:
                pubmed_data.append(existing_data_map[url])
                print(f"♻️  Preserved PERSISTENT Expert PubMed: {url} (Scrape failed: {e})")
            else:
                print(f"❌ Error scraping PubMed {url}: {e}")
            
    # 4. Final Validation & Combine
    print("\n--- Phase 4: Final Validation ---")
    print(f"Blogs: {len(blog_data)} / 3")
    print(f"YouTube: {len(youtube_data)} / 2")
    print(f"PubMed: {len(pubmed_data)} / 1")
    
    combined_data = blog_data + youtube_data + pubmed_data
    save_json(combined_data, output_path)
    
    # 5. Logging Abuse Metrics
    print("\n--- Phase 5: Abuse Prevention Audit ---")
    for i, item in enumerate(combined_data):
        flags = item.get("abuse_flags", [])
        penalty = item.get("abuse_penalty", 0.0)
        source = item.get("source_url", "Unknown")[:50] + "..."
        if flags:
            print(f"⚠️  ABUSE ALERT [{item['source_type'].upper()}] {source}")
            print(f"   Flags: {', '.join(flags)}")
            print(f"   Penalty: {penalty}")
        else:
            print(f"✅  CLEAN [{item['source_type'].upper()}] {source}")
    
    if len(blog_data) == 3 and len(youtube_data) == 2 and len(pubmed_data) == 1:
        print("\n🏆 COMPLIANCE ACHIEVED: Exactly 6 sources processed.")
    else:
        print("\n⚠️ WARNING: Missing some sources. Check logs.")
    
    print(f"Data saved to {output_dir}/scraped_data.json")
    
    print(f"\nPipeline completed successfully! Data saved to {output_dir}/ folder.")

if __name__ == "__main__":
    main()
