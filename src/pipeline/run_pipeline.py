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
import datetime as dt
from typing import Optional

# --- your modules (adjust paths if needed) ---
from src.models.news_api import get_news_articles_urls
# Support either extractor name you used
try:
    from src.models.news_api import extract_title_url_content as extract_titles, normalize_minimal
except Exception:
    from src.models.news_api import extract_title_and_urls as extract_titles, normalize_minimal

from src.service.pre_processing import filtered_articles              # your trusted filter
from src.service.openai import filter_relevant_articles              # your OpenAI filter
     # FinBERT title+desc
from src.service.sentiment_finBERT import enrich_with_sentiment     # FinBERT enrich
from src.service.sentiment_finBERT import aggregate_sentiment      # 0..100 aggregator
def _to_datestr(d):
    # Accepts datetime.date, datetime.datetime, or already-a-string
    if d is None:
        return None
    if isinstance(d, (dt.date, dt.datetime)):
        return d.strftime("%Y-%m-%d")  # <- forces date-only
    # if it's a string like '2025-08-23T00:00:00', trim to 'YYYY-MM-DD'
    s = str(d).strip()
    return s[:10]  # defensive: first 10 chars are YYYY-MM-DD

def _clip_dates(date_from: dt.date, date_to: dt.date) -> tuple[dt.date, dt.date]:
    """Ensure window is within the last 31 days and not inverted."""
    today = dt.date.today()
    max_lookback = today - dt.timedelta(days=31)
    if date_from < max_lookback:
        date_from = max_lookback
    if date_to > today:
        date_to = today
    if date_from > date_to:
        date_from = date_to
    return date_from, date_to

def _parse_published_at(value) -> Optional[dt.datetime]:
    """Best-effort parse string/naive datetime -> naive datetime (UTC-ish)."""
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=None)
    try:
        s = str(value).replace("Z", "+00:00")
        return dt.datetime.fromisoformat(s).replace(tzinfo=None)
    except Exception:
        return None

def _within_range(art: dict, dfrom: dt.date, dto: dt.date) -> bool:
    pub = _parse_published_at(art.get("published_at"))
    if not pub:
        return True  # keep if unknown date
    d = pub.date()
    return (dfrom <= d <= dto)

def run_pipeline(
    company_name: str,
    date_from: Optional[dt.date] = None,
    date_to: Optional[dt.date] = None,
    *,
    openai_api_key: str | None = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline for a company name within an optional date range (max 31 days).

    Args:
      company_name: e.g., "Tesla"
      date_from:    date object (inclusive)
      date_to:      date object (inclusive)

    Returns:
      {
        "query": str,
        "date_from": "YYYY-MM-DD" | None,
        "date_to":   "YYYY-MM-DD" | None,
        "count": int,
        "articles": [...],
        "aggregate": {...}
      }
    """
#    api_key = os.getenv("OPENAI_API_KEY")
    # if not api_key:
    #     raise RuntimeError("OPENAI_API_KEY not set. `export OPENAI_API_KEY=...`")

    # Normalize/clip dates (max 31 days)
    if date_from and date_to:
        date_from, date_to = _clip_dates(date_from, date_to)

    # 1) Fetch raw (prefer passing dates to your fetcher if it supports them)
    try:
        if date_from and date_to:
            raw = get_news_articles_urls(
                company_name.strip(),
                date_from=_to_datestr(date_from),
                date_to=_to_datestr(date_to),
            )
        else:
            raw = get_news_articles_urls(company_name)
    except TypeError:
        # Your fetcher doesn't accept date params; fall back to no-date fetch
        raw = get_news_articles_urls(company_name)

    # 2) Extract minimal fields
    extracted = extract_titles(raw)

    # 3) Normalize
    #rows = normalize_minimal(extracted)

    # 3b) Local filter by date range if needed
    if date_from and date_to:
        rows = [r for r in extracted if _within_range(r, date_from, date_to)]

    # 4) Trusted-source filter
    trusted = filtered_articles(rows)

    # 5) LLM relevance (OpenAI) — keep only relevant
    final_articles: List[Dict[str, Any]] = filter_relevant_articles(trusted, api_key=openai_api_key)


  # 6- FinBET Sentiment
    enriched_articles = enrich_with_sentiment(final_articles)
  # 7- Aggregate to a 0..100 score + tag

    agg = aggregate_sentiment(enriched_articles)

    return {
        "query": company_name,
        "date_from": date_from.isoformat() if date_from else None,
        "date_to": date_to.isoformat() if date_to else None,
        "count": len(final_articles),
        "articles": final_articles,
        "aggregate": agg,
    }

# def run_pipeline(company_name: str) -> Dict[str, Any]:
#     """
#     Run the full pipeline for a company name and return a structured dict:
#       {
#         "query": company_name,
#         "count": <int>,
#         "articles": [ {title, description, url, source, sentiment_*}, ... ],
#         "aggregate": { score_0_100, overall_tag, counts, weighted_share }
#       }
#     """
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         raise RuntimeError("OPENAI_API_KEY not set. `export OPENAI_API_KEY=...`")

#     # 1) Fetch raw (by company name)
#     raw = get_news_articles_urls(company_name)

#     # 2) Extract minimal fields from NewsAPI response
#     extracted = extract_titles(raw)

#     # 3) Normalize (keep only title/description/url/source/domain/published_at if present)

#     # 4) Trusted-source filter (your domain/source pass)
#     trusted = filtered_articles(extracted)

#     # 5) OpenAI relevance filter — keep only investment-relevant items
#     final_articles: List[Dict[str, Any]] = filter_relevant_articles(trusted, api_key)

#     # # 6) FinBERT sentiment on title+description
#     # for a in final_articles:
#     #     s = label_to_signed(a.get("title", ""), a.get("description", ""))
#     #     a["sentiment_label"] = s["label"]
#     #     a["sentiment_conf"] = s["confidence"]

#     # 7) Aggregate to a 0..100 score + tag
#     enriched_articles = enrich_with_sentiment(final_articles)
#     agg = aggregate_sentiment(enriched_articles)

#     return {
#         "query": company_name,
#         "count": len(final_articles),
#         "articles": final_articles,   # main.py decides whether to print all
#         "aggregate": agg,
#     }
