import json
from agent.model.BaseModel import BaseModel
import agent.AgentGraph as graph

class AgentMain(graph.Node):

    def getPrompt(self):
        content = {"role": "system", "content":
            f"你是一名处理分类问题智能体。严格按照要求格式返回数据。\n"
            "你需要结合历史信息已一步一步的理解用户需求判断用户问题的类型: \n"
            "  简单问题 -> 立即处理类，常识类问题，简单问答，非最近信息（3个月前），简单逻辑问题，短篇故事或句子（一千字以内），单一步骤问题。 \n"
            "  复杂问题 -> 立即处理类，复杂的逻辑问题，近实时信息，中长篇故事或句子，多步骤问题，涉及action等与程序外部交互的问题（例如IO操作，编程，运行程序，安装软件，搜索，下载，通信，计算机管理等） \n"
            "  任务触发类问题 -> 非立即处理类问题，周期类，延时类（如用户需求为对定时任务，延时任务进行创建和查询的操作时候） \n"
            "返回值json格式如下: \n"
            "{\"status\": 2,\"reply\":\"...\",\"eventType\":0} \n"
            "返回值说明: \n"
            "   eventType: 0->简单问题, 1->复杂问题，2 -> 任务触发类问题 \n"
            "   status: 2 \n"
            "   reply: status为2 -> 返回成功原因 \n"

            }
        return content

    async def exec(self, messageNo: str, llm: BaseModel):

        response = await llm.acall(json.dumps(self.messageDict[messageNo]))
        jsonData = json.loads(response)

        if jsonData["status"] == 0 or jsonData["status"] == 1:
            self.reply = jsonData["reply"]
            self.appendMessage(messageNo,{"role":"assistant","content": self.reply})
            return response
        else:
            messages = self.messageDict[messageNo]
            eventType = jsonData["eventType"]

            if eventType == 0:
                self.childs[0].appendMessage(messageNo, messages[-1])
                respose = await self.childs[0].exec(messageNo, llm)
                jsonData = json.loads(respose)
                self.reply = jsonData["reply"]
                self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
                return respose
            elif eventType == 1:
                self.childs[1].appendMessage(messageNo, messages[-1])
                respose = await self.childs[1].exec(messageNo, llm)
                jsonData = json.loads(respose)
                self.reply = jsonData["reply"]
                self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
                return respose
            elif eventType == 2:
                self.childs[2].appendMessage(messageNo, messages[-1])
                respose = await self.childs[2].exec(messageNo, llm)
                jsonData = json.loads(respose)
                self.reply = jsonData["reply"]
                self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
                return respose

