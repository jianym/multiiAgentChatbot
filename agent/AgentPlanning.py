
import json
from agent.AgentNode import Node
from agent.model.DeepseekModel import llm
from agent.tool.AgentToolImport import tools


class AgentPlanning(Node):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.tryTime = 2

    def getPrompt(self, messageNo=None):
        content = f"""
           你是一名任务规划助手
           你的工作流程如下:
             1.首先结合多轮对话对用户问题进行错别字修改然后进行解决方案分析并拆分成各个可执行的步骤，然后分配给Agent执行，给出初步答案
                - 你应该一步一步的深刻理解需求，满足调用Agent工具的所需条件，组合好各Agent完成任务
                - 对于周期类，延时类等计划执行类问题，其触发时间和触发内容应该看做一个整体，不可拆分
                - 只有明确的周期时间或延时时间才可以调用任务计划管理工具
                - 只有明确的收件人信息时和发送内容时才可以调用发送邮件相关的工具
             2. 现在，请重新评估你的初步答案，寻找其中可能的错误或遗漏， 并尝试改进:
                - 如果存在分配的Agent，检查是否满足Agent工具的调用要求及是否满足调用Agent工具的参数
                - 判断是否遗漏关键信息没有处理
                - 判断是否错误的理解问题意图
                - 其他可能存在的问题
             3. 如果有更好的方式，请重新执行工作流程的第二步来规划新的解决方法和步骤。
             4. 将最终的答案返回成json格式数据
            
           基本信息:
           {self.baseInfo}
             
           返回json格式的数据:
           {{"code":0,"reply":<string>,"process":<string>, "agent":[{{"step":"...","reason","...","agentName":"..."}},...]}}
           
           返回值说明:
           - `code: 0 -> 阶段已完成
           - `reply`: 字符串类型 code为0 -> 任务分配过程，code为1  -> 分配失败原因
           - `process`: 你回答问题的思考过程文字描述
           - `agent`: 具体任务步骤分配列表，如果失败则为空,具体值含义: step -> 具体步骤应包含调用Agent工具所需的要求，reason -> 分配原因, agentName -> 分配来执行步骤的agent名称
           
           待分配的Agent信息:
           {tools.queryAgents()}
        """
        message = {"role": "system", "content": content}
        return message

    def queryName(self) -> str:
        return "planningAgent"

    async def action(self,messageNo: str,jsonData: dict):
            agents = jsonData["agent"]
            messages = []
            messages.append({"role": "assistant", "content": json.dumps(jsonData,ensure_ascii=False)})
            for agent in agents:

                messages.append({"role": "user", "content": agent["step"]})

                agentInstance = tools.getTool(agent["agentName"])
                agentInstance.appendMessages(messageNo, messages)
                jsonDataInstance = await agentInstance.exec(messageNo)

                self.appendMessage(messageNo, {"role": "assistant", "content":  jsonDataInstance["reply"]})
                messages.append({"role": "assistant", "content":   jsonDataInstance["reply"]})
                if jsonDataInstance["code"] != 0:
                    self.appendMessage(messageNo, {"role": "user", "content": "规划步骤执行结束，请给出最终答案"})
                    outputRes = await self.llm.acall(json.dumps(self.getMessage(messageNo), ensure_ascii=False), "text")
                    return {"code": 1, "reply": outputRes}

            self.appendMessage(messageNo, {"role": "user", "content": "规划步骤执行结束，根据上下文信息给出最终答案"})
            outputRes = await self.llm.acall(json.dumps(self.getMessage(messageNo),ensure_ascii=False),"text")
            return {"code": 0,"reply":outputRes}