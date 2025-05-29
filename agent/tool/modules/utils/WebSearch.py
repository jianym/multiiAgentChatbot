from duckduckgo_search import DDGS

def duckduckgoSearch(query: str,maxResult: int):
    ddgs = DDGS()
    try:
        return ddgs.text(query, max_results=maxResult)
    except Exception as e:
        print(str(e))
        return None
