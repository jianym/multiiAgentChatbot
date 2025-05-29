import json

from agent.agent_node import AgentNode
from agent.model.DeepseekModel import llm
from agent.model.WanxModel import wanXllm

class TextToImageAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.tool_data = ""

    def get_prompt(self, chat_no=None):
        content = f"""
        你是一名图像生成助手，你的目标是根据用户问题调用相关工具进行图片或视频生成

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


        内容生成约束:
            1. 如果要生成图片中包含暴力，色情，政治敏感等内容，应该拒绝生成，并返回正能量答复
            2. 如果用户没有明确生成图片的尺寸大小，则根据用户图片描述进行推断，size字段格式例子：512*512
            3. 图片使用超链接


        返回json格式:
        {{"code": <int>,"reply": <string>,"tool_use": <bool>,"tool_name": <string>,"args": <list>}}

        返回值说明:
          - `code`：0 -> 执行成功
          - `tool_use`:  true -> 需使用工具, false -> 不使用工具
          - `reply`:  提供问题的最终回复信息
          - `tool_name`: 调用工具的名称
          - `args`: 调用工具所需的参数列表

        可调用工具信息:
          - `image_gen(query: str,size: str)`: 通过用户对图片的描述来生成图片，返回值为生成图片的url地址列表
            - `query`: 必需传递，用户对生成图片的描述
            - `size`: 必需传递，要生成图片的大小，如果用户没有明确要求生成的图片大小，根据用户问题描述推断图片的大小，格式例子 512*512
        """
        message = {"role": "system", "content": content}
        return message

    def query_desc(self) -> str:
        desc = """
        TextToImageAgent -> 你是一名图像生成Agent，你的目标是根据用户问题调用相关工具进行图片或视频生成
        """
        return desc

    def query_name(self) -> str:
        return "TextToImageAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] != 0:
            return json_data
        if json_data["tool_name"] == "image_gen":
            self.tool_data = await self.image_gen(json_data["args"][0], json_data["args"][1])
        return self.tool_data

    async def image_gen(self, query: str, size="512*512"):
        response = wanXllm.acall(query,size)
        return {"code": 0, "reply": json.dumps(response)}

instance = TextToImageAgent()

