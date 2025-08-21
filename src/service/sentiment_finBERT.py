from transformers import AutoTokenizer, AutoModelForSequenceClassification
from functools import lru_cache
import torch
from typing import List, Dict

MODEL_ID = "ProsusAI/finbert"
LABELS = ["negative", "neutral", "positive"]

@lru_cache(maxsize=1)
def _load():
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    mdl.to(device).eval()
    return tok, mdl, device

def score_text(text: str) -> Dict:
    """Return {'label','confidence','probs'} using FinBERT on title/snippet."""
    if not text:
        return {"label":"neutral","confidence":0.0,"probs":[0.33,0.34,0.33]}
    tok, mdl, device = _load()
    inputs = tok(text[:2000], truncation=True, return_tensors="pt").to(device)
    with torch.no_grad():
        logits = mdl(**inputs).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy().squeeze().tolist()
    idx = int(max(range(3), key=lambda i: probs[i]))
    return {"label": LABELS[idx], "confidence": float(probs[idx]), "probs": probs}

def label_to_score(label: str, conf: float) -> float:
    """Map to [-1,1] numeric sentiment for scoring."""
    base = {"positive":1.0, "neutral":0.0, "negative":-1.0}.get(label, 0.0)
    return base * float(conf)

def enrich_with_sentiment(articles: List[Dict]) -> List[Dict]:
    """Mutates each article adding sentiment_label/conf/score."""
    for a in articles:
        title = a.get("title","")
        description = a.get("summary") or a.get("description") or a.get("body") or ""
        res = score_text((title + ". " + description).strip())
        a["sentiment_label"] = res["label"]
        a["sentiment_conf"]  = res["confidence"]
        a["sentiment_score"] = label_to_score(res["label"], res["confidence"])
    return articles
def get_sentiment_scores(articles: List[Dict]) -> List[Dict]:
    """
    Returns a list of articles with sentiment scores.
    Each article will have 'sentiment_label', 'sentiment_conf', and 'sentiment_score'.
    """
    return enrich_with_sentiment(articles)

"""
Aggregate sentiment (simple version).
- No recency weighting
- No source weighting
- Final score in [0, 100] (0 = fully bearish, 50 = neutral, 100 = fully bullish)
"""

from typing import List, Dict

def label_to_signed(label: str | None, conf: float | None) -> float:
    """
    Map label+confidence to signed value in [-1,1].
      positive -> +conf
      neutral  -> 0
      negative -> -conf
    """
    if not label or conf is None:
        return 0.0
    base = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}.get(label, 0.0)
    return base * float(conf)

def aggregate_sentiment(articles: List[Dict]) -> Dict:
    """
    Aggregate per-article sentiment into one ticker-level score.

    Args:
        articles: list of dicts with keys:
          - sentiment_label ('positive'|'neutral'|'negative')
          - sentiment_conf  float in [0,1]

    Returns:
        {
          "score_0_100": float,     # in [0,100]
          "overall_tag": str,       # Bullish | Neutral | Bearish
          "counts": {...},          # raw counts
          "weighted_share": {...}   # share by weight
        }
    """
    if not articles:
        return {
            "score_0_100": 50.0,
            "overall_tag": "Neutral",
            "counts": {"positive": 0, "neutral": 0, "negative": 0, "total": 0},
            "weighted_share": {"positive": 0.0, "neutral": 1.0, "negative": 0.0},
        }

    pos_w = neu_w = neg_w = 0.0
    sum_w = 0.0
    sum_wsigned = 0.0

    for a in articles:
        label = a.get("sentiment_label")
        conf  = float(a.get("sentiment_conf", 0.0) or 0.0)

        signed = label_to_signed(label, conf)  # [-1,1]
        w = conf                              # weight = confidence only

        sum_w += w
        sum_wsigned += w * signed

        if label == "positive":
            pos_w += w
        elif label == "negative":
            neg_w += w
        else:
            neu_w += w

    if sum_w <= 1e-9:
        return {
            "score_0_100": 50.0,
            "overall_tag": "Neutral",
            "counts": {"positive": 0, "neutral": 0, "negative": 0, "total": len(articles)},
            "weighted_share": {"positive": 0.0, "neutral": 1.0, "negative": 0.0},
        }

    avg_signed = sum_wsigned / sum_w    # [-1,1]
    score_0_100 = (avg_signed + 1) * 50 # map -1..1 → 0..100

    # decide tag
    if score_0_100 >= 60:
        tag = "Bullish"
    elif score_0_100 <= 40:
        tag = "Bearish"
    else:
        tag = "Neutral"

    return {
        "score_0_100": round(score_0_100, 1),
        "overall_tag": tag,
        "counts": {
            "positive": sum(1 for a in articles if a.get("sentiment_label")=="positive"),
            "neutral":  sum(1 for a in articles if a.get("sentiment_label")=="neutral"),
            "negative": sum(1 for a in articles if a.get("sentiment_label")=="negative"),
            "total":    len(articles),
        },
        "weighted_share": {
            "positive": round(pos_w/sum_w, 3),
            "neutral":  round(neu_w/sum_w, 3),
            "negative": round(neg_w/sum_w, 3),
        },
    }
