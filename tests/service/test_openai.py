
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
    This functions tests the working of the filter_relevant_articles function.
    It assumes that the open_ai will return at least one article.
    '''
    stock = 'Nvidia'
    date_from = '2025-08-20'
    date_to = '2025-08-24'
    data = get_news_articles_urls(stock, date_from, date_to)
    articles = extract_title_and_urls(data)
    filtered_aricles = filtered_articles(articles)
    result = filter_relevant_articles(filtered_aricles, api_key)
    print(f"Relevant Articles: {json.dumps(result, indent=2)}")
    assert result is not None
    assert isinstance(result, list)
    if result:  # Only check contents if the list is not empty
        assert isinstance(result[0], dict)
        assert 'source' in result[0]
        assert 'title' in result[0]
        assert 'url' in result[0]
    else:
        print("Warning: No relevant articles returned by filter_relevant_articles.")
