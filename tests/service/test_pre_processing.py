import os 
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.service.pre_processing import is_trusted_source, filtered_articles
from src.models.news_api import extract_title_and_urls, get_news_articles_urls
from src.service.pre_processing import format_av_time_series_data
from src.models.alpha_vintage_api import av_time_series_daily
from dotenv import load_dotenv
load_dotenv()
ALPHA_VINTAGE_API_KEY = os.getenv("ALPHA_VINTAGE_API_KEY")
ALPHA_VINTAGE_API_URL = os.getenv("ALPHA_VINTAGE_API_URL")

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

def test_format_av_time_series_data():
    # The data should get from Alpha Vantage API
    ticker = "AAPL"
    data = av_time_series_daily(ticker, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)
    formatted_data = format_av_time_series_data(data)
    print(formatted_data)
    # The function should return data formatted by date wise
    assert isinstance(formatted_data, list)
    assert isinstance(formatted_data[0], dict)
    assert 'date' in formatted_data[0]
    assert '1. open' in formatted_data[0]
    assert '2. high' in formatted_data[0]
    assert '3. low' in formatted_data[0]
    assert '4. close' in formatted_data[0]
