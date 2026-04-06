import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.healthline.com/nutrition/gut-microbiome-and-health",
    "https://my.clevelandclinic.org/health/body/25201-gut-microbiome"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in urls:
    try:
        print(f"Testing: {url}")
        # Increasing timeout to 20 for these sites
        response = requests.get(url, headers=headers, timeout=20)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        article_body = soup.find('article') or soup.find('main') or soup.body
        if not article_body:
            print("FAILED to find article body!")
            continue
            
        paragraphs = article_body.find_all(['p', 'h2', 'h3'])
        full_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        print(f"Text length: {len(full_text)}")
        if len(full_text) < 500:
            print("WARNING: Very short text extraction. Likely JS-blocked or structure change.")
            
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
    print("-" * 20)
