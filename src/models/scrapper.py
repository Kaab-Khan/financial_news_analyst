# """
# This code is a Python script that uses Selenium to scrape full articles from a given URL. It initializes a headless Chrome browser, navigates to the specified URL, and extracts the text content of the article by selecting all paragraph elements.
# The script handles exceptions and returns the full article text or None if an error occurs.
# # But I don't need this code at the moment because we will get the full article from the news_api.py file
# """

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import os
# import sys
# import re

# sys.path.append(
#     os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
# )


# def is_valid_url(url):
#     """Validate the URL format."""
#     regex = re.compile(
#         r"^(https?://)?"  # http:// or https://
#         r"([a-zA-Z0-9.-]+)"  # domain
#         r"(\.[a-zA-Z]{2,})"  # top-level domain
#         r"(:\d+)?"  # optional port
#         r"(\/.*)?$"  # optional path
#     )
#     return re.match(regex, url) is not None


# def scrape_full_articles(url):
#     if not is_valid_url(
#         url
#     ):  # This will check if the URL is valid if not it will return None
#         print(f"Invalid URL: {url}")
#         return None

#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     # Ensure the URL is a string and strip any whitespace
#     url = str(url).strip()
#     print(f"Getting content of {url}")
#     driver.get(url)
#     time.sleep(3)

#     print(driver.title, "\n")

#     # Extract the article body
#     try:
#         article_content = driver.execute_script(
#             "return document.querySelector('article').innerText"
#         )
#         paragraphs = driver.find_elements(By.TAG_NAME, "p")

#         # Join all the paragraphs into a full article
#         full_article = "\n".join([p.text for p in paragraphs])
#         driver.quit()  # Quit the WebDriver after use
#         return full_article
#     except Exception as e:
#         print(f"Error: {e}")
#         driver.quit()  # Ensure WebDriver quits even on error
#         return None
