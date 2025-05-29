# from elasticsearch import AsyncElasticsearch
# import config
#
# # 连接到本地 Elasticsearch
# es = AsyncElasticsearch("http://localhost:9200")
#
#
# async def create(index: str,mapping: dict):
#     # 创建索引
#     if not es.indices.exists(index=index):
#         await es.indices.create(index=index, body=mapping)
#         print(f"索引 {index} 创建成功！")
#     else:
#         print(f"索引 {index} 已存在。")
#
# async def add(index: str, doc: dict):
#     return await es.index(index=index, document=doc)
#
# async def search(index: str,query: dict):
#     return await es.search(index=index, query=query)
#
# async def update(index: str,id: str,doc: dict):
#     return await es.update(index=index, id=id, body=doc)
#
# async def delete(index: str,id: str):
#     return await es.delete(index=index, id=id)
#
#
