from selenium import webdriver
from selenium.webdriver.common.by import By
import time 



options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
dr = webdriver.Chrome(options=options)


def scrape_full_articles(url):
    url = str(url).strip()
    print(f"Getting content of {url}")
    dr.get(url)
    time.sleep(3)

    print(dr.title, "\n")

    # Extract the article body 
    try: 
        article_content = dr.execute_script("return document.query.Selector('article').innerText")
        paragraphs = dr.find_element(by.TAG_NAME, 'p')

        # Join all the paragraphs into a full article 

        full_article = "\n".join([p.text for p in paragraphs])
        return full_article
    except Exception as e:
        print(f"Error: {e}")
        return None