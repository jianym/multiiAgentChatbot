from agent.AgentMain import AgentMain
from agent.AgentSimple import AgentSimple
from agent.AgentAnaly import AgentAnaly
from agent.AgentPlanning import AgentPlanning
from agent.AgentSchedule import AgentSchedule
from agent.model.DeepseekModel import llm

class AgentQueryGraphBuild:

    def __init__(self):

        self.analyAgent = AgentAnaly()
        self.agentMain = AgentMain()
        self.simpleAgent = AgentSimple()
        self.agentSchedule = AgentSchedule()
        self.agentPlanning = AgentPlanning()

        self.analyAgent.addChild(self.agentPlanning)
        self.agentMain.addChild(self.simpleAgent)
        self.agentMain.addChild(self.analyAgent)
        self.agentMain.addChild(self.agentSchedule)

    def getUserPrompt(self,prompt: str):
         content = {"role": "user", "content": prompt}
         return content

    async def start(self,messageNo: str, query: str):
        self.agentMain.appendMessage(messageNo,self.getUserPrompt(query))
        await self.agentMain.exec(messageNo, llm)
        return self.agentMain.getReply()

queryGraph = AgentQueryGraphBuild()

