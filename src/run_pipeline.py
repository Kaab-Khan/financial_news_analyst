# src/pipeline/run_pipeline.py
"""
End-to-end pipeline (simple, title+description only).
Input: a plain company name string (e.g., "Tesla").
Flow:
  fetch -> extract -> normalize -> trusted filter -> OpenAI relevance -> FinBERT -> aggregate (0..100)
"""

from __future__ import annotations
import os
from typing import Dict, Any, List

# --- your modules (adjust paths if needed) ---
from src.models.news_api import get_news_articles_urls
# Support either extractor name you used
try:
    from src.models.news_api import extract_title_url_content as extract_titles
except Exception:
    from src.models.news_api import extract_title_and_urls as extract_titles

from src.service.pre_processing import filtered_articles              # your trusted filter
from src.service.openai import filter_relevant_articles              # your OpenAI filter
     # FinBERT title+desc
from src.service.sentiment_finBERT import enrich_with_sentiment     # FinBERT enrich
from src.service.sentiment_finBERT import aggregate_sentiment      # 0..100 aggregator


def run_pipeline(company_name: str) -> Dict[str, Any]:
    """
    Run the full pipeline for a company name and return a structured dict:
      {
        "query": company_name,
        "count": <int>,
        "articles": [ {title, description, url, source, sentiment_*}, ... ],
        "aggregate": { score_0_100, overall_tag, counts, weighted_share }
      }
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set. `export OPENAI_API_KEY=...`")

    # 1) Fetch raw (by company name)
    raw = get_news_articles_urls(company_name)

    # 2) Extract minimal fields from NewsAPI response
    extracted = extract_titles(raw)

    # 3) Normalize (keep only title/description/url/source/domain/published_at if present)

    # 4) Trusted-source filter (your domain/source pass)
    trusted = filtered_articles(extracted)

    # 5) OpenAI relevance filter — keep only investment-relevant items
    final_articles: List[Dict[str, Any]] = filter_relevant_articles(trusted, api_key)

    # # 6) FinBERT sentiment on title+description
    # for a in final_articles:
    #     s = label_to_signed(a.get("title", ""), a.get("description", ""))
    #     a["sentiment_label"] = s["label"]
    #     a["sentiment_conf"] = s["confidence"]

    # 7) Aggregate to a 0..100 score + tag
    enriched_articles = enrich_with_sentiment(final_articles)
    agg = aggregate_sentiment(enriched_articles)

    return {
        "query": company_name,
        "count": len(final_articles),
        "articles": final_articles,   # main.py decides whether to print all
        "aggregate": agg,
    }
