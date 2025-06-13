from duckduckgo_search import DDGS

def search_web(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query)
            if results:
                top_result = results[0]
                return f"{top_result['title']} — {top_result['body']}\nSource: {top_result['href']}"
            else:
                return "No results found."
    except Exception as e:
        return f"[WebSearch Error] {e}"
