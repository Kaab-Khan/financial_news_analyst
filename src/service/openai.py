import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# api_key = os.getenv("OPENAI_API_KEY")


def filter_relevant_articles(articles, api_key: str | None = None) -> list[dict]:
    """
    This functions sends a batch of articles to OpenAI and
    filters only the most relevant ones.
    """
    prompt = """
    #Role:
    You are an AI financial news assistant with expertise in markets,
    investments and global economny.
    ##Task:
    - Your task is to analyze the provided news articles and select only
    those that are **highly relevant** to investment, financial analysis
    and policy makers about {relevant_stock}.
    ### Selection Criteria:
    1- Market impact: Market Impact** – Does the article influence
    financial markets, stocks, commodities, or major economic trends?
    2- Investment Relevance** – Would an investor, hedge fund manager,
    or analyst find this news actionable?
    3- Credible Source** – Does it come from a well-regarded financial publication?
    4- Avoid General News** – Ignore irrelevant articles (e.g.,
    company PR announcements, minor updates, general economy news without clear financial insights).
    5- Language** – Articles should be in English."""

    formatted_articles = "\n".join(
        [
            f"Title: {a['title']}\nURL: {a['url']}\nSource: {a['source']}\n"
            for a in articles
        ]
    )

    # Add LLM Instructinos
    prompt += formatted_articles + (
        "\n\n **Instructions:**\n*"
        "- Returns only the **most relevant articles that meet the criteria above. \n"
        "-Keep the format **strictly as JSON** like this:\n"
        "'''json\n"
        '[{"title": "Example Title", "url": "https://example.com","source":"Reuters"}]\n'
        "'''\n"
        "- Do **not** include any explainabtion, markdowns, or extra text. Return JSON only."
    )
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not provided.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an AI financial news assistant with expertise in markets, investments and global economny.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=600,
    )

    response_text = response.choices[0].message.content.strip()

    # 🛠 Strip Markdown formatting before parsing JSON
    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "").replace("```", "").strip()

    # 🛠 Try to parse JSON response
    try:
        filtered_articles_new = json.loads(response_text)
    except json.JSONDecodeError:
        print("Error: Failed to parse OpenAI response as JSON!")
        print(f"Response Text: {response_text}")  # Debugging
        filtered_articles_new = []

    return filtered_articles_new  # Returns parsed articles
