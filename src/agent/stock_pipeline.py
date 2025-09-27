from agent.us_resolver import resolve_us_ticker_basic
from models.alpha_vintage_api import av_symbol_search
from typing import Optional, Dict
import os, sys

query = "Apple"
ALPHA_VINTAGE_API_KEY = os.getenv("ALPHA_VINTAGE_API_KEY")
ALPHA_VINTAGE_API_URL = os.getenv("ALPHA_VINTAGE_API_URL")

def av_ticker_lookup(query: str) -> Optional[Dict]:
    """
    First resolve the ticker using US resolver.
    then go to Alpha Vantage to get more details.
    Lookup ticker using Alpha Vantage API.
    Returns dict with keys: symbol, name, type, region, currency, matchScore, raw
    or None if no good match.
    """
    if not ALPHA_VINTAGE_API_KEY or not ALPHA_VINTAGE_API_URL:
        print("Alpha Vantage API key or URL not set in environment variables.", file=sys.stderr)
        return None
        # First try to resolve using US resolver
    us_res = resolve_us_ticker_basic(query)
    if us_res:
        query = us_res["ticker"]
        # Now query Alpha Vantage
    try:
        result = av_symbol_search(query, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)
        if result["matchScore"] >= 0.5:
            return result
        else:
            return None
    except Exception as e:
        print(f"Error during Alpha Vantage lookup for '{query}': {e}", file=sys.stderr)
        return None