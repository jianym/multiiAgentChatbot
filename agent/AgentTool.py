
import json
from datetime import datetime
from typing import re


class Tool:

    downFile = {}



    def __init__(self):
        self.messageDict = {}
        self.reply = None
        self.llm = None
        self.tryTime = 0
        self.baseInfo = {}


    def setBaseInfo(self):
        # 获取当前时间
        current_time = datetime.now()
        # 格式化时间
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        self.baseInfo = {"当前时间":formatted_time}

    def appendMessage(self, messageNo: str, content: dict):
        message = self.messageDict.get(messageNo)
        if message == None:
            message = []
            self.messageDict[messageNo] = message
        message.append({"role": content["role"], "content": content["content"]})

    def appendMessages(self, messageNo: str, contents: list):
        message = self.messageDict.get(messageNo)
        if message == None:
            message = []
            self.messageDict[messageNo] = message
        for content in contents:
            message.append({"role": content["role"], "content": content["content"]})

    def cleaarMessages(self, messageNo: str):
         return self.messageDict.pop(messageNo,None)

    def getMessage(self, messageNo: str):
        return self.messageDict.get(messageNo)

    def getMessageAndPrompt(self, messageNo: str):
        messages = []
        messages.append(self.getPrompt(messageNo))
        messages.extend(self.messageDict.get(messageNo))
        return messages

    def queryDesc(self) -> str:
        pass

    def queryName(self) -> str:
        pass

    def getPrompt(self, messageNo=None):
        pass

    def setContentData(self, data: dict):
        pass

    async def exec(self, messageNo: str):
        try:
            self.setBaseInfo()
            jsonData = await self.exec0(messageNo)
            if self.tryTime > 1:
                for i in range(1,self.tryTime):
                    if jsonData["code"] == 0:
                        break
                    self.appendMessage(messageNo, {"role": "assistant", "content": jsonData["reply"]})
                    self.appendMessage(messageNo, {"role": "user", "content": "推理失败，请根据多轮对话进行反思原因然后再试一次"})
                    jsonData = await self.exec0(messageNo)
            return jsonData
        except Exception as e:
            raise e
            # 捕获可能的异常并返回错误
            print(f"推理请求失败: {str(e)}")
            return {"code": 1, "reply": f"执行失败: {str(e)}"}
        finally:
            self.cleaarMessages(messageNo)

    async def exec0(self, messageNo: str):
        try:
            response = await self.llm.acall(json.dumps(self.getMessageAndPrompt(messageNo)))
            jsonData = json.loads(response)
            if jsonData["code"] != 0:
                return jsonData

            self.appendMessage(messageNo, {"role": "assistant", "content": jsonData["reply"]})
            return await self.action(messageNo, jsonData)
        except Exception as e:
            raise e
            # 捕获可能的异常并返回错误
            print(f"推理请求失败: {str(e)}")
            return {"code": 1, "reply": f"推理请求失败: {str(e)}"}

    async def action(self,messageNo: str,jsonData: dict) -> dict:
        pass





