from langchain.tools import tool

# for web scrapping etc.
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient

import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
# print("Tavily client initialized")

@tool
def web_search(query: str) -> str:
    """Search the web for the recent and reliable information on a topic. Returns Tiltles, URLs and snippets of the search results."""
    results = tavily.search(query, max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f'Title: {r['title']}\nURL : {r['url']}\nSnippet : {r['content'][:300]}\n'
        )

    # to make list of strings into one string with separator
    return "\n----\n".join(out)


# print(web_search.invoke("What is the latest news on War ?"))

    




