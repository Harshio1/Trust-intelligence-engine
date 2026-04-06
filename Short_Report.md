# Short Report: Data Scraping & Trust Scoring Implementation

## 1. Scraping Strategy
The project implements a **multi-phase ingestion pipeline** (`main.py`) designed for high availability and metadata precision.

- **Phase 1: Blogs**: We utilize `requests` with a browser-mimicking `User-Agent`. Article cleaning is handled by the `BeautifulSoup` to extract the primary `article` or `main` tag content while discarding non-content elements (ads, nav, sidebars) to ensure high textual data quality.
- **Phase 2: YouTube**: We use a **hybrid parsing method**. High-level metadata is extracted directly from the video page HTML using optimized regex patterns to avoid the overhead of heavy scraping libraries. Transcripts are fetched via the `youtube-transcript-api` with a custom-built instance fallback to ensure reliability across changing Google API updates.
- **Phase 3: PubMed**: We leverage the official **NCBI Entrez E-utilities XML API**. This ensures we get high-fidelity, structured data directly from the source, specifically targeting Article Titles, Abstracts, Journals, and full Author lists with minimal scraping noise.

## 2. Topic Tagging Method
Topic identification is handled by the `tagging.py` utility using **KeyBERT**. 
- **Algorithm**: KeyBERT uses BERT-based sentence embeddings (Transformer-based) to identify keywords and phrases that are most representative of the content. 
- **Execution**: We extract the top-5 most relevant tags per source (e.g., "gut health", "microbiome", "bacteria") to populate the `topic_tags` field, enabling structured filtering in the UI.

## 3. Trust Score Algorithm
The **GutBut Trust Score** is a heuristic weight-based engine ($0-1$ range) implementing the requested formula:
$$Trust Score = Base (0.3) + \sum Authors, Domain, Recency, Citations, Disclaimer}$$

- **Author Averaging**: For multi-author sources (PubMed), we compute the average credibility score of all contributors. This prevents a single unverified name from zeroing out the reputation of a professional research group.
- **Recency Decay**: Rather than static year-based rules, we use an **exponential decay model** ($0.2 \cdot e^{-0.2 \cdot age}$). This ensures that a paper from 2024 is significantly more trusted than one from 2018, reflecting the fast-moving pace of gut microbiome science.
- **Validation**: High-trust medical domains (NIH, Cleveland Clinic) receive a significant boost ($+0.30$), while commercial/spam domains receive heavy penalties.

## 4. Edge Case Handling
- **Missing Metadata**: If an author or date is missing, the system applies safety defaults (e.g., "Channel not available", "Unknown") and applies a corresponding trust penalty ($ -0.15 $).
- **Non-English Content**: The `langdetect` library automatically identifies the source language to populate the `language` field, with a default fallback to "en".
- **Dynamic Content**: For long articles, our `chunking.py` utility ensures that data is split into manageable segments for downstream LLM or search indexing performance.
- **Baseline Trust**: Every source is guaranteed a **minimum score of 0.2** as per requirement, preventing any valid URI from being excluded by analytics filters solely due to metadata extraction failures.
