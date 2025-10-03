# 📰 Financial News Analyst

A Streamlit app + Python pipeline that:
- fetches recent news by **company name**
- filters to **investment-relevant** items (OpenAI)
- runs **FinBERT** sentiment on title + description
- fetches **stock prices** for the same window from **Alpha Vantage**
- aggregates everything into a **0–100** sentiment score with a tag

---

## Project Structure

.
├─ Makefile
├─ logging_config.py
├─ resources/
│ └─ schema.sql
├─ src/
│ ├─ agent/
│ │ ├─ stock_pipeline.py
│ │ └─ us_resolver.py
│ ├─ config/
│ │ └─ db_config.py
│ ├─ models/
│ │ ├─ alpha_vintage_api.py
│ │ ├─ news_api.py
│ │ └─ scrapper.py
│ ├─ pipeline/
│ │ ├─ price_pipeline.py
│ │ └─ run_pipeline.py
│ ├─ repository/
│ │ └─ stock_prices.py
│ └─ service/
│ ├─ openai.py
│ ├─ pre_processing.py
│ ├─ sentiment_finBERT.py
│ └─ store_faiss.py
├─ streamlit_app.py
└─ tests/
├─ models/
├─ pipeline/
├─ repository/
└─ service/


## Quick Start

### 1) Requirements
- Python 3.10+
- Virtual environment recommended

### 2) Install
```bash
pip install -r requirements-dev.txt
3) Local Environment (.env)
Create a .env at the repo root:

.env
OPENAI_API_KEY=sk-...
ALPHA_VINTAGE_API_KEY=YOUR_ALPHA_VANTAGE_KEY
# IMPORTANT: no trailing "?"
ALPHA_VINTAGE_API_URL=https://www.alphavantage.co/query

4) Run the App
bash
streamlit run streamlit_app.py --logger.level=info
Programmatic Use

from src.pipeline.run_pipeline import run_pipeline

# date_from/date_to are optional (date or datetime); 31-day max window enforced
res = run_pipeline(
    "Tesla",
    # date_from=date(2025, 9, 1),
    # date_to=date(2025, 10, 1),
    openai_api_key="sk-..."  # or rely on env var
)

print(res["aggregate"])     # {score_0_100, overall_tag, ...}
print(res["price_change"])  # {first_day, last_day, first_price, last_price, percentage_change}
Deploying on Streamlit Cloud
Create .streamlit/secrets.toml (TOML requires quotes):

toml

OPENAI_API_KEY = "sk-..."
ALPHA_VINTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_KEY"
ALPHA_VINTAGE_API_URL = "https://www.alphavantage.co/query"
In code, these are read as environment variables at runtime.

Dev Workflow
Format + lint:

bash

make quality
Run tests:

bash

pytest -q
Recommended .flake8 to align with Black:

ini

[flake8]
extend-ignore = E203,E501,W503

Common Issues & Fixes
ValueError: Alpha Vantage API key or URL not set

Ensure both are present. URL must be exactly https://www.alphavantage.co/query (no ?).

Streamlit “Invalid TOML” in Secrets

TOML must be key = "value" (quotes required).

Same price for different companies

Confirm symbol resolution → pass the resolved ticker to Alpha Vantage.

The app logs Resolved ticker: and Alpha Vantage symbol—check they match.

TypeError: Object of type date is not JSON serializable

When exporting, use json.dumps(obj, default=str) or convert dates to ISO strings.

Streamlit deprecation

Replace use_container_width=True with width="stretch" (or "content").

Notes
The news fetcher limits windows to the past 31 days.

The relevance filter uses OpenAI; set OPENAI_API_KEY.

Alpha Vantage has rate limits; code includes small delays between calls.