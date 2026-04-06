# GutBut: Multi-Source Trust Analytics Pipeline

A robust automation pipeline for scraping gut-health related content from multiple platforms (Blogs, YouTube, PubMed) and evaluating its medical reliability using a heuristic-based trust scoring engine.

## 🛠️ Tools and Libraries Used
- **Backend**: Python 3.11 with FastAPI (`main_api.py`) for data serving.
- **Scraping**: 
  - `requests` & `BeautifulSoup4` for manual scraping of blogs and PubMed IDs.
  - `youtube-transcript-api` for automated YouTube transcript retrieval.
- **NLP & Data Processing**:
  - `KeyBERT` for keyword extraction and auto-tagging.
  - `langdetect` for automatic language identification.
  - `newspaper3k` logic for clean article text extraction (in `blog_scraper.py`).
- **Frontend**: React (Vite + TypeScript), Tailwind CSS, Framer Motion (animations), and Lucide React (icons).

## 📡 Scraping Approach
The pipeline handles three distinct source types:
1.  **Blogs**: Uses custom headers to mimic browser requests, extracts clean article text while stripping ads/navigation, and targets structured metadata (author, pub date).
2.  **YouTube**: Extracts video metadata using robust regex patterns. Transcript fetching includes a defensive instance-based fallback (`YouTubeTranscriptApi().fetch()`) to handle various API versions.
3.  **PubMed**: Utilizes the NCBI Entrez E-utilities (XML API) for high-precision extraction of peer-reviewed titles, abstracts, and author lists.

## ⚖️ Trust Score Design
The **GutBut Trust Engine** calculates a reliability score ($0.0$ to $1.0$) based on the following weighted formula:
$$Trust Score = f(Author, Domain, Recency, Citations, Disclaimer)}$$

- **Author Credibility**: Average score of all named authors. Deduct for "Unknown" or generic names; bonus for "Dr.", "MD", "PhD", or institutional labels.
- **Recency**: Implements an exponential decay function ($0.2 \cdot e^{-0.2 \cdot age}$) favoring research from the last 2 years.
- **Domain Authority**: Predefined mapping of highly trusted domains (NIH, PubMed, Mayo Clinic).
- **Abuse Prevention**: Penalties for "medical miracle" keywords, lack of disclaimers, and SEO spam triggers.

## ⚠️ Limitations
- **YouTube Metadata**: Extraction is inherently fragile due to dynamic Google DOM changes.
- **Region Detection**: Geographic region is currently defaulted to "global" unless explicitly tagged.
- **Bias**: The heuristic scoring favors academic/institutional authors over independent creators.

## 🚀 How to Run
1.  **Configure Environment**:
    - Install Python dependencies: `pip install -r requirements.txt`
    - Install Node dependencies: `cd frontend && npm install`
2.  **Run Pipeline**:
    - `python main.py` (Scrapes data and generates `output/scraped_data.json`).
3.  **Launch Backend**:
    - `python main_api.py` (Runs FastAPI on localhost:8000).
4.  **Launch Dashboard**:
    - `cd frontend && npm run dev` (View the Data Explorer on localhost:5173).
