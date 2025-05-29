import ast
import json

from agent.agent_node import AgentNode
from agent.info_context import InfoContext
from agent.model.DeepseekModel import llm
from agent.app.rpa_app_agent_modules.agent_import import agent_import


class RpaAppAgent(AgentNode):

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
                - EmailAgent-> 发送邮件

            返回值json格式如下: 
            {{"code": 0,"reply":<string>,"agent_name":<string>}}

            返回值说明:
            - `code`: 0 -> 完成分类
            - `reply`: code为0 -> 分配原因 ,code为1 -> 失败原因
            - `agent_name`: Agent名称

        """
        message = {"role": "system", "content": content}
        return message

    def query_name(self) -> str:
        return "RpaAppAgent"

    async def action(self, chat_no: str, json_data: dict):
        if json_data["code"] != 0:
            return json_data
        else:
            agent_name = json_data["agent_name"]

            if agent_name:
                agent_instance = agent_import.get_agent(agent_name)
                agent_instance.appendMessage(chat_no,
                                             {"role": "user", "content": json.dumps(self.message_dict[chat_no][0:-1])})
                return await agent_instance.exec(chat_no)
