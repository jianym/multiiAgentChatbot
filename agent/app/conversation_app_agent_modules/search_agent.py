import asyncio
import hashlib
import json
import mimetypes
import os
import subprocess
from urllib.parse import unquote, urlparse

import aiohttp
import config
from agent.agent_node import AgentNode
from agent.model.BgeModel import bgeModel
import agent.tool.modules.utils.documents as dc
import agent.tool.modules.utils.cosineSimilarity as cosineSimilar
from agent.model.DeepseekModel import llm
import agent.tool.modules.utils.WebSearch as ws


class SearchAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = ""

    def get_prompt(self,chat_no=None):
        content = f"""
         你是一名网络搜索助手，你的必须调用相关工具回答用户的问题，并返回json格式数据。
         
         你按照如下步骤进行工作:
             1. 根据用户问题判断当前用户的意图
             2. 选择调用的工具和传入相关参数（必须使用一个工具来检索信息）
             3. 结合工具返回的信息，给出最终回复答案
             4. 将最终答案返回成json格式数据        
             
        问题及子问题内容约束:
             1. 用户问题中包含如昨日，明天，后天，前天等可以计算到某个时间，应根据当前时间进行计算到具体的时间（年月日十分秒等）
             2. 用户问题中包含的时间，如最新，近年来等这些无法具体到某一时间点的，无需转换成具体时间
             2. 保证用户搜索时间的准确性
             
        上下文信息:
           - 基本信息:
            {self.get_context_data(chat_no,"baseInfo")}
            
           - 电影网站推荐
             ["https://www.maoyan.com/"]          
           
        返回json格式数据:
         {{"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name":<string>,"args": <list>}}

        返回值说明:
          - `code`：0 -> 执行成功
          - `reply`:  提供问题的最终回复信息
          - `tool_use`:  True -> 需使用工具, False -> 不使用工具
          - `tool_name`: 调用工具的名称
          - `args`: 调用工具所需的参数列表
          
        可调用工具信息:
          - `web_search_engine(query: str,recommend_links: list)`: 通过搜索引擎进行网络搜索答案
            - `query`: 需要搜索的用户问题
            - `recommend_links`: 推荐的网络链接地址（以http或https开头）列表
          - `question_links(query: str,link: str)`: 通过用户提供的网络链接地址回答用户的问题
            - `query`: 用户的问题
            - `link`: 用户提供的网络链接地址
         """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
         SearchAgent -> 这个是一名网络搜索工具，通过网络搜索来回答用户的问题，用于网络信息的搜索
         
         """
        return desc

    def query_name(self) -> str:
        return "SearchAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] != 0 or not json_data["tool_use"]:
            return json_data
        if json_data["tool_name"] == "web_search_engine":
            links = []
            query = json_data["args"][0]
            recommend = json_data["args"][1]
            if len(recommend) > 0:
                links.extend(recommend)
            return await self.web_search_engine(query,chat_no, links)
        elif json_data["tool_name"] == "question_links":
            return await self.web_search_engine(json_data["args"][0], chat_no, json_data["args"][1])
        return json_data
    async def question_links(self,query,chat_no,link: str):
        links = []
        links.append(link)
        return await self.web_search(query,chat_no,links)

    async def web_search_engine(self,query: str, chat_no: str,links: list):
        results = await asyncio.to_thread(ws.duckduckgoSearch, query, 5)
        if not results:
            return {"code": "3", "reply": "没有检索到相关数据"}
        for result in results[:4]:
            links.append(result['href'])
        return await self.web_search(query,chat_no,links)

    async def web_search(self,query: str, chat_no: str,links: list):
        docs = await dc.getDocumentsFromLinks(links)
        self.toolData = await self.search(docs, query, similarity_threshold=0.3, top_n=7)
        response_prompt = f"""
            根据搜索结果，回答用户的问题，如果返回结果有引用外部信息部分应标记出引用来源链接
            
            用户问题:
            {query}
            
            基本信息:
            {self.get_context_data(chat_no,"baseInfo")}
            
            搜索结果:
            {self.toolData}
            
            返回结果reply内容约束:
              1.返回结果中引用搜索结果部分必须标记出搜索来源链接，方便溯源
                - 每当引用搜索结果时，必须标明来源链接，确保信息可追溯
                - 基于网络搜索的结果使用 [源](URL) 语法来插入超链接，确保用户能够直接访问原始内容
                - 可以在引用部分增加具体的 发布日期，以便用户了解信息的时效性
              2.尽可能多的返回与查询问题相关的信息（保证全面性，准确性和细节完整）
                - 提供 背景信息、技术细节、实施步骤、案例分析、数据支撑、溯源信息、程序代码等内容。
                - 如果有多个相关因素或选项，要分别列出并给出权衡，帮助用户做出决策。
                - 如果有可能，举例说明或提供图表来辅助理解
              3.涉及到时间问题的应参考上下文信息，保证信息检索的时间范围
              
            返回json格式数据:
            {{"code": <int>,"reply": <string>,"source":<list>}}

            返回值说明:
            - `code`：0 -> 执行成功
            - `reply`:  提供问题的最终回复信息,返回结果有引用的部分，要提供引用来源链接
            - `source`: 来源，引用的搜索链接列表
        """
        result = await self.llm.acall(json.dumps([{"role":"user","content": response_prompt}]))
        return json.loads(result)

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
instance = SearchAgent()

