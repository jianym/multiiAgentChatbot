import asyncio
import hashlib
import json
import mimetypes
import os
import subprocess
from urllib.parse import unquote, urlparse

import aiohttp

import config
from agent.AgentTool import Tool
from agent.model.BgeModel import bgeModel
import agent.tool.modules.utils.documents as dc
import agent.tool.modules.utils.cosineSimilarity as cosineSimilar
from agent.model.DeepseekModel import llm
import agent.tool.modules.utils.WebSearch as ws

class SearchTool(Tool):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = None

    def getPrompt(self,messageNo=None):
        content = f"""
         你是一名网络搜索助手，你的必须调用相关工具回答用户网络搜索的相关的问题，并返回json格式数据。
         
         你按照如下步骤进行工作:
             1. 首先你的必须选择相关工具来处理用户问题
             2. 然后结合工具返回的结果数据信息，给出最终回复答案
             3. 将最终答案返回成json格式数据
        
         基本信息:
         {self.baseInfo}
         
         返回json格式数据:
         {{"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name": <string>,"args": <list>}}

         返回值说明:
          - `code`：0 -> 执行成功
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `reply`:  提供问题的最终回复信息
          - `tool_name`: 需要调用的工具名称
          - `args`: 工具所需的参数列表
          
         可调用工具信息:
          - `search(query: str,recommend: list)`: 通过网络搜索答案，用于近实时，实时，互联网数据信息的搜索
            - `query`: 必需参数，用户的搜索问题，用于传给搜索引擎进行搜索
            - `recommend`: 必需参数，推荐搜索的url网络地址列表，如小说网站地址，影视剧网站地址，股票证券，官方网站地址等 格式 http或https开头
          - `downLinks(urls: list)`: 通过网络url连接下载文件，可以同时从多个url地址下载文件,返回下载后的文件地址
            - `urls`: 不能为空，下载的url连接集合列表，url以http或https开头
         工具返回的结果数据信息:
         {self.toolData}
         
         """
        message = {"role": "system", "content": content}
        return message

    def queryDesc(self) -> str:
        desc = """
         SearchTool -> 这个是一名网络搜索工具，通过网络搜索来回答用户的问题，用于网络信息的搜索
           - `search(query: str,recommend: list)`: 通过网络搜索答案，用于近实时，实时，官方，互联网数据信息的搜索
             - `query`: 必需传递，用户的搜索问题，用于传给搜索引擎进行搜索
             - `recommend`: 必需传递，推荐搜索的url网络地址列表，如小说网站地址，影视剧网站地址，股票证券地址，官方网站地址等 格式 http或https开头
           - `downLinks(urls: list)`: 通过网络url连接下载文件，可以同时从多个url地址下载文件,返回下载后的文件地址
             - `urls`: 不能为空，下载的url连接集合列表，url以http或https开头
         """
        return desc

    def queryName(self) -> str:
        return "SearchTool"

    async def action(self, messageNo: str, jsonData: dict):
        print(jsonData)
        print(2222222222222)
        print(2222222222222)
        if jsonData["code"] != 0:
            return jsonData

        if jsonData["tool_name"] == "search":
            links = []
            query = jsonData["args"][0]
            recommend = jsonData["args"][1]


            results = await asyncio.to_thread(ws.duckduckgoSearch,query,5)


            # 输出前几个搜索结果
            for result in results[:5]:
                links.append(result['href'])
            if len(recommend) > 0:
                print(recommend)
                links.extend(recommend)
            docs = dc.getDocumentsFromLinks(links)


            self.toolData = await self.search(docs, query, similarity_threshold=0.3, top_n=5)
            self.appendMessage(messageNo, {"role": "user", "content": "工具搜索结果已返回，根据给出最终答案"})
            outputRes = await self.llm.acall(json.dumps(self.getMessageAndPrompt(messageNo), ensure_ascii=False))
            print(outputRes)
            return json.loads(outputRes)

        elif jsonData["tool_name"] == "downLinks":
            self.toolData = await self.downLinks(jsonData["args"][0])

        return {"code": 0,"reply": json.dumps(self.toolData)}

    async def getEmbeddingAsync(self, text):
        return await asyncio.to_thread(bgeModel.getEmbedding, text)

    async def downLinks(self,links: list):
        filePaths = []
        for link in links:
          filePaths.append(self.downloadFileByLink(link))
        return filePaths


    async def get_filename_and_extension(self,url: str) -> tuple[str, str]:
        """获取文件名和扩展名，优先级：URL > Content-Disposition > Content-Type"""
        parsed_url = urlparse(url)
        filename = unquote(parsed_url.path.split("/")[-1])  # 从 URL 解析文件名
        extension = os.path.splitext(filename)[-1] if filename else ""

        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                # 从 Content-Disposition 获取文件名
                content_disposition = response.headers.get("Content-Disposition", "")
                if "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip().strip('"')
                    extension = os.path.splitext(filename)[-1]

                # 从 Content-Type 猜测扩展名
                if not extension:
                    content_type = response.headers.get("Content-Type", "")
                    extension = mimetypes.guess_extension(content_type) or ""

        # 如果没有文件名，生成唯一文件名
        filename = filename or f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}{extension}"
        return filename, extension

    async def downloadFileByLink(self,url: str):
        """下载文件，并使用 file 命令校正扩展名"""
        save_dir = config.OS_BASE_PATH + "/download"
        filename, extension = await self.get_filename_and_extension(url)
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(save_path, "wb") as file:
                    while chunk := await response.content.read(8192):  # 分块下载
                        file.write(chunk)

        print(f"File downloaded: {save_path}")

        # 使用 file 命令检测实际文件类型
        corrected_extension = self.detect_file_type(save_path)
        if corrected_extension and corrected_extension != extension:
            new_path = f"{save_path}{corrected_extension}"
            os.rename(save_path, new_path)
            print(f"Updated file extension: {new_path}")
        else:
            new_path = save_path
        return "/download/" + os.path.splitext(new_path)[-1]

    def detect_file_type(self,file_path: str) -> str:
        """使用 `file` 命令检测文件类型并返回扩展名"""
        try:
            result = subprocess.run(["file", "--mime-type", "-b", file_path], capture_output=True, text=True)
            mime_type = result.stdout.strip()
            ext = mimetypes.guess_extension(mime_type) or ""
            return ext
        except Exception as e:
            print(f"Failed to detect file type: {e}")
            return ""

    async def search(self, docs, query, similarity_threshold=0.6, top_n=7):
        # 获取查询嵌入
        queryEmbedding = await self.getEmbeddingAsync(query)

        # 获取文档嵌入
        docEmbeddings = []
        for doc in docs:
            docEmbedding = await self.getEmbeddingAsync(doc["pageContent"])
            docEmbeddings.append(docEmbedding)

        # 计算相似度
        similarity = [
            {"index": i, "similarity": cosineSimilar.computeSimilarity(queryEmbedding, docEmbedding, 'cosine')} for i, docEmbedding in enumerate(docEmbeddings)
        ]

        # 给文档添加相似度属性
        for sim in similarity:
            docs[sim["index"]]["similarity"] = sim["similarity"]

        # 排序并获取前 N 个文档
        sortedDocs = sorted(
            [docs[sim["index"]] for sim in similarity if sim["similarity"] > similarity_threshold],
            key=lambda x: x["similarity"],
            reverse=True
        )[:top_n]

        return sortedDocs
instance = SearchTool()
