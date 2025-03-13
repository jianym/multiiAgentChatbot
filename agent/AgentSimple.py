from agent.model.BaseModel import BaseModel
from agent.AgentGraph import Node
import json

class AgentSimple(Node):

    def getPrompt(self):
        content = {"role": "system", "content":
                   f"你是一名通用助手。\n"
                   "你的目标是根据历史信息，完成用户的要求。\n"
                   "返回json格式:\n"
                   "{\"status\":2,\"reply\":\"...\"} \n"
                   "返回值说明： \n"
                   " status: 1 -> 完成失败, 2 -> 完成成功 \n"
                   " reply: 如果完成成功-> 完成答案，如果完成失败-> 错误原因"
                   }
        return content

    def queryDesc(self) -> str:
        return " - simpleAgent: 如果其他agent不满足，使用这个"

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