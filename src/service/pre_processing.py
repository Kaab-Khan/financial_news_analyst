from fuzzywuzzy import process
from resources.trusted_sources import trusted_sources
from datetime import datetime
from typing import List, Dict


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
            "date": datetime.strptime(
                date, "%Y-%m-%d"
            ).date(),  # Convert date to datetime.date
            "open": float(values.get("1. open", 0)),
            "high": float(values.get("2. high", 0)),
            "low": float(values.get("3. low", 0)),
            "close": float(values.get("4. close", 0)),
            "adjusted_close": float(
                values.get("5. adjusted close", 0)
            ),  # Use "5. adjusted close" if available
            "volume": int(values.get("5. volume", 0)),
        }
        formatted_data.append(formatted_entry)

    return formatted_data


def filter_ohlcv_by_range(data: List[Dict], start_date, end_date) -> List[Dict]:
    """
    Filters OHLCV data for the given date range [start_date, end_date].
    If no data is available for the range, returns the nearest available data.
    """
    # Convert string dates in data to datetime.date
    filtered = []
    for row in data:
        if isinstance(row["date"], str):
            row_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
        else:
            row_date = row["date"]
        if start_date <= row_date <= end_date:
            new_row = dict(row)
            new_row["date"] = row_date
            filtered.append(new_row)

    # Sort ascending by date
    filtered.sort(key=lambda x: x["date"], reverse=True)

    # If filtered data is empty, find the nearest available data
    if not filtered:
        # Sort the data by date to find the nearest dates
        data.sort(key=lambda x: x["date"])
        nearest_before = None
        nearest_after = None

        for row in data:
            row_date = row["date"]
            if row_date < start_date:
                nearest_before = row
            elif row_date > end_date and nearest_after is None:
                nearest_after = row
                break

        # Create a failsafe response with the nearest available data
        failsafe_data = []
        if nearest_before:
            failsafe_data.append(
                {
                    "date": nearest_before["date"],
                    "open": nearest_before["open"],
                    "high": nearest_before["high"],
                    "low": nearest_before["low"],
                    "close": nearest_before["close"],
                    "adjusted_close": nearest_before["adjusted_close"],
                    "volume": nearest_before["volume"],
                }
            )
        if nearest_after:
            failsafe_data.append(
                {
                    "date": nearest_after["date"],
                    "open": nearest_after["open"],
                    "high": nearest_after["high"],
                    "low": nearest_after["low"],
                    "close": nearest_after["close"],
                    "adjusted_close": nearest_after["adjusted_close"],
                    "volume": nearest_after["volume"],
                }
            )
        return failsafe_data

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
        "percentage_change": round(percent_change, 2),
    }
