
from agent.model.BaseModel import BaseModel


class Node:

    def __init__(self):
        self.childs = []
        self.messageDict = {}
        self.agentNo = None
        self.reply = None

    def appendMessage(self, messageNo: str, content: dict):
        message = self.messageDict.get(messageNo)
        if message == None:
            message = []
            message.append(self.getPrompt())
            self.messageDict[messageNo] = message
        message.append(content)


    def appendMessages(self, messageNo: str, contents: list):
        message = self.messageDict.get(messageNo)
        if message == None:
            message = []
            message.append(self.getPrompt())
            self.messageDict[messageNo] = message
        for content in contents:
            message.append(content)

    def addChild(self, node):
        self.childs.append(node)

    def clearMessage(self, messageNo: str):
        self.messageDict.pop(messageNo)

    def getMessage(self, messageNo: str):
        return self.messageDict[messageNo]

    def queryDesc(self) -> str:
        pass

    def queryName(self) -> str:
        pass
    def getReply(self):
        return self.reply

    def getPrompt(self):
        pass

    def getFallbackPrompt(self):
        pass

    async def exec(self, messageNo: str, llm: BaseModel):
        pass






