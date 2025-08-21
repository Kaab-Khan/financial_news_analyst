
import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.service.sentiment_finBERT import enrich_with_sentiment, aggregate_sentiment
from src.service.openai import filter_relevant_articles
from src.models.news_api import get_news_articles_urls, extract_title_and_urls
from src.service.pre_processing import filtered_articles
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

'''
Test cases for sentiment enrichment using FinBERT.
These tests ensure that the sentiment analysis is correctly applied to articles.'''
def test_finbert_enrichment_basic():
    arts = [
        {"title":"Tesla beats expectations", "url":"x", "source":"Reuters", "description":"Deliveries up y/y"},
        {"title":"Regulatory probe widens", "url":"y", "source":"Bloomberg", "description":"NHTSA expands review"},
    ]
    out = enrich_with_sentiment(arts)
    assert len(out)==2
    for a in out:
        assert a["sentiment_label"] in {"positive","neutral","negative"}
        assert 0.0 <= a["sentiment_conf"] <= 1.0
        assert -1.0 <= a["sentiment_score"] <= 1.0

@pytest.mark.skip(reason="Integration test - requires OpenAI API key")
def test_finbert_integration():
    '''
    This function tests the integration of filtering relevant articles and enriching them with sentiment.
    It fetches articles related to Tesla, filters them, and then applies sentiment analysis.
    '''
    stock = 'tesla'
    data = get_news_articles_urls(stock) # Fetching news articles related to Tesla
    articles = extract_title_and_urls(data) # Extracting titles and URLs from the fetched data
    filtered_aricles = filtered_articles(articles)
    arts = filter_relevant_articles(filtered_aricles,api_key)
    enriched_arts = enrich_with_sentiment(arts)
    assert len(enriched_arts) > 0
    for a in enriched_arts:
        print(f"Title: {a['title']}")
        print(f"URL: {a['url']}")
        print(f"Source: {a['source']}")
        print(f"Sentiment: {a['sentiment_label']}")
        print(f"Confidence: {a['sentiment_conf']}")
        print(f"Score: {a['sentiment_score']}")
    print(f" Number of articles: {len(enriched_arts)}")
    print("\n" * 3)

      

@pytest.mark.skip(reason="dummy test for aggregate sentiment")
def test_aggregate_sentiment_demo():
    # Fake articles with different sentiments + confidences
    ''' This function tests the aggregate sentiment calculation.
    It creates a set of articles with known sentiments and checks if the aggregation works correctly.
    IT IS A UNIT TEST, NOT AN INTEGRATION TEST.'''
    articles = [
        {"sentiment_label": "positive", "sentiment_conf": 0.9},
        {"sentiment_label": "negative", "sentiment_conf": 0.6},
        {"sentiment_label": "neutral",  "sentiment_conf": 0.8},
        {"sentiment_label": "positive", "sentiment_conf": 0.7},
    ]

    result = aggregate_sentiment(articles)

    # Print output so you can see it in pytest -s
    print("\n=== Aggregate Sentiment Test Output ===")
    print("Overall sentiment:", result["overall_tag"], f"({result['score_0_100']}/100)")
    print("Counts:", result["counts"])
    print("Weighted shares:", result["weighted_share"])

    # Assertions (basic sanity checks)
    assert 0 <= result["score_0_100"] <= 100
    assert result["overall_tag"] in ["Bullish", "Neutral", "Bearish"]
    assert result["counts"]["total"] == len(articles)

# Test the function with real data
def test_aggregate_sentiment():
    stock = 'tesla'
    data = get_news_articles_urls(stock)  # Fetching news articles related to Tesla
    articles = extract_title_and_urls(data)  # Extracting titles and URLs from the fetched data
    filtered_articles_list = filtered_articles(articles)  # Filtering articles to keep only those with trusted sources
    arts = filter_relevant_articles(filtered_articles_list, api_key)  # Filtering relevant articles
    enriched_arts = enrich_with_sentiment(arts)  # Enriching articles with sentiment analysis
    result = aggregate_sentiment(enriched_arts)  # Aggregating sentiment

    print("\n=== Aggregate Sentiment Test Output ===")
    print("Overall sentiment:", result["overall_tag"], f"({result['score_0_100']}/100)")
    print("Counts:", result["counts"])
    print("Weighted shares:", result["weighted_share"])

    assert isinstance(result, dict)
    assert "overall_tag" in result
    assert "score_0_100" in result
    assert "counts" in result
    assert "weighted_share" in result
    assert result["counts"]["total"] == len(enriched_arts)
    assert result["score_0_100"] >= 0.0 and result["score_0_100"] <= 100.0
    assert result["overall_tag"] in ["Bullish", "Neutral", "Bearish"]
    print(f"Number of articles processed: {len(enriched_arts)}")
    print("\n" * 3)
