from agent.model.BaseModel import BaseModel
import json
from agent.tool.AgentTool import tools
from agent.AgentGraph import Node
class AgentPlanning(Node):

    def getPrompt(self):
        content = """
           你是一名任务规划助手。
           你的工作职责是结合上下文信息将用户需求进行解决方案分析并规划成各个可执行的步骤，然后分配给Agent执行。
            - 你应该一步一步的深刻理解需求，满足调用Agent工具的所需条件，组合好各Agent完成任务。
            - 对于周期类，延时类等计划执行类问题，其触发时间和触发内容应该看做一个整体，不可拆分
            
           返回json格式的数据:
           {"status":2,"reply":"...", "agent":[{"step":"...","reason","...","agentName":"..."},...]}
           
           返回值说明:
           - `status`: 1 -> 无法完成需要回退上一阶段处理, 2 -> 阶段已完成
           - `reply`: status为2 -> 具体解决方案，status为1  -> 失败原因
           - `agent`: 具体任务步骤分配列表，如果失败则为空,具体值含义: step -> 具体步骤应包含调用Agent工具所需的要求，reason -> 分配原因, agentName -> 分配来执行步骤的agent名称
          
           已有的agent信息:  
        """ + tools.queryAgents()
        message = {"role": "system", "content": content}
        return message


    async def exec(self, messageNo: str, llm: BaseModel):
        response = await llm.acall(json.dumps(self.messageDict[messageNo]))
        jsonData = json.loads(response)
        print(response)
        if jsonData["status"] == 0 or jsonData["status"] == 1:
            self.reply = jsonData["reply"]
            self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
            return response
        else:

            agents = jsonData["agent"]
            messages = []
            messages.append({"role": "assistant", "content": response})

            for agent in agents:
                messages.append({"role": "user", "content": agent["step"]})

                agentInstance = tools.getTool(agent["agentName"])
                agentInstance.appendMessages(messageNo, messages)

                instanceRes = await agentInstance.exec(messageNo, llm)

                jsonData = json.loads(instanceRes)

                self.reply = jsonData["reply"]
                self.appendMessage(messageNo, {"role": "assistant", "content": self.reply})
                if jsonData["status"] != 2:
                    return instanceRes
                else:
                    messages.append({"role": "assistant", "content":  self.reply})
            return response