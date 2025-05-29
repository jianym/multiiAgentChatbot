import json

from agent.agent_memory import memory
from agent.info_context import InfoContext
from service.knowkledgeService import knowledageServiceInstance
from agent.context.UserTagContext import userTag
from agent.model.DeepseekModel import llm
class MemoryContextManager:

    def __init__(self,chat_no: str, query: str):
        self.query = query
        self.chat_no = chat_no
        self.reply = None

    def __enter__(self):
        base_dict = InfoContext.baseInfoDict.get(self.chat_no, None)

        if not base_dict:
            InfoContext.baseInfoDict[self.chat_no] = {}
        if self.query:
            memory.add_message(self.chat_no, self.get_user_prompt(self.query))

        self.memory_message = memory.get_message(self.chat_no)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        InfoContext.baseInfoDict.pop(self.chat_no, None)
        InfoContext.usage_dict.pop(self.chat_no, None)
        if exc_type:
            print(f"Exception: {exc_type}, {exc_val}")
            return False
        memory.add_message(self.chat_no, {"role": "assistant", "content": self.reply})
        return True  # 如果返回True，异常将被忽略；否则，异常会被抛出

    def set_reply(self,reply: str):
        self.reply = reply

    def get_user_prompt(self,prompt: str):
         return {"role": "user", "content": prompt}


