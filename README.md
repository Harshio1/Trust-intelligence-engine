# GutBut Trust Intelligence Engine

## Overview
The **GutBut Trust Intelligence Engine** is a comprehensive data pipeline and real-time analysis platform designed to evaluate the reliability of health and science content across the web. Developed for the Data Scraping & Trust Scoring assignment, the system ingests data from blogs, YouTube transcripts, and PubMed abstracts, applying a sophisticated mathematical model to generate a trust reliability score between 0.0 and 1.0.

## Tools & Libraries Used
- **fastapi & uvicorn**: High-performance web framework and server for real-time URL analysis.
- **requests & beautifulsoup4**: Core scraping engine for fetching and parsing HTML content.
- **youtube-transcript-api**: Specialized library for extracting text data from video content.
- **keybert / TF-IDF fallback**: AI-driven keyword extraction with a robust frequency-based fallback.
- **langdetect**: Automatic language identification for regional content analysis.
- **pandas**: Used for structured data management and registry organization.
- **biopython**: Specialized tools for handling technical metadata from clinical sources (NCBI).
- **python-multipart**: Handles form-data for real-time analysis requests.
- **scikit-learn**: Provides the foundation for semantic analysis and feature extraction.

## Scraping Approach
The engine employs a modular scraping architecture:
- **`blog_scraper.py`**: Prioritizes **JSON-LD** and **Open Graph** metadata with DOM sanitization to isolate core article content.
- **`youtube_scraper.py`**: Extracts high-fidelity transcripts and channel metadata directly from the HTML without API dependency.
- **`pubmed_scraper.py`**: Utilizes precise CSS selectors to ingest clinical abstracts, authors, and journal details.
- **`utils/chunking.py`**: Implements content chunking to handle long articles and optimize for NLP processing.

## Trust Score Design
Our scoring model calculates reliability using 6 weighted components:
1. **Domain Authority (30%)**
2. **Author Credibility (25%)**
3. **Recency / Date Decay (15%)**
4. **Citations & References (15%)**
5. **Medical Disclaimer Presence (10%)**
6. **Content Density (5%)**

The final score is enhanced using **Sigmoid Scaling ($k=7$)** to provide clear separation between high-trust and low-trust sources, ultimately mapped to a range of **0.0 to 1.0**.

## Topic Tagging
- **Semantic Extraction**: Uses KeyBERT to identify core themes within the content.
- **Parameters**: Employs an N-gram range of (1, 2) for phrase-based tagging.
- **Safety**: Protected by a `langdetect` language guard and a high-performance frequency-based fallback.

## Edge Cases Handled
- **Missing Metadata**: Automatically assigns a neutral baseline (0.5) to missing fields without crashing the pipeline.
- **Multiple Authors**: Calculates aggregate credibility for clinical teams and multi-author papers.
- **Non-English Content**: Identifies and flags foreign-language content for regional auditing.
- **Long Articles**: Split into manageable fragments to ensure comprehensive audit coverage.

## Limitations
- **Dynamic YouTube DOM**: Metadata extraction is subject to YouTube's periodic HTML structure updates.
- **Institutional Bias**: The algorithm currently favors established academic domains over independent research.
- **No OCR Support**: Data within images or video overlays cannot currently be ingested.
- **Ephemeral Filesystem**: In cloud environments (Render), new results are stored in memory and not persisted across restarts.

## How to Run

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Seed the initial registry (6 mandatory sources)
python main.py

# Start the API server
uvicorn main_api:app --reload
```

### API Endpoints
- **`GET /api/scraped`**: Retrieves the full audit registry.
- **`POST /api/analyze`**: Submits a URL for real-time intelligence analysis.

### Live Demo
- **Backend API**: [https://gutbut-api.onrender.com](https://gutbut-api.onrender.com)
- **Frontend Dashboard**: [https://gutbut-frontend.onrender.com](https://gutbut-frontend.onrender.com)

## Project Structure
```text
project/
├── scraper/                # Source-specific scraping logic
│   ├── blog_scraper.py
│   ├── youtube_scraper.py
│   └── pubmed_scraper.py
├── scoring/                # Trust Intelligence Engine
│   └── trust_score.py
├── utils/                  # NLP & Utility modules
│   ├── tagging.py
│   └── chunking.py
├── output/                 # Local data storage (JSON)
├── frontend/               # React + Vite Dashboard
│   ├── src/
│   │   ├── components/
│   │   └── App.tsx
│   └── tsconfig.json
├── main.py                 # Pipeline Seeding Script
├── main_api.py             # FastAPI Backend
├── requirements.txt        # Backend Dependencies
├── Short_Report.md         # Technical Report
└── README.md               # Documentation
```
