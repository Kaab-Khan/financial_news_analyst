import os 
import sys
import requests
import datetime 

# ALPHA_VINTAGE_API_KEY = os.getenv("APLHA_VINTAGE_API_KEY")
# ALPHA_VINTAGE_API_URL = os.getenv("ALPHA_VINTAGE_API_URL")

    
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

