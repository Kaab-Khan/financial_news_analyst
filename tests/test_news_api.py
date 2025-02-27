import os 
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.models.news_api import get_news_articles_urls, extract_title_and_urls, print_news_articles
# The function takes in a stock name as a parameter and returns the news articles related to the stock name
def test_get_news_articles_urls():
    assert get_news_articles_urls('tesla')  is not None

# This function test the get_news_articles_urls function from the news_api.py file
def test_extract_title_and_urls():
    data = get_news_articles_urls('tesla')
    assert extract_title_and_urls(data) is not None
    assert extract_title_and_urls(data)[0]['title'] is not None
    assert extract_title_and_urls(data)[0]['source'] is not None
    assert extract_title_and_urls(data)[0]['url'] is not None
    assert extract_title_and_urls(data)[0]['description'] is not None
def test_print_news_articles():
    assert print_news_articles('tesla') is None
    
