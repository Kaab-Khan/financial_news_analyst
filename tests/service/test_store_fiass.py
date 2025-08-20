# tests/service/test_faiss_store.py
import sys, os
import pytest

'''Test cases for FAISS-based article storage and retrieval.
These tests ensure that articles can be added, searched, and retrieved
with reasonable relevance and similarity scores.
The tests assume the use of the all-MiniLM-L6-v2 model for embeddings.
The tests will skip if the model cannot be loaded (e.g., in offline CI).
This file requires pytest to run.
It uses the ArticleStore class from src/service/store_faiss.py,
which is based on FAISS and SentenceTransformers.'''

# --- TEMP path hack (safe to remove once you add pytest.ini or pyproject) ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# ---------------------------------------------------------------------------

from src.service.store_faiss import ArticleStore  # uses all-MiniLM-L6-v2 (384-dim)

# --- Helpers ----------------------------------------------------------------
SAMPLE_ARTICLES = [
    {
        "title": "Tesla beats earnings expectations as deliveries rise",
        "url": "http://example.com/a1",
        "source": "Reuters",
        "description": "Q2 deliveries up 12% y/y; margin steady; guidance maintained.",
    },
    {
        "title": "Regulatory probe expands into Tesla Autopilot system",
        "url": "http://example.com/a2",
        "source": "Bloomberg",
        "description": "NHTSA expands investigation citing additional incidents and data.",
    },
    {
        "title": "Gigafactory expansion plans signal capacity boost in Texas",
        "url": "http://example.com/a3",
        "source": "WSJ",
        "description": "Capex to increase; potential hiring wave; suppliers notified.",
    },
]

@pytest.fixture(scope="module")
# Store or skip fixture
# This fixture initializes the ArticleStore and adds sample articles.
# If the SentenceTransformer model cannot be loaded, it skips the tests.
def store_or_skip():
    """
    Try to initialize ArticleStore and add sample docs.
    If SentenceTransformer/model download fails (e.g., offline CI),
    skip the tests gracefully.
    """
    try:
        st = ArticleStore()
        st.add(SAMPLE_ARTICLES)
        return st
    except Exception as e:
        pytest.skip(f"Skipping FAISS tests (embedding model unavailable): {e!r}")

# --- Tests ------------------------------------------------------------------
# Test cases for the ArticleStore class

def test_empty_index_returns_empty(): # 
    s = ArticleStore()
    out = s.search("tesla outlook", k=5)
    assert out == []

def test_add_populates_meta_and_search(store_or_skip):
    s = store_or_skip
    # Meta should have as many items as added
    assert len(s.meta) == len(SAMPLE_ARTICLES)

    # Basic semantic search should return at least one result
    out = s.search("tesla earnings deliveries guidance", k=3)
    assert isinstance(out, list)
    assert 1 <= len(out) <= 3

def test_k_larger_than_count(store_or_skip):
    s = store_or_skip
    out = s.search("autopilot investigation", k=10)
    # Must not exceed number of indexed docs
    assert 1 <= len(out) <= len(SAMPLE_ARTICLES)

def test_similarity_range_0_1(store_or_skip):
    s = store_or_skip
    out = s.search("factory expansion capacity texas", k=3)
    assert len(out) >= 1
    for r in out:
        # Using normalized embeddings + inner product ≈ cosine in [0,1]
        assert 0.0 <= r["similarity"] <= 1.0

def test_relevance_reasonable_ordering(store_or_skip):
    """
    Sanity check (not perfectly strict): queries about 'earnings/deliveries'
    should rank the 'beats earnings' article near the top.
    """
    s = store_or_skip
    out = s.search("earnings deliveries margin guidance", k=3)
    titles = [r["title"].lower() for r in out]
    assert any("beats earnings" in t or "deliveries" in t for t in titles)

def test_duplicate_additions_do_not_crash(store_or_skip):
    """
    Adding the same articles again should increase meta length and not crash.
    (We don't deduplicate at index level in this simple store.)
    """
    s = store_or_skip
    initial = len(s.meta)
    s.add(SAMPLE_ARTICLES)
    assert len(s.meta) == initial + len(SAMPLE_ARTICLES)
