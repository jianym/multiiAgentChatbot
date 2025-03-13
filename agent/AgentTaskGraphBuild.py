from agent.AgentPlanning import AgentPlanning
from agent.model.DeepseekModel import llm

class AgentTaskGraphBuild:
    def __init__(self):
        self.agentPlanning = AgentPlanning()

    def getUserPrompt(self, prompt: str):
        content = {"role": "user", "content": prompt}
        return content

    async def start(self, messageNo: str, query: str):

        self.agentPlanning.appendMessage(messageNo, self.getUserPrompt(query))
        print(self.agentPlanning.getMessage(messageNo))
        await self.agentPlanning.exec(messageNo, llm)

taskGraph = AgentTaskGraphBuild()