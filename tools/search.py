from ddgs import DDGS
import httpx
from bs4 import BeautifulSoup

def fetch_page_content(url: str, max_chars: int = 1500) -> str:
    try:
        response = httpx.get(url, timeout=5, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        # remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:max_chars]
    except:
        return ""

def search_web(query: str, max_results: int = 5) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    
    output = ""
    for r in results[:3]:  # fetch content for top 3 only
        output += f"Title: {r['title']}\n"
        output += f"URL: {r['href']}\n"
        output += f"Summary: {r['body']}\n"
        content = fetch_page_content(r['href'])
        if content:
            output += f"Content: {content}\n"
        output += "\n"
    
    return output if output else "No results found."