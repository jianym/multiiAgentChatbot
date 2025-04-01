import time

from agent.AgentPlanning import AgentPlanning
from agent.model.DeepseekModel import llm

class AgentTaskGraphBuild:
    def __init__(self):
        self.agentPlanning = AgentPlanning()

    def getUserPrompt(self, prompt: str):
        content = {"time": time.time(), "role": "user", "content": prompt}
        return content

    async def start(self, messageNo: str, query: str):

        self.agentPlanning.appendMessage(messageNo, self.getUserPrompt(query))
        await self.agentPlanning.exec(messageNo)

taskGraph = AgentTaskGraphBuild()