"""
Simplest runner for the pipeline.
- Hardcode the company name here for now.
- Tomorrow we can add CLI parsing, or hook it to a web app / Telegram bot.
"""

from src.run_pipeline import run_pipeline

if __name__ == "__main__":
    company_name = "Tesla"   # 👈 change this string to try a different company

    result = run_pipeline(company_name)

    agg = result["aggregate"]
    print(f"\nOverall sentiment for {company_name}: {agg['overall_tag']} ({agg['score_0_100']}/100)")
    print("Counts:", agg["counts"])
    print("Weighted shares:", agg["weighted_share"])

    print(f"\n=== Relevant Articles ({result['count']}) ===")
    for i, a in enumerate(result["articles"], 1):
        print(f"{i}. {a.get('source','')} — {a.get('title','')}")
        print(f"   sentiment: {a.get('sentiment_label','-')} ({a.get('sentiment_conf',0):.2f})")
        print(f"   {a.get('url','')}")
