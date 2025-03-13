# from agent.tool import Tool
# from langchain.llms.base import LLM
from duckduckgo_search import DDGS

ddgs = DDGS()
query = "好看的小说"
results = ddgs.text(query,max_results=7)

# 输出前几个搜索结果
for result in results[:5]:
    print(f"Title: {result['title']}")
    print(f"URL: {result['href']}")
    print(f"URL: {result['body']}")

