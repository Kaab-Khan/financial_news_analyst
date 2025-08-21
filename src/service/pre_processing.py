import fuzzywuzzy
from fuzzywuzzy import process
from collections import defaultdict
from resources.trusted_sources import trusted_sources


def is_trusted_source(source, threshold):
    """
    This function takes a news source as input and check if it is a
    trusted source using fuzzy matching.
    """
    # Check if the source is in the trusted sources list
    if not source or not trusted_sources:
        return False
    result = process.extractOne(source, trusted_sources)
    if result:
        match, score = result
        return score >= threshold
    return False


def filtered_articles(article_list):
    """
    This function takes a list of articles as input and filters out articles
    from untrusted sources.
    """

    if not isinstance(article_list, list):
        return []

    filtered_article_list = [
        article
        for article in article_list
        if isinstance(article, dict)
        and is_trusted_source(article.get("source", {}).get("name", ""), 0)
    ]
    return filtered_article_list
