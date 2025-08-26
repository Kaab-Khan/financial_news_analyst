import os
import json
import datetime as dt
import streamlit as st

# your pipeline
from src.pipeline.run_pipeline import run_pipeline

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

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
st.title("📰 Financial News Sentiment (Headline-only MVP)")
st.caption("Fetches news by company name → filters for investment relevance → FinBERT on title+description → aggregates to a 0–100 sentiment.")

# -------------------------
# sidebar controls
# -------------------------
# --- sidebar controls ---

# --- Ask user for their own OpenAI key
with st.sidebar:
    st.header("🔑 API Settings")
    user_openai_key = st.text_input(
        "Enter your OpenAI API key", 
        type="password", 
        help="Your key is only used for this session and not stored."
    )

    # Decide which key to use
    if user_openai_key:
        OPENAI_API_KEY = user_openai_key.strip()
    else:
        st.warning("⚠️ Please enter your own OpenAI API key in the sidebar to run live analysis.")
        st.stop()

    # Company name
    default_query = st.session_state.get("default_query", "Enter a stock name")
    query = st.text_input("Company name", value=default_query, placeholder="e.g., Tesla, Apple, NVIDIA")
    st.session_state["default_query"] = query

    # Date range (max 31 days)
    import datetime as dt
    today = dt.date.today()
    max_lookback = today - dt.timedelta(days=31)

    st.subheader("Date range (max 31 days)")
    col_a, col_b = st.columns(2)
    with col_a:
        date_from = st.date_input("From", value=max_lookback, min_value=max_lookback, max_value=today)
    with col_b:
        date_to = st.date_input("To", value=today, min_value=max_lookback, max_value=today)

    # Enforce max 31 days window
    if (date_to - date_from).days > 31:
        st.warning("Range exceeds 31 days. It will be clipped to the last 31 days.")

    run_btn = st.button("Run pipeline", type="primary", use_container_width=True)


# -------------------------
# helpers
# -------------------------
@st.cache_data(show_spinner=False, ttl=15*60)
def _run(query_str: str, date_from, date_to, openai_key : str) -> dict:
    if (date_to - date_from).days > 31:
        date_from = date_to - dt.timedelta(days=31)
    if date_from > date_to:
        date_from = date_to
    return run_pipeline(query_str, date_from=date_from, date_to=date_to, api_key=openai_key)


def _badge(tag: str) -> str:
    m = {
        "Bullish": "bullish",
        "Bearish": "bearish",
        "Neutral": "neutral",
    }
    cls = m.get(tag, "neutral")
    return f'<span class="badge {cls}">{tag}</span>'

def _dl_bytes(data: dict) -> bytes:
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

def _md_report(data: dict) -> str:
    agg = data["aggregate"]
    lines = []
    lines.append(f"# Sentiment Report — {data['query']}")
    lines.append(f"_Generated: {dt.datetime.utcnow().isoformat()}Z_")
    lines.append("")
    lines.append(f"**Overall:** {agg['overall_tag']} ({agg['score_0_100']}/100)")
    lines.append(f"- Counts: {agg['counts']}")
    lines.append(f"- Weighted share: {agg['weighted_share']}")
    lines.append("")
    lines.append(f"## Articles ({data['count']})")
    for i, a in enumerate(data["articles"], 1):
        lines.append(f"{i}. **{a.get('source','')}** — {a.get('title','')}")
        lines.append(f"   - Sentiment: {a.get('sentiment_label','-')} ({a.get('sentiment_conf',0):.2f})")
        lines.append(f"   - Link: {a.get('url','')}")
    return "\n".join(lines)

# -------------------------
# main panel
# -------------------------
if run_btn:
    if not query.strip():
        st.warning("Please type a company name.")
        st.stop()
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set. Export it in your shell and relaunch.")
        st.stop()

    with st.spinner(f"Running pipeline for '{query}'..."):
        try:
            result = _run(query.strip(), date_from, date_to, user_openai_key)
        except Exception as e:
            st.exception(e)
            st.stop()

    # overall metrics
    agg = result["aggregate"]
    tag = agg["overall_tag"]
    score = agg["score_0_100"]

    # top summary row
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
        st.progress(int(score))  # simple visual bar (0-100)

    st.divider()

    # articles table
    st.subheader(f"Relevant Articles ({result['count']})")

    # Convert to a lightweight table with clickable links
    table_rows = []
    for a in result["articles"]:
        link = a.get("url") or ""
        source = a.get("source","")
        title = a.get("title","")
        sent = f"{a.get('sentiment_label','-')} ({a.get('sentiment_conf',0):.2f})"
        table_rows.append({
            "Source": source,
            "Title": title,
            "Sentiment": sent,
            "URL": link
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    # downloads
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
    st.info("Type a company name in the sidebar and click **Run pipeline**.")
    st.write("This MVP uses only **title + description** for sentiment (FinBERT), after filtering for investment relevance.")
