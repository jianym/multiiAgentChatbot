import asyncio
import base64
import json

import aiofiles

from agent.AgentTool import Tool
from agent.model.QwenModel import llmQwen as qw_llm
from agent.model.DeepseekModel import llm


class OmniCommonTool(Tool):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.toolData = ""
        # asyncio.run(self.imageModelByUrl("这个图片内容是什么","https://pixnio.com/free-images/2025/03/18/2025-03-18-09-24-57-1920x1500.jpeg"))

    def getPrompt(self, messageNo=None):
        content = f"""
        你是一名多模态助手，你的目标是根据用户问题调用相关工具对图片进行识别

        你按照如下步骤进行工作:
             1. 根据用户问题判断当前用户的意图。
             2. 调用相关工具传入相关参数
             3. 结合工具返回的信息，给出最终回复答案
             4. 将最终答案返回成json格式数据
             
        基本信息:
        {self.baseInfo}
        
        返回json格式:
        {{"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name": <string>,"args": <list>}}

        返回值说明:
          - `code`：0 -> 执行成功
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `reply`:  提供问题的最终回复信息
          - `tool_name`: 调用工具的名称
          - `args`: 调用工具所需的参数列表
          
        可调用工具信息:
          - `imageModelByUrl(query: str,url: str)`: 通过图片的url地址识别图片内容，参数为用户问题和图片的网络链接地址
            - `query`: 必需传递，用户的针对图片的问题，用于传给图片大模型进行推理， 例如: 图片中有几把钥匙
            - `url`: 必需传递，图片的网络链接地址，  例如: http://example.com/1233.png
          - `imageModelByBase64(query: str,base64: str)`: 通过图片的base64编码识别图片内容，参数为用户问题和图片base64编码
            - `query`: 必需传递，用户的针对图片的问题，用于传给图片大模型进行推理
            - `base64`: 必需传递，图片的base64编码

        """
        message = {"role": "system", "content": content}
        return message

    def queryDesc(self) -> str:
        desc = """
        OmniCommonTool ->  这是一个用于图片内容识别的多模态Agent
          - `imageModelByUrl(query: str,url: str)`: 通过图片的url地址识别图片内容，参数为用户问题和图片的网络链接地址
            - `query`: 必需传递，用户的针对图片的问题，用于传给多模态大模型进行推理 
            - `url`: 必需传递，图片的网络链接地址
          - `imageModelByBase64(query: str,base64: str)`: 通过图片的base64编码识别图片内容，参数为用户问题和图片base64编码
            - `query`: 必需传递，用户的针对图片的问题，用于传给多模态大模型进行推理
            - `base64`: 必需传递，图片的base64编码
        """
        return desc

    def queryName(self) -> str:
        return "OmniCommonTool"

    async def action(self, messageNo: str, jsonData: dict):
        if jsonData["code"] != 0:
            return jsonData
        if jsonData["tool_name"] == "imageModelByUrl":
            self.toolData = await self.imageModelByUrl(jsonData["args"][0], jsonData["args"][1])
        elif jsonData["tool_name"] == "imageModelByBase64":
            self.toolData = await self.imageModelByBase64(jsonData["args"][0], jsonData["args"][1])
        return self.toolData

    async def imageModelByUrl(self,query: str,url: str):
        messages = [{"role": "system", "content": [{"type": "text", "text": "你是一名帮助助手"}]}]
        messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": url}}, {"type": "text", "text": query}]})
        response = await qw_llm.acall(json.dumps(messages))
        return {"code": 0,"reply": response}

    async def imageModelByBase64(self,query: str,base64Encode: str):
        messages = [{"role": "system", "content": [{"type": "text", "text": "你是一名帮助助手"}]}]
        messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64Encode}"}}, {"type": "text", "text": query}]})
        response = await qw_llm.acall(json.dumps(messages))

        return {"code": 0, "reply": response}


instance = OmniCommonTool()
