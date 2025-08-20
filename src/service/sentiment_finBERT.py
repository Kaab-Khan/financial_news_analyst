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
        snippet = a.get("summary") or a.get("description") or a.get("body") or ""
        res = score_text((title + ". " + snippet).strip())
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