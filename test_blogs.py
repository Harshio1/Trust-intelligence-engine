import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.healthline.com/nutrition/gut-microbiome-and-health",
    "https://my.clevelandclinic.org/health/body/25201-gut-microbiome",
    "https://theconversation.com/a-healthy-gut-microbiome-is-linked-to-a-longer-life-156382"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in urls:
    try:
        print(f"Testing: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Content length: {len(response.content)}")
        else:
            print(f"FAILED with status: {response.status_code}")
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
    print("-" * 20)
