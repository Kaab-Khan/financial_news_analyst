from src.models.scrapper import scrape_full_articles
import pytest

def test_scrape_full_articles():
    url = 'https://www.bbc.com/news/business-58643403'
    assert scrape_full_articles(url) is not None
    assert isinstance(scrape_full_articles(url), str)
    assert len(scrape_full_articles(url)) > 0
    