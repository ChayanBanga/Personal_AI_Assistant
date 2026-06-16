from ddgs import DDGS

def search_web(query: str, max_results: int = 5) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    
    output = ""
    for r in results:
        output += f"Title: {r['title']}\n"
        output += f"URL: {r['href']}\n"
        output += f"Summary: {r['body']}\n\n"
    
    return output if output else "No results found."