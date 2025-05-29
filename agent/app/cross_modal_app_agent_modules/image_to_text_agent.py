import asyncio
import base64
import json
import os

import aiofiles
import aiohttp

import config
from agent.agent_node import AgentNode
from agent.model.QwenModel import llmQwen as qw_llm
from agent.model.DeepseekModel import llm


class ImageToTextAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.tool_data = ""

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名多模态助手，你的目标是根据用户问题调用相关工具对图片进行识别

        你按照如下步骤进行工作:
             1. 根据用户问题判断当前用户的意图。
             2. 确认调用的工具和传入相关参数，给出初步答案
             3. 现在，请重新评估你的初步答案，寻找其中可能的错误或遗漏， 并尝试改进:
                - 判断是否正确的调用了工具
                - 判断是否遗漏参数或参数格式是否正确
                - 其他可能存在的问题
             4. 最终需要调用的工具及传入的参数
             5. 结合工具返回的信息，给出最终回复答案
             6. 将最终答案返回成json格式数据 
             
             
        上下文信息:
           - 基本信息:
            {self.get_context_data(chat_no,"baseInfo")}
            
            
        内容生成约束:
            1. 如果图片中包含暴力，色情，政治敏感等内容，应该拒绝识别用意并给出正能量的回答
            
            
        返回json格式:
        {{"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name": <string>,"args": <list>}}

        返回值说明:
          - `code`：0 -> 执行成功
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `reply`:  提供问题的最终回复信息
          - `tool_name`: 调用工具的名称
          - `args`: 调用工具所需的参数列表
          
        可调用工具信息:
          - `image_modal_by_url(query: str,url: str)`: 通过图片的url地址识别图片内容，参数为用户问题和图片的网络链接地址
            - `query`: 必需传递，用户的针对图片的问题，用于传给图片大模型进行推理， 例如: 图片中有几把钥匙
            - `url`: 必需传递，图片的网络链接地址，  例如: http://example.com/1233.png
        """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
        ImageToTextAgent ->  这是一个用于图片内容识别的多模态Agent
        """
        return desc

    def query_name(self) -> str:
        return "ImageToTextAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] != 0:
            return json_data
        if json_data["tool_name"] == "image_modal_by_url":
            self.tool_data = await self.image_modal_by_url(json_data["args"][0], json_data["args"][1])
        return self.tool_data


    async def image_modal_by_url(self,query: str,url: str):
        base64str = await self.image_url_to_base64_async(url)
        return await self.image_modal_By_Base64(query,base64str)

    async def image_modal_By_Base64(self,query: str,base64Encode: str):
        messages = [{"role": "system", "content": [{"type": "text", "text": "你是一名多模态帮助助手"}]}]
        messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64Encode}"}}, {"type": "text", "text": query}]})
        response = await qw_llm.acall(json.dumps(messages))
        return {"code": 0, "reply": response}

    async def image_url_to_base64_async(self,url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    base64_str = base64.b64encode(image_data).decode('utf-8')
                    return base64_str
                else:
                    raise Exception(f"图片请求失败，状态码：{response.status}")

instance = ImageToTextAgent()

