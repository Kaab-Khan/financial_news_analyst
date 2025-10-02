"""
Simplest runner for the pipeline.
- Hardcode the company name here for now.
- Tomorrow we can add CLI parsing, or hook it to a web app / Telegram bot.
"""

from src.pipeline.run_pipeline import run_pipeline

# at top of src/pipeline/run_pipeline.py
import datetime as dt
import json
import os


if __name__ == "__main__":
    company_name = ""
    date_from = dt.date(2025, 8, 20)
    date_to = dt.date(2025, 8, 22)  # e.g. dt.date(2023,8,1)
    result = run_pipeline(company_name, date_from=date_from, date_to=date_to)

    agg = result["aggregate"]
    print(
        f"\nOverall sentiment for {company_name}: {agg['overall_tag']} ({agg['score_0_100']}/100)"
    )
    print("Counts:", agg["counts"])
    print("Weighted shares:", agg["weighted_share"])

    print(f"\n=== Relevant Articles ({result['count']}) ===")
    for i, a in enumerate(result["articles"], 1):
        print(f"{i}. {a.get('source','')} — {a.get('title','')}")
        print(
            f"   sentiment: {a.get('sentiment_label','-')} ({a.get('sentiment_conf',0):.2f})"
        )
        print(f"   {a.get('url','')}")
# Save to a timestamped file
# (so you can keep track of runs over time)


out_dir = "runs"
os.makedirs(out_dir, exist_ok=True)
ts = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
out_path = os.path.join(out_dir, f"{company_name}_{ts}.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\nSaved run to {out_path}")
