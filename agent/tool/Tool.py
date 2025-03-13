

class Tool:

    messagesDict = {}

    def getPrompt(self):
        pass

    def appendMessage(self, messageNo: str,content: str):
        message = self.messagesDict.get(messageNo)
        if message == None:
            message = []
            message.append(self.getPrompt())
        message.append(content)
        self.messagesDict[messageNo] = message

    def clearMessage(self,messageNo: str):
        self.messagesDict.pop(messageNo)

    def queryDesc(self) -> str:
        pass

    def queryName(self) -> str:
        pass

    def exec(self,message: str) -> str:
        pass

