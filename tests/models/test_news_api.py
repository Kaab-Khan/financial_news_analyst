import os 
import sys
import pytest

#sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from src.models.news_api import get_news_articles_urls, extract_title_and_urls, print_news_articles
# The function takes in a stock name as a parameter and returns the news articles related to the stock name
def test_get_news_articles_urls():
    assert get_news_articles_urls('tesla')  is not None

# This function test the get_news_articles_urls function from the news_api.py file
def test_extract_title_and_urls():
    # give the stock name and dates as input parameters
    stock = 'Nvidia'
    date_from = '2025-08-20'
    date_to = '2025-08-24'
    data = get_news_articles_urls(stock,date_from,date_to)
    # data = get_news_articles_urls('tesla')
    assert extract_title_and_urls(data) is not None
    assert extract_title_and_urls(data)[0]['title'] is not None
    assert extract_title_and_urls(data)[0]['source'] is not None
    assert extract_title_and_urls(data)[0]['url'] is not None
    assert extract_title_and_urls(data)[0]['description'] is not None

def test_print_news_articles():
    assert print_news_articles('Nvidia') is None

def test_nomalize_minimal():
    from src.models.news_api import normalize_minimal
    sample_data = [
        {"title": "Sample Title", "source": "Sample Source", "url": "http://example.com", "description": "Sample Description", "extra_field": "Should be removed"},
        {"title": "Another Title", "source": "Another Source", "url": "http://example2.com"}  # Missing description
    ]
    normalized = normalize_minimal(sample_data)
    assert len(normalized) == 2
    assert all("title" in article for article in normalized)
    assert all("source" in article for article in normalized)
    assert all("url" in article for article in normalized)
    assert all("description" in article for article in normalized)
    assert normalized[0]["description"] == "Sample Description"
    assert normalized[1]["description"] == ""  # Default for missing description
    assert all("extra_field" not in article for article in normalized)  # Extra fields should be removed
    
