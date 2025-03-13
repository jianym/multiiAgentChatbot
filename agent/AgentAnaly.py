from agent.model.BaseModel import BaseModel
import json
from agent.AgentGraph import Node

class AgentAnaly(Node):

    def getPrompt(self):
        content = {"role": "system", "content": f"你是一名需求分析助手。\n"
                   "你的工作职责是将深刻分析用户问题，判断当前需求是否可以完成，是否需要补充信息。不需要回答用户的问题。对于问题中不明确或不清晰的地方需要和用户进行一次性确认。\n"
                   "返回json格式的数据: \n"
                   "{\"status\":0,\"reply\":\"\"} \n"
                   "返回值说明： \n"
                   " status: 0 -> 将不确定性问题返回用户, 2 -> 将用户问题转换成具体的用户实际需求 \n"
                   " reply: status为0 -> 需要和用户待确认的问题, status为2-> 用户问题转换的实际需求内容 "
                  }
        return content

    def getFallbackPrompt(self):
        pass

    async def exec(self, messageNo: str, llm: BaseModel):

        response = await llm.acall(json.dumps(self.messageDict[messageNo]))
        jsonData = json.loads(response)
        messages = []
        messages.append(self.messageDict[messageNo][-1])
        if jsonData["status"] == 0 or jsonData["status"] == 1:
            self.reply = jsonData["reply"]
            self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
            return response
        else:
            messages.append({"role":"assistant","content": jsonData["reply"]})
            self.childs[0].appendMessages(messageNo,messages)
            instanceRes = await self.childs[0].exec(messageNo,llm)

            jsonData = json.loads(instanceRes)
            self.reply = jsonData["reply"]
            self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
            return instanceRes