from agent.model.BaseModel import BaseModel
from agent.AgentGraph import Node
import json

class AgentSimple(Node):

    def getPrompt(self):
        content = """
        你是一名通用助手。
        你的目标是根据上下午信息，完成用户的要求。
        
        返回json格式:
        {"status":<int>,"reply":<string>}
        
        返回值说明:
        - `status`: 1 -> 完成失败, 2 -> 完成成功
        - `reply`: 如果完成成功-> 完成答案，如果完成失败-> 错误原因"
        """
        message = {"role": "system", "content": content}
        return message

    def queryDesc(self) -> str:
        desc = """
        simpleAgent -> 如果其他Agent不满足，使用这个
        """
        return desc

    def queryName(self) -> str:
        return "simpleAgent"

    def getFallbackPrompt(self):
        pass

    async def exec(self, messageNo: str, llm: BaseModel) -> str:
        response = await llm.acall(json.dumps(self.messageDict[messageNo]))
        jsonData = json.loads(response)
        self.reply = jsonData["reply"]
        self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
        return response