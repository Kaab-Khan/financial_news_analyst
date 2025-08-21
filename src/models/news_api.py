import os
import sys
from newsapi import NewsApiClient
from datetime import datetime
import requests
import json
import dotenv
from dotenv import load_dotenv

load_dotenv()

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)


NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = os.getenv("NEWS_API_URL")


def get_news_articles_urls(stock_name):
    URL = f"{NEWS_API_URL}q={stock_name}&from=2025-08-15&sortBy=relevance&apiKey={NEWS_API_KEY}"
    response = requests.get(URL)
    data = response.json()
    print(data)
    return data


def extract_title_and_urls(data):
    articles = data["articles"]
    title_and_urls = []
    for article in articles:
        title = article.get("title", "No title available")
        source = article.get("source", "No source available")
        url = article.get("url", "No url available")
        description = article.get("description", "No description available")
        title_and_urls.append(
            {"title": title, "source": source, "url": url, "description": description}
        )

    return title_and_urls

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
            {"title": title, "source": source, "url": url, "description": description, "content": content}
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
