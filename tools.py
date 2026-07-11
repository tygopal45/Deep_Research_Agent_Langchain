# These are the two "hands" of the agents: one to search the web, one to read a page.
# The @tool decorator turns a plain function into something an LLM can actually call.
from langchain.tools import tool

# requests fetches the raw HTML, BeautifulSoup cleans it up, Tavily does the searching.
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient

import os
from dotenv import load_dotenv
from rich import print  # nicer, colored output when we print during development

# Pull secrets (API keys) out of the .env file so they never get hard-coded.
load_dotenv()

# Fail fast: if the key is missing, crash right here with a helpful message
# instead of blowing up later mid-search with something cryptic.
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise EnvironmentError(
        "TAVILY_API_KEY is not set. Add it to your .env file "
        "(get a key at https://tavily.com)."
    )

# One shared Tavily client we reuse for every search call.
tavily = TavilyClient(api_key=TAVILY_API_KEY)
# print("Tavily client initialized")

@tool
def web_search(query: str) -> str:
    """Search the web for the recent and reliable information on a topic. Returns Tiltles, URLs and snippets of the search results."""
    # Ask Tavily for the top 5 hits — enough coverage without drowning the model in text.
    results = tavily.search(query, max_results=5)

    out = []

    # Reshape each result into a tidy little block. We trim the snippet to 300 chars
    # because the full page content is huge and we only need a preview here.
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL : {r['url']}\nSnippet : {r['content'][:300]}\n"
        )

    # Glue the blocks into a single string with a clear separator between them,
    # so the LLM can easily tell one source from the next.
    return "\n----\n".join(out)


# print(web_search.invoke("What is the latest news on War ?"))

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    # Wrapped in try/except on purpose: a single dead link or timeout shouldn't
    # take down the whole research run — we just hand back an error string instead.
    try:
        # Pretend to be a real browser. A lot of sites block anything that looks
        # like a bot, and the timeout stops us from hanging on a slow page.
        response = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        # Strip out the page "chrome" (menus, scripts, footers...) so we're left
        # with the actual article text and not a wall of navigation noise.
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()
            # why decompose? because it removes the tag from the soup and also destroys it to free up memory, which is more efficient than just extracting the tag.

        # Cap at 3000 chars — keeps the prompt small (= cheaper + faster) and safely
        # inside the model's context window.
        return soup.get_text(separator=" ", strip=True)[:3000]


    except Exception as e:
        return f"Error scraping URL: {e}"
    

# print(scrape_url.invoke("https://en.wikipedia.org/wiki/Democracy"))
    


    




