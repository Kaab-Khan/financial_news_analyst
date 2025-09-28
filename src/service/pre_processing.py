import fuzzywuzzy
from fuzzywuzzy import process
from collections import defaultdict
from resources.trusted_sources import trusted_sources
from src.models.alpha_vintage_api import get_av_daily_data
import os
import sys


def is_trusted_source(source, threshold):
    """
    This function takes a news source as input and check if it is a
    trusted source using fuzzy matching.
    """
    # Check if the source is in the trusted sources list
    if not source or not trusted_sources:
        return False
    result = process.extractOne(source, trusted_sources)
    if result:
        match, score = result
        return score >= threshold
    return False


def filtered_articles(article_list):
    """
    This function takes a list of articles as input and filters out articles
    from untrusted sources.
    """

    if not isinstance(article_list, list):
        return []

    filtered_article_list = [
        article
        for article in article_list
        if isinstance(article, dict)
        and is_trusted_source(article.get("source", {}).get("name", ""), 0)
    ]
    return filtered_article_list
def format_av_daily_data(data):
    """
    This function takes the Alpha Vantage daily data and formats it
    to match the database schema.
    """
    formatted_data = []
    time_series = data.get("Time Series (Daily)", {})

    for date, values in time_series.items():
        formatted_entry = {
            "date": date,
            "open": float(values.get("1. open", 0)),
            "high": float(values.get("2. high", 0)),
            "low": float(values.get("3. low", 0)),
            "close": float(values.get("4. close", 0)),
            "adjusted_close": float(values.get("5. adjusted close", 0)),  # Use "5. adjusted close" if available
            "volume": int(values.get("5. volume", 0)),
        }
        formatted_data.append(formatted_entry)

    return formatted_data

import datetime
from typing import List, Dict

def filter_ohlcv_by_range(
    data: List[Dict], start_date: datetime.date, end_date: datetime.date
) -> List[Dict]:
    """
    Filters OHLCV data for the given date range [start_date, end_date].
    Expects data as a list of dicts with 'date' as YYYY-MM-DD string.
    """
    # Convert string dates in data to datetime.date
    filtered = []
    for row in data:
        row_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
        if start_date <= row_date <= end_date:
            new_row = dict(row)
            new_row["date"] = row_date
            filtered.append(new_row)

    # Sort ascending by date
    filtered.sort(key=lambda x: x["date"])
    return filtered


def aggregate_price_change(filtered_data: List[Dict]) -> Dict:
    """
    Aggregates filtered OHLCV data to show price change over the period.
    Returns start price, end price, and percentage change.
    """
    if not filtered_data:
        return {"start_price": None, "end_price": None, "percent_change": None}

    start_price = filtered_data[0]["close"]
    end_price = filtered_data[-1]["close"]

    percent_change = ((end_price - start_price) / start_price) * 100

    return {
        "start_date": filtered_data[0]["date"],
        "end_date": filtered_data[-1]["date"],
        "start_price": start_price,
        "end_price": end_price,
        "percent_change": round(percent_change, 2),
    }
