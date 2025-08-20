from src.service.sentiment_finBERT import enrich_with_sentiment

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
