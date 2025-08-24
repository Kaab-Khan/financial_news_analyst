

'''
This file contains a list of trusted sources that are used to filter out
unreliable news sources. This list is used by the NewsAPI class in the
news_api.py file to filter out news articles from untrusted sources.

'''


trusted_sources = [
    # --- Core Financial & Market News ---
    "Bloomberg", "Reuters", "Financial Times", "Wall Street Journal", "CNBC",
    "Forbes", "Yahoo Finance", "MarketWatch", "Investing.com", "The Economist",
    "Barron's", "Business Insider", "TheStreet", "Seeking Alpha", "Nikkei Asia",
    "Financial Post", "Fortune", "Motley Fool", "Kiplinger", "ValueWalk",
    "TipRanks", "Zacks Investment Research", "Morningstar", "Simply Wall St",
    "Benzinga",

    # --- Major Newspapers / Broadcasters ---
    "BBC News", "The Guardian", "The New York Times", "The Washington Post",
    "The Telegraph", "The Times (UK)", "The Independent", "Politico",
    "The Hill",

    # --- Commodities, Energy & Metals ---
    "OilPrice.com", "Mining.com", "Platts (S&P Global)", "Gold.org",
    "Argus Media", "Hellenic Shipping News", "ICIS",

    # --- Technology & Business Impact ---
    "TechCrunch", "The Verge", "Wired", "Ars Technica",
    "MIT Technology Review", "VentureBeat",

    # --- Crypto / Digital Assets ---
    "CoinDesk", "Cointelegraph", "Decrypt", "CryptoSlate",
    "Bitcoin Magazine", "The Block", "Messari",

    # --- Institutions & Research ---
    "International Monetary Fund", "World Bank", "OECD",
    "Bank for International Settlements", "Federal Reserve",
    "European Central Bank", "Bank of England", "Bank of Japan"
]

