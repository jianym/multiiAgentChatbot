import ast
import json

from agent.agent_node import AgentNode
from agent.model.DeepseekModel import llm
from agent.app.cross_modal_app_agent_modules.agent_import import agent_import


class CrossModalAppAgent(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm

    def get_prompt(self, chat_no=None):
        content = f"""
            你是一名处理分类问题的智能体,你只做问题分配，不回答问题。

            你的流程步骤:
               1. 结合多轮对话信息与上下文信息来理解用户问题
               2. 将用户问题分配给Agent执行

            上下文信息:
                - 基本信息:
                    {self.get_context_data(chat_no, "baseInfo")}

            已知Agent信息:
                - ImageToTextAgent -> 图像识别
                - TextToImageAgent -> 通过文本生成图像
            
            
            以下情况分配失败:
                - 用户问题意义不明，表达混乱
                - 没有能够解决用户问题的Agent
                
            返回值json格式如下: 
            {{"code": 0,"reply":<string>,"agent_name":<string>}}

            返回值说明:
            - `code`: 0 -> 完成分类，1 -> 分配失败
            - `reply`: code为0 -> 分配原因 ,code为1 -> 失败原因
            - `agent_name`: Agent名称

        """
        message = {"role": "system", "content": content}
        return message

    def query_name(self) -> str:
        return "CrossModalAppAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] != 0:
            return json_data
        else:
            agent_name = json_data["agent_name"]

            if agent_name:
                agent_instance = agent_import.get_agent(agent_name)
                agent_instance.append_message(chat_no,
                                             {"role": "user", "content": json.dumps(self.message_dict[chat_no][0:-1])})
                return await agent_instance.exec(chat_no)
