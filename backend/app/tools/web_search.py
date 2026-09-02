from duckduckgo_search import DDGS
from langchain_core.tools import tool

@tool
def web_search(query: str):
    """Searches the web for current events and information."""
    with DDGS as ddgs:
        return ddgs.text(query, region='wt-ini', safesearch='off', timelimit=None)
    
    top_three = islice(results, 3)

    formatted_results = []
    for i, result in enumerate(top_three, 1):
        title = result.get("title", "No Title")
        href = result.get("href", "No URL")
        body = result.get("body", "No Description")
        formatted_results.append(
            f"{i}. {title}\n   URL: {href}\n   {body}\n"
        )

    return "\n".join(formatted_results).strip()