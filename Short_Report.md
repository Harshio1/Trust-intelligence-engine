# GutBut Trust Intelligence: Data Scraping & Trust Scoring Report

**Project**: Multi-Source Trust Intelligence Engine  
**Author**: GutBut Engineering Team  
**Date**: April 6, 2026  

---

## 1. Scraping Strategy
The system utilizes a modular, multi-source scraping architecture designed for high-density metadata extraction and content retrieval.

### **1.1. Architecture & Tools**
- **Blog Scraper**: Uses `requests` for fetching and `BeautifulSoup4` for parsing. It prioritizes **JSON-LD (Schema.org)** data for structured metadata (author, date, region) and falls back to Open Graph/Meta tags.
- **YouTube Scraper**: Leverages the `youtube-transcript-api` to extract full video transcripts. Metadata (Channel Name, Publish Date) is extracted from the video's underlying HTML structure to avoid heavy API dependencies.
- **PubMed Scraper**: Specifically tuned for clinical reliability. It extracts technical abstracts, multi-author lists, and specific journal provenance using targeted CSS selectors.

### **1.2. Content Extraction**
To ensure clean data for analysis, the system implements **DOM Sanitization** to remove navigation links, advertisements, and unrelated sidebars. Extracting only the "core" text body is critical for accurate trust scoring and topic tagging.

---

## 2. Topic Tagging Method
The system implements a sophisticated NLP-based tagging engine located in `utils/tagging.py`.

### **2.1. AI-Powered Extraction**
We use **KeyBERT** initialized with the `all-MiniLM-L6-v2` transformer model. Unlike simple frequency counts, KeyBERT uses BERT embeddings to identify keywords that are most semantically similar to the document's central theme.
- **N-gram Range**: Set to (1, 2) to capture both individual concepts (e.g., "Microbiome") and complex phrases (e.g., "Gut Health").
- **Language Detection**: Integrated `langdetect` ensures that the system identifies the source language before processing, allowing for future multi-lingual expansion.

### **2.2. Reliability Fallbacks**
In scenarios where transformer-based extraction fails (e.g., extremely short text or resource constraints), the system automatically falls back to a frequency-based heuristic with weighted stop-word filtering to ensure `topic_tags` is never empty.

---

## 3. Trust Score Algorithm
The Trust Scoring system (`scoring/trust_score.py`) moves away from rigid `if-else` thresholds in favor of a **Continuous Mathematical Model**.

### **3.1. Component Weights**
The final score is a weighted linear combination of six normalized signals:
- **Domain Authority (30%)**: Verified against a whitelist of clinical journals (NIH, PubMed, Mayo Clinic).
- **Author Credibility (25%)**: Penalizes "Unknown" authors; boosts verified medical credentials (MD, PhD, MBBS).
- **Recency (15%)**: Uses an **Exponential Decay Function** ($e^{-0.15 \times age}$) to significantly penalize outdated medical data.
- **Citation Density (15%)**: Scans for scientific markers (DOI, [number], "journal", "study").
- **Medical Disclaimers (10%)**: Rewards the presence of safety transparency.
- **Content Quality (5%)**: Based on semantic density and length.

### **3.2. Advanced Calibration**
To ensure clear separation between "Trusted" and "Unreliable" sources, we apply:
1. **Sigmoid Scaling**: A steepening function ($k=7$) centered at 0.5 to spread scores away from the neutral middle.
2. **Confidence Weighting**: The final score is multiplied by $(0.8 + 0.2 \times \text{confidence})$ where confidence is a ratio of available vs. missing metadata.
3. **Non-linear Spread**: A power effect ($x^{1.2}$) is applied to push high-trust scores toward the 0.9+ range while suppressing lower scores.

---

## 4. Edge Case Handling & Abuse Prevention
The engine is hardened against common manipulation tactics.

### **4.1. Edge Cases**
- **Missing Metadata**: Instead of failing, the system assigns a **Neutral Baseline (0.5)** to unknown authors/dates but applies a "Missing Metadata" penalty to the final confidence score.
- **Multiple Authors**: The system lists all detected authors and computes an **Average Credibility Score** to prevent a single outlier from skewing the audit.
- **Long Articles**: Implemented **Content Chunking** (in `utils/chunking.py`) to break long narratives into segments for localized analysis.

### **4.2. Abuse Prevention Logic**
- **Fake Authors**: Cross-checks author strings against known credential patterns. Anonymous "staff" or "admin" users are automatically capped at the neutral baseline.
- **SEO Spam Detection**: A dedicated "Abuse Monitor" scans for sensationalist "Miracle Cure" keywords. Domains exhibiting high spam-keyword density receive a heavy penalty magnitude ($0.2 \times \text{spam_score}$).
- **Compliance Enforcement**: Flagging is used to alert the UI of **outdated_content**, **low_citation_count**, or **missing_disclaimer** through explicit audit badges.

---
**Conclusion**: This dual-layered approach combining robust scraping with a mathematically spread trust model provides a clinical-grade intelligence platform capable of identifying high-integrity medical content at scale.
