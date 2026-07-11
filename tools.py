from langchain.tools import tool

# for web scrapping etc.
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient

import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise EnvironmentError(
        "TAVILY_API_KEY is not set. Add it to your .env file "
        "(get a key at https://tavily.com)."
    )

tavily = TavilyClient(api_key=TAVILY_API_KEY)
# print("Tavily client initialized")

@tool
def web_search(query: str) -> str:
    """Search the web for the recent and reliable information on a topic. Returns Tiltles, URLs and snippets of the search results."""
    results = tavily.search(query, max_results=5)

    out = []

    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL : {r['url']}\nSnippet : {r['content'][:300]}\n"
        )

    # to make list of strings into one string with separator
    return "\n----\n".join(out)


# print(web_search.invoke("What is the latest news on War ?"))

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        # headers to mimic a browser visit to avoid being blocked by some websites
        response = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        # remove unwanted tags that are not part of the main content
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()
            # why decompose? because it removes the tag from the soup and also destroys it to free up memory, which is more efficient than just extracting the tag.

        return soup.get_text(separator=" ", strip=True)[:3000]

    
    except Exception as e:
        return f"Error scraping URL: {e}"
    

# print(scrape_url.invoke("https://en.wikipedia.org/wiki/Democracy"))
    


    




