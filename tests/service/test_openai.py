
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.service.openai import filter_relevant_articles
from src.models.news_api import get_news_articles_urls, extract_title_and_urls
from src.service.pre_processing import filtered_articles
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def test_filter_relevant_articles():
    '''
    This functions tests the working of the filter_relevant_articles function
    '''
    stock = 'tesla'
    data = get_news_articles_urls(stock)
    articles = extract_title_and_urls(data)
    filtered_aricles = filtered_articles(articles)
    print(f"Filtered Articles: {json.dumps(filtered_aricles, indent=2)}")
    # The function should return a list of articles with trusted sources
    assert filter_relevant_articles(filtered_aricles,api_key) is not None
    assert isinstance(filter_relevant_articles(filtered_aricles,api_key), list)
    assert isinstance(filter_relevant_articles(filtered_aricles,api_key)[0], dict)
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'title' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'url' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
    assert 'source' in filter_relevant_articles(filtered_aricles,api_key)[0]
