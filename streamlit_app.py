import os
import json
import datetime as dt
import streamlit as st
from logging_config import logger
import logging

# Set the logging level for your application
logging.basicConfig(level=logging.INFO)  # Change DEBUG to INFO or WARNING for less verbosity

# Suppress logs from noisy libraries
logging.getLogger("watchdog").setLevel(logging.WARNING)  # Suppress inotify events
logging.getLogger("streamlit").setLevel(logging.WARNING)  # Suppress Streamlit logs
logging.getLogger("urllib3").setLevel(logging.WARNING)    # Suppress urllib3 logs

# Your custom logger
from logging_config import logger
logger.setLevel(logging.DEBUG)  # Keep DEBUG for your application-specific logs
# your pipeline

from src.pipeline.run_pipeline import run_pipeline
from src.service.pre_processing import aggregate_price_change

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VINTAGE_API_KEY = os.getenv("ALPHA_VINTAGE_API_KEY")

# -------------------------
# page config
# -------------------------
st.set_page_config(
    page_title="News Sentiment (Title+Description)",
    page_icon="📰",
    layout="wide",
)

# minimal styles (optional)
st.markdown("""
<style>
.small { font-size: 0.9rem; color: #666; }
.code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace }
.badge {
  display:inline-block; padding:0.25rem 0.6rem; border-radius: 999px;
  background:#eee; margin-left:0.5rem; font-size:0.85rem;
}
.bullish { background:#e6ffed; color:#047857; }
.bearish { background:#ffecec; color:#b91c1c; }
.neutral { background:#eef2ff; color:#3730a3; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# header
# -------------------------
st.title("📰 Financial News Sentiment")
st.caption("Fetches news by company name → filters for investment relevance → FinBERT on title+description → aggregates to a 0–100 sentiment." \
"Stok prices over the same period are fetched from Alpha Vantage.")

# -------------------------
# sidebar controls
# -------------------------
with st.sidebar:
    st.header("🔑 API Settings")
    user_openai_key = st.text_input(
        "Enter your OpenAI API key", 
        type="password", 
        help="Your key is only used for this session and not stored."
    )

    if user_openai_key:
        OPENAI_API_KEY = user_openai_key.strip()
    else:
        st.warning("⚠️ Please enter your own OpenAI API key in the sidebar to run live analysis.")
        st.stop()

    default_query = st.session_state.get("default_query", "Enter a stock name")
    query = st.text_input("Company name", value=default_query, placeholder="e.g., Tesla, Apple, NVIDIA")
    st.caption("Please write the full company name")
    st.session_state["default_query"] = query

    today = dt.date.today()
    max_lookback = today - dt.timedelta(days=31)

    st.subheader("Date range (max 31 days)")
    col_a, col_b = st.columns(2)
    with col_a:
        date_from = st.date_input("From", value=max_lookback, min_value=max_lookback, max_value=today)
    with col_b:
        date_to = st.date_input("To", value=today, min_value=max_lookback, max_value=today)

    if (date_to - date_from).days > 31:
        st.warning("Range exceeds 31 days. It will be clipped to the last 31 days.")

    run_btn = st.button("Run", type="primary", use_container_width=True)

# -------------------------
# helpers
# -------------------------
def _badge(tag: str) -> str:
    """
    Returns an HTML badge for the given sentiment tag.
    """
    tag = tag.lower()
    if tag == "bullish":
        return '<span class="badge bullish">Bullish</span>'
    elif tag == "bearish":
        return '<span class="badge bearish">Bearish</span>'
    else:
        return '<span class="badge neutral">Neutral</span>'

def _dl_bytes(result: dict) -> bytes:
    """
    Converts the result dictionary to a JSON string and encodes it as bytes.
    Handles datetime/date serialization by converting to ISO string.
    """
    def _default(o):
        if isinstance(o, (dt.date, dt.datetime)):
            return o.isoformat()
        return str(o)  # fallback for other exotic objects

    return json.dumps(result, indent=4, default=_default).encode("utf-8")

def _md_report(result: dict) -> str:
    """
    Generates a Markdown report from the result dictionary.
    """
    report = f"# Sentiment Analysis Report for {result['query']}\n\n"
    report += f"**Overall Sentiment:** {result['aggregate']['overall_tag']}\n\n"
    report += f"**Score:** {result['aggregate']['score_0_100']}/100\n\n"
    report += "## Stock Price and Percentage Change\n"
    price_change = result.get("price_change", {})
    if price_change:
        report += f"- **Start Date:** {price_change.get('start_date')}\n"
        report += f"- **End Date:** {price_change.get('end_date')}\n"
        report += f"- **Start Price:** ${price_change.get('start_price')}\n"
        report += f"- **End Price:** ${price_change.get('end_price')}\n"
        report += f"- **Percentage Change:** {price_change.get('percentage_change')}%\n"
    else:
        report += "No stock price data available for the selected period.\n"

    report += "\n## Relevant Articles\n"
    for article in result["articles"]:
        report += f"- **Source:** {article.get('source', 'Unknown')}\n"
        report += f"  - **Title:** {article.get('title', 'No Title')}\n"
        report += f"  - **Sentiment:** {article.get('sentiment_label', 'Unknown')} ({article.get('sentiment_conf', 0):.2f})\n"
        report += f"  - **URL:** {article.get('url', 'No URL')}\n\n"

    return report

@st.cache_data(show_spinner=False, ttl=15*60)
def _run(query_str: str, date_from, date_to, openai_key: str) -> dict:
    logger.debug(f"_run called with query_str: {query_str}, date_from: {date_from}, date_to: {date_to}")

    if (date_to - date_from).days > 31:
        date_from = date_to - dt.timedelta(days=31)
    if date_from > date_to:
        date_from = date_to

    # Run your pipeline
    result = run_pipeline(query_str, date_from=date_from, date_to=date_to, openai_api_key=openai_key)

    # Try to get structured stock data first
    stock_data = result.get("stock_data", [])
    price_change = aggregate_price_change(stock_data)

    # Normalize into one schema
    if price_change and all(k in price_change for k in ["first_day", "last_day", "first_price", "last_price"]):
        normalized = {
            "first_day": price_change.get("first_day"),
            "last_day": price_change.get("last_day"),
            "first_price": price_change.get("first_price"),
            "last_price": price_change.get("last_price"),
            "percentage_change": price_change.get("percentage_change"),
        }
    else:
        # fallback to values from run_pipeline
        logger.warning("Price change data is empty or malformed. Using fallback values.")
        start = result.get("Stock Price Start")
        end = result.get("Stock Price End")
        normalized = {
            "first_day": date_from,
            "last_day": date_to,
            "first_price": start,
            "last_price": end,
            "percentage_change": ((end - start) / start * 100) if start else None,
        }

    result["price_change"] = normalized
    logger.debug(f"Final result: {result}")
    return result

# -------------------------
# main panel
# -------------------------
if run_btn:
    if not query.strip():
        st.warning("Please type a company name.")
        st.stop()

    with st.spinner(f"Finding relevant news for '{query}'..."):
        try:
            result = _run(query.strip(), date_from, date_to, user_openai_key)
        except Exception as e:
            st.exception(e)
            st.stop()

    agg = result["aggregate"]
    tag = agg["overall_tag"]
    score = agg["score_0_100"]

    left, mid, right = st.columns([1.2, 1, 1])
    with left:
        st.subheader(f"Overall for '{result['query']}' {tag}")
        st.markdown(_badge(tag), unsafe_allow_html=True)
        st.markdown(f"**Score:** {score}/100")
    with mid:
        st.metric("Positive / Neutral / Negative (weighted share)",
                  value=f"{int(agg['weighted_share']['positive']*100)}% / {int(agg['weighted_share']['neutral']*100)}% / {int(agg['weighted_share']['negative']*100)}%")
        st.caption(str(agg["counts"]))
    with right:
        st.progress(int(score))

    st.divider()
    # -------------------------
    # section for stock price change
    # -------------------------
    st.subheader("📈 Stock Price and Percentage Change")
    price_change = result.get("price_change", {})
    if price_change:
        st.write(f"**Start Date:** {price_change.get('first_day')}")
        st.write(f"**End Date:** {price_change.get('last_day')}")
        st.write(f"**Start Price:** ${price_change.get('first_price')}")
        st.write(f"**End Price:** ${price_change.get('last_price')}")
        st.write(f"**Percentage Change:** {price_change.get('percentage_change')}%")
    else:
        st.warning("No stock price data available for the selected period.")

    st.divider()

    st.subheader(f"Relevant Articles ({result['count']})")
    table_rows = []
    for a in result["articles"]:
        link = a.get("url") or ""
        source = a.get("source", "")
        title = a.get("title", "")
        sent = f"{a.get('sentiment_label', '-')} ({a.get('sentiment_conf', 0):.2f})"
        table_rows.append({
            "Source": source,
            "Title": title,
            "Sentiment": sent,
            "URL": link
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.markdown("### Save this run")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download JSON",
            data=_dl_bytes(result),
            file_name=f"{result['query']}_{dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "⬇️ Download Markdown Report",
            data=_md_report(result).encode("utf-8"),
            file_name=f"{result['query']}_{dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )

else:
    st.info("Type a company name in the sidebar and click **Find News Sentiment**.")
    st.write("This uses only **title + description** for sentiment (FinBERT), after filtering for investment relevance.")