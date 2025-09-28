import os 
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.service.pre_processing import is_trusted_source, filtered_articles, format_av_daily_data
from src.models.news_api import extract_title_and_urls, get_news_articles_urls

def test_is_trusted_source():
    # The data should be fed into extact_title_and_urls function
    stock = 'tesla'
    data = get_news_articles_urls(stock)
    articles = extract_title_and_urls(data)
    # The function should return a boolean value
    assert is_trusted_source(articles[0]['source']['name'], 85) == True

def test_filtered_articles():
    stock = 'tesla'
    data = get_news_articles_urls(stock)
    articles = extract_title_and_urls(data)
    # The function should return a list of articles
    filtered_aricles = filtered_articles(articles)
    assert filtered_articles(articles) is not None
    assert isinstance(filtered_articles(articles), list)
    assert isinstance(filtered_articles(articles)[0], dict)
    assert 'source' in filtered_articles(articles)[0]
    assert 'title' in filtered_articles(articles)[0]
    assert 'url' in filtered_articles(articles)[0]
    assert 'description' in filtered_articles(articles)[0]
    assert 'source' in filtered_articles(articles)[0]
    assert 'source' in filtered_articles(articles)[0]
    assert 'source' in filtered_articles(articles)[0]
    assert 'source' in filtered_articles(articles)[0]
    # The function should return a list of articles with trusted sources

def test_av_daily_data_formatting():
    '''Test the format_av_daily_data function
    The function should return a list of dictionaries with the correct keys and value types
    This is a mock test with sample data'''
    from src.service.pre_processing import format_av_daily_data
    sample_data = [
        {
            "date": "2023-10-01",
            "open": "150.0",
            "high": "155.0",
            "low": "149.0",
            "close": "154.0",
            "adjusted_close": "154.0",
            "volume": "1000000"
        },
        {
            "date": "2023-10-02",
            "open": "152.0",
            "high": "156.0",
            "low": "151.0",
            "close": "155.0",
            "adjusted_close": "155.0",
            "volume": "1100000"
        }
    ]
    formatted_data = format_av_daily_data(sample_data)
    assert isinstance(formatted_data, list)
    assert len(formatted_data) == 2
    for entry in formatted_data:
        assert isinstance(entry, dict)
        assert 'date' in entry
        assert isinstance(entry['open'], float)
        assert isinstance(entry['high'], float)
        assert isinstance(entry['low'], float)
        assert isinstance(entry['close'], float)
        assert isinstance(entry['adjusted_close'], float)
        assert isinstance(entry['volume'], int)

def test_format_av_daily_data_on_live_data():
    '''Test the format_av_daily_data function on live data from Alpha Vantage API'''
    from src.models.alpha_vintage_api import get_av_daily_adjusted
    from src.config.api_config import ALPHA_VINTAGE_API_KEY, ALPHA_VINTAGE_API_URL
    stock = 'AAPL'
    data = get_av_daily_adjusted(stock, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)
    formatted_data = format_av_daily_data(data)
    assert isinstance(formatted_data, list)
    assert len(formatted_data) > 0
    for entry in formatted_data:
        assert isinstance(entry, dict)
        assert 'date' in entry
        assert isinstance(entry['open'], float)
        assert isinstance(entry['high'], float)
        assert isinstance(entry['low'], float)
        assert isinstance(entry['close'], float)
        assert isinstance(entry['adjusted_close'], float)
        assert isinstance(entry['volume'], int)