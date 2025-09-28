import fuzzywuzzy
from fuzzywuzzy import process
from collections import defaultdict
from resources.trusted_sources import trusted_sources
from src.models.alpha_vintage_api import av_time_series_daily


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
    This function takes a list of dictionaries as input and formats the data
    to match the database schema.
    """
    formatted_data = []
    for entry in data:
        formatted_entry = {
            "date": entry.get("date"),
            "open": float(entry.get("open", 0)),
            "high": float(entry.get("high", 0)),
            "low": float(entry.get("low", 0)),
            "close": float(entry.get("close", 0)),
            "adjusted_close": float(entry.get("adjusted_close", 0)),
            "volume": int(entry.get("volume", 0)),
        }
        formatted_data.append(formatted_entry)
    return formatted_data

def format_av_time_series_data(data):
    """
    Format the 'Monthly Time Series' data into a date-wise structure.
    """
    if "Monthly Time Series" not in data:
        raise ValueError("The data does not contain 'Monthly Time Series'.")

    # Extract the time series data
    av_monthlay_data = data["Monthly Time Series"]

    # Create a list of rows with date and corresponding values
    formatted_av_data = []
    for date, values in av_monthlay_data.items():
        row = {"date": date}
        row.update(values)
        formatted_av_data.append(row)

    return formatted_av_data