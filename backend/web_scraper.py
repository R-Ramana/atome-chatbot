import requests
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

def chunk_text(text, size=500):
    return [text[i:i + size] for i in range(0, len(text), size)]

def is_valid_chunk(chunk):
    return len(chunk.strip()) > 50

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def add_to_kb(data, article_list):
    chunks = chunk_text(data)
    article_list.extend([c for c in chunks if is_valid_chunk(c)])


def build_api_url(url):
    """
    Convert a Zendesk help center URL into its API endpoint.
    """

    parsed = urlparse(url)

    base = f"{parsed.scheme}://{parsed.netloc}"

    # detect locale (e.g. /en-gb/)
    parts = parsed.path.split("/")
    locale = "en-gb"

    for p in parts:
        if "-" in p:  # crude but works for locales like en-gb
            locale = p
            break

    return f"{base}/api/v2/help_center/{locale}/articles.json"

def scrape(url=None):
    if url:
        api_url = build_api_url(url)
    else:
        api_url = "https://help.atome.ph/api/v2/help_center/en-gb/articles.json"

    articles = []
    page = 1

    while True:
        if "api/v2/help_center" in api_url:
            r = requests.get(f"{api_url}?page={page}", headers=HEADERS)
            data = r.json()

            for article in data["articles"]:
                content = article["body"]
                if content:
                    cleaned_data = clean_html(content)
                    add_to_kb(cleaned_data, articles)
                    
            if data["next_page"] is None:
                break

            page += 1
        
        else:
            r = requests.get(api_url, headers=HEADERS)
            r.raise_for_status()
            cleaned_data = clean_html(r.text)
            if cleaned:
                add_to_kb(cleaned_data, articles)
            break
        
    print("Fetched articles:", len(articles))
    return articles

def scrape_kb(url):
    print("Scraping KB:", url)
    return scrape(url)