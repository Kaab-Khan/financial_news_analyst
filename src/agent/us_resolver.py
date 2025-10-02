# src/agent/us_resolver.py
from __future__ import annotations
import csv
import os
import re
from functools import lru_cache
from typing import Dict, List, Tuple

DATA_PATH = os.getenv("US_TICKERS_CSV", "resources/ticker_us.csv")
_TICKER_RE = re.compile(r"^[A-Z.-]{1,6}$")


def _norm(s: str) -> str:
    """Lowercase + strip non-alphanum to normalize names for matching."""
    import re

    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def _load_rows() -> List[Dict[str, str]]:
    """Read rows from CSV and standardize fields."""
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows: List[Dict[str, str]] = []
        for r in rdr:
            rows.append(
                {
                    "ticker": (r.get("ticker") or "").strip().upper(),
                    "company_name": (r.get("company_name") or "").strip(),
                    "exchange": (r.get("exchange") or "").strip().upper(),
                    "aliases": (r.get("aliases") or "").strip(),
                }
            )
        return rows


@lru_cache(maxsize=1)
def _build_index():
    """
    Build in-memory indices:
      - by_ticker: quick direct lookup (if user already typed 'AAPL').
      - name_index: normalized primary names
      - alias_index: normalized aliases (split by '|')
    Cached once per process.
    """
    rows = _load_rows()
    by_ticker: Dict[str, Dict] = {}
    name_index: List[Tuple[str, str, Dict]] = []
    alias_index: List[Tuple[str, str, Dict]] = []

    for r in rows:
        tkr = r["ticker"]
        if not tkr:
            continue
        by_ticker[tkr] = r
        name_index.append((_norm(r["company_name"]), tkr, r))
        if r["aliases"]:
            for alias in r["aliases"].split("|"):
                alias = alias.strip()
                if alias:
                    alias_index.append((_norm(alias), tkr, r))

    return by_ticker, name_index, alias_index


@lru_cache(maxsize=1024)
def resolve_us_ticker_basic(query: str) -> Dict:
    """
    Minimal resolver:
      1) If user typed a valid ticker that exists → return it.
      2) Exact company-name match (normalized) → return ticker.
      3) Exact alias match → return ticker.
      Else → not_found (we’ll add fuzzy next step).

    Returns:
      {"status":"ok","ticker":"AAPL","source":"ticker|exact|alias","meta":{...}}
      or {"status":"not_found"}
    """
    if not query or not query.strip():
        return {"status": "not_found"}

    q = query.strip()
    qn = _norm(q)
    by_ticker, name_index, alias_index = _build_index()

    # 1) already a valid ticker?
    if _TICKER_RE.fullmatch(q) and q in by_ticker:
        return {"status": "ok", "ticker": q, "source": "ticker", "meta": by_ticker[q]}

    # 2) exact primary name
    for n, tkr, row in name_index:
        if n == qn:
            return {"status": "ok", "ticker": tkr, "source": "exact", "meta": row}

    # 3) exact alias
    for n, tkr, row in alias_index:
        if n == qn:
            return {"status": "ok", "ticker": tkr, "source": "alias", "meta": row}

    return {"status": "not_found"}
