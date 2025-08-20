import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from src.models.scrapper import scrape_full_articles

# Test with an invalid URL
def test_scrape_full_articles_invalid_url():
    url = 'invalid_url'
    assert scrape_full_articles(url) is None

# Test with a valid URL
def test_scrape_full_articles():
    url = 'https://www.bbc.com/news/business' # give a url for only one article
    # Ensure the URL is valid and the function returns a non-empty string
    assert scrape_full_articles(url) is not None
    assert isinstance(scrape_full_articles(url), str)
    assert len(scrape_full_articles(url)) > 0
    