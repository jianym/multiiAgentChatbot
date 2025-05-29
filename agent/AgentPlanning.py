
import json

from agent.AgentNode import AgentNode
from agent.model.DeepseekModel import llm
from agent.tool.AgentToolImport import tools


class AgentPlanning(AgentNode):

    def __init__(self):
        super().__init__()
        self.llm = llm
        self.tryTime = 2

    def getPrompt(self, messageNo=None):
        # - 只有明确的周期时间或延时时间才可以调用任务计划管理工具
        content = f"""
           你是一名任务规划助手
           你的工作流程如下:
             1.首先结合多轮对话和上下文提供的信息对用户问题进行错别字修改然后根据待分配的agent信息进行问题拆分，交给相应的agent进行执行
                - 你应该深刻理解需求，满足调用Agent工具的所需条件，组合好各Agent完成任务
                - 对于周期类，延时类等计划执行类问题，其触发时间和触发内容应该看做一个整体，不可拆分
                - 可以查看数据表信息，调用相关的数据处理Agent来处理问题
                - 只有明确的收件人信息时和发送内容时才可以调用发送邮件相关的工具
                - 可以通过摄像头Agent来获取当前环境的最新影像
                - 如果涉及到时间问题，保证时间正确，以当前时间作为参考对象
                - 关注上下文中最新时间
             2. 现在，请重新评估你的初步答案，寻找其中可能的错误或遗漏， 并尝试改进:
                - 如果存在分配的Agent，检查是否满足Agent工具的调用要求及是否满足调用Agent工具的参数
                - 判断是否遗漏关键信息没有处理
                - 判断是否错误的理解问题意图
                - 其他可能存在的问题
             3. 如果有更好的方式，请重新执行工作流程的第二步来规划新的解决方法和步骤。
             4. 将最终的答案返回成json格式数据
               
           基本信息:
                {self.getContextData(messageNo,"baseInfo")}
                
           问题及子问题内容约束:
             1. 用户问题中包含明确的相对时间的，如昨日，明天等，应根据当前时间进行计算到具体的时间（年月日十分秒等）
             2. 保证用户搜索时间的准确性
             
           最终答案约束:
             1.如果返回结果有引用外部信息部分应标记出引用来源链接
            
        
           返回json格式的数据:
           {{"code":0,"reply":<string>,"process":<string>, "agent":[{{"step":"...","reason","...","agentName":"..."}},...]}}
           
           返回值说明:
           - `code: 0 -> 阶段已完成
           - `reply`: 字符串类型 code为0 -> 任务分配过程，code为1  -> 分配失败原因
           - `process`: 你回答问题的思考过程文字描述
           - `agent`: 具体任务步骤分配列表，如果失败则为空,具体值含义: step -> 当前agent要处理的问题及问题相关的上下文信息，reason -> 分配原因, agentName -> 分配来执行步骤的agent名称
           
           待分配的Agent信息:
           {tools.queryAgents()}
        """
        message = {"role": "system", "content": content}
        return message

    def queryName(self) -> str:
        return "PlanningAgent"

    async def action(self, message_no: str, json_data: dict):
            agents = json_data["agent"]
            messages = []
            # messages.append({"role": "assistant", "content": json.dumps(jsonData,ensure_ascii=False)})
            return await self.action0(message_no,agents,messages)

    async def suspend(self,messageNo: str):
        pass

    async def notify(self,taakId: str):
        pass

    async def action0(self,messageNo: str,agents: list,messages: list):
        print(agents)
        for agent in agents:

            messages.append({"role": "user", "content": agent["step"]})
            agentInstance = tools.getTool(agent["agentName"])
            agentInstance.appendMessages(messageNo, messages)
            jsonDataInstance = await agentInstance.exec(messageNo)

            self.appendMessage(messageNo, {"role": "assistant", "content": jsonDataInstance["reply"]})
            messages.append({"role": "assistant", "content": jsonDataInstance["reply"]})
            if jsonDataInstance["code"] != 0:
                self.appendMessage(messageNo, {"role": "user", "content": "执行结束，请给出最终答案"})
                outputRes = await self.llm.acall(json.dumps(messages), "text")
                return {"code": 1, "reply": outputRes}

        self.appendMessage(messageNo, {"role": "system", "content":
               f"""
               基本信息:
                {self.getContextData(messageNo,"baseInfo")}
                
               最终答案约束:
                  1.如果返回结果有引用外部信息部分应标记出引用来源链接
                
               """
        })
        self.appendMessage(messageNo, {"role": "user", "content": "执行结束，根据上下文信息给出最终答案，如果返回结果有引用外部信息部分应标记出引用来源链接"})
        outputRes = await self.llm.acall(json.dumps(messages), "text")
        return {"code": 0, "reply": outputRes}

