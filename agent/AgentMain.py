import json
from agent.model.BaseModel import BaseModel
import agent.AgentGraph as graph

class AgentMain(graph.Node):

    def getPrompt(self):
        content = """
            你是一名处理分类问题的智能体。
            你的工作职责是结合上下文信息将用户问题进行分类，然后分配给Agent执行。
            
            返回值json格式如下: 
            {"status": 2,"reply":"...","agentName":"..."}
            
            返回值说明:
            - `status`: 0 -> 有不明确影响分类因素需用户确认 2 -> 完成分类
            - `reply`: status为2 -> 分类原因 ，status为0  -> 影响分类因素需用户确认的问题
            - `agentName`: Agent名称
            
            已知Agent信息:
            - simpleAgent -> 简单问题，常识类问题，简单问答，非最近信息（3个月前），简单逻辑问题，短篇故事或句子（一千字以内），单一步骤问题
            - analyAgent -> 复杂问题，复杂的逻辑问题，近实时信息，中长篇故事或句子，多步骤问题，涉及action等与程序外部交互的问题（例如IO操作，编程，运行程序，安装软件，搜索，下载，通信，计算机管理等)
        """
        # - scheduleAgent -> 非立即处理类问题，周期类，延时类 (校验: 时间不能为空)
        message = {"role": "system", "content": content}
        return message


    async def exec(self, messageNo: str, llm: BaseModel):

        response = await llm.acall(json.dumps(self.messageDict[messageNo]))
        print(response)
        jsonData = json.loads(response)

        if jsonData["status"] == 0 or jsonData["status"] == 1:
            self.reply = jsonData["reply"]
            self.appendMessage(messageNo,{"role":"assistant","content": self.reply})
            return response
        else:
            messages = self.messageDict[messageNo]
            agentName = jsonData["agentName"]

            if agentName == "simpleAgent":
                self.childs[0].appendMessage(messageNo, messages[-1])
                respose = await self.childs[0].exec(messageNo, llm)
                jsonData = json.loads(respose)
                self.reply = jsonData["reply"]
                self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
                return respose
            elif agentName == "analyAgent":
                self.childs[1].appendMessage(messageNo, messages[-1])
                respose = await self.childs[1].exec(messageNo, llm)
                jsonData = json.loads(respose)
                self.reply = jsonData["reply"]
                self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
                return respose
            # elif agentName == "scheduleAgent":
            #     self.childs[2].appendMessage(messageNo, messages[-1])
            #     respose = await self.childs[2].exec(messageNo, llm)
            #     jsonData = json.loads(respose)
            #     self.reply = jsonData["reply"]
            #     self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
            #     return respose

