import os
import sys
from datetime import datetime
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "fdac2281006a456d88ae4acccd2490eb")
NEWS_API_URL = os.getenv("NEWS_API_URL", "https://newsapi.org/v2/everything")


def get_news_articles_urls(
    query: str,
    date_from: str | None = None,
    date_to: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
):
    """
    Fetch raw NewsAPI response for a company name (query).
    date_from/date_to should be ISO 'YYYY-MM-DD' if provided.
    """
    key = api_key or NEWS_API_KEY
    if not key:
        raise RuntimeError("NEWS_API_KEY not set. export NEWS_API_KEY=...")

    url = base_url or NEWS_API_URL or "https://newsapi.org/v2/everything"

    params = {
        "q": (query or "").strip(),
        "apiKey": key,
        "sortBy": "popularity",
        "language": "en",
    }
    if date_from:
        params["from"] = str(date_from)[:10]
    if date_to:
        params["to"] = str(date_to)[:10]

    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        raise RuntimeError(f"NewsAPI request failed: {e}")

    if resp.status_code != 200:
        snippet = resp.text[:300].replace("\n", " ")
        raise RuntimeError(f"NewsAPI HTTP {resp.status_code}. Body: {snippet}")

    try:
        data = resp.json()
    except ValueError:
        snippet = resp.text[:300].replace("\n", " ")
        raise RuntimeError(f"NewsAPI returned non-JSON response. Body: {snippet}")

    if data.get("status") != "ok":
        raise RuntimeError(f"NewsAPI error: {data}")

    return data


def extract_title_url_content(data):
    articles = data["articles"]
    title_url_content = []
    for article in articles:
        title = article.get("title", "No title available")
        source = article.get("source", "No source available")
        url = article.get("url", "No url available")
        description = article.get("description", "No description available")
        content = article.get("content", "No content available")
        title_url_content.append(
            {
                "title": title,
                "source": source,
                "url": url,
                "description": description,
                "content": content,
            }
        )

    return title_url_content


def print_news_articles(stock_name):
    data = get_news_articles_urls(stock_name)
    title_url_content = extract_title_url_content(data)
    for article in title_url_content:
        print(f'title: {article["title"]}')
        print(f'source: {article["source"]}')
        print(f'url: {article["url"]}')
        print(f'description: {article["description"]}')
        print(f'content: {article["content"]}')
        print("\n" * 2)
    print(f"Total articles found: {len(title_url_content)}")
    print(f"Data fetched at: {datetime.now().strftime('%Y-%m-%d) %H:%M:%S')}")
    print("\n" * 5)
    return


def normalize_minimal(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize NewsAPI articles into a minimal consistent schema.

    Keeps:
      - title
      - description
      - url
      - source (string only, extracts "name" if dict)
      - domain (parsed from URL, handy for trusted-source filtering)
      - published_at (if available)
    """
    out = []
    for r in rows:
        # title / description
        title = (r.get("title") or "").strip()
        desc = (r.get("description") or "").strip()

        # url
        url = r.get("url") or ""

        # source
        src = r.get("source")
        if isinstance(src, dict):
            source_name = src.get("name", "")
        else:
            source_name = str(src or "")

        # domain (parsed from URL)
        domain = ""
        if url:
            try:
                domain = urlparse(url).netloc.lower()
                # clean common prefixes
                for pref in ("www.", "m.", "amp."):
                    if domain.startswith(pref):
                        domain = domain[len(pref) :]
            except Exception:
                pass

        # publishedAt / published_at
        published_at = r.get("publishedAt") or r.get("published_at") or None
        out.append(
            {
                "title": title,
                "description": desc,
                "url": url,
                "source": source_name,
                "domain": domain,
                "published_at": published_at,
            }
        )
    return out
