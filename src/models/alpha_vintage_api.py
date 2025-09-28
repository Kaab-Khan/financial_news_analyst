import os 
import sys
import requests
import datetime 

ALPHA_VINTAGE_API_KEY = os.getenv("APLHA_VINTAGE_API_KEY")
ALPHA_VINTAGE_API_URL = os.getenv("ALPHA_VINTAGE_API_URL")

    
def av_symbol_search(query: str,ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY,*, region_preference=("United States", "United Kingdom", "Canada")) -> dict:
    """
    Return the best match dict from Alpha Vantage SYMBOL_SEARCH.
    Strategy: highest matchScore, preferring preferred regions if present.
    """
    params = {"function": "SYMBOL_SEARCH", "keywords": query, "apikey": ALPHA_VINTAGE_API_KEY}
    r = requests.get(ALPHA_VINTAGE_API_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    matches = data.get("bestMatches", []) or []
    if not matches:
        raise RuntimeError(f"No matches for '{query}': {data}")

    # normalize + score
    def key(m):
        score = float(m.get("9. matchScore", "0") or 0)
        region = m.get("4. region", "")
        pref_boost = 0.1 if region in region_preference else 0.0
        return (score + pref_boost, score)

    best = sorted(matches, key=key, reverse=True)[0]
    return {
        "symbol": best.get("1. symbol"),
        "name": best.get("2. name"),
        "type": best.get("3. type"),
        "region": best.get("4. region"),
        "currency": best.get("8. currency"),
        "matchScore": float(best.get("9. matchScore", "0") or 0),
        "raw": best,
    }

def av_time_series_daily(ticker: str, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY) -> dict:
    """
    Return monthly time series for ticker from Alpha Vantage TIME_SERIES_MONTHLY.
    Returns dict with keys: meta, time_series (date->data)
    """
    params = {"function": "TIME_SERIES_MONTHLY", "symbol": ticker, "apikey": ALPHA_VINTAGE_API_KEY}
    r = requests.get(ALPHA_VINTAGE_API_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if "Error Message" in data:
        raise RuntimeError(f"Error from Alpha Vantage for '{ticker}': {data['Error Message']}")
    meta = data.get("Meta Data", {})
    ts = data.get("Monthly Time Series", {}) or {}
    if not ts:
        raise RuntimeError(f"No time series data for '{ticker}': {data}")

    # Convert date strings to datetime.date and values to float
    time_series = {}
    for date_str, vals in ts.items():
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            time_series[date] = {k: float(v) for k, v in vals.items()}
        except Exception as e:
            print(f"Skipping invalid date entry '{date_str}' for '{ticker}': {e}", file=sys.stderr)

    return {"meta": meta, "Monthly Time Series": time_series}

def get_av_daily_data(ticker, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY):
    """
    Get the daily time series data for a given ticker from Alpha Vantage API.
    """
    if not ALPHA_VINTAGE_API_KEY or not ALPHA_VINTAGE_API_URL:
        raise ValueError("Alpha Vantage API key or URL not set in environment variables.")
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "apikey": ALPHA_VINTAGE_API_KEY,
    }
    response = requests.get(ALPHA_VINTAGE_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    if "Error Message" in data:
        raise RuntimeError(f"Error from Alpha Vantage for '{ticker}': {data['Error Message']}")
    if "Time Series (Daily)" not in data:
        raise RuntimeError(f"No daily time series data for '{ticker}': {data}")
    return data
    