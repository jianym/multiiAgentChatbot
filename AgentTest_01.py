# This is a sample Python script.
import json
from typing import Optional

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import requests
from langchain.llms.base import LLM


messages = []
class CustomAPIModel(LLM):
    api_url: str = "https://api.deepseek.com"

    api_key: str = "*********************************"

    def _call(self, prompt: str, stop: Optional[list] = None) -> str:
        """这个方法会用来调用自定义 API，并返回结果"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages.append(json.loads(prompt))
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }

        response = requests.post(f"{self.api_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        messages.append(response_data["choices"][0]["message"])
        return response_data["choices"][0]["message"]["content"]

    def _handle_tool_error(self, error: Exception) -> str:
        """处理工具调用过程中可能出现的错误"""
        return f"Error occurred: {str(error)}"



    @property
    def _llm_type(self) -> str:
        return "deepseek_api"

class MyTool:

    def add(self, a: int, b: int) -> int:
        """将两整数相加"""
        return a + b


def getToolPrompt():
   content = {"role": "system", "content":
            f"你是一名助手，你可以使用一下工具:\n"
            " -add(a: int, b: int): 两整数相加\n"
            "如果需要调用工具解决问题，返回格式如下: \n"
            "{\"tool_name\":tool_name,\"args\": [...]}"}
   return json.dumps(content)

def getUserPrompt(prompt: str):
   content = {"role": "user", "content": prompt}
   return json.dumps(content)

tools = MyTool()

custom_model = CustomAPIModel()
messages.append(json.loads(getToolPrompt()))
response =custom_model.invoke(getUserPrompt("计算3加5等于几"))
jsonData = json.loads(response)
result = getattr(tools, jsonData["tool_name"])(*jsonData["args"])
response =custom_model.invoke(getUserPrompt("工具返回的结果为: "+str(result)))
print(response)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
