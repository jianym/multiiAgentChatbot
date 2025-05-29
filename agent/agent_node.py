
import json
from datetime import datetime
from typing import re
from agent.info_context import InfoContext


class AgentNode:

    def add_child(self, node):
        self.childs.append(node)

    def __init__(self):
        super().__init__()
        self.childs = []
        self.message_dict = {}
        self.reply = None
        self.llm = None
        self.tryTime = 0
        self.context_info = {}
        self.kwargs = {}

    def set_base_info(self,chat_no: str):
        # 获取当前时间
        current_time = datetime.now()
        # 格式化时间
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        context_data = self.context_info.get(chat_no, None)
        if context_data:
            context_data["baseInfo"] = {"当前时间":formatted_time}
        else:
            context_data = {"baseInfo": {"当前时间": formatted_time}}
            self.context_info = {chat_no: context_data}

        context_data["baseInfo"].update(InfoContext.baseInfoDict[chat_no])

    def append_message(self, chat_no: str, content: dict):
        message = self.message_dict.get(chat_no)
        if message == None:
            message = []
            self.message_dict[chat_no] = message
        message.append({"role": content["role"], "content": content["content"]})

    def append_messages(self, chat_no: str, contents: list):
        message = self.message_dict.get(chat_no)
        if message == None:
            message = []
            self.message_dict[chat_no] = message
        for content in contents:
            message.append({"role": content["role"], "content": content["content"]})

    def clear_messages(self, chat_no: str):
         return self.message_dict.pop(chat_no,None)

    def get_message(self, chat_no: str):
        return self.message_dict.get(chat_no)

    def get_message_and_prompt(self, chat_no: str):
        messages = []
        messages.append(self.get_prompt(chat_no))
        messages.extend(self.message_dict.get(chat_no))
        return messages

    def query_desc(self) -> str:
        pass

    def query_name(self) -> str:
        pass

    def get_prompt(self, chat_no=None):
        pass

    async def exec(self, chat_no: str):
        try:
            self.set_base_info(chat_no)
            await self.set_context_data(self.context_info.get(chat_no))
            json_data = await self.exec0(chat_no)
            if self.tryTime > 1:
                for i in range(1,self.tryTime):
                    if json_data["code"] == 0:
                        break
                    self.append_message(chat_no, {"role": "assistant", "content": json_data["reply"]})
                    self.append_message(chat_no, {"role": "user", "content": "推理失败，请根据多轮对话进行反思原因然后再试一次"})
                    json_data = await self.exec0(chat_no)

            return json_data
        except Exception as e:
            # raise e
            # # 捕获可能的异常并返回错误
            print(f"推理请求失败: {str(e)}")
            json_data = {"code": 1, "reply": f"执行失败: {str(e)}"}
            return json_data
        finally:
            # if jsonData["code"] != 0:
            #     await self.suspend(messageNo)
            self.context_info.pop(chat_no, None)
            self.clear_messages(chat_no)

    def get_context_data(self,chat_no: str,key: str):
        if self.context_info.get(chat_no,None):
            return self.context_info.get(chat_no).get(key,None)

    async def set_context_data(self,context_data: dict):
        pass

    async def append_context_data(self,chat_no, context_data: dict):
        context = self.context_info.get(chat_no)
        if not context:
            context = {}
        for key, value in context_data.items():
            context[key] = value
        self.context_info[chat_no] = context

    async def suspend(self,chat_no: str):
        pass

    async def notify(self, task_id: str):
        pass

    async def exec0(self, chat_no: str):
        try:
            response = await self.llm.acall(json.dumps(self.get_message_and_prompt(chat_no)), **self.kwargs)
            token_usage = response["usage"]
            InfoContext.usage_dict[chat_no] = token_usage
            response_data = response["choices"][0]["message"]["content"]
            json_data = json.loads(response_data)
            if json_data["reply"]:
                json_data["reply"] = str(json_data["reply"])
            if json_data["code"] != 0:
                return json_data

            self.append_message(chat_no, {"role": "assistant", "content": json_data["reply"]})
            return await self.action(chat_no, json_data)
        except Exception as e:

            # raise e
            # 捕获可能的异常并返回错误
            print(f"推理请求失败: {str(e)}")
            return {"code": 1, "reply": f"推理请求失败: {str(e)}"}

    async def action(self,chat_no: str,json_data: dict) -> dict:
        pass





