from duckduckgo_search import DDGS

def duckduckgoSearch(query: str,maxResult: int):
    ddgs = DDGS()
    return ddgs.text(query, max_results=maxResult)
